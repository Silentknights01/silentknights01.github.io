#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Silent Knights - Daily Cyber News Fetcher
این اسکریپت اخبار روز دنیای سایبری را از منابع معتبر دریافت می‌کند
"""

import feedparser
import json
import os
import re
from datetime import datetime, timedelta
import hashlib
import html

# ===== تنظیمات =====
RSS_FEEDS = [
    "https://feeds.feedburner.com/TheHackersNews",
    "https://www.bleepingcomputer.com/feed/",
    "https://krebsonsecurity.com/feed/",
    "https://www.cisa.gov/cybersecurity-advisories/all.xml",
    "https://threatpost.com/feed/",
]

# مسیرهای فایل‌ها
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS_DIR = os.path.join(BASE_DIR, "_posts")
DATA_DIR = os.path.join(BASE_DIR, "_data")
PUBLISHED_FILE = os.path.join(DATA_DIR, "published_news.json")
INDEX_FILE = os.path.join(DATA_DIR, "news_index.json")

# ===== توابع کمکی =====

def clean_summary(summary):
    """پاک‌سازی خلاصه خبر از تگ‌های HTML"""
    if not summary:
        return ""
    # حذف تگ‌های HTML
    clean = re.sub(r'<[^>]+>', '', summary)
    # حذف کاراکترهای اضافی
    clean = re.sub(r'\s+', ' ', clean).strip()
    # محدود کردن به ۲۰۰ کاراکتر
    if len(clean) > 200:
        clean = clean[:197] + "..."
    return clean

def detect_category(text):
    """تشخیص دسته‌بندی خودکار خبر بر اساس کلمات کلیدی"""
    text_lower = text.lower()
    
    categories = {
        "vulnerability": [
            "vulnerability", "cve", "zero-day", "patch", "update", "bug", 
            "exploit", "security flaw", "critical", "advisory", "vulnerable",
            "آسیب‌پذیری", "روزنه", "نقص امنیتی"
        ],
        "attack": [
            "attack", "breach", "hack", "data leak", "compromise", "cyber attack",
            "ransomware attack", "ddos", "phishing", "intrusion", "malicious",
            "حمله", "نفوذ", "هک", "خرابی داده"
        ],
        "malware": [
            "malware", "virus", "trojan", "ransomware", "worm", "backdoor",
            "spyware", "adware", "rootkit", "keylogger", "badware",
            "بدافزار", "ویروس", "تروجان", "باج‌افزار"
        ],
        "cybercrime": [
            "cybercrime", "hacker", "ransom", "phishing", "scam", "fraud",
            "cyber criminal", "data breach", "identity theft",
            "جرایم سایبری", "کلاهبرداری", "فیشینگ"
        ],
        "technology": [
            "ai", "machine learning", "cloud", "blockchain", "quantum",
            "iot", "5g", "automation", "digital", "cyber",
            "هوش مصنوعی", "یادگیری ماشین", "ابر", "بلاکچین"
        ]
    }
    
    for category, keywords in categories.items():
        if any(keyword in text_lower for keyword in keywords):
            return category
    
    return "general"

def get_category_label(category):
    """دریافت برچسب فارسی دسته‌بندی"""
    labels = {
        "vulnerability": "آسیب‌پذیری",
        "attack": "حمله",
        "malware": "بدافزار",
        "cybercrime": "جرایم سایبری",
        "technology": "فناوری",
        "general": "عمومی"
    }
    return labels.get(category, "عمومی")

def get_source_name(url):
    """دریافت نام منبع از URL"""
    source_map = {
        "thehackernews.com": "The Hacker News",
        "bleepingcomputer.com": "Bleeping Computer",
        "krebsonsecurity.com": "Krebs on Security",
        "cisa.gov": "CISA",
        "threatpost.com": "Threatpost"
    }
    for domain, name in source_map.items():
        if domain in url:
            return name
    return "منبع ناشناس"

def fetch_news_from_rss(feeds, days_back=2):
    """دریافت اخبار از RSS فیدها"""
    all_news = []
    cutoff_date = datetime.now() - timedelta(days=days_back)
    
    for feed_url in feeds:
        try:
            print(f"📡 Fetching: {feed_url}")
            feed = feedparser.parse(feed_url)
            
            if feed.bozo:
                print(f"⚠️ Warning: {feed_url} - {feed.bozo_exception}")
            
            for entry in feed.entries:
                try:
                    # تبدیل تاریخ
                    pub_date = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        pub_date = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        pub_date = datetime(*entry.updated_parsed[:6])
                    else:
                        pub_date = datetime.now()
                    
                    # فقط اخبار جدید
                    if pub_date < cutoff_date:
                        continue
                    
                    # ساخت شناسه یکتا
                    news_id = hashlib.md5(entry.link.encode()).hexdigest()[:10]
                    
                    # دریافت خلاصه
                    summary = ""
                    if hasattr(entry, 'summary'):
                        summary = entry.summary
                    elif hasattr(entry, 'description'):
                        summary = entry.description
                    
                    # دریافت عنوان
                    title = entry.title if hasattr(entry, 'title') else "بدون عنوان"
                    
                    news_item = {
                        "id": news_id,
                        "title": html.unescape(title),
                        "link": entry.link,
                        "summary": clean_summary(summary),
                        "source": get_source_name(feed_url),
                        "source_link": entry.link,
                        "published": pub_date.isoformat(),
                        "category": detect_category(title + " " + summary),
                        "category_label": get_category_label(detect_category(title + " " + summary))
                    }
                    all_news.append(news_item)
                    
                except Exception as e:
                    print(f"⚠️ Error processing entry: {e}")
                    continue
                    
        except Exception as e:
            print(f"❌ Error fetching {feed_url}: {e}")
    
    return all_news

def load_published_news():
    """بارگذاری لیست اخبار منتشر شده قبلی"""
    if os.path.exists(PUBLISHED_FILE):
        try:
            with open(PUBLISHED_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return set(data.get("published_ids", []))
        except:
            return set()
    return set()

def save_published_news(news_ids):
    """ذخیره لیست اخبار منتشر شده"""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(PUBLISHED_FILE, 'w', encoding='utf-8') as f:
        json.dump({"published_ids": list(news_ids)}, f, indent=2, ensure_ascii=False)

def generate_blog_post(news_item):
    """تولید فایل Markdown برای خبر"""
    os.makedirs(POSTS_DIR, exist_ok=True)
    
    # ساخت نام فایل
    date = datetime.now().strftime('%Y-%m-%d')
    title_slug = re.sub(r'[^\w\s-]', '', news_item['title'])
    title_slug = re.sub(r'[-\s]+', '-', title_slug).strip('-')[:50]
    filename = f"{date}-{title_slug}.md"
    filepath = os.path.join(POSTS_DIR, filename)
    
    # اگر فایل وجود دارد، رد کن
    if os.path.exists(filepath):
        return False
    
    # محتوای Markdown
    content = f"""---
title: "{news_item['title']}"
date: {date}
category: "{news_item['category']}"
category_label: "{news_item['category_label']}"
source: "{news_item['source']}"
source_link: "{news_item['source_link']}"
original_link: "{news_item['link']}"
---

## 🛡️ خلاصه خبر

{news_item['summary']}

---

### 📊 اطلاعات بیشتر

| مورد | توضیح |
|------|-------|
| **منبع** | [{news_item['source']}]({news_item['source_link']}) |
| **تاریخ انتشار اصلی** | {news_item['published']} |
| **دسته‌بندی** | {news_item['category_label']} |

---
*این خبر به‌صورت خودکار از منابع معتبر گردآوری شده است.*
"""
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def generate_news_index():
    """تولید فایل ایندکس از تمام پست‌ها برای نمایش در سایت"""
    os.makedirs(DATA_DIR, exist_ok=True)
    
    news_list = []
    
    if not os.path.exists(POSTS_DIR):
        with open(INDEX_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, indent=2, ensure_ascii=False)
        return
    
    for filename in os.listdir(POSTS_DIR):
        if filename.endswith('.md'):
            filepath = os.path.join(POSTS_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # استخراج Frontmatter
                    frontmatter = {}
                    if content.startswith('---'):
                        parts = content.split('---', 2)
                        if len(parts) >= 3:
                            import yaml
                            try:
                                frontmatter = yaml.safe_load(parts[1])
                            except:
                                # اگر yaml نصب نبود، ساده استخراج کن
                                for line in parts[1].split('\n'):
                                    if ':' in line:
                                        key, val = line.split(':', 1)
                                        frontmatter[key.strip()] = val.strip().strip('"\'')
                    
                    # استخراج خلاصه (بعد از frontmatter)
                    body = content.split('---', 2)[-1].strip()
                    summary_lines = body.split('\n')
                    summary = ""
                    for line in summary_lines:
                        if line.strip() and not line.startswith('#'):
                            summary = line.strip()
                            break
                    
                    if not summary:
                        summary = frontmatter.get('summary', 'خلاصه‌ای موجود نیست.')
                    
                    news_item = {
                        'id': filename.replace('.md', ''),
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

def main():
    """اجرای اصلی برنامه"""
    print("=" * 60)
    print("🛡️  Silent Knights - Daily Cyber News Fetcher")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # دریافت اخبار جدید
    print("\n📡 Fetching news from RSS feeds...")
    new_news = fetch_news_from_rss(RSS_FEEDS, days_back=2)
    
    if not new_news:
        print("⚠️ No new news found.")
        generate_news_index()
        return
    
    print(f"📰 Found {len(new_news)} news items.")
    
    # بارگذاری اخبار منتشر شده قبلی
    published_ids = load_published_news()
    
    # فیلتر اخبار تکراری
    fresh_news = [n for n in new_news if n['id'] not in published_ids]
    
    if not fresh_news:
        print("✅ All news already published.")
        generate_news_index()
        return
    
    print(f"📝 {len(fresh_news)} new news items to publish.")
    
    # تولید پست‌های بلاگ
    created_count = 0
    for news in fresh_news:
        if generate_blog_post(news):
            published_ids.add(news['id'])
            created_count += 1
            print(f"✅ Created: {news['title'][:50]}...")
    
    # ذخیره وضعیت انتشار
    save_published_news(published_ids)
    
    # تولید ایندکس
    generate_news_index()
    
    print("\n" + "=" * 60)
    print(f"🎉 Successfully published {created_count} new posts.")
    print(f"📊 Total published news: {len(published_ids)}")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
