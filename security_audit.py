#!/usr/bin/env python3
"""
EWLT Security Audit Tool
Comprehensive security check before running load tests
"""

import os
import sys
import subprocess
import platform
import socket
import json
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}")
    print(f"{text}")
    print(f"{'='*60}{Colors.END}\n")

def check_pass(msg):
    print(f"{Colors.GREEN}✓{Colors.END} {msg}")

def check_warn(msg):
    print(f"{Colors.YELLOW}⚠{Colors.END} {msg}")

def check_fail(msg):
    print(f"{Colors.RED}✗{Colors.END} {msg}")

def check_info(msg):
    print(f"{Colors.BLUE}ℹ{Colors.END} {msg}")

class SecurityAudit:
    def __init__(self):
        self.system = platform.system()
        self.issues = []
        self.warnings = []
        self.passes = []
    
    def run_full_audit(self):
        """Run complete security audit."""
        print_header("EWLT SECURITY AUDIT")
        
        self.check_system_info()
        self.check_privileges()
        self.check_tor()
        self.check_network()
        self.check_firewall()
        self.check_dns()
        self.check_time_sync()
        self.check_entropy()
        self.check_memory_security()
        self.check_python_packages()
        self.check_network_interfaces()
        
        self.print_summary()
    
    def check_system_info(self):
        """Display system information."""
        print_header("SYSTEM INFORMATION")
        
        check_info(f"Operating System: {platform.system()} {platform.release()}")
        check_info(f"Architecture: {platform.machine()}")
        check_info(f"Python Version: {platform.python_version()}")
        check_info(f"Hostname: {socket.gethostname()}")
    
    def check_privileges(self):
        """Check if running with appropriate privileges."""
        print_header("PRIVILEGE CHECK")
        
        if self.system != 'Windows':
            if os.geteuid() == 0:
                check_pass("Running as root (required for MAC spoofing)")
                self.passes.append("Root privileges")
            else:
                check_warn("Not running as root (MAC spoofing will not work)")
                check_info("Run with: sudo python web_load_tester.py")
                self.warnings.append("No root privileges")
        else:
            check_info("Windows detected - privilege check skipped")
    
    def check_tor(self):
        """Check Tor installation and status."""
        print_header("TOR CHECK")
        
        # Check if Tor is installed
        tor_cmd = "tor.exe" if self.system == "Windows" else "tor"
        
        if subprocess.run(["which" if self.system != "Windows" else "where", tor_cmd],
                         capture_output=True).returncode == 0:
            check_pass(f"Tor is installed")
            self.passes.append("Tor installed")
            
            # Check Tor version
            try:
                result = subprocess.run([tor_cmd, "--version"],
                                      capture_output=True, text=True)
                version = result.stdout.split('\n')[0]
                check_info(f"Version: {version}")
            except Exception:
                pass
            
            # Check if Tor is running
            if self.system == "Linux":
                result = subprocess.run(["systemctl", "is-active", "tor"],
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    check_pass("Tor service is active")
                    self.passes.append("Tor running")
                else:
                    check_warn("Tor service is not running")
                    check_info("Start with: sudo systemctl start tor")
                    self.warnings.append("Tor not running")
            
            # Check Tor ports
            self.check_port("Tor SOCKS", 9050)
            self.check_port("Tor Control", 9051)
            
        else:
            check_fail("Tor is NOT installed")
            check_info("Install: sudo apt install tor (Ubuntu/Debian)")
            check_info("         brew install tor (macOS)")
            self.issues.append("Tor not installed")
    
    def check_port(self, name, port):
        """Check if a port is listening."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        
        if result == 0:
            check_pass(f"{name} port {port} is listening")
            return True
        else:
            check_warn(f"{name} port {port} is NOT listening")
            return False
    
    def check_network(self):
        """Check network configuration."""
        print_header("NETWORK CHECK")
        
        # Check internet connectivity
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            check_pass("Internet connectivity OK")
            self.passes.append("Internet connected")
        except OSError:
            check_fail("No internet connectivity")
            self.issues.append("No internet")
        
        # Check if VPN is active (basic check)
        try:
            result = subprocess.run(["ip", "link" if self.system == "Linux" else "ifconfig"],
                                  capture_output=True, text=True)
            if "tun" in result.stdout or "tap" in result.stdout:
                check_info("VPN interface detected (tun/tap)")
            else:
                check_info("No VPN interface detected")
        except Exception:
            pass
    
    def check_firewall(self):
        """Check firewall status."""
        print_header("FIREWALL CHECK")
        
        if self.system == "Linux":
            # Check ufw
            try:
                result = subprocess.run(["ufw", "status"],
                                      capture_output=True, text=True)
                if "Status: active" in result.stdout:
                    check_pass("UFW firewall is active")
                    self.passes.append("Firewall active")
                    
                    # Check if Tor ports are allowed
                    if "9050" in result.stdout:
                        check_pass("Tor SOCKS port (9050) is allowed")
                    else:
                        check_warn("Tor SOCKS port (9050) may be blocked")
                        check_info("Allow with: sudo ufw allow 9050/tcp")
                else:
                    check_warn("UFW firewall is inactive")
                    self.warnings.append("Firewall inactive")
            except FileNotFoundError:
                # Try iptables
                try:
                    result = subprocess.run(["iptables", "-L"],
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        check_info("iptables firewall detected")
                    else:
                        check_warn("No firewall detected")
                        self.warnings.append("No firewall")
                except Exception:
                    check_warn("Could not determine firewall status")
        
        elif self.system == "Darwin":
            try:
                result = subprocess.run(["pfctl", "-s", "info"],
                                      capture_output=True, text=True)
                if "Enabled" in result.stdout:
                    check_pass("macOS firewall (pf) is enabled")
                    self.passes.append("Firewall active")
                else:
                    check_warn("macOS firewall may be disabled")
            except Exception:
                check_info("Could not check macOS firewall status")
    
    def check_dns(self):
        """Check DNS configuration."""
        print_header("DNS CHECK")
        
        try:
            if self.system == "Linux":
                with open('/etc/resolv.conf', 'r') as f:
                    content = f.read()
                    
                check_info("Current DNS servers:")
                for line in content.split('\n'):
                    if line.startswith('nameserver'):
                        dns = line.split()[1]
                        check_info(f"  • {dns}")
                        
                        # Check for common DNS servers
                        if dns in ['8.8.8.8', '8.8.4.4']:
                            check_warn("Using Google DNS (potential privacy concern)")
                        elif dns in ['1.1.1.1', '1.0.0.1']:
                            check_info("Using Cloudflare DNS (good privacy)")
                        elif dns.startswith('127.0'):
                            check_pass("Using local DNS resolver")
        except Exception:
            check_warn("Could not read DNS configuration")
    
    def check_time_sync(self):
        """Check time synchronization."""
        print_header("TIME SYNCHRONIZATION CHECK")
        
        try:
            import ntplib
            client = ntplib.NTPClient()
            response = client.request('pool.ntp.org', version=3, timeout=5)
            
            offset = abs(response.offset)
            if offset < 1.0:
                check_pass(f"Time is synchronized (offset: {offset:.3f}s)")
                self.passes.append("Time synchronized")
            else:
                check_warn(f"Time offset is {offset:.3f}s (should be < 1s)")
                self.warnings.append(f"Time offset: {offset:.3f}s")
        except ImportError:
            check_warn("ntplib not installed (cannot verify time sync)")
            check_info("Install with: pip install ntplib")
        except Exception as e:
            check_warn(f"Could not verify time synchronization: {e}")
    
    def check_entropy(self):
        """Check system entropy for cryptographic operations."""
        print_header("ENTROPY CHECK")
        
        if self.system == "Linux":
            try:
                with open('/proc/sys/kernel/random/entropy_avail', 'r') as f:
                    entropy = int(f.read().strip())