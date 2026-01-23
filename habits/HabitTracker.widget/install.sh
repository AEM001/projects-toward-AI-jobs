#!/bin/bash

# Habit Tracker Installation Script
# This script installs the Habit Tracker widget for Übersicht

set -e

echo "🔥 Habit Tracker Installation Script"
echo "===================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Übersicht is installed
echo "Checking for Übersicht..."
if [ ! -d "/Applications/Übersicht.app" ]; then
    echo -e "${RED}❌ Übersicht is not installed!${NC}"
    echo "Please install Übersicht first:"
    echo "  brew install --cask ubersicht"
    exit 1
fi
echo -e "${GREEN}✓ Übersicht found${NC}"
echo ""

# Create widget directory
WIDGET_DIR="$HOME/Library/Application Support/Übersicht/widgets/HabitTracker.widget"
echo "Creating widget directory..."
mkdir -p "$WIDGET_DIR"
echo -e "${GREEN}✓ Widget directory created${NC}"
echo ""

# Copy widget files
echo "Copying widget files..."
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [ -f "$SCRIPT_DIR/index.jsx" ]; then
    cp "$SCRIPT_DIR/index.jsx" "$WIDGET_DIR/"
    echo -e "${GREEN}✓ index.jsx copied${NC}"
else
    echo -e "${RED}❌ index.jsx not found!${NC}"
    exit 1
fi

if [ -f "$SCRIPT_DIR/README.md" ]; then
    cp "$SCRIPT_DIR/README.md" "$WIDGET_DIR/"
    echo -e "${GREEN}✓ README.md copied${NC}"
fi

echo ""

# Ask about backend installation
echo -e "${YELLOW}Do you want to install the optional backend server? (y/n)${NC}"
read -r INSTALL_BACKEND

if [[ $INSTALL_BACKEND =~ ^[Yy]$ ]]; then
    echo ""
    echo "Installing backend server..."
    
    # Check for Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 is not installed!${NC}"
        echo "Please install Python 3 first"
        exit 1
    fi
    echo -e "${GREEN}✓ Python 3 found${NC}"
    
    # Copy backend files
    cp "$SCRIPT_DIR/habit_server.py" "$WIDGET_DIR/"
    cp "$SCRIPT_DIR/requirements.txt" "$WIDGET_DIR/"
    cp "$SCRIPT_DIR/BACKEND.md" "$WIDGET_DIR/"
    echo -e "${GREEN}✓ Backend files copied${NC}"
    
    # Install Python dependencies
    echo ""
    echo "Installing Python dependencies..."
    pip3 install -r "$SCRIPT_DIR/requirements.txt"
    echo -e "${GREEN}✓ Dependencies installed${NC}"
    
    # Ask about auto-start
    echo ""
    echo -e "${YELLOW}Do you want to set up auto-start for the backend server? (y/n)${NC}"
    read -r INSTALL_AUTOSTART
    
    if [[ $INSTALL_AUTOSTART =~ ^[Yy]$ ]]; then
        echo ""
        echo "Setting up auto-start..."
        
        # Update plist with correct paths
        PLIST_FILE="$HOME/Library/LaunchAgents/local.habittracker.server.plist"
        PYTHON_PATH=$(which python3)
        
        cat > "$PLIST_FILE" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>local.habittracker.server</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>$PYTHON_PATH</string>
        <string>$WIDGET_DIR/habit_server.py</string>
    </array>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <true/>
    
    <key>StandardOutPath</key>
    <string>/tmp/habittracker.out.log</string>
    
    <key>StandardErrorPath</key>
    <string>/tmp/habittracker.err.log</string>
    
    <key>WorkingDirectory</key>
    <string>$WIDGET_DIR</string>
</dict>
</plist>
EOF
        
        # Load the service
        launchctl bootstrap gui/$(id -u) "$PLIST_FILE" 2>/dev/null || true
        launchctl enable gui/$(id -u)/local.habittracker.server 2>/dev/null || true
        launchctl kickstart gui/$(id -u)/local.habittracker.server 2>/dev/null || true
        
        echo -e "${GREEN}✓ Auto-start configured${NC}"
        echo ""
        echo "Backend server is now running on http://127.0.0.1:8788"
        echo "Logs: /tmp/habittracker.out.log and /tmp/habittracker.err.log"
    else
        echo ""
        echo "To start the backend manually, run:"
        echo "  cd '$WIDGET_DIR'"
        echo "  python3 habit_server.py"
    fi
fi

echo ""
echo -e "${GREEN}✅ Installation complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Open Übersicht (or restart if already running)"
echo "2. The Habit Tracker widget should appear on your desktop"
echo "3. Click on habit buttons to switch between habits"
echo "4. Click on any day cell to toggle completion"
echo ""
echo "Configuration:"
echo "  Widget location: $WIDGET_DIR"
echo "  Data file: ~/.habit-tracker-data.json"
echo ""
echo "For more information, see:"
echo "  $WIDGET_DIR/README.md"
if [[ $INSTALL_BACKEND =~ ^[Yy]$ ]]; then
    echo "  $WIDGET_DIR/BACKEND.md"
fi
echo ""
echo "Enjoy tracking your habits! 🔥"
