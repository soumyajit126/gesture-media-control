# ---------------------------------------------
# Clean Git repo: remove .venv and large binaries
# ---------------------------------------------

# Step 1: Backup current branch
git branch backup-main

# Step 2: Remove .venv and large binaries from Git history
git filter-branch --force --index-filter "git rm -r --cached --ignore-unmatch .venv" --prune-empty --tag-name-filter cat -- --all
git filter-branch --force --index-filter "git rm --cached --ignore-unmatch .venv/Lib/site-packages/cv2/cv2.pyd" --prune-empty --tag-name-filter cat -- --all
git filter-branch --force --index-filter "git rm --cached --ignore-unmatch .venv/Lib/site-packages/mediapipe/python/opencv_world3410.dll" --prune-empty --tag-name-filter cat -- --all
git filter-branch --force --index-filter "git rm --cached --ignore-unmatch .venv/Lib/site-packages/jaxlib/jax_common.dll" --prune-empty --tag-name-filter cat -- --all

# Step 3: Create .gitignore to avoid future issues
@"
.venv/
__pycache__/
*.pyc
*.pyd
*.dll
"@ | Out-File -Encoding UTF8 .gitignore

git add .gitignore
git commit -m "Add .gitignore to ignore virtual env and binaries"

# Step 4: Force push cleaned repo
git push origin main --force

Write-Host "`n✅ Repo cleaned and pushed successfully!"
Write-Host "Backup branch 'backup-main' is available in case anything goes wrong."
