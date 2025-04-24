<p align="center">
  <a href="https://github.com/aguiarsc/numen/releases"><img src="https://img.shields.io/github/v/release/aguiarsc/numen?style=flat-square" alt="Latest Release"></a>
  <a href="https://github.com/aguiarsc/numen/blob/main/LICENSE"><img src="https://img.shields.io/github/license/aguiarsc/numen?style=flat-square" alt="License"></a>
</p>

# ✨ Numen — AI-Augmented Terminal Notepad

**Numen** is a sleek, Markdown-first terminal notepad that brings your notes to life with the power of AI. Write code snippets, brainstorm ideas, and transform text seamlessly with models like **Claude 3**, **GPT-4**, **Gemini**, or local engines like **Ollama** — all from the comfort of your terminal.

---

https://github.com/user-attachments/assets/029ed3b6-e5f1-4087-9b9e-44406e2ad660

---

## 🚀 Features

- 📝 **Markdown-first editing** experience
- 🤖 **Multi-AI integration**: Claude 3, GPT-4, Gemini, Ollama
- 🏷️ **Tag-based** note organization
- 📋 **Template system** for different note types
- 📜 **Version history** with diff comparisons
- ⚡ **Powerful CLI** interface
- 💾 **Local-first** storage (no cloud, full control)
- 🖼️ **Rich-text terminal display**
- 🔐 **Backup & import** functionality
- 📊 **Stats & insights** on your note-taking habits

---

## 📦 Installation

### 🛠 From Source

```bash
# Clone the repo
git clone https://github.com/aguiarsc/numen.git
cd numen

# Install core (no AI)
pip install -e .

# Add AI provider support:
pip install -e ".[gemini]"     # Google Gemini (Rust-free)
pip install -e ".[anthropic]"  # Claude 3 (needs Rust)
pip install -e ".[openai]"     # OpenAI GPT (needs Rust)

# All providers
pip install -e ".[all-ai]"

# For development (includes tests, linters, etc.)
pip install -e ".[dev]"
```

### 🐧 Arch Linux (and friends)

Arch Linux uses an externally managed environment for Python packages. The recommended installation method is using the install script which automatically detects and uses pipx:

```bash
# Clone the repo
git clone https://github.com/aguiarsc/numen.git
cd numen

# Run the install script (includes all AI providers by default)
./install.sh --all-ai

# Or for minimal installation without AI features
./install.sh
```

This installation method:
- Uses pipx to create an isolated environment
- Avoids conflicts with system packages
- Makes uninstallation cleaner (`./uninstall.sh` will use pipx too)
- Works with Arch's PEP 668 externally managed environment

### 🧰 Rust Requirements

Claude and GPT integrations depend on Rust. You can:

1. Skip AI and use it as a standard notepad  
2. Use **Gemini** or **Ollama** (no Rust required)  
3. Install all AI tools if Rust is available

Numen smartly detects what’s available and falls back gracefully.

---

## ⚙️ Configuration

Numen stores config and notes in `~/.numen/`.

First run:

```bash
numen config
```

This creates `~/.numen/config.toml`. Add your API keys:

```toml
[ai]
default_provider = "gemini"
anthropic_api_key = "your-api-key"
openai_api_key = "your-api-key"
gemini_api_key = "your-api-key"
ollama_base_url = "http://localhost:11434"
default_model = "gemini-1.5-flash"
temperature = 0.7

[editor]
default = "nvim"

[paths]
notes_dir = "~/.numen/notes"
```

---

## 💡 Usage

### ✍️ Core CLI Commands

```bash
numen new "Note title"                    # Create a note
numen new "Meeting Notes" -t meeting      # Create from template
numen list                                # List all notes
numen list --tag idea                     # Filter by tag
numen edit my-note                        # Edit in $EDITOR
numen view my-note                        # Read-only display
numen search "regex"                      # Fuzzy search
numen tag my-note +inspo                  # Add or remove tags
numen remove my-note                      # Delete note
```

### 📋 Templates

```bash
numen templates list                      # List all templates
numen templates create book-review        # Create new template
numen templates edit meeting              # Edit a template
numen templates show journal              # View template content
numen templates delete my-template        # Delete a template
numen templates reset meeting             # Reset default template
```

### 📜 Version History

```bash
numen history save my-note -m "Comment"   # Create a version
numen history list my-note                # List all versions
numen history view my-note 0              # View oldest version
numen history restore my-note 1           # Revert to second oldest version
numen history diff my-note 0 1            # Compare oldest vs second version
numen history remove my-note              # Delete all version history
```

### 📈 Stats & Insights

```bash
numen stats
```

- Total notes
- Monthly breakdown
- Top tags
- Word count stats

### 📦 Backup & Restore

```bash
numen backup ./backup.zip             # Create zip
numen import ./backup.zip             # Restore
numen import ./backup.zip --overwrite # Overwrite existing
```

### 🧠 AI Commands

```bash
numen ai expand my-note --section 2                 # Expand section
numen ai summarize my-note                          # Summarize
numen ai summarize my-note --preview                # Dry run
numen ai summarize my-note --replace                # Inline replace
numen ai poetic my-note --section 3                 # Make it lyrical
numen ai custom my-note "Make it a love letter"     # Freeform AI prompt
```

---

## 🗃 Note Structure

Notes are stored in `~/.numen/notes/` as Markdown with frontmatter:

```markdown
---
title: A Bright Idea
date: 2023-04-21T15:30:45
tags: [inspiration, python, cli]
---

# A Bright Idea

Everything begins here.

## Details

Markdown. Syntax. Bliss.
```

---

## 🧾 Command Reference

### Core

| Command                  | Description                             |
|--------------------------|-----------------------------------------|
| `new <title>`            | Create a new note                       |
| `new <title> -t <template>` | Create note from template            |
| `list [--tag <tag>]`     | List all notes (filtered if needed)     |
| `edit <note>`            | Edit in your default terminal editor    |
| `view <note> [--raw]`    | View content (raw optional)             |
| `search <query>`         | Fuzzy search your notes                 |
| `tag <note> [+tag] [-tag]`| Manage tags on notes                   |
| `remove <note> [--force]`| Delete note (with optional force)       |
| `stats`                  | Show statistics                         |

### Templates

| Command                      | Description                          |
|------------------------------|--------------------------------------|
| `templates list`             | List all available templates         |
| `templates create <name>`    | Create a new template                |
| `templates edit <name>`      | Edit an existing template            |
| `templates show <name>`      | Display a template's content         |
| `templates delete <name>`    | Delete a template                    |
| `templates reset <name>`     | Reset a default template             |

### Version History

| Command                       | Description                         |
|-------------------------------|-------------------------------------|
| `history save <note> [-m]`    | Create a version with message       |
| `history list <note>`         | List all versions of a note         |
| `history view <note> <idx>`   | View a specific version (by index or ID) |
| `history restore <note> <idx>`| Revert to a previous version        |
| `history diff <note> <v1> <v2>` | Compare two versions              |
| `history remove <note>`       | Delete all version history          |

### Backup & Restore

| Command                | Description                            |
|------------------------|----------------------------------------|
| `backup [path]`        | Backup all notes into a zip archive    |
| `import <path>`        | Restore from a backup zip              |
| `import <path> --overwrite`| Overwrite notes on restore         |

### AI Tools

| Command                                              | Description                               |
|------------------------------------------------------|-------------------------------------------|
| `ai expand <note>`                                   | Expand content using AI                   |
| `ai summarize <note>`                                | Generate summaries                        |
| `ai poetic <note>`                                   | Make it poetic                            |
| `ai custom <note> "<instruction>"`                   | Custom AI task                            |
| `--section N`, `--preview`, `--replace` (any command) | Modify how AI interacts with note content |

---

## 🛠 Development

```bash
make dev-install  # Install dev deps
make test         # Run test suite
make lint         # Lint code
make format       # Format code
make clean        # Clean up
```

---

## 🧠 Philosophy

> *“A good note is a thought that refused to be forgotten.”*

Numen is for tinkerers, thinkers, and terminal romantics. It’s a place to write raw ideas and refine them with the help of machines — all while staying offline, markdown-pure, and in full control.
