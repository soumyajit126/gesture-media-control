# clean_repo.ps1
# Safe cleanup of large files and virtual environment from Git history

# Activate your virtual environment first
Write-Host "Make sure your virtual environment is activated and all changes are committed."
Write-Host "Press Enter to continue..."
Read-Host

# Check git status
git status
Write-Host "If there are uncommitted changes, commit or stash them first!"
Write-Host "Press Enter to continue..."
Read-Host

# Install git-filter-repo if not installed
pip show git-filter-repo > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing git-filter-repo..."
    pip install git-filter-repo
}

# Remove large files and .venv from history
Write-Host "Cleaning Git history..."
git filter-repo --invert-paths --path .venv/ --path *.dll --path *.pyd --path *.pyc

# Add .gitignore entries to prevent future commits of these files
Write-Host "Updating .gitignore..."
$gitignorePath = ".gitignore"
$entries = @(".venv/", "*.dll", "*.pyd", "*.pyc")
foreach ($entry in $entries) {
    if (-not (Select-String -Path $gitignorePath -Pattern [regex]::Escape($entry))) {
        Add-Content -Path $gitignorePath -Value $entry
    }
}

# Commit .gitignore changes
git add .gitignore
git commit -m "Update .gitignore to exclude .venv and large binaries"

Write-Host "Cleanup complete. You can now force push the cleaned repo:"
Write-Host "`tgit push origin main --force"
    