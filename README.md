# EWLT - Extreme Web Load Tester




### ⚠️ AUTHORIZED TESTING ONLY - EXTREMLY POWERFUL ⚠️
---
#### EWLT is a highly secure, anonymized web load testing tool designed for ethical, authorized penetration testing and performance evaluation. It integrates advanced anonymity features like proxy chaining, Tor integration, TLS fingerprint randomization, decoy traffic, and secure data wiping to prevent traceability. Misuse may violate laws—use responsibly and only with explicit permission from system owners.
---
## Overview
EWLT builds on Locust for distributed load testing while adding layers of privacy and anti-detection:

- Anonymity: Proxy validation, Tor circuits, and TLS randomization.
- Anti-Correlation: Chaotic timing models mimicking human behavior.
- Obfuscation: Dynamic decoy traffic to mask real requests.
- Security: Memory-only encrypted logging and DoD-standard wiping.
- No Leaks: DNS over HTTPS/TLS and mandatory self-destruct on exit.

Ideal for testing web apps under load without exposing your IP or patterns. ***Not for DDoS or unauthorized access.***
## Features

- Proxy Management: Validates SOCKS5/HTTP/Tor proxies with health checks and chaining.
- Tor Integration: Safe controller for identity rotation and circuit verification.
- TLS Fingerprinting: Randomizes handshakes to mimic Chrome/Firefox.
- Decoy Traffic: Injects realistic fake requests (e.g., searches on Google, Reddit).
- Secure DNS: DoH/DoT to prevent leaks (Cloudflare, Google, Quad9).
- Timing Models: Poisson/exponential delays with human-like patterns.
- Logging: Volatile, encrypted memory logs (no disk writes).
- Self-Destruct: Wipes memory/files on exit (SIGINT/SIGTERM).
- Locust Compatible: Extends HttpUser for easy scaling.
## Installation


- Prerequisites:

   - Python 3.8+.
   - Tor running locally (default: SOCKS 9050, Control 9051).
  - Optional: Free proxy lists (e.g., from ProxyScrape).
- Clone the Repo
- Start Tor (if not running):

        - Linux/macOS: tor (via brew/apt).
        - Windows: Run tor.exe from Tor Browser.
        - Verify: curl --socks5-hostname 127.0.0.1:9050 https://check.torproject.org/.

### Configuration
- Edit main file or use env vars/flags.

    

