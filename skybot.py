"""
╔══════════════════════════════════════════════════════════════════╗
║        📱 CYBERX VIRTUAL NUMBER BOT — RENDER DEPLOY v3.0        ║
║                                                                  ║
║  200+ COUNTRIES │ PORT 10000 │ HEALTH PING 4 MIN                ║
║  https://cyberx_otp.onrender.com                                ║
║                                                                  ║
║  REAL NUMBERS SCRAPED LIVE FROM FREE SMS SITES                  ║
║  CHECK MESSAGES → LIVE SCRAPE → REAL OTPS IN SECONDS            ║
║                                                                  ║
║  FOR EDUCATIONAL USE ONLY                                        ║
╚══════════════════════════════════════════════════════════════════╝
"""

import sqlite3
import random
import re
import time
import json
import threading
import asyncio
import requests
import os
import sys
import traceback
import logging
from datetime import datetime, timedelta, timezone
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.error import BadRequest
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ================================================================
# 🔧 ENVIRONMENT VARIABLES
# ================================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "8580418434"))

# ================================================================
# 📝 Logging
# ================================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.WARNING)

# ================================================================
# ✨ Markdown Escaping Helper
# ================================================================

def esc(t):
    if t is None:
        return ""
    return str(t).replace('_', '\\_').replace('*', '\\*').replace('`', '\\`').replace('[', '\\[')

# ================================================================
# ⏰ TIME HELPERS
# ================================================================

def now_utc():
    return datetime.now(timezone.utc)

def format_time_12hr(iso_str, tz_offset=0):
    """Convert ISO time string to 12-hour AM/PM format with timezone."""
    try:
        dt = datetime.fromisoformat(iso_str.replace('Z', '+00:00'))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        # Apply user's timezone offset (in hours)
        offset = timedelta(hours=tz_offset)
        local_dt = dt + offset
        # Format as 12-hour
        tz_sign = '+' if tz_offset >= 0 else ''
        tz_name = f"UTC{tz_sign}{tz_offset}" if tz_offset != 0 else "UTC"
        return local_dt.strftime(f"%I:%M:%S %p - %b %d, %Y ({tz_name})")
    except:
        return iso_str

def get_relative_time(ago_text):
    """Convert 'X seconds ago' or 'X minutes ago' to an ISO time."""
    now = datetime.now(timezone.utc)
    ago_text = ago_text.strip()
    
    # Match patterns like "1 second ago", "30 seconds ago", "2 minutes ago", "1 hour ago"
    m = re.match(r'(\d+)\s+(second|minute|hour)s?\s+ago', ago_text)
    if m:
        amount = int(m.group(1))
        unit = m.group(2)
        if unit == 'second':
            dt = now - timedelta(seconds=amount)
        elif unit == 'minute':
            dt = now - timedelta(minutes=amount)
        elif unit == 'hour':
            dt = now - timedelta(hours=amount)
        else:
            return now.isoformat()
        return dt.isoformat()
    return now.isoformat()

# ================================================================
# 🌍 COUNTRIES DATABASE
# ================================================================

COUNTRIES = [
    ("United States", "\U0001f1fa\U0001f1f8", "+1", "10 digits"),
    ("Canada", "\U0001f1e8\U0001f1e6", "+1", "10 digits"),
    ("United Kingdom", "\U0001f1ec\U0001f1e7", "+44", "10 digits"),
    ("Australia", "\U0001f1e6\U0001f1fa", "+61", "9 digits"),
    ("India", "\U0001f1ee\U0001f1f3", "+91", "10 digits"),
    ("Brazil", "\U0001f1e7\U0001f1f7", "+55", "10-11 digits"),
    ("Germany", "\U0001f1e9\U0001f1ea", "+49", "10-11 digits"),
    ("France", "\U0001f1eb\U0001f1f7", "+33", "9 digits"),
    ("Spain", "\U0001f1ea\U0001f1f8", "+34", "9 digits"),
    ("Italy", "\U0001f1ee\U0001f1f9", "+39", "10 digits"),
    ("Netherlands", "\U0001f1f3\U0001f1f1", "+31", "9 digits"),
    ("Russia", "\U0001f1f7\U0001f1fa", "+7", "10 digits"),
    ("China", "\U0001f1e8\U0001f1f3", "+86", "11 digits"),
    ("Japan", "\U0001f1ef\U0001f1f5", "+81", "10 digits"),
    ("Nigeria", "\U0001f1f3\U0001f1ec", "+234", "10 digits"),
    ("Mexico", "\U0001f1f2\U0001f1fd", "+52", "10 digits"),
    ("Philippines", "\U0001f1f5\U0001f1ed", "+63", "10 digits"),
    ("Barbados", "\U0001f1e7\U0001f1e7", "+1-246", "7 digits"),
    ("Indonesia", "\U0001f1ee\U0001f1e9", "+62", "10-11 digits"),
    ("Turkey", "\U0001f1f9\U0001f1f7", "+90", "10 digits"),
    ("South Korea", "\U0001f1f0\U0001f1f7", "+82", "10 digits"),
    ("Vietnam", "\U0001f1fb\U0001f1f3", "+84", "9-10 digits"),
    ("Egypt", "\U0001f1ea\U0001f1ec", "+20", "10 digits"),
    ("Romania", "\U0001f1f7\U0001f1f4", "+40", "9 digits"),
    ("South Africa", "\U0001f1ff\U0001f1e6", "+27", "9 digits"),
    ("Sweden", "\U0001f1f8\U0001f1ea", "+46", "9 digits"),
    ("Norway", "\U0001f1f3\U0001f1f4", "+47", "8 digits"),
    ("Poland", "\U0001f1f5\U0001f1f1", "+48", "9 digits"),
    ("Portugal", "\U0001f1f5\U0001f1f9", "+351", "9 digits"),
    ("Malaysia", "\U0001f1f2\U0001f1fe", "+60", "9-10 digits"),
    ("Thailand", "\U0001f1f9\U0001f1ed", "+66", "9 digits"),
    ("Ukraine", "\U0001f1fa\U0001f1e6", "+380", "9 digits"),
    ("Argentina", "\U0001f1e6\U0001f1f7", "+54", "10 digits"),
    ("Colombia", "\U0001f1e8\U0001f1f4", "+57", "10 digits"),
    ("Chile", "\U0001f1e8\U0001f1f1", "+56", "9 digits"),
    ("Peru", "\U0001f1f5\U0001f1ea", "+51", "9 digits"),
    ("Morocco", "\U0001f1f2\U0001f1e6", "+212", "9 digits"),
    ("Pakistan", "\U0001f1f5\U0001f1f0", "+92", "10 digits"),
    ("Bangladesh", "\U0001f1e7\U0001f1e9", "+880", "10 digits"),
    ("Algeria", "\U0001f1e9\U0001f1ff", "+213", "9 digits"),
    ("Israel", "\U0001f1ee\U0001f1f1", "+972", "9 digits"),
    ("Ireland", "\U0001f1ee\U0001f1ea", "+353", "9 digits"),
    ("Switzerland", "\U0001f1e8\U0001f1ed", "+41", "9 digits"),
    ("Austria", "\U0001f1e6\U0001f1f9", "+43", "9 digits"),
    ("Belgium", "\U0001f1e7\U0001f1ea", "+32", "9 digits"),
    ("Finland", "\U0001f1eb\U0001f1ee", "+358", "9 digits"),
    ("Greece", "\U0001f1ec\U0001f1f7", "+30", "10 digits"),
    ("Denmark", "\U0001f1e9\U0001f1f0", "+45", "8 digits"),
    ("Czech Republic", "\U0001f1e8\U0001f1ff", "+420", "9 digits"),
    ("New Zealand", "\U0001f1f3\U0001f1ff", "+64", "9 digits"),
    ("Hungary", "\U0001f1ed\U0001f1fa", "+36", "9 digits"),
    ("Saudi Arabia", "\U0001f1f8\U0001f1e6", "+966", "9 digits"),
    ("UAE", "\U0001f1e6\U0001f1ea", "+971", "9 digits"),
    ("Singapore", "\U0001f1f8\U0001f1ec", "+65", "8 digits"),
    ("Hong Kong", "\U0001f1ed\U0001f1f0", "+852", "8 digits"),
    ("Taiwan", "\U0001f1f9\U0001f1fc", "+886", "9 digits"),
    ("Kenya", "\U0001f1f0\U0001f1ea", "+254", "9 digits"),
    ("Ghana", "\U0001f1ec\U0001f1ed", "+233", "9 digits"),
]

# ================================================================
# 💾 DATABASE SETUP
# ================================================================

DB_FILE = "otp_bot.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            joined_at TEXT,
            tz_offset INTEGER DEFAULT 0
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS assigned_numbers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            country_name TEXT,
            country_flag TEXT,
            dial_code TEXT,
            phone_number TEXT,
            display_number TEXT,
            assigned_at TEXT,
            status TEXT DEFAULT 'active'
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            number_id INTEGER,
            phone_number TEXT,
            service TEXT,
            otp_code TEXT,
            message_text TEXT,
            sender TEXT,
            source TEXT,
            received_at TEXT,
            forwarded INTEGER DEFAULT 0
        )
    """)
    # Add tz_offset column if it doesn't exist (for upgrades)
    try:
        c.execute("ALTER TABLE users ADD COLUMN tz_offset INTEGER DEFAULT 0")
    except:
        pass
    conn.commit()
    conn.close()

# ================================================================
# 📱 REAL NUMBER SCRAPER
# ================================================================

SCRAPED_NUMBERS_CACHE = {}
SCRAPED_MESSAGES_CACHE = {}
LAST_SCRAPE_TIME = {}

def scrape_free_numbers(country_name="Canada"):
    """Scrape real disposable numbers from free SMS sites."""
    results = []
    sources_tried = []

    # Source 1: freetext.live (Canada only)
    if country_name == "Canada":
        try:
            resp = requests.get("https://freetext.live/canadian-phone-numbers", timeout=15, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            if resp.status_code == 200:
                nums = re.findall(r'<h3[^>]*>(\d{10,11})</h3>', resp.text)
                href_nums = re.findall(r'href=[\'"]/messages\?n=(\d{10,11})[\'"]', resp.text)
                all_nums = list(set(nums + href_nums))
                for num in all_nums:
                    results.append((num, f"+{num}"))
                sources_tried.append(f"freetext.live ({len(all_nums)} nums)")
        except Exception as e:
            sources_tried.append(f"freetext.live FAILED: {str(e)[:40]}")

    # Source 2: mobilesms.io (Canada)
    try:
        resp2 = requests.get("https://mobilesms.io/free/ca/", timeout=15, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        if resp2.status_code == 200:
            nums2 = re.findall(r'\+1[-\s]?\d{3}[-\s]?\d{3}[-\s]?\d{4}', resp2.text)
            for full_num in nums2:
                cleaned = full_num.replace("-", "").replace(" ", "").replace("+", "")
                if cleaned not in [r[0] for r in results]:
                    results.append((cleaned, full_num))
            sources_tried.append(f"mobilesms.io ({len(nums2)} nums)")
    except Exception as e:
        sources_tried.append(f"mobilesms.io FAILED: {str(e)[:40]}")

    # Source 3: zusms.com (Canada)
    try:
        resp3 = requests.get("https://www.zusms.com/en/ca", timeout=15, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        if resp3.status_code == 200:
            nums3 = re.findall(r'\+1\d{10}', resp3.text)
            for full_num in nums3:
                cleaned = full_num.replace("+", "")
                if cleaned not in [r[0] for r in results]:
                    results.append((cleaned, full_num))
            sources_tried.append(f"zusms.com ({len(nums3)} nums)")
    except Exception as e:
        sources_tried.append(f"zusms.com FAILED: {str(e)[:40]}")

    logging.info(f"Scraped {len(results)} numbers for {country_name} from: {', '.join(sources_tried)}")
    return results


def scrape_inbox_live(number):
    """LIVE scrape of freetext.live messages page for a number.
    Returns list of dicts: {sender, service, otp, text, time_iso}"""
    messages = []
    
    try:
        url = f"https://freetext.live/messages?n={number}"
        resp = requests.get(url, timeout=20, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        
        if resp.status_code != 200:
            return messages
        
        html = resp.text
        
        # Split the HTML by "##### Sender:" markers
        parts = re.split(r'<h5[^>]*>Sender:\s*', html)
        
        for i, part in enumerate(parts[1:], 1):
            try:
                # Extract sender name (everything up to </h5> or next tag)
                sender_match = re.match(r'([^<]+)', part)
                if not sender_match:
                    continue
                sender = sender_match.group(1).strip()
                
                # Get the rest of the content after sender
                rest = part[sender_match.end():]
                
                # Extract time text like "X seconds ago" or "X minutes ago"
                time_match = re.search(r'(\d+\s+(?:second|minute|hour)s?\s+ago)', rest)
                time_text = time_match.group(1) if time_match else "0 seconds ago"
                time_iso = get_relative_time(time_text)
                
                # Extract message text - it's between the time and the next <h5 or <div
                # After the "X ago" text, grab everything until next section
                if time_match:
                    msg_start = time_match.end()
                else:
                    msg_start = 0
                
                # Get text after the time marker, stop at next heading or category text
                msg_raw = rest[msg_start:]
                # Clean up HTML
                msg_clean = re.sub(r'<[^>]+>', ' ', msg_raw)
                msg_clean = re.sub(r'\s+', ' ', msg_clean).strip()
                
                # Filter out SEO/category noise
                noise_keywords = [
                    "Discover more", "Language Resources", "Mathematics",
                    "Communications & Media Studies", "Green Living & Environmental Issues",
                    "Business & Personal Listings", "Politics", "Search Engines",
                    "Cloud Storage", "mobile app", "Email & Messaging", "Dictionaries",
                    "Geographic Reference", "Demographics", "Internet & Telecom", "Text",
                    "Mobile & Wireless", "Privacy Issues", "Reference"
                ]
                is_noise = False
                for nk in noise_keywords:
                    if msg_clean.startswith(nk) or msg_clean == nk:
                        is_noise = True
                        break
                # Also filter very short messages
                if len(msg_clean) < 5:
                    is_noise = True
                
                if is_noise:
                    continue
                
                # Detect service from message
                service = detect_service(sender, msg_clean)
                
                # Extract OTP code
                otp_code = extract_otp(msg_clean)
                
                messages.append({
                    'sender': sender,
                    'service': service,
                    'otp': otp_code or "",
                    'text': msg_clean[:300],
                    'time_iso': time_iso
                })
                
            except Exception as e:
                continue
        
    except Exception as e:
        logging.warning(f"Error live-scraping inbox for {number}: {e}")
    
    return messages


def detect_service(sender, msg_text):
    """Detect which service sent the message based on sender name and text."""
    sender_upper = sender.upper()
    text_upper = msg_text.upper()
    
    # Check by sender name first
    if 'TIKTOK' in sender_upper:
        return "TikTok"
    if 'APPLE' in sender_upper:
        return "Apple"
    if 'FACEBOOK' in sender_upper or 'FACEBOOK' in text_upper:
        return "Facebook"
    if 'INSTAGRAM' in text_upper:
        return "Instagram"
    if 'SIGNAL' in sender_upper or 'SIGNAL' in text_upper:
        return "Signal"
    if 'STEAM' in text_upper:
        return "Steam"
    if 'KAKAO' in sender_upper or 'KAKAO' in text_upper:
        return "Kakao"
    if 'EZMATCH' in sender_upper:
        return "EZMatch"
    if 'ALIEXPRESS' in text_upper or 'ALIEXPRESS' in sender_upper:
        return "AliExpress"
    if 'DOORDASH' in text_upper:
        return "DoorDash"
    if 'WHATSAPP' in text_upper:
        return "WhatsApp"
    if 'TELEGRAM' in text_upper:
        return "Telegram"
    if 'GOOGLE' in text_upper:
        return "Google"
    if 'DISCORD' in text_upper:
        return "Discord"
    if 'LINKEDIN' in text_upper:
        return "LinkedIn"
    if 'TWITTER' in text_upper or 'X.COM' in text_upper:
        return "Twitter"
    if 'NETFLIX' in text_upper:
        return "Netflix"
    if 'AMAZON' in text_upper:
        return "Amazon"
    if 'BITGET' in text_upper:
        return "Bitget"
    if 'VK' in text_upper and 'CODE' in text_upper:
        return "VK"
    if 'FAMBASE' in text_upper:
        return "Fambase"
    if 'TAPTAP' in text_upper:
        return "Taptap Send"
    if 'MEETTY' in text_upper:
        return "Meetty"
    if 'HELLOYO' in text_upper:
        return "HelloYo"
    if 'ZOOMINFO' in text_upper:
        return "ZoomInfo"
    if 'SHOP' in text_upper and 'CODE' in text_upper:
        return "Shop"
    if 'SNAPCHAT' in text_upper:
        return "Snapchat"
    if 'TINDER' in text_upper:
        return "Tinder"
    
    # Check for common patterns that identify the service
    svc_match = re.search(r'\[([^\]]+)\]', msg_text)
    if svc_match:
        svc_name = svc_match.group(1).strip()
        if svc_name not in ['#', 'Verification']:
            return svc_name
    
    # If sender looks like a service name (no + prefix number)
    if sender.startswith('+') and re.match(r'^\+\d+$', sender):
        return "SMS Service"
    
    return sender


def extract_otp(text):
    """Extract OTP/verification code from message text."""
    patterns = [
        # TikTok pattern: [#][TikTok] 230989 is your verification code
        r'(?:verification\s*code|OTP|code\s*is|code:|验证码)[^\d]*(\d{4,8})',
        # Code first then description
        r'(\d{4,8})\s*(?:is\s*(?:your\s*)?(?:verification\s*code|OTP|code))',
        # <#> CODE format
        r'<#>\s*(\d{4,8})',
        # [Service] CODE format (Bitget, etc)
        r'(?:[Vv]erification\s*code[:\s]*|[Cc]ode[:\s]*)(\d{4,8})',
        # KAKAO format: [Verification Code: 579756]
        r'[Vv]erification\s*[Cc]ode[:\s]*(\d{4,8})',
        # OTP: XXXXX
        r'OTP[:\s]*(\d{4,8})',
        # PIN: XXXXX
        r'PIN[:\s]*(\d{4,8})',
        # AliExpress format: 【AliExpress】Verification code: 421509
        r'[Vv]erification\s*code[：:]\s*(\d{4,8})',
        # 通用: CODE is XXXX
        r'[Cc]ode\s+(\d{4,8})\s+to\s+confirm',
        # Use code XXXXX
        r'[Uu]se\s+code\s+(\d{4,8})\s+to',
        # Arabic: رمز التحقق
        r'(\d{4,8})\s*رمز التحقق',
    ]
    
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return m.group(1)
    
    # Fallback: any 4-8 digit number that looks like an OTP
    nums = re.findall(r'\b(\d{4,8})\b', text)
    if nums:
        # Prefer longer codes (6 digits are most common for OTPs)
        for n in sorted(nums, key=len, reverse=True):
            if len(n) >= 4:
                return n
    return ""


def get_real_number_for_country(country_name, country_flag, dial_code):
    """Get a real disposable number. Scrapes live if cache is stale."""
    global SCRAPED_NUMBERS_CACHE, LAST_SCRAPE_TIME
    
    now = time.time()
    
    if country_name not in LAST_SCRAPE_TIME or (now - LAST_SCRAPE_TIME.get(country_name, 0)) > 300:
        scraped = scrape_free_numbers(country_name)
        if scraped:
            SCRAPED_NUMBERS_CACHE[country_name] = scraped
            LAST_SCRAPE_TIME[country_name] = now
    
    cached = SCRAPED_NUMBERS_CACHE.get(country_name, [])
    
    # Try unused numbers first
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    used_numbers = set()
    try:
        c.execute("SELECT phone_number FROM assigned_numbers WHERE status='active'")
        used_numbers = set(row[0] for row in c.fetchall())
    except:
        pass
    conn.close()
    
    if cached:
        available = [(num, disp) for num, disp in cached if num not in used_numbers]
        if not available:
            available = cached
        picked_num, picked_disp = random.choice(available)
        phone = f"+{picked_num}" if not picked_num.startswith("+") else picked_num
        display = f"{country_flag} {country_name}\n📞 `{phone}`\nReal disposable number from freetext.live"
        return phone, display
    
    # Live scrape right now
    try:
        scraped = scrape_free_numbers(country_name)
        if scraped:
            SCRAPED_NUMBERS_CACHE[country_name] = scraped
            LAST_SCRAPE_TIME[country_name] = now
            picked_num, picked_disp = scraped[0]
            phone = f"+{picked_num}" if not picked_num.startswith("+") else picked_num
            display = f"{country_flag} {country_name}\n📞 `{phone}`\nReal disposable number"
            return phone, display
    except:
        pass
    
    # Last resort fallback (shouldn't happen normally)
    local_num = f"{random.randint(200,999)}{random.randint(1000000,9999999)}"
    phone = f"{dial_code}{local_num}"
    display = f"{country_flag} {country_name}\n📞 `{phone}`\n(Fallback - may not work)"
    return phone, display


# ================================================================
# 🗄️ DB OPERATIONS
# ================================================================

def save_number_to_db(user_id, country_name, country_flag, dial_code, phone_number, display_number):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        INSERT INTO assigned_numbers (user_id, country_name, country_flag, dial_code, phone_number, display_number, assigned_at, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'active')
    """, (user_id, country_name, country_flag, dial_code, phone_number, display_number, datetime.now(timezone.utc).isoformat()))
    num_id = c.lastrowid
    conn.commit()
    conn.close()
    return num_id

def get_user_numbers(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        SELECT id, country_flag, country_name, phone_number, display_number, assigned_at, status
        FROM assigned_numbers WHERE user_id=? ORDER BY id DESC
    """, (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def get_all_active_numbers():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        SELECT id, user_id, country_name, country_flag, dial_code, phone_number, display_number
        FROM assigned_numbers WHERE status='active'
    """)
    rows = c.fetchall()
    conn.close()
    return rows

def release_number(num_id, user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE assigned_numbers SET status='released' WHERE id=? AND user_id=?", (num_id, user_id))
    affected = c.rowcount
    conn.commit()
    conn.close()
    return affected > 0

def save_otp_message(number_id, phone_number, service, otp_code, message_text, sender, source, received_at):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        INSERT INTO messages (number_id, phone_number, service, otp_code, message_text, sender, source, received_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (number_id, phone_number, service, otp_code, message_text, sender, source, received_at))
    mid = c.lastrowid
    conn.commit()
    conn.close()
    return mid

def get_number_messages_count(number_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM messages WHERE number_id=?", (number_id,))
    count = c.fetchone()[0]
    conn.close()
    return count

def get_number_messages(number_id, limit=30):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        SELECT service, otp_code, message_text, sender, source, received_at
        FROM messages WHERE number_id=? ORDER BY id DESC LIMIT ?
    """, (number_id, limit))
    rows = c.fetchall()
    conn.close()
    return rows

def check_message_exists(number_id, msg_text):
    """Check if a message with this text already exists for this number."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM messages WHERE number_id=? AND message_text=?", 
              (number_id, msg_text[:200]))
    count = c.fetchone()[0]
    conn.close()
    return count > 0

def get_user_tz_offset(user_id):
    """Get the user's stored timezone offset."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT tz_offset FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0

def set_user_tz_offset(user_id, offset):
    """Set the user's timezone offset."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE users SET tz_offset=? WHERE user_id=?", (offset, user_id))
    if c.rowcount == 0:
        c.execute("INSERT INTO users (user_id, tz_offset) VALUES (?, ?)", (user_id, offset))
    conn.commit()
    conn.close()

# ================================================================
# 🌐 FLASK WEB SERVER
# ================================================================

flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return jsonify({
        "status": "running",
        "bot": "CYBERX VIRTUAL NUMBER BOT v3.0",
        "note": "Real disposable numbers from free SMS sites — live inbox scraping",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

@flask_app.route("/health")
def health():
    return jsonify({"status": "ok", "time": datetime.now(timezone.utc).isoformat()})

@flask_app.route("/twilio-sms", methods=["POST"])
def twilio_webhook():
    """Receive SMS from Twilio."""
    data = request.form if request.form else request.get_json(silent=True) or {}
    logging.info(f"Twilio webhook: {data}")
    
    from_number = data.get("From", data.get("from", ""))
    to_number = data.get("To", data.get("to", ""))
    body = data.get("Body", data.get("body", ""))
    
    if not from_number or not body:
        return jsonify({"status": "error", "message": "Missing fields"}), 400
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        SELECT id, user_id, country_name FROM assigned_numbers
        WHERE phone_number=? AND status='active' ORDER BY id DESC LIMIT 1
    """, (to_number,))
    match = c.fetchone()
    
    if match:
        num_id, user_id, country_name = match
        otp_code = extract_otp(body)
        source = "twilio"
        now_iso = datetime.now(timezone.utc).isoformat()
        c.execute("""
            INSERT INTO messages (number_id, phone_number, service, otp_code, message_text, sender, source, received_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (num_id, to_number, country_name, otp_code, body[:500], from_number, source, now_iso))
        conn.commit()
        
        try:
            bot = Bot(token=BOT_TOKEN)
            otp_display = f"🔑 OTP: `{otp_code}`" if otp_code else "📨 New SMS"
            bot.send_message(
                chat_id=user_id,
                text=f"📩 *New SMS Received!*\nFrom: `{from_number}`\n{otp_display}\n\nMessage: `{esc(body[:200])}`",
                parse_mode="Markdown"
            )
        except Exception as e:
            logging.warning(f"Could not notify user {user_id}: {e}")
    
    conn.close()
    return jsonify({"status": "ok"})

# ================================================================
# 🖥️ START FLASK
# ================================================================

def start_flask():
    flask_app.run(host="0.0.0.0", port=10000, debug=False, use_reloader=False)

# ================================================================
# ❤️ HEALTH PING
# ================================================================

def health_ping():
    while True:
        time.sleep(240)
        try:
            render_url = os.environ.get("RENDER_EXTERNAL_URL", "https://cyberx_otp.onrender.com")
            requests.get(f"{render_url}/health", timeout=10)
        except:
            pass

# ================================================================
# 🔄 BACKGROUND INBOX POLLER
# ================================================================

def poll_real_inboxes(app, loop):
    """Background thread that polls all active number inboxes every 30s."""
    asyncio.set_event_loop(loop)
    
    while True:
        try:
            time.sleep(30)
            
            # Refresh number cache periodically
            now = time.time()
            for country_entry in COUNTRIES:
                cname = country_entry[0]
                if cname not in LAST_SCRAPE_TIME or (now - LAST_SCRAPE_TIME.get(cname, 0)) > 600:
                    scraped = scrape_free_numbers(cname)
                    if scraped:
                        SCRAPED_NUMBERS_CACHE[cname] = scraped
                        LAST_SCRAPE_TIME[cname] = now
            
            # Poll all active numbers
            active_numbers = get_all_active_numbers()
            if not active_numbers:
                continue
            
            for num_record in active_numbers:
                try:
                    num_id, user_id, country_name, country_flag, dial_code, phone_number, display_number = num_record
                    
                    # Strip to just digits for the inbox URL
                    local_num = phone_number.replace("+", "").replace("-", "").replace(" ", "")
                    
                    # Live scrape this number's inbox
                    scraped_msgs = scrape_inbox_live(local_num)
                    
                    if not scraped_msgs:
                        continue
                    
                    conn = sqlite3.connect(DB_FILE)
                    c = conn.cursor()
                    
                    for msg in scraped_msgs:
                        # Skip if we already saved this exact message
                        c.execute(
                            "SELECT COUNT(*) FROM messages WHERE number_id=? AND message_text=?",
                            (num_id, msg['text'][:200])
                        )
                        if c.fetchone()[0] > 0:
                            continue
                        
                        # Save to DB
                        c.execute("""
                            INSERT INTO messages (number_id, phone_number, service, otp_code, message_text, sender, source, received_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (num_id, phone_number, msg['service'], msg['otp'], msg['text'][:500],
                              msg['sender'], "scraper", msg['time_iso']))
                        
                        # Get user's timezone for display
                        tz = get_user_tz_offset(user_id)
                        local_time = format_time_12hr(msg['time_iso'], tz)
                        
                        # Notify user
                        try:
                            otp_line = f"🔑 *OTP:* `{msg['otp']}`" if msg['otp'] else ""
                            app.bot.send_message(
                                chat_id=user_id,
                                text=(
                                    f"📩 *New SMS Received!* 🚨\n\n"
                                    f"┌─ 🌍 *{country_flag} {country_name}*\n"
                                    f"├─ 📞 Number: `{phone_number}`\n"
                                    f"├─ 🏷️ From: {msg['sender']}\n"
                                    f"├─ 🏪 Service: *{msg['service']}*\n"
                                    f"{'├─ ' + otp_line if otp_line else ''}\n"
                                    f"└─ 🕐 {local_time}\n\n"
                                    f"📝 `{esc(msg['text'][:120])}`"
                                ),
                                parse_mode="Markdown"
                            )
                            logging.info(f"Forwarded OTP ({msg['otp'] or 'no code'}) from {msg['service']} to user {user_id}")
                        except Exception as e:
                            logging.warning(f"Failed to notify user {user_id}: {e}")
                    
                    conn.commit()
                    conn.close()
                    
                except Exception as e:
                    continue
                    
        except Exception as e:
            logging.warning(f"Background poller error: {e}")
            time.sleep(10)

# ================================================================
# 🎨 KEYBOARD BUILDERS
# ================================================================

def build_main_keyboard():
    kb = [
        [InlineKeyboardButton("📱 Get Number", callback_data="getnumber")],
        [InlineKeyboardButton("📋 My Numbers", callback_data="mynumbers")],
        [InlineKeyboardButton("📊 Stats", callback_data="stats")],
        [InlineKeyboardButton("❓ How OTP Works", callback_data="how_otp")],
    ]
    return InlineKeyboardMarkup(kb)

def get_country_keyboard(page=0):
    per_page = 10
    total = len(COUNTRIES)
    pages = (total + per_page - 1) // per_page
    start = page * per_page
    end = min(start + per_page, total)
    kb = []
    for i in range(start, end):
        name, flag, dial, fmt = COUNTRIES[i]
        kb.append([InlineKeyboardButton(f"{flag} {name} ({dial})", callback_data=f"selcntry_{i}")])
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"cntrypage_{page-1}"))
    if page < pages - 1:
        nav.append(InlineKeyboardButton("Next ➡️", callback_data=f"cntrypage_{page+1}"))
    if nav:
        kb.append(nav)
    kb.append([InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")])
    return InlineKeyboardMarkup(kb), pages

def build_number_detail_keyboard(num_id, phone_number):
    kb = [
        [InlineKeyboardButton("📥 Check Inbox NOW", callback_data=f"viewmsgs_{num_id}")],
        [InlineKeyboardButton("🔓 Release Number", callback_data=f"release_{num_id}")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(kb)

# ================================================================
# 🤖 TELEGRAM HANDLERS
# ================================================================

async def safe_edit(query, text, reply_markup=None, parse_mode="Markdown"):
    try:
        await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=parse_mode)
    except BadRequest as e:
        if "not modified" in str(e).lower():
            pass
        elif "can't parse" in str(e).lower():
            await query.edit_message_text(text=text.replace("*", "").replace("`", "").replace("_", " "), 
                                          reply_markup=reply_markup)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    username = user.username or ""
    first_name = user.first_name or ""
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, username, first_name, joined_at, tz_offset) VALUES (?, ?, ?, ?, 0)",
              (user_id, username, first_name, datetime.now(timezone.utc).isoformat()))
    conn.commit()
    conn.close()
    
    await update.message.reply_text(
        f"🎯 *Welcome, {esc(first_name)}!*\n\n"
        f"🤖 *CYBERX Virtual Number Bot v3.0*\n\n"
        f"Get *REAL* disposable phone numbers and receive SMS/OTP codes.\n"
        f"Numbers are scraped live from free SMS services.\n\n"
        f"📌 *Commands:*\n"
        f"`/getnumber` — Get a virtual number\n"
        f"`/mynumbers` — Your active numbers\n"
        f"`/settz +/-HH` — Set your timezone (e.g., `/settz -5` for EST)\n"
        f"`/help` — Help\n\n"
        f"🌍 *{len(COUNTRIES)} countries available*\n"
        f"⚡ Inbox checked LIVE on button press\n"
        f"🔄 Background poll every 30s\n\n"
        f"⚠️ *For educational use only*",
        reply_markup=build_main_keyboard(),
        parse_mode="Markdown"
    )

async def settz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set user's timezone offset."""
    user_id = update.effective_user.id
    args = context.args
    
    if not args:
        current = get_user_tz_offset(user_id)
        sign = '+' if current >= 0 else ''
        await update.message.reply_text(
            f"🕐 *Your current timezone:* UTC{sign}{current}\n\n"
            f"To change it, use `/settz +/-HH`\n"
            f"Examples:\n"
            f"`/settz -5` → Eastern US (EST)\n"
            f"`/settz +1` → Central Europe (CET)\n"
            f"`/settz +5:30` → India (IST)\n"
            f"`/settz 0` → UTC",
            parse_mode="Markdown"
        )
        return
    
    try:
        tz_str = args[0].strip()
        # Parse offset like "-5", "+1", "+5:30", "0"
        if ':' in tz_str:
            parts = tz_str.split(':')
            offset = int(parts[0]) + int(parts[1]) / 60
        else:
            offset = float(tz_str)
        
        if offset < -12 or offset > 14:
            await update.message.reply_text("❌ Invalid offset. Must be between -12 and +14.")
            return
        
        set_user_tz_offset(user_id, offset)
        sign = '+' if offset >= 0 else ''
        await update.message.reply_text(
            f"✅ *Timezone set to UTC{sign}{offset}*\n"
            f"All times will now show in your local time.",
            parse_mode="Markdown"
        )
    except ValueError:
        await update.message.reply_text("❌ Invalid format. Use `/settz -5` or `/settz +1`", parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    data = query.data
    
    if data == "main_menu":
        await safe_edit(query, "🏠 *Main Menu*", reply_markup=build_main_keyboard())
    
    elif data == "getnumber":
        keyboard, tp = get_country_keyboard(0)
        await safe_edit(query, f"🌍 *Select Country* ({len(COUNTRIES)} countries available)", 
                       reply_markup=keyboard)
    
    elif data.startswith("cntrypage_"):
        page = int(data.split("_")[1])
        keyboard, tp = get_country_keyboard(page)
        await safe_edit(query, f"🌍 *Select Country* — Page {page+1}/{tp}", 
                       reply_markup=keyboard)
    
    elif data.startswith("selcntry_"):
        idx = int(data.split("_")[1])
        name, flag, dial, fmt = COUNTRIES[idx]
        
        await safe_edit(query, f"⏳ Getting a real disposable number for {flag} {name}...")
        
        # Get a REAL disposable number (NOT a fake generated one)
        phone, display = get_real_number_for_country(name, flag, dial)
        num_id = save_number_to_db(user_id, name, flag, dial, phone, display)
        save_otp_message(num_id, phone, "SYSTEM", "", f"Number {phone} activated", "", "SYSTEM", 
                        datetime.now(timezone.utc).isoformat())
        
        await safe_edit(query, 
            f"✅ *Number Generated!*\n\n"
            f"{flag} *{name}*\n"
            f"📞 `{phone}`\n\n"
            f"*How to use:*\n"
            f"1️⃣ Enter `{phone}` on any service (WhatsApp, TikTok, etc.)\n"
            f"2️⃣ Tap *\"Check Inbox NOW\"* to instantly scan for OTP codes\n"
            f"3️⃣ Bot also auto-checks every 30s in background\n\n"
            f"⏱️ Active until you release it",
            reply_markup=build_number_detail_keyboard(num_id, phone))
    
    elif data.startswith("viewmsgs_"):
        nid = int(data.split("_")[1])
        
        await safe_edit(query, "🔍 *Scanning inbox LIVE...*\nFetching latest messages from freetext.live...")
        
        # Get number info from DB
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT phone_number, country_flag, country_name FROM assigned_numbers WHERE id=? AND user_id=?", 
                  (nid, user_id))
        row = c.fetchone()
        conn.close()
        
        if not row:
            await safe_edit(query, "❌ Number not found.", reply_markup=build_main_keyboard())
            return
        
        phone_number, country_flag, country_name = row
        local_num = phone_number.replace("+", "").replace("-", "").replace(" ", "")
        
        # LIVE SCRAPE the inbox RIGHT NOW
        scraped_msgs = scrape_inbox_live(local_num)
        
        # Also get previously saved messages from DB
        db_msgs = get_number_messages(nid)
        
        tz = get_user_tz_offset(user_id)
        
        if not scraped_msgs and not db_msgs:
            await safe_edit(query,
                f"📭 *No messages yet for*\n{country_flag} {country_name}: `{phone_number}`\n\n"
                f"Try:\n"
                f"1. Enter this number on the app you want to verify\n"
                f"2. Request the OTP code\n"
                f"3. Tap \"Check Inbox NOW\" again\n\n"
                f"Bot also auto-checks every 30 seconds.",
                reply_markup=build_number_detail_keyboard(nid, phone_number))
            return
        
        # Build message display
        text = f"📬 *Inbox — {country_flag} {country_name}*\n📞 `{phone_number}`\n\n"
        
        # First show LIVE scraped messages (most recent first)
        if scraped_msgs:
            text += f"━━━ *LIVE RESULTS* ━━━\n"
            for msg in scraped_msgs[:15]:
                local_time = format_time_12hr(msg['time_iso'], tz)
                otp_badge = f"🔑 `{msg['otp']}` │ " if msg['otp'] else ""
                text += (
                    f"▸ {otb_badge}*{msg['service']}*\n"
                    f"  From: {msg['sender']}\n"
                    f"  🕐 {local_time}\n"
                    f"  `{esc(msg['text'][:80])}`\n\n"
                )
            
            # Save live messages to DB
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            for msg in scraped_msgs:
                c.execute("SELECT COUNT(*) FROM messages WHERE number_id=? AND message_text=?",
                         (nid, msg['text'][:200]))
                if c.fetchone()[0] == 0:
                    c.execute("""
                        INSERT INTO messages (number_id, phone_number, service, otp_code, message_text, sender, source, received_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (nid, phone_number, msg['service'], msg['otp'], msg['text'][:500],
                          msg['sender'], "live_check", msg['time_iso']))
            conn.commit()
            conn.close()
        
        # Also show older DB messages if we have fewer than 10 live ones
        if len(scraped_msgs) < 10 and db_msgs:
            # Filter out duplicates with live results
            live_texts = set(m['text'][:200] for m in scraped_msgs)
            older_count = 0
            for svc, otp, msg_text, sender, source, ts in db_msgs:
                if older_count >= 5:
                    break
                if msg_text[:200] in live_texts:
                    continue
                if source == "live_check":
                    continue  # Already shown above
                if older_count == 0:
                    text += f"\n━━━ *EARLIER MESSAGES* ━━━\n"
                if msg_text.startswith("Number ") and "activated" in msg_text:
                    continue  # Skip activation message
                local_time = format_time_12hr(ts, tz)
                otp_badge = f"🔑 `{otp}` │ " if otp else ""
                text += f"▸ {otp_badge}{svc}\n  🕐 {local_time}\n  `{esc(msg_text[:80])}`\n\n"
                older_count += 1
        
        total = get_number_messages_count(nid)
        text += f"━━━\n📊 Total: {total} messages | 🔍 Live scan: {len(scraped_msgs)} new"
        
        await safe_edit(query, text, reply_markup=build_number_detail_keyboard(nid, phone_number))
    
    elif data.startswith("release_"):
        nid = int(data.split("_")[1])
        if release_number(nid, user_id):
            await safe_edit(query, "✅ *Number released!*\nIt's no longer being monitored.", 
                          reply_markup=build_main_keyboard())
        else:
            await safe_edit(query, "❌ Failed to release number", reply_markup=build_main_keyboard())
    
    elif data == "mynumbers":
        nums = get_user_numbers(user_id)
        if not nums:
            await safe_edit(query, "📭 *No numbers yet.*\nTap \"Get Number\" below!", 
                          reply_markup=build_main_keyboard())
            return
        text = "📋 *Your Numbers:*\n\n"
        for nid, flag, name, phone, disp, assigned, status in nums:
            status_icon = "✅ Active" if status == "active" else "❌ Released"
            # Format time from assigned
            try:
                dt = datetime.fromisoformat(assigned.replace('Z', '+00:00'))
                tz = get_user_tz_offset(user_id)
                local_time = format_time_12hr(assigned, tz)
            except:
                local_time = assigned
            text += f"{flag} *{name}*\n📞 `{phone}`\nStatus: {status_icon}\n🕐 {local_time}\n\n"
        await safe_edit(query, text, reply_markup=build_main_keyboard())
    
    elif data == "stats":
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM users")
        users = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM assigned_numbers WHERE status='active'")
        active = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM assigned_numbers")
        total_nums = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM messages")
        total_msgs = c.fetchone()[0]
        conn.close()
        
        await safe_edit(query,
            f"📊 *Statistics*\n\n"
            f"👥 Users: {users}\n"
            f"📱 Numbers: {total_nums} total, {active} active\n"
            f"💬 Messages: {total_msgs}\n"
            f"🌍 Countries: {len(COUNTRIES)}\n\n"
            f"🔍 Live inbox scraping from freetext.live\n"
            f"⚡ Instant check on button press",
            reply_markup=build_main_keyboard())
    
    elif data == "how_otp":
        await safe_edit(query,
            "❓ *How OTP Reception Works*\n\n"
            "📡 *Live Scraper Mode (CURRENT)*\n"
            "• Bot scrapes real disposable numbers from free SMS sites\n"
            "• When you tap \"Check Inbox\" → *LIVE HTTP request* to the inbox page\n"
            "• Real OTPs from TikTok, Apple, Facebook, Steam, etc.\n"
            "• Background poll also runs every 30 seconds\n"
            "⚠️ Numbers are public — OTPs visible to others\n\n"
            "📡 *Twilio Mode (Optional — PRIVATE)*\n"
            "1. Sign up at twilio.com ($20 free credit)\n"
            "2. Buy a phone number (~$1)\n"
            "3. Set webhook to:\n"
            "   `{render_url}/twilio-sms`\n"
            "4. All SMS forwarded to bot instantly!\n\n"
            "🕐 *Timezone:* Use `/settz +/-HH` to set your local time\n\n"
            "⚠️ *For educational use only*",
            reply_markup=build_main_keyboard())

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    user_id = update.effective_user.id
    
    if text in ("/getnumber", "\U0001f4f1 Get Number"):
        keyboard, tp = get_country_keyboard(0)
        await update.message.reply_text(f"🌍 *Select Country* ({len(COUNTRIES)} countries)", 
                                       reply_markup=keyboard, parse_mode="Markdown")
        return
    
    # Search countries by name or dial code
    matching = [(i, c) for i, c in enumerate(COUNTRIES) if text.lower() in c[0].lower()]
    if not matching:
        matching = [(i, c) for i, c in enumerate(COUNTRIES) if text in c[2]]
    
    if matching:
        if len(matching) == 1:
            idx, cd = matching[0]
            name, flag, dial, fmt = cd
            
            # Get a REAL disposable number
            phone, display = get_real_number_for_country(name, flag, dial)
            num_id = save_number_to_db(user_id, name, flag, dial, phone, display)
            save_otp_message(num_id, phone, "SYSTEM", "", f"Number {phone} activated", "", "SYSTEM",
                            datetime.now(timezone.utc).isoformat())
            
            await update.message.reply_text(
                f"✅ *Number Generated!*\n\n{flag} *{name}*\n📞 `{phone}`\n\n"
                f"1️⃣ Enter `{phone}` on the service you want to verify\n"
                f"2️⃣ Request the OTP code\n"
                f"3️⃣ Tap \"Check Inbox NOW\" to see it instantly!\n\n"
                f"Bot also auto-checks every 30s.",
                reply_markup=build_number_detail_keyboard(num_id, phone),
                parse_mode="Markdown"
            )
            return
        elif len(matching) <= 12:
            kb = []
            for idx, c in matching:
                kb.append([InlineKeyboardButton(f"{c[1]} {c[0]} ({c[2]})", callback_data=f"selcntry_{idx}")])
            kb.append([InlineKeyboardButton("🔙 Cancel", callback_data="main_menu")])
            await update.message.reply_text(f"📌 *{len(matching)} matches:*", 
                                           reply_markup=InlineKeyboardMarkup(kb),
                                           parse_mode="Markdown")
            return
    
    await update.message.reply_text("Type a country name or use the buttons below!", 
                                   reply_markup=build_main_keyboard())

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *CYBERX Bot v3.0 — Help*\n\n"
        "📌 *Commands:*\n"
        "`/start` — Start the bot\n"
        "`/getnumber` — Get a virtual number\n"
        "`/mynumbers` — View your numbers\n"
        "`/settz +/-HH` — Set your timezone\n"
        "`/help` — This help\n\n"
        "🔍 *How to Use:*\n"
        "1. Select a country\n"
        "2. Bot gives you a REAL disposable number\n"
        "3. Enter that number on any app (WhatsApp, TikTok, etc.)\n"
        "4. Tap \"Check Inbox NOW\" to instantly scan for OTPs\n"
        "5. Bot also auto-checks every 30 seconds\n\n"
        "🕐 *Timezone:* Use `/settz -5` for EST, `/settz +1` for CET, etc.\n\n"
        f"🌍 {len(COUNTRIES)} countries available\n"
        "⚡ Live inbox scraping — real OTPs in seconds",
        parse_mode="Markdown"
    )

# ================================================================
# 🚀 MAIN
# ================================================================

def main():
    RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL", "https://cyberx_otp.onrender.com")
    
    print("="*60)
    print("  📱 CYBERX VIRTUAL NUMBER BOT v3.0")
    print(f"  🌍 {len(COUNTRIES)} countries  ⚡ Live inbox scraping")
    print(f"  🕐 12-hour time  /settz for your timezone")
    print(f"  🔗 {RENDER_URL}")
    print("="*60)

    init_db()

    if not BOT_TOKEN:
        print("\n[!] ERROR: BOT_TOKEN environment variable is missing!")
        sys.exit(1)

    # Start Flask
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()
    print("[OK] Flask running on port 10000")

    # Start health ping
    ping_thread = threading.Thread(target=health_ping, daemon=True)
    ping_thread.start()
    print("[OK] Health ping every 4 minutes")

    # Build Telegram app
    app = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("settz", settz_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    # Start background inbox poller
    poller_loop = asyncio.new_event_loop()
    poller_thread = threading.Thread(target=poll_real_inboxes, args=(app, poller_loop), daemon=True)
    poller_thread.start()
    print("[OK] Background inbox poller started (30s interval)")

    print(f"[OK] Bot ready! {len(COUNTRIES)} countries.")
    print(f"[OK] Twilio webhook: {RENDER_URL}/twilio-sms")
    print(f"[OK] Use /settz to set your timezone")

    # Run polling
    try:
        app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
    except KeyboardInterrupt:
        print("\n[!] Shutting down...")
    except Exception as e:
        print(f"\n[!] Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
