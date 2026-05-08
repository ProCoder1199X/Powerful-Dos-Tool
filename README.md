# Powerful DoS Tool

A comprehensive load testing and distributed denial of service simulation platform designed for authorized security testing and infrastructure assessment.

---

## Legal Notice

THIS TOOL IS FOR AUTHORIZED TESTING ONLY

Unauthorized access to computer systems is illegal and punishable by:
- Up to 10 years imprisonment
- Fines up to $250,000
- Civil liability

BY USING THIS SOFTWARE, YOU ACCEPT FULL LEGAL RESPONSIBILITY

---

## Features

**Core Capabilities**
- Multi-threaded concurrent user simulation
- Configurable request patterns and payloads
- Real-time performance metrics and statistics
- Target URL validation and testing
- Customizable request headers and parameters
- Request rate control and throttling

**Network Features**
- Proxy chain support with validation
- Tor integration with circuit rotation
- Anonymity through multi-layer request routing
- DNS resolution management
- HTTPS/SSL support with certificate verification
- TCP and UDP protocol support

**Monitoring and Reporting**
- Live web-based dashboard
- Real-time request/response tracking
- Performance statistics generation
- JSON report export
- Latency and throughput analysis
- Error rate monitoring

**Advanced Options**
- Custom request scheduling
- Identity rotation capabilities
- Timing randomization
- Automatic fallback mechanisms
- Graceful shutdown with cleanup
- Dry-run validation mode

---

## Quick Start

### Installation
```bash
git clone https://github.com/ProCoder1199X/ethical-web-load-tester.git
cd ethical-web-load-tester
python web_load_tester.py --help
```

### Basic Usage
```bash
python web_load_tester.py \
  --target-url http://localhost:8080 \
  --users 50 \
  --duration 60
```

### With Dashboard
```bash
python web_load_tester.py \
  --target-url http://localhost:8080 \
  --users 50 \
  --duration 120 \
  --dashboard
```

### Advanced Testing
```bash
python web_load_tester.py \
  --target-url https://example.com \
  --users 100 \
  --use-tor \
  --identity-rotation 60 \
  --dashboard \
  --save-report
```

---

## Command-Line Options

**Required Arguments:**
- `--target-url URL` - Target URL to test

**Load Configuration:**
- `--users N` - Number of concurrent users (1-2000, default: 50)
- `--spawn-rate N` - Users spawned per second (default: 5)
- `--duration N` - Test duration in seconds (default: 60)

**Network Options:**
- `--use-tor` - Route requests through Tor network
- `--identity-rotation N` - Rotate identity every N seconds
- `--proxy-list FILE` - Use proxy list from file

**Output Options:**
- `--dashboard` - Enable real-time dashboard
- `--dashboard-port N` - Dashboard port (default: 8089)
- `--save-report` - Save test report as JSON
- `--verbose` - Verbose logging output
- `--dry-run` - Validate configuration without sending traffic

---

## Download

For security reasons, this tool has been removed from github (On april 8, 2026) .  
However for educational purposes, you can access this, but not for free.  Email me : **dheeraj1018279@gmail.com**

Bitcoin Wallet Address: 1A1z7agoat8Bt8ShJvzjCosePC98xxxx

Contribution Amount: $100

---

## License

MIT License
