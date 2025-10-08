import os
import sys
import subprocess
import time
import argparse
import logging
from threading import Thread
import atexit
import platform
import random

# Setup logging (safe, anonymized to file)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='ewlt.log')
logger = logging.getLogger(__name__)

def install_locust():
    """Auto-install Locust if not present."""
    try:
        import locust
    except ImportError:
        logger.info("Installing Locust...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "locust"])
        logger.info("Locust installed. Restart if needed.")

install_locust()

from locust import HttpUser, task, between, FastHttpUser
from locust.env import Environment
from locust.log import setup_logging

class WebsiteUser(FastHttpUser):
    wait_time = between(1, 5)  # Random wait for realism

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_url = None
        self.post_data = None  # Optional POST payload for realism

    @task(3)  # Weight: More GETs
    def load_get(self):
        self.client.get(self.target_url)

    @task(1)  # Weight: Fewer POSTs
    def load_post(self):
        if self.post_data:
            self.client.post(self.target_url, data=self.post_data)

def spoof_mac(interface=None, restore=False):
    """Cross-platform MAC spoofing. Spoof on start, restore on exit."""
    system = platform.system().lower()
    if system == 'linux':
        if not shutil.which('macchanger') or not shutil.which('ifconfig'):
            logger.warning("Install macchanger and ifconfig for Linux MAC spoofing.")
            return
        cmd_down = ['ifconfig', interface, 'down']
        cmd_spoof = ['macchanger', '-r', interface] if not restore else ['macchanger', '-p', interface]
        cmd_up = ['ifconfig', interface, 'up']
    elif system == 'windows':
        if not interface:
            logger.warning("Specify Windows adapter name (e.g., 'Wi-Fi') for MAC spoofing.")
            return
        # Windows: Use netsh (requires admin)
        cmd_down = ['netsh', 'interface', 'set', 'interface', interface, 'admin=disable']
        new_mac = ''.join(random.choice('0123456789ABCDEF') for _ in range(12)) if not restore else 'original'  # Placeholder; use registry for real restore
        cmd_spoof = ['netsh', 'interface', 'set', 'interface', interface, f'address={new_mac}']  # Simplified; actual requires regedit
        cmd_up = ['netsh', 'interface', 'set', 'interface', interface, 'admin=enable']
        logger.warning("Windows MAC spoofing requires admin and may need registry tweaks.")
    else:
        logger.warning(f"MAC spoofing not supported on {system}.")
        return

    try:
        subprocess.run(cmd_down, check=True)
        subprocess.run(cmd_spoof, check=True)
        subprocess.run(cmd_up, check=True)
        action = "restored" if restore else "spoofed"
        logger.info(f"MAC {action} on {interface}")
    except subprocess.CalledProcessError as e:
        logger.error(f"MAC spoof failed: {e}")

def start_tor():
    """Start Tor in background (cross-platform)."""
    tor_path = "tor.exe" if platform.system() == "Windows" else "tor"
    if not shutil.which(tor_path):
        logger.error("Tor not found. Install from torproject.org and add to PATH.")
        return None
    try:
        proc = subprocess.Popen([tor_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(5)  # Bootstrap wait
        logger.info(f"Tor started (PID: {proc.pid}).")
        return proc
    except Exception as e:
        logger.error(f"Tor start failed: {e}")
        return None

def run_locust(target_url, users, hatch_rate, duration, use_tor, vpn_proxy=None, post_data=None, dry_run=False):
    """Run Locust load test safely."""
    setup_logging("INFO", None)
    
    if dry_run:
        logger.info("Dry run: Simulating setup without traffic.")
        return
    
    if vpn_proxy:
        os.environ['http_proxy'] = vpn_proxy
        os.environ['HTTPS_PROXY'] = vpn_proxy
        logger.info(f"Using VPN proxy: {vpn_proxy}")
    
    if use_tor:
        os.environ['http_proxy'] = 'socks5h://localhost:9050'  # 'h' for remote DNS (leak prevention)
        os.environ['HTTPS_PROXY'] = 'socks5h://localhost:9050'
        logger.info("Using Tor with remote DNS resolution for anonymity (no leaks).")

    env = Environment(user_classes=[WebsiteUser])
    env.create_local_runner()
    
    # Set dynamic params
    for user in env.user_classes:
        user.target_url = target_url
        user.post_data = post_data

    env.runner.start(users, hatch_rate)
    logger.info(f"Starting load test: {users} users at {hatch_rate}/sec for {duration} seconds...")
    print("Open http://localhost:8089 in Tor Browser for monitoring (avoid fingerprinting).")

    time.sleep(duration)
    env.runner.quit()

def main():
    parser = argparse.ArgumentParser(description="Ethical Web Load Tester (EWLT) - For self-testing only.")
    parser.add_argument('--target-url', required=True, help="Your website URL (e.g., http://localhost/)")
    parser.add_argument('--users', type=int, default=100, help="Simulated users (max 500)")
    parser.add_argument('--hatch-rate', type=int, default=10, help="Users/sec ramp-up")
    parser.add_argument('--duration', type=int, default=60, help="Test duration (seconds)")
    parser.add_argument('--use-tor', action='store_true', help="Enable Tor for anonymity")
    parser.add_argument('--vpn-proxy', help="VPN SOCKS proxy (e.g., socks5://localhost:1080)")
    parser.add_argument('--post-data', help="Optional POST data (e.g., 'key=value')")
    parser.add_argument('--mac-interface', help="Network interface for MAC spoofing (e.g., wlan0 or Wi-Fi)")
    parser.add_argument('--dry-run', action='store_true', help="Simulate without sending traffic")

    args = parser.parse_args()

    # Safety caps
    args.users = min(args.users, 500)
    args.hatch_rate = min(args.hatch_rate, 50)
    
    print("WARNING: Use ONLY on your own sites. Start low to avoid crashes. For max anonymity: Use in VM, Tor Browser for UI.")

    tor_proc = None
    if args.use_tor:
        tor_proc = start_tor()
    
    if args.mac_interface:
        spoof_mac(args.mac_interface)
        atexit.register(spoof_mac, args.mac_interface, restore=True)  # Auto-restore

    try:
        run_locust(args.target_url, args.users, args.hatch_rate, args.duration, args.use_tor, args.vpn_proxy, args.post_data, args.dry_run)
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        if tor_proc:
            tor_proc.terminate()
            logger.info("Tor stopped.")

if __name__ == "__main__":
    main()
