#!/bin/bash
# Build macOS .app bundle for FileSeekr

set -e

APP_NAME="FileSeekr"
VERSION="1.0.0"
BUNDLE_ID="com.fileseekr.app"
BUILD_DIR="build/macos"
APP_DIR="$BUILD_DIR/$APP_NAME.app"

echo "Building $APP_NAME for macOS..."

# Clean previous build
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

# Build with PyInstaller
echo "Creating executable with PyInstaller..."
pyinstaller --clean --noconfirm \
    --name="$APP_NAME" \
    --windowed \
    --onefile \
    --icon="assets/icon.icns" \
    --osx-bundle-identifier="$BUNDLE_ID" \
    main_tray.py

# Move to build directory
mv "dist/$APP_NAME.app" "$APP_DIR"

# Create Info.plist
echo "Creating Info.plist..."
cat > "$APP_DIR/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>en</string>
    <key>CFBundleExecutable</key>
    <string>$APP_NAME</string>
    <key>CFBundleIdentifier</key>
    <string>$BUNDLE_ID</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>$APP_NAME</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>$VERSION</string>
    <key>CFBundleVersion</key>
    <string>$VERSION</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
    <key>LSUIElement</key>
    <true/>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSPrincipalClass</key>
    <string>NSApplication</string>
    <key>LSApplicationCategoryType</key>
    <string>public.app-category.utilities</string>
</dict>
</plist>
EOF

# Create DMG installer
echo "Creating DMG installer..."
DMG_NAME="$APP_NAME-$VERSION.dmg"
hdiutil create -volname "$APP_NAME" -srcfolder "$BUILD_DIR" -ov -format UDZO "$DMG_NAME"

echo "✓ macOS build complete: $DMG_NAME"
echo ""
echo "To install:"
echo "1. Open $DMG_NAME"
echo "2. Drag $APP_NAME to Applications folder"
echo "3. Launch $APP_NAME from Applications"
echo "4. Press Ctrl+Shift+Space to search"
