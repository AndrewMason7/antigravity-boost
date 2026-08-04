---
name: boost
description: Display antigravity-boost plugin status, active features, and quick help guide for developers.
---

# 🚀 Antigravity Boost Plugin Status

When activated, report the plugin status and features to the user:

```markdown
### 🚀 `antigravity-boost` v1.0.0 is Active & Ready!

Your pair-programming session is automatically enhanced with:

- 💾 **1. Git WIP Checkpoints & Rollbacks**: Automatically saves your progress as a Git WIP commit when Antigravity finishes a task. Type `/checkpoint` anytime to save a custom snapshot, or `/undo` for a safe soft-rollback without losing code edits.
- 📦 **2. Auto-Dependency Resolver**: Automatically detects missing packages across Python, Node/TS, C/C++ headers, Rust, Go, and System CLI tools with interactive 1-click `ask_question` installs.
- 🛡️ **3. Smart Permission Guard**: Auto-approves safe read & test commands (`git status`, `pytest`, `npm test`) so you aren't spammed with popups, while protecting against dangerous file deletions (`rm -rf`) and subshell injections (`$()`).
```
