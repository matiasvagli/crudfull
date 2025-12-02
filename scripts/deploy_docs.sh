#!/bin/bash
# Build and deploy MkDocs documentation to GitHub Pages

echo "Building documentation..."
mkdocs build --clean

echo ""
echo "Deploying to GitHub Pages..."
mkdocs gh-deploy --force

echo ""
echo "Documentation deployed successfully!"
echo "Visit: https://matiasvagli.github.io/crudfull/"
