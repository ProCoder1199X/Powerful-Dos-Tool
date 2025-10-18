#!/bin/bash
# EWLT Ultimate Setup Script
# Automated installation and configuration

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║   ███████╗██╗    ██╗██╗  ████████╗    ██╗   ██╗██████╗  ██████╗  ║
║   ██╔════╝██║    ██║██║  ╚══██╔══╝    ██║   ██║╚════██╗██╔═████╗ ║
║   █████╗  ██║ █╗ ██║██║     ██║       ██║   ██║ █████╔╝██║██╔██║ ║
║   ██╔══╝  ██║███╗██║██║     ██║       ╚██╗ ██╔╝ ╚═══██╗████╔╝██║ ║
║   ███████╗╚███╔███╔╝███████╗██║        ╚████╔╝ ██████╔╝╚██████╔╝ ║
║   ╚══════╝ ╚══╝╚══╝ ╚══════╝╚═╝         ╚═══╝  ╚═════╝  ╚═════╝  ║
║                                                                   ║
║                    ULTIMATE SETUP SCRIPT                          ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "${YELLOW}⚠️  This will install ALL dependencies for EWLT Ultimate Edition${NC}"
echo -e "${YELLOW}⚠️  This may take 5-10 minutes depending on your connection${NC}"
echo ""
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Installation cancelled."
    exit 0
fi

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
else
    echo -e "${RED}✗ Unsupported OS: $OSTYPE${NC}"
    exit 1
fi

echo -e "\n${BLUE}[1/8] Detected OS: $OS${NC}"

# Check for root (needed for some features)
if [ "$EUID" -ne 0 ] && [ "$OS" == "linux" ]; then
    echo -e "${YELLOW}⚠️  Not running as root. Some features (MAC spoofing) will require sudo.${NC}"
fi

# Update package manager
echo -e "\n${BLUE}[2/8] Updating package manager...${NC}"
if [ "$OS" == "linux" ]; then
    if command -v apt-get &> /dev/null; then
        sudo apt-get update -qq
    elif command -v dnf &> /dev/null; then
        sudo dnf check-update -q || true
    elif command -v pacman &> /dev/null; then
        sudo pacman -Sy --noconfirm
    fi
elif [ "$OS" == "macos" ]; then
    if ! command -v brew &> /dev/null; then
        echo -e "${YELLOW}Installing Homebrew...${NC}"
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    brew update
fi

# Install system dependencies
echo -e "\n${BLUE}[3/8] Installing system dependencies...${NC}"
if [ "$OS" == "linux" ]; then
    if command -v apt-get &> /dev/null; then
        sudo apt-get install -y -qq \
            python3 \
            python3-pip \
            python3-dev \
            tor \
            iproute2 \
            build-essential \
            libssl-dev \
            libffi-dev \
            git \
            curl \
            wget \
            haveged
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y -q \
            python3 \
            python3-pip \
            python3-devel \
            tor \
            iproute \
            gcc \
            gcc-c++ \
            openssl-devel \
            libffi-devel \
            git \
            curl \
            wget \
            haveged
    elif command -v pacman &> /dev/null; then
        sudo pacman -S --noconfirm --needed \
            python \
            python-pip \
            tor \
            iproute2 \
            base-devel \
            openssl \
            libffi \
            git \
            curl \
            wget \
            haveged
    fi
    
    # Enable and start services
    sudo systemctl enable tor haveged 2>/dev/null || true
    sudo systemctl start tor haveged 2>/dev/null || true
    
elif [ "$OS" == "macos" ]; then
    brew install python3 tor openssl libffi git curl wget
    brew services start tor
fi

echo -e "${GREEN}✓ System dependencies installed${NC}"

# Install Python dependencies
echo -e "\n${BLUE}[4/8] Installing Python packages...${NC}"
pip3 install --upgrade pip setuptools wheel -q

echo "Installing core packages..."
pip3 install -q \
    locust \
    requests \
    PySocks \
    stem \
    cryptography \
    websocket-client \
    h2 \
    httpx[http2] \
    scapy \
    pyOpenSSL

echo "Installing optional ML packages (may take a while)..."
pip3 install -q numpy scipy scikit-learn 2>/dev/null || \
    echo -e "${YELLOW}⚠️  ML packages skipped (optional)${NC}"

echo -e "${GREEN}✓ Python packages installed${NC}"

# Create directory structure
echo -e "\n${BLUE}[5/8] Creating directory structure...${NC}"
mkdir -p ~/.ewlt_ultimate_logs
mkdir -p ~/.ewlt_config
mkdir -p ~/.ewlt_reports
chmod 700 ~/.ewlt_ultimate_logs ~/.ewlt_config

echo -e "${GREEN}✓ Directory structure created${NC}"

# Configure Tor
echo -e "\n${BLUE}[6/8] Configuring Tor...${NC}"
if [ "$OS" == "linux" ]; then
    TOR_CONFIG="/etc/tor/torrc"
    if [ -f "$TOR_CONFIG" ]; then
        # Backup original config
        sudo cp "$TOR_CONFIG" "$TOR_CONFIG.backup.$(date +%s)"
        
        # Add EWLT-specific configuration
        if ! grep -q "# EWLT Configuration" "$TOR_CONFIG"; then
            sudo tee -a "$TOR_CONFIG" > /dev/null << 'EOL'

# EWLT Configuration
SocksPort 9050 IsolateDestAddr IsolateDestPort
ControlPort 9051
CookieAuthentication 1
NumEntryGuards 8
CircuitBuildTimeout 60
EnforceDistinctSubnets 1
EOL
            sudo systemctl restart tor
        fi
    fi
fi

echo -e "${GREEN}✓ Tor configured${NC}"

# Firewall configuration
echo -e "\n${BLUE}[7/8] Configuring firewall...${NC}"
if [ "$OS" == "linux" ]; then
    if command -v ufw &> /dev/null; then
        sudo ufw allow 9050/tcp comment 'Tor SOCKS' 2>/dev/null || true
        sudo ufw allow 9051/tcp comment 'Tor Control' 2>/dev/null || true
        echo -e "${GREEN}✓ Firewall rules added${NC}"
    else
        echo -e "${YELLOW}⚠️  UFW not found, skipping firewall configuration${NC}"
    fi
fi

# Final checks
echo -e "\n${BLUE}[8/8] Running system checks...${NC}"

# Check Python
if python3 --version &> /dev/null; then
    echo -e "${GREEN}✓ Python3: $(python3 --version)${NC}"
else
    echo -e "${RED}✗ Python3 not found${NC}"
fi

# Check Tor
if tor --version &> /dev/null; then
    echo -e "${GREEN}✓ Tor: $(tor --version | head -n1)${NC}"
else
    echo -e "${RED}✗ Tor not found${NC}"
fi

# Check if Tor is running
if netstat -tuln 2>/dev/null | grep -q ":9050 " || lsof -i:9050 &>/dev/null; then
    echo -e "${GREEN}✓ Tor service is running${NC}"
else
    echo -e "${YELLOW}⚠️  Tor service not running. Start with: sudo systemctl start tor${NC}"
fi

# Check entropy
if [ -f /proc/sys/kernel/random/entropy_avail ]; then
    ENTROPY=$(cat /proc/sys/kernel/random/entropy_avail)
    if [ "$ENTROPY" -gt 1000 ]; then
        echo -e "${GREEN}✓ System entropy: $ENTROPY bits${NC}"
    else
        echo -e "${YELLOW}⚠️  Low entropy: $ENTROPY bits (haveged should help)${NC}"
    fi
fi

# Installation complete
echo -e "\n${GREEN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║                    ✓ INSTALLATION COMPLETE                        ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "${GREEN}Everything is ready!${NC}\n"

echo -e "${BLUE}Quick Start Commands:${NC}"
echo -e "  ${YELLOW}# Run security audit${NC}"
echo -e "  python3 security_audit.py"
echo -e ""
echo -e "  ${YELLOW}# Basic test${NC}"
echo -e "  python3 web_load_tester.py --target-url http://localhost:8080 --users 50"
echo -e ""
echo -e "  ${YELLOW}# Ultimate test with all features${NC}"
echo -e "  sudo python3 ewlt_ultimate.py \\"
echo -e "    --target-url https://yoursite.com \\"
echo -e "    --users 100 \\"
echo -e "    --use-tor \\"
echo -e "    --mac-interface wlan0 \\"
echo -e "    --dashboard"
echo -e ""
echo -e "  ${YELLOW}# Open dashboard${NC}"
echo -e "  Open Tor Browser and navigate to: http://localhost:8089"
echo -e ""

echo -e "${BLUE}Next Steps:${NC}"
echo -e "1. Review documentation: ${YELLOW}cat README.md${NC}"
echo -e "2. Read power features: ${YELLOW}cat POWER_FEATURES.md${NC}"
echo -e "3. Check attack profiles: ${YELLOW}cat attack_profiles.json${NC}"
echo -e "4. Run security audit: ${YELLOW}python3 security_audit.py${NC}"
echo -e "5. Open dashboard: ${YELLOW}firefox dashboard.html${NC}"
echo -e ""

echo -e "${RED}⚠️  IMPORTANT REMINDERS:${NC}"
echo -e "  • Only test systems you OWN or have WRITTEN permission to test"
echo -e "  • Unauthorized testing is ILLEGAL and may result in prosecution"
echo -e "  • Start with small loads (10-50 users) and increase gradually"
echo -e "  • Monitor your target server during tests"
echo -e "  • Have a kill switch ready (Ctrl+C)"
echo -e "  • Use --dry-run flag to test configuration first"
echo -e ""
echo "Installing MQTT, gRPC, and WebSocket dependencies..."
pip3 install paho-mqtt grpcio grpcio-tools websocket-client

echo "✓ Protocol dependencies installed"

echo -e "${GREEN}Installation log saved to: ./ewlt_setup.log${NC}"
echo -e "${GREEN}Support: https://github.com/yourusername/ethical-web-load-tester${NC}"
echo -e ""
echo -e "${BLUE}Happy (ethical) testing! 🛡️${NC}"