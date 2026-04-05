---
name: secondpass_multireview
description: Send the active Claude plan to other AI models (Codex 5.3, Gemini 3.1 Pro) via OpenRouter for a second opinion.
allowed-tools: Bash(source *secondpass_multireview*), Bash(git *), Bash(echo *), Read
---

# Second Pass Multi-Review

Get a second opinion on your current plan from other AI models via OpenRouter.

## Steps

1. **Gather context** — Build a comprehensive review payload with THREE sections. All three are required — do not skip the diff or code context.

   **Section 1: Plan summary** — Summarize from the conversation:
   - What is being changed and why (the bug, feature, or goal)
   - Key implementation details and approach
   - File paths and functions affected
   - Any trade-offs or alternatives considered

   **Section 2: Code diff** — Get the actual changes:
   - If changes are already committed: `git diff HEAD~1` (or appropriate range)
   - If changes are staged/unstaged: `git diff` and/or `git diff --cached`
   - If this is a pre-implementation plan, skip this section

   **Section 3: Relevant code context** — Read and include surrounding code that reviewers need to understand the change:
   - The full function/class containing each change (not just the changed lines)
   - Any callers or dependencies that interact with the changed code
   - Related tool/prompt definitions if the change affects AI behavior
   - Keep each snippet to ~50 lines max, use `# ... (trimmed)` for long sections

2. **Write a temp file** — Assemble all sections into a temp file, then pipe to the script:
   ```bash
   source ~/.zshrc 2>/dev/null && python3 scripts/secondpass_multireview.py < /tmp/secondpass_review.md
   ```

   Format the temp file as:
   ```
   ## Plan
   <plan summary>

   ## Diff
   ```diff
   <git diff output>
   ```

   ## Code Context
   ### <filename:function_name>
   ```python
   <relevant surrounding code>
   ```
   ```

   The script queries these models in parallel via OpenRouter:
   - **GPT-5.3 Codex** (OpenAI)
   - **Gemini 3.1 Pro** (Google)

   Override models with: `SECONDPASS_MODELS="model/a,model/b" python3 scripts/secondpass_multireview.py`

3. **Present results** — Show each model's feedback clearly, organized by model. Highlight any:
   - Consensus across models (things multiple models flag)
   - Disagreements worth considering
   - Actionable suggestions

4. **Summarize** — End with a brief synthesis: what the models agree on, key concerns raised, and whether the plan should be adjusted.

## Requirements

- `OPENROUTER_API_KEY` environment variable must be set
- No external Python dependencies required (uses stdlib only)
