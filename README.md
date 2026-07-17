# llm-agent

A small command-line coding agent built while working through the [Boot.dev "Build an AI Agent in Python" course](https://www.boot.dev/courses/build-ai-agent-python). You give it a
task in plain English, and it uses an LLM to decide which of a few file-system
tools to call, executes them, feeds the results back to the model, and repeats
until the task is done.

The agent operates on a sandboxed sample project (the `calculator/` app in this
repo) so its file reads, writes, and script executions can't escape a fixed
working directory.

## What it does

Given a prompt, the agent can:

- List files and directories in the working directory
- Read a file's contents (capped at `MAX_CHARS`, currently 10,000 characters)
- Write or overwrite a file (creating parent directories as needed)
- Run a Python file with optional arguments and capture its output

For example:

```bash
uv run main.py "fix the bug in the calculator's addition function" --verbose
```

The model might list the `calculator/` directory, read the relevant source
file, write a corrected version, then run the tests to confirm the fix — all in
a single command.

## How it works

The agent runs a feedback loop (up to 20 iterations):

1. Send the conversation (system prompt + history) to the model, advertising
   the available tools.
2. If the model returns tool calls, execute each one, then append both the
   model's turn and the tool results back into the message history.
3. If the model returns a plain-text response instead, that's the final answer
   and the loop stops.
4. If the loop hits the iteration cap without a final answer, it stops and says
   so.

The model is reached through [OpenRouter](https://openrouter.ai)'s
OpenAI-compatible API, using the free model router (`openrouter/free`). Note
that this router picks a different free model per request, so tool-calling
reliability varies run to run; a malformed response usually resolves on a
re-run.

## Project layout

```
.
├── calculator/                 # Sample app the agent operates on (the working directory)
├── functions/                  # Tool implementations, schemas, and the dispatcher
│   ├── get_files_info.py
│   ├── get_file_content.py
│   ├── write_file.py
│   ├── run_python_file.py
│   └── call_function.py        # get_schemas() + call_function() dispatch
├── config.py                   # MAX_CHARS (read-size cap)
├── prompts.py                  # System prompt
├── main.py                     # CLI entry point and feedback loop
├── test_get_files_info.py      # Tests, one per tool
├── test_get_file_content.py
├── test_run_python_file.py
├── test_write_file.py
├── pyproject.toml              # Project + dependencies (managed by uv)
├── uv.lock
└── .python-version
```

## Setup

This project uses [uv](https://docs.astral.sh/uv/) for dependency and
environment management.

1. Clone the repo and enter it:

   ```bash
   git clone https://github.com/ethan-hann/llm-agent.git
   cd llm-agent
   ```

2. Install dependencies (uv reads `pyproject.toml` and `uv.lock`):

   ```bash
   uv sync
   ```

3. Create a `.env` file in the project root with your OpenRouter API key:

   ```
   OPENROUTER_API_KEY=your-key-here
   ```

   Get a key from your [OpenRouter keys page](https://openrouter.ai/settings/keys).
   Free models have low daily rate limits.

## Usage

```bash
uv run main.py "your prompt here"
```

Add `--verbose` to see token counts and each tool call as it happens:

```bash
uv run main.py "read the contents of lorem.txt" --verbose
```

Example prompts:

- `"run tests.py"`
- `"get the contents of lorem.txt"`
- `"create a new README.md file with the contents '# calculator'"`
- `"what does the calculator do? explain how it works"`

## Configuration
You can configure the max number of characters that the LLM reads from a file as well as the static working directory the agent should use. These are defined in the `config.py` file:

```python
MAX_CHARS = 10000
WORKING_DIRECTORY = "./calculator"
```

> [!WARNING]
> The `WORKING_DIRECTORY` should be set to a directory you don't care about. See the [Safety Notes](#safety-notes) below for more info.

## Running the tests

Each tool has a standalone test module:

```bash
uv run test_get_files_info.py
uv run test_get_file_content.py
uv run test_run_python_file.py
uv run test_write_file.py
```

## Safety notes

All tool paths are relative to a fixed working directory, which is injected by
the caller rather than accepted from the model. Any path that resolves outside
the working directory is rejected, so the agent can't read or write arbitrary
files on the host. File reads are additionally capped at `MAX_CHARS` to keep
large files from blowing up the prompt.

That said, this is a learning project. The agent can write files and execute
Python within its sandbox, so point it at a throwaway directory (like the
included `calculator/` app), not something you care about.

## Acknowledgements

Built following the [Boot.dev "Build an AI Agent in Python" course](https://www.boot.dev/courses/build-ai-agent-python) (with some improvements; mainly the model-retry loop in `main.py`).