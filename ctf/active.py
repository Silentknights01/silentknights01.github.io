#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
████████ ULTIMATE ACTIVE RECON TOOL v1.0 ████████
✅ فقط ابزارهای خود Kali
✅ بدون نیاز به کتابخانه‌های Python
✅ 100% مبتنی بر دستورات سیستمی
"""

import subprocess
import sys
import os
import re
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import socket
import time
from typing import Dict, List, Set, Tuple, Optional
import ipaddress

# ==================== فقط از کتابخانه‌های استاندارد استفاده شده ====================

# ==================== Colorama ====================
try:
    from colorama import Fore, Back, Style, init
    init(autoreset=True)
except ImportError:
    class Fore:
        RED = '\033[91m'; GREEN = '\033[92m'; YELLOW = '\033[93m'
        BLUE = '\033[94m'; MAGENTA = '\033[95m'; CYAN = '\033[96m'
        WHITE = '\033[97m'; RESET = '\033[0m'
    class Back:
        RED = '\033[101m'; GREEN = '\033[102m'; YELLOW = '\033[103m'
        BLUE = '\033[104m'; MAGENTA = '\033[105m'; CYAN = '\033[106m'
        WHITE = '\033[107m'; RESET = '\033[0m'
    class Style:
        BRIGHT = '\033[1m'; DIM = '\033[2m'; RESET_ALL = '\033[0m'

# ==================== کلاس اصلی ====================
class KaliActiveRecon:
    def __init__(self, target: str):
        self.target = target
        self.results = {
            'target': target,
            'timestamp': datetime.now().isoformat(),
            'ping': {},
            'dns': {},
            'traceroute': '',
            'nmap': {
                'basic': '',
                'full': '',
                'services': '',
                'os': ''
            },
            'open_ports': [],
            'services': [],
            'os_detection': '',
            'scripts': {}
        }
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = f"active_recon_{target}_{self.timestamp}"
        
        os.makedirs(self.output_dir, exist_ok=True)
        
        print(f"{Fore.CYAN}{'='*70}")
        print(f"{Fore.RED}{Style.BRIGHT}🔴 ACTIVE RECON TOOL v1.0")
        print(f"{Fore.CYAN}{'='*70}")
        print(f"{Fore.GREEN}📌 Target: {target}")
        print(f"{Fore.GREEN}📁 Output: {self.output_dir}")
        print(f"{Fore.GREEN}⏱️  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{Fore.YELLOW}⚠️  Active Scanning - Use only on authorized targets!")
        print(f"{Fore.CYAN}{'='*70}\n")

    def log(self, message: str, level: str = "INFO"):
        colors = {
            'INFO': Fore.CYAN,
            'SUCCESS': Fore.GREEN,
            'WARNING': Fore.YELLOW,
            'ERROR': Fore.RED,
            'CRITICAL': Back.RED + Fore.WHITE
        }
        color = colors.get(level, Fore.WHITE)
        print(f"{color}[{level}] {message}")

    def save_json(self, data: dict, filename: str):
        with open(f"{self.output_dir}/{filename}", 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str, ensure_ascii=False)

    def save_text(self, content: str, filename: str):
        with open(f"{self.output_dir}/{filename}", 'w', encoding='utf-8') as f:
            f.write(content)

    def run_command(self, cmd: str, timeout: int = 60) -> Tuple[str, str]:
        """اجرای دستور در ترمینال با timeout"""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
            return result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return f"[TIMEOUT] Command took longer than {timeout}s", ""
        except Exception as e:
            return f"[ERROR] {str(e)}", ""

    def check_tool(self, tool: str) -> bool:
        """بررسی وجود ابزار در سیستم"""
        stdout, stderr = self.run_command(f"which {tool}")
        return bool(stdout.strip())

    # ========== 1. PING ==========
    def ping_scan(self):
        """بررسی زنده بودن هاست با ping"""
        self.log(f"Pinging {self.target}...", "INFO")
        
        stdout, stderr = self.run_command(f"ping -c 4 {self.target}", timeout=10)
        
        if stdout:
            self.save_text(stdout, "ping.txt")
            
            # استخراج اطلاعات
            ping_data = {}
            
            # IP
            ip_match = re.search(r'PING .*?\(([0-9.]+)\)', stdout)
            if ip_match:
                ping_data['ip'] = ip_match.group(1)
            
            # Packet Loss
            loss_match = re.search(r'(\d+)% packet loss', stdout)
            if loss_match:
                ping_data['packet_loss'] = loss_match.group(1)
            
            # Time
            time_match = re.search(r'time=([0-9.]+) ms', stdout)
            if time_match:
                ping_data['avg_time'] = time_match.group(1)
            
            # TTL
            ttl_match = re.search(r'ttl=(\d+)', stdout)
            if ttl_match:
                ping_data['ttl'] = ttl_match.group(1)
                # تشخیص OS از TTL
                ttl = int(ttl_match.group(1))
                if ttl <= 64:
                    ping_data['os_guess'] = 'Linux/Unix'
                elif ttl <= 128:
                    ping_data['os_guess'] = 'Windows'
                else:
                    ping_data['os_guess'] = 'Unknown'
            
            self.results['ping'] = ping_data
            
            print(f"\n{Fore.MAGENTA}{'='*50}")
            print(f"{Fore.YELLOW}📡 PING RESULTS")
            print(f"{Fore.MAGENTA}{'='*50}")
            
            print(f"{Fore.CYAN}IP: {Fore.WHITE}{ping_data.get('ip', 'N/A')}")
            print(f"{Fore.CYAN}Packet Loss: {Fore.WHITE}{ping_data.get('packet_loss', 'N/A')}%")
            print(f"{Fore.CYAN}Avg Time: {Fore.WHITE}{ping_data.get('avg_time', 'N/A')} ms")
            print(f"{Fore.CYAN}TTL: {Fore.WHITE}{ping_data.get('ttl', 'N/A')}")
            if ping_data.get('os_guess'):
                print(f"{Fore.CYAN}OS Guess: {Fore.WHITE}{ping_data['os_guess']}")
            
            self.save_json(ping_data, 'ping.json')
            self.log("Ping completed", "SUCCESS")
        else:
            self.log("Ping failed - host may be down or ICMP blocked", "WARNING")
            self.results['ping'] = {'status': 'down_or_blocked'}

    # ========== 2. HOST ==========
    def host_lookup(self):
        """DNS Lookup با host"""
        self.log(f"Running host lookup on {self.target}...", "INFO")
        
        stdout, stderr = self.run_command(f"host {self.target}")
        
        if stdout:
            self.save_text(stdout, "host.txt")
            
            dns_data = {}
            
            # A Record
            a_match = re.findall(r'has address ([0-9.]+)', stdout)
            if a_match:
                dns_data['A'] = a_match
            
            # AAAA Record
            aaaa_match = re.findall(r'has IPv6 address ([0-9a-f:]+)', stdout)
            if aaaa_match:
                dns_data['AAAA'] = aaaa_match
            
            # MX Record
            mx_match = re.findall(r'handled by (\d+) (.+)', stdout)
            if mx_match:
                dns_data['MX'] = [f"{pref} {server}" for pref, server in mx_match]
            
            # NS Record
            ns_match = re.findall(r'name server (.+)', stdout)
            if ns_match:
                dns_data['NS'] = ns_match
            
            # CNAME
            cname_match = re.findall(r'is an alias for (.+)', stdout)
            if cname_match:
                dns_data['CNAME'] = cname_match
            
            self.results['dns']['host'] = dns_data
            
            print(f"\n{Fore.MAGENTA}{'='*50}")
            print(f"{Fore.YELLOW}🌐 HOST LOOKUP")
            print(f"{Fore.MAGENTA}{'='*50}")
            
            if dns_data.get('A'):
                print(f"{Fore.CYAN}A Records:")
                for ip in dns_data['A'][:5]:
                    print(f"  {Fore.WHITE}→ {ip}")
            
            if dns_data.get('MX'):
                print(f"{Fore.CYAN}MX Records:")
                for mx in dns_data['MX'][:5]:
                    print(f"  {Fore.WHITE}→ {mx}")
            
            if dns_data.get('NS'):
                print(f"{Fore.CYAN}NS Records:")
                for ns in dns_data['NS'][:5]:
                    print(f"  {Fore.WHITE}→ {ns}")
            
            self.save_json(dns_data, 'host.json')
            self.log("Host lookup completed", "SUCCESS")

    # ========== 3. NSLOOKUP ==========
    def nslookup(self):
        """DNS Lookup با nslookup"""
        self.log(f"Running nslookup on {self.target}...", "INFO")
        
        record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA']
        nslookup_data = {}
        
        for rtype in record_types:
            stdout, stderr = self.run_command(f"nslookup -type={rtype} {self.target}", timeout=10)
            if stdout:
                nslookup_data[rtype] = stdout
                # استخراج اطلاعات
                if rtype == 'A':
                    ips = re.findall(r'Address: ([0-9.]+)', stdout)
                    if ips:
                        nslookup_data[f'{rtype}_ips'] = ips
        
        self.results['dns']['nslookup'] = nslookup_data
        self.save_text(str(nslookup_data), 'nslookup.txt')
        self.save_json(nslookup_data, 'nslookup.json')
        self.log("nslookup completed", "SUCCESS")

    # ========== 4. DIG ==========
    def dig_analysis(self):
        """DNS Analysis با dig"""
        self.log(f"Running dig on {self.target}...", "INFO")
        
        record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA', 'SRV']
        dig_data = {}
        
        for rtype in record_types:
            stdout, stderr = self.run_command(f"dig {self.target} {rtype} +short", timeout=10)
            if stdout.strip():
                dig_data[rtype] = [line.strip() for line in stdout.split('\n') if line.strip()]
        
        self.results['dns']['dig'] = dig_data
        
        print(f"\n{Fore.MAGENTA}{'='*50}")
        print(f"{Fore.YELLOW}🔍 DIG RESULTS")
        print(f"{Fore.MAGENTA}{'='*50}")
        
        for rtype, records in dig_data.items():
            if records:
                print(f"\n{Fore.CYAN}[{rtype}]")
                for record in records[:5]:
                    print(f"  {Fore.WHITE}→ {record}")
                if len(records) > 5:
                    print(f"  {Fore.YELLOW}... and {len(records)-5} more")
        
        self.save_json(dig_data, 'dig.json')
        self.log("dig completed", "SUCCESS")

    # ========== 5. TRACEROUTE ==========
    def traceroute(self):
        """Traceroute با traceroute"""
        self.log(f"Running traceroute to {self.target}...", "INFO")
        
        if not self.check_tool("traceroute"):
            self.log("traceroute not found", "WARNING")
            return
        
        stdout, stderr = self.run_command(f"traceroute -I {self.target}", timeout=30)
        
        if stdout:
            self.save_text(stdout, "traceroute.txt")
            self.results['traceroute'] = stdout
            
            print(f"\n{Fore.MAGENTA}{'='*50}")
            print(f"{Fore.YELLOW}🛤️ TRACEROUTE")
            print(f"{Fore.MAGENTA}{'='*50}")
            
            # نمایش 15 خط اول
            lines = stdout.split('\n')[:15]
            for line in lines:
                if line.strip():
                    print(f"  {Fore.WHITE}{line}")
            
            if len(stdout.split('\n')) > 15:
                print(f"  {Fore.YELLOW}... and {len(stdout.split('\n'))-15} more lines")
            
            self.log("traceroute completed", "SUCCESS")

    # ========== 6. NMAP - Basic ==========
    def nmap_basic(self):
        """Nmap Basic Scan"""
        self.log(f"Running Nmap basic scan on {self.target}...", "INFO")
        
        if not self.check_tool("nmap"):
            self.log("nmap not found - installing...", "WARNING")
            self.run_command("sudo apt install -y nmap")
            if not self.check_tool("nmap"):
                self.log("nmap installation failed", "ERROR")
                return
        
        # Basic Scan (Top 1000 ports)
        stdout, stderr = self.run_command(f"nmap -T4 {self.target}", timeout=60)
        
        if stdout:
            self.save_text(stdout, "nmap_basic.txt")
            self.results['nmap']['basic'] = stdout
            
            # استخراج پورت‌های باز
            ports = re.findall(r'(\d+)/tcp\s+open\s+(\S+)', stdout)
            for port, service in ports:
                self.results['open_ports'].append({'port': port, 'service': service})
            
            print(f"\n{Fore.MAGENTA}{'='*50}")
            print(f"{Fore.YELLOW}🔍 NMAP BASIC SCAN")
            print(f"{Fore.MAGENTA}{'='*50}")
            
            # نمایش خلاصه
            if ports:
                print(f"{Fore.CYAN}Open Ports:")
                for port, service in ports:
                    print(f"  {Fore.GREEN}✓ {Fore.WHITE}Port {port}: {service}")
            else:
                print(f"{Fore.YELLOW}No open ports found or host is down")
            
            self.log("Nmap basic scan completed", "SUCCESS")

    # ========== 7. NMAP - Full Port Scan ==========
    def nmap_full(self):
        """Nmap Full Port Scan (All ports)"""
        self.log(f"Running Nmap full port scan on {self.target}...", "INFO")
        
        if not self.check_tool("nmap"):
            self.log("nmap not found", "ERROR")
            return
        
        stdout, stderr = self.run_command(f"nmap -p- -T4 {self.target}", timeout=300)
        
        if stdout:
            self.save_text(stdout, "nmap_full.txt")
            self.results['nmap']['full'] = stdout
            
            # استخراج پورت‌ها
            ports = re.findall(r'(\d+)/tcp\s+open', stdout)
            for port in ports:
                if port not in [p['port'] for p in self.results['open_ports']]:
                    self.results['open_ports'].append({'port': port, 'service': 'unknown'})
            
            print(f"\n{Fore.MAGENTA}{'='*50}")
            print(f"{Fore.YELLOW}📡 NMAP FULL PORT SCAN")
            print(f"{Fore.MAGENTA}{'='*50}")
            
            if ports:
                print(f"{Fore.CYAN}All Open Ports Found:")
                for port in ports:
                    print(f"  {Fore.GREEN}✓ {Fore.WHITE}Port {port}")
                print(f"{Fore.CYAN}Total: {len(ports)} open ports")
            else:
                print(f"{Fore.YELLOW}No open ports found")
            
            self.log("Nmap full port scan completed", "SUCCESS")

    # ========== 8. NMAP - Service Detection ==========
    def nmap_services(self):
        """Nmap Service & Version Detection"""
        self.log(f"Running Nmap service detection on {self.target}...", "INFO")
        
        if not self.check_tool("nmap"):
            self.log("nmap not found", "ERROR")
            return
        
        # فقط روی پورت‌های باز
        if not self.results['open_ports']:
            self.log("No open ports found - skipping service detection", "WARNING")
            return
        
        ports = ','.join([p['port'] for p in self.results['open_ports']][:20])
        if not ports:
            self.log("No ports to scan", "WARNING")
            return
        
        stdout, stderr = self.run_command(f"nmap -sV -p {ports} -T4 {self.target}", timeout=120)
        
        if stdout:
            self.save_text(stdout, "nmap_services.txt")
            self.results['nmap']['services'] = stdout
            
            # استخراج سرویس‌ها
            services = re.findall(r'(\d+)/tcp\s+open\s+(\S+)\s+(\S+)\s+(.+)', stdout)
            for port, state, service, version in services:
                self.results['services'].append({
                    'port': port,
                    'service': service,
                    'version': version.strip()
                })
            
            print(f"\n{Fore.MAGENTA}{'='*50}")
            print(f"{Fore.YELLOW}🛠️ NMAP SERVICE DETECTION")
            print(f"{Fore.MAGENTA}{'='*50}")
            
            if self.results['services']:
                for svc in self.results['services']:
                    print(f"{Fore.CYAN}Port {svc['port']}:")
                    print(f"  {Fore.WHITE}Service: {svc['service']}")
                    print(f"  {Fore.WHITE}Version: {svc['version']}")
                    print()
            else:
                print(f"{Fore.YELLOW}No services detected")
            
            self.save_json(self.results['services'], 'services.json')
            self.log("Nmap service detection completed", "SUCCESS")

    # ========== 9. NMAP - OS Detection ==========
    def nmap_os(self):
        """Nmap OS Detection"""
        self.log(f"Running Nmap OS detection on {self.target}...", "INFO")
        
        if not self.check_tool("nmap"):
            self.log("nmap not found", "ERROR")
            return
        
        stdout, stderr = self.run_command(f"nmap -O -T4 {self.target}", timeout=120)
        
        if stdout:
            self.save_text(stdout, "nmap_os.txt")
            self.results['nmap']['os'] = stdout
            
            # استخراج OS
            os_match = re.search(r'OS details?: (.+)', stdout, re.IGNORECASE)
            if os_match:
                self.results['os_detection'] = os_match.group(1).strip()
            
            print(f"\n{Fore.MAGENTA}{'='*50}")
            print(f"{Fore.YELLOW}💻 NMAP OS DETECTION")
            print(f"{Fore.MAGENTA}{'='*50}")
            
            if self.results['os_detection']:
                print(f"{Fore.CYAN}OS: {Fore.WHITE}{self.results['os_detection']}")
            else:
                # از TTL استفاده کن
                if self.results['ping'].get('os_guess'):
                    print(f"{Fore.CYAN}OS Guess (from TTL): {Fore.WHITE}{self.results['ping']['os_guess']}")
                else:
                    print(f"{Fore.YELLOW}OS could not be determined")
            
            self.save_json({'os': self.results['os_detection']}, 'os_detection.json')
            self.log("Nmap OS detection completed", "SUCCESS")

    # ========== 10. NMAP - Scripts ==========
    def nmap_scripts(self):
        """Nmap Default Scripts"""
        self.log(f"Running Nmap default scripts on {self.target}...", "INFO")
        
        if not self.check_tool("nmap"):
            self.log("nmap not found", "ERROR")
            return
        
        if not self.results['open_ports']:
            self.log("No open ports - skipping scripts", "WARNING")
            return
        
        ports = ','.join([p['port'] for p in self.results['open_ports']][:10])
        if not ports:
            self.log("No ports to scan", "WARNING")
            return
        
        stdout, stderr = self.run_command(f"nmap -sC -p {ports} -T4 {self.target}", timeout=180)
        
        if stdout:
            self.save_text(stdout, "nmap_scripts.txt")
            self.results['scripts']['default'] = stdout
            
            print(f"\n{Fore.MAGENTA}{'='*50}")
            print(f"{Fore.YELLOW}📜 NMAP SCRIPTS")
            print(f"{Fore.MAGENTA}{'='*50}")
            
            # نمایش خلاصه
            lines = stdout.split('\n')[:30]
            for line in lines:
                if line.strip():
                    print(f"  {Fore.WHITE}{line}")
            
            if len(stdout.split('\n')) > 30:
                print(f"  {Fore.YELLOW}... and {len(stdout.split('\n'))-30} more lines")
            
            self.log("Nmap scripts completed", "SUCCESS")

    # ========== 11. NMAP - Aggressive ==========
    def nmap_aggressive(self):
        """Nmap Aggressive Scan"""
        self.log(f"Running Nmap aggressive scan on {self.target}...", "INFO")
        
        if not self.check_tool("nmap"):
            self.log("nmap not found", "ERROR")
            return
        
        stdout, stderr = self.run_command(f"nmap -A -T4 {self.target}", timeout=180)
        
        if stdout:
            self.save_text(stdout, "nmap_aggressive.txt")
            self.results['nmap']['aggressive'] = stdout
            
            print(f"\n{Fore.MAGENTA}{'='*50}")
            print(f"{Fore.YELLOW}⚡ NMAP AGGRESSIVE SCAN")
            print(f"{Fore.MAGENTA}{'='*50}")
            
            lines = stdout.split('\n')[:25]
            for line in lines:
                if line.strip():
                    print(f"  {Fore.WHITE}{line}")
            
            self.log("Nmap aggressive scan completed", "SUCCESS")

    # ========== 12. MASSCAN ==========
    def masscan_scan(self):
        """Masscan for fast port scanning"""
        self.log(f"Running Masscan on {self.target}...", "INFO")
        
        if not self.check_tool("masscan"):
            self.log("masscan not found - installing...", "WARNING")
            self.run_command("sudo apt install -y masscan")
            if not self.check_tool("masscan"):
                self.log("masscan installation failed", "WARNING")
                return
        
        stdout, stderr = self.run_command(f"masscan -p1-65535 {self.target} --rate=1000", timeout=120)
        
        if stdout:
            self.save_text(stdout, "masscan.txt")
            self.results['masscan'] = stdout
            
            print(f"\n{Fore.MAGENTA}{'='*50}")
            print(f"{Fore.YELLOW}⚡ MASSCAN RESULTS")
            print(f"{Fore.MAGENTA}{'='*50}")
            
            # استخراج پورت‌ها
            ports = re.findall(r'Discovered open port (\d+)/tcp', stdout)
            if ports:
                print(f"{Fore.CYAN}Open Ports Found:")
                for port in ports[:20]:
                    print(f"  {Fore.GREEN}✓ {Fore.WHITE}Port {port}")
                if len(ports) > 20:
                    print(f"  {Fore.YELLOW}... and {len(ports)-20} more")
            else:
                print(f"{Fore.YELLOW}No open ports found by masscan")
            
            self.log("Masscan completed", "SUCCESS")

    # ========== 13. Final Report ==========
    def final_report(self):
        """گزارش نهایی"""
        print(f"\n{Fore.GREEN}{'='*70}")
        print(f"{Fore.RED}{Style.BRIGHT}✅ ACTIVE RECON COMPLETE")
        print(f"{Fore.GREEN}{'='*70}")
        
        print(f"\n{Fore.CYAN}📊 SUMMARY REPORT")
        print(f"{Fore.CYAN}{'-'*50}")
        
        print(f"{Fore.WHITE}Target: {Fore.YELLOW}{self.target}")
        print(f"{Fore.WHITE}Date: {Fore.YELLOW}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{Fore.WHITE}Output: {Fore.YELLOW}{self.output_dir}")
        
        print(f"\n{Fore.WHITE}Results:")
        
        if self.results['ping'].get('ip'):
            print(f"  {Fore.CYAN}IP: {Fore.WHITE}{self.results['ping']['ip']}")
        
        if self.results['ping'].get('os_guess'):
            print(f"  {Fore.CYAN}OS Guess: {Fore.WHITE}{self.results['ping']['os_guess']}")
        
        if self.results['os_detection']:
            print(f"  {Fore.CYAN}OS (Nmap): {Fore.WHITE}{self.results['os_detection']}")
        
        print(f"  {Fore.CYAN}Open Ports: {Fore.WHITE}{len(self.results['open_ports'])}")
        
        if self.results['services']:
            print(f"  {Fore.CYAN}Services: {Fore.WHITE}{len(self.results['services'])}")
        
        # خلاصه
        summary = {
            'target': self.target,
            'timestamp': datetime.now().isoformat(),
            'ip': self.results['ping'].get('ip', 'N/A'),
            'os_guess': self.results['ping'].get('os_guess', 'N/A'),
            'os_detected': self.results.get('os_detection', 'N/A'),
            'open_ports_count': len(self.results['open_ports']),
            'services_count': len(self.results['services']),
            'open_ports': self.results['open_ports'],
            'services': self.results['services'],
            'files': os.listdir(self.output_dir)
        }
        
        self.save_json(summary, 'summary.json')
        
        print(f"\n{Fore.GREEN}📁 All results saved to: {self.output_dir}")
        print(f"{Fore.GREEN}{'='*70}\n")

    # ========== 14. Run Full ==========
    def run_full_recon(self):
        """اجرای کامل"""
        self.log("🚀 Starting Full Active Reconnaissance", "CRITICAL")
        
        start_time = time.time()
        
        # مرحله 1: Ping
        self.ping_scan()
        
        # مرحله 2: DNS Tools
        self.host_lookup()
        self.nslookup()
        self.dig_analysis()
        
        # مرحله 3: Traceroute
        self.traceroute()
        
        # مرحله 4: Nmap
        self.nmap_basic()
        self.nmap_full()
        self.nmap_services()
        self.nmap_os()
        self.nmap_scripts()
        self.nmap_aggressive()
        
        # مرحله 5: Masscan
        self.masscan_scan()
        
        # مرحله 6: Report
        self.final_report()
        
        elapsed = time.time() - start_time
        print(f"{Fore.CYAN}⏱️  Total time: {elapsed:.2f} seconds")

    def run_quick(self):
        """اجرای سریع"""
        self.log("🚀 Starting Quick Active Reconnaissance", "CRITICAL")
        
        start_time = time.time()
        
        self.ping_scan()
        self.host_lookup()
        self.dig_analysis()
        self.nmap_basic()
        self.nmap_services()
        self.nmap_os()
        
        self.final_report()
        
        elapsed = time.time() - start_time
        print(f"{Fore.CYAN}⏱️  Total time: {elapsed:.2f} seconds")

# ==================== Main ====================
def main():
    if len(sys.argv) < 2:
        print(f"""
{Fore.RED}████████ ACTIVE RECON TOOL v1.0 ████████
{Fore.YELLOW}
Usage:
  python3 active_recon.py <target>        # Full recon (all tools)
  python3 active_recon.py <target> --quick # Quick recon (basic tools)

{Fore.GREEN}Examples:
  python3 active_recon.py 192.168.1.10
  python3 active_recon.py example.com
  python3 active_recon.py 192.168.1.10 --quick

{Fore.CYAN}Tools Used (Kali System Tools):
  • ping       - Host discovery
  • host       - DNS lookup
  • nslookup   - DNS lookup
  • dig        - Advanced DNS
  • traceroute - Network path
  • nmap       - Port scanning, service detection, OS detection
  • masscan    - Fast port scanning

{Fore.YELLOW}⚠️  WARNING: Active scanning can be detected!
  Use only on authorized targets and CTF environments.

{Fore.RESET}""")
        sys.exit(1)
    
    target = sys.argv[1]
    quick_mode = '--quick' in sys.argv
    
    recon = KaliActiveRecon(target)
    
    if quick_mode:
        recon.run_quick()
    else:
        recon.run_full_recon()

if __name__ == "__main__":
    main()