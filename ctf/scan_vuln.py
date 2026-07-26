#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
████████ ULTIMATE SCANNING & VULNERABILITY ANALYSIS TOOL v1.0 ████████
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
import socket
import time
from typing import Dict, List, Set, Tuple, Optional

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
class KaliScanVuln:
    def __init__(self, target: str):
        self.target = target
        self.results = {
            'target': target,
            'timestamp': datetime.now().isoformat(),
            'network': {},
            'ports': {},
            'services': {},
            'vulnerabilities': {},
            'web_vulns': {},
            'exploits': {},
            'summary': {}
        }
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = f"scan_vuln_{target}_{self.timestamp}"
        
        os.makedirs(self.output_dir, exist_ok=True)
        
        print(f"{Fore.CYAN}{'='*70}")
        print(f"{Fore.RED}{Style.BRIGHT}🔍 SCANNING & VULNERABILITY ANALYSIS TOOL v1.0")
        print(f"{Fore.CYAN}{'='*70}")
        print(f"{Fore.GREEN}📌 Target: {target}")
        print(f"{Fore.GREEN}📁 Output: {self.output_dir}")
        print(f"{Fore.GREEN}⏱️  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{Fore.YELLOW}⚠️  Use only on authorized targets!")
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

    def run_command(self, cmd: str, timeout: int = 120) -> Tuple[str, str]:
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

    # ========== A. Network Scanning ==========
    
    # 1. Host Discovery با Nmap
    def network_scan(self):
        """اسکن شبکه برای پیدا کردن هاست‌های زنده"""
        self.log("Running Network Scan (Host Discovery)...", "INFO")
        
        network_data = {}
        
        # Ping Sweep
        self.log("Nmap Ping Sweep...", "INFO")
        stdout, stderr = self.run_command(f"nmap -sn {self.target}/24", timeout=60)
        if stdout:
            network_data['ping_sweep'] = stdout
            self.save_text(stdout, "network_ping_sweep.txt")
            
            # استخراج هاست‌های زنده
            hosts = re.findall(r'Nmap scan report for ([0-9.]+)', stdout)
            if hosts:
                network_data['live_hosts'] = hosts
                print(f"\n{Fore.MAGENTA}{'='*50}")
                print(f"{Fore.YELLOW}🌐 NETWORK SCAN RESULTS")
                print(f"{Fore.MAGENTA}{'='*50}")
                print(f"{Fore.CYAN}Live Hosts Found:")
                for host in hosts[:20]:
                    print(f"  {Fore.GREEN}✓ {Fore.WHITE}{host}")
                if len(hosts) > 20:
                    print(f"  {Fore.YELLOW}... and {len(hosts)-20} more")
        
        # ARP Scan (Local Network)
        if self.check_tool("arp-scan"):
            self.log("ARP Scan...", "INFO")
            stdout, stderr = self.run_command(f"arp-scan {self.target}/24", timeout=30)
            if stdout:
                network_data['arp_scan'] = stdout
                self.save_text(stdout, "network_arp_scan.txt")
        
        # Netdiscover
        if self.check_tool("netdiscover"):
            self.log("Netdiscover...", "INFO")
            stdout, stderr = self.run_command(f"netdiscover -r {self.target}/24 -i eth0", timeout=30)
            if stdout:
                network_data['netdiscover'] = stdout
                self.save_text(stdout, "network_netdiscover.txt")
        
        self.results['network'] = network_data
        self.save_json(network_data, 'network.json')
        self.log("Network scan completed", "SUCCESS")

    # ========== B. Port & Service Scanning ==========
    
    # 2. Port Scan (Basic)
    def port_scan_basic(self):
        """اسکن پورت‌های رایج"""
        self.log("Running Basic Port Scan...", "INFO")
        
        stdout, stderr = self.run_command(f"nmap -T4 -F {self.target}", timeout=60)
        
        if stdout:
            self.save_text(stdout, "ports_basic.txt")
            self.results['ports']['basic'] = stdout
            
            # استخراج پورت‌های باز
            ports = re.findall(r'(\d+)/tcp\s+open\s+(\S+)', stdout)
            if ports:
                self.results['ports']['open'] = [{'port': p, 'service': s} for p, s in ports]
            
            print(f"\n{Fore.MAGENTA}{'='*50}")
            print(f"{Fore.YELLOW}📡 BASIC PORT SCAN")
            print(f"{Fore.MAGENTA}{'='*50}")
            
            if ports:
                print(f"{Fore.CYAN}Open Ports:")
                for port, service in ports:
                    print(f"  {Fore.GREEN}✓ {Fore.WHITE}Port {port}: {service}")
            else:
                print(f"{Fore.YELLOW}No open ports found")
        
        self.log("Basic port scan completed", "SUCCESS")

    # 3. Full Port Scan
    def port_scan_full(self):
        """اسکن کامل همه پورت‌ها"""
        self.log("Running Full Port Scan (all ports)...", "INFO")
        
        stdout, stderr = self.run_command(f"nmap -p- -T4 {self.target}", timeout=300)
        
        if stdout:
            self.save_text(stdout, "ports_full.txt")
            self.results['ports']['full'] = stdout
            
            # استخراج پورت‌ها
            ports = re.findall(r'(\d+)/tcp\s+open', stdout)
            if ports:
                for port in ports:
                    if port not in [p['port'] for p in self.results['ports'].get('open', [])]:
                        self.results['ports']['open'].append({'port': port, 'service': 'unknown'})
            
            print(f"\n{Fore.MAGENTA}{'='*50}")
            print(f"{Fore.YELLOW}📡 FULL PORT SCAN")
            print(f"{Fore.MAGENTA}{'='*50}")
            
            if ports:
                print(f"{Fore.CYAN}All Open Ports Found:")
                for port in ports[:20]:
                    print(f"  {Fore.GREEN}✓ {Fore.WHITE}Port {port}")
                if len(ports) > 20:
                    print(f"  {Fore.YELLOW}... and {len(ports)-20} more")
                print(f"{Fore.CYAN}Total: {len(ports)} open ports")
        
        self.log("Full port scan completed", "SUCCESS")

    # 4. Service Detection
    def service_detection(self):
        """تشخیص سرویس‌ها و نسخه‌ها"""
        self.log("Running Service Detection...", "INFO")
        
        if not self.results['ports'].get('open'):
            self.log("No open ports found - skipping service detection", "WARNING")
            return
        
        ports = ','.join([p['port'] for p in self.results['ports']['open'][:20]])
        if not ports:
            return
        
        stdout, stderr = self.run_command(f"nmap -sV -p {ports} -T4 {self.target}", timeout=120)
        
        if stdout:
            self.save_text(stdout, "services.txt")
            self.results['services']['detection'] = stdout
            
            # استخراج سرویس‌ها
            services = re.findall(r'(\d+)/tcp\s+open\s+(\S+)\s+(\S+)\s+(.+)', stdout)
            if services:
                self.results['services']['list'] = [
                    {'port': p, 'service': s, 'version': v.strip()}
                    for p, s, _, v in services
                ]
            
            print(f"\n{Fore.MAGENTA}{'='*50}")
            print(f"{Fore.YELLOW}🛠️ SERVICE DETECTION")
            print(f"{Fore.MAGENTA}{'='*50}")
            
            if services:
                for port, service, _, version in services[:20]:
                    print(f"{Fore.CYAN}Port {port}:")
                    print(f"  {Fore.WHITE}Service: {service}")
                    print(f"  {Fore.WHITE}Version: {version}")
                    print()
        
        self.log("Service detection completed", "SUCCESS")

    # 5. OS Detection
    def os_detection(self):
        """تشخیص سیستم‌عامل"""
        self.log("Running OS Detection...", "INFO")
        
        stdout, stderr = self.run_command(f"nmap -O -T4 {self.target}", timeout=120)
        
        if stdout:
            self.save_text(stdout, "os_detection.txt")
            self.results['services']['os'] = stdout
            
            # استخراج OS
            os_match = re.search(r'OS details?: (.+)', stdout, re.IGNORECASE)
            if os_match:
                self.results['services']['os_guess'] = os_match.group(1).strip()
            
            print(f"\n{Fore.MAGENTA}{'='*50}")
            print(f"{Fore.YELLOW}💻 OS DETECTION")
            print(f"{Fore.MAGENTA}{'='*50}")
            
            if self.results['services'].get('os_guess'):
                print(f"  {Fore.CYAN}OS: {Fore.WHITE}{self.results['services']['os_guess']}")
            else:
                print(f"{Fore.YELLOW}OS could not be determined")
        
        self.log("OS detection completed", "SUCCESS")

    # ========== C. Vulnerability Scanning ==========
    
    # 6. Nmap NSE Vulnerability
    def nmap_nse_vuln(self):
        """اسکن آسیب‌پذیری با Nmap NSE"""
        self.log("Running Nmap NSE Vulnerability Scan...", "INFO")
        
        nse_data = {}
        
        # Vuln Scripts روی همه پورت‌ها
        stdout, stderr = self.run_command(f"nmap --script=vuln -sV {self.target}", timeout=180)
        if stdout:
            nse_data['vuln'] = stdout
            self.save_text(stdout, "nmap_nse_vuln.txt")
            
            # استخراج CVEs
            cves = re.findall(r'CVE-\d{4}-\d{4,}', stdout)
            if cves:
                nse_data['cves'] = list(set(cves))
            
            print(f"\n{Fore.MAGENTA}{'='*50}")
            print(f"{Fore.YELLOW}🔴 NMAP NSE VULNERABILITY SCAN")
            print(f"{Fore.MAGENTA}{'='*50}")
            
            if cves:
                print(f"{Fore.CYAN}CVEs Found:")
                for cve in list(set(cves))[:20]:
                    print(f"  {Fore.RED}⚠️ {Fore.WHITE}{cve}")
                if len(set(cves)) > 20:
                    print(f"  {Fore.YELLOW}... and {len(set(cves))-20} more")
            else:
                # نمایش خلاصه
                lines = stdout.split('\n')[:20]
                for line in lines:
                    if 'VULNERABLE' in line or 'CVE' in line:
                        print(f"  {Fore.RED}→ {Fore.WHITE}{line.strip()}")
        
        # Default Scripts
        stdout, stderr = self.run_command(f"nmap -sC -sV {self.target}", timeout=120)
        if stdout:
            nse_data['default'] = stdout
            self.save_text(stdout, "nmap_nse_default.txt")
        
        self.results['vulnerabilities']['nmap_nse'] = nse_data
        self.save_json(nse_data, 'nmap_nse.json')
        self.log("Nmap NSE scan completed", "SUCCESS")

    # 7. Nikto Scan
    def nikto_scan(self):
        """اسکن وب‌سرور با Nikto"""
        self.log("Running Nikto Web Server Scan...", "INFO")
        
        if not self.check_tool("nikto"):
            self.log("Nikto not found - skipping", "WARNING")
            return
        
        stdout, stderr = self.run_command(f"nikto -h {self.target} -ssl -Format html -o {self.output_dir}/nikto.html", timeout=120)
        
        if stdout:
            self.save_text(stdout, "nikto.txt")
            self.results['vulnerabilities']['nikto'] = stdout
            
            # استخراج یافته‌ها
            findings = []
            for line in stdout.split('\n'):
                if '+ ' in line:
                    findings.append(line.strip())
            
            print(f"\n{Fore.MAGENTA}{'='*50}")
            print(f"{Fore.YELLOW}🔴 NIKTO RESULTS")
            print(f"{Fore.MAGENTA}{'='*50}")
            
            if findings:
                print(f"{Fore.CYAN}Findings:")
                for finding in findings[:20]:
                    print(f"  {Fore.YELLOW}→ {Fore.WHITE}{finding}")
                if len(findings) > 20:
                    print(f"  {Fore.YELLOW}... and {len(findings)-20} more")
        
        self.log("Nikto scan completed", "SUCCESS")

    # 8. Nuclei Scan
    def nuclei_scan(self):
        """اسکن با Nuclei"""
        self.log("Running Nuclei Scan...", "INFO")
        
        if not self.check_tool("nuclei"):
            self.log("Nuclei not found - installing...", "WARNING")
            self.run_command("sudo apt install -y nuclei")
            if not self.check_tool("nuclei"):
                self.log("Nuclei installation failed - skipping", "WARNING")
                return
        
        stdout, stderr = self.run_command(f"nuclei -u {self.target} -severity critical,high -o {self.output_dir}/nuclei.txt", timeout=180)
        
        if stdout:
            self.save_text(stdout, "nuclei.txt")
            self.results['vulnerabilities']['nuclei'] = stdout
            
            # استخراج CVEs
            cves = re.findall(r'CVE-\d{4}-\d{4,}', stdout)
            if cves:
                self.results['vulnerabilities']['cves'] = list(set(cves))
            
            print(f"\n{Fore.MAGENTA}{'='*50}")
            print(f"{Fore.YELLOW}🔴 NUCLEI RESULTS")
            print(f"{Fore.MAGENTA}{'='*50}")
            
            if cves:
                print(f"{Fore.CYAN}CVEs Found:")
                for cve in list(set(cves))[:20]:
                    print(f"  {Fore.RED}⚠️ {Fore.WHITE}{cve}")
            else:
                lines = stdout.split('\n')[:20]
                for line in lines:
                    if line.strip():
                        print(f"  {Fore.WHITE}{line}")
        
        self.log("Nuclei scan completed", "SUCCESS")

    # 9. SearchSploit
    def searchsploit(self):
        """جستجو در Exploit Database"""
        self.log("Running SearchSploit...", "INFO")
        
        if not self.check_tool("searchsploit"):
            self.log("SearchSploit not found - installing...", "WARNING")
            self.run_command("sudo apt install -y exploitdb")
            if not self.check_tool("searchsploit"):
                self.log("SearchSploit not found - skipping", "WARNING")
                return
        
        exploits = {}
        
        # جستجو بر اساس سرویس‌ها
        for service in self.results['services'].get('list', []):
            name = service.get('service', '')
            version = service.get('version', '')
            
            if name and version:
                query = f"{name} {version}"
                self.log(f"Searching exploits for: {query}", "INFO")
                
                stdout, stderr = self.run_command(f"searchsploit {query} --json", timeout=30)
                if stdout:
                    try:
                        data = json.loads(stdout)
                        if data.get('RESULTS_EXPLOIT'):
                            exploits[query] = data['RESULTS_EXPLOIT']
                    except:
                        pass
        
        # جستجوی عمومی
        stdout, stderr = self.run_command(f"searchsploit {self.target}", timeout=30)
        if stdout:
            self.save_text(stdout, "searchsploit.txt")
            exploits['general'] = stdout
        
        self.results['exploits'] = exploits
        self.save_json(exploits, 'exploits.json')
        
        print(f"\n{Fore.MAGENTA}{'='*50}")
        print(f"{Fore.YELLOW}💀 SEARCHSPLOIT RESULTS")
        print(f"{Fore.MAGENTA}{'='*50}")
        
        for service, results in exploits.items():
            if service != 'general':
                print(f"{Fore.CYAN}{service}:")
                if isinstance(results, list):
                    for exp in results[:5]:
                        print(f"  {Fore.GREEN}→ {Fore.WHITE}{exp.get('Title', 'N/A')}")
        
        self.log("SearchSploit completed", "SUCCESS")

    # ========== D. Web Vulnerability Analysis ==========
    
    # 10. Web Scan با Nmap
    def web_nmap_scan(self):
        """اسکن وب با Nmap"""
        self.log("Running Web Nmap Scan...", "INFO")
        
        web_data = {}
        
        # HTTP Scripts
        stdout, stderr = self.run_command(f"nmap -p80,443 --script=http-* {self.target}", timeout=120)
        if stdout:
            web_data['http_scripts'] = stdout
            self.save_text(stdout, "web_nmap.txt")
            
            print(f"\n{Fore.MAGENTA}{'='*50}")
            print(f"{Fore.YELLOW}🌐 WEB NMAP SCAN")
            print(f"{Fore.MAGENTA}{'='*50}")
            
            lines = stdout.split('\n')[:25]
            for line in lines:
                if 'http' in line.lower() or 'title' in line.lower():
                    print(f"  {Fore.WHITE}{line}")
        
        self.results['web_vulns']['nmap'] = web_data
        self.log("Web Nmap scan completed", "SUCCESS")

    # 11. WhatWeb (Technology)
    def web_whatweb(self):
        """شناسایی تکنولوژی وب"""
        self.log("Running WhatWeb...", "INFO")
        
        if not self.check_tool("whatweb"):
            self.log("WhatWeb not found - skipping", "WARNING")
            return
        
        stdout, stderr = self.run_command(f"whatweb -a 3 {self.target}", timeout=30)
        if stdout:
            self.save_text(stdout, "whatweb.txt")
            self.results['web_vulns']['whatweb'] = stdout
            
            print(f"\n{Fore.MAGENTA}{'='*50}")
            print(f"{Fore.YELLOW}🔍 WHATWEB RESULTS")
            print(f"{Fore.MAGENTA}{'='*50}")
            
            lines = stdout.split('\n')[:15]
            for line in lines:
                if line.strip():
                    print(f"  {Fore.WHITE}{line}")

    # 12. Wafw00f
    def web_wafw00f(self):
        """تشخیص WAF"""
        self.log("Running Wafw00f...", "INFO")
        
        if not self.check_tool("wafw00f"):
            self.log("Wafw00f not found - skipping", "WARNING")
            return
        
        stdout, stderr = self.run_command(f"wafw00f {self.target}", timeout=30)
        if stdout:
            self.save_text(stdout, "wafw00f.txt")
            self.results['web_vulns']['wafw00f'] = stdout
            
            print(f"\n{Fore.MAGENTA}{'='*50}")
            print(f"{Fore.YELLOW}🛡️ WAFW00F RESULTS")
            print(f"{Fore.MAGENTA}{'='*50}")
            
            for line in stdout.split('\n'):
                if 'WAF' in line or 'detected' in line:
                    print(f"  {Fore.WHITE}{line}")

    # ========== 13. Final Report ==========
    def final_report(self):
        """گزارش نهایی"""
        print(f"\n{Fore.GREEN}{'='*70}")
        print(f"{Fore.RED}{Style.BRIGHT}✅ SCANNING & VULNERABILITY ANALYSIS COMPLETE")
        print(f"{Fore.GREEN}{'='*70}")
        
        print(f"\n{Fore.CYAN}📊 SUMMARY REPORT")
        print(f"{Fore.CYAN}{'-'*50}")
        
        print(f"{Fore.WHITE}Target: {Fore.YELLOW}{self.target}")
        print(f"{Fore.WHITE}Date: {Fore.YELLOW}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{Fore.WHITE}Output: {Fore.YELLOW}{self.output_dir}")
        
        print(f"\n{Fore.WHITE}Results:")
        
        # Open Ports
        open_ports = self.results['ports'].get('open', [])
        print(f"  {Fore.CYAN}Open Ports: {Fore.WHITE}{len(open_ports)}")
        
        # Services
        services = self.results['services'].get('list', [])
        if services:
            print(f"  {Fore.CYAN}Services: {Fore.WHITE}{len(services)}")
            for svc in services[:5]:
                print(f"    → {svc.get('port')}: {svc.get('service')} {svc.get('version', '')}")
        
        # CVEs
        cves = self.results['vulnerabilities'].get('cves', [])
        if cves:
            print(f"  {Fore.CYAN}CVEs Found: {Fore.WHITE}{len(cves)}")
            for cve in list(set(cves))[:10]:
                print(f"    → {cve}")
        
        # Exploits
        exploits = self.results['exploits']
        if exploits:
            print(f"  {Fore.CYAN}Exploits Found: {Fore.WHITE}{len(exploits)}")
        
        # خلاصه
        summary = {
            'target': self.target,
            'timestamp': datetime.now().isoformat(),
            'statistics': {
                'open_ports': len(open_ports),
                'services': len(services),
                'cves': len(set(cves)),
                'exploits': len(exploits)
            },
            'open_ports': open_ports,
            'services': services[:10],
            'cves': list(set(cves))[:20],
            'files': os.listdir(self.output_dir)
        }
        
        self.save_json(summary, 'summary.json')
        
        print(f"\n{Fore.GREEN}📁 All results saved to: {self.output_dir}")
        print(f"{Fore.GREEN}{'='*70}\n")

    # ========== 14. Run Full ==========
    def run_full(self):
        """اجرای کامل"""
        self.log("🚀 Starting Full Scanning & Vulnerability Analysis", "CRITICAL")
        
        start_time = time.time()
        
        # A. Network Scanning
        self.network_scan()
        
        # B. Port & Service Scanning
        self.port_scan_basic()
        self.port_scan_full()
        self.service_detection()
        self.os_detection()
        
        # C. Vulnerability Scanning
        self.nmap_nse_vuln()
        self.nikto_scan()
        self.nuclei_scan()
        self.searchsploit()
        
        # D. Web Vulnerability Analysis
        self.web_nmap_scan()
        self.web_whatweb()
        self.web_wafw00f()
        
        self.final_report()
        
        elapsed = time.time() - start_time
        print(f"{Fore.CYAN}⏱️  Total time: {elapsed:.2f} seconds")

    def run_quick(self):
        """اجرای سریع"""
        self.log("🚀 Starting Quick Scanning & Vulnerability Analysis", "CRITICAL")
        
        start_time = time.time()
        
        self.port_scan_basic()
        self.service_detection()
        self.nmap_nse_vuln()
        self.searchsploit()
        self.web_nmap_scan()
        
        self.final_report()
        
        elapsed = time.time() - start_time
        print(f"{Fore.CYAN}⏱️  Total time: {elapsed:.2f} seconds")

# ==================== Main ====================
def main():
    if len(sys.argv) < 2:
        print(f"""
{Fore.CYAN}████████ SCANNING & VULNERABILITY ANALYSIS TOOL v1.0 ████████
{Fore.YELLOW}
Usage:
  python3 scan_vuln.py <target>        # Full scan
  python3 scan_vuln.py <target> --quick # Quick scan

{Fore.GREEN}Examples:
  python3 scan_vuln.py 192.168.1.10
  python3 scan_vuln.py example.com
  python3 scan_vuln.py 192.168.1.10 --quick

{Fore.CYAN}Tools Used:
  A. Network Scanning:
  • nmap (ping sweep, arp-scan, netdiscover)
  
  B. Port & Service Scanning:
  • nmap (port scan, service detection, OS detection)
  
  C. Vulnerability Scanning:
  • nmap NSE (vuln scripts)
  • nikto (web server scanner)
  • nuclei (template-based scanner)
  • searchsploit (exploit database)
  
  D. Web Vulnerability Analysis:
  • nmap (http scripts)
  • whatweb (technology detection)
  • wafw00f (WAF detection)

{Fore.YELLOW}⚠️  Use only on authorized targets!
{Fore.RESET}""")
        sys.exit(1)
    
    target = sys.argv[1]
    quick_mode = '--quick' in sys.argv
    
    recon = KaliScanVuln(target)
    
    if quick_mode:
        recon.run_quick()
    else:
        recon.run_full()

if __name__ == "__main__":
    main()