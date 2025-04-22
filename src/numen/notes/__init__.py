"""Note management for Numen."""

import datetime
import os
import pathlib
import subprocess
from typing import Dict, List, Optional, Set, Union

import frontmatter
import yaml
from rich.console import Console
from rich.table import Table

from numen.config import get_editor, get_notes_dir

console = Console()


def create_note(title: str) -> pathlib.Path:
    """Create a new note with the given title."""
    date_prefix = datetime.datetime.now().strftime("%Y-%m-%d")
    slug = "".join(c if c.isalnum() or c in ['-', '_'] else '-' for c in title.lower().replace(" ", "-"))
    filename = f"{date_prefix}-{slug}.md"
    
    metadata = {
        "title": title,
        "date": datetime.datetime.now().isoformat(),
        "tags": [],
    }
    
    content = frontmatter.Post("", **metadata)
    content_str = frontmatter.dumps(content)
    
    notes_dir = get_notes_dir()
    os.makedirs(notes_dir, exist_ok=True)
    
    note_path = notes_dir / filename
    try:
        with open(note_path, "w", encoding="utf-8") as f:
            f.write(content_str)
    except Exception as e:
        console.print(f"[red]Error creating note: {e}[/red]")
        raise
    
    return note_path


def list_notes(tag: Optional[str] = None) -> List[pathlib.Path]:
    """List all notes, optionally filtered by tag."""
    notes_dir = get_notes_dir()
    os.makedirs(notes_dir, exist_ok=True)
    
    all_notes = list(notes_dir.glob("*.md"))
    
    if tag is None:
        return all_notes
    
    filtered_notes = []
    for note_path in all_notes:
        with open(note_path, "r", encoding="utf-8") as f:
            post = frontmatter.load(f)
            note_tags = post.get("tags", [])
            if tag in note_tags:
                filtered_notes.append(note_path)
    
    return filtered_notes


def display_notes(notes: List[pathlib.Path]) -> None:
    """Display a list of notes in a rich table."""
    table = Table(title="📚 Numen Notes")
    table.add_column("Date", style="cyan")
    table.add_column("Title", style="green")
    table.add_column("Tags", style="yellow")
    
    for note_path in notes:
        with open(note_path, "r", encoding="utf-8") as f:
            post = frontmatter.load(f)
            
        date = post.get("date", "")
        if isinstance(date, datetime.datetime):
            date_str = date.strftime("%Y-%m-%d")
        else:
            try:
                date_str = datetime.datetime.fromisoformat(date).strftime("%Y-%m-%d")
            except (ValueError, TypeError):
                date_str = str(date)
        
        title = post.get("title", note_path.stem)
        tags = post.get("tags", [])
        tags_str = ", ".join([f"#{tag}" for tag in tags])
        
        table.add_row(date_str, title, tags_str)
    
    console.print(table)


def edit_note(note_identifier: str) -> bool:
    """Open a note in the configured editor."""
    notes_dir = get_notes_dir()
    note_path = resolve_note_path(note_identifier)
    
    if note_path is None:
        console.print(f"[red]Note not found: {note_identifier}")
        return False
    
    editor = get_editor()
    subprocess.run([editor, str(note_path)], check=False)
    return True


def resolve_note_path(note_identifier: str) -> Optional[pathlib.Path]:
    """Resolve a note identifier to a full path."""
    notes_dir = get_notes_dir()
    os.makedirs(notes_dir, exist_ok=True)
    
    if os.path.isabs(note_identifier):
        path = pathlib.Path(note_identifier)
        if path.exists():
            return path
        return None
    
    direct_path = notes_dir / note_identifier
    if direct_path.exists():
        return direct_path
    
    if not note_identifier.endswith(".md"):
        md_path = notes_dir / f"{note_identifier}.md"
        if md_path.exists():
            return md_path
    
    candidates = []
    try:
        candidates = sorted(
            [p for p in notes_dir.glob(f"*{note_identifier}*.md")],
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
    except Exception as e:
        console.print(f"[red]Error finding notes: {e}[/red]")
    
    if candidates:
        return candidates[0]
    
    return None


def search_notes(query: str) -> List[pathlib.Path]:
    """Search for notes containing the query string."""
    notes_dir = get_notes_dir()
    all_notes = list(notes_dir.glob("*.md"))
    matching_notes = []
    
    for note_path in all_notes:
        with open(note_path, "r", encoding="utf-8") as f:
            content = f.read().lower()
            
        if query.lower() in content:
            matching_notes.append(note_path)
    
    return matching_notes


def update_tags(note_identifier: str, add_tags: List[str], remove_tags: List[str]) -> bool:
    """Update the tags for a note."""
    note_path = resolve_note_path(note_identifier)
    if note_path is None:
        console.print(f"[red]Note not found: {note_identifier}[/red]")
        return False
    
    try:
        with open(note_path, "r", encoding="utf-8") as f:
            post = frontmatter.load(f)
    except Exception as e:
        console.print(f"[red]Error reading note: {e}[/red]")
        return False
    
    current_tags = set(post.get("tags", []))
    
    for tag in add_tags:
        current_tags.add(tag)
    
    for tag in remove_tags:
        if tag in current_tags:
            current_tags.remove(tag)
    
    post["tags"] = sorted(list(current_tags))
    
    try:
        with open(note_path, "w", encoding="utf-8") as f:
            f.write(frontmatter.dumps(post))
    except Exception as e:
        console.print(f"[red]Error writing note: {e}[/red]")
        return False
    
    return True


def get_section_content(note_identifier: str, section: Optional[int] = None) -> Optional[str]:
    """Get content from a specific section of a note, or the entire note if section is None."""
    note_path = resolve_note_path(note_identifier)
    if note_path is None:
        console.print(f"[red]Note not found: {note_identifier}[/red]")
        return None
    
    try:
        with open(note_path, "r", encoding="utf-8") as f:
            post = frontmatter.load(f)
    except Exception as e:
        console.print(f"[red]Error loading note: {e}[/red]")
        return None
    
    content = post.content
    
    if section is None:
        return content
    
    sections = []
    current_section = []
    for line in content.split("\n"):
        if line.startswith("#"):
            if current_section:
                sections.append("\n".join(current_section))
                current_section = []
        current_section.append(line)
    
    if current_section:
        sections.append("\n".join(current_section))
    
    if not sections and content.strip():
        sections = [content.strip()]
    
    if not sections:
        console.print("[yellow]Note is empty. Nothing to process.[/yellow]")
        return None
    elif section < 0 or section >= len(sections):
        console.print(f"[red]Section {section} not found. Note has {len(sections)} sections (0-{len(sections)-1}).[/red]")
        return None
    
    return sections[section]


def update_note_content(note_identifier: str, new_content: str, section: Optional[int] = None, preserve_original: bool = True) -> bool:
    """Update the content of a note, either entirely or for a specific section.
    
    Args:
        note_identifier: The note to update
        new_content: The new content to add
        section: Optional section index to update (if None, updates entire note)
        preserve_original: If True, keeps the original text and appends AI-generated content
    """
    note_path = resolve_note_path(note_identifier)
    if note_path is None:
        console.print(f"[red]Note not found: {note_identifier}")
        return False
    
    try:
        with open(note_path, "r", encoding="utf-8") as f:
            post = frontmatter.load(f)
    except Exception as e:
        console.print(f"[red]Error reading note: {e}[/red]")
        return False
    
    content = post.content
    
    if section is None:
        if preserve_original:
            post.content = f"{content}\n\n## AI-Generated Content\n\n{new_content}"
        else:
            post.content = new_content
    else:
        sections = []
        current_section = []
        for line in content.split("\n"):
            if line.startswith("#"):
                if current_section:
                    sections.append("\n".join(current_section))
                    current_section = []
            current_section.append(line)
        
        if current_section:
            sections.append("\n".join(current_section))
        
        if not sections and content.strip():
            sections = [content]
            
        if not sections:
            console.print("[yellow]Note is empty. Cannot update.[/yellow]")
            return False
        elif section < 0 or section >= len(sections):
            console.print(f"[red]Section {section} not found. Note has {len(sections)} sections (0-{len(sections)-1}).[/red]")
            return False
        
        if preserve_original:
            original = sections[section]
            sections[section] = f"{original}\n\n### AI-Generated Content\n\n{new_content}"
        else:
            sections[section] = new_content
        
        post.content = "\n\n".join(sections)
    
    try:
        with open(note_path, "w", encoding="utf-8") as f:
            f.write(frontmatter.dumps(post))
    except Exception as e:
        console.print(f"[red]Error writing note: {e}[/red]")
        return False
    
    return True
