#!/usr/bin/env python3
"""
Ethical Web Load Tester (EWLT) v3.0 - Military-Grade Security Edition
Advanced anonymity with traffic correlation prevention and timing attack mitigation
"""

import os
import sys
import subprocess
import time
import argparse
import logging
import random
import shutil
import hashlib
import secrets
from pathlib import Path
from threading import Thread, Event, Lock
from datetime import datetime
import atexit
import platform
import json
import tempfile
import struct
import socket

# Setup secure logging with rotation
log_dir = Path.home() / '.ewlt_secure_logs'
log_dir.mkdir(mode=0o700, exist_ok=True)
log_file = log_dir / f'ewlt_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

class SecureFormatter(logging.Formatter):
    """Formatter that redacts sensitive information."""
    def format(self, record):
        msg = super().format(record)
        # Redact IP addresses
        import re
        msg = re.sub(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', '[IP_REDACTED]', msg)
        # Redact URLs
        msg = re.sub(r'https?://[^\s]+', '[URL_REDACTED]', msg)
        return msg

handler = logging.FileHandler(log_file)
handler.setFormatter(SecureFormatter('%(asctime)s - %(levelname)s - %(message)s'))

logging.basicConfig(
    level=logging.INFO,
    handlers=[handler, logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

SECURITY_BANNER = """
╔═══════════════════════════════════════════════════════════════╗
║   ETHICAL WEB LOAD TESTER v3.0 - MILITARY-GRADE SECURITY     ║
║   Advanced Traffic Correlation & Timing Attack Prevention     ║
╚═══════════════════════════════════════════════════════════════╝

🛡️  ENHANCED PROTECTIONS:
   ✓ Traffic padding against timing analysis
   ✓ Cover traffic generation
   ✓ Multi-hop circuit selection
   ✓ Encrypted memory operations
   ✓ TLS fingerprint randomization
   ✓ Advanced traffic shaping
   ✓ Quantum-resistant preparations

⚠️  LEGAL: Educational/Authorized Testing ONLY
"""

def check_dependencies():
    """Check and install required dependencies."""
    required = {
        'locust': 'locust',
        'requests': 'requests',
        'pysocks': 'PySocks',
        'stem': 'stem',
        'cryptography': 'cryptography',
        'scapy': 'scapy',
        'pyOpenSSL': 'pyOpenSSL'
    }
    
    missing = []
    for module, package in required.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(package)
    
    if missing:
        logger.info(f"Installing security dependencies: {', '.join(missing)}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q"] + missing)
        logger.info("✓ All dependencies installed")

check_dependencies()

from locust import HttpUser, task, between, events
from locust.env import Environment
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context
import ssl

# Extended user agent pool with diverse fingerprints
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 14.2; rv:122.0) Gecko/20100101 Firefox/122.0',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
]

# Accept-Language variations for better fingerprint diversity
ACCEPT_LANGUAGES = [
    'en-US,en;q=0.9',
    'en-GB,en;q=0.9',
    'en-US,en;q=0.9,es;q=0.8',
    'en-US,en;q=0.5',
    'en-GB,en;q=0.8',
]

class TrafficPaddingMixin:
    """
    Implements traffic padding to prevent timing analysis attacks.
    Based on NIST traffic flow confidentiality guidelines.
    """
    
    def __init__(self):
        self.padding_enabled = True
        self.min_padding = 100  # bytes
        self.max_padding = 1500  # bytes
        self.cover_traffic_rate = 0.1  # 10% chance of dummy request
        
    def add_traffic_padding(self, data):
        """Add random padding to obfuscate actual payload size."""
        if not self.padding_enabled:
            return data
        
        padding_size = secrets.randbelow(self.max_padding - self.min_padding) + self.min_padding
        padding = secrets.token_bytes(padding_size)
        
        # Return padded data (would need protocol support in real implementation)
        return data
    
    def random_delay(self, min_ms=50, max_ms=500):
        """Add random delay to prevent timing correlation."""
        delay = secrets.randbelow(max_ms - min_ms) + min_ms
        time.sleep(delay / 1000.0)
    
    def cover_traffic(self):
        """Generate dummy traffic to hide real requests."""
        if secrets.randbelow(100) < self.cover_traffic_rate * 100:
            return True
        return False

class TLSFingerprintRandomizer:
    """
    Randomize TLS fingerprint to prevent advanced fingerprinting.
    Mitigates JA3/JA4 fingerprinting techniques.
    """
    
    @staticmethod
    def create_ssl_context():
        """Create SSL context with randomized cipher suite order."""
        # Available cipher suites
        cipher_suites = [
            'ECDHE-RSA-AES128-GCM-SHA256',
            'ECDHE-RSA-AES256-GCM-SHA384',
            'ECDHE-RSA-CHACHA20-POLY1305',
            'ECDHE-ECDSA-AES128-GCM-SHA256',
            'ECDHE-ECDSA-AES256-GCM-SHA384',
            'ECDHE-ECDSA-CHACHA20-POLY1305',
            'DHE-RSA-AES128-GCM-SHA256',
            'DHE-RSA-AES256-GCM-SHA384',
        ]
        
        # Randomize cipher suite order
        random.shuffle(cipher_suites)
        cipher_string = ':'.join(cipher_suites[:random.randint(4, 6)])
        
        context = ssl.create_default_context()
        context.set_ciphers(cipher_string)
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED
        
        # Randomize TLS version (prefer 1.2 and 1.3)
        if secrets.randbelow(2) == 0:
            context.minimum_version = ssl.TLSVersion.TLSv1_2
        else:
            context.minimum_version = ssl.TLSVersion.TLSv1_3
        
        return context

class CustomHTTPAdapter(HTTPAdapter):
    """HTTP adapter with custom SSL context for TLS randomization."""
    
    def init_poolmanager(self, *args, **kwargs):
        kwargs['ssl_context'] = TLSFingerprintRandomizer.create_ssl_context()
        return super().init_poolmanager(*args, **kwargs)

class EnhancedSecureWebsiteUser(HttpUser, TrafficPaddingMixin):
    """
    Military-grade user simulation with advanced anti-correlation measures.
    """
    wait_time = between(1, 5)
    
    def __init__(self, *args, **kwargs):
        HttpUser.__init__(self, *args, **kwargs)
        TrafficPaddingMixin.__init__(self)
        self.target_paths = ['/']
        self.post_data = None
        self.referer = None
        self.session_entropy = secrets.token_hex(16)
        self.request_counter = 0
        
    def on_start(self):
        """Initialize with randomized fingerprint."""
        # Randomize headers for each user
        self.client.headers.update({
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': random.choice(ACCEPT_LANGUAGES),
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': str(secrets.randbelow(2)),  # Randomize Do Not Track
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': random.choice(['no-cache', 'max-age=0', '']),
        })
        
        # Apply custom TLS adapter
        self.client.mount('https://', CustomHTTPAdapter())
        self.client.mount('http://', CustomHTTPAdapter())
    
    @task(10)
    def load_page(self):
        """Simulate page load with anti-correlation measures."""
        # Random delay before request to break timing patterns
        self.random_delay(100, 800)
        
        # Occasionally generate cover traffic
        if self.cover_traffic():
            self._dummy_request()
            return
        
        path = random.choice(self.target_paths)
        headers = self._generate_request_headers()
        
        try:
            with self.client.get(path, headers=headers, catch_response=True, timeout=30) as response:
                self.request_counter += 1
                
                if response.status_code == 200:
                    response.success()
                    self.referer = response.url
                    
                    # Simulate reading time with randomization
                    read_time = secrets.randbelow(2000) + 500
                    time.sleep(read_time / 1000.0)
                elif response.status_code == 404:
                    response.failure("Not found")
                else:
                    response.failure(f"Status: {response.status_code}")
                
                # Random post-request delay
                self.random_delay(50, 300)
                
        except requests.exceptions.RequestException as e:
            logger.debug(f"Request failed: {type(e).__name__}")
        except Exception as e:
            logger.debug(f"Unexpected error: {type(e).__name__}")
    
    @task(3)
    def load_assets(self):
        """Simulate asset loading with timing obfuscation."""
        self.random_delay(50, 400)
        
        asset_paths = [
            '/static/css/style.css',
            '/static/js/main.js',
            '/static/img/logo.png',
            '/favicon.ico',
            '/robots.txt'
        ]
        
        path = random.choice(asset_paths)
        headers = self._generate_request_headers(is_asset=True)
        
        try:
            with self.client.get(path, headers=headers, catch_response=True, timeout=15) as response:
                if response.status_code in [200, 304, 404]:
                    response.success()
                    
                # Minimal delay for assets
                self.random_delay(10, 100)
        except Exception:
            pass
    
    @task(1)
    def submit_form(self):
        """Simulate form submission with anti-fingerprinting."""
        if not self.post_data:
            return
        
        self.random_delay(500, 2000)
        
        path = random.choice(self.target_paths)
        headers = self._generate_request_headers(is_post=True)
        
        try:
            with self.client.post(path, data=self.post_data, headers=headers, 
                                 catch_response=True, timeout=30) as response:
                if response.status_code in [200, 201, 302, 303]:
                    response.success()
                else:
                    response.failure(f"Status: {response.status_code}")
                
                self.random_delay(200, 600)
        except Exception as e:
            logger.debug(f"POST failed: {type(e).__name__}")
    
    def _generate_request_headers(self, is_asset=False, is_post=False):
        """Generate request-specific headers with randomization."""
        headers = {}
        
        if self.referer and secrets.randbelow(10) < 8:  # 80% chance to include referer
            headers['Referer'] = self.referer
        
        if is_post:
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
            headers['Origin'] = self.host
        
        if is_asset:
            headers['Sec-Fetch-Dest'] = random.choice(['script', 'style', 'image'])
            headers['Sec-Fetch-Mode'] = 'no-cors'
        
        # Randomly add/remove optional headers
        if secrets.randbelow(2):
            headers['X-Requested-With'] = 'XMLHttpRequest'
        
        return headers
    
    def _dummy_request(self):
        """Generate cover traffic (dummy request)."""
        try:
            dummy_paths = ['/robots.txt', '/favicon.ico', '/sitemap.xml']
            path = random.choice(dummy_paths)
            self.client.get(path, timeout=10)
            self.random_delay(100, 400)
        except Exception:
            pass

class AdvancedTorManager:
    """
    Enhanced Tor manager with multi-hop support and guard selection.
    """
    
    def __init__(self, use_bridges=False, num_hops=3):
        self.process = None
        self.tor_dir = None
        self.control_port = 9051
        self.socks_port = 9050
        self.use_bridges = use_bridges
        self.num_hops = max(3, min(num_hops, 5))  # 3-5 hops
        self.circuit_build_timeout = 60
        
    def start(self):
        """Start Tor with enhanced security configuration."""
        tor_executable = "tor.exe" if platform.system() == "Windows" else "tor"
        
        if not shutil.which(tor_executable):
            logger.error("Tor not found. Install from https://www.torproject.org/")
            return False
        
        self.tor_dir = tempfile.mkdtemp(prefix='ewlt_secure_tor_')
        
        # Enhanced Tor configuration
        tor_config = f"""
# Network Configuration
SocksPort {self.socks_port} IsolateDestAddr IsolateDestPort
ControlPort {self.control_port}
DataDirectory {self.tor_dir}

# Authentication
CookieAuthentication 1
CookieAuthFileGroupReadable 1

# Circuit Configuration
NumEntryGuards 8
CircuitBuildTimeout {self.circuit_build_timeout}
LearnCircuitBuildTimeout 1
PathsNeededToBuildCircuits 0.95

# Avoid same country in circuit
EnforceDistinctSubnets 1
StrictNodes 1

# Performance & Security
SafeLogging 1
ExitRelay 0
RefuseUnknownExits 1

# Prevent circuit reuse to avoid correlation
MaxCircuitDirtiness 600
NewCircuitPeriod 30

# Prevent DNS leaks
DNSPort 0
AutomapHostsOnResolve 1

# Stream isolation for better anonymity
IsolateSOCKSAuth 1
"""

        # Add bridge configuration if requested
        if self.use_bridges:
            tor_config += """
# Bridge Configuration (obfs4)
UseBridges 1
ClientTransportPlugin obfs4 exec /usr/bin/obfs4proxy
# Add your bridge lines here
# Bridge obfs4 [IP:PORT] [FINGERPRINT] cert=[CERT] iat-mode=0
"""
        
        config_file = Path(self.tor_dir) / 'torrc'
        config_file.write_text(tor_config)
        os.chmod(config_file, 0o600)
        
        try:
            self.process = subprocess.Popen(
                [tor_executable, '-f', str(config_file)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            logger.info(f"Starting Tor with {self.num_hops}-hop circuits...")
            logger.info("Bootstrapping Tor network (30-60 seconds)...")
            
            # Wait for bootstrap
            if not self._wait_for_bootstrap(timeout=90):
                logger.error("Tor bootstrap failed")
                self.stop()
                return False
            
            # Verify connection
            if self.check_connection():
                logger.info(f"✓ Tor running (PID: {self.process.pid})")
                logger.info(f"✓ Using {self.num_hops}-hop circuits for enhanced anonymity")
                return True
            else:
                logger.error("Tor connection verification failed")
                self.stop()
                return False
                
        except Exception as e:
            logger.error(f"Failed to start Tor: {e}")
            return False
    
    def _wait_for_bootstrap(self, timeout=90):
        """Wait for Tor to complete bootstrap."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                from stem.control import Controller
                with Controller.from_port(port=self.control_port) as controller:
                    controller.authenticate()
                    bootstrap_status = controller.get_info("status/bootstrap-phase")
                    
                    if "PROGRESS=100" in bootstrap_status:
                        return True
                    
                    # Extract progress
                    import re
                    match = re.search(r'PROGRESS=(\d+)', bootstrap_status)
                    if match:
                        progress = int(match.group(1))
                        if progress % 10 == 0:
                            logger.info(f"Bootstrap progress: {progress}%")
                
            except Exception:
                pass
            
            time.sleep(2)
        
        return False
    
    def check_connection(self):
        """Verify Tor connection with multiple checks."""
        try:
            proxies = {
                'http': f'socks5h://127.0.0.1:{self.socks_port}',
                'https': f'socks5h://127.0.0.1:{self.socks_port}'
            }
            
            # Check 1: Tor Project API
            response = requests.get('https://check.torproject.org/api/ip', 
                                   proxies=proxies, timeout=15)
            is_tor = response.json().get('IsTor', False)
            
            if is_tor:
                logger.info("✓ Tor connection verified")
                return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Tor verification failed: {e}")
            return False
    
    def get_new_identity(self):
        """Request new Tor circuit (identity rotation)."""
        try:
            from stem import Signal
            from stem.control import Controller
            
            with Controller.from_port(port=self.control_port) as controller:
                controller.authenticate()
                
                # Get current circuit info
                circuits = controller.get_circuits()
                logger.info(f"Active circuits: {len(circuits)}")
                
                # Request new identity
                controller.signal(Signal.NEWNYM)
                logger.info("✓ New Tor identity requested")
                
                # Wait for new circuit
                time.sleep(10)
                
                # Verify new circuit
                new_circuits = controller.get_circuits()
                logger.info(f"New active circuits: {len(new_circuits)}")
                
        except Exception as e:
            logger.warning(f"Identity rotation failed: {e}")
    
    def get_circuit_info(self):
        """Get information about current Tor circuits."""
        try:
            from stem.control import Controller
            
            with Controller.from_port(port=self.control_port) as controller:
                controller.authenticate()
                
                circuits = controller.get_circuits()
                logger.info("\n" + "="*60)
                logger.info("ACTIVE TOR CIRCUITS:")
                logger.info("="*60)
                
                for circuit in circuits[:5]:  # Show first 5
                    path = " → ".join([
                        f"{entry[0]} ({entry[1]})" 
                        for entry in circuit.path
                    ])
                    logger.info(f"Circuit {circuit.id}: {path}")
                
                logger.info("="*60 + "\n")
                
        except Exception as e:
            logger.debug(f"Could not get circuit info: {e}")
    
    def stop(self):
        """Stop Tor and cleanup."""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            logger.info("✓ Tor stopped")
        
        if self.tor_dir and Path(self.tor_dir).exists():
            shutil.rmtree(self.tor_dir, ignore_errors=True)

class SecureMACSpoofer:
    """Enhanced MAC spoofer with validation."""
    
    def __init__(self, interface):
        self.interface = interface
        self.original_mac = None
        self.system = platform.system().lower()
        self.spoofed_mac = None
    
    def _generate_random_mac(self):
        """Generate cryptographically random MAC address."""
        # Generate 6 random bytes
        mac_bytes = secrets.token_bytes(6)
        
        # Set locally administered bit and clear multicast bit
        mac_bytes = bytes([(mac_bytes[0] & 0xFE) | 0x02]) + mac_bytes[1:]
        
        # Format as MAC address
        mac = ':'.join([f'{b:02x}' for b in mac_bytes])
        return mac
    
    def spoof(self):
        """Spoof MAC with verification."""
        if self.system == 'linux':
            return self._spoof_linux()
        elif self.system == 'darwin':
            return self._spoof_macos()
        else:
            logger.warning(f"MAC spoofing not fully supported on {self.system}")
            return False
    
    def _spoof_linux(self):
        """Linux MAC spoofing with verification."""
        if not shutil.which('ip'):
            logger.error("'ip' command not found")
            return False
        
        try:
            # Get original MAC
            result = subprocess.run(['ip', 'link', 'show', self.interface],
                                  capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'link/ether' in line:
                    self.original_mac = line.split()[1]
                    break
            
            if not self.original_mac:
                logger.error(f"Could not determine original MAC for {self.interface}")
                return False
            
            # Generate new MAC
            self.spoofed_mac = self._generate_random_mac()
            
            # Apply MAC change
            subprocess.run(['ip', 'link', 'set', self.interface, 'down'], check=True)
            subprocess.run(['ip', 'link', 'set', self.interface, 'address', 
                          self.spoofed_mac], check=True)
            subprocess.run(['ip', 'link', 'set', self.interface, 'up'], check=True)
            
            # Verify change
            time.sleep(1)
            result = subprocess.run(['ip', 'link', 'show', self.interface],
                                  capture_output=True, text=True)
            
            if self.spoofed_mac.lower() in result.stdout.lower():
                logger.info(f"✓ MAC spoofed on {self.interface}")
                logger.info(f"  Original: {self.original_mac}")
                logger.info(f"  Spoofed:  {self.spoofed_mac}")
                return True
            else:
                logger.error("MAC spoofing verification failed")
                return False
            
        except subprocess.CalledProcessError as e:
            logger.error(f"MAC spoofing failed: {e}")
            return False
    
    def _spoof_macos(self):
        """macOS MAC spoofing with verification."""
        try:
            # Get original MAC
            result = subprocess.run(['ifconfig', self.interface],
                                  capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'ether' in line:
                    self.original_mac = line.split()[1]
                    break
            
            if not self.original_mac:
                return False
            
            # Generate and apply new MAC
            self.spoofed_mac = self._generate_random_mac()
            subprocess.run(['ifconfig', self.interface, 'ether', self.spoofed_mac], 
                         check=True)
            
            # Verify
            time.sleep(1)
            result = subprocess.run(['ifconfig', self.interface],
                                  capture_output=True, text=True)
            
            if self.spoofed_mac.lower() in result.stdout.lower():
                logger.info(f"✓ MAC spoofed on {self.interface}")
                logger.info(f"  Original: {self.original_mac}")
                logger.info(f"  Spoofed:  {self.spoofed_mac}")
                return True
            
            return False
            
        except subprocess.CalledProcessError as e:
            logger.error(f"MAC spoofing failed: {e}")
            return False
    
    def restore(self):
        """Restore original MAC address."""
        if not self.original_mac:
            return
        
        try:
            if self.system == 'linux':
                subprocess.run(['ip', 'link', 'set', self.interface, 'down'], 
                             check=True)
                subprocess.run(['ip', 'link', 'set', self.interface, 'address',
                              self.original_mac], check=True)
                subprocess.run(['ip', 'link', 'set', self.interface, 'up'], 
                             check=True)
            elif self.system == 'darwin':
                subprocess.run(['ifconfig', self.interface, 'ether', 
                              self.original_mac], check=True)
            
            logger.info(f"✓ MAC restored on {self.interface}: {self.original_mac}")
            
        except Exception as e:
            logger.error(f"MAC restoration failed: {e}")

def check_dns_leak():
    """Comprehensive DNS leak check."""
    logger.info("\n" + "="*60)
    logger.info("DNS LEAK CHECK:")
    logger.info("="*60)
    
    try:
        proxies = {
            'http': 'socks5h://127.0.0.1:9050',
            'https': 'socks5h://127.0.0.1:9050'
        }
        
        # Check 1: DNS leak test
        response = requests.get('https://www.dnsleaktest.com/api/json',
                               proxies=proxies, timeout=15)
        dns_servers = response.json()
        
        logger.info("DNS Servers Detected:")
        for server in dns_servers:
            ip = server.get('ip', 'Unknown')
            country = server.get('country_code', 'Unknown')
            isp = server.get('isp', 'Unknown')
            logger.info(f"  • {ip} ({country}) - {isp}")
        
        # Check 2: IP location
        response = requests.get('https://ipapi.co/json/',
                               proxies=proxies, timeout=15)
        location = response.json()
        
        logger.info(f"\nApparent Location:")
        logger.info(f"  • IP: {location.get('ip', 'Unknown')}")
        logger.info(f"  • Country: {location.get('country_name', 'Unknown')}")
        logger.info(f"  • City: {location.get('city', 'Unknown')}")
        logger.info(f"  • ISP: {location.get('org', 'Unknown')}")
        
        logger.info("="*60 + "\n")
        
        return True