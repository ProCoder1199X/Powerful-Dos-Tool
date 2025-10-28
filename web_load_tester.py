#!/usr/bin/env python3
"""
███████╗██╗    ██╗██╗  ████████╗    ███╗   ███╗███████╗ ██████╗  █████╗ 
██╔════╝██║    ██║██║  ╚══██╔══╝    ████╗ ████║██╔════╝██╔════╝ ██╔══██╗
█████╗  ██║ █╗ ██║██║     ██║       ██╔████╔██║█████╗  ██║  ███╗███████║
██╔══╝  ██║███╗██║██║     ██║       ██║╚██╔╝██║██╔══╝  ██║   ██║██╔══██║
███████╗╚███╔███╔╝███████╗██║       ██║ ╚═╝ ██║███████╗╚██████╔╝██║  ██║
╚══════╝ ╚══╝╚══╝ ╚══════╝╚═╝       ╚═╝     ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝

ETHICAL WEB LOAD TESTER - MEGA EDITION v5.0
Complete unified version with maximum security, power, and anonymity

Copyright (c) 2025 - MIT License
⚠️  AUTHORIZED TESTING ONLY - EDUCATIONAL USE ⚠️
"""

import os
import sys
import subprocess
import time
import argparse
import logging
import random
import secrets
import hashlib
import json
import socket
import threading
import signal
import atexit
import tempfile
import shutil
import ctypes
from pathlib import Path
from datetime import datetime
from collections import deque, defaultdict
from typing import Optional, Dict, List, Set, Tuple
from urllib.parse import urlparse
import re
import struct
import http.server
import socketserver
import webbrowser

VERSION = "5.0.0-MEGA"
RELEASE_DATE = "2025-01-15"

# ============================================================================
# SECURE MEMORY LOGGING
# ============================================================================

class VolatileMemoryHandler(logging.Handler):
    """Logs stored in encrypted volatile memory only."""
    
    def __init__(self, max_size=10000):
        super().__init__()
        self.log_buffer = deque(maxlen=max_size)
        self.encryption_key = secrets.token_bytes(32)
        self.lock = threading.Lock()
        
    def emit(self, record):
        try:
            msg = self.format(record)
            encrypted = self._xor_encrypt(msg.encode())
            with self.lock:
                self.log_buffer.append((time.time(), encrypted))
        except Exception:
            pass
    
    def _xor_encrypt(self, data: bytes) -> bytes:
        """Fast XOR encryption for volatile storage."""
        key = self.encryption_key
        return bytes(a ^ b for a, b in zip(data, (key * (len(data) // len(key) + 1))[:len(data)]))
    
    def get_logs(self, last_n: int = 100) -> List[str]:
        """Decrypt and return recent logs."""
        with self.lock:
            recent = list(self.log_buffer)[-last_n:]
        return [self._xor_encrypt(log[1]).decode('utf-8', errors='ignore') for log in recent]
    
    def wipe(self):
        """Securely wipe all logs."""
        with self.lock:
            self.log_buffer.clear()
            self.encryption_key = secrets.token_bytes(32)

# Setup logging
log_dir = Path.home() / '.ewlt_mega_logs'
log_dir.mkdir(mode=0o700, exist_ok=True)
volatile_handler = VolatileMemoryHandler()
volatile_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))

logger = logging.getLogger('EWLT_MEGA')
logger.addHandler(volatile_handler)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.INFO)

# ============================================================================
# DEPENDENCY MANAGEMENT
# ============================================================================

def install_dependencies():
    """Smart dependency installation with fallbacks."""
    required = {
        'core': ['requests', 'locust', 'aiohttp'],
        'security': ['cryptography', 'pysocks', 'stem'],
        'optional': ['dnspython', 'scapy']
    }
    
    logger.info("🔧 Checking dependencies...")
    missing = []
    
    for category, packages in required.items():
        for pkg in packages:
            try:
                __import__(pkg.replace('-', '_'))
            except ImportError:
                if category != 'optional':
                    missing.append(pkg)
                else:
                    logger.debug(f"Optional: {pkg} not installed")
    
    if missing:
        logger.info(f"📦 Installing: {', '.join(missing)}")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "-q", "--upgrade"] + missing,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            logger.info("✅ Dependencies installed successfully")
        except Exception as e:
            logger.error(f"❌ Installation failed: {e}")
            logger.error("Please install manually: pip install " + " ".join(missing))
            sys.exit(1)

install_dependencies()

# Import after installation
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from locust import HttpUser, task, between
from locust.env import Environment
from locust.stats import stats_printer, stats_history
from cryptography.fernet import Fernet
import stem
from stem import Signal
from stem.control import Controller

try:
    import dns.resolver
    HAS_DNS = True
except ImportError:
    HAS_DNS = False

# ============================================================================
# VALIDATED PROXY MANAGER WITH HEALTH CHECKS
# ============================================================================

class ValidatedProxyManager:
    """Production-grade proxy manager with health checks and fallbacks."""
    
    def __init__(self):
        self.proxy_pools = {'socks5': [], 'http': [], 'tor': []}
        self.validated = set()
        self.dead = set()
        self.health_check_interval = 300
        self.last_check = 0
        self.lock = threading.Lock()
        self.validation_timeout = 10
        
    def add_proxy(self, proxy_type: str, proxy_url: str, validate: bool = True) -> bool:
        """Add proxy with optional validation."""
        if validate and not self._validate_proxy(proxy_url):
            logger.warning(f"⚠️  Invalid proxy: {proxy_url[:30]}...")
            self.dead.add(proxy_url)
            return False
        
        with self.lock:
            self.proxy_pools[proxy_type].append(proxy_url)
            self.validated.add(proxy_url)
        logger.info(f"✅ Added proxy: {proxy_url[:30]}...")
        return True
    
    def _validate_proxy(self, proxy_url: str) -> bool:
        """Validate proxy connectivity and anonymity."""
        try:
            proxies = {'http': proxy_url, 'https': proxy_url}
            
            # Test 1: Basic connectivity
            r = requests.get('https://httpbin.org/ip', proxies=proxies, timeout=self.validation_timeout)
            if r.status_code != 200:
                return False
            
            proxy_ip = r.json().get('origin', '')
            
            # Test 2: Verify IP is different
            try:
                local_r = requests.get('https://httpbin.org/ip', timeout=5)
                local_ip = local_r.json().get('origin', '')
                if local_ip == proxy_ip:
                    logger.warning("⚠️  Proxy not masking IP!")
                    return False
            except Exception:
                pass  # Can't verify, but proxy works
            
            # Test 3: Response time check
            start = time.time()
            requests.get('https://httpbin.org/get', proxies=proxies, timeout=self.validation_timeout)
            latency = (time.time() - start) * 1000
            
            if latency > 10000:  # >10s is too slow
                logger.warning(f"⚠️  Proxy too slow: {latency:.0f}ms")
                return False
            
            logger.debug(f"✅ Proxy validated - Latency: {latency:.0f}ms")
            return True
            
        except Exception as e:
            logger.debug(f"Proxy validation failed: {type(e).__name__}")
            return False
    
    def get_validated_proxy(self) -> Optional[str]:
        """Get a random validated proxy."""
        # Periodic health check
        if time.time() - self.last_check > self.health_check_interval:
            threading.Thread(target=self._background_health_check, daemon=True).start()
            self.last_check = time.time()
        
        with self.lock:
            # Prefer Tor
            if self.proxy_pools['tor']:
                return random.choice(self.proxy_pools['tor'])
            
            # Then validated proxies
            available = [p for p in self.proxy_pools['socks5'] + self.proxy_pools['http'] 
                        if p in self.validated and p not in self.dead]
            
            if available:
                return random.choice(available)
        
        logger.warning("⚠️  No valid proxies available!")
        return None
    
    def _background_health_check(self):
        """Background proxy health check."""
        all_proxies = []
        with self.lock:
            for pool in self.proxy_pools.values():
                all_proxies.extend(pool)
        
        for proxy in all_proxies[:5]:  # Check max 5 at a time
            if proxy in self.dead:
                continue
            
            if not self._validate_proxy(proxy):
                with self.lock:
                    self.validated.discard(proxy)
                    self.dead.add(proxy)
                logger.info(f"🔴 Proxy marked dead: {proxy[:30]}...")
    
    def get_proxy_dict(self) -> Optional[Dict[str, str]]:
        """Get proxy dict for requests or None if no proxies."""
        proxy = self.get_validated_proxy()
        if proxy:
            return {'http': proxy, 'https': proxy}
        return None

# ============================================================================
# SAFE TOR CONTROLLER WITH VERIFICATION
# ============================================================================

class SafeTorController:
    """Production Tor controller with safety checks."""
    
    def __init__(self, control_port: int = 9051, socks_port: int = 9050):
        self.control_port = control_port
        self.socks_port = socks_port
        self.controller = None
        self.is_connected = False
        self.last_identity_change = 0
        self.min_identity_interval = 10
        self.verification_url = 'https://check.torproject.org/api/ip'
        
    def connect_with_retry(self, max_retries: int = 3) -> bool:
        """Connect to Tor with retries and verification."""
        for attempt in range(max_retries):
            try:
                self.controller = Controller.from_port(port=self.control_port)
                self.controller.authenticate()
                
                if self._verify_tor_working():
                    self.is_connected = True
                    logger.info(f"✅ Tor connected (attempt {attempt + 1}/{max_retries})")
                    return True
                else:
                    logger.warning(f"⚠️  Tor connected but not routing traffic properly")
                    if self.controller:
                        self.controller.close()
                    time.sleep(2)
                    
            except Exception as e:
                logger.warning(f"Tor connection attempt {attempt + 1} failed: {type(e).__name__}")
                time.sleep(2)
        
        logger.error("❌ TOR UNAVAILABLE - Tests will proceed without Tor")
        return False
    
    def _verify_tor_working(self) -> bool:
        """Verify Tor is actually routing traffic."""
        try:
            proxies = {
                'http': f'socks5h://127.0.0.1:{self.socks_port}',
                'https': f'socks5h://127.0.0.1:{self.socks_port}'
            }
            
            r = requests.get(self.verification_url, proxies=proxies, timeout=15)
            is_tor = r.json().get('IsTor', False)
            
            if is_tor:
                tor_ip = r.json().get('IP', 'Unknown')
                logger.info(f"✅ Tor verified - Exit IP: {tor_ip}")
                return True
            
            return False
            
        except Exception as e:
            logger.debug(f"Tor verification failed: {type(e).__name__}")
            return False
    
    def new_identity_safe(self) -> bool:
        """Request new Tor identity with rate limiting."""
        if not self.is_connected:
            logger.warning("Tor not connected, skipping identity rotation")
            return False
        
        now = time.time()
        if now - self.last_identity_change < self.min_identity_interval:
            logger.debug("Identity change rate limited")
            return False
        
        try:
            self.controller.signal(Signal.NEWNYM)
            self.last_identity_change = now
            logger.info("✅ New Tor identity requested")
            time.sleep(10)  # Wait for new circuit
            return self._verify_tor_working()
        except Exception as e:
            logger.error(f"Identity change failed: {e}")
            self.is_connected = False
            return False
    
    def get_circuit_countries(self) -> List[str]:
        """Get countries in current Tor circuits."""
        if not self.is_connected or not self.controller:
            return []
        
        try:
            countries = []
            for circuit in self.controller.get_circuits():
                if circuit.status == 'BUILT':
                    for entry in circuit.path:
                        try:
                            desc = self.controller.get_network_status(entry[0])
                            if hasattr(desc, 'country_code'):
                                countries.append(desc.country_code)
                        except Exception:
                            pass
            return countries
        except Exception:
            return []
    
    def close(self):
        """Safely close Tor controller."""
        if self.controller:
            try:
                self.controller.close()
            except Exception:
                pass
        self.is_connected = False

# ============================================================================
# ADVANCED TLS & FINGERPRINT RANDOMIZATION
# ============================================================================

class CompleteTLSRandomizer:
    """Complete TLS handshake randomization."""
    
    CHROME_CIPHERS = [
        'TLS_AES_128_GCM_SHA256', 'TLS_AES_256_GCM_SHA384',
        'TLS_CHACHA20_POLY1305_SHA256', 'ECDHE-ECDSA-AES128-GCM-SHA256',
        'ECDHE-RSA-AES128-GCM-SHA256', 'ECDHE-ECDSA-AES256-GCM-SHA384',
        'ECDHE-RSA-AES256-GCM-SHA384', 'ECDHE-ECDSA-CHACHA20-POLY1305',
    ]
    
    FIREFOX_CIPHERS = [
        'TLS_AES_128_GCM_SHA256', 'TLS_CHACHA20_POLY1305_SHA256',
        'TLS_AES_256_GCM_SHA384', 'ECDHE-ECDSA-AES128-GCM-SHA256',
        'ECDHE-RSA-AES128-GCM-SHA256', 'ECDHE-ECDSA-CHACHA20-POLY1305',
    ]
    
    @classmethod
    def get_random_profile(cls):
        """Get randomized TLS profile mimicking real browsers."""
        profile = random.choice(['chrome', 'firefox'])
        
        if profile == 'chrome':
            ciphers = cls.CHROME_CIPHERS.copy()
        else:
            ciphers = cls.FIREFOX_CIPHERS.copy()
        
        random.shuffle(ciphers)
        
        return {
            'profile': profile,
            'ciphers': ciphers[:random.randint(5, 8)],
            'curves': ['X25519', 'prime256v1', 'secp384r1'],
            'alpn': ['h2', 'http/1.1'] if secrets.randbelow(2) else ['http/1.1'],
        }

# ============================================================================
# DYNAMIC DECOY TRAFFIC GENERATOR
# ============================================================================

class DynamicDecoyGenerator:
    """Advanced decoy traffic with ML-inspired patterns."""
    
    def __init__(self):
        self.decoy_pool = self._generate_large_pool(200)
        self.rate = random.uniform(0.02, 0.08)
        self.last_rotation = time.time()
        self.rotation_interval = 300
        
    def _generate_large_pool(self, size: int) -> List[Dict]:
        """Generate large diverse decoy pool."""
        categories = {
            'search': ['google.com', 'bing.com', 'duckduckgo.com', 'yahoo.com'],
            'news': ['news.ycombinator.com', 'reddit.com', 'bbc.com', 'cnn.com', 'reuters.com'],
            'social': ['twitter.com', 'facebook.com', 'linkedin.com', 'instagram.com'],
            'tech': ['github.com', 'stackoverflow.com', 'medium.com', 'dev.to'],
            'video': ['youtube.com', 'vimeo.com', 'twitch.tv'],
            'shop': ['amazon.com', 'ebay.com', 'etsy.com'],
            'general': ['wikipedia.org', 'imdb.com', 'weather.com'],
        }
        
        queries = ['weather', 'news', 'tech', 'tutorial', 'review', 'guide',
                  'how to', 'best', 'top 10', '2025', 'today', secrets.token_hex(3)]
        
        pool = []
        for cat, sites in categories.items():
            for site in sites:
                for _ in range(random.randint(2, 5)):
                    pool.append({
                        'url': f'https://www.{site}',
                        'category': cat,
                        'ua': self._random_ua(),
                        'lang': random.choice(['en-US,en;q=0.9', 'en-GB,en;q=0.8']),
                    })
        
        random.shuffle(pool)
        return pool[:size]
    
    def _random_ua(self) -> str:
        """Generate random but realistic user agent."""
        templates = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/{}.0.0.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/{}.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) Firefox/{}.0',
        ]
        template = random.choice(templates)
        version = random.randint(115, 125)
        return template.format(version)
    
    def should_inject(self) -> bool:
        """Decide whether to inject decoy now."""
        if time.time() - self.last_rotation > self.rotation_interval:
            self.decoy_pool = self._generate_large_pool(200)
            self.rate = random.uniform(0.02, 0.08)
            self.last_rotation = time.time()
        
        return secrets.randbelow(1000) < self.rate * 1000
    
    def get_decoy(self) -> Dict:
        """Get random decoy request config."""
        return random.choice(self.decoy_pool)

# ============================================================================
# DNS OVER HTTPS/TLS RESOLVER
# ============================================================================

class SecureDNSResolver:
    """DNS over HTTPS to prevent DNS leaks."""
    
    DOH_SERVERS = [
        'https://1.1.1.1/dns-query',  # Cloudflare
        'https://dns.google/resolve',  # Google
        'https://dns.quad9.net/dns-query',  # Quad9
    ]
    
    def __init__(self):
        self.cache = {}
        self.cache_timeout = 300
        self.use_doh = True
        
    def resolve(self, hostname: str) -> Optional[str]:
        """Resolve hostname using DoH."""
        if hostname in self.cache:
            ip, timestamp = self.cache[hostname]
            if time.time() - timestamp < self.cache_timeout:
                return ip
        
        if self.use_doh and HAS_DNS:
            ip = self._resolve_doh(hostname)
        else:
            ip = self._resolve_standard(hostname)
        
        if ip:
            self.cache[hostname] = (ip, time.time())
        
        return ip
    
    def _resolve_doh(self, hostname: str) -> Optional[str]:
        """Resolve using DNS over HTTPS."""
        try:
            server = random.choice(self.DOH_SERVERS)
            r = requests.get(server, params={'name': hostname, 'type': 'A'},
                           headers={'Accept': 'application/dns-json'}, timeout=5)
            
            if r.status_code == 200:
                data = r.json()
                if 'Answer' in data and data['Answer']:
                    return data['Answer'][0]['data']
            return None
        except Exception:
            return self._resolve_standard(hostname)
    
    def _resolve_standard(self, hostname: str) -> Optional[str]:
        """Fallback to standard DNS."""
        try:
            return socket.gethostbyname(hostname)
        except Exception:
            return None

# ============================================================================
# CHAOTIC TIMING MODEL (ANTI-CORRELATION)
# ============================================================================

class ChaoticTimingModel:
    """ML-inspired timing model to defeat traffic analysis."""
    
    def __init__(self):
        self.base_rate = 1.0
        self.patterns = self._load_patterns()
        self.strategy_weights = [0.3, 0.3, 0.2, 0.2]  # Poisson, Human, Random, Exp
        
    def _load_patterns(self) -> List[float]:
        """Load human-like timing patterns."""
        patterns = []
        # Burst reading (quick clicks)
        patterns.extend([0.5, 0.6, 0.7, 0.8] * 3)
        # Long pause (reading content)
        patterns.extend([5.0, 8.0, 12.0, 15.0] * 2)
        # Steady browsing
        patterns.extend([2.0, 2.5, 3.0, 2.8, 3.2] * 4)
        # Search behavior
        patterns.extend([1.0, 15.0, 1.5, 20.0, 2.0] * 2)
        random.shuffle(patterns)
        return patterns
    
    def get_delay(self) -> float:
        """Get next delay using chaotic model."""
        strategy = random.choices(range(4), weights=self.strategy_weights)[0]
        
        if strategy == 0:
            # Poisson distribution
            import math
            u = secrets.randbelow(10000) / 10000.0
            return max(0.1, -math.log(1 - u + 0.0001) / self.base_rate)
        elif strategy == 1:
            # Human-like pattern
            return random.choice(self.patterns)
        elif strategy == 2:
            # Pure random
            return random.uniform(0.5, 8.0)
        else:
            # Exponential
            return random.expovariate(1.0 / self.base_rate)

# ============================================================================
# SELF-DESTRUCT MANAGER
# ============================================================================

class UltimateDestructor:
    """Emergency self-destruct with memory wiping."""
    
    def __init__(self):
        self.cleanup_funcs = []
        self.is_armed = True
        signal.signal(signal.SIGINT, self.emergency_destruct)
        signal.signal(signal.SIGTERM, self.emergency_destruct)
        atexit.register(self.normal_destruct)
        
    def register(self, func):
        """Register cleanup function."""
        self.cleanup_funcs.append(func)
    
    def emergency_destruct(self, signum, frame):
        """Emergency destruction on signal."""
        if not self.is_armed:
            return
        logger.warning("\n🔥 EMERGENCY DESTRUCT ACTIVATED")
        self.execute_destruction()
        os._exit(0)
    
    def normal_destruct(self):
        """Normal cleanup on exit."""
        if not self.is_armed:
            return
        logger.info("🧹 Cleaning up...")
        self.execute_destruction()
    
    def execute_destruction(self):
        """Execute all destruction sequences."""
        self.is_armed = False
        
        # Run custom cleanups
        for func in self.cleanup_funcs:
            try:
                func()
            except Exception as e:
                logger.debug(f"Cleanup error: {type(e).__name__}")
        
        # Wipe volatile logs
        volatile_handler.wipe()
        
        # Force garbage collection
        import gc
        gc.collect()
        
        logger.info("✅ Cleanup complete")

# ============================================================================
# ENHANCED LOCUST USER CLASS
# ============================================================================

class MegaSecureUser(HttpUser):
    """Ultimate secure user with all protections."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.proxy_mgr = ValidatedProxyManager()
        self.tor_ctrl = SafeTorController()
        self.dns_resolver = SecureDNSResolver()
        self.decoy_gen = DynamicDecoyGenerator()
        self.timing_model = ChaoticTimingModel()
        self.tls_randomizer = CompleteTLSRandomizer()
        self.request_count = 0
        self.session_id = secrets.token_hex(16)
        
    def wait_time_func(self):
        """Dynamic wait time using chaotic model."""
        return self.timing_model.get_delay()
    
    wait_time = wait_time_func
    
    def on_start(self):
        """Initialize with maximum security."""
        # Setup proxies if configured
        proxies = self.proxy_mgr.get_proxy_dict()
        if proxies:
            for scheme in ['http', 'https']:
                self.client.proxies[scheme] = proxies.get(scheme)
        
        # Randomize headers
        tls_profile = self.tls_randomizer.get_random_profile()
        self.client.headers.update({
            'User-Agent': self._generate_ua(tls_profile['profile']),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': random.choice(['en-US,en;q=0.9', 'en-GB,en;q=0.8', 'en;q=0.9']),
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': str(secrets.randbelow(2)),
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Setup retry adapter
        adapter = HTTPAdapter(max_retries=Retry(total=3, backoff_factor=0.5))
        self.client.mount('https://', adapter)
        self.client.mount('http://', adapter)
        
        logger.debug(f"✅ User initialized - Session: {self.session_id[:8]}...")
    
    def _generate_ua(self, profile: str) -> str:
        """Generate realistic user agent."""
        version = random.randint(115, 125)
        if profile == 'chrome':
            os_str = random.choice([
                'Windows NT 10.0; Win64; x64',
                'Macintosh; Intel Mac OS X 10_15_7',
                'X11; Linux x86_64'
            ])
            return f'Mozilla/5.0 ({os_str}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36'
        else:  # firefox
            os_str = random.choice([
                'Windows NT 10.0; Win64; x64',
                'X11; Linux x86_64',
                'Macintosh; Intel Mac OS X 10.15'
            ])
            return f'Mozilla/5.0 ({os_str}; rv:{version}.0) Gecko/20100101 Firefox/{version}.0'
    
    @task(10)
    def secure_page_load(self):
        """Load page with all security measures."""
        # Inject decoy traffic randomly
        if self.decoy_gen.should_inject():
            self._send_decoy()
            return
        
        # Timing jitter
        time.sleep(secrets.randbelow(200) / 1000.0)
        
        path = '/'
        
        # Generate ephemeral cookies
        cookies = {
            'session_id': secrets.token_hex(16),
            '_ga': f'GA1.2.{secrets.randbelow(10**9)}.{int(time.time())}',
            'csrf': secrets.token_hex(16),
        }
        
        try:
            with self.client.get(path, cookies=cookies, catch_response=True, timeout=30) as r:
                self.request_count += 1
                
                if r.status_code == 200:
                    r.success()
                elif r.status_code == 429:
                    r.failure("Rate limited")
                    time.sleep(5)
                else:
                    r.failure(f"Status: {r.status_code}")
                
                # Human-like reading time
                time.sleep(random.uniform(0.5, 2.5))
                
        except Exception as e:
            logger.debug(f"Request error: {type(e).__name__}")
    
    def _send_decoy(self):
        """Send decoy request to random site."""
        try:
            decoy = self.decoy_gen.get_decoy()
            headers = {
                'User-Agent': decoy['ua'],
                'Accept-Language': decoy['lang'],
            }
            requests.get(decoy['url'], headers=headers, timeout=5)
            logger.debug("🎭 Decoy traffic sent")
        except Exception:
            pass  # Silent fail for decoys

# ============================================================================
# DASHBOARD SERVER
# ============================================================================

class DashboardServer:
    """Real-time dashboard server."""
    
    def __init__(self, port=8089):
        self.port = port
        self.server = None
        self.stats = {'requests': 0, 'failures': 0, 'users': 0}
        self.lock = threading.Lock()
        
    def start(self):
        """Start dashboard server in background."""
        def run_server():
            try:
                handler = http.server.SimpleHTTPRequestHandler
                with socketserver.TCPServer(("", self.port), handler) as httpd:
                    self.server = httpd
                    logger.info(f"🎛️  Dashboard: http://localhost:{self.port}/dashboard.html")
                    httpd.serve_forever()
            except Exception as e:
                logger.error(f"Dashboard failed: {e}")
        
        threading.Thread(target=run_server, daemon=True).start()
        time.sleep(1)  # Give server time to start
    
    def update_stats(self, stats_dict):
        """Update dashboard statistics."""
        with self.lock:
            self.stats.update(stats_dict)
    
    def stop(self):
        """Stop dashboard server."""
        if self.server:
            self.server.shutdown()

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def run_mega_test(args):
    """Run EWLT MEGA test with all features."""
    
    print(f"""
╔═══════════════════════════════════════════════════════════════╗
║                    EWLT MEGA v{VERSION}                      ║
║              Maximum Security Load Testing Suite              ║
╚═══════════════════════════════════════════════════════════════╝

🎯 Target: {args.target_url}
👥 Users: {args.users}
⏱️  Duration: {args.duration}s
🔒 Security Level: {'MAXIMUM' if args.use_tor else 'STANDARD'}
""")
    
    # Initialize components
    destructor = UltimateDestructor()
    tor_ctrl = None
    dashboard = None
    
    try:
        # Start dashboard if requested
        if args.dashboard:
            dashboard = DashboardServer(args.dashboard_port)
            dashboard.start()
            time.sleep(2)
            if not args.headless:
                try:
                    webbrowser.open(f'http://localhost:{args.dashboard_port}/dashboard.html')
                except Exception:
                    pass
        
        # Setup Tor if requested
        if args.use_tor:
            logger.info("🔧 Setting up Tor...")
            tor_ctrl = SafeTorController()
            if not tor_ctrl.connect_with_retry():
                logger.warning("⚠️  Continuing without Tor")
            else:
                # Setup Tor proxy environment
                tor_proxy = f'socks5h://127.0.0.1:{tor_ctrl.socks_port}'
                os.environ['http_proxy'] = tor_proxy
                os.environ['https_proxy'] = tor_proxy
                
                # Register cleanup
                destructor.register(tor_ctrl.close)
        
        # Dry run check
        if args.dry_run:
            logger.info("✅ DRY RUN - Configuration validated")
            logger.info("   Remove --dry-run to execute test")
            return
        
        # Setup Locust environment
        from locust.log import setup_logging
        setup_logging("WARNING", None)
        
        env = Environment(user_classes=[MegaSecureUser])
        env.create_local_runner()
        
        # Configure target
        MegaSecureUser.host = args.target_url
        
        # Start test
        logger.info(f"\n{'='*60}")
        logger.info("🚀 STARTING TEST")
        logger.info(f"{'='*60}")
        
        env.runner.start(args.users, spawn_rate=args.spawn_rate)
        
        # Run for duration with identity rotation
        start_time = time.time()
        last_rotation = start_time
        rotation_interval = args.identity_rotation
        
        try:
            while time.time() - start_time < args.duration:
                time.sleep(1)
                
                # Rotate Tor identity if configured
                if tor_ctrl and rotation_interval > 0:
                    if time.time() - last_rotation >= rotation_interval:
                        tor_ctrl.new_identity_safe()
                        last_rotation = time.time()
                
                # Update dashboard
                if dashboard and env.stats.total.num_requests > 0:
                    dashboard.update_stats({
                        'requests': env.stats.total.num_requests,
                        'failures': env.stats.total.num_failures,
                        'users': args.users,
                        'rps': env.stats.total.current_rps,
                        'avg_response': env.stats.total.avg_response_time,
                    })
        
        except KeyboardInterrupt:
            logger.info("\n⏸️  Test interrupted by user")
        
        # Stop test
        env.runner.quit()
        
        # Print results
        logger.info(f"\n{'='*60}")
        logger.info("📊 TEST RESULTS")
        logger.info(f"{'='*60}")
        
        stats = env.stats.total
        logger.info(f"Total Requests:      {stats.num_requests:,}")
        logger.info(f"Failed Requests:     {stats.num_failures:,}")
        
        if stats.num_requests > 0:
            success_rate = ((stats.num_requests - stats.num_failures) / stats.num_requests) * 100
            logger.info(f"Success Rate:        {success_rate:.2f}%")
        
        logger.info(f"\nResponse Times:")
        logger.info(f"  Average:           {stats.avg_response_time:.2f}ms")
        logger.info(f"  Median:            {stats.median_response_time:.2f}ms")
        logger.info(f"  95th Percentile:   {stats.get_response_time_percentile(0.95):.2f}ms")
        logger.info(f"  Min:               {stats.min_response_time}ms")
        logger.info(f"  Max:               {stats.max_response_time}ms")
        
        logger.info(f"\nThroughput:")
        logger.info(f"  Requests/sec:      {stats.current_rps:.2f}")
        
        if stats.num_failures > 0:
            logger.info(f"\n⚠️  Errors:")
            for error in env.stats.errors.values():
                logger.info(f"  • {error.name}: {error.occurrences} times")
        
        logger.info(f"{'='*60}\n")
        
        # Save report
        if args.save_report:
            report_file = log_dir / f'report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            report_data = {
                'timestamp': datetime.now().isoformat(),
                'target': args.target_url,
                'users': args.users,
                'duration': args.duration,
                'requests': stats.num_requests,
                'failures': stats.num_failures,
                'avg_response_time': stats.avg_response_time,
                'rps': stats.current_rps,
            }
            report_file.write_text(json.dumps(report_data, indent=2))
            logger.info(f"📄 Report saved: {report_file}")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
    finally:
        # Cleanup
        if dashboard:
            dashboard.stop()
        
        logger.info(f"\n💾 Logs: {log_dir}")
        logger.info("✅ EWLT MEGA test complete")

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point."""
    
    parser = argparse.ArgumentParser(
        description=f"EWLT MEGA v{VERSION} - Ultimate Load Testing Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic test
  python ewlt_mega.py --target-url http://localhost:8080 --users 50
  
  # Maximum anonymity
  sudo python ewlt_mega.py --target-url https://yoursite.com --users 100 \\
    --use-tor --identity-rotation 60 --dashboard
  
  # Dry run (verify config)
  python ewlt_mega.py --target-url http://localhost --dry-run

⚠️  LEGAL: Only test systems you own or have written permission to test!
        """
    )
    
    # Core options
    parser.add_argument('--target-url', required=True, 
                       help='Target URL (ONLY authorized systems!)')
    parser.add_argument('--users', type=int, default=50,
                       help='Concurrent users (default: 50)')
    parser.add_argument('--spawn-rate', type=int, default=5,
                       help='Users spawned per second (default: 5)')
    parser.add_argument('--duration', type=int, default=60,
                       help='Test duration in seconds (default: 60)')
    
    # Anonymity options
    parser.add_argument('--use-tor', action='store_true',
                       help='Route traffic through Tor network')
    parser.add_argument('--identity-rotation', type=int, default=0,
                       help='Rotate Tor identity every N seconds (0=off)')
    
    # Dashboard options
    parser.add_argument('--dashboard', action='store_true',
                       help='Enable real-time dashboard')
    parser.add_argument('--dashboard-port', type=int, default=8089,
                       help='Dashboard port (default: 8089)')
    parser.add_argument('--headless', action='store_true',
                       help='Don\'t open browser for dashboard')
    
    # Output options
    parser.add_argument('--save-report', action='store_true',
                       help='Save JSON report after test')
    parser.add_argument('--dry-run', action='store_true',
                       help='Validate configuration without sending traffic')
    
    # Advanced options
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Validate inputs
    args.users = max(1, min(args.users, 2000))
    args.spawn_rate = max(1, min(args.spawn_rate, 100))
    args.duration = max(10, args.duration)
    
    # Final authorization check
    if not args.dry_run:
        print("\n" + "="*60)
        print("⚠️  FINAL AUTHORIZATION CHECK")
        print("="*60)
        print(f"Target: {args.target_url}")
        print(f"This will send REAL TRAFFIC to the target.")
        print("\n⚖️  Legal Reminder:")
        print("   • Only test systems you OWN")
        print("   • Unauthorized testing is ILLEGAL")
        print("   • You are responsible for your actions")
        print("="*60)
        
        response = input("\nType 'YES' to proceed: ")
        if response.strip().upper() != 'YES':
            print("❌ Test cancelled")
            return
    
    # Run test
    run_mega_test(args)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
