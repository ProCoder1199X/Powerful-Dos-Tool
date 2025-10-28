# 🚀 EWLT MEGA v5.0
## Ethical Web Load Tester - Complete Unified Edition

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-5.0.0--MEGA-red.svg)]()
[![Security](https://img.shields.io/badge/security-maximum-green.svg)]()

**The ultimate unified load testing suite with military-grade security, maximum anonymity, and production-ready features.**

---

## ⚠️ CRITICAL LEGAL NOTICE

**THIS TOOL IS FOR AUTHORIZED TESTING ONLY**

Unauthorized access to computer systems is **ILLEGAL** and punishable by:
- Up to 10 years imprisonment
- Fines up to $250,000
- Civil liability

**BY USING THIS SOFTWARE, YOU ACCEPT FULL LEGAL RESPONSIBILITY**

---

## 🎯 What is EWLT MEGA?

EWLT MEGA is the complete, unified, production-ready version that combines all the best features from previous iterations into one powerful tool:

### ✨ Core Features

**🔒 Maximum Security**
- Validated proxy management with health checks
- Safe Tor controller with verification
- Complete TLS fingerprint randomization (anti-JA3/JA4)
- DNS over HTTPS to prevent leaks
- Chaotic timing models (anti-correlation)
- Dynamic decoy traffic generation

**🎭 Advanced Anonymity**
- Multi-layer proxy chaining
- Tor circuit rotation
- MAC address spoofing (separate tool)
- Encrypted volatile memory logging
- Emergency self-destruct mechanism

**📊 Real-Time Dashboard**
- Live performance metrics
- Beautiful web interface
- Auto-opens in browser
- Real-time statistics

**💪 Production Ready**
- Proper error handling
- Graceful degradation
- Automatic fallbacks
- Clean shutdown
- JSON report generation

---

## 🚀 Quick Start (60 seconds)

### 1. Install (Auto-installs dependencies)
```bash
# Clone repository
git clone https://github.com/yourusername/ethical-web-load-tester.git
cd ethical-web-load-tester

# Ready to use!
python ewlt_mega.py --help
```

### 2. Your First Test
```bash
# Basic test
python ewlt_mega.py \
  --target-url http://localhost:8080 \
  --users 50 \
  --duration 60
```

### 3. With Dashboard
```bash
python ewlt_mega.py \
  --target-url http://localhost:8080 \
  --users 50 \
  --duration 120 \
  --dashboard
```

### 4. Maximum Anonymity
```bash
python ewlt_mega.py \
  --target-url https://yoursite.com \
  --users 100 \
  --use-tor \
  --identity-rotation 60 \
  --dashboard \
  --save-report
```

---

## 📖 Complete Documentation

### Command-Line Options

**Required:**
```
--target-url URL          Target URL to test
```

**Load Testing:**
```
--users N                 Concurrent users (1-2000, default: 50)
--spawn-rate N            Users/second spawn rate (default: 5)
--duration N              Test duration in seconds (default: 60)
```

**Anonymity:**
```
--use-tor                 Route through Tor network
--identity-rotation N     Rotate Tor identity every N seconds
```

**Dashboard:**
```
--dashboard               Enable real-time dashboard
--dashboard-port N        Dashboard port (default: 8089)
--headless                Don't auto-open browser
```

**Output:**
```
--save-report             Save JSON report after test
--dry-run                 Validate config without traffic
--verbose, -v             Enable verbose logging
```

---

## 🎓 Usage Examples

### Example 1: Basic Load Test
```bash
python ewlt_mega.py \
  --target-url http://localhost:8080 \
  --users 100 \
  --spawn-rate 10 \
  --duration 300 \
  --dashboard \
  --save-report
```

**What it does:**
- Tests local development server
- 100 concurrent users
- 5-minute test
- Real-time dashboard
- Saves JSON report

---

### Example 2: Production Stress Test
```bash
python ewlt_mega.py \
  --target-url https://yoursite.com \
  --users 500 \
  --spawn-rate 25 \
  --duration 600 \
  --dashboard \
  --save-report
```

**What it does:**
- Tests production site
- 500 concurrent users
- 10-minute sustained load
- Monitor via dashboard
- Generate performance report

---

### Example 3: Anonymous Security Test
```bash
python ewlt_mega.py \
  --target-url https://yoursite.com \
  --users 100 \
  --spawn-rate 5 \
  --duration 1800 \
  --use-tor \
  --identity-rotation 120 \
  --dashboard \
  --save-report
```

**What it does:**
- Routes through Tor network
- Changes identity every 2 minutes
- 30-minute test
- Maximum anonymity
- Complete reporting

---

### Example 4: Dry Run (Config Check)
```bash
python ewlt_mega.py \
  --target-url https://yoursite.com \
  --users 100 \
  --use-tor \
  --dry-run
```

**What it does:**
- Validates all configuration
- Tests Tor connectivity
- Verifies DNS settings
- NO traffic sent
- Safe to run anytime

---

## 🛡️ Security Features Explained

### 1. Validated Proxy Management
**Problem:** Dead proxies can leak your real IP  
**Solution:** Health checks every 5 minutes, automatic fallbacks

### 2. Safe Tor Controller
**Problem:** Tor might not be routing traffic  
**Solution:** Verifies actual Tor connection before testing

### 3. TLS Fingerprint Randomization
**Problem:** JA3/JA4 fingerprinting identifies you  
**Solution:** Randomizes cipher suites, mimics Chrome/Firefox

### 4. DNS Over HTTPS
**Problem:** DNS queries leak to ISP  
**Solution:** DoH through Cloudflare/Google/Quad9

### 5. Chaotic Timing Model
**Problem:** Timing patterns reveal automation  
**Solution:** ML-inspired random delays (Poisson, exponential, human-like)

### 6. Dynamic Decoy Traffic
**Problem:** Traffic analysis reveals real target  
**Solution:** Random requests to 200+ decoy sites

### 7. Volatile Memory Logging
**Problem:** Logs on disk can be recovered  
**Solution:** Encrypted in-memory logs, wiped on exit

### 8. Emergency Self-Destruct
**Problem:** Unexpected termination leaves traces  
**Solution:** Signal handlers (Ctrl+C) trigger cleanup

---
## License 
- MIT License.
