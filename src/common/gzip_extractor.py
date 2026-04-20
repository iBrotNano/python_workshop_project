import logging
import gzip

from pathlib import Path
from typing import Callable
from common.terminal.progress_callback import ProgressCallback, emit_progress
from common.copy_stream import CopyStream

log = logging.getLogger(__name__)


class GzipExtractor:
    def __init__(self, gz_path: Path, extract_to: Path):
        """
        Initializes the GzipExtractor with the paths for the gzip file and the extraction destination.

        :param gz_path: Path to the gzip file to be extracted.
        :type gz_path: Path
        :param extract_to: Path where the extracted file will be stored.
        :type extract_to: Path
        """
        self._gz_path = gz_path
        self._extract_to = extract_to

    def extract(self, progress_callback: ProgressCallback | None = None):
        """
        Extracts the gzip file into the temp folder.

        :param progress_callback: Optional callback receiving neutral progress updates.
        :type progress_callback: ProgressCallback | None
        :raises OSError: If the gzip archive cannot be extracted.
        """
        log.info(f"Extracting {self._gz_path} to {self._extract_to}")

        with gzip.open(self._gz_path, "rb") as compressed_file:
            total_size = self._gz_path.stat().st_size

            emit_progress(
                progress_callback,
                phase="extract",
                description=f"Extracting {self._gz_path}",
                completed=0,
                total=total_size,
            )

            with self._extract_to.open("wb") as extracted_file:
                CopyStream.copy(
                    source=compressed_file,
                    target=extracted_file,
                    phase="extract",
                    description=f"Extracting {self._gz_path}",
                    total=total_size,
                    progress_callback=progress_callback,
                    position_reader=self._get_gzip_position_reader(compressed_file),
                )

        log.info(f"Stored extracted CSV export at {self._extract_to}")

    def _get_gzip_position_reader(
        self, compressed_file: gzip.GzipFile
    ) -> Callable[[], int] | None:
        """
        Creates a callback that reports the current read position in the gzip file.

        :param compressed_file: The gzip file being extracted.
        :type compressed_file: gzip.GzipFile
        :return: Callback returning the number of processed compressed bytes.
        :rtype: Callable[[], int] | None
        """
        file_object = getattr(compressed_file, "fileobj", None)

        if file_object is None:
            return None

        return file_object.tell
