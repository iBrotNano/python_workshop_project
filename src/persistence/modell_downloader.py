import os

from huggingface_hub import hf_hub_download
from common.progress_callback import ProgressCallback
from config.configuration import Configuration


class ModellDownloader:
    def __init__(self, configuration: Configuration):
        self._configuration = configuration

    def download_model_if_not_exists(self, repo: str, filename: str):
        os.makedirs(self._configuration.ai_models_folder, exist_ok=True)
        local_path = os.path.join(self._configuration.ai_models_folder, filename)

        if os.path.exists(local_path):
            return

        hf_hub_download(
            repo_id=repo,
            filename=filename,
            local_dir=self._configuration.ai_models_folder,
        )
