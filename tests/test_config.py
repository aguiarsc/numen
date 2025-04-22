"""Tests for the config module."""

import os
import pathlib
import tempfile
from unittest import mock

import pytest
import toml

from numen.config import (
    DEFAULT_CONFIG,
    ensure_config_exists,
    get_config,
    get_editor,
    get_notes_dir,
)


@pytest.fixture
def mock_config_dir():
    """Create a temporary directory for config files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        with mock.patch("numen.config.CONFIG_DIR", temp_dir):
            with mock.patch("numen.config.CONFIG_FILE", os.path.join(temp_dir, "config.toml")):
                yield temp_dir


def test_ensure_config_exists(mock_config_dir):
    """Test that ensure_config_exists creates the necessary directories and config file."""
    ensure_config_exists()
    
    assert os.path.exists(mock_config_dir)
    assert os.path.exists(os.path.join(mock_config_dir, "notes"))
    assert os.path.exists(os.path.join(mock_config_dir, "cache"))
    assert os.path.exists(os.path.join(mock_config_dir, "logs"))
    
    config_file = os.path.join(mock_config_dir, "config.toml")
    assert os.path.exists(config_file)
    
    with open(config_file, "r") as f:
        config = toml.load(f)
    
    assert config == DEFAULT_CONFIG


def test_get_config(mock_config_dir):
    """Test that get_config returns the config from the file."""
    ensure_config_exists()
    
    config = get_config()
    
    assert config == DEFAULT_CONFIG
    
    config["ai"]["default_provider"] = "test_provider"
    config_file = os.path.join(mock_config_dir, "config.toml")
    with open(config_file, "w") as f:
        toml.dump(config, f)
    
    new_config = get_config()
    
    assert new_config["ai"]["default_provider"] == "test_provider"


def test_get_editor():
    """Test that get_editor returns the configured editor or falls back to environment variable."""
    mock_config = {
        "editor": {
            "default": "test_editor"
        }
    }
    
    with mock.patch("numen.config.get_config", return_value=mock_config):
        assert get_editor() == "test_editor"
    
    mock_empty_config = {
        "editor": {
            "default": ""
        }
    }
    
    with mock.patch("numen.config.get_config", return_value=mock_empty_config):
        with mock.patch.dict(os.environ, {"EDITOR": "env_editor"}):
            assert get_editor() == "env_editor"
    
    with mock.patch("numen.config.get_config", return_value=mock_empty_config):
        with mock.patch.dict(os.environ, {}, clear=True):
            assert get_editor() == "nvim"


def test_get_notes_dir():
    """Test that get_notes_dir returns the configured notes directory."""
    mock_config = {
        "paths": {
            "notes_dir": "~/test_notes"
        }
    }
    
    with mock.patch("numen.config.get_config", return_value=mock_config):
        notes_dir = get_notes_dir()
        assert isinstance(notes_dir, pathlib.Path)
        assert str(notes_dir).endswith("test_notes") 