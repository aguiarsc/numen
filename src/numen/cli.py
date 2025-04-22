"""CLI for Numen."""

import os
import pathlib
import subprocess
from typing import List, Optional
from datetime import datetime

import typer
import frontmatter
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table

from numen.ai import process_text, get_ai_provider
from numen.config import get_ai_config, get_config, get_editor, get_notes_dir, ensure_config_exists
from numen.notes import (
    create_note,
    display_notes,
    edit_note,
    get_section_content,
    list_notes,
    resolve_note_path,
    search_notes,
    update_note_content,
    update_tags,
)

app = typer.Typer(
    name="numen",
    help="Numen - AI-Augmented Terminal Notepad",
    no_args_is_help=True,
    add_completion=False,
)
ai_app = typer.Typer(
    help="AI features for enhancing your notes",
    add_completion=False,
)
app.add_typer(ai_app, name="ai")

console = Console()


@app.callback()
def app_callback(ctx: typer.Context):
    """Numen - AI-Augmented Terminal Notepad

A Markdown-compatible notepad with AI integration."""
    ensure_config_exists()


@ai_app.callback()
def ai_callback(ctx: typer.Context):
    """AI features for enhancing your notes

Commands: expand, summarize, poetic, custom
Options: --section, --preview, --replace"""
    pass


@app.command("new")
def new_note(title: str = typer.Argument(..., help="Title of the new note")):
    """Create a new note with the given title.
    
    The note will be saved as a Markdown file with YAML frontmatter
    containing metadata like title, date, and tags.
    After creation, the note will open in your configured editor.
    
    Example:
      numen new "My New Note"
    """
    note_path = create_note(title)
    console.print(f"[green]Created note at:[/green] {note_path}")
    
    edit_note(str(note_path))


@app.command("list")
def list_notes_cmd(tag: Optional[str] = typer.Option(None, "--tag", "-t", help="Filter notes by tag")):
    """List all notes, optionally filtered by tag.
    
    Shows each note with its date, title, and tags in a formatted table.
    Use the --tag option to show only notes with a specific tag.
    
    Example:
      numen list
      numen list --tag important
    """
    notes = list_notes(tag)
    
    if not notes:
        if tag:
            console.print(f"[yellow]No notes found with tag: {tag}[/yellow]")
        else:
            console.print("[yellow]No notes found.[/yellow]")
        return
    
    display_notes(notes)


@app.command("edit")
def edit_note_cmd(note: str = typer.Argument(..., help="Note to edit (filename or partial name)")):
    """Open a note in the configured editor.
    
    You can specify the note by its exact filename, or by a partial name.
    Numen will search for notes that match the given string.
    
    Example:
      numen edit my-note
    """
    success = edit_note(note)
    if not success:
        console.print(f"[red]Failed to edit note: {note}[/red]")


@app.command("search")
def search_notes_cmd(query: str = typer.Argument(..., help="Search term")):
    """Search for notes containing the given text.
    
    Performs a case-insensitive search across all note contents.
    Returns a list of notes that contain the search term.
    
    Example:
      numen search keyword
    """
    notes = search_notes(query)
    
    if not notes:
        console.print(f"[yellow]No notes found containing: {query}[/yellow]")
        return
    
    console.print(f"[green]Found {len(notes)} notes containing '[bold]{query}[/bold]':[/green]")
    display_notes(notes)


@app.command("tag")
def tag_note(
    note: str = typer.Argument(..., help="Note to tag (filename or partial name)"),
    tags: List[str] = typer.Argument(..., help="Tags to add (+tag) or remove (no prefix)"),
):
    """Add or remove tags from a note.
    
    Add tags by prefixing with '+' (e.g., +important).
    Remove tags by using no prefix (e.g., draft).
    Tags are stored in the note's frontmatter and can be used for filtering.
    
    Example:
      numen tag my-note +important      # Add 'important' tag
      numen tag my-note draft           # Remove 'draft' tag
      numen tag my-note +urgent draft   # Add 'urgent' and remove 'draft'
    """
    add_tags = []
    remove_tags = []
    
    for tag in tags:
        if tag.startswith("+"):
            add_tags.append(tag[1:])
        else:
            remove_tags.append(tag)
    
    success = update_tags(note, add_tags, remove_tags)
    
    if success:
        add_msg = f"Added tags: {', '.join(add_tags)}" if add_tags else ""
        remove_msg = f"Removed tags: {', '.join(remove_tags)}" if remove_tags else ""
        if add_msg and remove_msg:
            console.print(f"[green]{add_msg}[/green]\n[yellow]{remove_msg}[/yellow]")
        elif add_msg:
            console.print(f"[green]{add_msg}[/green]")
        elif remove_msg:
            console.print(f"[yellow]{remove_msg}[/yellow]")
    else:
        console.print(f"[red]Failed to update tags for note: {note}[/red]")


@app.command("config")
def edit_config():
    """Edit the configuration file.
    
    Opens the TOML configuration file in your editor.
    The config file contains settings for:
    - AI providers and API keys
    - Editor preferences
    - Display settings
    - Directory paths
    
    Example:
      numen config
    """
    from numen.config import CONFIG_FILE
    
    editor = get_editor()
    
    subprocess.run([editor, CONFIG_FILE], check=False)
    console.print(f"[green]Edited config file: {CONFIG_FILE}[/green]")


@app.command("remove")
def remove_note(
    note: str = typer.Argument(..., help="Note to delete (filename or partial name)"),
    force: bool = typer.Option(False, "--force", "-f", help="Force deletion without confirmation"),
):
    """Delete a note.
    
    Permanently removes a note from the filesystem.
    By default, asks for confirmation before deletion.
    Use --force to skip the confirmation prompt.
    
    Example:
      numen remove my-note
      numen remove my-note --force
    """
    note_path = resolve_note_path(note)
    
    if note_path is None:
        console.print(f"[red]Note not found: {note}[/red]")
        return
    
    with open(note_path, "r") as f:
        post = frontmatter.load(f)
    
    title = post.get("title", note_path.stem)
    
    if not force:
        console.print(f"Are you sure you want to delete '[bold red]{title}[/bold red]'? (y/n): ", end="")
        confirm = input().lower().strip()
        if confirm != "y":
            console.print("[yellow]Deletion aborted.[/yellow]")
            return
    
    try:
        os.remove(note_path)
        console.print(f"[green]Successfully deleted note: [bold]{title}[/bold][/green]")
    except Exception as e:
        console.print(f"[red]Error deleting note: {e}[/red]")


@app.command("view")
def view_note(
    note: str = typer.Argument(..., help="Note to view (filename or partial name)"),
    raw: bool = typer.Option(False, "--raw", "-r", help="Show raw content including frontmatter"),
):
    """Display a note's content in the terminal with Markdown formatting.
    
    This allows you to quickly view a note without opening it in your editor.
    Use --raw to see the frontmatter and raw markdown instead of rendered content.
    
    Example:
      numen view my-note
      numen view my-note --raw
    """
    note_path = resolve_note_path(note)
    
    if note_path is None:
        console.print(f"[red]Note not found: {note}[/red]")
        return
    
    try:
        with open(note_path, "r", encoding="utf-8") as f:
            post = frontmatter.load(f)
    except Exception as e:
        console.print(f"[red]Error reading note: {e}[/red]")
        return
    
    title = post.get("title", note_path.stem)
    date = post.get("date", "")
    if isinstance(date, datetime):
        date_str = date.strftime("%Y-%m-%d %H:%M")
    else:
        try:
            date_str = datetime.fromisoformat(date).strftime("%Y-%m-%d %H:%M")
        except (ValueError, TypeError):
            date_str = str(date)
    
    tags = post.get("tags", [])
    tags_str = ", ".join([f"#{tag}" for tag in tags])
    
    if raw:
        console.print(f"[bold]File:[/bold] {note_path}")
        console.print(frontmatter.dumps(post))
    else:
        console.print(f"[bold cyan]{title}[/bold cyan]")
        console.print(f"[dim]Date: {date_str}[/dim]")
        if tags:
            console.print(f"[yellow]Tags: {tags_str}[/yellow]")
        console.print("---")
        
        if post.content.strip():
            md = Markdown(post.content)
            console.print(md)
        else:
            console.print("[italic dim]No content[/italic dim]")


@ai_app.command("expand")
def expand_text(
    note: str = typer.Argument(..., help="Note to expand (filename or partial name)"),
    section: Optional[int] = typer.Option(None, "--section", "-s", help="Section to expand (0-indexed)"),
    replace: bool = typer.Option(False, "--replace", "-r", help="Replace original text instead of preserving it"),
    preview: bool = typer.Option(False, "--preview", "-p", help="Preview expansion without updating the note"),
):
    """Expand a section of a note using AI.
    
    The AI will generate more detailed content based on your text.
    Text will be appended after your original content by default.
    
    Example:
      numen ai expand my-note
      numen ai expand my-note --section 2
      numen ai expand my-note --replace
      numen ai expand my-note --preview
    """
    content = get_section_content(note, section)
    if content is None:
        return
    
    console.print("[blue]Sending to AI for expansion...[/blue]")
    expanded = process_text("expand", content)
    
    if preview:
        console.print("\n[bold]Expanded version:[/bold]")
        console.print(Markdown(expanded))
        return
    
    note_path = resolve_note_path(note)
    if note_path is None:
        console.print(f"[red]Note not found: {note}[/red]")
        return
    
    success = update_note_content(note, expanded, section, preserve_original=not replace)
    
    if success:
        console.print("[green]Successfully expanded text![/green]")
        if not replace:
            console.print("[green]Original text preserved with AI content appended.[/green]")
    else:
        console.print("[red]Failed to update note with expanded text[/red]")
        console.print(expanded)


@ai_app.command("summarize")
def summarize_text(
    note: str = typer.Argument(..., help="Note to summarize (filename or partial name)"),
    section: Optional[int] = typer.Option(None, "--section", "-s", help="Section to summarize (0-indexed)"),
    replace: bool = typer.Option(False, "--replace", "-r", help="Replace original text instead of preserving it"),
    preview: bool = typer.Option(False, "--preview", "-p", help="Preview summary without updating the note"),
):
    """Summarize a note or section using AI.
    
    The AI will create a concise summary with key points.
    Summary will be appended after your original content by default.
    
    Example:
      numen ai summarize my-note
      numen ai summarize my-note --section 2
      numen ai summarize my-note --replace
      numen ai summarize my-note --preview
    """
    content = get_section_content(note, section)
    if content is None:
        return
    
    console.print("[blue]Sending to AI for summarization...[/blue]")
    summary = process_text("summarize", content)
    
    if preview:
        console.print("\n[bold]Summary:[/bold]")
        console.print(Markdown(summary))
        return
    
    success = update_note_content(note, summary, section, preserve_original=not replace)
    
    if success:
        console.print("[green]Successfully summarized text![/green]")
        if not replace:
            console.print("[green]Original text preserved with AI summary appended.[/green]")
    else:
        console.print("[red]Failed to update note with summary[/red]")
        console.print(summary)


@ai_app.command("poetic")
def poetic_rewrite(
    note: str = typer.Argument(..., help="Note to transform (filename or partial name)"),
    section: Optional[int] = typer.Option(None, "--section", "-s", help="Section to transform (0-indexed)"),
    replace: bool = typer.Option(False, "--replace", "-r", help="Replace original text instead of preserving it"),
    preview: bool = typer.Option(False, "--preview", "-p", help="Preview transformation without updating the note"),
):
    """Transform a note or section into poetry using AI.
    
    The AI will rewrite your text as a poetic piece.
    Poem will be appended after your original content by default.
    
    Example:
      numen ai poetic my-note
      numen ai poetic my-note --section 2
      numen ai poetic my-note --replace
      numen ai poetic my-note --preview
    """
    content = get_section_content(note, section)
    if content is None:
        return
    
    console.print("[blue]Sending to AI for poetic transformation...[/blue]")
    poem = process_text("poetic", content)
    
    if preview:
        console.print("\n[bold]Poetic version:[/bold]")
        console.print(Markdown(poem))
        return
    
    success = update_note_content(note, poem, section, preserve_original=not replace)
    
    if success:
        console.print("[green]Successfully transformed text into poetry![/green]")
        if not replace:
            console.print("[green]Original text preserved with poem appended.[/green]")
    else:
        console.print("[red]Failed to update note with poetic text[/red]")
        console.print(poem)


@ai_app.command("custom")
def custom_ai_instruction(
    note: str = typer.Argument(..., help="Note to process (filename or partial name)"),
    instruction: str = typer.Argument(..., help="Custom instruction for the AI"),
    section: Optional[int] = typer.Option(None, "--section", "-s", help="Section to process (0-indexed)"),
    replace: bool = typer.Option(False, "--replace", "-r", help="Replace original text instead of preserving it"),
    preview: bool = typer.Option(False, "--preview", "-p", help="Preview result without updating the note"),
):
    """Process a note with custom AI instructions.
    
    Provide any instruction to the AI model in plain language.
    Examples:
      - "Fix grammar and spelling errors"
      - "Convert this to a step-by-step tutorial"
      - "Make this more concise"
      - "Explain this concept for beginners"
    
    By default, original content is preserved and AI output is appended.
    
    Example:
      numen ai custom my-note "Fix grammar and style"
      numen ai custom my-note "Rewrite in a formal tone" --section 2
      numen ai custom my-note "Summarize the main points" --replace
      numen ai custom my-note "Generate a table of contents" --preview
    """
    content = get_section_content(note, section)
    if content is None:
        return
    
    console.print(f"[blue]Sending to AI with instruction: [bold]{instruction}[/bold][/blue]")
    
    custom_prompt = f"""{instruction}:

{content}
"""
    
    provider = get_ai_provider()
    result = provider.generate_text(custom_prompt)
    
    if preview:
        console.print("\n[bold]AI result:[/bold]")
        console.print(Markdown(result))
        return
    
    success = update_note_content(note, result, section, preserve_original=not replace)
    
    if success:
        console.print("[green]Successfully processed text with AI![/green]")
        if not replace:
            console.print("[green]Original text preserved with AI result appended.[/green]")
    else:
        console.print("[red]Failed to update note with AI result[/red]")
        console.print(result)


@app.command("backup")
def backup_notes(
    output_path: Optional[str] = typer.Argument(None, help="Output path for the backup zip file (default: numen_backup_YYYY-MM-DD.zip)"),
):
    """Create a backup of all notes as a zip file.
    
    This creates a zip archive containing all your notes, preserving folder structure.
    By default, the backup is saved in the current directory with a timestamp in the filename.
    
    Examples:
      numen backup                    # Default filename in current directory
      numen backup my-notes.zip       # Custom filename in current directory
      numen backup /path/to/backup.zip  # Custom path and filename
    """
    import zipfile
    
    notes_dir = get_notes_dir()
    
    if output_path is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
        output_path = f"numen_backup_{date_str}.zip"
    
    if not output_path.lower().endswith(".zip"):
        output_path += ".zip"
    
    try:
        output_path = os.path.expanduser(output_path)
        
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            note_files = list(notes_dir.glob("*.md"))
            total_files = len(note_files)
            
            if total_files == 0:
                console.print("[yellow]No notes found to back up.[/yellow]")
                return
            
            console.print(f"[blue]Backing up {total_files} notes to {output_path}...[/blue]")
            
            for i, note_path in enumerate(note_files):
                relative_path = os.path.basename(note_path)
                zipf.write(note_path, relative_path)
                
        console.print(f"[green]Successfully created backup at: {output_path}[/green]")
        console.print(f"[green]Backed up {total_files} notes.[/green]")
    except Exception as e:
        console.print(f"[red]Error creating backup: {e}[/red]")


@app.command("import")
def import_notes(
    import_path: str = typer.Argument(..., help="Path to the zip file to import"),
    overwrite: bool = typer.Option(False, "--overwrite", "-o", help="Overwrite existing notes with the same name"),
):
    """Import notes from a backup zip file.
    
    This extracts notes from a backup zip file created with the 'backup' command.
    By default, existing notes will not be overwritten unless --overwrite is specified.
    
    Example:
      numen import backup.zip
      numen import backup.zip --overwrite
    """
    import zipfile
    
    notes_dir = get_notes_dir()
    
    if not os.path.exists(import_path):
        console.print(f"[red]Import file not found: {import_path}[/red]")
        return
    
    if not import_path.lower().endswith(".zip"):
        console.print(f"[red]Import file must be a .zip file: {import_path}[/red]")
        return
    
    try:
        with zipfile.ZipFile(import_path, 'r') as zipf:
            md_files = [f for f in zipf.namelist() if f.endswith(".md")]
            
            if not md_files:
                console.print("[yellow]No notes found in the import file.[/yellow]")
                return
            
            console.print(f"[blue]Importing {len(md_files)} notes from {import_path}...[/blue]")
            
            imported = 0
            skipped = 0
            
            for file in md_files:
                target_path = os.path.join(notes_dir, os.path.basename(file))
                
                if os.path.exists(target_path) and not overwrite:
                    console.print(f"[yellow]Skipping existing note: {os.path.basename(file)}[/yellow]")
                    skipped += 1
                    continue
                
                zipf.extract(file, notes_dir)
                imported += 1
                
            console.print(f"[green]Successfully imported {imported} notes.[/green]")
            if skipped > 0:
                console.print(f"[yellow]Skipped {skipped} existing notes. Use --overwrite to replace them.[/yellow]")
    except Exception as e:
        console.print(f"[red]Error importing notes: {e}[/red]")


@app.command("stats")
def note_statistics():
    """Display statistics about your notes collection.
    
    Shows information like:
    - Total number of notes
    - Most used tags
    - Oldest and newest notes
    - Average note length
    - Notes created per month
    
    Example:
      numen stats
    """
    import collections
    import statistics
    
    notes_dir = get_notes_dir()
    all_notes = list(notes_dir.glob("*.md"))
    
    if not all_notes:
        console.print("[yellow]No notes found.[/yellow]")
        return
    
    note_data = []
    all_tags = []
    word_counts = []
    dates = []
    
    for note_path in all_notes:
        try:
            with open(note_path, "r", encoding="utf-8") as f:
                post = frontmatter.load(f)
                
            date = post.get("date", "")
            if isinstance(date, datetime):
                date_obj = date
            else:
                try:
                    date_obj = datetime.fromisoformat(date)
                except (ValueError, TypeError):
                    date_obj = None
            
            if date_obj:
                dates.append(date_obj)
            
            tags = post.get("tags", [])
            all_tags.extend(tags)
            
            word_count = len(post.content.split())
            word_counts.append(word_count)
            
            note_filename = os.path.basename(str(note_path))
            title_fallback = os.path.splitext(note_filename)[0]
            
            note_data.append({
                "path": note_path,
                "title": post.get("title", title_fallback),
                "date": date_obj,
                "tags": tags,
                "word_count": word_count,
            })
        except Exception as e:
            console.print(f"[red]Error processing {os.path.basename(str(note_path))}: {e}[/red]")
    
    console.print("[bold green]📊 Note Statistics[/bold green]")
    console.print(f"[cyan]Total notes:[/cyan] {len(all_notes)}")
    
    if dates:
        oldest_date = min(dates)
        newest_date = max(dates)
        console.print(f"[cyan]Date range:[/cyan] {oldest_date.strftime('%Y-%m-%d')} to {newest_date.strftime('%Y-%m-%d')}")
        
        month_counts = collections.Counter([d.strftime("%Y-%m") for d in dates])
        
        console.print("\n[bold]Notes per month:[/bold]")
        table = Table(show_header=True, header_style="bold")
        table.add_column("Month")
        table.add_column("Count", justify="right")
        
        for month, count in sorted(month_counts.items(), reverse=True)[:12]:
            year, month = month.split("-")
            month_name = datetime.strptime(month, "%m").strftime("%B")
            table.add_row(f"{month_name} {year}", str(count))
        
        console.print(table)
    
    if all_tags:
        tag_counts = collections.Counter(all_tags)
        top_tags = tag_counts.most_common(10)
        
        console.print("\n[bold]Top tags:[/bold]")
        table = Table(show_header=True, header_style="bold")
        table.add_column("Tag")
        table.add_column("Count", justify="right")
        table.add_column("% of Notes", justify="right")
        
        for tag, count in top_tags:
            percentage = (count / len(all_notes)) * 100
            table.add_row(tag, str(count), f"{percentage:.1f}%")
        
        console.print(table)
    
    if word_counts:
        avg_words = statistics.mean(word_counts)
        median_words = statistics.median(word_counts)
        min_words = min(word_counts)
        max_words = max(word_counts)
        
        console.print(f"\n[cyan]Word count statistics:[/cyan]")
        console.print(f"Average: {avg_words:.0f} words")
        console.print(f"Median: {median_words:.0f} words")
        console.print(f"Range: {min_words} to {max_words} words")


if __name__ == "__main__":
    app() 