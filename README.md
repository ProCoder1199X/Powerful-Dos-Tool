# Ethical Web Load Tester (EWLT) v3.0
### Highly advanced tool and poweful for load testing 
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Security: High](https://img.shields.io/badge/security-military--grade-red.svg)]()

## ⚠️ CRITICAL LEGAL NOTICE

**THIS TOOL IS STRICTLY FOR EDUCATIONAL, TESTING, AND RESEARCH PURPOSES ONLY**

Unauthorized testing of computer systems is **ILLEGAL** under international law. By using this tool, you accept FULL legal responsibility for your actions.

---

## 🎯 What Makes v3.0 Different?

This is **not** your typical load testing tool. EWLT v3.0 implements **military-grade anonymity** and **advanced anti-correlation** techniques used by security researchers and penetration testers.

### 🔒 Revolutionary Security Features

#### **Traffic Analysis Prevention**
- ✅ **Traffic Padding** - Variable-size padding prevents packet size correlation
- ✅ **Timing Obfuscation** - Cryptographic random delays break timing patterns
- ✅ **Cover Traffic Generation** - Background noise hides real request patterns
- ✅ **Request Reordering** - Non-sequential request patterns

#### **Advanced Tor Integration**
- ✅ **Multi-Hop Circuits** - 3-5 hop circuits (vs standard 3)
- ✅ **Guard Node Selection** - Enhanced entry node diversity
- ✅ **Circuit Isolation** - Stream isolation prevents cross-circuit correlation
- ✅ **Bridge Support** - Tor bridges for censored networks
- ✅ **Automatic Identity Rotation** - Periodic circuit changes

#### **Fingerprinting Resistance**
- ✅ **TLS Fingerprint Randomization** - Defeats JA3/JA4 fingerprinting
- ✅ **User Agent Rotation** - 10+ diverse browser fingerprints
- ✅ **Header Randomization** - Dynamic HTTP header generation
- ✅ **Accept-Language Diversity** - Geographic fingerprint variation
- ✅ **DNT Randomization** - Do Not Track header randomization

#### **Network Layer Protection**
- ✅ **MAC Address Spoofing** - Hardware identifier randomization
- ✅ **DNS Leak Prevention** - Forced DNS through proxy (socks5h)
- ✅ **Comprehensive DNS Leak Detection** - Multi-service verification
- ✅ **VPN Chaining Support** - VPN → Tor multi-layer anonymity

#### **Operational Security**
- ✅ **Secure Logging** - No IP/URL leaks in logs
- ✅ **Memory Protection** - Secure memory wiping
- ✅ **System Security Audit** - Pre-flight security checks
- ✅ **Entropy Monitoring** - Cryptographic randomness verification
- ✅ **Graceful Cleanup** - Automatic restoration of all changes

---

## 🚀 Quick Start

### Basic Test (No Anonymity)
```bash
python web_load_tester.py --target-url http://localhost:8080 --users 50
```

### Maximum Anonymity (Requires sudo)
```bash
sudo python web_load_tester.py \
  --target-url https://yoursite.com \
  --users 100 \
  --use-tor \
  --tor-hops 5 \
  --mac-interface wlan0 \
  --identity-rotation 60 \
  --cover-traffic \
  --check-dns-leak
```

---

## 📋 Installation

### System Requirements
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum (8GB+ for large tests)
- **Disk**: 500MB free space
- **Network**: Stable connection (Tor requires ~1-2 Mbps)

### Dependencies (Auto-Install)
```bash
git clone https://github.com/yourusername/ethical-web-load-tester.git
cd ethical-web-load-tester
python web_load_tester.py --help  # Auto-installs dependencies
```

### External Tools

#### Tor (Required for anonymity)
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install tor

# macOS
brew install tor

# Verify installation
tor --version
```

#### For MAC Spoofing (Linux)
```bash
# Ubuntu/Debian
sudo apt install iproute2

# Fedora/RHEL
sudo dnf install iproute

# Arch Linux
sudo pacman -S iproute2
```

---

## 📖 Complete Usage Guide

### Command-Line Options

#### Required Arguments
| Option | Description |
|--------|-------------|
| `--target-url` | Target URL (ONLY authorized systems!) |

#### Load Test Configuration
| Option | Default | Description |
|--------|---------|-------------|
| `--users` | 50 | Concurrent users (max: 2000) |
| `--spawn-rate` | 10 | Users spawned per second |
| `--duration` | 60 | Test duration in seconds |
| `--target-paths` | `/` | Comma-separated paths |
| `--post-data` | None | POST data for forms |

#### Tor Configuration (Advanced)
| Option | Default | Description |
|--------|---------|-------------|
| `--use-tor` | False | Enable Tor routing |
| `--tor-hops` | 3 | Number of hops (3-5) |
| `--use-bridges` | False | Use Tor bridges |
| `--identity-rotation` | 0 | Rotate identity every N seconds |
| `--show-circuits` | False | Display active circuits |

#### Additional Anonymity
| Option | Description |
|--------|-------------|
| `--vpn-proxy` | VPN SOCKS5 proxy for double-hop |
| `--mac-interface` | Network interface for MAC spoofing |

#### Anti-Correlation Features
| Option | Default | Description |
|--------|---------|-------------|
| `--cover-traffic` | False | Generate cover traffic |
| `--cover-traffic-interval` | 30 | Cover traffic interval (seconds) |

#### Security & Diagnostics
| Option | Description |
|--------|-------------|
| `--check-dns-leak` | Check for DNS leaks |
| `--security-check` | Run system security audit |
| `--dry-run` | Test config without traffic |

---

## 🎓 Advanced Examples

### 1. Basic Authorized Test
```bash
python web_load_tester.py \
  --target-url http://localhost:8080 \
  --users 50 \
  --duration 120
```

### 2. Tor with Identity Rotation
```bash
python web_load_tester.py \
  --target-url https://yoursite.com \
  --users 100 \
  --use-tor \
  --identity-rotation 90 \
  --duration 600
```

### 3. Maximum Security Stack
```bash
sudo python web_load_tester.py \
  --target-url https://yoursite.com \
  --users 150 \
  --spawn-rate 5 \
  --use-tor \
  --tor-hops 5 \
  --mac-interface wlan0 \
  --identity-rotation 60 \
  --cover-traffic \
  --cover-traffic-interval 20 \
  --check-dns-leak \
  --security-check \
  --duration 300
```

### 4. VPN + Tor Multi-Layer
```bash
# First connect to VPN, then:
sudo python web_load_tester.py \
  --target-url https://yoursite.com \
  --users 100 \
  --vpn-proxy socks5://localhost:1080 \
  --use-tor \
  --tor-hops 4 \
  --mac-interface eth0 \
  --identity-rotation 120
```

### 5. Censorship Circumvention (With Bridges)
```bash
sudo python web_load_tester.py \
  --target-url https://yoursite.com \
  --users 75 \
  --use-tor \
  --use-bridges \
  --mac-interface wlan0 \
  --cover-traffic \
  --duration 300
```

### 6. Security Audit Only
```bash
python web_load_tester.py \
  --target-url http://localhost \
  --security-check \
  --show-circuits \
  --dry-run
```

### 7. Multi-Path Load Testing
```bash
python web_load_tester.py \
  --target-url https://yoursite.com \
  --target-paths /,/api/v1/users,/api/v1/products,/admin \
  --users 200 \
  --spawn-rate 15 \
  --duration 180
```

### 8. Form/API Testing
```bash
python web_load_tester.py \
  --target-url https://yoursite.com/api/login \
  --post-data "username=testuser&password=testpass123&remember=true" \
  --users 50 \
  --duration 120
```

---

## 🛡️ What EWLT v3.0 Actually Protects Against

### ✅ PROTECTED
| Threat | Protection Level | Mechanism |
|--------|-----------------|-----------|
| **IP Tracking** | 🟢 Excellent | Tor multi-hop circuits |
| **DNS Leaks** | 🟢 Excellent | socks5h + leak