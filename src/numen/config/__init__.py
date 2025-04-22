"""Configuration management for Numen."""

import os
import pathlib
from typing import Any, Dict, Optional

import toml
from rich.console import Console

console = Console()

DEFAULT_CONFIG = {
    "ai": {
        "default_provider": "gemini",
        "anthropic_api_key": "",
        "openai_api_key": "",
        "gemini_api_key": "",
        "ollama_base_url": "http://localhost:11434",
        "default_model": "gemini-1.5-flash",
        "temperature": 0.7,
    },
    "editor": {
        "default": "",  # Empty use $EDITOR env
    },
    "paths": {
        "notes_dir": "~/.numen/notes",
    },
}

CONFIG_DIR = os.path.expanduser("~/.numen")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.toml")


def ensure_config_exists() -> None:
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        os.makedirs(os.path.join(CONFIG_DIR, "notes"), exist_ok=True)
        os.makedirs(os.path.join(CONFIG_DIR, "cache"), exist_ok=True)
        os.makedirs(os.path.join(CONFIG_DIR, "logs"), exist_ok=True)
        
        if not os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                toml.dump(DEFAULT_CONFIG, f)
            console.print(f"[green]Created default configuration at: {CONFIG_FILE}[/green]")
            console.print("[yellow]Please edit this file to add your API keys.[/yellow]")
    except Exception as e:
        console.print(f"[red]Error creating config directories or file: {e}[/red]")


def update_config_with_new_fields(config: Dict[str, Any]) -> Dict[str, Any]:
    updated = False
    
    def update_dict(config_dict, default_dict):
        nonlocal updated
        for key, value in default_dict.items():
            if key not in config_dict:
                config_dict[key] = value
                updated = True
            elif isinstance(value, dict) and isinstance(config_dict[key], dict):
                update_dict(config_dict[key], value)
    
    updated_config = config.copy()
    update_dict(updated_config, DEFAULT_CONFIG)
    
    if updated:
        try:
            save_config(updated_config)
            console.print("[green]Updated configuration with new default fields.[/green]")
        except Exception as e:
            console.print(f"[yellow]Warning: Unable to save updated config: {e}[/yellow]")
        
    return updated_config


def get_config() -> Dict[str, Any]:
    ensure_config_exists()
    
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = toml.load(f)
        
        return update_config_with_new_fields(config)
    except Exception as e:
        console.print(f"[red]Error loading config file: {e}[/red]")
        console.print("[yellow]Using default configuration...[/yellow]")
        return DEFAULT_CONFIG.copy()


def save_config(config: Dict[str, Any]) -> None:
    ensure_config_exists()
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            toml.dump(config, f)
    except Exception as e:
        console.print(f"[red]Error saving config: {e}[/red]")
        raise


def get_notes_dir() -> pathlib.Path:
    config = get_config()
    notes_dir = os.path.expanduser(config["paths"]["notes_dir"])
    return pathlib.Path(notes_dir)


def get_editor() -> str:
    config = get_config()
    editor = config["editor"]["default"]
    if not editor:
        editor = os.environ.get("EDITOR", "nvim")
    return editor


def get_ai_config() -> Dict[str, Any]:
    config = get_config()
    return config["ai"]
