#!/bin/bash

set -e

echo "Installing Numen - AI-Augmented Terminal Notepad"
echo "================================================"

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

version_major=$(echo $python_version | cut -d. -f1)
version_minor=$(echo $python_version | cut -d. -f2)
version_num=$(($version_major * 100 + $version_minor))

if [ $version_num -lt 311 ]; then
    echo "Error: Numen requires Python 3.11 or newer"
    exit 1
fi

# Check if pipx is installed
if command -v pipx &> /dev/null; then
    echo "pipx found, using isolated installation (recommended)"
    
    # Check if already installed with pipx
    if pipx list | grep -q "numen"; then
        echo "Numen already installed with pipx, upgrading..."
        pipx install . --force
    else
        echo "Installing Numen with pipx..."
        pipx install .
    fi
    
    # Create config directory if it doesn't exist
    if [ ! -d ~/.numen ]; then
        echo "Setting up configuration..."
        mkdir -p ~/.numen/notes ~/.numen/cache ~/.numen/logs
    fi
    
    echo "✅ Installation complete! Run 'numen --help' to get started."
else
    echo "pipx not found, falling back to traditional pip installation"
    echo "NOTE: For better isolation, consider installing pipx: https://pypa.github.io/pipx/"
    
    # Install dependencies
    echo "Installing dependencies..."
    pip install -e .
    
    # Create config directory
    echo "Setting up configuration..."
    mkdir -p ~/.numen/notes ~/.numen/cache ~/.numen/logs
    
    # Run numen for the first time to generate config
    echo "Generating initial configuration..."
    python -c "from numen.config import ensure_config_exists; ensure_config_exists()"
    
    echo "✅ Installation complete! Run 'numen --help' to get started."
fi

echo ""
echo "📝 Notes are stored in: ~/.numen/notes"
echo "⚙️  Edit config with:   numen config"