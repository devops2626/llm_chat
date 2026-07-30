import json
import os
import openai
from search_tool import SearchOrganizer

# Old SDK style (works on iSH / 32-bit musl)
openai.api_key = os.getenv("OPENAI_API_KEY")

SYSTEM_PROMPT = """
You are an AI research assistant. Your goal is to answer user queries by gathering and synthesising information from the web.
Use web_search to find relevant sources and extract_content to read full page text when needed.
"""

# Old 0.28 "functions" schema
FUNCTIONS = [
    {
        "name": "web_search",
        "description": "Perform a web search for a given query.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query"},
                "num_results": {
                    "type": "integer",
                    "description": "Number of results to return",
                    "default": 5,
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "extract_content",
        "description": "Extract and clean text from a given URL.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "The URL to extract"},
            },
            "required": ["url"],
        },
    },
]


class ResearchAgent:
    def __init__(self, llm_client=None, search_api_key=None):
        """
        llm_client is ignored – we use the global openai module
        so the constructor signature stays compatible with older code.
        """
        self.search_tool = SearchOrganizer(
            search_api_key or os.getenv("SERPAPI_API_KEY")
        )
        self.messages = []
        self.max_turns = 5

    def run(self, user_query: str) -> str:
        self.messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_query},
        ]

        turn = 0
        while turn < self.max_turns:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=self.messages,
                functions=FUNCTIONS,
                function_call="auto",
            )

            message = response["choices"][0]["message"]
            self.messages.append(message)

            # Old API uses "function_call" (singular)
            if message.get("function_call"):
                func_name = message["function_call"]["name"]
                try:
                    args = json.loads(message["function_call"]["arguments"])
                except json.JSONDecodeError:
                    args = {}

                if func_name == "web_search":
                    tool_result = self.search_tool.web_search(**args)
                elif func_name == "extract_content":
                    tool_result = self.search_tool.extract_content(**args)
                else:
                    tool_result = f"Unknown function: {func_name}"

                self.messages.append(
                    {
                        "role": "function",
                        "name": func_name,
                        "content": tool_result
                        if isinstance(tool_result, str)
                        else json.dumps(tool_result),
                    }
                )
            else:
                return message.get("content") or ""

            turn += 1

        last = self.messages[-1]
        return last.get("content") or str(last)


def get_client():
    """Dummy helper so existing scripts that call OpenAI(...) keep working."""

    class _Dummy:
        pass

    return _Dummy()
