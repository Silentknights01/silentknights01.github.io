#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Silent Knights - News Index Generator
این اسکریپت فایل ایندکس اخبار را برای نمایش در سایت تولید می‌کند
"""

import os
import json
import re
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS_DIR = os.path.join(BASE_DIR, "_posts")
DATA_DIR = os.path.join(BASE_DIR, "_data")
INDEX_FILE = os.path.join(DATA_DIR, "news_index.json")

def extract_frontmatter(content):
    """استخراج Frontmatter از فایل Markdown"""
    frontmatter = {}
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            for line in parts[1].split('\n'):
                line = line.strip()
                if ':' in line:
                    key, val = line.split(':', 1)
                    frontmatter[key.strip()] = val.strip().strip('"\'')
    return frontmatter

def generate_news_index():
    """تولید فایل ایندکس از تمام پست‌ها"""
    os.makedirs(DATA_DIR, exist_ok=True)
    
    news_list = []
    
    if not os.path.exists(POSTS_DIR):
        with open(INDEX_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, indent=2, ensure_ascii=False)
        print("⚠️ _posts directory not found, created empty index")
        return
    
    for filename in os.listdir(POSTS_DIR):
        if filename.endswith('.md'):
            filepath = os.path.join(POSTS_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # استخراج Frontmatter
                    frontmatter = extract_frontmatter(content)
                    
                    # استخراج خلاصه (بعد از frontmatter)
                    body = content.split('---', 2)[-1].strip()
                    summary_lines = [line.strip() for line in body.split('\n') if line.strip() and not line.startswith('#')]
                    summary = summary_lines[0] if summary_lines else "خلاصه‌ای موجود نیست."
                    
                    # حذف تاریخ از عنوان فایل برای ID
                    file_id = filename.replace('.md', '')
                    
                    news_item = {
                        'id': file_id,
                        'title': frontmatter.get('title', 'بدون عنوان'),
                        'date': frontmatter.get('date', datetime.now().isoformat()),
                        'category': frontmatter.get('category', 'general'),
                        'category_label': frontmatter.get('category_label', 'عمومی'),
                        'source': frontmatter.get('source', 'منبع ناشناس'),
                        'source_link': frontmatter.get('source_link', '#'),
                        'url': f"/posts/{filename.replace('.md', '.html')}",
                        'summary': summary[:150] + ('...' if len(summary) > 150 else '')
                    }
                    news_list.append(news_item)
            except Exception as e:
                print(f"⚠️ Error reading {filename}: {e}")
                continue
    
    # مرتب‌سازی بر اساس تاریخ (جدیدترین اول)
    news_list.sort(key=lambda x: x['date'], reverse=True)
    
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(news_list, f, indent=2, ensure_ascii=False)
    
    print(f"✅ News index generated with {len(news_list)} items.")
    return len(news_list)

if __name__ == "__main__":
    print("🛡️  Silent Knights - News Index Generator")
    generate_news_index()