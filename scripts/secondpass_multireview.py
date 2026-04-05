#!/usr/bin/env python3
"""Query multiple models via OpenRouter for a second opinion on a plan or code change."""

import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.request import Request, urlopen
from urllib.error import URLError

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

MODELS = [
    "openai/gpt-5.3-codex",
    "google/gemini-3.1-pro-preview",
]

SYSTEM_PROMPT = """\
You are a senior software engineer reviewing a proposed code change.
You will receive a structured review payload with up to three sections:
- **Plan**: What is being changed and why
- **Diff**: The actual git diff of changed code
- **Code Context**: Surrounding code that the diff modifies (functions, classes, callers)

Use ALL sections to give a grounded review. Reference specific lines from the diff
or context when pointing out issues. Cover:
1. **Correctness** — Will this work? Any bugs, logic errors, or regressions in the diff?
2. **Risks** — Security issues, edge cases, or failure modes visible in the code?
3. **Simplicity** — Is there a simpler approach? Any over-engineering?
4. **Missing pieces** — Anything important that was overlooked (tests, error handling, callers)?

Be direct. Skip praise. Focus on what could go wrong or be improved.
Keep your response under 400 words."""


def query_model(model: str, plan_text: str, api_key: str) -> dict:
    """Send plan to a single model and return the response."""
    payload = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Review this plan/change:\n\n{plan_text}"},
        ],
        "max_tokens": 2048,
        "temperature": 0.3,
    }).encode()

    req = Request(
        OPENROUTER_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/stopman/secondpass-multireview",
        },
        method="POST",
    )

    try:
        with urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
            return {
                "model": model,
                "response": data["choices"][0]["message"]["content"],
            }
    except (URLError, KeyError, json.JSONDecodeError) as e:
        return {"model": model, "error": str(e)}


def main():
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("Error: OPENROUTER_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    plan_text = sys.stdin.read().strip()
    if not plan_text:
        print("Error: No plan text provided on stdin", file=sys.stderr)
        sys.exit(1)

    models = MODELS
    # Allow overriding models via env var (comma-separated)
    if os.environ.get("SECONDPASS_MODELS"):
        models = [m.strip() for m in os.environ["SECONDPASS_MODELS"].split(",")]

    print(f"Querying {len(models)} models via OpenRouter...\n")

    with ThreadPoolExecutor(max_workers=len(models)) as pool:
        futures = {
            pool.submit(query_model, model, plan_text, api_key): model
            for model in models
        }
        results = []
        for future in as_completed(futures):
            results.append(future.result())

    # Print results sorted by model name for consistency
    for result in sorted(results, key=lambda r: r["model"]):
        model_name = result["model"].split("/")[-1]
        print(f"{'=' * 60}")
        print(f"  {model_name}")
        print(f"{'=' * 60}")
        if "error" in result:
            print(f"Error: {result['error']}\n")
        else:
            print(f"{result['response']}\n")


if __name__ == "__main__":
    main()
