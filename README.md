# llm_chat

Simple research agent that uses web search + content extraction.

## Quick start

```bash
pip install -r requirements.txt
export OPENAI_API_KEY=sk-...
export SERPAPI_API_KEY=...
python -c "from agent import ResearchAgent; print(ResearchAgent().run('What is LangGraph?'))"
```

## Platform notes

### iSH (iPhone / iPad)

iSH runs 32-bit Alpine (i686 + musl). Many modern packages fail to build:

- `openai >= 1.0` needs Rust extensions (`pydantic-core`, `jiter`) — **no i686 wheels**
- `aiohttp`, `multidict`, `yarl` often hit `libctf` / `qsort_r` linker errors

This repository is pinned to **openai==0.28.1** (last pure-Python release) so it can run on iSH.

See issues #3–#7 for the full dependency investigation.

### Normal Linux / macOS / Windows

You can upgrade to a modern OpenAI SDK and LangGraph if desired. The current `agent.py` uses the classic `ChatCompletion` + `functions` API.

## Human-in-the-loop

Examples of approval gates, review-and-edit, and confidence escalation are documented in the project issues and can be added on top of `ResearchAgent`.
