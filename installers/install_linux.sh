#!/bin/bash
# FileSeekr Linux Installation Script

set -e

APP_NAME="fileseekr"
INSTALL_DIR="/opt/fileseekr"
BIN_LINK="/usr/local/bin/fileseekr"
DESKTOP_FILE="/usr/share/applications/fileseekr.desktop"
AUTOSTART_DIR="$HOME/.config/autostart"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}FileSeekr Linux Installer${NC}"
echo ""

# Check if running as root for system-wide install
if [ "$EUID" -eq 0 ]; then
    SYSTEM_INSTALL=true
    echo "Installing system-wide (all users)..."
else
    SYSTEM_INSTALL=false
    INSTALL_DIR="$HOME/.local/share/fileseekr"
    BIN_LINK="$HOME/.local/bin/fileseekr"
    DESKTOP_FILE="$HOME/.local/share/applications/fileseekr.desktop"
    echo "Installing for current user only..."
fi

echo ""

# Check dependencies
echo "Checking dependencies..."

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    echo "Please install Python 3.8 or later"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✓ Python $PYTHON_VERSION found"

# Check for pip
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}Error: pip3 is not installed${NC}"
    echo "Please install pip3"
    exit 1
fi

echo "✓ pip3 found"

# Create installation directory
echo ""
echo "Creating installation directory: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"

# Copy files
echo "Copying application files..."
cp -r ../src "$INSTALL_DIR/"
cp -r ../main_tray.py "$INSTALL_DIR/"
cp -r ../requirements.txt "$INSTALL_DIR/"
cp -r ../config.yaml "$INSTALL_DIR/"
cp -r ../README.md "$INSTALL_DIR/"
cp -r ../LICENSE "$INSTALL_DIR/"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv "$INSTALL_DIR/venv"

# Activate venv and install dependencies
echo "Installing dependencies..."
source "$INSTALL_DIR/venv/bin/activate"
pip3 install --upgrade pip
pip3 install -r "$INSTALL_DIR/requirements.txt"

# Download spaCy model (optional but recommended)
echo ""
read -p "Download spaCy language model for enhanced NLP? (recommended, ~50MB) [Y/n] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
    echo "Downloading spaCy model..."
    python3 -m spacy download en_core_web_sm || echo -e "${YELLOW}Warning: Failed to download spaCy model${NC}"
fi

deactivate

# Create launcher script
echo ""
echo "Creating launcher script..."
mkdir -p "$(dirname $BIN_LINK)"

cat > "$BIN_LINK" << 'EOF'
#!/bin/bash
# FileSeekr Launcher

INSTALL_DIR="INSTALL_DIR_PLACEHOLDER"
source "$INSTALL_DIR/venv/bin/activate"
cd "$INSTALL_DIR"
python3 main_tray.py "$@"
EOF

# Replace placeholder
sed -i "s|INSTALL_DIR_PLACEHOLDER|$INSTALL_DIR|g" "$BIN_LINK"

chmod +x "$BIN_LINK"

echo "✓ Launcher created: $BIN_LINK"

# Create desktop entry
echo ""
echo "Creating desktop entry..."
mkdir -p "$(dirname $DESKTOP_FILE)"

cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Type=Application
Name=FileSeekr
Comment=Smart file search with global hotkey
Exec=$BIN_LINK
Icon=system-search
Terminal=false
Categories=Utility;FileTools;
Keywords=search;find;files;
StartupNotify=false
X-GNOME-Autostart-enabled=true
EOF

chmod +x "$DESKTOP_FILE"

echo "✓ Desktop entry created: $DESKTOP_FILE"

# Setup autostart
echo ""
read -p "Enable auto-start on login? [Y/n] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
    mkdir -p "$AUTOSTART_DIR"
    cp "$DESKTOP_FILE" "$AUTOSTART_DIR/fileseekr.desktop"
    echo "✓ Auto-start enabled"
fi

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    if [ "$SYSTEM_INSTALL" = true ]; then
        update-desktop-database /usr/share/applications 2>/dev/null || true
    else
        update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
    fi
fi

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✓ Installation complete!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "To start FileSeekr:"
echo "  $ fileseekr"
echo ""
echo "Or launch from your application menu"
echo ""
echo -e "${YELLOW}Global Hotkey: Ctrl+Shift+Space${NC}"
echo ""
echo "For help:"
echo "  $ fileseekr --help"
echo ""
echo "To uninstall, run:"
echo "  $ sudo rm -rf $INSTALL_DIR"
echo "  $ sudo rm $BIN_LINK"
echo "  $ sudo rm $DESKTOP_FILE"
echo ""

# Ask to launch
read -p "Launch FileSeekr now? [Y/n] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
    nohup "$BIN_LINK" > /dev/null 2>&1 &
    echo ""
    echo -e "${GREEN}FileSeekr is now running!${NC}"
    echo "Press Ctrl+Shift+Space to search files"
    echo "Check the system tray for the FileSeekr icon"
fi

echo ""
