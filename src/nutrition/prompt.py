import ctypes
import json
import logging
import llama_cpp

from config.configuration import Configuration
from nutrition.retriever import Retriever
from persistence.modell_downloader import ModellDownloader
from typing import Any


log = logging.getLogger(__name__)


@llama_cpp.llama_log_callback
def _suppress_llama_console_logs(
    level: int,
    text: bytes,
    user_data: ctypes.c_void_p,
):
    """
    Little hack to suppress llama.cpp's console logs, which can be quite verbose
    and not useful for our application. We set a custom log callback that does
    nothing, effectively silencing all logs from llama.cpp.
    """
    return


class Prompt:
    """
    Handles the generation of nutrition information based on user queries.
    """

    _MAX_TOOL_CALL_ROUNDS = 4
    _shared_llm: llama_cpp.Llama | None = None
    _llama_log_callback_configured = False

    def __init__(self, configuration: Configuration):
        """
        Initializes the Prompt instance with the provided configuration.

        :param configuration: The configuration object containing settings for the prompt.
        :type configuration: Configuration

        """
        self._configuration = configuration

    def execute(
        self, query: str, top_k: int = 10, messages: list[dict[str, Any]] | None = None
    ):
        """
        Generates nutrition information based on the provided query.

        :param query: The search query to generate nutrition information for.
        :type query: str
        :param top_k: The number of top results to return, default is 10.
        :type top_k: int
        :param messages: The list of previous messages in the conversation, used for context.
        :type messages: list[dict[str, Any]] | None
        :return: A tuple containing the generated message content, search result, and updated messages.
        :rtype: tuple[str, dict | None, list[dict[str, Any]]]
        """
        ModellDownloader(self._configuration).download_model_if_not_exists(
            self._configuration.used_prompting_model["repo"],
            self._configuration.used_prompting_model["filename"],
        )

        if not Prompt._llama_log_callback_configured:
            llama_cpp.llama_log_set(_suppress_llama_console_logs, ctypes.c_void_p(0))
            Prompt._llama_log_callback_configured = True

        llm = self._get_or_create_llm()
        retrieved_results = self._retrieve_nutrition_data(query, top_k=top_k)
        retrieval_context = self._build_retrieval_context(retrieved_results)

        role_prompt = {
            "role": "system",
            "content": (
                "You are a professional nutrition assistant. "
                "Stay in your role as a professional nutrition assistant at all times but answer shortly and talk personally. "
                "Always answer based on the provided retrieval results. "
                "Always recommend a healthy and balanced diet based on the retrieved nutrition data. "
                "Only use product details that are present in the retrieval context. "
                "Keep your answers concise and focused on the most relevant information. "
                "You can use a function call tool to retrieve additional nutrition data if needed, but try to answer based on the initial retrieval results first. "
                "If the retrieval results are insufficient or no relevant results were found, say that clearly. "
                "Answer in the language of the query. "
                "Format the answer as Markdown. "
                f"List up to {top_k} relevant results in your answer and include the URL when available. "
                "\n\n"
                f"Retrieved nutrition data:\n{retrieval_context}",
            ),
        }

        if messages is None:
            messages = [role_prompt]

        messages += [
            {"role": "user", "content": query},
        ]

        response = self._complete_chat_with_tools(llm, messages)
        message_content = self._extract_message_content(response)
        messages += [{"role": "assistant", "content": message_content}]
        return (message_content, None, messages)

    def _get_or_create_llm(self) -> llama_cpp.Llama:
        """
        Returns a shared llama model instance and initializes it lazily.

        :return: The shared llama model instance.
        :rtype: llama_cpp.Llama
        """
        if Prompt._shared_llm is None:
            import os

            # Enable Vulkan GPU acceleration for better performance
            os.environ["LLAMA_VULKAN"] = "1"

            Prompt._shared_llm = llama_cpp.Llama(
                model_path=str(self._configuration.used_prompting_model_path),
                chat_format=self._configuration.used_prompting_model_chat_format,
                n_ctx=0,
                verbose=False,
                n_gpu_layers=-1,
            )

        return Prompt._shared_llm

    def _complete_chat_with_tools(
        self,
        llm: llama_cpp.Llama,
        messages: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Completes a chat request and handles optional nutrition retrieval tool calls.

        :param llm: The initialized llama model.
        :type llm: llama_cpp.Llama
        :param messages: The current chat message history.
        :type messages: list[dict[str, Any]]
        :return: The final chat completion response.
        :rtype: dict[str, Any]
        """
        message_payload: Any = messages
        tools: Any = self._get_tool_definitions()
        last_response: dict[str, Any] = {}

        for _ in range(self._MAX_TOOL_CALL_ROUNDS):
            response: Any = llm.create_chat_completion(
                messages=message_payload,
                stream=False,
                tools=tools,
                tool_choice="auto",
            )

            if not isinstance(response, dict):
                return {"choices": [{"message": {"content": str(response)}}]}

            last_response = response
            message = self._extract_message(response)
            tool_calls = message.get("tool_calls") or []

            if not tool_calls:
                return response

            messages.append(message)

            for tool_call in tool_calls:
                tool_response = self._execute_tool_call(tool_call)
                tool_call_id = tool_call.get("id", "tool-call")

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "content": json.dumps(tool_response, ensure_ascii=False),
                    }
                )

        log.warning("Maximum tool-call rounds reached without final model answer.")
        return last_response

    def _get_tool_definitions(self) -> list[dict[str, Any]]:
        """
        Returns the tool definitions for the nutrition assistant.

        :return: A list of available tool definitions.
        :rtype: list[dict[str, Any]]
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "retrieve_nutrition_data",
                    "description": "Retrieves nutrition data for a user query.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The nutrition search query.",
                            },
                            "top_k": {
                                "type": "integer",
                                "description": "The maximum number of results to return.",
                            },
                        },
                        "required": ["query"],
                    },
                },
            }
        ]

    def _execute_tool_call(self, tool_call: dict[str, Any]) -> dict[str, Any]:
        """
        Executes a tool call requested by the model.

        :param tool_call: The tool call payload from the model.
        :type tool_call: dict[str, Any]
        :return: The serialized tool response payload.
        :rtype: dict[str, Any]
        """
        function_payload = tool_call.get("function") or {}
        function_name = function_payload.get("name")

        if function_name != "retrieve_nutrition_data":
            return {"error": f"Unsupported tool call: {function_name}"}

        arguments = self._parse_tool_arguments(function_payload.get("arguments"))
        query = arguments.get("query")

        if not isinstance(query, str) or query.strip() == "":
            return {"error": "Missing required tool argument 'query'."}

        top_k = self._sanitize_top_k(arguments.get("top_k", 10))
        retrieved_results = self._retrieve_nutrition_data(query.strip(), top_k=top_k)

        return {
            "query": query,
            "top_k": top_k,
            "results": self._build_retrieval_context(retrieved_results),
        }

    def _build_retrieval_context(self, retrieved_results) -> str:
        """
        Builds a plain text context block from retrieved nutrition results.

        :param retrieved_results: The retrieved nutrition results.
        :type retrieved_results: list
        :return: The formatted retrieval context.
        :rtype: str
        """
        if not retrieved_results:
            return "No matching nutrition results were found."

        context_blocks = []

        for index, result in enumerate(retrieved_results, start=1):
            document = getattr(result, "document", None)
            content = getattr(document, "content", None)
            chunk_content = getattr(result, "chunk_content", None)
            text = content or chunk_content or str(result)
            context_blocks.append(f"Result {index}:\n{text}")

        return "\n\n".join(context_blocks)

    def _extract_message(self, response: dict[str, Any]) -> dict[str, Any]:
        """
        Extracts a chat message payload from a llama response.

        :param response: Raw llama chat completion response.
        :type response: dict[str, Any]
        :return: The first message block if available.
        :rtype: dict[str, Any]
        """
        choices = response.get("choices")

        if not isinstance(choices, list) or not choices:
            return {}

        first_choice = choices[0]

        if not isinstance(first_choice, dict):
            return {}

        message = first_choice.get("message")

        if not isinstance(message, dict):
            return {}

        return message

    def _extract_message_content(self, response: dict[str, Any]) -> str:
        """
        Extracts the textual message content from a llama response.

        :param response: Raw llama chat completion response.
        :type response: dict[str, Any]
        :return: The assistant text content.
        :rtype: str
        """
        message = self._extract_message(response)
        content = message.get("content")

        if isinstance(content, str) and content.strip() != "":
            return content

        if message.get("tool_calls"):
            return "No textual answer generated by model after tool calls."

        return "No response content returned by model."

    def _parse_tool_arguments(self, raw_arguments: Any) -> dict[str, Any]:
        """
        Parses tool call arguments into a dictionary.

        :param raw_arguments: Raw arguments from llama tool call.
        :type raw_arguments: Any
        :return: Parsed dictionary of arguments.
        :rtype: dict[str, Any]
        """
        if isinstance(raw_arguments, dict):
            return raw_arguments

        if not isinstance(raw_arguments, str):
            return {}

        try:
            parsed = json.loads(raw_arguments or "{}")
        except json.JSONDecodeError:
            return {}

        if not isinstance(parsed, dict):
            return {}

        return parsed

    def _sanitize_top_k(self, top_k: Any) -> int:
        """
        Sanitizes top_k to an integer within a safe range.

        :param top_k: Candidate top_k value.
        :type top_k: Any
        :return: Safe top_k value.
        :rtype: int
        """
        try:
            value = int(top_k)
        except (TypeError, ValueError):
            return 10

        return max(1, min(value, 50))

    def _retrieve_nutrition_data(self, query: str, top_k: int = 10):
        """
        Retrieves nutrition data for the given products.

        :return: A list of nutrition data for the given products.
        :rtype: list
        """
        with Retriever(self._configuration) as retriever:
            return retriever.retrieve(query, top_k=top_k)
