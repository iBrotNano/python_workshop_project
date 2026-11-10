import logging
import re
from importlib.metadata import version

from sqlite_rag import SQLiteRag
from config.configuration import Configuration
from sqlite_rag.models.document_result import DocumentResult
from sqlite_rag.models.sentence_result import SentenceResult

log = logging.getLogger(__name__)


class Retriever:
    def __init__(self, configuration: Configuration):
        """
        Initializes the Retriever instance with the provided configuration.

        :param configuration: The configuration object containing settings for the retriever.
        :type configuration: Configuration
        """
        self.rag: SQLiteRag | None = SQLiteRag.create(
            configuration.sqlite_file_path,
            require_existing=True,
        )

        self.__batched_search_supported = version("sqlite-rag") == "0.1.4"

        if not self.__batched_search_supported:
            log.warning(
                "Batched sentence search supports sqlite-rag 0.1.4; "
                "using the library's original search implementation."
            )

    def close(self):
        """
        Closes the Retriever instance and releases any resources.
        """
        if self.rag is not None:
            self.rag.close()
            self.rag = None

    def __enter__(self) -> "Retriever":
        """
        Enters the runtime context related to this object.

        :return: The Retriever instance.
        :rtype: Retriever

        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exits the runtime context related to this object.

        :param exc_type: The exception type, if any.
        :param exc_value: The exception value, if any.
        :param traceback: The traceback object, if any.
        """
        self.close()

    def retrieve(self, query: str, top_k: int = 10) -> list[DocumentResult]:
        """
        Retrieves relevant nutrition information based on the provided query.

        :param query: The search query to retrieve nutrition information for.
        :type query: str
        :param top_k: The number of top results to return, default is 10.
        :type top_k: int
        :return: A list of retrieved results matching the query.
        :rtype: list[DocumentResult]
        :raises RuntimeError: If the retriever is closed.
        """
        if self.rag is None:
            raise RuntimeError("The retriever is closed.")
        
        if not self.__batched_search_supported or self.rag._settings.top_k_sentences < 0:
            return self.rag.search(query, top_k=top_k)

        #TODO: Extract the batch sentence scoring logic into a separate method for clarity and to make the code run only if an experimental mode is enabled. The code might change and using the normal logic is more stable.
        # sqlite-rag 0.1.4 exposes no public API for batch sentence scoring.
        rag = self.rag
        rag._ensure_initialized()
        engine = rag._engine
        settings = rag._settings
        engine.create_new_context()
        semantic_query = query

        if settings.use_prompt_templates:
            semantic_query = settings.prompt_template_retrieval_query.format(
                content=query
            )

        fts_query = " ".join(re.findall(r"\b\w+\b", query.lower())) + "*"
        query_embedding = engine.generate_embedding(semantic_query)
        results = engine.search_documents(query_embedding, fts_query, top_k=top_k)

        if not results or settings.top_k_sentences <= 0:
            return results

        scan = (
            "vector_quantize_scan_stream"
            if settings.quantize_scan
            else "vector_full_scan_stream"
        )

        chunk_ids = list(dict.fromkeys(result.chunk_id for result in results))

        sentences: dict[int, list[SentenceResult]] = {
            chunk_id: [] for chunk_id in chunk_ids
        }

        for start in range(0, len(chunk_ids), 500):
            batch = chunk_ids[start : start + 500]
            placeholders = ",".join("?" for _ in batch)
            rows = rag._conn.execute(
                f"""
                WITH candidates AS MATERIALIZED (
                    SELECT rowid AS sentence_id, chunk_id
                    FROM sentences
                    WHERE chunk_id IN ({placeholders})
                ),
                vec_matches AS (
                    SELECT s.chunk_id, v.rowid AS sentence_id,
                        row_number() OVER (
                            PARTITION BY s.chunk_id ORDER BY v.distance
                        ) AS rank_number,
                        v.distance
                    FROM {scan}('sentences', 'embedding', ?) AS v
                    JOIN candidates AS s ON s.sentence_id = v.rowid
                )
                SELECT v.chunk_id, v.sentence_id, v.rank_number, v.distance,
                    s.start_offset, s.end_offset,
                    COALESCE(
                        substr(c.content, s.start_offset + 1,
                               s.end_offset - s.start_offset), ''
                    ) AS content
                FROM vec_matches AS v
                JOIN sentences AS s ON s.rowid = v.sentence_id
                JOIN chunks AS c ON c.id = s.chunk_id
                WHERE v.rank_number <= ?
                ORDER BY v.chunk_id, v.rank_number
                """,
                [*batch, query_embedding, settings.top_k_sentences],
            ).fetchall()

            for row in rows:
                sentences[row["chunk_id"]].append(
                    SentenceResult(
                        id=row["sentence_id"],
                        chunk_id=row["chunk_id"],
                        content=row["content"].strip(),
                        rank=row["rank_number"],
                        distance=row["distance"],
                        start_offset=row["start_offset"],
                        end_offset=row["end_offset"],
                    )
                )

        for result in results:
            result.sentences = list(sentences[result.chunk_id])
            
        return results
