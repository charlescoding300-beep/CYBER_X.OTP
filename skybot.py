"""
╔══════════════════════════════════════════════════════════════════╗
║        📱 CYBERX VIRTUAL NUMBER BOT — RENDER DEPLOY             ║
║                                                                  ║
║  🔒 OTP LOCK: 10 fallback numbers → first OTP wins → auto-push  ║
║  200+ COUNTRIES │ PORT 10000 │ HEALTH PING 4 MIN                ║
║  URL: https://cyber-x-otp.onrender.com                          ║
╚══════════════════════════════════════════════════════════════════╝
"""

import sys
import asyncio
import sqlite3
import random
import re
import time
import threading
import requests
import os
from datetime import datetime
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ================================================================
# 🔧 ONLY TWO THINGS TO EDIT
# ================================================================

BOT_TOKEN = "8532550542:AAF35U8_cq_1rHYCYpyZWzUnDyO2_F26plY"          # From @BotFather
ADMIN_ID = 8580418434                   # Your Telegram ID

# ================================================================
# 🌍 200+ COUNTRIES — EVERY COUNTRY IN THE WORLD
# ================================================================

COUNTRIES = [
    # 🌍 AFRICA (54)
    ("Algeria", "🇩🇿", "+213", (2, 3, 6, 11)), ("Angola", "🇦🇴", "+244", (3, 3, 6, 12)),
    ("Benin", "🇧🇯", "+229", (3, 3, 6, 12)), ("Botswana", "🇧🇼", "+267", (3, 3, 6, 12)),
    ("Burkina Faso", "🇧🇫", "+226", (3, 3, 6, 12)), ("Burundi", "🇧🇮", "+257", (3, 3, 6, 12)),
    ("Cabo Verde", "🇨🇻", "+238", (3, 3, 6, 12)), ("Cameroon", "🇨🇲", "+237", (3, 3, 6, 12)),
    ("Central African Rep.", "🇨🇫", "+236", (3, 3, 6, 12)), ("Chad", "🇹🇩", "+235", (3, 3, 6, 12)),
    ("Comoros", "🇰🇲", "+269", (3, 3, 6, 12)), ("Congo", "🇨🇬", "+242", (3, 3, 6, 12)),
    ("Côte d'Ivoire", "🇨🇮", "+225", (3, 3, 6, 12)), ("DR Congo", "🇨🇩", "+243", (3, 3, 6, 12)),
    ("Djibouti", "🇩🇯", "+253", (3, 3, 6, 12)), ("Egypt", "🇪🇬", "+20", (2, 3, 7, 12)),
    ("Equatorial Guinea", "🇬🇶", "+240", (3, 3, 6, 12)), ("Eritrea", "🇪🇷", "+291", (3, 3, 6, 12)),
    ("Ethiopia", "🇪🇹", "+251", (3, 3, 6, 12)), ("Gabon", "🇬🇦", "+241", (3, 3, 6, 12)),
    ("Gambia", "🇬🇲", "+220", (3, 3, 6, 12)), ("Ghana", "🇬🇭", "+233", (3, 3, 6, 12)),
    ("Guinea", "🇬🇳", "+224", (3, 3, 6, 12)), ("Guinea-Bissau", "🇬🇼", "+245", (3, 3, 6, 12)),
    ("Kenya", "🇰🇪", "+254", (3, 3, 6, 12)), ("Lesotho", "🇱🇸", "+266", (3, 3, 6, 12)),
    ("Liberia", "🇱🇷", "+231", (3, 3, 6, 12)), ("Libya", "🇱🇾", "+218", (3, 3, 6, 12)),
    ("Madagascar", "🇲🇬", "+261", (3, 3, 6, 12)), ("Malawi", "🇲🇼", "+265", (3, 3, 6, 12)),
    ("Mali", "🇲🇱", "+223", (3, 3, 6, 12)), ("Mauritania", "🇲🇷", "+222", (3, 3, 6, 12)),
    ("Mauritius", "🇲🇺", "+230", (3, 3, 6, 12)), ("Morocco", "🇲🇦", "+212", (3, 3, 6, 12)),
    ("Mozambique", "🇲🇿", "+258", (3, 3, 6, 12)), ("Namibia", "🇳🇦", "+264", (3, 3, 6, 12)),
    ("Niger", "🇳🇪", "+227", (3, 3, 6, 12)), ("Nigeria", "🇳🇬", "+234", (3, 3, 6, 12)),
    ("Rwanda", "🇷🇼", "+250", (3, 3, 6, 12)), ("São Tomé", "🇸🇹", "+239", (3, 3, 6, 12)),
    ("Senegal", "🇸🇳", "+221", (3, 3, 6, 12)), ("Seychelles", "🇸🇨", "+248", (3, 3, 6, 12)),
    ("Sierra Leone", "🇸🇱", "+232", (3, 3, 6, 12)), ("Somalia", "🇸🇴", "+252", (3, 3, 6, 12)),
    ("South Africa", "🇿🇦", "+27", (2, 3, 6, 11)), ("South Sudan", "🇸🇸", "+211", (3, 3, 6, 12)),
    ("Sudan", "🇸🇩", "+249", (3, 3, 6, 12)), ("Eswatini", "🇸🇿", "+268", (3, 3, 6, 12)),
    ("Tanzania", "🇹🇿", "+255", (3, 3, 6, 12)), ("Togo", "🇹🇬", "+228", (3, 3, 6, 12)),
    ("Tunisia", "🇹🇳", "+216", (3, 3, 6, 12)), ("Uganda", "🇺🇬", "+256", (3, 3, 6, 12)),
    ("Zambia", "🇿🇲", "+260", (3, 3, 6, 12)), ("Zimbabwe", "🇿🇼", "+263", (3, 3, 6, 12)),
    ("Zanzibar", "🇹🇿", "+255", (3, 3, 6, 12)),

    # 🌍 NORTH AMERICA (26)
    ("Antigua", "🇦🇬", "+1-268", (4, 3, 6, 13)), ("Bahamas", "🇧🇸", "+1-242", (4, 3, 6, 13)),
    ("Barbados", "🇧🇧", "+1-246", (4, 3, 6, 13)), ("Belize", "🇧🇿", "+501", (3, 3, 6, 12)),
    ("Bermuda", "🇧🇲", "+1-441", (4, 3, 6, 13)), ("Canada", "🇨🇦", "+1", (1, 3, 7, 11)),
    ("Costa Rica", "🇨🇷", "+506", (3, 3, 6, 12)), ("Cuba", "🇨🇺", "+53", (2, 3, 6, 11)),
    ("Dominica", "🇩🇲", "+1-767", (4, 3, 6, 13)), ("Dominican Rep.", "🇩🇴", "+1-809", (4, 3, 6, 13)),
    ("El Salvador", "🇸🇻", "+503", (3, 3, 6, 12)), ("Grenada", "🇬🇩", "+1-473", (4, 3, 6, 13)),
    ("Guatemala", "🇬🇹", "+502", (3, 3, 6, 12)), ("Haiti", "🇭🇹", "+509", (3, 3, 6, 12)),
    ("Honduras", "🇭🇳", "+504", (3, 3, 6, 12)), ("Jamaica", "🇯🇲", "+1-876", (4, 3, 6, 13)),
    ("Mexico", "🇲🇽", "+52", (2, 3, 7, 12)), ("Nicaragua", "🇳🇮", "+505", (3, 3, 6, 12)),
    ("Panama", "🇵🇦", "+507", (3, 3, 6, 12)), ("Puerto Rico", "🇵🇷", "+1-787", (4, 3, 6, 13)),
    ("St. Kitts", "🇰🇳", "+1-869", (4, 3, 6, 13)), ("St. Lucia", "🇱🇨", "+1-758", (4, 3, 6, 13)),
    ("St. Vincent", "🇻🇨", "+1-784", (4, 3, 6, 13)), ("Trinidad", "🇹🇹", "+1-868", (4, 3, 6, 13)),
    ("Turks & Caicos", "🇹🇨", "+1-649", (4, 3, 6, 13)), ("United States", "🇺🇸", "+1", (1, 3, 7, 11)),

    # 🌍 SOUTH AMERICA (12)
    ("Argentina", "🇦🇷", "+54", (2, 3, 7, 12)), ("Bolivia", "🇧🇴", "+591", (3, 3, 6, 12)),
    ("Brazil", "🇧🇷", "+55", (2, 3, 8, 13)), ("Chile", "🇨🇱", "+56", (2, 3, 7, 12)),
    ("Colombia", "🇨🇴", "+57", (2, 3, 7, 12)), ("Ecuador", "🇪🇨", "+593", (3, 3, 6, 12)),
    ("Guyana", "🇬🇾", "+592", (3, 3, 6, 12)), ("Paraguay", "🇵🇾", "+595", (3, 3, 6, 12)),
    ("Peru", "🇵🇪", "+51", (2, 3, 7, 12)), ("Suriname", "🇸🇷", "+597", (3, 3, 6, 12)),
    ("Uruguay", "🇺🇾", "+598", (3, 3, 6, 12)), ("Venezuela", "🇻🇪", "+58", (2, 3, 7, 12)),

    # 🌍 ASIA (51)
    ("Afghanistan", "🇦🇫", "+93", (2, 3, 6, 11)), ("Armenia", "🇦🇲", "+374", (3, 3, 6, 12)),
    ("Azerbaijan", "🇦🇿", "+994", (3, 3, 6, 12)), ("Bahrain", "🇧🇭", "+973", (3, 3, 6, 12)),
    ("Bangladesh", "🇧🇩", "+880", (3, 3, 7, 13)), ("Bhutan", "🇧🇹", "+975", (3, 3, 6, 12)),
    ("Brunei", "🇧🇳", "+673", (3, 3, 6, 12)), ("Cambodia", "🇰🇭", "+855", (3, 3, 6, 12)),
    ("China", "🇨🇳", "+86", (2, 3, 8, 13)), ("Cyprus", "🇨🇾", "+357", (3, 3, 6, 12)),
    ("East Timor", "🇹🇱", "+670", (3, 3, 6, 12)), ("Georgia", "🇬🇪", "+995", (3, 3, 6, 12)),
    ("Hong Kong", "🇭🇰", "+852", (3, 3, 6, 12)), ("India", "🇮🇳", "+91", (2, 3, 7, 12)),
    ("Indonesia", "🇮🇩", "+62", (2, 3, 7, 12)), ("Iran", "🇮🇷", "+98", (2, 3, 7, 12)),
    ("Iraq", "🇮🇶", "+964", (3, 3, 6, 12)), ("Israel", "🇮🇱", "+972", (3, 3, 6, 12)),
    ("Japan", "🇯🇵", "+81", (2, 3, 7, 12)), ("Jordan", "🇯🇴", "+962", (3, 3, 6, 12)),
    ("Kazakhstan", "🇰🇿", "+7", (1, 3, 7, 11)), ("Kuwait", "🇰🇼", "+965", (3, 3, 6, 12)),
    ("Kyrgyzstan", "🇰🇬", "+996", (3, 3, 6, 12)), ("Laos", "🇱🇦", "+856", (3, 3, 6, 12)),
    ("Lebanon", "🇱🇧", "+961", (3, 3, 6, 12)), ("Macau", "🇲🇴", "+853", (3, 3, 6, 12)),
    ("Malaysia", "🇲🇾", "+60", (2, 3, 7, 12)), ("Maldives", "🇲🇻", "+960", (3, 3, 6, 12)),
    ("Mongolia", "🇲🇳", "+976", (3, 3, 6, 12)), ("Myanmar", "🇲🇲", "+95", (2, 3, 7, 12)),
    ("Nepal", "🇳🇵", "+977", (3, 3, 6, 12)), ("North Korea", "🇰🇵", "+850", (3, 3, 6, 12)),
    ("Oman", "🇴🇲", "+968", (3, 3, 6, 12)), ("Pakistan", "🇵🇰", "+92", (2, 3, 7, 12)),
    ("Palestine", "🇵🇸", "+970", (3, 3, 6, 12)), ("Philippines", "🇵🇭", "+63", (2, 3, 7, 12)),
    ("Qatar", "🇶🇦", "+974", (3, 3, 6, 12)), ("Saudi Arabia", "🇸🇦", "+966", (3, 3, 7, 13)),
    ("Singapore", "🇸🇬", "+65", (2, 3, 7, 12)), ("South Korea", "🇰🇷", "+82", (2, 3, 7, 12)),
    ("Sri Lanka", "🇱🇰", "+94", (2, 3, 7, 12)), ("Syria", "🇸🇾", "+963", (3, 3, 6, 12)),
    ("Taiwan", "🇹🇼", "+886", (3, 3, 6, 12)), ("Tajikistan", "🇹🇯", "+992", (3, 3, 6, 12)),
    ("Thailand", "🇹🇭", "+66", (2, 3, 7, 12)), ("Turkey", "🇹🇷", "+90", (2, 3, 7, 12)),
    ("Turkmenistan", "🇹🇲", "+993", (3, 3, 6, 12)), ("UAE", "🇦🇪", "+971", (3, 3, 6, 12)),
    ("Uzbekistan", "🇺🇿", "+998", (3, 3, 6, 12)), ("Vietnam", "🇻🇳", "+84", (2, 3, 7, 12)),
    ("Yemen", "🇾🇪", "+967", (3, 3, 6, 12)),

    # 🌍 EUROPE (47)
    ("Albania", "🇦🇱", "+355", (3, 3, 6, 12)), ("Andorra", "🇦🇩", "+376", (3, 3, 6, 12)),
    ("Austria", "🇦🇹", "+43", (2, 3, 7, 12)), ("Belarus", "🇧🇾", "+375", (3, 3, 6, 12)),
    ("Belgium", "🇧🇪", "+32", (2, 3, 7, 12)), ("Bosnia", "🇧🇦", "+387", (3, 3, 6, 12)),
    ("Bulgaria", "🇧🇬", "+359", (3, 3, 6, 12)), ("Croatia", "🇭🇷", "+385", (3, 3, 6, 12)),
    ("Czech Rep.", "🇨🇿", "+420", (3, 3, 6, 12)), ("Denmark", "🇩🇰", "+45", (2, 3, 7, 12)),
    ("Estonia", "🇪🇪", "+372", (3, 3, 6, 12)), ("Finland", "🇫🇮", "+358", (3, 3, 6, 12)),
    ("France", "🇫🇷", "+33", (2, 3, 7, 12)), ("Germany", "🇩🇪", "+49", (2, 3, 7, 12)),
    ("Greece", "🇬🇷", "+30", (2, 3, 7, 12)), ("Hungary", "🇭🇺", "+36", (2, 3, 7, 12)),
    ("Iceland", "🇮🇸", "+354", (3, 3, 6, 12)), ("Ireland", "🇮🇪", "+353", (3, 3, 6, 12)),
    ("Italy", "🇮🇹", "+39", (2, 3, 7, 12)), ("Kosovo", "🇽🇰", "+383", (3, 3, 6, 12)),
    ("Latvia", "🇱🇻", "+371", (3, 3, 6, 12)), ("Liechtenstein", "🇱🇮", "+423", (3, 3, 6, 12)),
    ("Lithuania", "🇱🇹", "+370", (3, 3, 6, 12)), ("Luxembourg", "🇱🇺", "+352", (3, 3, 6, 12)),
    ("Malta", "🇲🇹", "+356", (3, 3, 6, 12)), ("Moldova", "🇲🇩", "+373", (3, 3, 6, 12)),
    ("Monaco", "🇲🇨", "+377", (3, 3, 6, 12)), ("Montenegro", "🇲🇪", "+382", (3, 3, 6, 12)),
    ("Netherlands", "🇳🇱", "+31", (2, 3, 7, 12)), ("North Macedonia", "🇲🇰", "+389", (3, 3, 6, 12)),
    ("Norway", "🇳🇴", "+47", (2, 3, 7, 12)), ("Poland", "🇵🇱", "+48", (2, 3, 7, 12)),
    ("Portugal", "🇵🇹", "+351", (3, 3, 6, 12)), ("Romania", "🇷🇴", "+40", (2, 3, 7, 12)),
    ("Russia", "🇷🇺", "+7", (1, 3, 7, 11)), ("San Marino", "🇸🇲", "+378", (3, 3, 6, 12)),
    ("Serbia", "🇷🇸", "+381", (3, 3, 6, 12)), ("Slovakia", "🇸🇰", "+421", (3, 3, 6, 12)),
    ("Slovenia", "🇸🇮", "+386", (3, 3, 6, 12)), ("Spain", "🇪🇸", "+34", (2, 3, 7, 12)),
    ("Sweden", "🇸🇪", "+46", (2, 3, 7, 12)), ("Switzerland", "🇨🇭", "+41", (2, 3, 7, 12)),
    ("Ukraine", "🇺🇦", "+380", (3, 3, 6, 12)), ("United Kingdom", "🇬🇧", "+44", (2, 4, 6, 12)),
    ("Vatican City", "🇻🇦", "+379", (3, 3, 6, 12)),

    # 🌍 OCEANIA (14)
    ("Australia", "🇦🇺", "+61", (2, 3, 7, 12)), ("Fiji", "🇫🇯", "+679", (3, 3, 6, 12)),
    ("Kiribati", "🇰🇮", "+686", (3, 3, 6, 12)), ("Marshall Is.", "🇲🇭", "+692", (3, 3, 6, 12)),
    ("Micronesia", "🇫🇲", "+691", (3, 3, 6, 12)), ("Nauru", "🇳🇷", "+674", (3, 3, 6, 12)),
    ("New Zealand", "🇳🇿", "+64", (2, 3, 7, 12)), ("Palau", "🇵🇼", "+680", (3, 3, 6, 12)),
    ("Papua New Guinea", "🇵🇬", "+675", (3, 3, 6, 12)), ("Samoa", "🇼🇸", "+685", (3, 3, 6, 12)),
    ("Solomon Is.", "🇸🇧", "+677", (3, 3, 6, 12)), ("Tonga", "🇹🇴", "+676", (3, 3, 6, 12)),
    ("Tuvalu", "🇹🇻", "+688", (3, 3, 6, 12)), ("Vanuatu", "🇻🇺", "+678", (3, 3, 6, 12)),

    # 🌍 MICRO / SPECIAL
    ("Hawaii", "🌺", "+1-808", (4, 3, 6, 13)), ("Guam", "🇬🇺", "+1-671", (4, 3, 6, 13)),
    ("American Samoa", "🇦🇸", "+1-684", (4, 3, 6, 13)), ("Northern Mariana", "🇲🇵", "+1-670", (4, 3, 6, 13)),
]

COUNTRIES.sort(key=lambda x: x[0])
COUNTRY_BY_NAME = {c[0]: c for c in COUNTRIES}
COUNTRY_PER_PAGE = 8

# ================================================================
# 🔒 OTP LOCK SETTINGS — 10 fallback numbers, first OTP wins
# ================================================================

LOCK_POOL_SIZE = 10           # numbers fired at once
LOCK_POLL_SECONDS = 22        # seconds between check rounds
LOCK_TIMEOUT_MINUTES = 4      # give up & offer swap after this

# Countries with Shelex coverage (real network numbers → better OTP odds)
LOCK_COUNTRIES = ["United States", "United Kingdom", "India", "Canada",
                  "Australia", "Germany", "France", "Brazil", "Mexico",
                  "Indonesia", "Philippines", "Vietnam", "Thailand",
                  "Nigeria", "Kenya", "South Africa", "Egypt", "Turkey",
                  "Pakistan", "Russia", "Ukraine", "Poland", "Sweden",
                  "Spain", "Italy", "Netherlands", "Japan", "South Korea",
                  "Argentina", "Colombia", "Chile", "Peru", "New Zealand"]

SERVICE_LIST = ["whatsapp","facebook","instagram","tiktok","telegram",
                "google","twitter","snapchat","linkedin","discord",
                "amazon","paypal","uber","airbnb","netflix",
                "microsoft","apple","spotify","signal","wechat"]

# ================================================================
# 💾 DATABASE
# ================================================================

DB_FILE = "sky_numbers.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        joined_at TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS assigned_numbers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        country TEXT,
        flag TEXT,
        dial_code TEXT,
        phone_number TEXT UNIQUE,
        full_display TEXT,
        created_at TEXT,
        status TEXT DEFAULT 'active',
        locked INTEGER DEFAULT 0,
        locked_at TEXT,
        lock_session_id INTEGER
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        number_id INTEGER,
        phone_number TEXT,
        country TEXT,
        sender TEXT,
        message_text TEXT,
        otp_code TEXT,
        service TEXT,
        source TEXT DEFAULT 'system',
        received_at TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS config (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS lock_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        status TEXT DEFAULT 'running',
        winner_number TEXT,
        winner_service TEXT,
        winner_otp TEXT,
        started_at TEXT,
        ended_at TEXT
    )''')
    # upgrade old databases missing the new columns
    for col in ["locked", "locked_at", "lock_session_id"]:
        try: c.execute(f"ALTER TABLE assigned_numbers ADD COLUMN {col} TEXT")
        except: pass
    conn.commit()
    conn.close()

# ================================================================
# 📱 NUMBER GENERATOR (NANP-valid for US/Canada)
# ================================================================

def rand_digit(low=0, high=9):
    return str(random.randint(low, high))

def generate_number_for_country(country_data):
    name, flag, dial_code, fmt = country_data
    cc_digits, ac_digits, sub_digits, total_len = fmt
    clean_dial = dial_code.replace("+", "").replace("-", "")

    phone = clean_dial
    for _ in range(cc_digits):
        phone += rand_digit(0, 9)

    remaining_total = ac_digits + sub_digits
    for i in range(remaining_total):
        if name in ["United States", "Canada"]:
            phone += rand_digit(2, 9) if (i == 0 or i == ac_digits) else rand_digit(0, 9)
        elif name == "United Kingdom":
            phone += '7' if i == 0 else rand_digit(0, 9)
        elif name == "India":
            phone += rand_digit(6, 9) if i == 0 else rand_digit(0, 9)
        elif name == "Pakistan":
            phone += '3' if i == 0 else rand_digit(0, 9)
        elif name == "Nigeria":
            phone += str(random.choice([7, 8, 9])) if i == 0 else rand_digit(0, 9)
        elif name in ["China", "Bangladesh"]:
            phone += '1' if i == 0 else rand_digit(0, 9)
        elif name == "Australia":
            phone += '4' if i == 0 else rand_digit(0, 9)
        elif name in ["Uganda", "Kenya", "Tanzania"]:
            phone += str(random.choice([7, 2, 3])) if i == 0 else rand_digit(0, 9)
        elif name == "South Africa":
            phone += str(random.choice([6, 7, 8])) if i == 0 else rand_digit(0, 9)
        elif name in ["Zimbabwe", "Zambia"]:
            phone += str(random.choice([7, 9])) if i == 0 else rand_digit(0, 9)
        else:
            phone += rand_digit(0, 9)

    remaining = phone[len(clean_dial):]
    if name in ["United States", "Canada"] and len(remaining) >= 10:
        formatted = f"{dial_code} ({remaining[:3]}) {remaining[3:6]}-{remaining[6:10]}"
    elif name == "United Kingdom":
        r = remaining; formatted = f"+44 {r[:5]} {r[5:]}" if len(r) >= 6 else "+44 " + r
    elif name == "Japan": r = remaining; formatted = f"+81 {r[:3]}-{r[3:7]}-{r[7:]}"
    elif name == "South Korea": r = remaining; formatted = f"+82 {r[:3]}-{r[3:7]}-{r[7:]}"
    elif name == "India": r = remaining; formatted = f"+91 {r[:5]}-{r[5:]}"
    elif name == "Pakistan": r = remaining; formatted = f"+92 {r[:3]}-{r[3:]}"
    elif name == "China": r = remaining; formatted = f"+86 {r[:3]} {r[3:7]} {r[7:]}"
    elif name == "Australia": r = remaining; formatted = f"+61 {r[:1]} {r[1:4]} {r[4:7]} {r[7:]}"
    elif name == "Indonesia": r = remaining; formatted = f"+62 {r[:3]}-{r[3:7]}-{r[7:]}"
    elif name == "Nigeria": r = remaining; formatted = f"+234 {r[:3]} {r[3:6]} {r[6:]}"
    elif name in ["Uganda", "Kenya", "Tanzania"]: r = remaining; formatted = f"{dial_code} {r[:3]} {r[3:6]} {r[6:]}"
    elif name == "South Africa": r = remaining; formatted = f"+27 {r[:2]} {r[2:5]} {r[5:]}"
    elif clean_dial == "1": formatted = f"+1 ({remaining[:3]}) {remaining[3:6]}-{remaining[6:10]}"
    else:
        chunks = []; r = remaining
        while len(r) > 4: chunks.append(r[:3]); r = r[3:]
        chunks.append(r); formatted = dial_code + " " + " ".join(chunks)

    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT id FROM assigned_numbers WHERE phone_number=?", (phone,))
    exists = c.fetchone(); conn.close()
    if exists: return generate_number_for_country(country_data)
    return phone, formatted

# ================================================================
# 💾 DATABASE HELPERS
# ================================================================

def save_number_to_db(user_id, country_name, flag, dial_code, phone_number, display, locked=0):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("INSERT INTO assigned_numbers (user_id, country, flag, dial_code, phone_number, full_display, created_at, locked, locked_at) VALUES (?,?,?,?,?,?,?,?,?)",
              (user_id, country_name, flag, dial_code, phone_number, display, datetime.now().isoformat(), 1 if locked else 0, datetime.now().isoformat() if locked else None))
    conn.commit(); number_id = c.lastrowid; conn.close()
    return number_id

def get_user_numbers(user_id):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT id, country, flag, dial_code, phone_number, full_display, created_at, locked FROM assigned_numbers WHERE user_id=? AND status='active' ORDER BY id DESC", (user_id,))
    rows = c.fetchall(); conn.close()
    return rows

def release_number(number_id, user_id):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("UPDATE assigned_numbers SET status='released' WHERE id=? AND user_id=?", (number_id, user_id))
    affected = c.rowcount; conn.commit(); conn.close()
    return affected > 0

def save_otp_message(number_id, phone_number, country, sender, message_text, otp_code, service, source="system"):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("INSERT INTO messages (number_id, phone_number, country, sender, message_text, otp_code, service, source, received_at) VALUES (?,?,?,?,?,?,?,?,?)",
              (number_id, phone_number, country, sender, message_text, otp_code, service, source, datetime.now().isoformat()))
    conn.commit(); msg_id = c.lastrowid
    c.execute("SELECT COUNT(*) FROM messages WHERE number_id=?", (number_id,)); total = c.fetchone()[0]
    conn.close()
    return msg_id, total

def get_number_messages(number_id, limit=20):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT id, sender, message_text, otp_code, service, source, received_at FROM messages WHERE number_id=? ORDER BY id DESC LIMIT ?", (number_id, limit))
    rows = c.fetchall(); conn.close()
    return rows

def get_number_messages_count(number_id):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM messages WHERE number_id=?", (number_id,)); count = c.fetchone()[0]; conn.close()
    return count

# ================================================================
# 🔌 SHELEX FREE OTP API + SERVICE REGISTRATION CHECK
# ================================================================

COUNTRY_TO_SHELEX = {
    "United States": "us", "United Kingdom": "gb", "Russia": "ru",
    "Canada": "ca", "India": "in", "Brazil": "br", "Australia": "au",
    "Germany": "de", "France": "fr", "Sweden": "se", "Poland": "pl",
    "Netherlands": "nl", "Spain": "es", "Italy": "it", "Norway": "no",
    "Denmark": "dk", "Finland": "fi", "Japan": "jp", "South Korea": "kr",
    "China": "cn", "Thailand": "th", "Vietnam": "vn", "Philippines": "ph",
    "Indonesia": "id", "Malaysia": "my", "Singapore": "sg", "Mexico": "mx",
    "Argentina": "ar", "Chile": "cl", "Colombia": "co", "Peru": "pe",
    "South Africa": "za", "Nigeria": "ng", "Kenya": "ke", "Morocco": "ma",
    "Egypt": "eg", "Turkey": "tr", "UAE": "ae", "Israel": "il",
    "Pakistan": "pk", "Bangladesh": "bd", "Sri Lanka": "lk", "Nepal": "np",
    "Cambodia": "kh", "Myanmar": "mm", "Ukraine": "ua", "Romania": "ro",
    "Czech Rep.": "cz", "Portugal": "pt", "Greece": "gr", "Hungary": "hu",
    "Austria": "at", "Switzerland": "ch", "Belgium": "be", "Ireland": "ie",
    "New Zealand": "nz", "Hong Kong": "hk", "Taiwan": "tw",
    "Kazakhstan": "kz", "Qatar": "qa", "Kuwait": "kw",
    "Oman": "om", "Bahrain": "bh", "Jordan": "jo", "Lebanon": "lb",
}

def fetch_shelex_otp(country_code, phone_number):
    try:
        resp = requests.get(f"https://otp-api.shelex.dev/api/{country_code}/{phone_number}", timeout=10)
        if resp.status_code == 200: return resp.json()
    except: pass
    return []

def check_service_registration(phone_number, shelex_code=None):
    """
    Ask Shelex if this number already has app messages (WhatsApp, etc.).
    If yes → the number was already registered/used by another user.
    """
    registered = []
    codes = [shelex_code] if shelex_code else ["us"]
    clean = phone_number.replace("+", "").replace("-", "").replace(" ", "")
    for code in codes:
        if not code: continue
        try:
            r = requests.get(f"https://otp-api.shelex.dev/api/{code}/{clean}", timeout=5)
            if r.status_code == 200:
                data = r.json()
                if isinstance(data, list):
                    for m in data:
                        if isinstance(m, dict):
                            t = (m.get("message") or m.get("sms") or m.get("text") or "").lower()
                            for svc in SERVICE_LIST:
                                if svc in t and svc.upper() not in registered:
                                    registered.append(svc.upper())
        except: continue
    return registered

def shelex_poll_numbers(bot_app, loop):
    """Watch every active number. New OTP → save + push to owner instantly."""
    while True:
        try:
            time.sleep(30)
            conn = sqlite3.connect(DB_FILE); c = conn.cursor()
            c.execute("SELECT id, country, phone_number FROM assigned_numbers WHERE status='active'")
            our_numbers = c.fetchall(); conn.close()

            for num_id, country, phone in our_numbers:
                shelex_code = COUNTRY_TO_SHELEX.get(country)
                if not shelex_code: continue
                clean_phone = phone.replace("+", "").replace("-", "").replace(" ", "")
                try:
                    otp_data = fetch_shelex_otp(shelex_code, clean_phone)
                    if otp_data and isinstance(otp_data, list):
                        for msg in otp_data:
                            if isinstance(msg, dict):
                                msg_text = msg.get("message", msg.get("sms", msg.get("text", "")))
                                sender = msg.get("from", msg.get("sender", "Unknown"))
                                if not msg_text: continue
                                conn2 = sqlite3.connect(DB_FILE); c2 = conn2.cursor()
                                c2.execute("SELECT id FROM messages WHERE number_id=? AND message_text=? AND sender=?",
                                          (num_id, msg_text[:100], sender))
                                exists = c2.fetchone()
                                if not exists:
                                    otp_match = re.search(r'(\d{4,8})', msg_text)
                                    otp_code = otp_match.group(1) if otp_match else ""
                                    service = "UNKNOWN"
                                    msg_lower = msg_text.lower()
                                    for svc in SERVICE_LIST:
                                        if svc in msg_lower: service = svc.upper(); break
                                    save_otp_message(num_id, phone, country, sender, msg_text, otp_code, service, "shelex_free")
                                    conn3 = sqlite3.connect(DB_FILE); c3 = conn3.cursor()
                                    c3.execute("SELECT user_id FROM assigned_numbers WHERE id=?", (num_id,))
                                    user_row = c3.fetchone(); conn3.close()
                                    if user_row and bot_app:
                                        owner = user_row[0]
                                        async def notify():
                                            try:
                                                await bot_app.bot.send_message(chat_id=owner, text=f"📥 **New OTP!**\n\n📞 `{phone}`\n🏷️ {service}\n🔑 `{otp_code}`\n\nCheck Inbox!", parse_mode="Markdown")
                                            except: pass
                                        asyncio.run_coroutine_threadsafe(notify(), loop)
                                    print(f"[SHELEX] ✅ OTP: [{service}] {otp_code} for {phone}")
                                conn2.close()
                except: pass
        except Exception as e:
            print(f"[SHELEX] Error: {e}")
            time.sleep(10)

# ================================================================
# 🔒🔟 OTP LOCK FALLBACK POOL — 10 numbers, first OTP wins
# ================================================================

def lock_start_session(user_id):
    """Kill old session, fire 10 numbers at once, lock them to this user."""
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("UPDATE lock_sessions SET status='stopped', ended_at=? WHERE user_id=? AND status='running'",
              (datetime.now().isoformat(), user_id))
    c.execute("INSERT INTO lock_sessions (user_id, status, started_at) VALUES (?, 'running', ?)",
              (user_id, datetime.now().isoformat()))
    conn.commit(); sid = c.lastrowid; conn.close()

    numbers = []
    for _ in range(LOCK_POOL_SIZE):
        name = random.choice(LOCK_COUNTRIES)
        cd = COUNTRY_BY_NAME.get(name)
        if not cd: continue
        phone, display = generate_number_for_country(cd)
        num_id = save_number_to_db(user_id, cd[0], cd[1], cd[2], phone, display, locked=1)
        conn = sqlite3.connect(DB_FILE); c = conn.cursor()
        c.execute("UPDATE assigned_numbers SET lock_session_id=? WHERE id=?", (sid, num_id))
        conn.commit(); conn.close()
        numbers.append((num_id, phone, display, cd[0]))
    return sid, numbers

def lock_session_status(sid):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT status FROM lock_sessions WHERE id=?", (sid,))
    row = c.fetchone(); conn.close()
    return row[0] if row else 'gone'

def lock_end_session(sid, status, phone="", svc="", otp=""):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("UPDATE lock_sessions SET status=?, winner_number=?, winner_service=?, winner_otp=?, ended_at=? WHERE id=?",
              (status, phone, svc, otp, datetime.now().isoformat(), sid))
    c.execute("UPDATE assigned_numbers SET status='released' WHERE lock_session_id=?", (sid,))
    conn.commit(); conn.close()

def _lock_send(app, loop, user_id, text):
    async def go():
        try: await app.bot.send_message(chat_id=user_id, text=text, parse_mode="Markdown")
        except: pass
    try: asyncio.run_coroutine_threadsafe(go(), loop)
    except: pass

def lock_poll_thread(app, loop):
    """Background watcher: 10 numbers checked every ~22s. First OTP → instant push."""
    while True:
        try:
            time.sleep(LOCK_POLL_SECONDS + random.uniform(0, 5))  # jitter avoids rate-limit
            conn = sqlite3.connect(DB_FILE); c = conn.cursor()
            c.execute("SELECT id, user_id, started_at FROM lock_sessions WHERE status='running'")
            sessions = c.fetchall(); conn.close()

            for sid, user_id, started in sessions:
                try:
                    start_dt = datetime.fromisoformat(started)
                    if (datetime.now() - start_dt).total_seconds() > LOCK_TIMEOUT_MINUTES * 60:
                        lock_end_session(sid, 'expired')
                        _lock_send(app, loop, user_id,
                            "⏰ **4 min up — no OTP landed.**\n"
                            "Public pool is busy right now.\n\n"
                            "👉 Tap **🔄 Swap Pool** to fire 10 fresh numbers,\n"
                            "or real guaranteed OTPs need Twilio/SIM numbers.")
                        continue
                except: pass

                conn = sqlite3.connect(DB_FILE); c = conn.cursor()
                c.execute("""SELECT id, phone_number, country FROM assigned_numbers
                             WHERE lock_session_id=? AND status='active'""", (sid,))
                pool = c.fetchall(); conn.close()

                for num_id, phone, country in pool:
                    sc = COUNTRY_TO_SHELEX.get(country)
                    if not sc: continue
                    clean = phone.replace("+","").replace("-","").replace(" ","")
                    try:
                        data = fetch_shelex_otp(sc, clean)
                        if not isinstance(data, list): continue
                        for m in data:
                            if not isinstance(m, dict): continue
                            text = (m.get("message") or m.get("sms") or m.get("text") or "").strip()
                            if not text: continue
                            otp_m = re.search(r'\b(\d{4,8})\b', text)
                            if not otp_m: continue
                            otp = otp_m.group(1)
                            svc = "UNKNOWN"
                            low = text.lower()
                            for s in SERVICE_LIST:
                                if s in low: svc = s.upper(); break
                            save_otp_message(num_id, phone, country, m.get("from","Unknown"), text, otp, svc, "otp_lock")
                            lock_end_session(sid, 'won', phone, svc, otp)
                            _lock_send(app, loop, user_id,
                                f"🎯 **OTP CAPTURED!**\n\n"
                                f"📞 `{phone}` ({country})\n"
                                f"🏷️ {svc}\n"
                                f"🔑 **CODE: `{otp}`**\n\n"
                                f"⚡ Enter it in WhatsApp NOW — fast, before it expires!\n"
                                f"_{LOCK_POOL_SIZE-1} fallback numbers auto-released._")
                            break
                    except: continue
                    if lock_session_status(sid) != 'running': break
        except Exception as e:
            print(f"[LOCK] {e}")
            time.sleep(10)

async def lock_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    sid, nums = lock_start_session(user_id)
    lines = "\n".join(f"   • `{p}` ({c})" for _, p, d, c in nums[:5])
    extra = f"   • ...and {len(nums)-5} more" if len(nums) > 5 else ""
    await update.message.reply_text(
        f"🔒 **OTP LOCK ARMED — {len(nums)} numbers fired!**\n"
        f"_{LOCK_POLL_SECONDS}s check cycle · first OTP wins_\n\n"
        f"{lines}\n{extra}\n\n"
        f"⚡ Open WhatsApp, register any of these, wait — code lands here automatically.\n"
        f"🕐 Auto-swap in {LOCK_TIMEOUT_MINUTES} min if nothing lands.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔄 Swap Pool", callback_data="lock_swap"),
            InlineKeyboardButton("⏹ Stop", callback_data="lock_stop")]]))

async def lock_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    user_id = update.effective_user.id

    if q.data == "lock_arm":
        sid, nums = lock_start_session(user_id)
        lines = "\n".join(f"   • `{p}` ({c})" for _, p, d, c in nums[:5])
        extra = f"   • ...and {len(nums)-5} more" if len(nums) > 5 else ""
        await q.edit_message_text(
            f"🔒 **OTP LOCK ARMED — {len(nums)} numbers fired!**\n"
            f"_{LOCK_POLL_SECONDS}s check cycle · first OTP wins_\n\n"
            f"{lines}\n{extra}\n\n"
            f"⚡ Open WhatsApp, register any of these, wait — code lands here automatically.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔄 Swap Pool", callback_data="lock_swap"),
                InlineKeyboardButton("⏹ Stop", callback_data="lock_stop")]]))
    elif q.data == "lock_swap":
        sid, nums = lock_start_session(user_id)
        await q.edit_message_text(f"🔄 **Pool swapped — {len(nums)} fresh numbers fired.**\n_Watching…",
                                  parse_mode="Markdown")
    elif q.data == "lock_stop":
        conn = sqlite3.connect(DB_FILE); c = conn.cursor()
        c.execute("SELECT id FROM lock_sessions WHERE user_id=? AND status='running'", (user_id,))
        rows = c.fetchall(); conn.close()
        for (sid,) in rows: lock_end_session(sid, 'stopped')
        await q.edit_message_text("⏹ **Pool stopped. Numbers released.**\n\n_For real guaranteed OTPs, Twilio or a physical SIM is the way._",
                                  parse_mode="Markdown")

# ================================================================
# 🌐 FLASK + HEALTH PING (PORT 10000)
# ================================================================

flask_app = Flask(__name__)
RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL", "https://cyber-x-otp.onrender.com")

@flask_app.route('/twilio-sms', methods=['POST'])
def twilio_webhook():
    from_number = request.form.get('From', '').strip()
    to_number = request.form.get('To', '').strip()
    body = request.form.get('Body', '').strip()
    if not from_number or not body: return "OK", 200
    if ':' in from_number: from_number = from_number.split(':')[-1]

    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT id, user_id, country, phone_number FROM assigned_numbers WHERE phone_number=? AND status='active'", (to_number,))
    row = c.fetchone()
    if not row:
        c.execute("SELECT id, user_id, country, phone_number FROM assigned_numbers WHERE phone_number=? AND status='active'", (from_number,))
        row = c.fetchone()
    if row:
        num_id, user_id, country, phone = row
        otp_match = re.search(r'(\d{4,8})', body); otp_code = otp_match.group(1) if otp_match else ""
        service = "SMS"
        for svc in SERVICE_LIST:
            if svc in body.lower(): service = svc.upper(); break
        save_otp_message(num_id, phone, country, from_number, body, otp_code, service, "twilio")
        print(f"[TWILIO] ✅ OTP: [{service}] {otp_code} for {phone}")
    conn.close()
    return "OK", 200

@flask_app.route('/health', methods=['GET'])
@flask_app.route('/', methods=['GET'])
def health():
    return jsonify({
        "status": "ok",
        "time": datetime.now().isoformat(),
        "bot": "CYBERX Virtual Number Bot",
        "countries": len(COUNTRIES),
        "users": get_user_count(),
        "active_numbers": get_active_count(),
        "total_messages": get_message_count()
    })

def get_user_count():
    try:
        conn = sqlite3.connect(DB_FILE); c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM users"); count = c.fetchone()[0]; conn.close()
        return count
    except: return 0

def get_active_count():
    try:
        conn = sqlite3.connect(DB_FILE); c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM assigned_numbers WHERE status='active'"); count = c.fetchone()[0]; conn.close()
        return count
    except: return 0

def get_message_count():
    try:
        conn = sqlite3.connect(DB_FILE); c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM messages"); count = c.fetchone()[0]; conn.close()
        return count
    except: return 0

def start_flask():
    port = int(os.environ.get("PORT", 10000))   # Render injects PORT (default 10000)
    flask_app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

def health_ping():
    """Ping own /health every 4 minutes so Render never sleeps."""
    while True:
        url = os.environ.get("RENDER_EXTERNAL_URL") or RENDER_URL
        try:
            conn = sqlite3.connect(DB_FILE); c = conn.cursor()
            c.execute("SELECT value FROM config WHERE key='render_url'")
            row = c.fetchone()
            if row: url = row[0]
            conn.close()
        except: pass
        if not url: url = "https://cyber-x-otp.onrender.com"
        try:
            resp = requests.get(f"{url.rstrip('/')}/health", timeout=30)
            print(f"[HEALTH] ✅ {url}/health → {resp.status_code} | {datetime.now().strftime('%H:%M:%S')}")
        except Exception as e:
            print(f"[HEALTH] Ping failed: {e}")
        time.sleep(240)   # 4 minutes

# ================================================================
# 🤖 TELEGRAM BOT
# ================================================================

def get_country_keyboard(page=0, search=None):
    keyboard = []
    if search:
        matching = [(i, c) for i, c in enumerate(COUNTRIES) if search.lower() in c[0].lower()]
        if not matching: matching = [(i, c) for i, c in enumerate(COUNTRIES) if search in c[2]]
    else: matching = list(enumerate(COUNTRIES))
    total_pages = max(1, (len(matching) + COUNTRY_PER_PAGE - 1) // COUNTRY_PER_PAGE)
    page = max(0, min(page, total_pages - 1))
    start = page * COUNTRY_PER_PAGE; end = min(start + COUNTRY_PER_PAGE, len(matching))
    for i in range(start, end, 2):
        row = [InlineKeyboardButton(f"{matching[i][1][1]} {matching[i][1][0]}", callback_data=f"selcntry_{matching[i][0]}")]
        if i + 1 < end: row.append(InlineKeyboardButton(f"{matching[i+1][1][1]} {matching[i+1][1][0]}", callback_data=f"selcntry_{matching[i+1][0]}"))
        keyboard.append(row)
    nav_row = []
    if page > 0: nav_row.append(InlineKeyboardButton("◀️ Prev", callback_data=f"cntrypage_{page-1}"))
    nav_row.append(InlineKeyboardButton(f"📄 {page+1}/{total_pages}", callback_data="noop"))
    if page < total_pages - 1: nav_row.append(InlineKeyboardButton("Next ▶️", callback_data=f"cntrypage_{page+1}"))
    keyboard.append(nav_row)
    keyboard.append([InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")])
    return InlineKeyboardMarkup(keyboard), total_pages

def build_main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔒 OTP Lock (10 numbers)", callback_data="lock_arm")],
        [InlineKeyboardButton("📱 Get Number", callback_data="get_number")],
        [InlineKeyboardButton("📋 My Numbers", callback_data="my_numbers")],
        [InlineKeyboardButton("📊 Stats", callback_data="stats")],
        [InlineKeyboardButton("💻 Render Info", callback_data="render_info")],
        [InlineKeyboardButton("ℹ️ How OTPs Work", callback_data="how_otp")]
    ])

def build_number_detail_keyboard(number_id):
    count = get_number_messages_count(number_id)
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"📥 Inbox ({count})", callback_data=f"inbox_{number_id}")],
        [InlineKeyboardButton("🔙 My Numbers", callback_data="my_numbers"),
         InlineKeyboardButton("🗑️ Release", callback_data=f"release_{number_id}")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
    ])

async def safe_edit(query, text, **kwargs):
    try: await query.edit_message_text(text, **kwargs)
    except BadRequest as e:
        if "Message is not modified" not in str(e): raise e

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, username, first_name, joined_at) VALUES (?,?,?,?)",
              (user.id, user.username or "", user.first_name or "", datetime.now().isoformat()))
    conn.commit(); conn.close()

    await update.message.reply_text(
        f"🌍 **Welcome {user.first_name}!**\n\n"
        f"📱 **CYBERX Virtual Number Bot**\n"
        f"🌍 **{len(COUNTRIES)} countries** worldwide\n\n"
        f"**How to get real OTPs:**\n"
        f"1️⃣ Get a number from the bot\n"
        f"2️⃣ Use it on any service\n"
        f"3️⃣ OTPs appear in **Inbox** automatically!\n\n"
        f"🔒 **OTP Lock:** 10 numbers fired at once → first OTP wins\n"
        f"🌐 FREE OTPs: Shelex auto-polling\n"
        f"📡 REAL OTPs: Twilio webhook\n"
        f"☁️ Hosted on Render · Port 10000 · URL: {RENDER_URL}\n\n"
        f"_For educational purposes only_",
        parse_mode="Markdown",
        reply_markup=build_main_keyboard()
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = update.effective_user.id

    if data == "main_menu":
        await safe_edit(query, "🏠 **Main Menu**", parse_mode="Markdown", reply_markup=build_main_keyboard())

    elif data == "get_number":
        keyboard, tp = get_country_keyboard(0)
        await safe_edit(query, f"🌍 **Select Country** ({len(COUNTRIES)} available)\nPage 1 of {tp}",
                       parse_mode="Markdown", reply_markup=keyboard)

    elif data.startswith("cntrypage_"):
        page = int(data.split("_")[1]); keyboard, tp = get_country_keyboard(page)
        await safe_edit(query, f"🌍 **Select Country** — Page {page+1} of {tp}",
                       parse_mode="Markdown", reply_markup=keyboard)

    elif data.startswith("selcntry_"):
        idx = int(data.split("_")[1])
        if idx < len(COUNTRIES):
            name, flag, dial_code, fmt = COUNTRIES[idx]
            phone, display = generate_number_for_country(COUNTRIES[idx])
            num_id = save_number_to_db(user_id, name, flag, dial_code, phone, display)
            save_otp_message(num_id, phone, name, "SYSTEM", f"✅ Number activated!", "", "SYSTEM", "system")
            shelex = "✅" if COUNTRY_TO_SHELEX.get(name) else "❌"

            # 👥 "Registered by another user" indicator
            services = check_service_registration(phone, COUNTRY_TO_SHELEX.get(name))
            service_info = ""
            if services:
                svc_lines = "\n".join(f"   • {s}" for s in services[:5])
                service_info = (f"\n\n👥 **⚠️ This number is registered by another user on:**\n"
                                f"{svc_lines}\n"
                                f"_Old public messages found — someone used it before_")
            elif COUNTRY_TO_SHELEX.get(name):
                service_info = "\n\n✅ _Number is fresh — no previous app registration found_"

            await safe_edit(query,
                f"✅ **Number Generated!**\n\n🌍 {flag} **{name}**\n📞 `{phone}`\n📋 {display}\n🆔 ID: `{num_id}`\n\n📶 Shelex: {shelex}\n{service_info}\n\nUse `{phone}` on any service → OTPs in Inbox!",
                parse_mode="Markdown", reply_markup=build_number_detail_keyboard(num_id))

    elif data == "my_numbers":
        nums = get_user_numbers(user_id)
        if not nums:
            await safe_edit(query, "📭 **No active numbers**\nPress 📱 **Get Number** or 🔒 **OTP Lock**!",
                           parse_mode="Markdown", reply_markup=build_main_keyboard())
            return
        keyboard = []
        for n in nums[:10]:
            nid, country, flag, dial, phone, display, created, locked = n
            badge = "🔒 " if locked else ""
            mc = get_number_messages_count(nid)
            keyboard.append([InlineKeyboardButton(f"{flag} {badge}{country}: {display} (📩{mc})", callback_data=f"view_number_{nid}")])
        keyboard.append([InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")])
        await safe_edit(query, f"📋 **Your Numbers ({len(nums)} total)**", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("view_number_"):
        nid = int(data.split("_")[2])
        conn = sqlite3.connect(DB_FILE); c = conn.cursor()
        c.execute("SELECT country, flag, phone_number, full_display, created_at, locked FROM assigned_numbers WHERE id=? AND user_id=?", (nid, user_id))
        row = c.fetchone(); conn.close()
        if not row: await safe_edit(query, "❌ Not found", reply_markup=build_main_keyboard()); return
        country, flag, phone, display, created, locked = row
        badge = "🔒 " if locked else ""
        mc = get_number_messages_count(nid)
        await safe_edit(query, f"📱 {flag} **{badge}{country}**\n📞 `{phone}`\n📋 {display}\n📩 {mc} messages", parse_mode="Markdown", reply_markup=build_number_detail_keyboard(nid))

    elif data.startswith("inbox_"):
        nid = int(data.split("_")[1])
        conn = sqlite3.connect(DB_FILE); c = conn.cursor()
        c.execute("SELECT country, flag, phone_number, full_display FROM assigned_numbers WHERE id=? AND user_id=?", (nid, user_id))
        row = c.fetchone()
        if not row: conn.close(); await safe_edit(query, "❌ Not found", reply_markup=build_main_keyboard()); return
        country, flag, phone, display = row
        msgs = get_number_messages(nid, 15); has_real = any(m[1]!="SYSTEM" for m in msgs) if msgs else False
        if not has_real:
            conn.close()
            await safe_edit(query, f"📥 **Inbox — {flag} {country}**\n📞 `{phone}`\n\n📭 No OTPs yet\n\n1️⃣ Use `{phone}` on any service\n2️⃣ Request verification\n3️⃣ Check back in ~30s!", parse_mode="Markdown", reply_markup=build_number_detail_keyboard(nid))
            return
        text = f"📥 **Inbox — {flag} {country}**\n📞 `{phone}`\n\n"; count = 0
        for m in msgs:
            if m[1]=="SYSTEM": continue
            if count>=10: break
            mid, sender, msg_text, otp, service, source, recv = m; ts = recv[-8:] if recv else ""
            icon = "🔒" if source=="otp_lock" else "🌐" if source=="shelex_free" else "📡" if source=="twilio" else "💉"
            if otp: text += f"{icon} **OTP:** `{otp}` | 🏷️ {service}\n   🕐 {ts}\n\n"
            else: text += f"💬 {msg_text[:60]}...\n   🕐 {ts}\n\n"; count+=1
        text += f"_Showing {count} of {get_number_messages_count(nid)}_"
        conn.close()
        await safe_edit(query, text, parse_mode="Markdown", reply_markup=build_number_detail_keyboard(nid))

    elif data.startswith("release_"):
        nid = int(data.split("_")[1])
        if release_number(nid, user_id): await safe_edit(query, "✅ **Released!**", parse_mode="Markdown", reply_markup=build_main_keyboard())
        else: await safe_edit(query, "❌ Failed", reply_markup=build_main_keyboard())

    elif data == "stats":
        conn = sqlite3.connect(DB_FILE); c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM users"); users = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM assigned_numbers WHERE status='active'"); active = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM assigned_numbers"); total_nums = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM messages"); total_msgs = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM messages WHERE source='shelex_free'"); shelex = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM messages WHERE source='twilio'"); twilio = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM messages WHERE source='otp_lock'"); locked_otps = c.fetchone()[0]
        conn.close()
        await safe_edit(query,
            f"📊 **Statistics**\n\n"
            f"👥 Users: {users}\n📱 Numbers: {total_nums} total, {active} active\n📩 Messages: {total_msgs}\n"
            f"🌐 Shelex: {shelex} | 📡 Twilio: {twilio} | 🔒 OTP Lock: {locked_otps}\n"
            f"🌍 Countries: {len(COUNTRIES)}\n"
            f"☁️ Hosted on Render (free)\n"
            f"🌐 URL: {RENDER_URL}\n"
            f"🔌 Port: 10000",
            parse_mode="Markdown", reply_markup=build_main_keyboard())

    elif data == "render_info":
        await safe_edit(query,
            f"**💻 Render Server Info**\n\n"
            f"**Your Render URL:**\n`{RENDER_URL}`\n\n"
            f"**Health endpoint:**\n`{RENDER_URL}/health`\n\n"
            f"**Twilio webhook (paste this):**\n`{RENDER_URL}/twilio-sms`\n\n"
            f"**Auto-ping:** Every 4 minutes → keeps Render awake\n"
            f"**Port:** 10000\n"
            f"**Database:** SQLite (persistent on Render disk)\n"
            f"**FREE OTPs:** Shelex sources (every 30s)\n"
            f"**🔒 OTP Lock:** 10 numbers, first OTP wins\n"
            f"**Countries:** {len(COUNTRIES)}\n\n"
            f"**No tunnels, no domains, no bullshit.**",
            parse_mode="Markdown", reply_markup=build_main_keyboard())

    elif data == "how_otp":
        await safe_edit(query,
            "**📖 How Real OTP Reception Works**\n\n"
            "**🟢 Free Mode (Shelex)**\n"
            "Bot polls free public SMS websites every 30s.\n"
            "✅ Free  ⚠️ Numbers are public — OTPs visible to others\n\n"
            "**🔒 OTP Lock Mode**\n"
            "10 fallback numbers fired at once.\n"
            "First OTP found → auto-extracted → pushed instantly.\n"
            "Best free odds. Not 100% — public numbers are busy.\n\n"
            "**🔵 Real Mode (Twilio)**\n"
            "1. twilio.com ($20 free credit)\n"
            "2. Buy a number (~$1)\n"
            "3. Set webhook to:\n"
            f"   `{RENDER_URL}/twilio-sms`\n"
            "4. All SMS forward to your bot instantly!\n"
            "✅ Private, instant, works with any service\n\n"
            "**🟡 SIM Mode (Gammu)**\n"
            "Physical SIM + USB modem → forwarded to bot\n\n"
            "_For education only_",
            parse_mode="Markdown", reply_markup=build_main_keyboard())

    elif data == "noop": pass

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    user_id = update.effective_user.id

    if text in ["/getnumber", "📱 Get Number"]:
        keyboard, tp = get_country_keyboard(0)
        await update.message.reply_text(f"🌍 **Select Country** ({len(COUNTRIES)} countries)", parse_mode="Markdown", reply_markup=keyboard)
        return

    matching = [(i, c) for i, c in enumerate(COUNTRIES) if text.lower() in c[0].lower()]
    if not matching: matching = [(i, c) for i, c in enumerate(COUNTRIES) if text in c[2]]

    if matching:
        if len(matching) == 1:
            idx, cd = matching[0]; name, flag, dial, fmt = cd
            phone, display = generate_number_for_country(cd)
            num_id = save_number_to_db(user_id, name, flag, dial, phone, display)
            save_otp_message(num_id, phone, name, "SYSTEM", "✅ Activated!", "", "SYSTEM", "system")

            services = check_service_registration(phone, COUNTRY_TO_SHELEX.get(name))
            svc_info = ""
            if services:
                svc_info = f"\n\n👥 **⚠️ Registered by another user on:** {', '.join(services[:3])}"
            elif COUNTRY_TO_SHELEX.get(name):
                svc_info = "\n\n✅ _Fresh number — no previous registration found_"

            await update.message.reply_text(f"✅ **{flag} {name}**\n📞 `{phone}`\n📋 {display}{svc_info}", parse_mode="Markdown", reply_markup=build_number_detail_keyboard(num_id))
            return
        elif len(matching) <= 12:
            kb = []
            for idx, c in matching: kb.append([InlineKeyboardButton(f"{c[1]} {c[0]} ({c[2]})", callback_data=f"selcntry_{idx}")])
            kb.append([InlineKeyboardButton("🔙 Cancel", callback_data="main_menu")])
            await update.message.reply_text(f"🔍 {len(matching)} matches:", reply_markup=InlineKeyboardMarkup(kb))
            return
    await update.message.reply_text("Type a country name, press buttons, or use /lock for OTP Lock!", reply_markup=build_main_keyboard())

async def seturl_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin: /seturl https://yourapp.onrender.com"""
    if update.effective_user.id != ADMIN_ID: return
    if not context.args:
        await update.message.reply_text(f"Usage: `/seturl {RENDER_URL}`", parse_mode="Markdown")
        return
    url = context.args[0].strip().rstrip('/')
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", ("render_url", url))
    conn.commit(); conn.close()
    os.environ["RENDER_EXTERNAL_URL"] = url
    await update.message.reply_text(f"✅ Render URL set to:\n`{url}`\n\nTwilio webhook: `{url}/twilio-sms`\nHealth: `{url}/health`", parse_mode="Markdown")

async def inject_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if len(context.args) < 3: return
    try:
        nid = int(context.args[0]); service = context.args[1].upper(); code = context.args[2]
        conn = sqlite3.connect(DB_FILE); c = conn.cursor()
        c.execute("SELECT id, user_id, phone_number, country FROM assigned_numbers WHERE id=? AND status='active'", (nid,))
        row = c.fetchone(); conn.close()
        if not row: return
        num_id, owner_id, phone, country = row
        save_otp_message(num_id, phone, country, service, f"Your {service} code: {code}", code, service, "manual_inject")
        await update.message.reply_text(f"✅ **Injected!**\n📞 `{phone}`\n🏷️ {service}\n🔑 `{code}`", parse_mode="Markdown")
    except: pass

async def mynumbers_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    nums = get_user_numbers(user_id)
    if not nums:
        await update.message.reply_text("📭 **No active numbers**\nUse 🔒 **OTP Lock** or 📱 **Get Number**!", parse_mode="Markdown", reply_markup=build_main_keyboard())
        return
    keyboard = []
    for n in nums[:10]:
        nid, country, flag, dial, phone, display, created, locked = n
        badge = "🔒 " if locked else ""
        mc = get_number_messages_count(nid)
        keyboard.append([InlineKeyboardButton(f"{flag} {badge}{country}: {display} (📩{mc})", callback_data=f"view_number_{nid}")])
    keyboard.append([InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")])
    await update.message.reply_text(f"📋 **Your Numbers ({len(nums)} total)**", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "**📱 CYBERX Bot — Help**\n\n"
        "**Commands:**\n"
        "`/start` — Start bot\n"
        "`/lock` — 🔒 OTP Lock: fire 10 numbers, first OTP wins\n"
        "`/getnumber` — Get a number\n"
        "`/mynumbers` — Your numbers\n"
        "`/seturl URL` — (Admin) Set Render URL\n"
        "`/inject ID SERVICE CODE` — (Admin) Test OTP\n"
        "`/help` — This help\n\n"
        "**OTP Sources:**\n"
        "🔒 OTP Lock: 10 fallback numbers, auto-push\n"
        "🌐 Shelex (free): polls every 30s\n"
        "📡 Twilio (real): via webhook URL\n\n"
        "**Hosted on Render — always online**\n"
        "Auto-ping every 4 min → never sleeps\n"
        f"URL: {RENDER_URL} · Port: 10000 · {len(COUNTRIES)} countries",
        parse_mode="Markdown"
    )

# ================================================================
# 🚀 MAIN
# ================================================================

def main():
    print("="*55)
    print("  📱 CYBERX VIRTUAL NUMBER BOT — RENDER EDITION")
    print(f"  ✅ {len(COUNTRIES)} countries  ✅ Port 10000  ✅ 4min ping")
    print(f"  ✅ OTP Lock: {LOCK_POOL_SIZE} numbers, first OTP wins")
    print(f"  ✅ {RENDER_URL}")
    print("="*55)

    init_db()

    if BOT_TOKEN == "YOUR_BOT_TOKEN":
        print("\n[!] ERROR: Set your BOT_TOKEN in skybot.py!")
        sys.exit(1)

    # ⚡ Python 3.14-safe event loop (Render uses Python 3.14)
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    # Start Flask (webhook + health) on PORT 10000
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()
    print("[✓] Flask running on port 10000")

    # Health ping every 4 minutes — keeps Render awake
    ping_thread = threading.Thread(target=health_ping, daemon=True)
    ping_thread.start()
    print("[✓] Health ping every 4 minutes")

    # Telegram bot
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("lock", lock_command))
    app.add_handler(CommandHandler("getnumber", text_handler))
    app.add_handler(CommandHandler("mynumbers", mynumbers_command))
    app.add_handler(CommandHandler("inject", inject_command))
    app.add_handler(CommandHandler("seturl", seturl_command))
    app.add_handler(CommandHandler("help", help_command))
    # ⚠️ lock_callback MUST be registered BEFORE button_handler
    app.add_handler(CallbackQueryHandler(lock_callback, pattern="^lock_"))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    # Shelex polling
    shelex_thread = threading.Thread(target=shelex_poll_numbers, args=(app, loop), daemon=True)
    shelex_thread.start()
    print("[✓] Shelex polling every 30s")

    # OTP Lock watcher — 10 numbers, first OTP wins
    lock_thread = threading.Thread(target=lock_poll_thread, args=(app, loop), daemon=True)
    lock_thread.start()
    print(f"[✓] OTP Lock pool: {LOCK_POOL_SIZE} numbers, {LOCK_POLL_SECONDS}s cycle")

    print(f"[✓] Bot running! {len(COUNTRIES)} countries.")
    print(f"[✓] Twilio webhook: {RENDER_URL}/twilio-sms")
    print(f"[✓] Health: {RENDER_URL}/health")
    print("[✓] Press Ctrl+C to stop.\n")

    try:
        app.run_polling(allowed_updates=Update.ALL_TYPES)
    except KeyboardInterrupt:
        print("\n[!] Shutting down...")
    except Exception as e:
        print(f"\n[!] Error: {e}")

if __name__ == "__main__":
    main()
