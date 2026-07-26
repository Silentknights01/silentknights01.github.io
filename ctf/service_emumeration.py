#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
████████ ULTIMATE SERVICE ENUMERATION TOOL v1.0 ████████
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
class KaliServiceEnum:
    def __init__(self, target: str):
        self.target = target
        self.results = {
            'target': target,
            'timestamp': datetime.now().isoformat(),
            'services': {},
            'ftp': {},
            'ssh': {},
            'smtp': {},
            'dns': {},
            'http': {},
            'smb': {},
            'snmp': {},
            'ldap': {},
            'mysql': {},
            'postgresql': {},
            'redis': {},
            'nmap_scripts': {}
        }
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = f"service_enum_{target}_{self.timestamp}"
        
        os.makedirs(self.output_dir, exist_ok=True)
        
        print(f"{Fore.CYAN}{'='*70}")
        print(f"{Fore.MAGENTA}{Style.BRIGHT}🔎 SERVICE ENUMERATION TOOL v1.0")
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

    # ========== 1. FTP Enumeration (Port 21) ==========
    def enum_ftp(self):
        """Enumeration سرویس FTP"""
        self.log("Enumerating FTP (Port 21)...", "INFO")
        
        ftp_data = {}
        
        # 1. بررسی با Nmap
        stdout, stderr = self.run_command(f"nmap -sV -p21 --script=ftp-* {self.target}", timeout=60)
        if stdout:
            ftp_data['nmap'] = stdout
            self.save_text(stdout, "ftp_nmap.txt")
            
            # استخراج اطلاعات
            version = re.search(r'21/tcp\s+open\s+ftp\s+(.+)', stdout)
            if version:
                ftp_data['version'] = version.group(1).strip()
        
        # 2. بررسی Anonymous Login
        self.log("Checking FTP Anonymous Login...", "INFO")
        stdout, stderr = self.run_command(f"ftp -n {self.target} <<EOF\nuser anonymous anonymous\nquit\nEOF", timeout=30)
        if stdout and '230' in stdout:
            ftp_data['anonymous'] = True
            print(f"  {Fore.GREEN}✓ Anonymous login allowed!")
        
        # 3. بررسی با hydra (اختیاری)
        if self.check_tool("hydra"):
            self.log("Running hydra FTP brute force...", "WARNING")
            stdout, stderr = self.run_command(f"hydra -l admin -P /usr/share/wordlists/rockyou.txt ftp://{self.target} -t 4 -o {self.output_dir}/ftp_hydra.txt", timeout=120)
            if stdout:
                ftp_data['hydra'] = stdout
        
        self.results['ftp'] = ftp_data
        self.save_json(ftp_data, 'ftp.json')
        
        print(f"\n{Fore.MAGENTA}{'='*50}")
        print(f"{Fore.YELLOW}📁 FTP RESULTS")
        print(f"{Fore.MAGENTA}{'='*50}")
        
        if ftp_data.get('version'):
            print(f"  {Fore.CYAN}Version: {Fore.WHITE}{ftp_data['version']}")
        if ftp_data.get('anonymous'):
            print(f"  {Fore.GREEN}✓ Anonymous login: {Fore.WHITE}Allowed")
        else:
            print(f"  {Fore.YELLOW}✗ Anonymous login: {Fore.WHITE}Not allowed")
        
        self.log("FTP enumeration completed", "SUCCESS")

    # ========== 2. SSH Enumeration (Port 22) ==========
    def enum_ssh(self):
        """Enumeration سرویس SSH"""
        self.log("Enumerating SSH (Port 22)...", "INFO")
        
        ssh_data = {}
        
        # 1. بررسی با Nmap
        stdout, stderr = self.run_command(f"nmap -sV -p22 --script=ssh-* {self.target}", timeout=60)
        if stdout:
            ssh_data['nmap'] = stdout
            self.save_text(stdout, "ssh_nmap.txt")
            
            version = re.search(r'22/tcp\s+open\s+ssh\s+(.+)', stdout)
            if version:
                ssh_data['version'] = version.group(1).strip()
        
        # 2. دریافت بنر
        stdout, stderr = self.run_command(f"nc -nv {self.target} 22", timeout=10)
        if stdout:
            ssh_data['banner'] = stdout
            self.save_text(stdout, "ssh_banner.txt")
        
        # 3. بررسی با hydra (اختیاری)
        if self.check_tool("hydra"):
            self.log("Running hydra SSH brute force...", "WARNING")
            stdout, stderr = self.run_command(f"hydra -l root -P /usr/share/wordlists/rockyou.txt ssh://{self.target} -t 4 -o {self.output_dir}/ssh_hydra.txt", timeout=120)
            if stdout:
                ssh_data['hydra'] = stdout
        
        self.results['ssh'] = ssh_data
        self.save_json(ssh_data, 'ssh.json')
        
        print(f"\n{Fore.MAGENTA}{'='*50}")
        print(f"{Fore.YELLOW}🔑 SSH RESULTS")
        print(f"{Fore.MAGENTA}{'='*50}")
        
        if ssh_data.get('version'):
            print(f"  {Fore.CYAN}Version: {Fore.WHITE}{ssh_data['version']}")
        if ssh_data.get('banner'):
            print(f"  {Fore.CYAN}Banner: {Fore.WHITE}{ssh_data['banner'][:100]}...")
        
        self.log("SSH enumeration completed", "SUCCESS")

    # ========== 3. SMTP Enumeration (Port 25) ==========
    def enum_smtp(self):
        """Enumeration سرویس SMTP"""
        self.log("Enumerating SMTP (Port 25)...", "INFO")
        
        smtp_data = {}
        
        # 1. بررسی با Nmap
        stdout, stderr = self.run_command(f"nmap -sV -p25 --script=smtp-* {self.target}", timeout=60)
        if stdout:
            smtp_data['nmap'] = stdout
            self.save_text(stdout, "smtp_nmap.txt")
        
        # 2. دریافت بنر
        stdout, stderr = self.run_command(f"nc -nv {self.target} 25", timeout=10)
        if stdout:
            smtp_data['banner'] = stdout
            self.save_text(stdout, "smtp_banner.txt")
        
        # 3. VRFY Enumeration
        self.log("Checking SMTP VRFY...", "INFO")
        stdout, stderr = self.run_command(f"nc {self.target} 25 <<EOF\nVRFY root\nVRFY admin\nVRFY test\nQUIT\nEOF", timeout=30)
        if stdout:
            smtp_data['vrfy'] = stdout
            self.save_text(stdout, "smtp_vrfy.txt")
            
            # استخراج کاربران
            users = re.findall(r'User ([\w.-]+)', stdout)
            if users:
                smtp_data['users'] = users
                for user in users:
                    print(f"  {Fore.GREEN}✓ User found: {Fore.WHITE}{user}")
        
        self.results['smtp'] = smtp_data
        self.save_json(smtp_data, 'smtp.json')
        
        print(f"\n{Fore.MAGENTA}{'='*50}")
        print(f"{Fore.YELLOW}📧 SMTP RESULTS")
        print(f"{Fore.MAGENTA}{'='*50}")
        
        if smtp_data.get('banner'):
            print(f"  {Fore.CYAN}Banner: {Fore.WHITE}{smtp_data['banner'][:100]}...")
        if smtp_data.get('users'):
            print(f"  {Fore.CYAN}Users found: {Fore.WHITE}{len(smtp_data['users'])}")
        
        self.log("SMTP enumeration completed", "SUCCESS")

    # ========== 4. DNS Enumeration (Port 53) ==========
    def enum_dns(self):
        """Enumeration سرویس DNS"""
        self.log("Enumerating DNS (Port 53)...", "INFO")
        
        dns_data = {}
        
        # 1. بررسی با Nmap
        stdout, stderr = self.run_command(f"nmap -sV -p53 --script=dns-* {self.target}", timeout=60)
        if stdout:
            dns_data['nmap'] = stdout
            self.save_text(stdout, "dns_nmap.txt")
        
        # 2. Zone Transfer
        self.log("Checking DNS Zone Transfer...", "INFO")
        stdout, stderr = self.run_command(f"dnsrecon -d {self.target} -t axfr", timeout=30)
        if stdout:
            dns_data['zone_transfer'] = stdout
            self.save_text(stdout, "dns_zone_transfer.txt")
            
            if 'records found' in stdout:
                print(f"  {Fore.GREEN}✓ Zone Transfer successful!")
        
        # 3. DNS Enumeration
        self.log("Running DNS Enumeration...", "INFO")
        if self.check_tool("dnsenum"):
            stdout, stderr = self.run_command(f"dnsenum {self.target} -o {self.output_dir}/dnsenum.txt", timeout=60)
            if stdout:
                dns_data['dnsenum'] = stdout
        else:
            # استفاده از dnsrecon
            stdout, stderr = self.run_command(f"dnsrecon -d {self.target} -t std", timeout=60)
            if stdout:
                dns_data['dnsrecon'] = stdout
                self.save_text(stdout, "dns_recon.txt")
                
                # استخراج زیردامنه‌ها
                subs = re.findall(r'[a-zA-Z0-9.-]+\.' + re.escape(self.target), stdout)
                if subs:
                    dns_data['subdomains'] = list(set(subs))
                    print(f"  {Fore.CYAN}Subdomains found: {Fore.WHITE}{len(set(subs))}")
        
        self.results['dns'] = dns_data
        self.save_json(dns_data, 'dns.json')
        
        print(f"\n{Fore.MAGENTA}{'='*50}")
        print(f"{Fore.YELLOW}🌐 DNS RESULTS")
        print(f"{Fore.MAGENTA}{'='*50}")
        
        if dns_data.get('subdomains'):
            for sub in dns_data['subdomains'][:10]:
                print(f"  {Fore.GREEN}→ {Fore.WHITE}{sub}")
            if len(dns_data['subdomains']) > 10:
                print(f"  {Fore.YELLOW}... and {len(dns_data['subdomains'])-10} more")
        
        self.log("DNS enumeration completed", "SUCCESS")

    # ========== 5. HTTP Enumeration (Port 80/443) ==========
    def enum_http(self):
        """Enumeration سرویس HTTP"""
        self.log("Enumerating HTTP (Port 80/443)...", "INFO")
        
        http_data = {}
        
        # 1. بررسی با Nmap
        stdout, stderr = self.run_command(f"nmap -sV -p80,443 --script=http-* {self.target}", timeout=60)
        if stdout:
            http_data['nmap'] = stdout
            self.save_text(stdout, "http_nmap.txt")
        
        # 2. WhatWeb
        if self.check_tool("whatweb"):
            stdout, stderr = self.run_command(f"whatweb -a 3 {self.target}", timeout=30)
            if stdout:
                http_data['whatweb'] = stdout
                self.save_text(stdout, "http_whatweb.txt")
                
                # استخراج تکنولوژی
                techs = re.findall(r'\[([^\]]+)\]', stdout)
                if techs:
                    http_data['technologies'] = techs
        
        # 3. Curl Headers
        stdout, stderr = self.run_command(f"curl -I -L {self.target}", timeout=30)
        if stdout:
            http_data['headers'] = stdout
            self.save_text(stdout, "http_headers.txt")
            
            # استخراج Server
            server = re.search(r'Server:\s*(.+)', stdout, re.IGNORECASE)
            if server:
                http_data['server'] = server.group(1).strip()
        
        # 4. Robots.txt
        stdout, stderr = self.run_command(f"curl -s {self.target}/robots.txt", timeout=30)
        if stdout and 'User-agent' in stdout:
            http_data['robots'] = stdout
            self.save_text(stdout, "http_robots.txt")
            
            # استخراج Disallow
            disallow = re.findall(r'Disallow:\s*(.+)', stdout)
            if disallow:
                http_data['disallow'] = disallow
                for d in disallow:
                    print(f"  {Fore.YELLOW}→ Disallow: {Fore.WHITE}{d}")
        
        self.results['http'] = http_data
        self.save_json(http_data, 'http.json')
        
        print(f"\n{Fore.MAGENTA}{'='*50}")
        print(f"{Fore.YELLOW}🌐 HTTP RESULTS")
        print(f"{Fore.MAGENTA}{'='*50}")
        
        if http_data.get('server'):
            print(f"  {Fore.CYAN}Server: {Fore.WHITE}{http_data['server']}")
        if http_data.get('technologies'):
            print(f"  {Fore.CYAN}Technologies: {Fore.WHITE}{', '.join(http_data['technologies'][:5])}")
        
        self.log("HTTP enumeration completed", "SUCCESS")

    # ========== 6. SMB Enumeration (Port 139/445) ==========
    def enum_smb(self):
        """Enumeration سرویس SMB"""
        self.log("Enumerating SMB (Port 139/445)...", "INFO")
        
        smb_data = {}
        
        # 1. Nmap SMB Scripts
        stdout, stderr = self.run_command(f"nmap -p139,445 --script=smb-* {self.target}", timeout=60)
        if stdout:
            smb_data['nmap'] = stdout
            self.save_text(stdout, "smb_nmap.txt")
            
            # استخراج OS
            os_match = re.search(r'OS:\s*(.+)', stdout)
            if os_match:
                smb_data['os'] = os_match.group(1).strip()
        
        # 2. enum4linux
        if self.check_tool("enum4linux"):
            self.log("Running enum4linux...", "INFO")
            stdout, stderr = self.run_command(f"enum4linux {self.target}", timeout=120)
            if stdout:
                smb_data['enum4linux'] = stdout
                self.save_text(stdout, "smb_enum4linux.txt")
                
                # استخراج کاربران
                users = re.findall(r'user:\[([^\]]+)\]', stdout)
                if users:
                    smb_data['users'] = users
                    print(f"  {Fore.CYAN}Users found: {Fore.WHITE}{len(users)}")
                
                # استخراج Shares
                shares = re.findall(r'Sharename\s+Type\s+Comment\s+([\w-]+)', stdout)
                if shares:
                    smb_data['shares'] = shares
                    print(f"  {Fore.CYAN}Shares found: {Fore.WHITE}{len(shares)}")
                    for share in shares[:10]:
                        print(f"    {Fore.GREEN}→ {Fore.WHITE}{share}")
        
        # 3. smbclient
        if self.check_tool("smbclient"):
            self.log("Running smbclient...", "INFO")
            stdout, stderr = self.run_command(f"smbclient -L //{self.target} -N", timeout=30)
            if stdout:
                smb_data['smbclient'] = stdout
                self.save_text(stdout, "smb_smbclient.txt")
        
        # 4. smbmap
        if self.check_tool("smbmap"):
            self.log("Running smbmap...", "INFO")
            stdout, stderr = self.run_command(f"smbmap -H {self.target}", timeout=30)
            if stdout:
                smb_data['smbmap'] = stdout
                self.save_text(stdout, "smb_smbmap.txt")
                
                # استخراج Shares با دسترسی
                shares = re.findall(r'([\w-]+)\s+([A-Z_]+)', stdout)
                if shares:
                    smb_data['shares_permissions'] = shares
                    for share, perm in shares:
                        if 'READ' in perm or 'WRITE' in perm:
                            print(f"  {Fore.GREEN}✓ {Fore.WHITE}{share} -> {perm}")
        
        self.results['smb'] = smb_data
        self.save_json(smb_data, 'smb.json')
        
        print(f"\n{Fore.MAGENTA}{'='*50}")
        print(f"{Fore.YELLOW}💾 SMB RESULTS")
        print(f"{Fore.MAGENTA}{'='*50}")
        
        if smb_data.get('os'):
            print(f"  {Fore.CYAN}OS: {Fore.WHITE}{smb_data['os']}")
        if smb_data.get('users'):
            print(f"  {Fore.CYAN}Users: {Fore.WHITE}{len(smb_data['users'])}")
        if smb_data.get('shares'):
            print(f"  {Fore.CYAN}Shares: {Fore.WHITE}{len(smb_data['shares'])}")
        
        self.log("SMB enumeration completed", "SUCCESS")

    # ========== 7. SNMP Enumeration (Port 161) ==========
    def enum_snmp(self):
        """Enumeration سرویس SNMP"""
        self.log("Enumerating SNMP (Port 161)...", "INFO")
        
        snmp_data = {}
        
        # 1. Nmap SNMP Scripts
        stdout, stderr = self.run_command(f"nmap -sU -p161 --script=snmp-* {self.target}", timeout=60)
        if stdout:
            snmp_data['nmap'] = stdout
            self.save_text(stdout, "snmp_nmap.txt")
        
        # 2. snmpwalk با community string
        communities = ['public', 'private', 'manager', 'community']
        for community in communities:
            self.log(f"Testing SNMP community: {community}...", "INFO")
            stdout, stderr = self.run_command(f"snmpwalk -v2c -c {community} {self.target}", timeout=30)
            if stdout:
                snmp_data[f'community_{community}'] = stdout
                self.save_text(stdout, f"snmp_{community}.txt")
                print(f"  {Fore.GREEN}✓ Community '{community}' works!")
                
                # استخراج اطلاعات مهم
                hostname = re.search(r'SNMPv2-MIB::sysName.0 = STRING: (.+)', stdout)
                if hostname:
                    snmp_data['hostname'] = hostname.group(1).strip()
                
                users = re.findall(r'hrSWInstalledName\.\d+ = STRING: (.+)', stdout)
                if users:
                    snmp_data['software'] = users
                
                break
        
        self.results['snmp'] = snmp_data
        self.save_json(snmp_data, 'snmp.json')
        
        print(f"\n{Fore.MAGENTA}{'='*50}")
        print(f"{Fore.YELLOW}📡 SNMP RESULTS")
        print(f"{Fore.MAGENTA}{'='*50}")
        
        if snmp_data.get('hostname'):
            print(f"  {Fore.CYAN}Hostname: {Fore.WHITE}{snmp_data['hostname']}")
        if snmp_data.get('software'):
            print(f"  {Fore.CYAN}Software: {Fore.WHITE}{len(snmp_data['software'])} items")
        
        self.log("SNMP enumeration completed", "SUCCESS")

    # ========== 8. LDAP Enumeration (Port 389) ==========
    def enum_ldap(self):
        """Enumeration سرویس LDAP"""
        self.log("Enumerating LDAP (Port 389)...", "INFO")
        
        ldap_data = {}
        
        # 1. Nmap LDAP Scripts
        stdout, stderr = self.run_command(f"nmap -p389 --script=ldap-* {self.target}", timeout=60)
        if stdout:
            ldap_data['nmap'] = stdout
            self.save_text(stdout, "ldap_nmap.txt")
        
        # 2. ldapsearch
        if self.check_tool("ldapsearch"):
            self.log("Running ldapsearch...", "INFO")
            stdout, stderr = self.run_command(f"ldapsearch -x -H ldap://{self.target} -b '' -s base", timeout=30)
            if stdout:
                ldap_data['ldapsearch'] = stdout
                self.save_text(stdout, "ldap_search.txt")
                
                # استخراج اطلاعات
                domain = re.search(r'domainComponent:\s*(.+)', stdout)
                if domain:
                    ldap_data['domain'] = domain.group(1).strip()
        
        self.results['ldap'] = ldap_data
        self.save_json(ldap_data, 'ldap.json')
        
        print(f"\n{Fore.MAGENTA}{'='*50}")
        print(f"{Fore.YELLOW}📂 LDAP RESULTS")
        print(f"{Fore.MAGENTA}{'='*50}")
        
        if ldap_data.get('domain'):
            print(f"  {Fore.CYAN}Domain: {Fore.WHITE}{ldap_data['domain']}")
        
        self.log("LDAP enumeration completed", "SUCCESS")

    # ========== 9. MySQL Enumeration (Port 3306) ==========
    def enum_mysql(self):
        """Enumeration سرویس MySQL"""
        self.log("Enumerating MySQL (Port 3306)...", "INFO")
        
        mysql_data = {}
        
        # 1. Nmap MySQL Scripts
        stdout, stderr = self.run_command(f"nmap -p3306 --script=mysql-* {self.target}", timeout=60)
        if stdout:
            mysql_data['nmap'] = stdout
            self.save_text(stdout, "mysql_nmap.txt")
            
            # استخراج نسخه
            version = re.search(r'mysql-info:\s+Protocol:\s+\d+\s+Version:\s+(\d+\.\d+\.\d+)', stdout)
            if version:
                mysql_data['version'] = version.group(1).strip()
        
        # 2. بررسی با mysql client (اگر credentials داشته باشیم)
        if self.check_tool("mysql"):
            self.log("Checking MySQL with default credentials...", "INFO")
            stdout, stderr = self.run_command(f"mysql -h {self.target} -u root -e 'SELECT VERSION();' --connect-timeout=10", timeout=30)
            if stdout:
                mysql_data['root_connect'] = True
                print(f"  {Fore.GREEN}✓ Root connection successful!")
        
        self.results['mysql'] = mysql_data
        self.save_json(mysql_data, 'mysql.json')
        
        print(f"\n{Fore.MAGENTA}{'='*50}")
        print(f"{Fore.YELLOW}🗄️ MYSQL RESULTS")
        print(f"{Fore.MAGENTA}{'='*50}")
        
        if mysql_data.get('version'):
            print(f"  {Fore.CYAN}Version: {Fore.WHITE}{mysql_data['version']}")
        if mysql_data.get('root_connect'):
            print(f"  {Fore.GREEN}✓ Root access: {Fore.WHITE}Successful")
        
        self.log("MySQL enumeration completed", "SUCCESS")

    # ========== 10. Redis Enumeration (Port 6379) ==========
    def enum_redis(self):
        """Enumeration سرویس Redis"""
        self.log("Enumerating Redis (Port 6379)...", "INFO")
        
        redis_data = {}
        
        # 1. Nmap Redis Scripts
        stdout, stderr = self.run_command(f"nmap -p6379 --script=redis-* {self.target}", timeout=60)
        if stdout:
            redis_data['nmap'] = stdout
            self.save_text(stdout, "redis_nmap.txt")
        
        # 2. redis-cli
        if self.check_tool("redis-cli"):
            self.log("Checking Redis connection...", "INFO")
            stdout, stderr = self.run_command(f"redis-cli -h {self.target} -p 6379 INFO", timeout=30)
            if stdout:
                redis_data['info'] = stdout
                self.save_text(stdout, "redis_info.txt")
                
                # استخراج اطلاعات
                version = re.search(r'redis_version:(.+)', stdout)
                if version:
                    redis_data['version'] = version.group(1).strip()
                
                # استخراج کلیدها
                keys = re.search(r'db0:keys=(\d+)', stdout)
                if keys:
                    redis_data['keys'] = keys.group(1).strip()
        
        self.results['redis'] = redis_data
        self.save_json(redis_data, 'redis.json')
        
        print(f"\n{Fore.MAGENTA}{'='*50}")
        print(f"{Fore.YELLOW}⚡ REDIS RESULTS")
        print(f"{Fore.MAGENTA}{'='*50}")
        
        if redis_data.get('version'):
            print(f"  {Fore.CYAN}Version: {Fore.WHITE}{redis_data['version']}")
        if redis_data.get('keys'):
            print(f"  {Fore.CYAN}Keys: {Fore.WHITE}{redis_data['keys']}")
        
        self.log("Redis enumeration completed", "SUCCESS")

    # ========== 11. PostgreSQL Enumeration (Port 5432) ==========
    def enum_postgresql(self):
        """Enumeration سرویس PostgreSQL"""
        self.log("Enumerating PostgreSQL (Port 5432)...", "INFO")
        
        pgsql_data = {}
        
        # 1. Nmap PostgreSQL Scripts
        stdout, stderr = self.run_command(f"nmap -p5432 --script=pgsql-* {self.target}", timeout=60)
        if stdout:
            pgsql_data['nmap'] = stdout
            self.save_text(stdout, "postgresql_nmap.txt")
        
        # 2. Checking with psql
        if self.check_tool("psql"):
            self.log("Checking PostgreSQL with default credentials...", "INFO")
            stdout, stderr = self.run_command(f"psql -h {self.target} -U postgres -c 'SELECT version();' --port=5432", timeout=30)
            if stdout:
                pgsql_data['postgres_connect'] = True
                print(f"  {Fore.GREEN}✓ Postgres connection successful!")
        
        self.results['postgresql'] = pgsql_data
        self.save_json(pgsql_data, 'postgresql.json')
        
        print(f"\n{Fore.MAGENTA}{'='*50}")
        print(f"{Fore.YELLOW}🐘 POSTGRESQL RESULTS")
        print(f"{Fore.MAGENTA}{'='*50}")
        
        if pgsql_data.get('postgres_connect'):
            print(f"  {Fore.GREEN}✓ Postgres access: {Fore.WHITE}Successful")
        
        self.log("PostgreSQL enumeration completed", "SUCCESS")

    # ========== 12. Nmap NSE All Services ==========
    def nmap_nse_all(self):
        """اجرای NSE Scripts روی همه سرویس‌ها"""
        self.log("Running Nmap NSE on all services...", "INFO")
        
        nse_data = {}
        
        # اسکن کامل با اسکریپت‌های پیش‌فرض
        stdout, stderr = self.run_command(f"nmap -sC -sV {self.target}", timeout=180)
        if stdout:
            nse_data['default'] = stdout
            self.save_text(stdout, "nmap_nse_default.txt")
            
            print(f"\n{Fore.MAGENTA}{'='*50}")
            print(f"{Fore.YELLOW}📜 NMAP NSE RESULTS")
            print(f"{Fore.MAGENTA}{'='*50}")
            
            # نمایش خلاصه
            lines = stdout.split('\n')[:30]
            for line in lines:
                if 'open' in line or 'PORT' in line:
                    print(f"  {Fore.WHITE}{line}")
        
        self.results['nmap_scripts'] = nse_data
        self.save_json(nse_data, 'nmap_nse.json')
        self.log("Nmap NSE completed", "SUCCESS")

    # ========== 13. Final Report ==========
    def final_report(self):
        """گزارش نهایی"""
        print(f"\n{Fore.GREEN}{'='*70}")
        print(f"{Fore.MAGENTA}{Style.BRIGHT}✅ SERVICE ENUMERATION COMPLETE")
        print(f"{Fore.GREEN}{'='*70}")
        
        print(f"\n{Fore.CYAN}📊 SUMMARY REPORT")
        print(f"{Fore.CYAN}{'-'*50}")
        
        print(f"{Fore.WHITE}Target: {Fore.YELLOW}{self.target}")
        print(f"{Fore.WHITE}Date: {Fore.YELLOW}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{Fore.WHITE}Output: {Fore.YELLOW}{self.output_dir}")
        
        print(f"\n{Fore.WHITE}Services Enumerated:")
        
        # FTP
        if self.results['ftp']:
            print(f"  {Fore.CYAN}FTP (21): {Fore.WHITE}{self.results['ftp'].get('version', 'N/A')}")
        
        # SSH
        if self.results['ssh']:
            print(f"  {Fore.CYAN}SSH (22): {Fore.WHITE}{self.results['ssh'].get('version', 'N/A')}")
        
        # SMTP
        if self.results['smtp']:
            print(f"  {Fore.CYAN}SMTP (25): {Fore.WHITE}{len(self.results['smtp'].get('users', []))} users found")
        
        # DNS
        if self.results['dns']:
            subs = self.results['dns'].get('subdomains', [])
            print(f"  {Fore.CYAN}DNS (53): {Fore.WHITE}{len(subs)} subdomains found")
        
        # HTTP
        if self.results['http']:
            print(f"  {Fore.CYAN}HTTP (80/443): {Fore.WHITE}{self.results['http'].get('server', 'N/A')}")
        
        # SMB
        if self.results['smb']:
            shares = self.results['smb'].get('shares', [])
            users = self.results['smb'].get('users', [])
            print(f"  {Fore.CYAN}SMB (139/445): {Fore.WHITE}{len(shares)} shares, {len(users)} users")
        
        # SNMP
        if self.results['snmp']:
            print(f"  {Fore.CYAN}SNMP (161): {Fore.WHITE}{self.results['snmp'].get('hostname', 'N/A')}")
        
        # MySQL
        if self.results['mysql']:
            print(f"  {Fore.CYAN}MySQL (3306): {Fore.WHITE}{self.results['mysql'].get('version', 'N/A')}")
        
        # PostgreSQL
        if self.results['postgresql']:
            print(f"  {Fore.CYAN}PostgreSQL (5432): {Fore.WHITE}Detected")
        
        # Redis
        if self.results['redis']:
            print(f"  {Fore.CYAN}Redis (6379): {Fore.WHITE}{self.results['redis'].get('version', 'N/A')}")
        
        # خلاصه
        summary = {
            'target': self.target,
            'timestamp': datetime.now().isoformat(),
            'services': {
                'ftp': bool(self.results['ftp']),
                'ssh': bool(self.results['ssh']),
                'smtp': bool(self.results['smtp']),
                'dns': bool(self.results['dns']),
                'http': bool(self.results['http']),
                'smb': bool(self.results['smb']),
                'snmp': bool(self.results['snmp']),
                'ldap': bool(self.results['ldap']),
                'mysql': bool(self.results['mysql']),
                'postgresql': bool(self.results['postgresql']),
                'redis': bool(self.results['redis'])
            },
            'files': os.listdir(self.output_dir)
        }
        
        self.save_json(summary, 'summary.json')
        
        print(f"\n{Fore.GREEN}📁 All results saved to: {self.output_dir}")
        print(f"{Fore.GREEN}{'='*70}\n")

    # ========== 14. Run Full ==========
    def run_full_recon(self):
        """اجرای کامل Service Enumeration"""
        self.log("🚀 Starting Full Service Enumeration", "CRITICAL")
        
        start_time = time.time()
        
        # اجرای enumeration روی همه سرویس‌ها
        self.enum_ftp()
        self.enum_ssh()
        self.enum_smtp()
        self.enum_dns()
        self.enum_http()
        self.enum_smb()
        self.enum_snmp()
        self.enum_ldap()
        self.enum_mysql()
        self.enum_redis()
        self.enum_postgresql()
        self.nmap_nse_all()
        
        self.final_report()
        
        elapsed = time.time() - start_time
        print(f"{Fore.CYAN}⏱️  Total time: {elapsed:.2f} seconds")

    def run_quick(self):
        """اجرای سریع Service Enumeration"""
        self.log("🚀 Starting Quick Service Enumeration", "CRITICAL")
        
        start_time = time.time()
        
        # فقط سرویس‌های مهم
        self.enum_ftp()
        self.enum_ssh()
        self.enum_http()
        self.enum_smb()
        self.enum_dns()
        self.nmap_nse_all()
        
        self.final_report()
        
        elapsed = time.time() - start_time
        print(f"{Fore.CYAN}⏱️  Total time: {elapsed:.2f} seconds")

# ==================== Main ====================
def main():
    if len(sys.argv) < 2:
        print(f"""
{Fore.CYAN}████████ SERVICE ENUMERATION TOOL v1.0 ████████
{Fore.YELLOW}
Usage:
  python3 service_enum.py <target>        # Full enumeration
  python3 service_enum.py <target> --quick # Quick enumeration

{Fore.GREEN}Examples:
  python3 service_enum.py 192.168.1.10
  python3 service_enum.py example.com
  python3 service_enum.py 192.168.1.10 --quick

{Fore.CYAN}Services Enumerated:
  • FTP (21)      - Anonymous login, version
  • SSH (22)      - Version, banner
  • SMTP (25)     - VRFY, users
  • DNS (53)      - Zone transfer, subdomains
  • HTTP (80/443) - Technologies, headers, robots
  • SMB (139/445) - Shares, users, permissions
  • SNMP (161)    - Community strings, info
  • LDAP (389)    - Domain info
  • MySQL (3306)  - Version, credentials
  • Redis (6379)  - Version, keys
  • PostgreSQL (5432) - Access check

{Fore.YELLOW}⚠️  Use only on authorized targets!
{Fore.RESET}""")
        sys.exit(1)
    
    target = sys.argv[1]
    quick_mode = '--quick' in sys.argv
    
    recon = KaliServiceEnum(target)
    
    if quick_mode:
        recon.run_quick()
    else:
        recon.run_full_recon()

if __name__ == "__main__":
    main()