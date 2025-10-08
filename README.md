# Ethical Web Load Tester (EWLT) v2.0
### Enhanced Security & Anonymity Edition

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Security: Enhanced](https://img.shields.io/badge/security-enhanced-green.svg)]()

## ⚠️ CRITICAL LEGAL NOTICE

**THIS TOOL IS STRICTLY FOR EDUCATIONAL, TESTING, AND RESEARCH PURPOSES ONLY**

- ✅ **LEGAL USE**: Testing your own websites, systems you own, or systems where you have explicit written permission
- ❌ **ILLEGAL USE**: Testing any system without authorization is a **FEDERAL CRIME** under:
  - Computer Fraud and Abuse Act (CFAA) in the USA
  - Computer Misuse Act in the UK
  - Similar laws in virtually every country

**⚖️ The developer assumes NO liability for any misuse, illegal activities, or damages caused by this tool.**

---

## 🎯 What is EWLT?

EWLT is a sophisticated load testing framework designed to help you:
- **Test your own web applications** under realistic load conditions
- **Identify performance bottlenecks** before they affect real users
- **Verify security configurations** in your infrastructure
- **Learn about privacy and anonymity** technologies (Tor, VPNs, MAC spoofing)

### Why "Ethical"?
This tool includes powerful anonymity features not for malicious purposes, but to help security researchers and developers understand:
- How to protect against DDoS attacks
- How anonymity networks work
- How to detect and prevent malicious traffic
- Privacy-enhancing technologies

---

## 🚀 Features

### Core Load Testing
- ✨ **Realistic Traffic Simulation** - Mimics human browsing patterns
- 📊 **Detailed Performance Metrics** - Response times, throughput, failure rates
- 🔄 **Configurable Load Patterns** - Control users, spawn rates, duration
- 🎯 **Multi-Path Testing** - Test multiple endpoints simultaneously
- 📝 **Form Submission Testing** - Simulate POST requests with custom data

### Enhanced Privacy & Anonymity
- 🧅 **Tor Integration** - Route traffic through Tor network with automatic setup
- 🔄 **Identity Rotation** - Periodically change Tor circuits during testing
- 🛡️ **DNS Leak Prevention** - Force DNS resolution through proxy (socks5h)
- 🎭 **User Agent Rotation** - Randomize browser fingerprints
- 💾 **MAC Address Spoofing** - Change hardware identifier (Linux/macOS)
- 🔌 **VPN/Proxy Support** - Custom SOCKS5 proxy configuration
- 🔍 **DNS Leak Detection** - Verify your traffic is properly anonymized

### Security Features
- 📁 **Secure Logging** - Anonymized logs with no IP/URL leaks
- 🎲 **Request Timing Obfuscation** - Randomized delays for natural patterns
- 🔒 **TLS Fingerprint Randomization** - Vary connection characteristics
- 🚫 **Dry Run Mode** - Test configuration without sending traffic
- ⚡ **Graceful Shutdown** - Clean cleanup of resources and restoration of settings

---

## 📋 Requirements

### System Requirements
- **Python**: 3.8 or higher
- **Operating System**: 
  - Linux (Ubuntu, Debian, Fedora, Arch, etc.)
  - macOS (10.15+)
  - Windows 10/11 (limited MAC spoofing support)
- **RAM**: Minimum 2GB (4GB+ recommended for larger tests)
- **Network**: Stable internet connection

### Dependencies (Auto-installed)
- `locust` - Load testing framework
- `requests` - HTTP library
- `PySocks` - SOCKS proxy support
- `stem` - Tor control library

### Optional External Tools
- **Tor Browser** or **Tor standalone** - For anonymity features
  - Download: https://www.torproject.org/download/
- **iproute2** (Linux) - For MAC spoofing (`ip` command)
- **Administrator/sudo access** - Required for MAC spoofing

---

## 🔧 Installation

### Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/ethical-web-load-tester.git
cd ethical-web-load-tester

# Run the tool (dependencies auto-install)
python web_load_tester.py --target-url http://localhost:8080 --users 50

# For features requiring elevated privileges (MAC spoofing)
sudo python web_load_tester.py --target-url http://localhost --mac-interface eth0 --users 50
```

### Installing Tor (for anonymity features)

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install tor
sudo systemctl start tor
```

**macOS (Homebrew):**
```bash
brew install tor
brew services start tor
```

**Windows:**
1. Download Tor Browser Bundle from https://www.torproject.org/download/
2. Extract and add the Tor executable to your PATH

---

## 📖 Usage Guide

### Basic Examples

#### 1. Simple Load Test (Your Own Site)
```bash
python web_load_tester.py \
  --target-url http://localhost:8080 \
  --users 50 \
  --duration 60
```

#### 2. Test Multiple Endpoints
```bash
python web_load_tester.py \
  --target-url https://mysite.com \
  --target-paths /,/about,/products,/contact \
  --users 100 \
  --spawn-rate 10 \
  --duration 120
```

#### 3. Dry Run (Verify Configuration)
```bash
python web_load_tester.py \
  --target-url http://localhost \
  --users 100 \
  --dry-run
```

### Advanced Examples

#### 4. With Tor Anonymity
```bash
python web_load_tester.py \
  --target-url https://yoursite.com \
  --users 100 \
  --use-tor \
  --duration 300
```

#### 5. With Identity Rotation (Change Tor Circuit Every 60s)
```bash
python web_load_tester.py \
  --target-url https://yoursite.com \
  --users 150 \
  --use-tor \
  --identity-rotation 60 \
  --duration 600
```

#### 6. With MAC Spoofing (Requires sudo)
```bash
sudo python web_load_tester.py \
  --target-url http://localhost \
  --users 50 \
  --mac-interface wlan0 \
  --duration 120
```
*Note: Replace `wlan0` with your interface (use `ip link` on Linux, `ifconfig` on macOS)*

#### 7. Full Anonymity Stack
```bash
sudo python web_load_tester.py \
  --target-url https://yoursite.com \
  --users 100 \
  --spawn-rate 5 \
  --use-tor \
  --mac-interface eth0 \
  --identity-rotation 90 \
  --check-dns-leak \
  --duration 300
```

#### 8. With Custom VPN/Proxy
```bash
python web_load_tester.py \
  --target-url https://yoursite.com \
  --users 75 \
  --vpn-proxy socks5://localhost:1080 \
  --duration 180
```

#### 9. Form Submission Testing
```bash
python web_load_tester.py \
  --target-url https://yoursite.com/login \
  --users 50 \
  --post-data "username=testuser&password=testpass123" \
  --duration 120
```

---

## 🎛️ Command-Line Options

### Required Arguments
| Option | Description | Example |
|--------|-------------|---------|
| `--target-url` | Target URL to test (**only sites you own!**) | `http://localhost:8080` |

### Load Test Configuration
| Option | Default | Description |
|--------|---------|-------------|
| `--users` | 50 | Number of concurrent users (max: 1000) |
| `--spawn-rate` | 10 | Users spawned per second |
| `--duration` | 60 | Test duration in seconds |
| `--target-paths` | `/` | Comma-separated paths to test |
| `--post-data` | None | POST data for form submissions |

### Anonymity Options
| Option | Description |
|--------|-------------|
| `--use-tor` | Route traffic through Tor network |
| `--vpn-proxy` | Use custom SOCKS5 proxy (e.g., `socks5://localhost:1080`) |
| `--mac-interface` | Network interface for MAC spoofing (requires sudo) |
| `--identity-rotation` | Rotate Tor identity every N seconds (0=disabled) |
| `--check-dns-leak` | Check for DNS leaks (requires `--use-tor`) |

### Testing Options
| Option | Description |
|--------|-------------|
| `--dry-run` | Test configuration without sending traffic |

---

## 🔒 Security & Privacy Best Practices

### For Maximum Anonymity

1. **Use a Virtual Machine**
   - Run EWLT in a disposable VM (VirtualBox, VMware)
   - Take snapshots before testing
   - Destroy VM after testing

2. **Tor + VPN Combination**
   - Connect to VPN first, then use Tor
   - This hides Tor usage from ISP
   ```bash
   # Connect to VPN, then:
   sudo python web_load_tester.py --target-url <url> --use-tor --mac-interface eth0
   ```

3. **MAC Address Spoofing**
   - Always spoof MAC before connecting to network
   - Tool automatically restores original MAC on exit
   - Requires sudo/admin privileges

4. **DNS Leak Prevention**
   - Use `socks5h://` (not `socks5://`) for DNS through proxy
   - Enable `--check-dns-leak` to verify
   - Tool automatically prevents leaks when using Tor

5. **Browser Access**
   - If monitoring web UI: Use Tor Browser to access `http://localhost:8089`
   - Never use regular browser when testing with anonymity features

### What This Tool Does NOT Protect Against

- ❌ Advanced traffic correlation attacks
- ❌ Browser fingerprinting (if using web UI)
- ❌ Timing analysis by sophisticated adversaries
- ❌ Physical surveillance
- ❌ Compromised Tor nodes
- ❌ Legal consequences of unauthorized testing

---

## 📊 Understanding the Results

### Sample Output
```
Starting load test:
  • Target: http://localhost:8080
  • Users: 100
  • Spawn rate: 10/s
  • Duration: 60s
  • Anonymity: Tor

✓ New Tor identity requested

============================================================
TEST RESULTS:
============================================================
Total requests: 15,432
Failures: 23
Average response time: 245.67ms
Min response time: 89ms
Max response time: 1,523ms
Requests/sec: 257.20
============================================================
```

### Interpreting Metrics

- **Total Requests**: Total HTTP requests sent
- **Failures**: Failed requests (timeouts, errors, 5xx status codes)
- **Average Response Time**: Mean time for server to respond
- **Min/Max Response Time**: Fastest and slowest responses
- **Requests/sec**: Throughput (higher = better server performance)

### Performance Baselines

| Response Time | Performance Level |
|---------------|-------------------|
| < 100ms | Excellent |
| 100-300ms | Good |
| 300-500ms | Acceptable |
| 500-1000ms | Slow |
| > 1000ms | Poor - Needs optimization |

---

## 🛡️ Defensive Use: Protecting Your Site

### How to Use EWLT for Security

1. **Test Your DDoS Mitigation**
   ```bash
   python web_load_tester.py --target-url https://yoursite.com --users 500 --duration 300
   ```
   - Monitor your WAF/CDN behavior
   - Verify rate limiting works
   - Check if legitimate traffic is affected

2. **Identify Bottlenecks**
   - Test different endpoints with `--target-paths`
   - Find slow database queries
   - Discover resource-intensive operations

3. **Validate Caching**
   - Compare response times with/without cache
   - Verify CDN effectiveness
   - Test cache invalidation

4. **Simulate Attack Patterns**
   - Use Tor to simulate anonymized attacks
   - Test IP-based blocking
   - Verify CAPTCHA triggers

---

## 🔍 Troubleshooting

### Common Issues

#### 1. "Tor not found"
**Solution:**
```bash
# Ubuntu/Debian
sudo apt install tor

# macOS
brew install tor

# Windows: Download from torproject.org
```

#### 2. "MAC spoofing failed"
**Solutions:**
- Run with `sudo` (Linux/macOS)
- Check interface name: `ip link` (Linux) or `ifconfig` (macOS)
- Ensure `iproute2` is installed (Linux)

#### 3. "Connection refused" errors
**Causes:**
- Target server is down
- Firewall blocking requests
- Too many concurrent users overwhelming server

**Solution:** Reduce `--users` and `--spawn-rate`

#### 4. Tor circuit takes too long
**Solution:**
- Wait 30-60 seconds for Tor bootstrap
- Check Tor logs: `journalctl -u tor` (Linux)
- Try restarting Tor service

#### 5. DNS leaks detected
**Causes:**
- Not using `socks5h://` (with 'h')
- Proxy not configured correctly

**Solution:** Tool automatically uses `socks5h://` when `--use-tor` is enabled

---

## 📚 Educational Resources

### Learn More About

**Load Testing:**
- [Locust Documentation](https://docs.locust.io/)
- [Web Performance Testing Guide](https://web.dev/performance/)

**Tor & Anonymity:**
- [Tor Project Official Site](https://www.torproject.org/)
- [EFF's Surveillance Self-Defense](https://ssd.eff.org/)

**Network Security:**
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Guidelines
- Ensure all features maintain ethical use principles
- Add appropriate warnings for dangerous features
- Document all new options in README
- Test on Linux, macOS, and Windows (if applicable)

---

## 📜 Changelog

### Version 2.0 (Current)
- ✨ Complete rewrite with enhanced security
- 🧅 Integrated Tor management with automatic setup
- 🔄 Identity rotation support
- 🛡️ Improved DNS leak prevention
- 🎭 User agent rotation
- 💾 Cross-platform MAC spoofing
- 🔍 DNS leak detection
- 📊 Better result reporting
- 🚦 Graceful cleanup and restoration
- 📁 Secure logging system
- ⚡ Dry run mode
- 🎲 Realistic traffic simulation

### Version 1.0
- Basic load testing functionality
- Simple Tor support
- Basic MAC spoofing (Linux only)

---

## ⚖️ Legal Disclaimer

THIS SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED. THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE SOFTWARE IS WITH YOU.

**By using this software, you agree to:**
1. Only test systems you own or have explicit written permission to test
2. Comply with all applicable local, state, national, and international laws
3. Accept full responsibility for your actions
4. Hold the developer harmless from any damages or legal issues

**You understand that:**
- Unauthorized access to computer systems is illegal
- This tool can be detected and may result in IP bans or legal action
- Anonymity features do not guarantee complete protection
- You are solely responsible for how you use this tool

---

## 📧 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/ethical-web-load-tester/issues)
- **Security Concerns**: Email security@yourproject.com
- **Documentation**: See Wiki for detailed guides

---

## 🙏 Acknowledgments

- [Locust](https://locust.io/) - Load testing framework
- [Tor Project](https://www.torproject.org/) - Anonymity network
- Security research community for inspiration

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Remember: With great power comes great responsibility. Use this tool ethically and legally.**

---

**⚠️ FINAL REMINDER**: Only test systems you own or have written permission to test. Unauthorized testing is illegal and unethical.
