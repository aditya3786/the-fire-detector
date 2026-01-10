#!/bin/bash

# Script to set up and push to new repository "the-fire-detector"
# Make sure you've created the repository on GitHub first!

echo "Setting up new repository: the-fire-detector"
echo ""
echo "Step 1: Creating repository on GitHub..."
echo "Please go to https://github.com/new and create a repository named 'the-fire-detector'"
echo "Make sure it's empty (no README, .gitignore, or license)"
echo ""
read -p "Press Enter after you've created the repository on GitHub..."

echo ""
echo "Step 2: Removing old remotes..."
git remote remove origin 2>/dev/null
git remote remove firedetection 2>/dev/null

echo ""
echo "Step 3: Adding new remote..."
echo "Enter your GitHub username:"
read GITHUB_USERNAME

git remote add origin "https://github.com/${GITHUB_USERNAME}/the-fire-detector.git"

echo ""
echo "Step 4: Pushing to new repository..."
git push -u origin main

echo ""
echo "✅ Done! Your repository is now at: https://github.com/${GITHUB_USERNAME}/the-fire-detector"
