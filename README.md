# Numen - AI-Augmented Terminal Notepad

Numen is a sleek, Markdown-compatible terminal notepad that allows users to take notes, write snippets of code, and send selected text to AI models (Claude, GPT-4, Gemini, or local models like Ollama) for expansion, summarization, or transformation.

## Features

- **Markdown-first** editing experience
- **AI integration** with multiple providers:
  - Anthropic Claude 3
  - OpenAI GPT-4
  - Google Gemini
  - Ollama (local LLMs)
- **Tag-based** organization system
- **Powerful CLI** interface
- **Local file-based** storage (no cloud sync)
- **Rich text display** in terminal
- **Backup and import** for data safety
- **Statistics and insights** about your notes

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/aguiarsc/numen.git
cd numen

# Install dependencies
pip install -e .

# For development (includes testing tools)
pip install -e ".[dev]"
```

### Requirements

- Python 3.11+
- A terminal with a monospaced font that supports Unicode

## Setup

Numen stores its configuration and notes in your home directory at `~/.numen/`.

When first run, Numen will create a default configuration file at `~/.numen/config.toml`. You'll need to edit this file to add your API keys:

```bash
numen config
```

Update the config with your API keys:

```toml
[ai]
default_provider = "gemini"  # Options: anthropic, openai, gemini, ollama
anthropic_api_key = "your-api-key"
openai_api_key = "your-api-key"
gemini_api_key = "your-api-key"
ollama_base_url = "http://localhost:11434"
default_model = "gemini-1.5-flash"
temperature = 0.7

[editor]
default = "nvim"  # Will fall back to $EDITOR environment variable if not set

[paths]
notes_dir = "~/.numen/notes"
```

## Usage

### Basic Commands

```bash
# Create a new note
numen new "My new idea"

# List all notes
numen list

# List notes with specific tag
numen list --tag inspiration

# Edit a note
numen edit my-note.md

# View a note without editing
numen view my-note.md

# View raw note content (including frontmatter)
numen view my-note.md --raw

# Search for content
numen search "Python CLI"

# Tag management
numen tag my-note.md +inspiration -draft

# Delete a note
numen remove my-note.md

# Force delete without confirmation
numen remove my-note.md --force
```

### Statistics and Insights

```bash
# View statistics about your notes collection
numen stats
```

This provides insights including:
- Total number of notes
- Date range and notes per month
- Most used tags
- Word count statistics

### Backup and Import

```bash
# Backup all notes to a zip file
numen backup

# Specify a custom backup location
numen backup /path/to/my-backup.zip

# Import notes from a backup
numen import my-backup.zip

# Import and overwrite existing notes
numen import my-backup.zip --overwrite
```

### AI Integration

```bash
# Expand a section of your note
numen ai expand my-note.md --section 2

# Summarize an entire note
numen ai summarize my-note.md

# Preview a summary without modifying the note
numen ai summarize my-note.md --preview

# Replace original text with the AI output instead of preserving it
numen ai summarize my-note.md --replace

# Transform text into something poetic
numen ai poetic my-note.md --section 3

# Use a custom AI instruction
numen ai custom my-note.md "Rewrite this as a step-by-step tutorial"
```

## Note Structure

Notes are stored as Markdown files in `~/.numen/notes/` with YAML frontmatter:

```markdown
---
title: My Great Idea
date: 2023-04-21T15:30:45.123456
tags:
  - inspiration
  - project
  - python
---

# My Great Idea

This is the content of my note. I can use **Markdown** formatting.

## Details

More details about my idea go here.
```

## Command Reference

### Core Commands

| Command | Description |
|---------|-------------|
| `new <title>` | Create a new note with the given title |
| `list [--tag <tag>]` | List all notes, optionally filtered by tag |
| `edit <note>` | Open a note in your preferred editor |
| `view <note> [--raw]` | Display a note in the terminal without editing |
| `search <query>` | Find notes containing specific text |
| `tag <note> [+tag] [-tag]` | Add (+) or remove (-) tags from a note |
| `remove <note> [--force]` | Delete a note, with optional force flag to skip confirmation |
| `stats` | Display statistics about your note collection |

### File Management

| Command | Description |
|---------|-------------|
| `backup [path]` | Create a backup of all notes as a zip file |
| `import <path> [--overwrite]` | Import notes from a backup zip file |

### AI Features

| Command | Description |
|---------|-------------|
| `ai expand <note> [--section N] [--preview] [--replace]` | Expand content with AI |
| `ai summarize <note> [--section N] [--preview] [--replace]` | Summarize content with AI |
| `ai poetic <note> [--section N] [--preview] [--replace]` | Transform content into poetry with AI |
| `ai custom <note> <instruction> [--section N] [--preview] [--replace]` | Process with custom AI instruction |

### Configuration

| Command | Description |
|---------|-------------|
| `config` | Edit the configuration file |

## Development

For development, use the provided Makefile:

```bash
# Install development dependencies
make dev-install

# Run tests
make test

# Format code
make format

# Run linters
make lint

# Clean up artifacts
make clean
```

## License

MIT 