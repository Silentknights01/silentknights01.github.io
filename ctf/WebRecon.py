#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
████████ ULTIMATE WEB RECON TOOL v1.0 ████████
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
class KaliWebRecon:
    def __init__(self, target: str):
        # پاکسازی target
        self.target = target.replace('http://', '').replace('https://', '').strip('/')
        self.url = f"http://{self.target}"
        self.https_url = f"https://{self.target}"
        
        self.results = {
            'target': self.target,
            'timestamp': datetime.now().isoformat(),
            'whatweb': {},
            'wafw00f': {},
            'nikto': '',
            'gobuster': {},
            'ffuf': {},
            'dirb': '',
            'dirsearch': '',
            'curl': {},
            'headers': {},
            'robots': '',
            'sitemap': '',
            'technologies': set(),
            'directories': set(),
            'files': set(),
            'parameters': set()
        }
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = f"web_recon_{self.target}_{self.timestamp}"
        
        os.makedirs(self.output_dir, exist_ok=True)
        
        print(f"{Fore.CYAN}{'='*70}")
        print(f"{Fore.BLUE}{Style.BRIGHT}🌐 WEB RECON TOOL v1.0")
        print(f"{Fore.CYAN}{'='*70}")
        print(f"{Fore.GREEN}📌 Target: {self.target}")
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

    # ========== 1. WhatWeb - Technology Fingerprinting ==========
    def whatweb_scan(self):
        """شناسایی تکنولوژی‌های وب‌سایت با WhatWeb"""
        self.log("Running WhatWeb (Technology Fingerprinting)...", "INFO")
        
        if not self.check_tool("whatweb"):
            self.log("WhatWeb not found - installing...", "WARNING")
            self.run_command("sudo apt install -y whatweb")
            if not self.check_tool("whatweb"):
                self.log("WhatWeb installation failed", "ERROR")
                return
        
        # اسکن با WhatWeb
        stdout, stderr = self.run_command(f"whatweb -a 3 {self.url}", timeout=60)
        
        if stdout:
            self.save_text(stdout, "whatweb.txt")
            
            # استخراج اطلاعات
            techs = set()
            
            # تشخیص تکنولوژی‌ها
            tech_patterns = {
                'Server': r'Server:([^,\]]+)',
                'CMS': r'WordPress|Joomla|Drupal|Magento|Shopify|Wix|Squarespace',
                'Framework': r'Laravel|Django|Rails|Spring|Express|Flask|ASP\.NET',
                'JS': r'jQuery|React|Angular|Vue|Bootstrap|Tailwind',
                'Language': r'PHP|Python|Ruby|Java|JavaScript|C#',
                'Database': r'MySQL|PostgreSQL|MongoDB|MariaDB|SQLite'
            }
            
            for category, pattern in tech_patterns.items():
                matches = re.findall(pattern, stdout, re.IGNORECASE)
                if matches:
                    for match in matches:
                        if match and match.strip():
                            techs.add(f"{category}: {match.strip()}")
            
            self.results['whatweb'] = {
                'raw': stdout,
                'technologies': list(techs)
            }
            self.results['technologies'].update(techs)
            
            print(f"\n{Fore.MAGENTA}{'='*50}")
            print(f"{Fore.YELLOW}🔍 WHATWEB RESULTS")
            print(f"{Fore.MAGENTA}{'='*50}")
            
            if techs:
                for tech in sorted(techs):
                    print(f"  {Fore.GREEN}✓ {Fore.WHITE}{tech}")
            else:
                # نمایش خروجی خام
                lines = stdout.split('\n')[:10]
                for line in lines:
                    if line.strip():
                        print(f"  {Fore.WHITE}{line}")
            
            self.save_json(self.results['whatweb'], 'whatweb.json')
            self.log("WhatWeb completed", "SUCCESS")
        else:
            self.log("WhatWeb failed - no output", "ERROR")

    # ========== 2. Wafw00f - WAF Detection ==========
    def wafw00f_scan(self):
        """تشخیص WAF با Wafw00f"""
        self.log("Running Wafw00f (WAF Detection)...", "INFO")
        
        if not self.check_tool("wafw00f"):
            self.log("Wafw00f not found - installing...", "WARNING")
            self.run_command("sudo apt install -y wafw00f")
            if not self.check_tool("wafw00f"):
                self.log("Wafw00f installation failed", "ERROR")
                return
        
        stdout, stderr = self.run_command(f"wafw00f {self.url}", timeout=30)
        
        if stdout:
            self.save_text(stdout, "wafw00f.txt")
            
            # استخراج اطلاعات
            waf_data = {}
            
            # تشخیص WAF
            waf_match = re.search(r'\[.*?\]\s*(.+?)(?:\n|$)', stdout)
            if waf_match:
                waf_data['waf'] = waf_match.group(1).strip()
            
            # تشخیص Generic Detection
            if 'No WAF detected' in stdout:
                waf_data['status'] = 'No WAF detected'
            elif 'Cloudflare' in stdout:
                waf_data['status'] = 'Cloudflare detected'
            elif 'AWS' in stdout or 'Amazon' in stdout:
                waf_data['status'] = 'AWS WAF detected'
            else:
                waf_data['status'] = 'Unknown WAF'
            
            self.results['wafw00f'] = waf_data
            
            print(f"\n{Fore.MAGENTA}{'='*50}")
            print(f"{Fore.YELLOW}🛡️ WAFW00F RESULTS")
            print(f"{Fore.MAGENTA}{'='*50}")
            
            if waf_data.get('status'):
                status = waf_data['status']
                if 'No WAF' in status:
                    print(f"  {Fore.GREEN}✓ {Fore.WHITE}No WAF detected")
                else:
                    print(f"  {Fore.RED}⚠️ {Fore.WHITE}{status}")
            
            if waf_data.get('waf'):
                print(f"  {Fore.CYAN}WAF: {Fore.WHITE}{waf_data['waf']}")
            
            self.save_json(waf_data, 'wafw00f.json')
            self.log("Wafw00f completed", "SUCCESS")

    # ========== 3. Nikto - Web Server Scanner ==========
    def nikto_scan(self):
        """اسکن وب‌سرور با Nikto"""
        self.log("Running Nikto (Web Server Scanner)...", "INFO")
        
        if not self.check_tool("nikto"):
            self.log("Nikto not found - installing...", "WARNING")
            self.run_command("sudo apt install -y nikto")
            if not self.check_tool("nikto"):
                self.log("Nikto installation failed", "ERROR")
                return
        
        stdout, stderr = self.run_command(f"nikto -h {self.url} -ssl", timeout=120)
        
        if stdout:
            self.save_text(stdout, "nikto.txt")
            self.results['nikto'] = stdout
            
            print(f"\n{Fore.MAGENTA}{'='*50}")
            print(f"{Fore.YELLOW}🔍 NIKTO RESULTS")
            print(f"{Fore.MAGENTA}{'='*50}")
            
            # نمایش یافته‌های مهم
            findings = []
            for line in stdout.split('\n'):
                if '+ ' in line:
                    findings.append(line.strip())
            
            if findings:
                print(f"{Fore.CYAN}Findings:")
                for finding in findings[:20]:
                    print(f"  {Fore.YELLOW}→ {Fore.WHITE}{finding}")
                if len(findings) > 20:
                    print(f"  {Fore.YELLOW}... and {len(findings)-20} more findings")
            else:
                lines = stdout.split('\n')[:15]
                for line in lines:
                    if line.strip():
                        print(f"  {Fore.WHITE}{line}")
            
            self.log("Nikto completed", "SUCCESS")
        else:
            self.log("Nikto failed - no output", "ERROR")

    # ========== 4. Gobuster - Directory/File Enumeration ==========
    def gobuster_scan(self):
        """پیدا کردن دایرکتوری و فایل‌ها با Gobuster"""
        self.log("Running Gobuster (Directory Enumeration)...", "INFO")
        
        if not self.check_tool("gobuster"):
            self.log("Gobuster not found - installing...", "WARNING")
            self.run_command("sudo apt install -y gobuster")
            if not self.check_tool("gobuster"):
                self.log("Gobuster installation failed", "ERROR")
                return
        
        # Wordlist
        wordlist = "/usr/share/wordlists/dirb/common.txt"
        if not os.path.exists(wordlist):
            wordlist = "/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt"
        
        if not os.path.exists(wordlist):
            self.log("No wordlist found - skipping Gobuster", "WARNING")
            return
        
        # اسکن دایرکتوری
        stdout, stderr = self.run_command(
            f"gobuster dir -u {self.url} -w {wordlist} -t 50 -q", timeout=120
        )
        
        if stdout:
            self.save_text(stdout, "gobuster.txt")
            self.results['gobuster']['directories'] = stdout
            
            # استخراج دایرکتوری‌ها
            dirs = re.findall(r'/([^/\s]+)\s+\(', stdout)
            for d in dirs:
                if d and not d.startswith('.'):
                    self.results['directories'].add(d)
            
            print(f"\n{Fore.MAGENTA}{'='*50}")
            print(f"{Fore.YELLOW}📂 GOBUSTER RESULTS")
            print(f"{Fore.MAGENTA}{'='*50}")
            
            if self.results['directories']:
                print(f"{Fore.CYAN}Directories Found:")
                for d in sorted(self.results['directories'])[:20]:
                    print(f"  {Fore.GREEN}✓ {Fore.WHITE}/{d}")
                if len(self.results['directories']) > 20:
                    print(f"  {Fore.YELLOW}... and {len(self.results['directories'])-20} more")
            else:
                lines = stdout.split('\n')[:15]
                for line in lines:
                    if line.strip():
                        print(f"  {Fore.WHITE}{line}")
            
            self.log("Gobuster completed", "SUCCESS")
        
        # اسکن فایل با پسوند
        self.log("Gobuster - File Discovery...", "INFO")
        stdout, stderr = self.run_command(
            f"gobuster dir -u {self.url} -w {wordlist} -x php,txt,html,js,json,xml -t 50 -q", timeout=120
        )
        
        if stdout:
            self.save_text(stdout, "gobuster_files.txt")
            self.results['gobuster']['files'] = stdout
            
            # استخراج فایل‌ها
            files = re.findall(r'/([^/\s]+)\.(php|txt|html|js|json|xml)\s+\(', stdout)
            for f, ext in files:
                if f:
                    self.results['files'].add(f"{f}.{ext}")
            
            print(f"\n{Fore.CYAN}Files Found:")
            for f in sorted(self.results['files'])[:20]:
                print(f"  {Fore.GREEN}✓ {Fore.WHITE}/{f}")
            if len(self.results['files']) > 20:
                print(f"  {Fore.YELLOW}... and {len(self.results['files'])-20} more")
        
        self.save_json(self.results['gobuster'], 'gobuster.json')

    # ========== 5. FFUF - Web Fuzzing ==========
    def ffuf_scan(self):
        """Fuzzing با FFUF"""
        self.log("Running FFUF (Web Fuzzing)...", "INFO")
        
        if not self.check_tool("ffuf"):
            self.log("FFUF not found - installing...", "WARNING")
            self.run_command("sudo apt install -y ffuf")
            if not self.check_tool("ffuf"):
                self.log("FFUF installation failed", "ERROR")
                return
        
        # Wordlist
        wordlist = "/usr/share/wordlists/dirb/common.txt"
        if not os.path.exists(wordlist):
            wordlist = "/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt"
        
        if not os.path.exists(wordlist):
            self.log("No wordlist found - skipping FFUF", "WARNING")
            return
        
        # Directory Fuzzing
        self.log("FFUF - Directory Fuzzing...", "INFO")
        stdout, stderr = self.run_command(
            f"ffuf -u {self.url}/FUZZ -w {wordlist} -fc 404,403 -t 50 -s", timeout=120
        )
        
        if stdout:
            self.save_text(stdout, "ffuf_directories.txt")
            self.results['ffuf']['directories'] = stdout
            
            # استخراج دایرکتوری‌ها
            dirs = re.findall(r'/([^/]+)\s+.*?Status: 200', stdout)
            for d in dirs:
                if d:
                    self.results['directories'].add(d)
            
            print(f"\n{Fore.MAGENTA}{'='*50}")
            print(f"{Fore.YELLOW}🔍 FFUF DIRECTORY RESULTS")
            print(f"{Fore.MAGENTA}{'='*50}")
            
            if self.results['directories']:
                print(f"{Fore.CYAN}Directories Found:")
                for d in sorted(self.results['directories'])[:20]:
                    print(f"  {Fore.GREEN}✓ {Fore.WHITE}/{d}")
        
        # File Fuzzing با پسوند
        self.log("FFUF - File Fuzzing...", "INFO")
        stdout, stderr = self.run_command(
            f"ffuf -u {self.url}/FUZZ -w {wordlist} -e .php,.txt,.html,.js,.json,.xml -fc 404,403 -t 50 -s", timeout=120
        )
        
        if stdout:
            self.save_text(stdout, "ffuf_files.txt")
            self.results['ffuf']['files'] = stdout
            
            # استخراج فایل‌ها
            files = re.findall(r'/([^/\s]+)\.(php|txt|html|js|json|xml)\s+.*?Status: 200', stdout)
            for f, ext in files:
                if f:
                    self.results['files'].add(f"{f}.{ext}")
            
            print(f"\n{Fore.CYAN}Files Found:")
            for f in sorted(self.results['files'])[:20]:
                print(f"  {Fore.GREEN}✓ {Fore.WHITE}/{f}")
        
        self.save_json(self.results['ffuf'], 'ffuf.json')
        self.log("FFUF completed", "SUCCESS")

    # ========== 6. DIRB ==========
    def dirb_scan(self):
        """اسکن دایرکتوری با DIRB"""
        self.log("Running DIRB...", "INFO")
        
        if not self.check_tool("dirb"):
            self.log("DIRB not found - installing...", "WARNING")
            self.run_command("sudo apt install -y dirb")
            if not self.check_tool("dirb"):
                self.log("DIRB not found - skipping", "WARNING")
                return
        
        stdout, stderr = self.run_command(f"dirb {self.url} -r -z 10", timeout=120)
        
        if stdout:
            self.save_text(stdout, "dirb.txt")
            self.results['dirb'] = stdout
            
            print(f"\n{Fore.MAGENTA}{'='*50}")
            print(f"{Fore.YELLOW}📂 DIRB RESULTS")
            print(f"{Fore.MAGENTA}{'='*50}")
            
            # استخراج دایرکتوری‌ها
            dirs = re.findall(r'==> DIRECTORY: http://[^/]+/([^/\s]+)/', stdout)
            for d in dirs:
                if d:
                    self.results['directories'].add(d)
            
            if self.results['directories']:
                print(f"{Fore.CYAN}Directories Found:")
                for d in sorted(self.results['directories'])[:20]:
                    print(f"  {Fore.GREEN}✓ {Fore.WHITE}/{d}")
            else:
                lines = stdout.split('\n')[:15]
                for line in lines:
                    if line.strip():
                        print(f"  {Fore.WHITE}{line}")
            
            self.log("DIRB completed", "SUCCESS")

    # ========== 7. Dirsearch ==========
    def dirsearch_scan(self):
        """اسکن دایرکتوری با Dirsearch"""
        self.log("Running Dirsearch...", "INFO")
        
        if not self.check_tool("dirsearch"):
            self.log("Dirsearch not found - installing...", "WARNING")
            self.run_command("sudo apt install -y dirsearch")
            if not self.check_tool("dirsearch"):
                self.log("Dirsearch not found - skipping", "WARNING")
                return
        
        stdout, stderr = self.run_command(
            f"dirsearch -u {self.url} -e php,txt,html,js --simple-report={self.output_dir}/dirsearch.txt",
            timeout=120
        )
        
        # خواندن فایل گزارش
        try:
            with open(f"{self.output_dir}/dirsearch.txt", 'r') as f:
                stdout = f.read()
                self.results['dirsearch'] = stdout
                
                print(f"\n{Fore.MAGENTA}{'='*50}")
                print(f"{Fore.YELLOW}📂 DIRSEARCH RESULTS")
                print(f"{Fore.MAGENTA}{'='*50}")
                
                # استخراج نتایج
                paths = re.findall(r'Status: \d+.*?Size: \d+.*?http://[^/]+(/.+)', stdout)
                for path in paths[:20]:
                    print(f"  {Fore.GREEN}✓ {Fore.WHITE}{path}")
        except:
            pass
        
        self.log("Dirsearch completed", "SUCCESS")

    # ========== 8. CURL - Headers & Files ==========
    def curl_scan(self):
        """بررسی با CURL"""
        self.log("Running CURL checks...", "INFO")
        
        # دریافت هدرها
        stdout, stderr = self.run_command(f"curl -I -L -s {self.url}", timeout=30)
        if stdout:
            self.save_text(stdout, "headers.txt")
            self.results['headers']['http'] = stdout
            
            # استخراج اطلاعات
            server = re.search(r'Server:\s*(.+)', stdout, re.IGNORECASE)
            if server:
                self.results['technologies'].add(f"Server: {server.group(1).strip()}")
            
            x_powered = re.search(r'X-Powered-By:\s*(.+)', stdout, re.IGNORECASE)
            if x_powered:
                self.results['technologies'].add(f"Framework: {x_powered.group(1).strip()}")
            
            print(f"\n{Fore.MAGENTA}{'='*50}")
            print(f"{Fore.YELLOW}📡 HTTP HEADERS")
            print(f"{Fore.MAGENTA}{'='*50}")
            
            lines = stdout.split('\n')[:15]
            for line in lines:
                if line.strip():
                    print(f"  {Fore.WHITE}{line}")
        
        # دریافت robots.txt
        stdout, stderr = self.run_command(f"curl -s -L {self.url}/robots.txt", timeout=30)
        if stdout and 'User-agent' in stdout:
            self.save_text(stdout, "robots.txt")
            self.results['robots'] = stdout
            
            print(f"\n{Fore.MAGENTA}{'='*50}")
            print(f"{Fore.YELLOW}🤖 ROBOTS.TXT")
            print(f"{Fore.MAGENTA}{'='*50}")
            lines = stdout.split('\n')[:10]
            for line in lines:
                if line.strip():
                    print(f"  {Fore.WHITE}{line}")
        
        # دریافت sitemap.xml
        stdout, stderr = self.run_command(f"curl -s -L {self.url}/sitemap.xml", timeout=30)
        if stdout and '<urlset' in stdout:
            self.save_text(stdout, "sitemap.xml")
            self.results['sitemap'] = stdout
            
            print(f"\n{Fore.MAGENTA}{'='*50}")
            print(f"{Fore.YELLOW}🗺️ SITEMAP.XML")
            print(f"{Fore.MAGENTA}{'='*50}")
            lines = stdout.split('\n')[:10]
            for line in lines:
                if line.strip():
                    print(f"  {Fore.WHITE}{line}")
        
        self.log("CURL completed", "SUCCESS")

    # ========== 9. Final Report ==========
    def final_report(self):
        """گزارش نهایی"""
        print(f"\n{Fore.GREEN}{'='*70}")
        print(f"{Fore.BLUE}{Style.BRIGHT}✅ WEB RECON COMPLETE")
        print(f"{Fore.GREEN}{'='*70}")
        
        print(f"\n{Fore.CYAN}📊 SUMMARY REPORT")
        print(f"{Fore.CYAN}{'-'*50}")
        
        print(f"{Fore.WHITE}Target: {Fore.YELLOW}{self.target}")
        print(f"{Fore.WHITE}Date: {Fore.YELLOW}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{Fore.WHITE}Output: {Fore.YELLOW}{self.output_dir}")
        
        print(f"\n{Fore.WHITE}Results:")
        
        # تکنولوژی‌ها
        if self.results['technologies']:
            print(f"  {Fore.CYAN}Technologies: {Fore.WHITE}{len(self.results['technologies'])}")
            for tech in sorted(self.results['technologies'])[:10]:
                print(f"    → {tech}")
        
        # دایرکتوری‌ها
        if self.results['directories']:
            print(f"  {Fore.CYAN}Directories: {Fore.WHITE}{len(self.results['directories'])}")
            for d in sorted(self.results['directories'])[:10]:
                print(f"    → /{d}")
        
        # فایل‌ها
        if self.results['files']:
            print(f"  {Fore.CYAN}Files: {Fore.WHITE}{len(self.results['files'])}")
            for f in sorted(self.results['files'])[:10]:
                print(f"    → /{f}")
        
        # WAF
        if self.results['wafw00f']:
            waf_status = self.results['wafw00f'].get('status', 'Unknown')
            print(f"  {Fore.CYAN}WAF: {Fore.WHITE}{waf_status}")
        
        # خلاصه
        summary = {
            'target': self.target,
            'timestamp': datetime.now().isoformat(),
            'statistics': {
                'technologies': len(self.results['technologies']),
                'directories': len(self.results['directories']),
                'files': len(self.results['files']),
                'waf': self.results['wafw00f'].get('status', 'Unknown')
            },
            'technologies': list(self.results['technologies']),
            'directories': list(self.results['directories']),
            'files': list(self.results['files']),
            'files': os.listdir(self.output_dir)
        }
        
        self.save_json(summary, 'summary.json')
        
        print(f"\n{Fore.GREEN}📁 All results saved to: {self.output_dir}")
        print(f"{Fore.GREEN}{'='*70}\n")

    # ========== 10. Run Full ==========
    def run_full_recon(self):
        """اجرای کامل Web Recon"""
        self.log("🚀 Starting Full Web Reconnaissance", "CRITICAL")
        
        start_time = time.time()
        
        # مرحله 1: WhatWeb
        self.whatweb_scan()
        
        # مرحله 2: Wafw00f
        self.wafw00f_scan()
        
        # مرحله 3: Nikto
        self.nikto_scan()
        
        # مرحله 4: Gobuster
        self.gobuster_scan()
        
        # مرحله 5: FFUF
        self.ffuf_scan()
        
        # مرحله 6: DIRB
        self.dirb_scan()
        
        # مرحله 7: Dirsearch
        self.dirsearch_scan()
        
        # مرحله 8: CURL
        self.curl_scan()
        
        # مرحله 9: Report
        self.final_report()
        
        elapsed = time.time() - start_time
        print(f"{Fore.CYAN}⏱️  Total time: {elapsed:.2f} seconds")

    def run_quick(self):
        """اجرای سریع Web Recon"""
        self.log("🚀 Starting Quick Web Reconnaissance", "CRITICAL")
        
        start_time = time.time()
        
        self.whatweb_scan()
        self.wafw00f_scan()
        self.gobuster_scan()
        self.ffuf_scan()
        self.curl_scan()
        self.final_report()
        
        elapsed = time.time() - start_time
        print(f"{Fore.CYAN}⏱️  Total time: {elapsed:.2f} seconds")

# ==================== Main ====================
def main():
    if len(sys.argv) < 2:
        print(f"""
{Fore.CYAN}████████ WEB RECON TOOL v1.0 ████████
{Fore.YELLOW}
Usage:
  python3 web_recon.py <url>        # Full web recon
  python3 web_recon.py <url> --quick # Quick web recon

{Fore.GREEN}Examples:
  python3 web_recon.py example.com
  python3 web_recon.py 192.168.1.10
  python3 web_recon.py example.com --quick

{Fore.CYAN}Tools Used (Kali System Tools):
  • whatweb    - Technology fingerprinting
  • wafw00f    - WAF detection
  • nikto      - Web server scanner
  • gobuster   - Directory/file enumeration
  • ffuf       - Web fuzzing
  • dirb       - Directory enumeration
  • dirsearch  - Directory/file enumeration
  • curl       - HTTP headers & files

{Fore.YELLOW}⚠️  Use only on authorized targets!
{Fore.RESET}""")
        sys.exit(1)
    
    target = sys.argv[1]
    quick_mode = '--quick' in sys.argv
    
    recon = KaliWebRecon(target)
    
    if quick_mode:
        recon.run_quick()
    else:
        recon.run_full_recon()

if __name__ == "__main__":
    main()