"""Template management for Numen."""

import os
import pathlib
import shutil
import subprocess
from typing import Dict, List, Optional

import frontmatter
import yaml
from rich.console import Console
from rich.table import Table

from numen.config import get_config

console = Console()

DEFAULT_TEMPLATES = {
    "meeting": {
        "title": "Meeting Notes",
        "description": "Template for recording meeting notes with agenda and action items.",
        "content": """# {{title}}

## Meeting Details
- **Date:** {{date}}
- **Time:** 
- **Location:** 
- **Attendees:** 

## Agenda
1. 
2. 
3. 

## Notes

## Action Items
- [ ] 
- [ ] 
- [ ] 

## Next Steps

"""
    },
    "journal": {
        "title": "Daily Journal",
        "description": "Template for daily journaling with prompts.",
        "content": """# {{title}} - {{date}}

## How I'm feeling today

## Achievements
- 

## Challenges
- 

## Gratitude
- 

## Tomorrow's Focus
- 

"""
    },
    "code_snippet": {
        "title": "Code Snippet",
        "description": "Template for saving and documenting code snippets.",
        "content": """# {{title}}

## Purpose
<!-- What does this code do? -->

## Language
<!-- Programming language -->

## Dependencies
<!-- Any required libraries or frameworks -->

## Code
```
// Your code here
```

## Usage Example
```
// Example of how to use the code
```

## Notes
<!-- Any additional information or context -->

"""
    },
    "calendar": {
        "title": "Event Planning",
        "description": "Template for planning and organizing events.",
        "content": """# {{title}}

## Event Details
- **Date:** {{date}}
- **Time:** 
- **Location:** 

## Description

## Agenda/Schedule
- 

## Participants
- 

## Resources Needed
- 

## Notes

"""
    },
    "project": {
        "title": "Project Outline",
        "description": "Template for outlining and tracking projects.",
        "content": """# {{title}}

## Project Overview

## Objectives
- 

## Timeline
- Start Date: {{date}}
- End Date: 

## Milestones
- [ ] 
- [ ] 
- [ ] 

## Resources
- 

## Notes

"""
    }
}

def get_templates_dir() -> pathlib.Path:
    """Get the path to the templates directory."""
    config = get_config()
    templates_dir = pathlib.Path(os.path.expanduser(config.get("paths", {}).get("templates_dir", "~/.numen/templates")))
    os.makedirs(templates_dir, exist_ok=True)
    return templates_dir

def ensure_default_templates() -> None:
    """Ensure that default templates exist in the templates directory."""
    templates_dir = get_templates_dir()
    
    for template_name, template_data in DEFAULT_TEMPLATES.items():
        template_file = templates_dir / f"{template_name}.md"
        
        # Only create if the template doesn't exist
        if not template_file.exists():
            metadata = {
                "title": template_data["title"],
                "description": template_data["description"],
                "template": True,
            }
            
            content = frontmatter.Post(template_data["content"], **metadata)
            
            with open(template_file, "w", encoding="utf-8") as f:
                f.write(frontmatter.dumps(content))
            
            console.print(f"[green]Created default template: {template_data['title']}[/green]")

def list_templates() -> List[pathlib.Path]:
    """List all available templates."""
    templates_dir = get_templates_dir()
    ensure_default_templates()
    
    return list(templates_dir.glob("*.md"))

def display_templates(templates: List[pathlib.Path]) -> None:
    """Display a list of templates in a rich table."""
    table = Table(title="📝 Numen Templates")
    table.add_column("Name", style="cyan")
    table.add_column("Title", style="green")
    table.add_column("Description", style="yellow")
    
    for template_path in templates:
        with open(template_path, "r", encoding="utf-8") as f:
            post = frontmatter.load(f)
        
        name = template_path.stem
        title = post.get("title", name)
        description = post.get("description", "")
        
        table.add_row(name, title, description)
    
    console.print(table)

def create_template(name: str, title: str, description: str, content: str) -> pathlib.Path:
    """Create a new template with the given parameters."""
    templates_dir = get_templates_dir()
    
    # Sanitize the name
    name = "".join(c if c.isalnum() or c in ['-', '_'] else '-' for c in name.lower().replace(" ", "-"))
    template_path = templates_dir / f"{name}.md"
    
    metadata = {
        "title": title,
        "description": description,
        "template": True,
    }
    
    template = frontmatter.Post(content, **metadata)
    
    with open(template_path, "w", encoding="utf-8") as f:
        f.write(frontmatter.dumps(template))
    
    return template_path

def edit_template(template_name: str) -> bool:
    """Open a template in the configured editor."""
    from numen.config import get_editor
    templates_dir = get_templates_dir()
    
    template_path = templates_dir / f"{template_name}.md"
    if not template_path.exists():
        template_path = templates_dir / f"{template_name}"
        if not template_path.exists():
            console.print(f"[red]Template not found: {template_name}[/red]")
            return False
    
    editor = get_editor()
    subprocess.run([editor, str(template_path)], check=False)
    return True

def delete_template(template_name: str, force: bool = False) -> bool:
    """Delete a template."""
    templates_dir = get_templates_dir()
    
    template_path = templates_dir / f"{template_name}.md"
    if not template_path.exists():
        template_path = templates_dir / f"{template_name}"
        if not template_path.exists():
            console.print(f"[red]Template not found: {template_name}[/red]")
            return False
    
    # Check if it's a default template
    is_default = template_path.stem in DEFAULT_TEMPLATES
    
    if is_default and not force:
        console.print(f"[yellow]Warning: '{template_path.stem}' is a default template. Use --force to delete it anyway.[/yellow]")
        return False
    
    if not force:
        confirm = input(f"Are you sure you want to delete the template '{template_path.stem}'? (y/N): ")
        if confirm.lower() not in ["y", "yes"]:
            console.print("[yellow]Template deletion cancelled.[/yellow]")
            return False
    
    try:
        os.remove(template_path)
        console.print(f"[green]Template deleted: {template_path.stem}[/green]")
        return True
    except Exception as e:
        console.print(f"[red]Error deleting template: {e}[/red]")
        return False

def get_template_content(template_name: str) -> Optional[Dict]:
    """Get the content and metadata of a template."""
    templates_dir = get_templates_dir()
    ensure_default_templates()
    
    template_path = templates_dir / f"{template_name}.md"
    if not template_path.exists():
        template_path = templates_dir / f"{template_name}"
        if not template_path.exists():
            return None
    
    with open(template_path, "r", encoding="utf-8") as f:
        post = frontmatter.load(f)
    
    return {
        "metadata": dict(post.metadata),
        "content": post.content
    }

def apply_template(template_name: str, title: str) -> str:
    """Apply a template with the given title and return the processed content."""
    template_data = get_template_content(template_name)
    if not template_data:
        return ""
    
    from datetime import datetime
    
    content = template_data["content"]
    
    # Replace variables in the template
    now = datetime.now()
    variables = {
        "title": title,
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M"),
        "datetime": now.strftime("%Y-%m-%d %H:%M"),
    }
    
    for key, value in variables.items():
        content = content.replace(f"{{{{{key}}}}}", value)
    
    return content

def reset_template(template_name: str) -> bool:
    """Reset a template to its default state."""
    if template_name not in DEFAULT_TEMPLATES:
        console.print(f"[red]No default template named '{template_name}' exists.[/red]")
        return False
    
    templates_dir = get_templates_dir()
    template_path = templates_dir / f"{template_name}.md"
    
    template_data = DEFAULT_TEMPLATES[template_name]
    metadata = {
        "title": template_data["title"],
        "description": template_data["description"],
        "template": True,
    }
    
    content = frontmatter.Post(template_data["content"], **metadata)
    
    with open(template_path, "w", encoding="utf-8") as f:
        f.write(frontmatter.dumps(content))
    
    console.print(f"[green]Reset template to default: {template_data['title']}[/green]")
    return True
