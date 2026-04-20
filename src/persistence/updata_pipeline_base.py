import logging

from pathlib import Path
from common.terminal.progress_callback import ProgressCallback, emit_progress
from urllib.request import urlopen
from common.copy_stream import CopyStream

log = logging.getLogger(__name__)


class UpdatePipelineBase:
    def _download(
        self,
        target_path: Path,
        url: str,
        progress_callback: ProgressCallback | None = None,
    ):
        """
        Downloads the configured Open Food Facts gzip export into the temp folder.

        :param target_path: The path where the downloaded file will be stored.
        :type target_path: Path
        :param url: The URL of the file to download.
        :type url: str
        :param progress_callback: Optional callback receiving neutral progress updates.
        :type progress_callback: ProgressCallback | None
        :raises OSError: If the remote file cannot be downloaded.
        """
        target_path.parent.mkdir(parents=True, exist_ok=True)

        log.info(f"Downloading {url}")

        with urlopen(url) as response:
            total_size = self._get_response_size(response)

            emit_progress(
                progress_callback,
                phase="download",
                description=f"Downloading {url}",
                completed=0,
                total=total_size,
            )

            with target_path.open("wb") as download_file:
                CopyStream.copy(
                    source=response,
                    target=download_file,
                    phase="download",
                    description=f"Downloading {url}",
                    total=total_size,
                    progress_callback=progress_callback,
                )

        log.info(f"Stored gzip export at {target_path}")

    def _get_response_size(self, response) -> int | None:
        """
        Reads the content length from the HTTP response if available.

        :param response: The HTTP response returned by urlopen.
        :return: Response size in bytes or None if unavailable.
        :rtype: int | None
        """
        content_length = response.headers.get("Content-Length")

        if content_length is None:
            return None

        return int(content_length)

    def _prepare(self, progress_callback: ProgressCallback | None = None):
        """
        Placeholder for preparation steps before running the pipeline.

        Subclasses should implement this method to perform any necessary preparation such as downloading files or extracting archives.

        :param progress_callback: Optional callback receiving neutral progress updates.
        :type progress_callback: ProgressCallback | None
        """
        raise NotImplementedError("Subclasses must implement the _prepare method.")

    def _persist(self, progress_callback: ProgressCallback | None = None):
        """
        Placeholder for persistence steps to store data into the database.

        Subclasses should implement this method to perform the actual data import into the database.

        :param progress_callback: Optional callback receiving neutral progress updates.
        :type progress_callback: ProgressCallback | None
        """
        raise NotImplementedError("Subclasses must implement the _persist method.")
