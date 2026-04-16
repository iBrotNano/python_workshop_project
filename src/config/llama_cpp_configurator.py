import os

from config.configuration import Configuration, configuration


class LlamaCppConfigurator:
    """Configurator for Llama.cpp specific settings."""

    def __init__(self, configuration: Configuration):
        """
        Initializes the LlamaCppConfigurator with the given configuration.

        :param configuration: The Configuration instance containing settings.
        """
        self._configuration = configuration

    def configure(self):
        """
        Configures environment variables for Llama.cpp based on the configuration settings.
        This includes enabling Vulkan GPU acceleration and setting the number of threads for embeddings.
        """
        os.environ["OMP_NUM_THREADS"] = f"{self._configuration.ai_embedding_threads}"
        os.environ["LLAMA_THREADS"] = f"{self._configuration.ai_embedding_threads}"
        os.environ["GGML_VULKAN_RUNNER"] = "1"
        os.environ["GGML_VULKAN_FENCE_TYPE"] = "2"
        os.environ["GGML_VULKAN_MAX_HEAP_SIZE"] = "0"
        os.environ["GGML_VULKAN_DISABLE"] = "0"
        os.environ["GGML_VULKAN_DEBUG"] = "0"

        if self._configuration.ai_use_vulcan_llama_backend:
            os.environ["LLAMA_VULKAN"] = "1"


# Shared instances used across the application.
# TODO: Stuff here should be instantiated by DI.
llama_cpp_configurator = LlamaCppConfigurator(configuration)
