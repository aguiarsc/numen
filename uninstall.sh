#!/bin/bash
# uninstall.sh
# Complete uninstaller for Numen

# ANSI color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colorized output
print_color() {
    local color="$1"
    local message="$2"
    echo -e "${color}${message}${NC}"
}

# Function to uninstall Numen
uninstall_numen() {
    print_color "$GREEN" "Starting Numen uninstallation..."
    print_color "$YELLOW" "This will remove all Numen files, including your notes and configuration."

    # Ask for confirmation
    read -p "Are you sure you want to proceed? (y/N) " confirmation
    if [[ "$confirmation" != "y" && "$confirmation" != "Y" ]]; then
        print_color "$GREEN" "Uninstallation canceled."
        return
    fi

    # Optional: Ask about keeping notes
    read -p "Would you like to keep your notes? (Y/n) " keep_notes
    preserve_notes=true
    if [[ "$keep_notes" == "n" || "$keep_notes" == "N" ]]; then
        preserve_notes=false
    fi

    # First, uninstall the package
    print_color "$YELLOW" "Removing Numen package..."
    
    # Check if pipx is available
    if command -v pipx >/dev/null 2>&1; then
        print_color "$YELLOW" "Detected pipx installation. Using pipx to uninstall..."
        pipx uninstall numen
        if [ $? -eq 0 ]; then
            print_color "$GREEN" "Package successfully uninstalled using pipx."
        else
            print_color "$RED" "Failed to uninstall package with pipx."
        fi
    else
        # Fall back to pip if pipx is not available
        if pip uninstall -y numen 2>&1 | grep -q "externally-managed-environment"; then
            print_color "$YELLOW" "Detected externally managed environment (Arch Linux)."
            print_color "$RED" "Please uninstall manually with pipx:"
            print_color "$YELLOW" "pipx uninstall numen"
        else
            pip uninstall -y numen
            if [ $? -eq 0 ]; then
                print_color "$GREEN" "Package successfully uninstalled."
            else
                print_color "$RED" "Failed to uninstall package. It might not be installed via pip."
            fi
        fi
    fi

    # Then, remove configuration
    numen_dir="$HOME/.numen"
    
    if [ -d "$numen_dir" ]; then
        print_color "$YELLOW" "Removing Numen configuration directory..."
        
        if [ "$preserve_notes" = true ]; then
            # Move notes to a backup location
            notes_dir="$numen_dir/notes"
            if [ -d "$notes_dir" ]; then
                backup_dir="$HOME/numen_notes_backup"
                print_color "$YELLOW" "Backing up notes to $backup_dir"
                
                # Create backup directory if it doesn't exist
                mkdir -p "$backup_dir"
                
                # Copy notes to backup directory
                cp -r "$notes_dir"/* "$backup_dir" 2>/dev/null
                print_color "$GREEN" "Notes backed up successfully."
            fi
        fi

        # Remove the entire .numen directory
        rm -rf "$numen_dir"
        print_color "$GREEN" "Configuration directory removed."
    else
        print_color "$YELLOW" "Numen configuration directory not found at $numen_dir."
    fi

    # Clean up any system-wide installations if needed
    if [ -d "/usr/local/lib/python*/dist-packages/numen" ]; then
        print_color "$YELLOW" "Removing system-wide installation..."
        sudo rm -rf /usr/local/lib/python*/dist-packages/numen*
    fi

    # Remove any executable from path
    if [ -f "/usr/local/bin/numen" ]; then
        print_color "$YELLOW" "Removing executable from path..."
        sudo rm /usr/local/bin/numen
    fi

    print_color "$GREEN" "Numen has been completely uninstalled from your system."
    if [ "$preserve_notes" = true ]; then
        print_color "$GREEN" "Your notes have been preserved in $HOME/numen_notes_backup"
    fi
}

# Execute the uninstall function
uninstall_numen
