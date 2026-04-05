# secondpass-multireview

A Claude Code plugin that sends your plans and code changes to other AI models for a second opinion via [OpenRouter](https://openrouter.ai).

When you invoke `/secondpass-multireview:secondpass_multireview`, Claude gathers your current plan, the git diff, and surrounding code context, then sends it to GPT-5.3 Codex and Gemini 3.1 Pro in parallel. You get back a structured review from each model covering correctness, risks, simplicity, and missing pieces.

## Installation

```bash
claude /plugin install https://github.com/stopman/secondpass-multireview
```

## Setup

Set your OpenRouter API key:

```bash
export OPENROUTER_API_KEY="sk-or-v1-..."
```

Get a key at [openrouter.ai/keys](https://openrouter.ai/keys).

## Usage

During any Claude Code session, invoke the skill:

```
/secondpass-multireview:secondpass_multireview
```

Claude will:
1. Gather your current plan summary
2. Collect the git diff of your changes
3. Read relevant surrounding code for context
4. Send all three sections to GPT-5.3 Codex and Gemini 3.1 Pro
5. Present each model's review and synthesize the feedback

## Customizing Models

Override the default models with an environment variable:

```bash
export SECONDPASS_MODELS="anthropic/claude-sonnet-4-6,meta-llama/llama-4-maverick"
```

Any model available on [OpenRouter](https://openrouter.ai/models) works.

## How It Works

- **No external dependencies** — uses Python stdlib only (`urllib`, `json`, `concurrent.futures`)
- **Parallel queries** — all models are queried simultaneously
- **Structured input** — models receive the plan, diff, and code context so reviews are grounded in actual code
- **Concise output** — each model's review is capped at ~400 words

## License

MIT
