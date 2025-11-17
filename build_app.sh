#!/bin/bash
# Clean build script for Samurai Samus Avatar

echo "🧹 Cleaning previous build..."
rm -rf build dist

echo "🔨 Building app with py2app..."
source venv/bin/activate && python setup.py py2app

echo ""
echo "✅ Build complete!"
echo "📦 App location: dist/Samurai Samus Avatar.app"
echo ""
echo "To open: open 'dist/Samurai Samus Avatar.app'"
echo "To install: cp -r 'dist/Samurai Samus Avatar.app' /Applications/"

