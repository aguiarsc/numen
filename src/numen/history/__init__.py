"""Version history management for Numen notes."""

import datetime
import json
import os
import pathlib
import shutil
from typing import Dict, List, Optional, Tuple, Union

import frontmatter
from rich.console import Console
from rich.table import Table

from numen.config import get_config

console = Console()

def get_history_dir() -> pathlib.Path:
    """Get the path to the history directory."""
    config = get_config()
    history_dir = pathlib.Path(os.path.expanduser(config.get("paths", {}).get("history_dir", "~/.numen/history")))
    os.makedirs(history_dir, exist_ok=True)
    return history_dir

def save_version(note_path: pathlib.Path, message: Optional[str] = None) -> str:
    """Save the current state of a note as a version.
    
    Args:
        note_path: Path to the note file
        message: Optional commit message describing the changes
        
    Returns:
        Version ID (timestamp) of the saved version
    """
    if not os.path.exists(note_path):
        raise FileNotFoundError(f"Note not found: {note_path}")
    
    # Get note content
    with open(note_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Create version ID based on timestamp
    version_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    
    # Get the stem name of the note
    note_name = note_path.stem
    
    # Create history directory for this note
    history_dir = get_history_dir() / note_name
    os.makedirs(history_dir, exist_ok=True)
    
    # Save content to version file
    version_path = history_dir / f"{version_id}.md"
    with open(version_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    # Save metadata
    metadata = {
        "version_id": version_id,
        "timestamp": datetime.datetime.now().isoformat(),
        "message": message or "Version saved",
        "note_path": str(note_path),
    }
    
    metadata_path = history_dir / f"{version_id}.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    
    return version_id

def list_versions(note_path: pathlib.Path) -> List[Dict]:
    """List all saved versions of a note.
    
    Args:
        note_path: Path to the note file
        
    Returns:
        List of version metadata dictionaries
    """
    note_name = note_path.stem
    history_dir = get_history_dir() / note_name
    
    if not os.path.exists(history_dir):
        return []
    
    versions = []
    for metadata_file in sorted(history_dir.glob("*.json"), reverse=True):
        with open(metadata_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)
            versions.append(metadata)
    
    return versions

def resolve_version_id(note_path: pathlib.Path, version_ref: Union[str, int]) -> Optional[str]:
    """Resolve a version reference to a specific version ID.
    
    The version reference can be:
    - An integer index (0 = oldest, -1 = newest)
    - A specific version ID string
    
    Args:
        note_path: Path to the note file
        version_ref: Version reference (index or ID)
        
    Returns:
        Actual version ID or None if not found
    """
    # If it's already a version ID (string), return it directly
    if isinstance(version_ref, str):
        return version_ref
    
    # Get all versions in chronological order (oldest first for positive indices)
    versions = list_versions(note_path)
    if not versions:
        return None
        
    # Reverse list for positive indices (0 = oldest)
    all_versions = list(reversed(versions))
    
    try:
        # Handle negative indexing (-1 = newest)
        if version_ref < 0 and abs(version_ref) <= len(all_versions):
            # For negative indices, use the non-reversed list
            return versions[version_ref]["version_id"]
            
        # Handle positive indexing (0 = oldest)
        if version_ref >= 0 and version_ref < len(all_versions):
            return all_versions[version_ref]["version_id"]
    except (IndexError, TypeError):
        pass
        
    return None

def get_version_content(note_name: str, version_ref: Union[str, int]) -> Optional[str]:
    """Get the content of a specific version of a note.
    
    Args:
        note_name: Name (stem) of the note
        version_ref: Version reference (ID or index)
        
    Returns:
        Content of the specified version, or None if not found
    """
    history_dir = get_history_dir() / note_name
    
    # If version_ref is an integer, resolve it to an actual version ID
    if isinstance(version_ref, int):
        note_path = pathlib.Path(os.path.join(get_history_dir().parent, "notes", f"{note_name}.md"))
        version_id = resolve_version_id(note_path, version_ref)
        if not version_id:
            return None
    else:
        version_id = version_ref
    
    version_path = history_dir / f"{version_id}.md"
    
    if not os.path.exists(version_path):
        return None
    
    with open(version_path, "r", encoding="utf-8") as f:
        return f.read()

def restore_version(note_path: pathlib.Path, version_ref: Union[str, int]) -> bool:
    """Restore a note to a previous version.
    
    Args:
        note_path: Path to the note file
        version_ref: Version reference (ID or index)
        
    Returns:
        True if successful, False otherwise
    """
    note_name = note_path.stem
    history_dir = get_history_dir() / note_name
    
    # Resolve the version reference to a specific version ID
    version_id = resolve_version_id(note_path, version_ref)
    if not version_id:
        console.print(f"[red]Version {version_ref} not found for note: {note_name}[/red]")
        return False
    
    version_path = history_dir / f"{version_id}.md"
    if not os.path.exists(version_path):
        console.print(f"[red]Version {version_id} not found for note: {note_name}[/red]")
        return False
    
    try:
        # Save current state before restoring (without recursion)
        save_backup_version(note_path)
        
        # Copy version content to note
        shutil.copy2(version_path, note_path)
        console.print(f"[green]Restored note to version: {version_id}[/green]")
        return True
    except Exception as e:
        console.print(f"[red]Error restoring version: {e}[/red]")
        return False

def save_backup_version(note_path: pathlib.Path) -> None:
    """Save a backup of the current state without generating a regular version.
    
    This is used before restoring to create an automatic backup.
    """
    if not os.path.exists(note_path):
        return
    
    # Get note content
    with open(note_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Create backup version ID
    backup_id = f"backup_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Get the stem name of the note
    note_name = note_path.stem
    
    # Create history directory for this note
    history_dir = get_history_dir() / note_name
    os.makedirs(history_dir, exist_ok=True)
    
    # Save content to backup file
    backup_path = history_dir / f"{backup_id}.md"
    with open(backup_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    # Save metadata
    metadata = {
        "version_id": backup_id,
        "timestamp": datetime.datetime.now().isoformat(),
        "message": "Automatic backup before restore",
        "note_path": str(note_path),
    }
    
    metadata_path = history_dir / f"{backup_id}.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

def compare_versions(note_name: str, version_ref1: Union[str, int], version_ref2: Union[str, int]) -> List[str]:
    """Compare two versions of a note and return the differences.
    
    Args:
        note_name: Name (stem) of the note
        version_ref1: First version reference (ID or index)
        version_ref2: Second version reference (ID or index)
        
    Returns:
        List of difference strings
    """
    try:
        import difflib
        
        # Resolve version references to specific version IDs
        note_path = pathlib.Path(os.path.join(get_history_dir().parent, "notes", f"{note_name}.md"))
        
        version_id1 = resolve_version_id(note_path, version_ref1)
        version_id2 = resolve_version_id(note_path, version_ref2)
        
        if not version_id1 or not version_id2:
            return ["Error: One or both versions not found"]
        
        content1 = get_version_content(note_name, version_id1)
        content2 = get_version_content(note_name, version_id2)
        
        if content1 is None or content2 is None:
            return ["Error: One or both versions not found"]
        
        # Split content into lines
        lines1 = content1.splitlines()
        lines2 = content2.splitlines()
        
        # Get unified diff
        diff = list(difflib.unified_diff(
            lines1, lines2, 
            fromfile=f"Version {version_id1}", 
            tofile=f"Version {version_id2}",
            lineterm=""
        ))
        
        return diff
    except ImportError:
        return ["Error: difflib module not available"]
    except Exception as e:
        return [f"Error comparing versions: {e}"]

def display_versions(versions: List[Dict]) -> None:
    """Display a list of versions in a rich table.
    
    Args:
        versions: List of version metadata dictionaries
    """
    table = Table(title="📚 Version History")
    table.add_column("Index", style="blue", justify="right")
    table.add_column("Version", style="cyan")
    table.add_column("Date", style="yellow")
    table.add_column("Time", style="yellow")
    table.add_column("Message", style="green")
    
    for i, version in enumerate(versions):
        version_id = version["version_id"]
        
        # Format timestamp
        timestamp = datetime.datetime.fromisoformat(version["timestamp"])
        date_str = timestamp.strftime("%Y-%m-%d")
        time_str = timestamp.strftime("%H:%M:%S")
        
        message = version["message"]
        
        # Reverse index so 0 is oldest (opposite of the list order)
        index = len(versions) - i - 1
        
        table.add_row(str(index), version_id, date_str, time_str, message)
    
    console.print(table)

def remove_history(note_path: pathlib.Path) -> bool:
    """Remove all version history for a note.
    
    Args:
        note_path: Path to the note file
        
    Returns:
        True if successful, False otherwise
    """
    note_name = note_path.stem
    history_dir = get_history_dir() / note_name
    
    if not os.path.exists(history_dir):
        console.print(f"[yellow]No history found for note: {note_name}[/yellow]")
        return True
    
    try:
        shutil.rmtree(history_dir)
        console.print(f"[green]History removed for note: {note_name}[/green]")
        return True
    except Exception as e:
        console.print(f"[red]Error removing history: {e}[/red]")
        return False
