# Ethical Web Load Tester (EWLT) v3.0
### Professional Security Testing & Performance Analysis Suite

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Security: Enhanced](https://img.shields.io/badge/security-enhanced-green.svg)]()
[![Version](https://img.shields.io/badge/version-3.0-brightgreen.svg)]()

---

## ⚠️ CRITICAL LEGAL NOTICE

**THIS TOOL IS STRICTLY FOR EDUCATIONAL, TESTING, AND RESEARCH PURPOSES ONLY**

### ✅ LEGAL USE
- Testing **your own** websites and systems
- Testing systems where you have **explicit written permission**
- Educational research in controlled environments
- Security auditing of **authorized** infrastructure

### ❌ ILLEGAL USE
Testing any system **without authorization** is a **FEDERAL CRIME** under:
- **Computer Fraud and Abuse Act (CFAA)** - USA 🇺🇸
- **Computer Misuse Act** - UK 🇬🇧
- **Criminal Code** - Canada 🇨🇦
- Similar laws in **virtually every country**

**⚖️ PENALTIES:** Up to **10 years imprisonment** + **$250,000 fines** + civil liability

**The developer assumes ZERO liability for any misuse, illegal activities, or damages caused by this tool.**

---

## 🎯 What is EWLT?

EWLT is a **professional-grade load testing and security analysis framework** designed to help developers, security researchers, and DevOps teams:

✨ **Test web applications** under realistic and extreme load conditions  
🔍 **Identify performance bottlenecks** before they affect real users  
🛡️ **Verify security configurations** and DDoS mitigation strategies  
📊 **Generate comprehensive reports** with actionable insights  
🔒 **Learn about privacy technologies** (Tor, VPNs, MAC spoofing)  

### Why "Ethical"?
This tool includes powerful attack simulation and anonymity features **NOT** for malicious purposes, but to help you:
- **Defend** your applications against real-world attacks
- **Understand** how attackers think and operate
- **Test** your infrastructure's resilience
- **Learn** about privacy-enhancing technologies

---

## 🚀 Features

### 🎯 Advanced Load Testing
- **5 Attack Modes**: Flood, Slowloris, Burst, Adaptive (ML-inspired), RUDY
- **Realistic Traffic Simulation**: Human-like browsing patterns with Poisson distribution timing
- **Multi-Path Testing**: Test multiple endpoints simultaneously
- **Session Management**: Authenticated flow testing with cookie handling
- **Form Submission**: POST data testing with customizable payloads
- **HTTP/2 Support**: Modern protocol testing

### 📊 Professional Reporting
- **Real-Time Dashboard**: Colored terminal output with progress bars
- **Comprehensive Metrics**: Response times (avg, median, P95, P99), RPS, failure rates
- **Multiple Export Formats**: JSON, CSV, HTML reports
- **Status Code Analysis**: Detailed HTTP status distribution
- **Vulnerability Insights**: Automatic detection of bottlenecks and weaknesses
- **Historical Tracking**: Compare tests over time

### 🔒 Enhanced Privacy & Anonymity
- **Tor Integration**: Automatic Tor network setup and management
- **Circuit Monitoring**: Health checks and automatic failover
- **Identity Rotation**: Periodic Tor circuit changes (configurable intervals)
- **DNS Leak Prevention**: Force DNS resolution through proxy (socks5h)
- **MAC Address Spoofing**: Change hardware identifier (Linux/macOS)
- **Multi-Hop Proxy Chains**: VPN + Tor + SOCKS combinations
- **User Agent Rotation**: 1000+ realistic browser fingerprints (2025 profiles)
- **TLS Fingerprint Randomization**: Varied cipher suites and SSL configurations
- **Request Timing Obfuscation**: Poisson distribution-based delays

### 🛡️ Security Testing Features
- **Application Fuzzing**: XSS, SQLi, path traversal, command injection, buffer overflow
- **Attack Simulation**: Realistic DDoS patterns for defense testing
- **Rate Limit Testing**: Verify throttling mechanisms
- **Connection Exhaustion**: Test max connection limits
- **Resource Depletion**: Memory/CPU exhaustion detection
- **Cache Behavior Analysis**: CDN effectiveness testing
- **Auto-Scaling Validation**: Trigger and monitor scaling events

### ⚙️ Advanced Technical Features
- **Adaptive Retry Logic**: Exponential backoff with custom strategies
- **Connection Pooling**: 100 concurrent connections per user
- **Smart Error Handling**: Categorized error tracking and analysis
- **Thread-Safe Metrics**: Lock-based concurrent data collection
- **Memory Efficient**: Deque-based storage with 10K element limits
- **Cross-Platform**: Works on Linux, macOS, Windows
- **Graceful Cleanup**: Automatic resource restoration on exit
- **Signal Handling**: Proper Ctrl+C interruption

---

## 📋 Requirements

### System Requirements
- **Python**: 3.8 or higher
- **OS**: 
  - Linux (Ubuntu 20.04+, Debian 10+, Fedora, Arch, etc.)
  - macOS 10.15+
  - Windows 10/11 (limited MAC spoofing support)
- **RAM**: Minimum 2GB (4GB+ recommended for >200 users)
- **CPU**: 2+ cores recommended
- **Network**: Stable internet connection

### Dependencies (Auto-Installed)
```
locust>=2.15.0       # Load testing framework
requests>=2.31.0     # HTTP library
PySocks>=1.7.1       # SOCKS proxy support
stem>=1.8.0          # Tor control library
aiohttp>=3.9.0       # Async HTTP client
colorama>=0.4.6      # Terminal colors
tabulate>=0.9.0      # Table formatting
tqdm>=4.66.0         # Progress bars
```

### Optional External Tools
- **Tor** - For anonymity features ([download](https://www.torproject.org/download/))
- **sudo/admin access** - Required for MAC spoofing
- **iproute2** (Linux) - For MAC spoofing (`ip` command)

---

## 🔧 Installation

### Quick Install

```bash
# Clone repository
git clone https://github.com/yourusername/ethical-web-load-tester.git
cd ethical-web-load-tester

# Run (dependencies auto-install on first run)
python web_load_tester.py --help
```

### Installing Tor (Optional - for anonymity)

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install -y tor
sudo systemctl start tor
sudo systemctl enable tor
```

**macOS (Homebrew):**
```bash
brew install tor
brew services start tor
```

**Fedora/RHEL:**
```bash
sudo dnf install -y tor
sudo systemctl start tor
sudo systemctl enable tor
```

**Windows:**
1. Download Tor Browser Bundle from https://www.torproject.org/download/
2. Extract to `C:\Program Files\Tor Browser`
3. Add to PATH or use full path

**Verify Installation:**
```bash
tor --version
# Should output: Tor version 0.4.x.x
```

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

#### 2. Dry Run (Verify Configuration First)
```bash
python web_load_tester.py \
  --target-url http://localhost:8080 \
  --users 100 \
  --duration 120 \
  --dry-run
```

#### 3. Test Multiple Endpoints
```bash
python web_load_tester.py \
  --target-url https://mysite.com \
  --target-paths /,/about,/products,/api/health \
  --users 100 \
  --spawn-rate 10 \
  --duration 180
```

---

### Advanced Examples

#### 4. Adaptive Load Pattern (NEW!)
```bash
python web_load_tester.py \
  --target-url https://yoursite.com \
  --users 150 \
  --attack-mode adaptive \
  --duration 600
```
*Automatically adjusts load based on server response times*

#### 5. With Tor Anonymity
```bash
python web_load_tester.py \
  --target-url https://yoursite.com \
  --users 100 \
  --use-tor \
  --duration 300
```

#### 6. With Identity Rotation (Change Circuit Every 60s)
```bash
python web_load_tester.py \
  --target-url https://yoursite.com \
  --users 150 \
  --use-tor \
  --identity-rotation 60 \
  --check-dns-leak \
  --duration 600
```

#### 7. With MAC Spoofing (Requires sudo)
```bash
sudo python web_load_tester.py \
  --target-url http://yoursite.com \
  --users 50 \
  --mac-interface wlan0 \
  --duration 120
```
*Replace `wlan0` with your interface: `ip link` (Linux) or `ifconfig` (macOS)*

#### 8. Full Anonymity Stack
```bash
sudo python web_load_tester.py \
  --target-url https://yoursite.com \
  --users 100 \
  --spawn-rate 5 \
  --use-tor \
  --mac-interface eth0 \
  --identity-rotation 90 \
  --check-dns-leak \
  --duration 600 \
  --attack-mode adaptive
```

#### 9. Slowloris Attack Simulation
```bash
python web_load_tester.py \
  --target-url https://yoursite.com \
  --users 200 \
  --attack-mode slowloris \
  --duration 300 \
  --consent-file consent.json
```

#### 10. Application Fuzzing
```bash
python web_load_tester.py \
  --target-url https://yoursite.com/login \
  --users 50 \
  --attack-mode flood \
  --enable-fuzzing \
  --post-data "username=test&password=test" \
  --duration 180 \
  --consent-file consent.json
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
| `--users` | 50 | Number of concurrent users (1-1000) |
| `--spawn-rate` | 10 | Users spawned per second (1-100) |
| `--duration` | 60 | Test duration in seconds |
| `--target-paths` | `/` | Comma-separated paths (e.g., `/,/about,/api`) |
| `--post-data` | None | POST data (`key=value&key2=value2`) |

### Attack Modes
| Option | Description |
|--------|-------------|
| `--attack-mode flood` | **High-volume request flooding** (default) |
| `--attack-mode slowloris` | **Resource exhaustion via slow connections** |
| `--attack-mode burst` | **Rapid bursts of requests** |
| `--attack-mode adaptive` | **ML-inspired adaptive load** (NEW!) |
| `--attack-mode rudy` | **Slow POST body (R-U-Dead-Yet)** |

### Anonymity & Privacy
| Option | Description |
|--------|-------------|
| `--use-tor` | Route traffic through Tor network |
| `--vpn-proxy` | Custom SOCKS5 proxy (`socks5://host:port`) |
| `--mac-interface` | Network interface for MAC spoofing (requires sudo) |
| `--identity-rotation N` | Rotate Tor identity every N seconds (0=disabled) |
| `--check-dns-leak` | Check for DNS leaks (requires `--use-tor`) |

### Security Testing
| Option | Description |
|--------|-------------|
| `--enable-fuzzing` | Enable application fuzzing (XSS, SQLi, etc.) |
| `--consent-file` | Path to consent JSON (required for advanced modes) |

### Testing Options
| Option | Description |
|--------|-------------|
| `--dry-run` | Test configuration without sending traffic |

---

## 📊 Understanding Results

### Sample Output
```
╔════════════════════════════════════════════════════════════════╗
║  TEST RESULTS - 20251012_143025                                ║
╚════════════════════════════════════════════════════════════════╝

┌────────────────────┬─────────────────────────────────────────┐
│ Metric             │ Value                                   │
├────────────────────┼─────────────────────────────────────────┤
│ Target             │ https://mysite.com                      │
│ Attack Mode        │ adaptive                                │
│ Total Requests     │ 45,823                                  │
│ Successful         │ 45,532 (99.4%)                          │
│ Failed             │ 291 (0.6%)                              │
│ Duration           │ 300s                                    │
│ RPS                │ 152.74                                  │
└────────────────────┴─────────────────────────────────────────┘

⏱ Response Times:
Average         : 245.67ms
Median          : 198.23ms
95th Percentile : 512.89ms
99th Percentile : 1,023.45ms
Min             : 45ms
Max             : 2,341ms

📊 Status Code Distribution:
Code    Count     Percentage
200     44,832    97.8%
304     700       1.5%
404     245       0.5%
500     46        0.1%

✓ JSON report: ~/.ewlt_reports/report_20251012_143025.json
✓ CSV report: ~/.ewlt_reports/report_20251012_143025.csv
```

### Interpreting Metrics

**Response Time Benchmarks:**
| Time Range | Performance | Action Required |
|------------|-------------|-----------------|
| 0-100ms | 🟢 Excellent | Maintain optimization |
| 100-300ms | 🟢 Good | Monitor trends |
| 300-500ms | 🟡 Acceptable | Investigate bottlenecks |
| 500-1000ms | 🟠 Poor | Optimize immediately |
| 1000ms+ | 🔴 Critical | Major issues present |

**Failure Rate Guidelines:**
| Rate | Status | Interpretation |
|------|--------|----------------|
| 0-1% | 🟢 Excellent | System stable |
| 1-5% | 🟢 Good | Acceptable under load |
| 5-10% | 🟡 Warning | Approaching capacity |
| 10-20% | 🟠 Critical | System overloaded |
| 20%+ | 🔴 Failure | Infrastructure issues |

**Requests Per Second (RPS) Benchmarks:**
| Application Type | Expected RPS | High Performance |
|-----------------|--------------|------------------|
| Static HTML/CDN | 10,000+ | 50,000+ |
| WordPress/PHP | 100-500 | 1,000+ |
| Django/Flask | 500-2,000 | 5,000+ |
| Node.js API | 5,000-20,000 | 50,000+ |
| Go/Rust API | 20,000-50,000 | 100,000+ |

---

## 🔒 Security & Privacy Best Practices

### For Maximum Anonymity

#### 1. **Use a Virtual Machine**
```bash
# Example: VirtualBox with Ubuntu
# Take snapshot before testing
VBoxManage snapshot "TestVM" take "before_test"

# Run test in VM
python web_load_tester.py --target-url <url> --use-tor

# Destroy VM after testing
VBoxManage snapshot "TestVM" restore "before_test"
```

#### 2. **Tor + VPN Combination**
```bash
# Step 1: Connect to VPN (manually or via script)
sudo openvpn --config myvpn.ovpn &

# Step 2: Run EWLT with Tor
python web_load_tester.py \
  --target-url <url> \
  --use-tor \
  --identity-rotation 60 \
  --users 100

# This creates: You → VPN → Tor → Target
# VPN hides Tor usage from ISP
# Tor provides anonymity from VPN provider
```

#### 3. **MAC Address Spoofing**
```bash
# Always spoof MAC BEFORE connecting to network
sudo python web_load_tester.py \
  --target-url <url> \
  --mac-interface wlan0 \
  --use-tor \
  --users 50

# Tool automatically restores original MAC on exit
# Backup stored in ~/.ewlt_mac_backup.json
```

#### 4. **DNS Leak Prevention**
The tool automatically prevents DNS leaks when using `--use-tor` by:
- Using `socks5h://` protocol (DNS through proxy)
- Forcing all DNS queries through Tor
- Disabling system DNS resolver

**Verify:**
```bash
python web_load_tester.py \
  --target-url <url> \
  --use-tor \
  --check-dns-leak
```

#### 5. **Access Web UI Securely**
If using Locust web interface (port 8089):
```bash
# NEVER use regular browser - use Tor Browser
# Download: https://www.torproject.org/download/

# Access via: http://127.0.0.1:8089
# Through Tor Browser for anonymity
```

### ⚠️ What This Tool Does NOT Protect Against

- ❌ **Advanced Traffic Correlation**: Nation-state level surveillance
- ❌ **Browser Fingerprinting**: If using web UI in regular browser
- ❌ **Timing Analysis**: Sophisticated adversaries can correlate patterns
- ❌ **Physical Surveillance**: Cameras, law enforcement
- ❌ **Compromised Tor Nodes**: Exit node monitoring
- ❌ **Legal Consequences**: Unauthorized testing is still illegal
- ❌ **Zero-Day Exploits**: Unknown vulnerabilities
- ❌ **Quantum Computing Attacks**: Future cryptographic threats

---

## 🛡️ Defensive Use: Protecting Your Site

### How to Use EWLT for Security

#### 1. **Test Your DDoS Mitigation**
```bash
# Simulate DDoS attack
python web_load_tester.py \
  --target-url https://yoursite.com \
  --users 500 \
  --attack-mode flood \
  --duration 300

# Monitor:
# - WAF/CDN behavior (Cloudflare, AWS Shield)
# - Rate limiting effectiveness
# - Auto-scaling triggers
# - Legitimate traffic handling
```

#### 2. **Identify Performance Bottlenecks**
```bash
# Test multiple endpoints
python web_load_tester.py \
  --target-url https://yoursite.com \
  --target-paths /,/api/users,/api/products,/checkout \
  --users 100 \
  --attack-mode adaptive \
  --duration 600

# Analyze results to find:
# - Slow database queries
# - Inefficient API endpoints
# - Missing indexes
# - N+1 query problems
```

#### 3. **Validate Caching Strategies**
```bash
# Test 1: Cold cache
python web_load_tester.py \
  --target-url https://yoursite.com/api/data \
  --users 50 \
  --duration 60

# Wait 5 minutes for cache warm-up

# Test 2: Warm cache
python web_load_tester.py \
  --target-url https://yoursite.com/api/data \
  --users 200 \
  --duration 60

# Compare response times:
# Cold cache: ~500ms
# Warm cache: ~50ms (10x improvement)
```

#### 4. **Test Connection Limits**
```bash
# Slowloris to test max connections
python web_load_tester.py \
  --target-url https://yoursite.com \
  --users 300 \
  --attack-mode slowloris \
  --duration 180 \
  --consent-file consent.json

# Verify:
# - Connection timeout enforcement (< 60s)
# - Max connections per IP (< 100)
# - Reverse proxy protection active
```

#### 5. **Verify Rate Limiting**
```bash
# High-volume burst
python web_load_tester.py \
  --target-url https://yoursite.com/api \
  --users 100 \
  --attack-mode burst \
  --duration 120

# Expected results:
# - 429 status codes appearing
# - Rate limit headers present
# - Gradual request acceptance
```

---

## 🔍 Troubleshooting

### Common Issues & Solutions

#### Issue 1: "Tor not found"
**Error:** `✗ Tor not found. Install from https://www.torproject.org/`

**Solution:**
```bash
# Ubuntu/Debian
sudo apt install tor

# macOS
brew install tor

# Verify
tor --version
```

---

#### Issue 2: "MAC spoofing failed"
**Error:** `✗ MAC spoofing failed: Operation not permitted`

**Solutions:**
```bash
# 1. Run with sudo
sudo python web_load_tester.py --mac-interface wlan0 ...

# 2. Check interface name
ip link show          # Linux
ifconfig              # macOS

# 3. Ensure interface is down first
sudo ip link set wlan0 down
sudo python web_load_tester.py --mac-interface wlan0 ...

# 4. Install required tools (Linux)
sudo apt install iproute2
```

---

#### Issue 3: "Connection refused" errors
**Symptoms:** High failure rate, many connection errors

**Causes & Solutions:**
```bash
# 1. Target server is down
curl http://localhost:8080  # Test manually

# 2. Firewall blocking requests
sudo ufw allow from 192.168.1.0/24  # Whitelist test IP

# 3. Too many concurrent users
python web_load_tester.py --users 20  # Reduce load

# 4. Server overwhelmed
# Reduce spawn rate and total users
python web_load_tester.py \
  --users 50 \
  --spawn-rate 5 \
  --duration 120
```

---

#### Issue 4: Tor circuit takes too long
**Symptoms:** Hanging at "Bootstrapping Tor network..."

**Solutions:**
```bash
# 1. Wait longer (up to 60 seconds)
# First run can take time

# 2. Check Tor service
sudo systemctl status tor
sudo systemctl restart tor

# 3. Check firewall
sudo ufw allow 9050
sudo ufw allow 9051

# 4. Check Tor logs
journalctl -u tor -f         # Linux
tail -f /var/log/tor/log     # macOS

# 5. Test Tor manually
curl --socks5-hostname localhost:9050 https://check.torproject.org/api/ip
```

---

#### Issue 5: DNS leaks detected
**Symptoms:** DNS leak test shows non-Tor DNS servers

**Causes:**
- Not using `socks5h://` protocol
- System DNS resolver bypassing proxy

**Solution:**
```bash
# Tool automatically uses socks5h when --use-tor enabled
# Verify in logs:
grep "socks5h" ~/.ewlt_logs/ewlt_*.log

# Should see:
# ✓ Tor SOCKS5 proxy configured (DNS leak prevention)

# Manual test:
curl --socks5-hostname localhost:9050 https://api.ipify.org
# Should return Tor exit IP
```

---

#### Issue 6: "Too many open files"
**Error:** `OSError: [Errno 24] Too many open files`

**Solution:**
```bash
# Temporary fix
ulimit -n 65535

# Permanent fix (Linux)
sudo tee -a /etc/security/limits.conf << EOF
* soft nofile 65535
* hard nofile 65535
EOF

# Logout and login
ulimit -n  # Verify

# Or reduce concurrent users
python web_load_tester.py --users 100  # Instead of 1000
```

---

#### Issue 7: High memory usage
**Symptoms:** System slows down, OOM killer activates

**Solutions:**
```bash
# 1. Reduce users and spawn rate
python web_load_tester.py \
  --users 50 \
  --spawn-rate 5

# 2. Monitor memory during test
watch -n 1 'free -h'

# 3. Increase system swap (emergency)
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## 📚 Educational Resources

### Learn More About

**Load Testing:**
- [Locust Documentation](https://docs.locust.io/) - Official Locust guide
- [Web Performance](https://web.dev/performance/) - Google's performance guide
- [Load Testing Best Practices](https://www.blazemeter.com/blog/performance-testing-vs-load-testing-vs-stress-testing) - BlazeMeter guide

**Tor & Anonymity:**
- [Tor Project](https://www.torproject.org/) - Official Tor documentation
- [EFF's Surveillance Self-Defense](https://ssd.eff.org/) - Privacy protection
- [How Tor Works](https://2019.www.torproject.org/about/overview.html.en) - Technical overview

**Network Security:**
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/) - Security testing
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework) - Security standards
- [DDoS Mitigation](https://www.cloudflare.com/learning/ddos/ddos-mitigation/) - Cloudflare guide

**Ethical Hacking:**
- [HackerOne Resources](https://www.hackerone.com/resources) - Bug bounty platform
- [Bugcrowd University](https://www.bugcrowd.com/hackers/bugcrowd-university/) - Free courses
- [Penetration Testing](https://www.offensive-security.com/metasploit-unleashed/) - Metasploit guide

---

## 🤝 Contributing

Contributions are welcome! Please:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

### Contribution Guidelines

#### Code Quality
- Follow PEP 8 style guide
- Add type hints where appropriate
- Write docstrings for all functions
- Include unit tests for new features

#### Security
- Ensure all features maintain ethical use principles
- Add appropriate warnings for dangerous features
- Never reduce security protections
- Test anonymity features thoroughly

#### Documentation
- Update README.md with new features
- Add examples to usage guide
- Document all command-line options
- Include troubleshooting steps

#### Testing
- Test on Linux, macOS, and Windows (if applicable)
- Verify Tor integration works
- Ensure MAC spoofing cleanup works
- Test with various Python versions (3.8, 3.9, 3.10, 3.11, 3.12)

---

## 📜 Changelog

### Version 3.0 (Current) - October 2025
**🎉 Major Release - Complete Rewrite**

**New Features:**
- ✨ **5 Attack Modes**: Flood, Slowloris, Burst, Adaptive, RUDY
- 🧠 **Adaptive Load Pattern**: ML-inspired intelligent load adjustment
- 📊 **Enhanced Reporting**: JSON, CSV exports with colored terminal output
- 🔒 **Application Fuzzing**: XSS, SQLi, path traversal, command injection
- 🌐 **HTTP/2 Support**: Modern protocol testing
- 🎯 **Progress Bars**: Real-time visual feedback with tqdm
- 🔄 **Improved Tor Management**: Circuit monitoring and automatic failover
- 🛡️ **Enhanced MAC Spoofing**: Automatic backup and restore
- 📈 **Advanced Metrics**: P95/P99 percentiles, status code distribution
- 🎨 **Colored Output**: Professional terminal interface with colorama

**Improvements:**
- 🚀 Better performance with connection pooling (100 connections)
- 🔐 Enhanced privacy with 1000+ user agent profiles
- 🧹 Graceful cleanup with proper signal handling
- 📝 Comprehensive logging with secure file permissions
- 🎲 Poisson distribution for realistic timing
- 🔍 Automatic vulnerability detection
- 💾 Thread-safe metrics collection
- 🛠️ Cross-platform compatibility improvements

**Bug Fixes:**
- Fixed MAC restoration on unexpected exit
- Improved Tor bootstrap reliability
- Better error handling for network failures
- Fixed memory leaks in long-running tests

---

### Version 2.1 - September 2025
- Added attack modes (flood, slowloris, burst)
- Basic fuzzing support
- Enhanced reporting
- Identity rotation improvements

---

### Version 2.0 - August 2025
- Complete rewrite with enhanced security
- Integrated Tor management
- Improved DNS leak prevention
- User agent rotation
- Cross-platform MAC spoofing
- Secure logging system
- Dry run mode

---

### Version 1.0 - July 2025
- Initial release
- Basic load testing
- Simple Tor support
- MAC spoofing (Linux only)

---

## 🙏 Acknowledgments

Special thanks to:
- **[Locust](https://locust.io/)** - Excellent load testing framework
- **[Tor Project](https://www.torproject.org/)** - Anonymity network
- **[Requests](https://requests.readthedocs.io/)** - HTTP library
- **[Stem](https://stem.torproject.org/)** - Tor controller library
- Security research community for inspiration and feedback
- All contributors who helped improve this tool

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 Dheeraj Kumar

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## ⚖️ Legal Disclaimer

**READ CAREFULLY BEFORE USING THIS SOFTWARE**

THIS SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED. THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE SOFTWARE IS WITH YOU.

### By using this software, you agree to:

1. ✅ **Only test systems you own** or have **explicit written permission** to test
2. ✅ **Comply with all applicable** local, state, national, and international laws
3. ✅ **Accept full responsibility** for your actions
4. ✅ **Hold the developer harmless** from any damages or legal issues

### You understand that:

- ⚠️ **Unauthorized access to computer systems is ILLEGAL**
- ⚠️ This tool **can be detected** and may result in IP bans or legal action
- ⚠️ Anonymity features **do not guarantee complete protection**
- ⚠️ You are **solely responsible** for how you use this tool
- ⚠️ **Violating these terms may result in:**
  - Federal criminal charges
  - Up to 10 years imprisonment
  - Fines up to $250,000
  - Civil liability for damages
  - Permanent criminal record

### Developer Liability:

The developer of this software:
- ❌ Does **NOT** endorse illegal activities
- ❌ Is **NOT** responsible for misuse
- ❌ Assumes **ZERO** liability for any damages
- ❌ Provides **NO** legal advice or protection
- ❌ Cannot be held accountable for user actions

---

## 📧 Contact & Support

### Getting Help

**📖 Documentation:**
- Full guides in `/docs` directory
- Configuration examples in `/examples`
- Video tutorials on [YouTube Channel](#)

**🐛 Bug Reports:**
- [GitHub Issues](https://github.com/yourusername/ethical-web-load-tester/issues)
- Include log files from `~/.ewlt_logs/`
- Describe steps to reproduce

**💡 Feature Requests:**
- [GitHub Discussions](https://github.com/yourusername/ethical-web-load-tester/discussions)
- Explain use case and benefits
- Consider contributing implementation

**🔒 Security Concerns:**
- Email: security@yourproject.com
- PGP key available in repository
- Responsible disclosure appreciated

### Community

- **Discord**: Join our server for real-time help
- **Reddit**: r/EthicalWebLoadTester
- **Twitter**: @EWLT_Official
- **Blog**: blog.ewlt.dev

---

## 🌟 Star History

If you find this project useful, please consider giving it a star! ⭐

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/ethical-web-load-tester&type=Date)](https://star-history.com/#yourusername/ethical-web-load-tester&Date)

---

## 📈 Project Stats

![GitHub stars](https://img.shields.io/github/stars/yourusername/ethical-web-load-tester?style=social)
![GitHub forks](https://img.shields.io/github/forks/yourusername/ethical-web-load-tester?style=social)
![GitHub issues](https://img.shields.io/github/issues/yourusername/ethical-web-load-tester)
![GitHub license](https://img.shields.io/github/license/yourusername/ethical-web-load-tester)
![Python version](https://img.shields.io/badge/python-3.8%2B-blue)

---

**⚠️ FINAL REMINDER**: Only test systems you own or have written permission to test. Unauthorized testing is illegal, unethical, and can result in serious criminal penalties.

**Remember: With great power comes great responsibility. Use this tool ethically and legally.**

---

<div align="center">

**EWLT v3.0** - Professional Security Testing Suite  
*Educational and Authorized Testing Only*

Made with ❤️ for the security community

[⬆ Back to Top](#ethical-web-load-tester-ewlt-v30)

</div>