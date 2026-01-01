#!/bin/bash
# Script to push PyBalance to GitHub

echo "PyBalance GitHub Push Script"
echo "============================="
echo ""

# Get GitHub username
read -p "Enter your GitHub username: " GITHUB_USER
read -p "Enter repository name (default: LoadBalancer): " REPO_NAME
REPO_NAME=${REPO_NAME:-LoadBalancer}

REPO_URL="https://github.com/${GITHUB_USER}/${REPO_NAME}.git"

echo ""
echo "Repository URL: $REPO_URL"
echo ""
echo "IMPORTANT: First create the repository on GitHub:"
echo "  1. Go to https://github.com/new"
echo "  2. Repository name: $REPO_NAME"
echo "  3. DO NOT initialize with README, .gitignore, or license"
echo "  4. Click 'Create repository'"
echo ""
read -p "Press Enter after you've created the repository..."

echo ""
echo "Adding remote and pushing..."
git remote add origin "$REPO_URL" 2>/dev/null || git remote set-url origin "$REPO_URL"
git push -u origin main

echo ""
echo "Done! Your repository is now on GitHub:"
echo "  $REPO_URL"
