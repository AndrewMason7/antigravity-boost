# 🚀 `antigravity-boost`

> **Boost your developer productivity with zero friction, automated Git checkpoints, 1-click dependency installs, and smart permission gating.**  
> `antigravity-boost` is an essential productivity plugin for **Google Antigravity** engineered to give you complete peace of mind while pair-programming with AI.

---

## ⚡ 1-Line Installation (Mac, Windows & Linux)

Run this single command in your terminal to install `antigravity-boost` globally:

```bash
npx @andrewmason7/antigravity-boost
```

*Or install via cURL:*

```bash
curl -sSL https://raw.githubusercontent.com/AndrewMason7/antigravity-boost/main/install.sh | bash
```

*Or install manually via Git clone:*

```bash
mkdir -p ~/.gemini/config/plugins/
git clone https://github.com/AndrewMason7/antigravity-boost.git ~/.gemini/config/plugins/antigravity-boost
```

---

## 💡 Why You Need `antigravity-boost`

Pair-programming with AI agents should accelerate your work, not slow you down:

- ❌ **Lost Progress**: Closing your session or switching tasks and realizing uncommitted code changes disappeared.
- ❌ **Cryptic Import Errors**: Having your agent stall because `cv2`, `requests`, `express`, or `docker` isn't installed.
- ❌ **Permission Fatigue**: Being forced to click "Approve" 50 times a session for simple commands like `git status` or `pytest`.

`antigravity-boost` runs silently in the background to solve **all** of these problems automatically.

---

## ✨ Features Built for Your Peace of Mind

### 💾 1. Automatic & Manual Git WIP Checkpoints
- **Auto WIP Checkpoints**: Whenever Antigravity completes a task (`model_stop`), your progress is automatically saved into a lightweight Git WIP commit (`wip(boost): auto-checkpoint...`).
- **Commit History Hygiene**: Amends previous WIP commits so your `git log` stays clean instead of filling up with 20 snapshot commits.
- **Instant Safety Net (`/checkpoint` & `/undo`)**: Type `/checkpoint` anytime to save a snapshot, or `/undo` for a soft rollback (`git reset --soft HEAD~1`). **Zero code or file edits are ever deleted.**
- **Zero Workspace Clutter**: Keeps all internal state files in OS Temp (`$TMPDIR`), ensuring **zero junk files ever enter your Git repository**.

### 📦 2. 1-Click Interactive Dependency Resolver
- **Detects Missing Packages Instantly**: Automatically identifies missing imports across **Python**, **Node/TS**, **C/C++ Headers**, **Rust**, **Go**, and **System CLI tools** (`docker`, `terraform`, `jq`, `gh`, `ffmpeg`).
- **Smart Mappings**: Auto-maps ambiguous import names to canonical package names (`cv2` → `opencv-python`, `PIL` → `Pillow`, `bs4` → `beautifulsoup4`, `sklearn` → `scikit-learn`, `yaml` → `pyyaml`, etc.).
- **PEP 668 & Monorepo Aware**: Detects virtualenvs (`.venv`), lockfiles (`pnpm`, `yarn`, `bun`, `poetry`, `uv`), and Homebrew Python environments.
- **Interactive UI Prompt**: Presents clear `ask_question` options in Antigravity chat to install all missing dependencies at once with a single click.
- **Infinite Loop Protection**: Remembers skipped packages and caps install prompts at **max 2 attempts** to protect your API token budget.

### 🛡️ 3. Smart Permission Guard (Zero Popup Spams)
- **Auto-approves safe read & test commands**: Instantly grants execution for `git status`, `git diff`, `npm test`, `pytest`, `cargo check`, `go test`, `ls`, and `cat` so you can focus on coding without popups.
- **Strictly guards destructive operations**: Requires explicit human confirmation for dangerous operations like `rm -rf`, `git reset --hard`, `git push --force`, or database drops.
- **Subshell & Chained Command Security**: Intercepts hidden subshell tricks (`$()`, backticks, `$VAR`) and chained operators (`&&`, `;`) to ensure dangerous commands can never hide inside safe ones.
- **Plain-English Warnings**: Clear explanations tell you *why* a command requires approval before you click run.

---

## 🎮 How to Use in Antigravity

Just talk to Antigravity normally! `antigravity-boost` works silently behind the scenes.

| Command / Trigger | What It Does |
| :--- | :--- |
| **Type `/boost`** | Displays a visual status badge confirming all plugin guards & features are active. |
| **Type `/checkpoint`** | Manually saves your current work snapshot to Git. |
| **Type `/undo`** | Soft rolls back to your previous checkpoint without deleting your code. |
| **Missing Module Error** | Automatically triggers a 1-click package installation menu in chat. |

---

## ⚙️ User Customization (`config.json`)

Customize `antigravity-boost` to fit your personal workflow by editing `config.json`:

```json
{
  "auto_git_checkpoints": true,
  "max_install_attempts": 2,
  "custom_safe_patterns": ["^\\s*make\\s+test\\b"],
  "custom_destructive_patterns": [],
  "debug_mode": false
}
```

---

## 📄 License

MIT License - Built for the Antigravity developer community.
