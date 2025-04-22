"""Utility functions for Numen."""

import os
import re
from typing import Dict, List, Optional, Set, Tuple

from rich.console import Console
from rich.markdown import Markdown

console = Console()


def display_markdown(text: str) -> None:
    """Display text as Markdown in the terminal."""
    md = Markdown(text)
    console.print(md)


def extract_sections(content: str) -> List[Tuple[str, str]]:
    """Extract sections from Markdown content.
    
    Returns a list of (header, content) tuples.
    """
    if not content.strip():
        return [("", "")]
    
    pattern = r"(^#{1,6}\s+.*$)"
    parts = re.split(pattern, content, flags=re.MULTILINE)
    
    sections = []
    current_header = ""
    current_content = ""
    
    for i, part in enumerate(parts):
        if re.match(pattern, part, re.MULTILINE):
            if i > 0:
                sections.append((current_header, current_content.strip()))
            current_header = part
            current_content = ""
        else:
            current_content += part
    
    if current_header or current_content:
        sections.append((current_header, current_content.strip()))
    
    if not sections:
        sections = [("", content.strip())]
    
    return sections


def count_tokens(text: str) -> int:
    """Roughly estimate the number of tokens in a text.
    
    This is a very basic approximation. For more accuracy,
    you should use the tokenizer specific to your model.
    """
    return len(text) // 4


def chunk_text(text: str, max_tokens: int = 4000) -> List[str]:
    """Split text into chunks that fit within max_tokens."""
    estimated_tokens = count_tokens(text)
    
    if estimated_tokens <= max_tokens:
        return [text]
    
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""
    current_tokens = 0
    
    for paragraph in paragraphs:
        paragraph_tokens = count_tokens(paragraph)
        
        if paragraph_tokens > max_tokens:
            sentences = re.split(r'(?<=[.!?])\s+', paragraph)
            for sentence in sentences:
                sentence_tokens = count_tokens(sentence)
                
                if current_tokens + sentence_tokens <= max_tokens:
                    current_chunk += sentence + " "
                    current_tokens += sentence_tokens
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence + " "
                    current_tokens = sentence_tokens
        else:
            if current_tokens + paragraph_tokens <= max_tokens:
                current_chunk += paragraph + "\n\n"
                current_tokens += paragraph_tokens
            else:
                chunks.append(current_chunk.strip())
                current_chunk = paragraph + "\n\n"
                current_tokens = paragraph_tokens
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks


def optimize_large_content(content: str, max_size: int = 100000) -> str:
    """Optimize large content for AI processing to reduce token usage.
    
    For very large notes, this will intelligently trim the content
    to stay under the token limit while preserving important parts.
    
    Args:
        content: The note content
        max_size: Maximum character size (approx. tokens * 4)
        
    Returns:
        Optimized content ready for AI processing
    """
    if len(content) <= max_size:
        return content
        
    console.print(f"[yellow]Note is very large ({len(content):,} chars). Optimizing for AI processing...[/yellow]")
    
    sections = extract_sections(content)
    
    if len(sections) <= 1:
        first_part = content[:max_size // 2]
        last_part = content[-(max_size // 2):]
        return f"{first_part}\n\n[...content trimmed for size...]\n\n{last_part}"
        
    first_section = sections[0]
    last_section = sections[-1]
    
    first_size = len(first_section[0]) + len(first_section[1])
    last_size = len(last_section[0]) + len(last_section[1])
    middle_budget = max_size - first_size - last_size - 50
    
    middle_sections = []
    current_size = 0
    
    sorted_middle_sections = sorted(
        sections[1:-1],
        key=lambda s: len(s[1])
    )
    
    for header, content in sorted_middle_sections:
        section_size = len(header) + len(content)
        if current_size + section_size <= middle_budget:
            middle_sections.append((header, content))
            current_size += section_size
        else:
            break
            
    result = []
    result.append(first_section[0] + first_section[1])
    
    if middle_sections:
        for header, content in middle_sections:
            result.append(header + content)
    else:
        result.append("\n[...content trimmed for size...]\n")
        
    result.append(last_section[0] + last_section[1])
    
    optimized = "\n\n".join(result)
    console.print(f"[green]Successfully optimized content from {len(content):,} to {len(optimized):,} chars[/green]")
    
    return optimized
