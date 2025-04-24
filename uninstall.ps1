# uninstall.ps1
# Complete uninstaller for Numen

function Write-ColorOutput($ForegroundColor) {
    # Save the current color
    $previousForegroundColor = $host.UI.RawUI.ForegroundColor

    # Set the new color
    $host.UI.RawUI.ForegroundColor = $ForegroundColor

    # Check if the arguments list has more than 1 element
    if ($args.Count -gt 0) {
        Write-Output $args[0]
    }

    # Restore the previous color
    $host.UI.RawUI.ForegroundColor = $previousForegroundColor
}

function Uninstall-Numen {
    Write-ColorOutput Green "Starting Numen uninstallation..."
    Write-ColorOutput Yellow "This will remove all Numen files, including your notes and configuration."

    # Ask for confirmation
    $confirmation = Read-Host "Are you sure you want to proceed? (y/N)"
    if ($confirmation -ne 'y' -and $confirmation -ne 'Y') {
        Write-ColorOutput Green "Uninstallation canceled."
        return
    }

    # Optional: Ask about keeping notes
    $keepNotes = Read-Host "Would you like to keep your notes? (Y/n)"
    $preserveNotes = $keepNotes -ne 'n' -and $keepNotes -ne 'N'

    try {
        # First, uninstall the package
        Write-ColorOutput Yellow "Removing Numen package..."
        pip uninstall -y numen
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput Green "Package successfully uninstalled."
        } else {
            Write-ColorOutput Red "Failed to uninstall package. It might not be installed via pip."
        }

        # Then, remove configuration
        $numenDir = Join-Path $env:USERPROFILE ".numen"
        
        if (Test-Path $numenDir) {
            Write-ColorOutput Yellow "Removing Numen configuration directory..."
            
            if ($preserveNotes) {
                # Move notes to a backup location
                $notesDir = Join-Path $numenDir "notes"
                if (Test-Path $notesDir) {
                    $backupDir = Join-Path $env:USERPROFILE "numen_notes_backup"
                    Write-ColorOutput Yellow "Backing up notes to $backupDir"
                    
                    # Create backup directory if it doesn't exist
                    if (-not (Test-Path $backupDir)) {
                        New-Item -ItemType Directory -Path $backupDir | Out-Null
                    }
                    
                    # Copy notes to backup directory
                    Copy-Item -Path "$notesDir\*" -Destination $backupDir -Recurse -Force
                    Write-ColorOutput Green "Notes backed up successfully."
                }
            }

            # Remove the entire .numen directory
            Remove-Item -Path $numenDir -Recurse -Force
            Write-ColorOutput Green "Configuration directory removed."
        } else {
            Write-ColorOutput Yellow "Numen configuration directory not found at $numenDir."
        }

        # Clean up any environment variables (uncomment if needed)
        # [Environment]::SetEnvironmentVariable("NUMEN_SOMETHING", $null, "User")

        Write-ColorOutput Green "Numen has been completely uninstalled from your system."
        if ($preserveNotes) {
            Write-ColorOutput Green "Your notes have been preserved in $env:USERPROFILE\numen_notes_backup"
        }
    } catch {
        Write-ColorOutput Red "An error occurred during uninstallation:"
        Write-ColorOutput Red $_.Exception.Message
    }
}

# Execute the uninstall function
Uninstall-Numen
