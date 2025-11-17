# Building Kentroid Samurai PNG-Tuber as a macOS App

This guide will help you package the PNG-Tuber into a standalone macOS `.app` bundle that you can double-click to run.

## Prerequisites

Make sure you have the virtual environment set up and all dependencies installed:

```bash
# Activate your virtual environment
source venv/bin/activate

# Install 
pip install -r requirements.txt
```

## Building the App

### Step 1: Clean Previous Builds (if any)

```bash
rm -rf build dist
```

### Step 2: Build in Alias Mode (for testing)

This creates a lightweight app that links to your source files - good for testing:

```bash
python setup.py py2app -A
```

### Step 3: Test the Alias App

```bash
open dist/pngtuber.app
```

If it works correctly, proceed to create the standalone version.

### Step 4: Build Standalone App

This creates a fully self-contained app with all dependencies bundled:

```bash
# Clean first
rm -rf build dist

# Build standalone
python setup.py py2app
```

## Installing the App

After building, you'll find `pngtuber.app` in the `dist/` folder.

### Option 1: Use from dist folder
```bash
open dist/pngtuber.app
```

### Option 2: Copy to Applications
```bash
cp -r dist/pngtuber.app /Applications/
```

Now you can launch it from Launchpad or Spotlight like any other Mac app! 🎉

## Troubleshooting

### App won't launch
- Check Console.app for error messages
- Try running in alias mode first to debug: `python setup.py py2app -A`

### Missing dependencies
If you get import errors, add the missing packages to the `packages` list in `setup.py`:
```python
'packages': ['pygame', 'pyaudio', 'numpy', 'PIL', 'missing_package_here'],
```

### Missing resource files
If images or backgrounds are missing, verify they're listed in `DATA_FILES` in `setup.py`.

### Microphone not working
The app includes `NSMicrophoneUsageDescription` in the plist, but macOS will still ask for permission the first time you run it. Make sure to grant microphone access when prompted.

### App is too large
The standalone build includes Python and all dependencies, so it can be 100-300 MB. This is normal for bundled Python apps.

## Creating an Icon (Optional)

To add a custom icon:

1. Create a 1024x1024 PNG of your icon
2. Use Icon Composer or `iconutil` to convert it to `.icns` format:
   ```bash
   # Create iconset folder
   mkdir MyIcon.iconset
   
   # Add icon at various sizes (you'd need to generate these)
   # icon_512x512.png, icon_256x256.png, etc.
   
   # Convert to icns
   iconutil -c icns MyIcon.iconset
   ```
3. Update `setup.py` to point to your `.icns` file:
   ```python
   'iconfile': 'MyIcon.icns',
   ```

## Advanced: Signing and Notarization

For distribution outside your machine, you'll want to sign and notarize the app:

1. **Code Signing** (requires Apple Developer account):
   ```bash
   codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name" dist/pngtuber.app
   ```

2. **Notarization** (for Gatekeeper):
   - Create a DMG or ZIP of the app
   - Submit to Apple's notarization service
   - Staple the notarization ticket

This is only needed if you're distributing to other users.

## File Structure

After building, your app structure will look like:

```
dist/pngtuber.app/
  Contents/
    MacOS/
      pngtuber          # Main executable
    Resources/
      KentroidSamuraiTopVisorShade.PNG
      explosion.png
      bg/               # Background images
      emoji/            # Emoji images
      lib/              # Python libraries
    Info.plist          # App metadata
```

## Keeping It Updated

When you make changes to your code:

1. Clean the build: `rm -rf build dist`
2. Rebuild: `python setup.py py2app`
3. Test the new app

---

**Note**: The first build might take a few minutes as py2app bundles Python and all dependencies. Subsequent builds are faster.

Enjoy your standalone Mac app! 🎮✨

