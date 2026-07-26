#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
████████ ULTIMATE CTF RECON & REPORTING ASSISTANT v2.0 ████████
✅ Automated Pentest Reporting Engine
✅ بدون AI - 100% Rule-Based
✅ جمع‌آوری، Normalize، Correlate، Risk Scoring، Attack Path
"""

import subprocess
import sys
import os
import re
import json
import xml.etree.ElementTree as ET
from datetime import datetime
import socket
import time
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict
import hashlib
import shutil

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
class CTFReconAssistant:
    def __init__(self, target: str = "", input_dir: str = ""):
        self.target = target
        self.input_dir = input_dir
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = f"ctf_report_{target}_{self.timestamp}" if target else f"ctf_report_{self.timestamp}"
        
        # Data structures
        self.assets = {}
        self.findings = []
        self.evidence = {}
        self.attack_paths = []
        self.correlation_map = defaultdict(list)
        
        # Rules
        self.rules = self._load_rules()
        
        os.makedirs(self.output_dir, exist_ok=True)
        
        print(f"{Fore.CYAN}{'='*70}")
        print(f"{Fore.MAGENTA}{Style.BRIGHT}🚀 CTF RECON & REPORTING ASSISTANT v2.0")
        print(f"{Fore.CYAN}{'='*70}")
        print(f"{Fore.GREEN}📌 Target: {target if target else 'N/A'}")
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

    # ========== 1. Rules Engine ==========
    def _load_rules(self) -> Dict:
        """بارگذاری قواعد تحلیل"""
        return {
            'findings': [
                {
                    'id': 'FTP_ANON',
                    'condition': {'service': 'ftp', 'anonymous': True},
                    'finding': 'Anonymous FTP Access',
                    'severity': 'Medium',
                    'description': 'FTP server allows anonymous login. This may expose sensitive files.',
                    'remediation': 'Disable anonymous FTP access.'
                },
                {
                    'id': 'SMB_SIGNING',
                    'condition': {'port': 445, 'signing': False},
                    'finding': 'SMB Signing Disabled',
                    'severity': 'Medium',
                    'description': 'SMB signing is disabled. This allows man-in-the-middle attacks.',
                    'remediation': 'Enable SMB signing.'
                },
                {
                    'id': 'DIR_LISTING',
                    'condition': {'http': True, 'dir_listing': True},
                    'finding': 'Directory Listing Enabled',
                    'severity': 'Low',
                    'description': 'Directory listing is enabled. This may expose sensitive files.',
                    'remediation': 'Disable directory listing.'
                },
                {
                    'id': 'MISSING_HEADER',
                    'condition': {'http': True, 'missing_header': True},
                    'finding': 'Missing Security Headers',
                    'severity': 'Low',
                    'description': 'Important security headers are missing.',
                    'remediation': 'Add security headers.'
                },
                {
                    'id': 'OUTDATED_APACHE',
                    'condition': {'service': 'http', 'product': 'Apache', 'version': '<2.4.50'},
                    'finding': 'Outdated Apache Version',
                    'severity': 'High',
                    'description': 'Apache version is outdated and may contain known vulnerabilities.',
                    'remediation': 'Upgrade Apache to the latest version.'
                },
                {
                    'id': 'SSL_WEAK',
                    'condition': {'ssl': True, 'weak_cipher': True},
                    'finding': 'Weak SSL Ciphers',
                    'severity': 'High',
                    'description': 'Server supports weak SSL ciphers. This allows cryptographic attacks.',
                    'remediation': 'Disable weak SSL ciphers.'
                },
                {
                    'id': 'SSH_WEAK',
                    'condition': {'service': 'ssh', 'weak_algo': True},
                    'finding': 'Weak SSH Algorithms',
                    'severity': 'Medium',
                    'description': 'SSH server supports weak algorithms.',
                    'remediation': 'Configure SSH to use strong algorithms.'
                }
            ],
            'priority': {
                'Critical': 5,
                'High': 4,
                'Medium': 3,
                'Low': 2,
                'Info': 1
            },
            'attack_paths': [
                {
                    'id': 'WEB_COMPROMISE',
                    'steps': [
                        {'port': 80, 'service': 'http'},
                        {'finding': 'CVE'},
                        {'finding': 'RCE'},
                        {'result': 'shell'}
                    ]
                },
                {
                    'id': 'SMB_ATTACK',
                    'steps': [
                        {'port': 445, 'service': 'smb'},
                        {'finding': 'misconfig'},
                        {'result': 'access'}
                    ]
                },
                {
                    'id': 'CREDENTIAL_ATTACK',
                    'steps': [
                        {'finding': 'credentials'},
                        {'result': 'login'}
                    ]
                }
            ]
        }

    # ========== 2. Data Collection ==========
    def run_tools(self):
        """اجرای ابزارهای جمع‌آوری اطلاعات"""
        self.log("Running Recon Tools...", "INFO")
        
        tools_output = {}
        
        # 1. Nmap
        if self.target:
            self.log("Running Nmap...", "INFO")
            stdout, _ = self._run_command(f"nmap -sV -sC -p- -T4 {self.target} -oX {self.output_dir}/nmap.xml")
            tools_output['nmap'] = stdout
        
        # 2. WhatWeb
        if self.target:
            self.log("Running WhatWeb...", "INFO")
            stdout, _ = self._run_command(f"whatweb -a 3 {self.target} -j > {self.output_dir}/whatweb.json")
            tools_output['whatweb'] = stdout
        
        # 3. Nikto
        if self.target:
            self.log("Running Nikto...", "INFO")
            stdout, _ = self._run_command(f"nikto -h {self.target} -ssl -Format html -o {self.output_dir}/nikto.html")
            tools_output['nikto'] = stdout
        
        # 4. Nuclei
        if self.target:
            self.log("Running Nuclei...", "INFO")
            stdout, _ = self._run_command(f"nuclei -u {self.target} -severity critical,high,medium -o {self.output_dir}/nuclei.txt")
            tools_output['nuclei'] = stdout
        
        # 5. Gobuster
        if self.target:
            self.log("Running Gobuster...", "INFO")
            wordlist = "/usr/share/wordlists/dirb/common.txt"
            if os.path.exists(wordlist):
                stdout, _ = self._run_command(f"gobuster dir -u {self.target} -w {wordlist} -t 50 -o {self.output_dir}/gobuster.txt")
                tools_output['gobuster'] = stdout
        
        self.save_json(tools_output, 'tools_output.json')
        self.log("Tools execution completed", "SUCCESS")

    def _run_command(self, cmd: str, timeout: int = 180) -> Tuple[str, str]:
        """اجرای دستور در ترمینال"""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
            return result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return f"[TIMEOUT] Command took longer than {timeout}s", ""
        except Exception as e:
            return f"[ERROR] {str(e)}", ""

    # ========== 3. Parser ==========
    def parse_nmap(self, filepath: str = None):
        """Parse Nmap XML Output"""
        self.log("Parsing Nmap output...", "INFO")
        
        if not filepath:
            filepath = f"{self.output_dir}/nmap.xml"
        
        if not os.path.exists(filepath):
            self.log(f"Nmap output not found: {filepath}", "WARNING")
            return
        
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            
            for host in root.findall('host'):
                ip = host.find('address').get('addr')
                
                # OS Detection
                os_match = host.find('.//osmatch')
                os_name = os_match.get('name') if os_match is not None else 'Unknown'
                
                # Ports
                ports = []
                for port in host.findall('.//port'):
                    port_id = port.get('portid')
                    protocol = port.get('protocol')
                    state = port.find('state').get('state')
                    
                    service = port.find('service')
                    service_name = service.get('name') if service is not None else 'unknown'
                    product = service.get('product') if service is not None else ''
                    version = service.get('version') if service is not None else ''
                    
                    if state == 'open':
                        ports.append({
                            'port': port_id,
                            'protocol': protocol,
                            'service': service_name,
                            'product': product,
                            'version': version
                        })
                
                self.assets[ip] = {
                    'ip': ip,
                    'os': os_name,
                    'ports': ports
                }
                
                print(f"  {Fore.GREEN}✓ {Fore.WHITE}Host: {ip} ({os_name}) - {len(ports)} open ports")
        
        except Exception as e:
            self.log(f"Nmap parse error: {e}", "ERROR")

    def parse_whatweb(self, filepath: str = None):
        """Parse WhatWeb JSON Output"""
        self.log("Parsing WhatWeb output...", "INFO")
        
        if not filepath:
            filepath = f"{self.output_dir}/whatweb.json"
        
        if not os.path.exists(filepath):
            self.log(f"WhatWeb output not found: {filepath}", "WARNING")
            return
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            technologies = []
            for item in data:
                if isinstance(item, dict):
                    for key, value in item.items():
                        if isinstance(value, str):
                            technologies.append(value)
            
            # Add to assets
            for ip in self.assets:
                self.assets[ip]['technologies'] = technologies
                print(f"  {Fore.GREEN}✓ {Fore.WHITE}Technologies: {', '.join(technologies[:5])}")
        
        except Exception as e:
            self.log(f"WhatWeb parse error: {e}", "WARNING")

    def parse_nuclei(self, filepath: str = None):
        """Parse Nuclei Output"""
        self.log("Parsing Nuclei output...", "INFO")
        
        if not filepath:
            filepath = f"{self.output_dir}/nuclei.txt"
        
        if not os.path.exists(filepath):
            self.log(f"Nuclei output not found: {filepath}", "WARNING")
            return
        
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Extract findings
            findings = []
            for line in content.split('\n'):
                if 'CVE-' in line:
                    cve = re.search(r'CVE-\d{4}-\d{4,}', line)
                    cve = cve.group(0) if cve else 'N/A'
                    
                    severity_match = re.search(r'\[(critical|high|medium|low)\]', line, re.IGNORECASE)
                    severity = severity_match.group(1).capitalize() if severity_match else 'Medium'
                    
                    title = line.strip()
                    
                    findings.append({
                        'id': f"VULN-{len(self.findings)+1:03d}",
                        'title': title[:100],
                        'severity': severity,
                        'cve': cve,
                        'source': 'Nuclei',
                        'host': self.target
                    })
            
            for finding in findings:
                self.findings.append(finding)
                print(f"  {Fore.RED}⚠️ {Fore.WHITE}{finding['title'][:80]}...")
        
        except Exception as e:
            self.log(f"Nuclei parse error: {e}", "WARNING")

    def parse_nikto(self, filepath: str = None):
        """Parse Nikto Output"""
        self.log("Parsing Nikto output...", "INFO")
        
        if not filepath:
            filepath = f"{self.output_dir}/nikto.html"
        
        if not os.path.exists(filepath):
            self.log(f"Nikto output not found: {filepath}", "WARNING")
            return
        
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Extract findings from HTML
            findings = re.findall(r'<td[^>]*>(.*?)</td>', content)
            
            for finding in findings[:20]:
                if '+ ' in finding or 'OSVDB' in finding:
                    self.findings.append({
                        'id': f"VULN-{len(self.findings)+1:03d}",
                        'title': finding.strip()[:100],
                        'severity': 'Medium',
                        'cve': 'N/A',
                        'source': 'Nikto',
                        'host': self.target
                    })
                    print(f"  {Fore.YELLOW}→ {Fore.WHITE}{finding.strip()[:80]}...")
        
        except Exception as e:
            self.log(f"Nikto parse error: {e}", "WARNING")

    def parse_gobuster(self, filepath: str = None):
        """Parse Gobuster Output"""
        self.log("Parsing Gobuster output...", "INFO")
        
        if not filepath:
            filepath = f"{self.output_dir}/gobuster.txt"
        
        if not os.path.exists(filepath):
            self.log(f"Gobuster output not found: {filepath}", "WARNING")
            return
        
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            
            directories = []
            for line in content.split('\n'):
                if '/ ' in line and 'Status:' in line:
                    dir_match = re.search(r'/([^/\s]+)', line)
                    if dir_match:
                        directories.append(dir_match.group(1))
            
            if directories:
                print(f"  {Fore.GREEN}✓ {Fore.WHITE}Found {len(directories)} directories")
                for d in directories[:10]:
                    print(f"    → /{d}")
        
        except Exception as e:
            self.log(f"Gobuster parse error: {e}", "WARNING")

    # ========== 4. Correlation Engine ==========
    def correlate_findings(self):
        """Correlate findings and remove duplicates"""
        self.log("Correlating findings...", "INFO")
        
        # Group by CVE
        cve_map = defaultdict(list)
        for finding in self.findings:
            cve = finding.get('cve', 'N/A')
            if cve != 'N/A':
                cve_map[cve].append(finding)
        
        # Create correlated findings
        correlated = []
        for cve, findings in cve_map.items():
            if len(findings) > 1:
                # Multiple sources for same CVE
                correlated.append({
                    'id': f"CORR-{len(correlated)+1:03d}",
                    'cve': cve,
                    'title': findings[0]['title'],
                    'severity': max([f.get('severity_priority', 3) for f in findings]),
                    'sources': [f['source'] for f in findings],
                    'hosts': list(set([f['host'] for f in findings])),
                    'confidence': 'High' if len(findings) > 2 else 'Medium'
                })
        
        # Add correlated findings
        for corr in correlated:
            print(f"  {Fore.GREEN}✓ {Fore.WHITE}Correlated: {corr['cve']} ({len(corr['sources'])} sources)")
        
        self.correlation_map['cve_groups'] = correlated
        self.save_json(correlated, 'correlated_findings.json')

    # ========== 5. Risk Scoring ==========
    def calculate_risk(self):
        """Calculate risk scores for findings"""
        self.log("Calculating risk scores...", "INFO")
        
        severity_weights = {
            'Critical': 5,
            'High': 4,
            'Medium': 3,
            'Low': 2,
            'Info': 1
        }
        
        for finding in self.findings:
            severity = finding.get('severity', 'Medium')
            base_score = severity_weights.get(severity, 3)
            
            # Additional factors
            exploitability = 1
            if 'CVE-' in finding.get('cve', ''):
                exploitability = 2
            if 'RCE' in finding.get('title', '') or 'Remote' in finding.get('title', ''):
                exploitability = 3
            
            exposure = 1
            if 'public' in finding.get('host', '') or finding.get('host') == self.target:
                exposure = 2
            
            confidence = 1
            if len(self.findings) > 5:
                confidence = 2
            
            # Calculate final score
            risk_score = (base_score * 2) + exploitability + exposure + confidence
            
            # Determine severity
            if risk_score >= 15:
                final_severity = 'Critical'
            elif risk_score >= 11:
                final_severity = 'High'
            elif risk_score >= 7:
                final_severity = 'Medium'
            else:
                final_severity = 'Low'
            
            finding['risk_score'] = risk_score
            finding['final_severity'] = final_severity
            
            print(f"  {Fore.CYAN}→ {Fore.WHITE}{finding.get('title', 'N/A')[:50]}... Score: {risk_score} ({final_severity})")

    # ========== 6. Attack Path Analysis ==========
    def build_attack_paths(self):
        """Build attack path graph"""
        self.log("Building attack paths...", "INFO")
        
        paths = []
        
        # HTTP Path
        http_ports = [p for ip in self.assets for p in self.assets[ip].get('ports', []) if p.get('port') in ['80', '443']]
        if http_ports:
            path = {
                'id': 'PATH-001',
                'name': 'Web Application Attack',
                'steps': [
                    'Target Port 80/443',
                    'Web Server Identified',
                    'Potential Vulnerabilities',
                    'Exploitation',
                    'Initial Access'
                ],
                'findings': [f for f in self.findings if 'http' in f.get('title', '').lower()],
                'priority': 'High'
            }
            paths.append(path)
            print(f"  {Fore.GREEN}✓ {Fore.WHITE}Web Application Attack Path")
        
        # SMB Path
        smb_ports = [p for ip in self.assets for p in self.assets[ip].get('ports', []) if p.get('port') == '445']
        if smb_ports:
            path = {
                'id': 'PATH-002',
                'name': 'SMB Attack Path',
                'steps': [
                    'Target Port 445',
                    'SMB Service Detected',
                    'Check for Misconfigurations',
                    'Access Shares',
                    'Privilege Escalation'
                ],
                'findings': [f for f in self.findings if 'smb' in f.get('title', '').lower()],
                'priority': 'Medium'
            }
            paths.append(path)
            print(f"  {Fore.GREEN}✓ {Fore.WHITE}SMB Attack Path")
        
        # SSH Path
        ssh_ports = [p for ip in self.assets for p in self.assets[ip].get('ports', []) if p.get('port') == '22']
        if ssh_ports:
            path = {
                'id': 'PATH-003',
                'name': 'SSH Attack Path',
                'steps': [
                    'Target Port 22',
                    'SSH Service Detected',
                    'Check Credentials',
                    'Brute Force / Keys',
                    'Initial Access'
                ],
                'findings': [f for f in self.findings if 'ssh' in f.get('title', '').lower()],
                'priority': 'Medium'
            }
            paths.append(path)
            print(f"  {Fore.GREEN}✓ {Fore.WHITE}SSH Attack Path")
        
        self.attack_paths = paths
        self.save_json(paths, 'attack_paths.json')

    # ========== 7. Report Generation ==========
    def generate_html_report(self):
        """Generate HTML Report"""
        self.log("Generating HTML report...", "INFO")
        
        # Assets summary
        assets_html = ""
        for ip, data in self.assets.items():
            ports_html = "".join([f'<li>{p["port"]}/{p["protocol"]} - {p["service"]} ({p["product"]} {p["version"]})</li>' for p in data.get('ports', [])[:10]])
            assets_html += f"""
            <div class="asset">
                <h3>{ip}</h3>
                <p><strong>OS:</strong> {data.get('os', 'Unknown')}</p>
                <p><strong>Open Ports:</strong></p>
                <ul>{ports_html}</ul>
            </div>
            """
        
        # Findings
        findings_html = ""
        for finding in self.findings[:20]:
            severity_color = {
                'Critical': 'critical',
                'High': 'high',
                'Medium': 'medium',
                'Low': 'low'
            }.get(finding.get('severity', 'Medium'), 'medium')
            
            findings_html += f"""
            <div class="finding {severity_color}">
                <h4>{finding.get('title', 'N/A')[:100]}</h4>
                <p><strong>Severity:</strong> {finding.get('severity', 'N/A')}</p>
                <p><strong>CVE:</strong> {finding.get('cve', 'N/A')}</p>
                <p><strong>Source:</strong> {finding.get('source', 'N/A')}</p>
                <p><strong>Risk Score:</strong> {finding.get('risk_score', 'N/A')}</p>
            </div>
            """
        
        # Attack Paths
        paths_html = ""
        for path in self.attack_paths:
            steps_html = "".join([f'<li>{step}</li>' for step in path.get('steps', [])])
            paths_html += f"""
            <div class="path">
                <h3>{path.get('name', 'N/A')}</h3>
                <p><strong>Priority:</strong> {path.get('priority', 'N/A')}</p>
                <ol>{steps_html}</ol>
            </div>
            """
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>CTF Assessment Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; border-left: 4px solid #3498db; padding-left: 10px; }}
        .asset {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .finding {{ padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #ccc; }}
        .critical {{ border-left-color: #e74c3c; background: #fde8e8; }}
        .high {{ border-left-color: #e67e22; background: #fef3e8; }}
        .medium {{ border-left-color: #f1c40f; background: #fef9e8; }}
        .low {{ border-left-color: #2ecc71; background: #e8fef0; }}
        .path {{ background: #e8f4fd; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .summary {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; margin: 20px 0; }}
        .summary-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; }}
        .summary-item {{ text-align: center; background: #34495e; padding: 15px; border-radius: 5px; }}
        .summary-number {{ font-size: 32px; font-weight: bold; }}
        ul {{ list-style-type: none; padding-left: 0; }}
        ul li {{ padding: 3px 0; }}
    </style>
</head>
<body>
<div class="container">
    <h1>CTF Assessment Report</h1>
    
    <div class="summary">
        <h2>Executive Summary</h2>
        <div class="summary-grid">
            <div class="summary-item">
                <div class="summary-number">{len(self.assets)}</div>
                <div>Assets</div>
            </div>
            <div class="summary-item">
                <div class="summary-number">{len([p for ip in self.assets for p in self.assets[ip].get('ports', [])])}</div>
                <div>Open Ports</div>
            </div>
            <div class="summary-item">
                <div class="summary-number">{len(self.findings)}</div>
                <div>Findings</div>
            </div>
            <div class="summary-item">
                <div class="summary-number">{len(self.attack_paths)}</div>
                <div>Attack Paths</div>
            </div>
        </div>
    </div>
    
    <h2>1. Asset Inventory</h2>
    {assets_html}
    
    <h2>2. Vulnerability Findings</h2>
    {findings_html if findings_html else '<p>No findings found.</p>'}
    
    <h2>3. Attack Paths</h2>
    {paths_html if paths_html else '<p>No attack paths identified.</p>'}
    
    <h2>4. Recommendations</h2>
    <ul>
        <li>Apply security patches for identified vulnerabilities</li>
        <li>Review and harden configurations</li>
        <li>Implement security best practices</li>
        <li>Regular security assessments</li>
    </ul>
    
    <p style="text-align: center; margin-top: 40px; color: #999; border-top: 1px solid #ddd; padding-top: 20px;">
        Generated by CTF Recon & Reporting Assistant v2.0<br>
        {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </p>
</div>
</body>
</html>"""
        
        self.save_text(html, "report.html")
        print(f"  {Fore.GREEN}✓ {Fore.WHITE}HTML Report generated")

    def generate_markdown_report(self):
        """Generate Markdown Report"""
        self.log("Generating Markdown report...", "INFO")
        
        md = f"""# CTF Assessment Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Target:** {self.target if self.target else 'N/A'}

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Assets | {len(self.assets)} |
| Open Ports | {len([p for ip in self.assets for p in self.assets[ip].get('ports', [])])} |
| Findings | {len(self.findings)} |
| Attack Paths | {len(self.attack_paths)} |

---

## 1. Asset Inventory

"""
        
        for ip, data in self.assets.items():
            md += f"""
### Host: {ip}
- **OS:** {data.get('os', 'Unknown')}
- **Open Ports:**
"""
            for p in data.get('ports', [])[:10]:
                md += f"  - {p['port']}/{p['protocol']} - {p['service']} ({p['product']} {p['version']})\n"
        
        md += f"""
---

## 2. Vulnerability Findings

"""
        
        for finding in self.findings[:20]:
            md += f"""
### {finding.get('title', 'N/A')[:80]}
- **Severity:** {finding.get('severity', 'N/A')}
- **CVE:** {finding.get('cve', 'N/A')}
- **Source:** {finding.get('source', 'N/A')}
- **Risk Score:** {finding.get('risk_score', 'N/A')}
- **Final Severity:** {finding.get('final_severity', 'N/A')}
"""
        
        md += f"""
---

## 3. Attack Paths

"""
        
        for path in self.attack_paths:
            md += f"""
### {path.get('name', 'N/A')}
- **Priority:** {path.get('priority', 'N/A')}
- **Steps:**
"""
            for step in path.get('steps', []):
                md += f"  1. {step}\n"
        
        md += f"""
---

## 4. Recommendations

1. Apply security patches for identified vulnerabilities
2. Review and harden configurations
3. Implement security best practices
4. Regular security assessments

---

*Generated by CTF Recon & Reporting Assistant v2.0*
"""
        
        self.save_text(md, "report.md")
        print(f"  {Fore.GREEN}✓ {Fore.WHITE}Markdown Report generated")

    def generate_plain_report(self):
        """Generate Plain Text Report"""
        self.log("Generating Plain Text report...", "INFO")
        
        report = f"""
================================================================================
                        CTF ASSESSMENT REPORT
================================================================================

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Target: {self.target if self.target else 'N/A'}

================================================================================
SUMMARY
================================================================================

Assets: {len(self.assets)}
Open Ports: {len([p for ip in self.assets for p in self.assets[ip].get('ports', [])])}
Findings: {len(self.findings)}
Attack Paths: {len(self.attack_paths)}

================================================================================
ASSET INVENTORY
================================================================================

"""
        
        for ip, data in self.assets.items():
            report += f"""
Host: {ip}
OS: {data.get('os', 'Unknown')}
Open Ports:
"""
            for p in data.get('ports', [])[:10]:
                report += f"  - {p['port']}/{p['protocol']} - {p['service']} ({p['product']} {p['version']})\n"
        
        report += f"""
================================================================================
VULNERABILITY FINDINGS
================================================================================

"""
        
        for finding in self.findings[:20]:
            report += f"""
Title: {finding.get('title', 'N/A')}
Severity: {finding.get('severity', 'N/A')}
CVE: {finding.get('cve', 'N/A')}
Source: {finding.get('source', 'N/A')}
Risk Score: {finding.get('risk_score', 'N/A')}
Final Severity: {finding.get('final_severity', 'N/A')}
-------------------------------------------------------------------------------
"""
        
        report += f"""
================================================================================
ATTACK PATHS
================================================================================

"""
        
        for path in self.attack_paths:
            report += f"""
Path: {path.get('name', 'N/A')}
Priority: {path.get('priority', 'N/A')}
Steps:
"""
            for i, step in enumerate(path.get('steps', []), 1):
                report += f"  {i}. {step}\n"
        
        report += f"""
================================================================================
RECOMMENDATIONS
================================================================================

1. Apply security patches for identified vulnerabilities
2. Review and harden configurations
3. Implement security best practices
4. Regular security assessments

================================================================================
Generated by CTF Recon & Reporting Assistant v2.0
================================================================================
"""
        
        self.save_text(report, "report.txt")
        print(f"  {Fore.GREEN}✓ {Fore.WHITE}Plain Text Report generated")

    # ========== 8. Dashboard ==========
    def show_dashboard(self):
        """Show operator dashboard"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.MAGENTA}{Style.BRIGHT}📊 OPERATOR DASHBOARD")
        print(f"{Fore.CYAN}{'='*70}")
        
        print(f"\n{Fore.GREEN}Target: {Fore.WHITE}{self.target if self.target else 'N/A'}")
        print(f"{Fore.GREEN}Assets: {Fore.WHITE}{len(self.assets)}")
        
        # Open ports summary
        all_ports = []
        for ip in self.assets:
            for p in self.assets[ip].get('ports', []):
                all_ports.append(p)
        
        print(f"{Fore.GREEN}Open Ports: {Fore.WHITE}{len(all_ports)}")
        
        # Services
        services = {}
        for p in all_ports:
            svc = p.get('service', 'unknown')
            services[svc] = services.get(svc, 0) + 1
        
        print(f"\n{Fore.YELLOW}Services:")
        for svc, count in sorted(services.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {Fore.CYAN}→ {Fore.WHITE}{svc}: {count}")
        
        # Findings by severity
        severity_counts = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0}
        for f in self.findings:
            sev = f.get('severity', 'Medium')
            if sev in severity_counts:
                severity_counts[sev] += 1
        
        print(f"\n{Fore.RED}Findings by Severity:")
        for sev, count in severity_counts.items():
            if count > 0:
                color = Fore.RED if sev in ['Critical', 'High'] else Fore.YELLOW if sev == 'Medium' else Fore.GREEN
                print(f"  {color}→ {Fore.WHITE}{sev}: {count}")
        
        # Attack paths
        print(f"\n{Fore.MAGENTA}Attack Paths:")
        for path in self.attack_paths:
            print(f"  {Fore.GREEN}→ {Fore.WHITE}{path.get('name', 'N/A')} ({path.get('priority', 'N/A')})")
        
        print(f"\n{Fore.CYAN}{'='*70}")

    # ========== 9. Main Workflow ==========
    def run(self):
        """اجرای کامل پروفایل"""
        self.log("🚀 Starting CTF Recon & Reporting Assistant", "CRITICAL")
        
        start_time = time.time()
        
        # Step 1: Run Tools
        if self.target:
            self.run_tools()
        
        # Step 2: Parse Results
        self.parse_nmap()
        self.parse_whatweb()
        self.parse_nuclei()
        self.parse_nikto()
        self.parse_gobuster()
        
        # Step 3: Correlate
        self.correlate_findings()
        
        # Step 4: Calculate Risk
        self.calculate_risk()
        
        # Step 5: Build Attack Paths
        self.build_attack_paths()
        
        # Step 6: Show Dashboard
        self.show_dashboard()
        
        # Step 7: Generate Reports
        self.generate_html_report()
        self.generate_markdown_report()
        self.generate_plain_report()
        
        # Step 8: Save Data
        self.save_json({
            'assets': self.assets,
            'findings': self.findings,
            'attack_paths': self.attack_paths,
            'correlation': self.correlation_map
        }, 'full_data.json')
        
        elapsed = time.time() - start_time
        print(f"\n{Fore.GREEN}{'='*70}")
        print(f"{Fore.MAGENTA}{Style.BRIGHT}✅ REPORTING COMPLETE")
        print(f"{Fore.GREEN}{'='*70}")
        print(f"{Fore.CYAN}⏱️  Time: {elapsed:.2f} seconds")
        print(f"{Fore.CYAN}📁 Output: {self.output_dir}")
        print(f"{Fore.CYAN}📊 Reports:")
        print(f"  {Fore.GREEN}→ {Fore.WHITE}report.html")
        print(f"  {Fore.GREEN}→ {Fore.WHITE}report.md")
        print(f"  {Fore.GREEN}→ {Fore.WHITE}report.txt")
        print(f"{Fore.GREEN}{'='*70}\n")

# ==================== Main ====================
def main():
    if len(sys.argv) < 2:
        print(f"""
{Fore.CYAN}████████ CTF RECON & REPORTING ASSISTANT v2.0 ████████
{Fore.YELLOW}
Usage:
  python3 ctf_reporter.py -t <target>        # Run full scan + report
  python3 ctf_reporter.py -i <input_dir>     # Parse existing results
  python3 ctf_reporter.py -t <target> --parse # Parse only (no scanning)

{Fore.GREEN}Examples:
  python3 ctf_reporter.py -t 192.168.1.10
  python3 ctf_reporter.py -t example.com --parse
  python3 ctf_reporter.py -i ./results/

{Fore.CYAN}Features:
  • Automated Tool Execution (Nmap, WhatWeb, Nikto, Nuclei, Gobuster)
  • Multi-Format Parser (XML, JSON, TXT, HTML)
  • Correlation Engine (Deduplication)
  • Risk Scoring Engine
  • Attack Path Analysis
  • Multi-Format Reports (HTML, MD, TXT)
  • Operator Dashboard

{Fore.YELLOW}⚠️  Use only on authorized targets!
{Fore.RESET}""")
        sys.exit(1)
    
    target = ""
    input_dir = ""
    parse_only = False
    
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '-t':
            target = sys.argv[i+1]
            i += 2
        elif sys.argv[i] == '-i':
            input_dir = sys.argv[i+1]
            i += 2
        elif sys.argv[i] == '--parse':
            parse_only = True
            i += 1
        else:
            i += 1
    
    assistant = CTFReconAssistant(target, input_dir)
    
    if parse_only:
        # Only parse existing results
        assistant.parse_nmap()
        assistant.parse_whatweb()
        assistant.parse_nuclei()
        assistant.parse_nikto()
        assistant.parse_gobuster()
        assistant.correlate_findings()
        assistant.calculate_risk()
        assistant.build_attack_paths()
        assistant.show_dashboard()
        assistant.generate_html_report()
        assistant.generate_markdown_report()
        assistant.generate_plain_report()
        assistant.save_json({
            'assets': assistant.assets,
            'findings': assistant.findings,
            'attack_paths': assistant.attack_paths,
            'correlation': assistant.correlation_map
        }, 'full_data.json')
    else:
        assistant.run()

if __name__ == "__main__":
    main()