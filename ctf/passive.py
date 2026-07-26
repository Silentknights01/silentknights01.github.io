#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
████████ ULTIMATE PASSIVE RECON TOOL v7.0 ████████
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
class KaliPassiveRecon:
    def __init__(self, target: str):
        self.target = target
        self.results = {
            'target': target,
            'timestamp': datetime.now().isoformat(),
            'whois': {},
            'dns': {},
            'subdomains': set(),
            'emails': set(),
            'ips': set(),
            'technologies': set(),
            'ssl_info': {},
            'google_dorks': [],
            'cloud_detection': set()
        }
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = f"passive_recon_{target}_{self.timestamp}"
        
        os.makedirs(self.output_dir, exist_ok=True)
        
        print(f"{Fore.CYAN}{'='*70}")
        print(f"{Fore.YELLOW}{Style.BRIGHT}🔍 KALI PASSIVE RECON TOOL v7.0")
        print(f"{Fore.CYAN}{'='*70}")
        print(f"{Fore.GREEN}📌 Target: {target}")
        print(f"{Fore.GREEN}📁 Output: {self.output_dir}")
        print(f"{Fore.GREEN}⏱️  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
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

    # ========== 1. WHOIS (ابزار سیستمی) ==========
    def whois_analysis(self):
        """WHOIS با ابزار سیستمی whois"""
        self.log("Running WHOIS (system tool)...", "INFO")
        
        stdout, stderr = self.run_command(f"whois {self.target}")
        
        if stdout:
            self.save_text(stdout, "whois_raw.txt")
            
            # استخراج اطلاعات کلیدی
            whois_data = {}
            patterns = {
                'domain_name': r'Domain Name:\s*(.+)',
                'registrar': r'Registrar:\s*(.+)',
                'creation_date': r'Creation Date:\s*(.+)',
                'expiration_date': r'Expiry Date:\s*(.+)|Expiration Date:\s*(.+)',
                'updated_date': r'Updated Date:\s*(.+)',
                'name_servers': r'Name Server:\s*(.+)',
                'org': r'OrgName:\s*(.+)|Organization:\s*(.+)',
                'country': r'Country:\s*(.+)',
                'state': r'State/Province:\s*(.+)',
                'city': r'City:\s*(.+)',
                'emails': r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                'status': r'Status:\s*(.+)'
            }
            
            for key, pattern in patterns.items():
                matches = re.findall(pattern, stdout, re.IGNORECASE)
                if matches:
                    if key == 'name_servers':
                        whois_data[key] = [m.strip() for m in matches if m]
                    elif key == 'emails':
                        whois_data[key] = list(set(matches))
                    else:
                        whois_data[key] = matches[0][0] if isinstance(matches[0], tuple) else matches[0].strip()
            
            self.results['whois'] = whois_data
            
            # نمایش
            print(f"\n{Fore.MAGENTA}{'='*50}")
            print(f"{Fore.YELLOW}📋 WHOIS INFORMATION")
            print(f"{Fore.MAGENTA}{'='*50}")
            
            print(f"{Fore.CYAN}Domain: {Fore.WHITE}{whois_data.get('domain_name', 'N/A')}")
            print(f"{Fore.CYAN}Registrar: {Fore.WHITE}{whois_data.get('registrar', 'N/A')}")
            print(f"{Fore.CYAN}Created: {Fore.WHITE}{whois_data.get('creation_date', 'N/A')}")
            print(f"{Fore.CYAN}Expires: {Fore.WHITE}{whois_data.get('expiration_date', 'N/A')}")
            
            if whois_data.get('name_servers'):
                print(f"{Fore.CYAN}Name Servers: {Fore.WHITE}{', '.join(whois_data['name_servers'][:5])}")
            
            print(f"{Fore.CYAN}Organization: {Fore.WHITE}{whois_data.get('org', 'N/A')}")
            print(f"{Fore.CYAN}Country: {Fore.WHITE}{whois_data.get('country', 'N/A')}")
            
            if whois_data.get('emails'):
                print(f"{Fore.CYAN}Emails in WHOIS: {Fore.WHITE}{', '.join(whois_data['emails'][:3])}")
                for email in whois_data['emails']:
                    self.results['emails'].add(email)
            
            self.save_json(whois_data, 'whois.json')
            self.log("WHOIS completed", "SUCCESS")
        else:
            self.log("WHOIS failed - no output", "ERROR")

    # ========== 2. DNS (ابزار dig) ==========
    def dns_analysis(self):
        """DNS با ابزار سیستمی dig"""
        self.log("Running DNS analysis (dig)...", "INFO")
        
        record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA', 'SRV']
        dns_results = {}
        
        for rtype in record_types:
            stdout, stderr = self.run_command(f"dig {self.target} {rtype} +short")
            if stdout.strip():
                dns_results[rtype] = [line.strip() for line in stdout.split('\n') if line.strip()]
                
                # استخراج IP از A record
                if rtype == 'A':
                    for ip in dns_results[rtype]:
                        if ip:
                            self.results['ips'].add(ip)
                
                # استخراج ایمیل از TXT
                if rtype == 'TXT':
                    for txt in dns_results[rtype]:
                        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', txt)
                        for email in emails:
                            self.results['emails'].add(email)
                        # تشخیص فناوری‌ها
                        if 'v=spf1' in txt.lower():
                            self.results['technologies'].add('SPF')
                        if 'dkim' in txt.lower():
                            self.results['technologies'].add('DKIM')
                        if 'dmarc' in txt.lower():
                            self.results['technologies'].add('DMARC')
                
                # استخراج IP از MX
                if rtype == 'MX':
                    for mx in dns_results[rtype]:
                        parts = mx.split()
                        if len(parts) >= 2:
                            mx_domain = parts[1]
                            mx_stdout, _ = self.run_command(f"dig {mx_domain} A +short")
                            for mx_ip in mx_stdout.split('\n'):
                                if mx_ip.strip():
                                    self.results['ips'].add(mx_ip.strip())
        
        self.results['dns'] = dns_results
        
        print(f"\n{Fore.MAGENTA}{'='*50}")
        print(f"{Fore.YELLOW}🌐 DNS RECORDS")
        print(f"{Fore.MAGENTA}{'='*50}")
        
        for rtype, records in dns_results.items():
            if records:
                print(f"\n{Fore.CYAN}[{rtype}]")
                for record in records[:10]:
                    print(f"  {Fore.WHITE}→ {record}")
                if len(records) > 10:
                    print(f"  {Fore.YELLOW}... and {len(records)-10} more")
        
        self.save_json(dns_results, 'dns_records.json')
        self.log("DNS analysis completed", "SUCCESS")

    # ========== 3. Subdomain Discovery (Amass + DNSRecon + crt.sh) ==========
    def subdomain_discovery(self):
        """پیدا کردن زیردامنه‌ها با ابزارهای سیستمی"""
        self.log("Starting Subdomain Discovery...", "INFO")
        
        subdomains = set()
        
        # 1. Amass (Passive)
        if self.check_tool("amass"):
            self.log("Running Amass (passive)...", "INFO")
            stdout, stderr = self.run_command(f"amass enum -passive -d {self.target}", timeout=120)
            if stdout:
                for line in stdout.split('\n'):
                    sub = line.strip()
                    if sub and self.target in sub and sub != self.target:
                        subdomains.add(sub)
                self.log(f"Amass found subdomains", "SUCCESS")
        else:
            self.log("Amass not found - skipping", "WARNING")
        
        # 2. DNSRecon
        if self.check_tool("dnsrecon"):
            self.log("Running DNSRecon...", "INFO")
            stdout, stderr = self.run_command(f"dnsrecon -d {self.target} -t std", timeout=60)
            if stdout:
                for line in stdout.split('\n'):
                    if ' A ' in line or ' CNAME ' in line:
                        parts = line.split()
                        if len(parts) >= 1:
                            sub = parts[0]
                            if sub.endswith(self.target) and sub != self.target:
                                subdomains.add(sub)
                                if len(parts) >= 3 and '.' in parts[2]:
                                    self.results['ips'].add(parts[2])
                self.log("DNSRecon completed", "SUCCESS")
        else:
            self.log("DNSRecon not found - skipping", "WARNING")
        
        # 3. crt.sh (با curl)
        self.log("Getting subdomains from crt.sh...", "INFO")
        stdout, stderr = self.run_command(f"curl -s 'https://crt.sh/?q=%25.{self.target}&output=json'", timeout=15)
        if stdout:
            try:
                data = json.loads(stdout)
                for entry in data:
                    name = entry.get('name_value', '')
                    if name:
                        for sub in name.split('\n'):
                            sub = sub.strip()
                            if sub and self.target in sub:
                                subdomains.add(sub)
                self.log(f"crt.sh found subdomains", "SUCCESS")
            except:
                self.log("crt.sh JSON parse failed", "ERROR")
        else:
            self.log("crt.sh curl failed", "WARNING")
        
        self.results['subdomains'] = subdomains
        
        print(f"\n{Fore.MAGENTA}{'='*50}")
        print(f"{Fore.YELLOW}🎯 SUBDOMAINS FOUND")
        print(f"{Fore.MAGENTA}{'='*50}")
        
        if subdomains:
            for idx, sub in enumerate(sorted(subdomains), 1):
                print(f"{Fore.GREEN}[{idx:3d}] {Fore.WHITE}{sub}")
            print(f"\n{Fore.CYAN}Total: {len(subdomains)} subdomains")
        else:
            print(f"{Fore.YELLOW}No subdomains found")
        
        self.save_text('\n'.join(sorted(subdomains)), 'subdomains.txt')
        self.save_json(list(subdomains), 'subdomains.json')
        
        # Resolve subdomain IPs
        self._resolve_subdomains(subdomains)
        self.log(f"Subdomain discovery completed - {len(subdomains)} found", "SUCCESS")

    def _resolve_subdomains(self, subdomains: Set[str]):
        """حل کردن IP زیردامنه‌ها با dig"""
        self.log("Resolving subdomain IPs...", "INFO")
        
        resolved = {}
        for sub in list(subdomains)[:100]:
            stdout, _ = self.run_command(f"dig {sub} A +short")
            if stdout.strip():
                ip = stdout.strip().split('\n')[0]
                resolved[sub] = ip
                self.results['ips'].add(ip)
        
        self.save_json(resolved, 'subdomain_resolved.json')
        self.log(f"Resolved {len(resolved)} IPs", "SUCCESS")

    # ========== 4. Email Gathering (theHarvester) ==========
    def email_gathering(self):
        """جمع‌آوری ایمیل با theHarvester"""
        self.log("Running theHarvester...", "INFO")
        
        if not self.check_tool("theHarvester"):
            self.log("theHarvester not found - skipping", "WARNING")
            return
        
        stdout, stderr = self.run_command(f"theHarvester -d {self.target} -b google,bing,yahoo", timeout=90)
        
        if stdout:
            email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            emails = re.findall(email_pattern, stdout)
            for email in emails:
                if self.target in email:
                    self.results['emails'].add(email)
            
            # استخراج زیردامنه‌ها از theHarvester
            sub_pattern = r'[a-zA-Z0-9.-]*\.' + re.escape(self.target)
            subs = re.findall(sub_pattern, stdout)
            for sub in subs:
                if sub and sub != self.target:
                    self.results['subdomains'].add(sub)
            
            self.log(f"theHarvester found {len(self.results['emails'])} emails", "SUCCESS")
        
        print(f"\n{Fore.MAGENTA}{'='*50}")
        print(f"{Fore.YELLOW}📧 EMAILS FOUND")
        print(f"{Fore.MAGENTA}{'='*50}")
        
        if self.results['emails']:
            for idx, email in enumerate(sorted(self.results['emails']), 1):
                print(f"{Fore.GREEN}[{idx:3d}] {Fore.WHITE}{email}")
            print(f"\n{Fore.CYAN}Total: {len(self.results['emails'])} emails")
        else:
            print(f"{Fore.YELLOW}No emails found")
        
        self.save_text('\n'.join(sorted(self.results['emails'])), 'emails.txt')
        self.save_json(list(self.results['emails']), 'emails.json')

    # ========== 5. Technology Detection (curl + headers) ==========
    def technology_detection(self):
        """تشخیص فناوری با curl"""
        self.log("Detecting Technologies (curl)...", "INFO")
        
        techs = set()
        
        # دریافت هدرها
        stdout, stderr = self.run_command(f"curl -s -I -L {self.target}")
        if stdout:
            headers = stdout
            self.save_text(headers, 'headers.txt')
            
            # تشخیص از هدرها
            server_match = re.search(r'Server:\s*(.+)', headers, re.IGNORECASE)
            if server_match:
                techs.add(f"Server: {server_match.group(1).strip()}")
            
            powered_match = re.search(r'X-Powered-By:\s*(.+)', headers, re.IGNORECASE)
            if powered_match:
                techs.add(f"Framework: {powered_match.group(1).strip()}")
            
            aspnet_match = re.search(r'X-AspNet-Version:\s*(.+)', headers, re.IGNORECASE)
            if aspnet_match:
                techs.add(f"ASP.NET: {aspnet_match.group(1).strip()}")
        
        # دریافت HTML برای تشخیص
        stdout, stderr = self.run_command(f"curl -s -L {self.target} | head -100")
        if stdout:
            # تشخیص CMS
            cms_patterns = {
                'WordPress': r'wp-content|wp-includes|wordpress',
                'Joomla': r'joomla|com_content',
                'Drupal': r'drupal|sites/all',
                'Laravel': r'laravel|csrf-token',
                'Django': r'django|csrftoken',
                'React': r'react|_reactRoot',
                'Angular': r'ng-app|angular',
                'Vue': r'v-app|vue.js'
            }
            
            for cms, pattern in cms_patterns.items():
                if re.search(pattern, stdout, re.IGNORECASE):
                    techs.add(cms)
        
        self.results['technologies'] = techs
        
        print(f"\n{Fore.MAGENTA}{'='*50}")
        print(f"{Fore.YELLOW}🛠️ TECHNOLOGIES DETECTED")
        print(f"{Fore.MAGENTA}{'='*50}")
        
        if techs:
            for tech in sorted(techs):
                print(f"  {Fore.GREEN}✓ {Fore.WHITE}{tech}")
        else:
            print(f"{Fore.YELLOW}No technologies detected")
        
        self.save_json(list(techs), 'technologies.json')
        self.log("Technology detection completed", "SUCCESS")

    # ========== 6. SSL Analysis (openssl) ==========
    def ssl_analysis(self):
        """تحلیل SSL با openssl"""
        self.log("Analyzing SSL Certificate (openssl)...", "INFO")
        
        if not self.check_tool("openssl"):
            self.log("openssl not found - skipping", "WARNING")
            return
        
        # دریافت گواهی
        stdout, stderr = self.run_command(
            f"echo | openssl s_client -connect {self.target}:443 -servername {self.target} 2>/dev/null | openssl x509 -text"
        )
        
        if stdout:
            self.save_text(stdout, 'ssl_certificate.txt')
            
            ssl_info = {}
            
            # استخراج اطلاعات
            subject_match = re.search(r'Subject:\s*(.+)', stdout)
            if subject_match:
                ssl_info['subject'] = subject_match.group(1).strip()
            
            issuer_match = re.search(r'Issuer:\s*(.+)', stdout)
            if issuer_match:
                ssl_info['issuer'] = issuer_match.group(1).strip()
            
            not_before = re.search(r'Not Before:\s*(.+)', stdout)
            if not_before:
                ssl_info['not_before'] = not_before.group(1).strip()
            
            not_after = re.search(r'Not After :\s*(.+)', stdout)
            if not_after:
                ssl_info['not_after'] = not_after.group(1).strip()
            
            serial = re.search(r'Serial Number:\s*(.+)', stdout)
            if serial:
                ssl_info['serial'] = serial.group(1).strip()
            
            # تشخیص فناوری SSL
            alt_names = re.findall(r'DNS:(.+)', stdout)
            if alt_names:
                ssl_info['alt_names'] = alt_names
            
            self.results['ssl_info'] = ssl_info
            
            print(f"\n{Fore.MAGENTA}{'='*50}")
            print(f"{Fore.YELLOW}🔒 SSL CERTIFICATE")
            print(f"{Fore.MAGENTA}{'='*50}")
            
            print(f"{Fore.CYAN}Subject: {Fore.WHITE}{ssl_info.get('subject', 'N/A')}")
            print(f"{Fore.CYAN}Issuer: {Fore.WHITE}{ssl_info.get('issuer', 'N/A')}")
            print(f"{Fore.CYAN}Not Before: {Fore.WHITE}{ssl_info.get('not_before', 'N/A')}")
            print(f"{Fore.CYAN}Not After: {Fore.WHITE}{ssl_info.get('not_after', 'N/A')}")
            
            self.save_json(ssl_info, 'ssl_info.json')
            self.log("SSL analysis completed", "SUCCESS")
        else:
            self.log("SSL analysis failed - no certificate", "WARNING")

    # ========== 7. Google Dorks ==========
    def google_dorks(self):
        """تولید Google Dorks"""
        self.log("Generating Google Dorks...", "INFO")
        
        dorks = [
            f"site:{self.target}",
            f"site:{self.target} -www",
            f"site:{self.target} filetype:pdf",
            f"site:{self.target} filetype:docx",
            f"site:{self.target} filetype:xlsx",
            f"site:{self.target} filetype:sql",
            f"site:{self.target} filetype:log",
            f"site:{self.target} filetype:conf",
            f"site:{self.target} filetype:ini",
            f"site:{self.target} intitle:admin",
            f"site:{self.target} intitle:login",
            f"site:{self.target} intitle:\"Index of\"",
            f"site:{self.target} inurl:admin",
            f"site:{self.target} inurl:login",
            f"site:{self.target} inurl:config",
            f"site:{self.target} inurl:backup",
            f"site:{self.target} inurl:api",
            f"site:{self.target} inurl:rest",
            f"site:{self.target} inurl:graphql",
            f"site:{self.target} \"username\"",
            f"site:{self.target} \"password\"",
            f"site:{self.target} \"email\"",
            f"site:{self.target} \"@\"",
            f"site:{self.target} \"confidential\"",
            f"site:{self.target} \"secret\"",
            f"site:{self.target} \"powered by\"",
            f"site:{self.target} \"version\"",
            f"site:{self.target} \"Server:\"",
            f"site:*.{self.target} -www",
            f"site:{self.target} \"Parent Directory\"",
            f"site:{self.target} ext:php | ext:asp | ext:jsp"
        ]
        
        self.results['google_dorks'] = dorks
        
        print(f"\n{Fore.MAGENTA}{'='*50}")
        print(f"{Fore.YELLOW}🔍 GOOGLE DORKS")
        print(f"{Fore.MAGENTA}{'='*50}")
        
        content = ""
        for idx, dork in enumerate(dorks, 1):
            url = f"https://www.google.com/search?q={dork.replace(' ', '%20')}"
            content += f"{idx}. {dork}\n   {url}\n\n"
            print(f"{Fore.CYAN}[{idx:2d}] {Fore.WHITE}{dork}")
            print(f"    {Fore.BLUE}→ {url}\n")
        
        self.save_text(content, 'google_dorks.txt')
        self.save_json(dorks, 'google_dorks.json')
        self.log("Google Dorks generated", "SUCCESS")

    # ========== 8. Cloud Detection ==========
    def cloud_detection(self):
        """تشخیص سرویس‌های ابری"""
        self.log("Detecting Cloud Services...", "INFO")
        
        cloud_services = set()
        
        # بررسی از روی IP با whois
        for ip in list(self.results['ips'])[:20]:
            stdout, _ = self.run_command(f"whois {ip}")
            if stdout:
                if 'cloudflare' in stdout.lower():
                    cloud_services.add('Cloudflare')
                if 'amazon' in stdout.lower() or 'aws' in stdout.lower():
                    cloud_services.add('AWS')
                if 'microsoft' in stdout.lower() or 'azure' in stdout.lower():
                    cloud_services.add('Azure')
                if 'google' in stdout.lower() or 'gcp' in stdout.lower():
                    cloud_services.add('GCP')
                if 'digitalocean' in stdout.lower():
                    cloud_services.add('DigitalOcean')
        
        # بررسی از روی DNS با dig
        stdout, _ = self.run_command(f"dig {self.target} A +short")
        if stdout:
            for ip in stdout.split('\n'):
                if ip.strip():
                    whois_out, _ = self.run_command(f"whois {ip.strip()}")
                    if whois_out:
                        if 'cloudflare' in whois_out.lower():
                            cloud_services.add('Cloudflare')
                        elif 'amazon' in whois_out.lower():
                            cloud_services.add('AWS')
                        elif 'microsoft' in whois_out.lower():
                            cloud_services.add('Azure')
                        elif 'google' in whois_out.lower():
                            cloud_services.add('GCP')
        
        self.results['cloud_detection'] = cloud_services
        
        if cloud_services:
            print(f"\n{Fore.MAGENTA}{'='*50}")
            print(f"{Fore.YELLOW}☁️ CLOUD SERVICES DETECTED")
            print(f"{Fore.MAGENTA}{'='*50}")
            for service in cloud_services:
                print(f"  {Fore.GREEN}✓ {Fore.WHITE}{service}")

    # ========== 9. Final Report ==========
    def final_report(self):
        """گزارش نهایی"""
        print(f"\n{Fore.GREEN}{'='*70}")
        print(f"{Fore.YELLOW}{Style.BRIGHT}✅ PASSIVE RECON COMPLETE")
        print(f"{Fore.GREEN}{'='*70}")
        
        print(f"\n{Fore.CYAN}📊 SUMMARY REPORT")
        print(f"{Fore.CYAN}{'-'*50}")
        
        print(f"{Fore.WHITE}Target: {Fore.YELLOW}{self.target}")
        print(f"{Fore.WHITE}Date: {Fore.YELLOW}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{Fore.WHITE}Output: {Fore.YELLOW}{self.output_dir}")
        
        print(f"\n{Fore.WHITE}Results:")
        print(f"  {Fore.CYAN}Subdomains: {Fore.WHITE}{len(self.results['subdomains'])}")
        print(f"  {Fore.CYAN}IPs: {Fore.WHITE}{len(self.results['ips'])}")
        print(f"  {Fore.CYAN}Emails: {Fore.WHITE}{len(self.results['emails'])}")
        print(f"  {Fore.CYAN}Technologies: {Fore.WHITE}{len(self.results['technologies'])}")
        print(f"  {Fore.CYAN}Google Dorks: {Fore.WHITE}{len(self.results['google_dorks'])}")
        
        if self.results['cloud_detection']:
            print(f"  {Fore.CYAN}Cloud Services: {Fore.WHITE}{', '.join(self.results['cloud_detection'])}")
        
        # خلاصه
        summary = {
            'target': self.target,
            'timestamp': datetime.now().isoformat(),
            'statistics': {
                'subdomains': len(self.results['subdomains']),
                'ips': len(self.results['ips']),
                'emails': len(self.results['emails']),
                'technologies': len(self.results['technologies']),
                'google_dorks': len(self.results['google_dorks']),
                'cloud_services': list(self.results['cloud_detection'])
            },
            'files': os.listdir(self.output_dir)
        }
        
        self.save_json(summary, 'summary.json')
        
        print(f"\n{Fore.GREEN}📁 All results saved to: {self.output_dir}")
        print(f"{Fore.GREEN}{'='*70}\n")

    # ========== 10. Run Full ==========
    def run_full_recon(self):
        """اجرای کامل"""
        self.log("🚀 Starting Full Passive Reconnaissance", "CRITICAL")
        
        start_time = time.time()
        
        self.whois_analysis()
        self.dns_analysis()
        self.subdomain_discovery()
        self.email_gathering()
        self.technology_detection()
        self.ssl_analysis()
        self.google_dorks()
        self.cloud_detection()
        self.final_report()
        
        elapsed = time.time() - start_time
        print(f"{Fore.CYAN}⏱️  Total time: {elapsed:.2f} seconds")

    def run_quick(self):
        """اجرای سریع"""
        self.log("🚀 Starting Quick Passive Reconnaissance", "CRITICAL")
        
        start_time = time.time()
        
        self.whois_analysis()
        self.dns_analysis()
        self.subdomain_discovery()
        self.email_gathering()
        self.google_dorks()
        self.final_report()
        
        elapsed = time.time() - start_time
        print(f"{Fore.CYAN}⏱️  Total time: {elapsed:.2f} seconds")

# ==================== Main ====================
def main():
    if len(sys.argv) < 2:
        print(f"""
{Fore.CYAN}████████ KALI PASSIVE RECON TOOL v7.0 ████████
{Fore.YELLOW}
Usage:
  python3 kali_passive.py <domain>        # Full recon
  python3 kali_passive.py <domain> --quick # Quick recon

{Fore.GREEN}Examples:
  python3 kali_passive.py example.com
  python3 kali_passive.py example.com --quick

{Fore.CYAN}Tools Used (Kali System Tools):
  • whois       - Domain registration
  • dig         - DNS records
  • amass       - Subdomain discovery (passive)
  • dnsrecon    - DNS enumeration
  • theHarvester - Email gathering
  • curl        - HTTP headers & content
  • openssl     - SSL certificate analysis

{Fore.YELLOW}⚠️  No Python packages needed!
  Only uses standard library + system tools
  Works out of the box on Kali Linux

{Fore.RESET}""")
        sys.exit(1)
    
    target = sys.argv[1]
    quick_mode = '--quick' in sys.argv
    
    recon = KaliPassiveRecon(target)
    
    if quick_mode:
        recon.run_quick()
    else:
        recon.run_full_recon()

if __name__ == "__main__":
    main()