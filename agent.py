import json
from openai import OpenAI
from search_tool import SearchOrganizer

SYSTEM_PROMPT = """
You are an AI research assistant. Your goal is to answer user queries by gathering and synthesising information from the web.
Use web_search to find relevant sources and extract_content to read full page text when needed.
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Perform a web search for a given query.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query"},
                    "num_results": {"type": "integer", "description": "Number of results to return", "default": 5}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "extract_content",
            "description": "Extract and clean text from a given URL.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "The URL to extract"}
                },
                "required": ["url"]
            }
        }
    }
]

class ResearchAgent:
    def __init__(self, llm_client, search_api_key):
        self.llm = llm_client
        self.search_tool = SearchOrganizer(search_api_key)
        self.messages = []
        self.max_turns = 5

    def run(self, user_query: str) -> str:
        self.messages.append({"role": "system", "content": SYSTEM_PROMPT})
        self.messages.append({"role": "user", "content": user_query})

        turn = 0
        while turn < self.max_turns:
            response = self.llm.chat.completions.create(
                model="gpt-4",
                messages=self.messages,
                tools=TOOLS,
                tool_choice="auto"
            )
            assistant_msg = response.choices[0].message
            self.messages.append(assistant_msg)

            if assistant_msg.tool_calls:
                for tool_call in assistant_msg.tool_calls:
                    tool_name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments)

                    if tool_name == "web_search":
                        tool_result = self.search_tool.web_search(**args)
                    elif tool_name == "extract_content":
                        tool_result = self.search_tool.extract_content(**args)
                    else:
                        tool_result = "Unknown tool"

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_result
                    })
            else:
                return assistant_msg.content

            turn += 1

        return self.messages[-1].content
