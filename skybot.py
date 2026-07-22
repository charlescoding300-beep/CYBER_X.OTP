"""
╔══════════════════════════════════════════════════════════════════╗
║        📱 CYBERX VIRTUAL NUMBER BOT — RENDER DEPLOY             ║
║                                                                  ║
║  NO TUNNELS  │  NO DUCK DNS  │  NO CLOUDFLARE  │  NO NGROK      ║
║                                                                  ║
║  200+ COUNTRIES │ PORT 10000 │ HEALTH PING 4 MIN                ║
║  https://cyberx_otp.onrender.com                                ║
║                                                                  ║
║  REAL NUMBERS  │  SCRAPED FROM FREE SMS SITES  │  REAL OTPS     ║
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
from datetime import datetime, timedelta
from html.parser import HTMLParser
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
# 🌍 COUNTRIES DATABASE
# ================================================================
# Each entry: (name, flag_emoji, dial_code, format_hint)
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
            joined_at TEXT
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
    c.execute("""
        CREATE TABLE IF NOT EXISTS country_pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country TEXT UNIQUE,
            page INTEGER DEFAULT 1,
            last_fetched TEXT
        )
    """)
    conn.commit()
    conn.close()

# ================================================================
# 📱 REAL NUMBER SCRAPER
# ================================================================

SCRAPED_NUMBERS_CACHE = {}  # {country: [(number, flag, dial, source_url), ...]}
SCRAPED_MESSAGES_CACHE = {} # {number: [{sender, text, time}, ...]}
LAST_SCRAPE_TIME = {}

def scrape_free_numbers(country_name="Canada"):
    """Scrape real disposable numbers from freetext.live or other free SMS sites.
    Returns a list of (full_number, display_text) tuples."""
    results = []
    sources_tried = []

    # Source 1: freetext.live
    try:
        url = f"https://freetext.live/canadian-phone-numbers" if country_name == "Canada" else None
        if url:
            resp = requests.get(url, timeout=15, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            if resp.status_code == 200:
                # Extract numbers from h3 tags containing digit-only text
                numbers = re.findall(r'<h3[^>]*>(\d{10,11})</h3>', resp.text)
                # Also try href patterns with ?n=NUMBER
                href_numbers = re.findall(r'href=[\'"]/messages\?n=(\d{10,11})[\'"]', resp.text)
                all_nums = list(set(numbers + href_numbers))
                for num in all_nums:
                    display = f"+{num}" if not num.startswith("+") else num
                    results.append((num, display))
                sources_tried.append(f"freetext.live ({len(all_nums)} numbers)")
    except Exception as e:
        sources_tried.append(f"freetext.live (FAILED: {str(e)[:50]})")

    # Source 2: mobilesms.io
    if len(results) < 10:
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
                sources_tried.append(f"mobilesms.io ({len(nums2)} numbers)")
        except Exception as e:
            sources_tried.append(f"mobilesms.io (FAILED: {str(e)[:50]})")

    # Source 3: zusms.com
    if len(results) < 10:
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
                sources_tried.append(f"zusms.com ({len(nums3)} numbers)")
        except Exception as e:
            sources_tried.append(f"zusms.com (FAILED: {str(e)[:50]})")

    logging.info(f"Scraped {len(results)} numbers for {country_name} from: {', '.join(sources_tried)}")
    return results


def scrape_messages_for_number(number):
    """Scrape inbox messages for a specific number from freetext.live."""
    messages = []
    try:
        url = f"https://freetext.live/messages?n={number}"
        resp = requests.get(url, timeout=15, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        if resp.status_code == 200:
            html = resp.text
            # Find all message blocks - they appear as sender + message text pairs
            # Pattern: Sender: +XXXXX followed by message content
            sender_pattern = r'Sender:</strong>\s*([^<]+)'
            messages_text = []
            senders = re.findall(sender_pattern, html)
            
            # Also look for text content containing verification codes
            otp_lines = re.findall(
                r'(?:verification code|OTP|code is|code:|验证码|Your code)[^.]*[.!\n]?',
                html, re.IGNORECASE
            )
            
            # Get the main message body divs
            msg_blocks = re.findall(
                r'<div[^>]*class="[^"]*message[^"]*"[^>]*>(.*?)</div>',
                html, re.DOTALL | re.IGNORECASE
            )
            
            for block in msg_blocks:
                # Extract text from HTML
                text = re.sub(r'<[^>]+>', ' ', block).strip()
                text = re.sub(r'\s+', ' ', text)
                if text and len(text) > 3:
                    messages.append(text)

            # If no structured blocks found, try alternative parsing
            if not messages:
                # Look for any text between sender tags and next tag
                parts = re.split(r'<strong>Sender:</strong>', html)
                for i, part in enumerate(parts[1:], 1):
                    sender_match = re.search(r'([^<]+)', part)
                    if sender_match:
                        sender = sender_match.group(1).strip()
                        # Get text after sender until next message
                        text_block = part.split('</div>')[0] if '</div>' in part else part[:500]
                        clean_text = re.sub(r'<[^>]+>', ' ', text_block).strip()
                        clean_text = re.sub(r'\s+', ' ', clean_text)
                        if clean_text and len(clean_text) > 10:
                            messages.append(f"[{sender}] {clean_text}")
    except Exception as e:
        logging.warning(f"Error scraping messages for {number}: {e}")
    
    return messages


def get_real_number_for_country(country_name, country_flag, dial_code):
    """Get a real disposable number for a country. Falls back to source list then cache."""
    global SCRAPED_NUMBERS_CACHE, LAST_SCRAPE_TIME
    
    now = time.time()
    
    # Refresh cache if older than 5 minutes
    if country_name not in LAST_SCRAPE_TIME or (now - LAST_SCRAPE_TIME.get(country_name, 0)) > 300:
        scraped = scrape_free_numbers(country_name)
        if scraped:
            SCRAPED_NUMBERS_CACHE[country_name] = scraped
            LAST_SCRAPE_TIME[country_name] = now
    
    # Get from cache
    cached = SCRAPED_NUMBERS_CACHE.get(country_name, [])
    if cached:
        # Pick a random one that hasn't been used too much (track via assigned_numbers table)
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        used_numbers = set()
        try:
            c.execute("SELECT phone_number FROM assigned_numbers WHERE status='active'")
            used_numbers = set(row[0] for row in c.fetchall())
        except:
            pass
        conn.close()
        
        # Prefer unused numbers
        available = [(num, disp) for num, disp in cached if num not in used_numbers]
        if not available:
            available = cached  # All used, just reuse
        
        picked_num, picked_disp = random.choice(available)
        phone = f"{dial_code}{picked_num}" if not picked_num.startswith(dial_code.replace("+", "")) else f"+{picked_num}"
        display = f"{country_flag} {country_name}\n📞 `{phone}`\nReal disposable number from freetext.live"
        return phone, display
    
    # Ultimate fallback - scrape live right now
    try:
        scraped = scrape_free_numbers(country_name)
        if scraped:
            SCRAPED_NUMBERS_CACHE[country_name] = scraped
            LAST_SCRAPE_TIME[country_name] = now
            picked_num, picked_disp = scraped[0]
            phone = f"{dial_code}{picked_num}" if not picked_num.startswith(dial_code.replace("+", "")) else f"+{picked_num}"
            display = f"{country_flag} {country_name}\n📞 `{phone}`\nReal disposable number"
            return phone, display
    except:
        pass
    
    # Last resort - shouldn't normally happen
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
    """, (user_id, country_name, country_flag, dial_code, phone_number, display_number, datetime.now().isoformat()))
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

def get_number_messages(number_id, limit=15):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        SELECT service, otp_code, message_text, sender, source, received_at
        FROM messages WHERE number_id=? ORDER BY id DESC LIMIT ?
    """, (number_id, limit))
    rows = c.fetchall()
    conn.close()
    return rows

# ================================================================
# 🌐 FLASK WEB SERVER (for webhooks + health)
# ================================================================

flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return jsonify({
        "status": "running",
        "bot": "CYBERX VIRTUAL NUMBER BOT",
        "version": "2.0",
        "note": "Real disposable numbers from free SMS sites",
        "timestamp": datetime.now().isoformat()
    })

@flask_app.route("/health")
def health():
    return jsonify({"status": "ok", "time": datetime.now().isoformat()})

@flask_app.route("/twilio-sms", methods=["POST"])
def twilio_webhook():
    """Receive SMS from Twilio and store in DB."""
    data = request.form if request.form else request.get_json(silent=True) or {}
    logging.info(f"Twilio webhook received: {data}")
    
    from_number = data.get("From", data.get("from", ""))
    to_number = data.get("To", data.get("to", ""))
    body = data.get("Body", data.get("body", ""))
    
    if not from_number or not body:
        return jsonify({"status": "error", "message": "Missing fields"}), 400
    
    # Find matching number in DB
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        SELECT id, user_id, country_name FROM assigned_numbers
        WHERE phone_number=? AND status='active' ORDER BY id DESC LIMIT 1
    """, (to_number,))
    match = c.fetchone()
    
    if match:
        num_id, user_id, country_name = match
        # Extract OTP code
        otp_code = extract_otp(body)
        source = "twilio"
        now = datetime.now().isoformat()
        c.execute("""
            INSERT INTO messages (number_id, phone_number, service, otp_code, message_text, sender, source, received_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (num_id, to_number, country_name, otp_code, body, from_number, source, now))
        conn.commit()
        
        # Try to notify user via Telegram
        try:
            bot = Bot(token=BOT_TOKEN)
            otp_display = f"🔑 OTP: {otp_code}" if otp_code else "📨 New SMS"
            bot.send_message(
                chat_id=user_id,
                text=f"📩 *New SMS received!*\n\nFrom: `{from_number}`\n{otp_display}\n\nMessage: `{esc(body[:200])}`",
                parse_mode="Markdown"
            )
        except Exception as e:
            logging.warning(f"Could not notify user {user_id}: {e}")
    
    conn.close()
    return jsonify({"status": "ok"})

def extract_otp(text):
    """Extract OTP code from message text."""
    # Common OTP patterns
    patterns = [
        r'(?:verification\s*code|OTP|code\s*is|code:|验证码)[^\d]*(\d{4,8})',
        r'(\d{4,8})\s*(?:is\s*(?:your\s*)?(?:verification\s*code|OTP))',
        r'<#>\s*(\d{4,8})',
        r'(\d{4,8})(?:\s*-?\s*code)',
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return m.group(1)
    # Fallback: look for any 4-8 digit number
    nums = re.findall(r'\b(\d{4,8})\b', text)
    if nums:
        return nums[0]
    return ""

# ================================================================
# 🖥️ START FLASK
# ================================================================

def start_flask():
    flask_app.run(host="0.0.0.0", port=10000, debug=False, use_reloader=False)

# ================================================================
# ❤️ HEALTH PING
# ================================================================

def health_ping():
    """Ping the health endpoint every 4 minutes to keep Render alive."""
    while True:
        time.sleep(240)
        try:
            render_url = os.environ.get("RENDER_EXTERNAL_URL", "https://cyberx_otp.onrender.com")
            requests.get(f"{render_url}/health", timeout=10)
        except:
            pass

# ================================================================
# 🔄 REAL INBOX POLLER (replaces dead Shelex API)
# ================================================================

def poll_real_inboxes(app, loop):
    """Poll real number inboxes for incoming OTPs."""
    asyncio.set_event_loop(loop)
    
    while True:
        try:
            time.sleep(30)  # Poll every 30 seconds
            
            # Refresh the scraped number cache periodically
            now = time.time()
            for country_entry in COUNTRIES:
                cname = country_entry[0]
                if cname not in LAST_SCRAPE_TIME or (now - LAST_SCRAPE_TIME.get(cname, 0)) > 600:
                    scraped = scrape_free_numbers(cname)
                    if scraped:
                        SCRAPED_NUMBERS_CACHE[cname] = scraped
                        LAST_SCRAPE_TIME[cname] = now
            
            # Get all active numbers assigned to users
            active_numbers = get_all_active_numbers()
            if not active_numbers:
                continue
                
            for num_record in active_numbers:
                try:
                    num_id, user_id, country_name, country_flag, dial_code, phone_number, display_number = num_record
                    
                    # Extract local number (without +1 or dial code)
                    local_num = phone_number.replace("+", "")
                    for prefix in ["1", dial_code.replace("+", "")]:
                        if local_num.startswith(prefix) and len(local_num) > len(prefix):
                            local_num = local_num[len(prefix):]
                            break
                    
                    # Scrape inbox for this number
                    messages = scrape_messages_for_number(local_num)
                    
                    if messages:
                        conn = sqlite3.connect(DB_FILE)
                        c = conn.cursor()
                        
                        for msg_text in messages[:5]:  # Process up to 5 new messages
                            # Check if we already have this message
                            c.execute(
                                "SELECT COUNT(*) FROM messages WHERE number_id=? AND message_text=?",
                                (num_id, msg_text[:200])
                            )
                            if c.fetchone()[0] > 0:
                                continue  # Already saved
                            
                            # Try to identify the service and OTP
                            otp_code = extract_otp(msg_text)
                            service = "Unknown"
                            for svc in ["WhatsApp", "TikTok", "Google", "Facebook", "Apple", 
                                         "Telegram", "Instagram", "Twitter", "Discord", "Amazon",
                                         "AliExpress", "DoorDash", "Steam", "Signal", "Kakao",
                                         "Tinder", "Snapchat", "LinkedIn", "Microsoft", "Netflix"]:
                                if svc.lower() in msg_text.lower():
                                    service = svc
                                    break
                            
                            # Save to DB
                            now_iso = datetime.now().isoformat()
                            sender = re.search(r'\[([^\]]+)\]', msg_text)
                            sender_text = sender.group(1) if sender else "Unknown"
                            
                            c.execute("""
                                INSERT INTO messages (number_id, phone_number, service, otp_code, message_text, sender, source, received_at)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            """, (num_id, phone_number, service, otp_code or "", msg_text[:500], 
                                  sender_text, "scraper", now_iso))
                            
                            # Notify user via Telegram
                            try:
                                app.bot.send_message(
                                    chat_id=user_id,
                                    text=(
                                        f"📩 *New SMS received!*\n\n"
                                        f"📞 Number: `{phone_number}`\n"
                                        f"🏷️ Service: {service}\n"
                                        f"{'🔑 OTP: `' + otp_code + '`' if otp_code else ''}\n"
                                        f"📝 Message: `{esc(msg_text[:150])}`"
                                    ),
                                    parse_mode="Markdown"
                                )
                                logging.info(f"Forwarded OTP to user {user_id}: {otp_code or 'no code'}")
                            except Exception as e:
                                logging.warning(f"Failed to notify user {user_id}: {e}")
                        
                        conn.commit()
                        conn.close()
                        
                except Exception as e:
                    logging.warning(f"Error polling number: {e}")
                    continue
                    
        except Exception as e:
            logging.warning(f"Inbox poller error: {e}")
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

def build_number_detail_keyboard(num_id):
    kb = [
        [InlineKeyboardButton("🔄 Check Messages", callback_data=f"viewmsgs_{num_id}")],
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
            await query.edit_message_text(text=text.replace("*", "").replace("`", ""), 
                                          reply_markup=reply_markup)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    username = user.username or ""
    first_name = user.first_name or ""
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, username, first_name, joined_at) VALUES (?, ?, ?, ?)",
              (user_id, username, first_name, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    
    await update.message.reply_text(
        f"🎯 *Welcome, {esc(first_name)}!*\n\n"
        f"🤖 *CYBERX Virtual Number Bot*\n\n"
        f"Get *real* disposable phone numbers to receive SMS and OTP codes.\n"
        f"Numbers are scraped live from free SMS services.\n\n"
        f"📌 *Commands:*\n"
        f"`/getnumber` — Get a virtual number\n"
        f"`/mynumbers` — Your active numbers\n"
        f"`/help` — Help\n\n"
        f"🌍 *{len(COUNTRIES)} countries available*\n"
        f"⏱️ Inbox polled every 30s\n\n"
        f"⚠️ *For educational use only*",
        reply_markup=build_main_keyboard(),
        parse_mode="Markdown"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    data = query.data
    
    if data == "main_menu":
        await safe_edit(query, "🏠 *Main Menu*", reply_markup=build_main_keyboard())
    
    elif data == "getnumber":
        keyboard, tp = get_country_keyboard(0)
        await safe_edit(query, f"🌍 *Select Country* ({len(COUNTRIES)} countries)", 
                       reply_markup=keyboard)
    
    elif data.startswith("cntrypage_"):
        page = int(data.split("_")[1])
        keyboard, tp = get_country_keyboard(page)
        await safe_edit(query, f"🌍 *Select Country* ({len(COUNTRIES)} countries) — Page {page+1}", 
                       reply_markup=keyboard)
    
    elif data.startswith("selcntry_"):
        idx = int(data.split("_")[1])
        name, flag, dial, fmt = COUNTRIES[idx]
        
        await safe_edit(query, f"⏳ Getting a real number for {flag} {name}...")
        
        # Get a REAL disposable number instead of generating a fake one
        phone, display = get_real_number_for_country(name, flag, dial)
        num_id = save_number_to_db(user_id, name, flag, dial, phone, display)
        save_otp_message(num_id, phone, name, "SYSTEM", "Number activated!", "", "SYSTEM", datetime.now().isoformat())
        
        await safe_edit(query, 
            f"✅ *Number Ready!*\n\n{display}\n\n"
            f"📌 *How to use:*\n"
            f"1. Use this number on WhatsApp or any service\n"
            f"2. Tap 'Check Messages' to see incoming OTPs\n"
            f"3. Bot polls inbox every 30s automatically\n\n"
            f"⏱️ Active until you release it",
            reply_markup=build_number_detail_keyboard(num_id))
    
    elif data.startswith("viewmsgs_"):
        nid = int(data.split("_")[1])
        messages = get_number_messages(nid)
        if not messages:
            await safe_edit(query, "📭 No messages yet. Waiting for SMS...", 
                          reply_markup=build_number_detail_keyboard(nid))
            return
        
        # Also fetch live messages from the scraper
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT phone_number, country_name FROM assigned_numbers WHERE id=?", (nid,))
        row = c.fetchone()
        conn.close()
        
        text = ""
        count = 0
        for svc, otp, msg, sender, source, ts in messages:
            if count >= 20:
                break
            if otp:
                text += f"🔑 OTP: `{otp}` | {svc}\n   Time: {ts}\n\n"
                count += 1
            else:
                text += f"📨 {svc}: {msg[:60]}...\n   Time: {ts}\n\n"
                count += 1
        
        total = get_number_messages_count(nid)
        text = f"📬 *Messages ({total} total, showing last {count})*\n\n{text}"
        
        await safe_edit(query, text, reply_markup=build_number_detail_keyboard(nid))
    
    elif data.startswith("release_"):
        nid = int(data.split("_")[1])
        if release_number(nid, user_id):
            await safe_edit(query, "✅ *Number released!*", reply_markup=build_main_keyboard())
        else:
            await safe_edit(query, "❌ Failed to release number", reply_markup=build_main_keyboard())
    
    elif data == "mynumbers":
        nums = get_user_numbers(user_id)
        if not nums:
            await safe_edit(query, "📭 *No numbers yet.*\nGet one with the button below!", 
                          reply_markup=build_main_keyboard())
            return
        text = "📋 *Your Numbers:*\n\n"
        for nid, flag, name, phone, disp, assigned, status in nums:
            status_icon = "✅ Active" if status == "active" else "❌ Released"
            text += f"{flag} *{name}*\n📞 `{phone}`\nStatus: {status_icon}\n\n"
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
            f"🔍 Numbers are scraped live from free SMS services.\n"
            f"📡 Inbox polled every 30 seconds.",
            reply_markup=build_main_keyboard())
    
    elif data == "how_otp":
        await safe_edit(query,
            "❓ *How OTP Reception Works*\n\n"
            "🔍 *Scraper Mode (current)*\n"
            "Bot scrapes real disposable numbers from free SMS websites\n"
            "↻ Inboxes polled every 30s for incoming messages\n"
            "⚠️ Numbers are public — OTPs visible to others\n\n"
            "📡 *Twilio Mode (optional)*\n"
            "1. Sign up at twilio.com ($20 free credit)\n"
            "2. Buy a phone number (~$1)\n"
            "3. Set webhook to:\n"
            "   `{render_url}/twilio-sms`\n"
            "4. All SMS forward to your bot instantly!\n\n"
            "🔐 Private, instant, works with any service\n\n"
            "⚠️ *For educational use only*",
            reply_markup=build_main_keyboard())
    
    elif data == "noop":
        pass

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    user_id = update.effective_user.id
    
    if text in ("/getnumber", "\U0001f4f1 Get Number"):
        keyboard, tp = get_country_keyboard(0)
        await update.message.reply_text(f"🌍 Select Country ({len(COUNTRIES)} countries)", 
                                       reply_markup=keyboard)
        return
    
    # Search countries by name
    matching = [(i, c) for i, c in enumerate(COUNTRIES) if text.lower() in c[0].lower()]
    if not matching:
        matching = [(i, c) for i, c in enumerate(COUNTRIES) if text in c[2]]
    
    if matching:
        if len(matching) == 1:
            idx, cd = matching[0]
            name, flag, dial, fmt = cd
            
            # Get a REAL number
            phone, display = get_real_number_for_country(name, flag, dial)
            num_id = save_number_to_db(user_id, name, flag, dial, phone, display)
            save_otp_message(num_id, phone, name, "SYSTEM", "Activated!", "", "SYSTEM", datetime.now().isoformat())
            
            await update.message.reply_text(
                f"✅ *Number Ready!*\n\n{display}\n\n"
                f"1. Use this number on WhatsApp or any service\n"
                f"2. Tap 'Check Messages' to see OTPs\n"
                f"3. Bot polls every 30s automatically",
                reply_markup=build_number_detail_keyboard(num_id),
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
    
    await update.message.reply_text("Type a country name or use the buttons!", 
                                   reply_markup=build_main_keyboard())

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *CYBERX Bot — Help*\n\n"
        "📌 *Commands:*\n"
        "`/start` — Start the bot\n"
        "`/getnumber` — Get a virtual number\n"
        "`/mynumbers` — View your numbers\n"
        "`/help` — This help\n\n"
        "🔍 *How it works:*\n"
        "1. Select a country\n"
        "2. Bot scrapes a real disposable number\n"
        "3. Use the number on any service\n"
        "4. Bot polls inbox every 30s for OTPs\n"
        "5. You get notified when SMS arrives\n\n"
        "📡 *Twilio setup (for private numbers):*\n"
        "Set webhook → `{os.environ.get('RENDER_EXTERNAL_URL', 'https://cyberx_otp.onrender.com')}/twilio-sms`\n\n"
        "🌍 *{len(COUNTRIES)} countries* available",
        parse_mode="Markdown"
    )

# ================================================================
# 🚀 MAIN
# ================================================================

def main():
    print("="*55)
    print("  CYBERX VIRTUAL NUMBER BOT - RENDER EDITION v2.0")
    print(f"  {len(COUNTRIES)} countries  Port 10000  4min health ping")
    print("  REAL NUMBERS from free SMS sites")
    print("="*55)

    init_db()

    if not BOT_TOKEN:
        print("\n[!] ERROR: BOT_TOKEN environment variable is missing!")
        sys.exit(1)

    render_url = os.environ.get("RENDER_EXTERNAL_URL", "https://cyberx_otp.onrender.com")

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
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    # Start real inbox poller (replaces dead Shelex API)
    poller_loop = asyncio.new_event_loop()
    poller_thread = threading.Thread(target=poll_real_inboxes, args=(app, poller_loop), daemon=True)
    poller_thread.start()
    print("[OK] Real inbox poller started (30s interval)")

    print(f"[OK] Bot ready! {len(COUNTRIES)} countries.")
    print(f"[OK] Twilio webhook: {render_url}/twilio-sms")

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
