---
trigger: always_on
---

# Flow Conventions Rule

1. **Adapt to Local Conventions**: Automatically inspect project config files (`package.json`, `tsconfig.json`, `pyproject.toml`, `.eslintrc`) and follow existing naming, formatting, and structural patterns.
2. **Interactive Dependency Prompting**: When missing dependencies are detected, present clear multiple-choice options using `ask_question` allowing installation all at once, item-by-item, or skipping.
3. **Unhandled Failure Fallback & Referral**: If a command or test fails and the script could NOT automatically recognize the exact missing dependency, DO NOT guess or fail silently. Analyze the error log and immediately call `ask_question` to present 2–3 plausible troubleshooting options or potential root causes to the user, allowing them to choose how to proceed.
