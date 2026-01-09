# Setting Up New Repository: "the fire Detector"

## Step 1: Create Repository on GitHub

1. Go to https://github.com/new
2. Repository name: `the-fire-detector` (GitHub doesn't allow spaces, so use hyphens)
3. Description: "Fire and Smoke Detection System using YOLOv8 with Flask Dashboard and FastAPI"
4. Choose: **Public** or **Private** (your choice)
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click **"Create repository"**

## Step 2: Add Remote and Push

After creating the repository, run these commands:

```bash
# Remove old remotes
git remote remove origin
git remote remove firedetection

# Add new remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/the-fire-detector.git

# Push to new repository
git push -u origin main
```

## Alternative: If you want to keep the old remotes

```bash
# Just add the new remote with a different name
git remote add new-repo https://github.com/YOUR_USERNAME/the-fire-detector.git

# Push to new repository
git push -u new-repo main
```
