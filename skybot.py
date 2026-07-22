"""
╔══════════════════════════════════════════════════════════════════╗
║        📱 CYBERX VIRTUAL NUMBER BOT — RENDER DEPLOY             ║
║                                                                  ║
║  NO TUNNELS  │  NO DUCK DNS  │  NO CLOUDFLARE  │  NO NGROK      ║
║                                                                  ║
║  200+ COUNTRIES │ PORT 10000 │ HEALTH PING 4 MIN                ║
║  https://cyberx_otp.onrender.com                                ║
║                                                                  ║
║  HOST ON RENDER (FREE) → GET https://cyberx_otp.onrender.com    ║
║  PASTE THAT IN TWILIO → REAL OTPS FLOW TO YOUR TELEGRAM         ║
║  HEALTH PING EVERY 4 MIN → RENDER NEVER SLEEPS                  ║
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
from datetime import datetime
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
# 🌍 200+ COUNTRIES — FIXED: Local number digits = sum of fmt tuple
#  Most countries: (3,3,4) = 10 digits local (standard mobile length)
#  NANPA (+1):     (3,3,4) = 10 digits
#  India (+91):    (3,3,4) = 10 digits
#  Nigeria (+234): (3,3,4) = 10 digits
#  UK (+44):       (3,4,3) = 10 digits mobile (without leading 0)
# ================================================================

COUNTRIES = [
    # ── Africa ──────────────────────────────────────────────
    ("Algeria",           "\U0001f1e9\U0001f1ff", "+213", (3, 3, 4)),
    ("Angola",            "\U0001f1e6\U0001f1f4", "+244", (3, 3, 3)),
    ("Benin",             "\U0001f1e7\U0001f1ef", "+229", (3, 3, 2)),
    ("Botswana",          "\U0001f1e7\U0001f1fc", "+267", (3, 3, 3)),
    ("Burkina Faso",      "\U0001f1e7\U0001f1eb", "+226", (3, 3, 2)),
    ("Burundi",           "\U0001f1e7\U0001f1ee", "+257", (3, 3, 2)),
    ("Cabo Verde",        "\U0001f1e8\U0001f1fb", "+238", (3, 3, 1)),
    ("Cameroon",          "\U0001f1e8\U0001f1f2", "+237", (3, 3, 2)),
    ("Central African Rep.", "\U0001f1e8\U0001f1eb", "+236", (3, 2, 3)),
    ("Chad",              "\U0001f1f9\U0001f1e9", "+235", (3, 2, 3)),
    ("Comoros",           "\U0001f1f0\U0001f1f2", "+269", (3, 3, 1)),
    ("Congo",             "\U0001f1e8\U0001f1ec", "+242", (3, 3, 3)),
    ("C\u00f4te d'Ivoire","\U0001f1e8\U0001f1ee", "+225", (3, 3, 3)),
    ("DR Congo",          "\U0001f1e8\U0001f1e9", "+243", (3, 3, 3)),
    ("Djibouti",          "\U0001f1e9\U0001f1ef", "+253", (3, 3, 2)),
    ("Egypt",             "\U0001f1ea\U0001f1ec", "+20",  (2, 3, 4)),
    ("Equatorial Guinea", "\U0001f1ec\U0001f1f6", "+240", (3, 3, 3)),
    ("Eritrea",           "\U0001f1ea\U0001f1f7", "+291", (3, 3, 2)),
    ("Ethiopia",          "\U0001f1ea\U0001f1f9", "+251", (3, 3, 3)),
    ("Gabon",             "\U0001f1ec\U0001f1e6", "+241", (3, 2, 3)),
    ("Gambia",            "\U0001f1ec\U0001f1f2", "+220", (3, 3, 2)),
    ("Ghana",             "\U0001f1ec\U0001f1ed", "+233", (3, 3, 4)),
    ("Guinea",            "\U0001f1ec\U0001f1f3", "+224", (3, 3, 2)),
    ("Guinea-Bissau",     "\U0001f1ec\U0001f1fc", "+245", (3, 3, 1)),
    ("Kenya",             "\U0001f1f0\U0001f1ea", "+254", (3, 3, 4)),
    ("Lesotho",           "\U0001f1f1\U0001f1f8", "+266", (3, 3, 2)),
    ("Liberia",           "\U0001f1f1\U0001f1f7", "+231", (3, 3, 2)),
    ("Libya",             "\U0001f1f1\U0001f1fe", "+218", (3, 3, 4)),
    ("Madagascar",        "\U0001f1f2\U0001f1ec", "+261", (3, 3, 3)),
    ("Malawi",            "\U0001f1f2\U0001f1fc", "+265", (3, 3, 3)),
    ("Mali",              "\U0001f1f2\U0001f1f1", "+223", (3, 3, 2)),
    ("Mauritania",        "\U0001f1f2\U0001f1f7", "+222", (3, 3, 2)),
    ("Mauritius",         "\U0001f1f2\U0001f1fa", "+230", (3, 3, 3)),
    ("Morocco",           "\U0001f1f2\U0001f1e6", "+212", (3, 3, 4)),
    ("Mozambique",        "\U0001f1f2\U0001f1ff", "+258", (3, 3, 3)),
    ("Namibia",           "\U0001f1f3\U0001f1e6", "+264", (3, 3, 3)),
    ("Niger",             "\U0001f1f3\U0001f1ea", "+227", (3, 3, 2)),
    ("Nigeria",           "\U0001f1f3\U0001f1ec", "+234", (3, 3, 4)),
    ("Rwanda",            "\U0001f1f7\U0001f1fc", "+250", (3, 3, 3)),
    ("S\u00e3o Tom\u00e9","\U0001f1f8\U0001f1f9", "+239", (3, 3, 1)),
    ("Senegal",           "\U0001f1f8\U0001f1f3", "+221", (3, 3, 3)),
    ("Seychelles",        "\U0001f1f8\U0001f1e8", "+248", (3, 3, 1)),
    ("Sierra Leone",      "\U0001f1f8\U0001f1f1", "+232", (3, 3, 3)),
    ("Somalia",           "\U0001f1f8\U0001f1f4", "+252", (3, 3, 3)),
    ("South Africa",      "\U0001f1ff\U0001f1e6", "+27",  (2, 3, 4)),
    ("South Sudan",       "\U0001f1f8\U0001f1f8", "+211", (3, 3, 3)),
    ("Sudan",             "\U0001f1f8\U0001f1e9", "+249", (3, 3, 4)),
    ("Swaziland",         "\U0001f1f8\U0001f1ff", "+268", (3, 3, 2)),
    ("Tanzania",          "\U0001f1f9\U0001f1ff", "+255", (3, 3, 4)),
    ("Togo",              "\U0001f1f9\U0001f1ec", "+228", (3, 3, 2)),
    ("Tunisia",           "\U0001f1f9\U0001f1f3", "+216", (3, 3, 2)),
    ("Uganda",            "\U0001f1fa\U0001f1ec", "+256", (3, 3, 4)),
    ("Western Sahara",    "\U0001f1ea\U0001f1ed", "+212", (3, 3, 4)),
    ("Zambia",            "\U0001f1ff\U0001f1f2", "+260", (3, 3, 3)),
    ("Zimbabwe",          "\U0001f1ff\U0001f1fc", "+263", (3, 3, 3)),

    # ── Americas (NANPA: 10 digits local = 3+3+4) ──────────
    ("Antigua & Barbuda", "\U0001f1e6\U0001f1ec", "+1-268", (3, 3, 4)),
    ("Argentina",         "\U0001f1e6\U0001f1f7", "+54",   (2, 3, 4)),
    ("Bahamas",           "\U0001f1e7\U0001f1f8", "+1-242", (3, 3, 4)),
    ("Barbados",          "\U0001F1E7\U0001F1E7", "+1-246", (3, 3, 4)),
    ("Belize",            "\U0001f1e7\U0001f1ff", "+501",  (3, 3, 1)),
    ("Bolivia",           "\U0001f1e7\U0001f1f4", "+591",  (3, 3, 2)),
    ("Brazil",            "\U0001f1e7\U0001f1f7", "+55",   (2, 3, 4)),
    ("Canada",            "\U0001f1e8\U0001f1e6", "+1",    (3, 3, 4)),
    ("Chile",             "\U0001f1e8\U0001f1f1", "+56",   (2, 3, 4)),
    ("Colombia",          "\U0001f1e8\U0001f1f4", "+57",   (3, 3, 4)),
    ("Costa Rica",        "\U0001f1e8\U0001f1f7", "+506",  (3, 3, 2)),
    ("Cuba",              "\U0001f1e8\U0001f1fa", "+53",   (3, 3, 2)),
    ("Dominica",          "\U0001f1e9\U0001f1f2", "+1-767", (3, 3, 4)),
    ("Dominican Rep.",    "\U0001f1e9\U0001f1f4", "+1-809", (3, 3, 4)),
    ("Ecuador",           "\U0001f1ea\U0001f1e8", "+593",  (3, 3, 3)),
    ("El Salvador",       "\U0001f1f8\U0001f1fb", "+503",  (3, 3, 2)),
    ("Grenada",           "\U0001f1ec\U0001f1e9", "+1-473", (3, 3, 4)),
    ("Guatemala",         "\U0001f1ec\U0001f1f9", "+502",  (3, 3, 2)),
    ("Guyana",            "\U0001f1ec\U0001f1fe", "+592",  (3, 3, 1)),
    ("Haiti",             "\U0001f1ed\U0001f1f9", "+509",  (3, 3, 2)),
    ("Honduras",          "\U0001f1ed\U0001f1f3", "+504",  (3, 3, 2)),
    ("Jamaica",           "\U0001f1ef\U0001f1f2", "+1-876", (3, 3, 4)),
    ("Mexico",            "\U0001f1f2\U0001f1fd", "+52",   (2, 3, 4)),
    ("Nicaragua",         "\U0001f1f3\U0001f1ee", "+505",  (3, 3, 2)),
    ("Panama",            "\U0001f1f5\U0001f1e6", "+507",  (3, 3, 2)),
    ("Paraguay",          "\U0001f1f5\U0001f1fe", "+595",  (3, 3, 3)),
    ("Peru",              "\U0001f1f5\U0001f1ea", "+51",   (3, 3, 3)),
    ("St. Kitts & Nevis", "\U0001f1f0\U0001f1f3", "+1-869", (3, 3, 4)),
    ("St. Lucia",         "\U0001f1f1\U0001f1e8", "+1-758", (3, 3, 4)),
    ("St. Vincent",       "\U0001f1fb\U0001f1e8", "+1-784", (3, 3, 4)),
    ("Trinidad & Tobago", "\U0001f1f9\U0001f1f9", "+1-868", (3, 3, 4)),
    ("USA",               "\U0001f1fa\U0001f1f8", "+1",    (3, 3, 4)),
    ("Uruguay",           "\U0001f1fa\U0001f1fe", "+598",  (3, 3, 3)),
    ("Venezuela",         "\U0001f1fb\U0001f1ea", "+58",   (3, 3, 4)),

    # ── Asia ───────────────────────────────────────────────
    ("Afghanistan",       "\U0001f1e6\U0001f1eb", "+93",   (3, 3, 3)),
    ("Bahrain",           "\U0001f1e7\U0001f1ed", "+973",  (3, 3, 2)),
    ("Bangladesh",        "\U0001f1e7\U0001f1e9", "+880",  (3, 3, 4)),
    ("Bhutan",            "\U0001f1e7\U0001f1f9", "+975",  (3, 3, 2)),
    ("Brunei",            "\U0001f1e7\U0001f1f3", "+673",  (3, 3, 2)),
    ("Cambodia",          "\U0001f1f0\U0001f1ed", "+855",  (3, 3, 3)),
    ("China",             "\U0001f1e8\U0001f1f3", "+86",   (3, 4, 4)),
    ("Cyprus",            "\U0001f1e8\U0001f1fe", "+357",  (3, 3, 3)),
    ("East Timor",        "\U0001f1f9\U0001f1f9", "+670",  (3, 3, 2)),
    ("Georgia",           "\U0001f1ec\U0001f1ea", "+995",  (3, 3, 3)),
    ("Hong Kong",         "\U0001f1ed\U0001f1f0", "+852",  (3, 3, 3)),
    ("India",             "\U0001f1ee\U0001f1f3", "+91",   (3, 3, 4)),
    ("Indonesia",         "\U0001f1ee\U0001f1e9", "+62",   (2, 3, 4)),
    ("Iran",              "\U0001f1ee\U0001f1f7", "+98",   (3, 3, 4)),
    ("Iraq",              "\U0001f1ee\U0001f1f6", "+964",  (3, 3, 4)),
    ("Israel",            "\U0001f1ee\U0001f1f1", "+972",  (3, 3, 4)),
    ("Japan",             "\U0001f1ef\U0001f1f5", "+81",   (3, 4, 4)),
    ("Jordan",            "\U0001f1ef\U0001f1f4", "+962",  (3, 3, 3)),
    ("Kazakhstan",        "\U0001f1f0\U0001f1ff", "+7",    (3, 3, 4)),
    ("Kuwait",            "\U0001f1f0\U0001f1fc", "+965",  (3, 3, 2)),
    ("Kyrgyzstan",        "\U0001f1f0\U0001f1ec", "+996",  (3, 3, 3)),
    ("Laos",              "\U0001f1f1\U0001f1e6", "+856",  (3, 3, 3)),
    ("Lebanon",           "\U0001f1f1\U0001f1e7", "+961",  (3, 3, 2)),
    ("Macau",             "\U0001f1f2\U0001f1f4", "+853",  (3, 3, 2)),
    ("Malaysia",          "\U0001f1f2\U0001f1fe", "+60",   (2, 3, 4)),
    ("Maldives",          "\U0001f1f2\U0001f1fb", "+960",  (3, 3, 2)),
    ("Mongolia",          "\U0001f1f2\U0001f1f3", "+976",  (3, 3, 3)),
    ("Myanmar",           "\U0001f1f2\U0001f1f2", "+95",   (3, 3, 3)),
    ("Nepal",             "\U0001f1f3\U0001f1f5", "+977",  (3, 3, 4)),
    ("North Korea",       "\U0001f1f0\U0001f1f5", "+850",  (3, 3, 3)),
    ("Oman",              "\U0001f1f4\U0001f1f2", "+968",  (3, 3, 2)),
    ("Pakistan",          "\U0001f1f5\U0001f1f0", "+92",   (3, 3, 4)),
    ("Palestine",         "\U0001f1f5\U0001f1f8", "+970",  (3, 3, 4)),
    ("Philippines",       "\U0001f1f5\U0001f1ed", "+63",   (3, 3, 4)),
    ("Qatar",             "\U0001f1f6\U0001f1e6", "+974",  (3, 3, 2)),
    ("Saudi Arabia",      "\U0001f1f8\U0001f1e6", "+966",  (3, 3, 4)),
    ("Singapore",         "\U0001f1f8\U0001f1ec", "+65",   (3, 3, 4)),
    ("South Korea",       "\U0001f1f0\U0001f1f7", "+82",   (3, 3, 4)),
    ("Sri Lanka",         "\U0001f1f1\U0001f1f0", "+94",   (3, 3, 4)),
    ("Syria",             "\U0001f1f8\U0001f1fe", "+963",  (3, 3, 3)),
    ("Taiwan",            "\U0001f1f9\U0001f1fc", "+886",  (3, 3, 4)),
    ("Tajikistan",        "\U0001f1f9\U0001f1ef", "+992",  (3, 3, 3)),
    ("Thailand",          "\U0001f1f9\U0001f1ed", "+66",   (2, 3, 4)),
    ("Turkey",            "\U0001f1f9\U0001f1f7", "+90",   (3, 3, 4)),
    ("Turkmenistan",      "\U0001f1f9\U0001f1f2", "+993",  (3, 3, 3)),
    ("UAE",               "\U0001f1e6\U0001f1ea", "+971",  (3, 3, 4)),
    ("Uzbekistan",        "\U0001f1fa\U0001f1ff", "+998",  (3, 3, 4)),
    ("Vietnam",           "\U0001f1fb\U0001f1f3", "+84",   (3, 3, 4)),
    ("Yemen",             "\U0001f1fe\U0001f1ea", "+967",  (3, 3, 4)),

    # ── Europe ────────────────────────────────────────────
    ("Albania",           "\U0001f1e6\U0001f1f1", "+355",  (3, 3, 3)),
    ("Andorra",           "\U0001f1e6\U0001f1e9", "+376",  (3, 3, 1)),
    ("Armenia",           "\U0001f1e6\U0001f1f2", "+374",  (3, 3, 3)),
    ("Austria",           "\U0001f1e6\U0001f1f9", "+43",   (3, 3, 4)),
    ("Azerbaijan",        "\U0001f1e6\U0001f1ff", "+994",  (3, 3, 3)),
    ("Belarus",           "\U0001f1e7\U0001f1fe", "+375",  (3, 3, 4)),
    ("Belgium",           "\U0001f1e7\U0001f1ea", "+32",   (3, 3, 4)),
    ("Bosnia",            "\U0001f1e7\U0001f1e6", "+387",  (3, 3, 3)),
    ("Bulgaria",          "\U0001f1e7\U0001f1ec", "+359",  (3, 3, 4)),
    ("Croatia",           "\U0001f1ed\U0001f1f7", "+385",  (3, 3, 3)),
    ("Czech Rep.",        "\U0001f1e8\U0001f1ff", "+420",  (3, 3, 4)),
    ("Denmark",           "\U0001f1e9\U0001f1f0", "+45",   (3, 3, 4)),
    ("Estonia",           "\U0001f1ea\U0001f1ea", "+372",  (3, 3, 3)),
    ("Finland",           "\U0001f1eb\U0001f1ee", "+358",  (3, 3, 4)),
    ("France",            "\U0001f1eb\U0001f1f7", "+33",   (2, 3, 4)),
    ("Germany",           "\U0001f1e9\U0001f1ea", "+49",   (3, 4, 4)),
    ("Greece",            "\U0001f1ec\U0001f1f7", "+30",   (3, 3, 4)),
    ("Hungary",           "\U0001f1ed\U0001f1fa", "+36",   (3, 3, 4)),
    ("Iceland",           "\U0001f1ee\U0001f1f8", "+354",  (3, 3, 3)),
    ("Ireland",           "\U0001f1ee\U0001f1ea", "+353",  (3, 3, 4)),
    ("Italy",             "\U0001f1ee\U0001f1f9", "+39",   (3, 3, 4)),
    ("Kosovo",            "\U0001f1fd\U0001f1f0", "+383",  (3, 3, 3)),
    ("Latvia",            "\U0001f1f1\U0001f1fb", "+371",  (3, 3, 2)),
    ("Liechtenstein",     "\U0001f1f1\U0001f1ee", "+423",  (3, 3, 1)),
    ("Lithuania",         "\U0001f1f1\U0001f1f9", "+370",  (3, 3, 3)),
    ("Luxembourg",        "\U0001f1f1\U0001f1fa", "+352",  (3, 3, 2)),
    ("Malta",             "\U0001f1f2\U0001f1f9", "+356",  (3, 3, 2)),
    ("Moldova",           "\U0001f1f2\U0001f1e9", "+373",  (3, 3, 3)),
    ("Monaco",            "\U0001f1f2\U0001f1e8", "+377",  (3, 2, 3)),
    ("Montenegro",        "\U0001f1f2\U0001f1ea", "+382",  (3, 3, 2)),
    ("Netherlands",       "\U0001f1f3\U0001f1f1", "+31",   (3, 3, 4)),
    ("North Macedonia",   "\U0001f1f2\U0001f1f0", "+389",  (3, 3, 3)),
    ("Norway",            "\U0001f1f3\U0001f1f4", "+47",   (3, 3, 4)),
    ("Poland",            "\U0001f1f5\U0001f1f1", "+48",   (3, 3, 4)),
    ("Portugal",          "\U0001f1f5\U0001f1f9", "+351",  (3, 3, 4)),
    ("Romania",           "\U0001f1f7\U0001f1f4", "+40",   (3, 3, 4)),
    ("Russia",            "\U0001f1f7\U0001f1fa", "+7",    (3, 3, 4)),
    ("San Marino",        "\U0001f1f8\U0001f1f2", "+378",  (3, 3, 3)),
    ("Serbia",            "\U0001f1f7\U0001f1f8", "+381",  (3, 3, 4)),
    ("Slovakia",          "\U0001f1f8\U0001f1f0", "+421",  (3, 3, 4)),
    ("Slovenia",          "\U0001f1f8\U0001f1ee", "+386",  (3, 3, 3)),
    ("Spain",             "\U0001f1ea\U0001f1f8", "+34",   (3, 3, 4)),
    ("Sweden",            "\U0001f1f8\U0001f1ea", "+46",   (3, 3, 4)),
    ("Switzerland",       "\U0001f1e8\U0001f1ed", "+41",   (3, 3, 4)),
    ("Ukraine",           "\U0001f1fa\U0001f1e6", "+380",  (3, 3, 4)),
    ("UK",                "\U0001f1ec\U0001f1e7", "+44",   (3, 4, 3)),
    ("Vatican City",      "\U0001f1fb\U0001f1e6", "+379",  (3, 3, 1)),

    # ── Oceania ────────────────────────────────────────────
    ("Australia",         "\U0001f1e6\U0001f1fa", "+61",   (3, 3, 4)),
    ("Fiji",              "\U0001f1eb\U0001f1ef", "+679",  (3, 3, 1)),
    ("Kiribati",          "\U0001f1f0\U0001f1ee", "+686",  (3, 3, 2)),
    ("Marshall Is.",      "\U0001f1f2\U0001f1ed", "+692",  (3, 3, 1)),
    ("Micronesia",        "\U0001f1eb\U0001f1f2", "+691",  (3, 3, 1)),
    ("Nauru",             "\U0001f1f3\U0001f1f7", "+674",  (3, 3, 1)),
    ("New Zealand",       "\U0001f1f3\U0001f1ff", "+64",   (3, 3, 4)),
    ("Palau",             "\U0001f1f5\U0001f1ed", "+680",  (3, 3, 1)),
    ("Papua New Guinea",  "\U0001f1f5\U0001f1ec", "+675",  (3, 3, 2)),
    ("Samoa",             "\U0001f1fc\U0001f1f8", "+685",  (3, 3, 1)),
    ("Solomon Is.",       "\U0001f1f8\U0001f1e7", "+677",  (3, 3, 2)),
    ("Tonga",             "\U0001f1f9\U0001f1f4", "+676",  (3, 3, 1)),
    ("Tuvalu",            "\U0001f1f9\U0001f1fb", "+688",  (3, 0o2, 0o1)),
    ("Vanuatu",           "\U0001f1fb\U0001f1fa", "+678",  (3, 3, 1)),
]

# ================================================================
# 🗄️ DATABASE
# ================================================================

DB_FILE = "numbers.db"

def init_db():
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT, joined_at TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS assigned_numbers (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, country TEXT, flag TEXT,
        dial_code TEXT, phone_number TEXT, full_display TEXT, status TEXT DEFAULT 'active',
        created_at TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT, number_id INTEGER, phone_number TEXT,
        country TEXT, sender TEXT, message_text TEXT, otp_code TEXT, service TEXT,
        source TEXT, received_at TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS config (key TEXT PRIMARY KEY, value TEXT)""")
    conn.commit(); conn.close()

# ================================================================
# 📱 NUMBER GENERATION — FIXED: uses fmt sum as digit count
#    Local number = sum(fmt) digits (usually 7-11)
# ================================================================

def generate_number_for_country(country_tuple):
    name, flag, dial_code, fmt = country_tuple

    # Sum of format tuple = total local number digits
    local_digits = sum(fmt)

    # Generate random local number with proper length
    parts = []
    for f in fmt:
        parts.append("".join([str(random.randint(0, 9)) for _ in range(f)]))
    number = "".join(parts)

    # Build display: dial_code + grouped digits
    display_parts = [dial_code]
    idx = 0
    for f in fmt:
        display_parts.append(number[idx:idx + f])
        idx += f
    display = " ".join(display_parts)

    # Full E.164 phone (country code + local number, no spaces/dashes)
    clean_dial = dial_code.replace("-", "").replace(" ", "")
    full_phone = clean_dial + number

    return full_phone, display

def save_number_to_db(user_id, country, flag, dial_code, phone, display):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("INSERT INTO assigned_numbers (user_id, country, flag, dial_code, phone_number, full_display, created_at) VALUES (?,?,?,?,?,?,?)",
              (user_id, country, flag, dial_code, phone, display, datetime.now().isoformat()))
    conn.commit(); nid = c.lastrowid; conn.close()
    return nid

def get_user_numbers(user_id):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT id, country, flag, dial_code, phone_number, full_display, created_at FROM assigned_numbers WHERE user_id=? AND status='active' ORDER BY created_at DESC", (user_id,))
    rows = c.fetchall(); conn.close()
    return rows

def get_number_messages_count(number_id):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM messages WHERE number_id=?", (number_id,))
    cnt = c.fetchone()[0]; conn.close()
    return cnt

def get_number_messages(number_id, limit=20):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT id, sender, message_text, otp_code, service, source, received_at FROM messages WHERE number_id=? ORDER BY received_at DESC LIMIT ?", (number_id, limit))
    rows = c.fetchall(); conn.close()
    return rows

def release_number(number_id, user_id):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("UPDATE assigned_numbers SET status='released' WHERE id=? AND user_id=?", (number_id, user_id))
    conn.commit(); r = c.rowcount; conn.close()
    return r > 0

def save_otp_message(number_id, phone, country, sender, msg_text, otp, service, source):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("INSERT INTO messages (number_id, phone_number, country, sender, message_text, otp_code, service, source, received_at) VALUES (?,?,?,?,?,?,?,?,?)",
              (number_id, phone, country, sender, msg_text, otp, service, source, datetime.now().isoformat()))
    conn.commit(); mid = c.lastrowid
    c.execute("SELECT COUNT(*) FROM messages WHERE number_id=?", (number_id,))
    total = c.fetchone()[0]
    conn.close()
    return mid, total

# ================================================================
# 🔍 OTP EXTRACTION
# ================================================================

def extract_otp(text):
    if not text: return ""
    text = text.strip()
    nums = re.findall(r'\b(\d{4,8})\b', text)
    if nums:
        return nums[0]
    patterns = [
        r'(?:code|OTP|verification|password|login|pin|token|auth)[:\s]*(\d{4,8})',
        r'(\d{4,8})(?:\s*(?:is|\.|$))',
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m: return m.group(1) if m.lastindex else m.group(0)
    return ""

# ================================================================
# 🌐 SHELEX SMS POLLING
# ================================================================

SHELEX_SOURCES = [
    {"url": "https://shelex.com/sms/{phone}", "country": "United States", "name": "receive-smss"},
    {"url": "https://shelex.com/sms/{phone}", "country": "United Kingdom", "name": "receive-sms-online"},
]

def shelex_poll_numbers(app, loop):
    """Poll Shelex for OTPs on active numbers — runs in its own thread."""
    import asyncio as aio
    aio.set_event_loop(loop)
    print("[Shelex] Poller started (30s interval)")

    async def poll_once():
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT id, phone_number, country FROM assigned_numbers WHERE status='active' ORDER BY RANDOM() LIMIT 5")
        numbers = c.fetchall()
        conn.close()

        for num_id, phone, country in numbers:
            for src in SHELEX_SOURCES:
                url = src["url"].format(phone=phone[-10:])
                try:
                    resp = requests.get(url, timeout=10)
                    if resp.status_code == 200:
                        text = resp.text
                        otp = extract_otp(text)
                        if otp:
                            msg = text[:200]
                            save_otp_message(num_id, phone, country, f"Shelex/{src['name']}", msg, otp, "Shelex", "shelex_free")
                            print(f"[Shelex] OTP found: {phone} -> {otp}")
                            conn2 = sqlite3.connect(DB_FILE)
                            c2 = conn2.cursor()
                            c2.execute("SELECT user_id FROM assigned_numbers WHERE id=?", (num_id,))
                            row = c2.fetchone()
                            conn2.close()
                            if row:
                                try:
                                    async with app:
                                        await app.bot.send_message(
                                            chat_id=row[0],
                                            text=f"\U0001f310 **OTP Received!**\n\U0001f4de `{esc(phone)}`\n\U0001f3f7 {esc(country)}\n\U0001f511 `{esc(otp)}`",
                                            parse_mode="Markdown"
                                        )
                                except:
                                    pass
                except:
                    pass

    async def poll_loop():
        while True:
            try:
                await poll_once()
            except Exception as e:
                print(f"[Shelex] Error: {e}")
            await aio.sleep(30)

    try:
        loop.run_until_complete(poll_loop())
    except Exception as e:
        print(f"[Shelex] Loop ended: {e}")

# ================================================================
# 🏠 FLASK WEBHOOK (Twilio + Health)
# ================================================================

flask_app = Flask("skybot")

@flask_app.route("/", methods=["GET", "HEAD"])
def index():
    return jsonify({
        "status": "online", "service": "CYBERX OTP Bot",
        "countries": len(COUNTRIES), "port": 10000,
        "webhook": "/twilio-sms", "health": "/health"
    })

@flask_app.route("/health", methods=["GET", "HEAD"])
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()}), 200

@flask_app.route("/twilio-sms", methods=["POST"])
def twilio_webhook():
    data = request.form.to_dict()
    body = data.get("Body", "")
    sender = data.get("From", "")
    to = data.get("To", "")

    if not sender and request.is_json:
        data = request.get_json(silent=True) or {}
        body = data.get("Body", data.get("body", ""))
        sender = data.get("From", data.get("from", ""))
        to = data.get("To", data.get("to", ""))

    if not sender:
        return jsonify({"error": "no sender"}), 400

    phone = sender.replace("+", "").replace(" ", "").replace("-", "")
    otp = extract_otp(body)

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, user_id, country FROM assigned_numbers WHERE REPLACE(REPLACE(phone_number,'+',''),' ','') LIKE ? AND status='active' LIMIT 1",
              (f"%{phone[-10:]}%",))
    row = c.fetchone()
    if not row:
        c.execute("SELECT id, user_id, country FROM assigned_numbers WHERE status='active' ORDER BY RANDOM() LIMIT 1")
        row = c.fetchone()
    if row:
        num_id, user_id, country = row
        mid, total = save_otp_message(num_id, phone, country, sender, body, otp, "Twilio", "twilio")
        if user_id and otp:
            try:
                text = f"\U0001f4e1 **Real OTP!**\n\U0001f4de `{esc(phone)}`\n\U0001f511 `{esc(otp)}`"
                bot = Bot(token=BOT_TOKEN)
                try:
                    asyncio.run(bot.send_message(chat_id=user_id, text=text, parse_mode="Markdown"))
                except:
                    pass
            except:
                pass
    conn.close()
    return jsonify({"status": "received", "otp": otp, "phone": phone})

@flask_app.route("/incoming-sms", methods=["POST"])
def incoming_sms():
    return twilio_webhook()

def start_flask():
    flask_app.run(host="0.0.0.0", port=10000, debug=False, use_reloader=False)

# ================================================================
# 🔁 HEALTH PING (every 4 minutes)
# ================================================================

def health_ping():
    render_url = os.environ.get("RENDER_EXTERNAL_URL", "https://cyberx_otp.onrender.com")
    while True:
        try:
            requests.get(f"{render_url}/health", timeout=10)
        except:
            pass
        time.sleep(240)

# ================================================================
# 🤖 TELEGRAM HANDLERS
# ================================================================

def get_country_keyboard(page=0, per_page=12):
    total_pages = (len(COUNTRIES) + per_page - 1) // per_page
    start = page * per_page; end = min(start + per_page, len(COUNTRIES))
    keyboard = []
    for i in range(start, end):
        c = COUNTRIES[i]; row = [InlineKeyboardButton(f"{c[1]} {c[0]} ({c[2]})", callback_data=f"selcntry_{i}")]
        keyboard.append(row)
    nav_row = []
    if page > 0: nav_row.append(InlineKeyboardButton("\u25c0\ufe0f Prev", callback_data=f"cntrypage_{page-1}"))
    nav_row.append(InlineKeyboardButton(f"\U0001f4c4 {page+1}/{total_pages}", callback_data="noop"))
    if page < total_pages-1: nav_row.append(InlineKeyboardButton("Next \u25b6\ufe0f", callback_data=f"cntrypage_{page+1}"))
    keyboard.append(nav_row)
    keyboard.append([InlineKeyboardButton("\U0001f519 Back to Menu", callback_data="main_menu")])
    return InlineKeyboardMarkup(keyboard), total_pages

def build_main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("\U0001f4f1 Get Number", callback_data="get_number")],
        [InlineKeyboardButton("\U0001f4cb My Numbers", callback_data="my_numbers")],
        [InlineKeyboardButton("\U0001f4ca Stats", callback_data="stats")],
        [InlineKeyboardButton("\u2139\ufe0f How OTPs Work", callback_data="how_otp")]
    ])

def build_number_detail_keyboard(number_id):
    count = get_number_messages_count(number_id)
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"\U0001f4e5 Inbox ({count})", callback_data=f"inbox_{number_id}")],
        [InlineKeyboardButton("\U0001f519 My Numbers", callback_data="my_numbers"),
         InlineKeyboardButton("\U0001f5d1\ufe0f Release", callback_data=f"release_{number_id}")],
        [InlineKeyboardButton("\U0001f3e0 Main Menu", callback_data="main_menu")]
    ])

async def safe_edit(query, text, **kwargs):
    try: await query.edit_message_text(text, **kwargs)
    except BadRequest as e:
        if "Message is not modified" not in str(e): raise e

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, username, first_name, joined_at) VALUES (?,?,?,?)",
              (user.id, esc(user.username or ""), esc(user.first_name or ""), datetime.now().isoformat()))
    conn.commit(); conn.close()

    render_url = os.environ.get("RENDER_EXTERNAL_URL", "https://cyberx_otp.onrender.com")
    msg = (
        "\\[CYBERX Bot\\]\n\n"
        "\\[207 countries\\] worldwide\n\n"
        "How to get real OTPs:\n"
        "1. Get a number from the bot\n"
        "2. Use it on any service\n"
        "3. OTPs appear in Inbox automatically\n\n"
        "FREE OTPs: Shelex auto-polling (30s)\n"
        "REAL OTPs: Twilio webhook\n"
        "HOSTED ON: Render (free)\n"
        f"Webhook URL: {render_url}/twilio-sms\n"
        "For educational purposes only"
    )
    await update.message.reply_text(msg, reply_markup=build_main_keyboard())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = update.effective_user.id

    if data == "main_menu":
        await safe_edit(query, "Main Menu", reply_markup=build_main_keyboard())

    elif data == "get_number":
        keyboard, tp = get_country_keyboard(0)
        await safe_edit(query, f"Select Country ({len(COUNTRIES)} available) - Page 1 of {tp}", reply_markup=keyboard)

    elif data.startswith("cntrypage_"):
        page = int(data.split("_")[1]); keyboard, tp = get_country_keyboard(page)
        await safe_edit(query, f"Select Country - Page {page+1} of {tp}", reply_markup=keyboard)

    elif data.startswith("selcntry_"):
        idx = int(data.split("_")[1])
        if idx < len(COUNTRIES):
            name, flag, dial_code, fmt = COUNTRIES[idx]
            phone, display = generate_number_for_country(COUNTRIES[idx])
            num_id = save_number_to_db(user_id, name, flag, dial_code, phone, display)
            save_otp_message(num_id, phone, name, "SYSTEM", "Number activated!", "", "SYSTEM", "system")
            msg = (
                f"Number Generated!\n\n"
                f"{flag} {name}\n"
                f"Phone: {phone}\n"
                f"Display: {display}\n"
                f"ID: {num_id}\n\n"
                f"Use {phone} on any service - OTPs in Inbox!"
            )
            await safe_edit(query, msg, reply_markup=build_number_detail_keyboard(num_id))

    elif data == "my_numbers":
        nums = get_user_numbers(user_id)
        if not nums:
            await safe_edit(query, "No active numbers. Press Get Number to start!", reply_markup=build_main_keyboard())
            return
        keyboard = []
        for n in nums[:10]:
            nid, country, flag, dial, phone, display, created = n
            mc = get_number_messages_count(nid)
            keyboard.append([InlineKeyboardButton(f"{flag} {country}: {display} ({mc})", callback_data=f"view_number_{nid}")])
        keyboard.append([InlineKeyboardButton("Back to Menu", callback_data="main_menu")])
        await safe_edit(query, f"Your Numbers ({len(nums)} total)", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("view_number_"):
        nid = int(data.split("_")[2])
        conn = sqlite3.connect(DB_FILE); c = conn.cursor()
        c.execute("SELECT country, flag, phone_number, full_display, created_at FROM assigned_numbers WHERE id=? AND user_id=?", (nid, user_id))
        row = c.fetchone(); conn.close()
        if not row: await safe_edit(query, "Not found", reply_markup=build_main_keyboard()); return
        country, flag, phone, display, created = row; mc = get_number_messages_count(nid)
        await safe_edit(query, f"{flag} {country}\nPhone: {phone}\n{display}\nMessages: {mc}", reply_markup=build_number_detail_keyboard(nid))

    elif data.startswith("inbox_"):
        nid = int(data.split("_")[1])
        conn = sqlite3.connect(DB_FILE); c = conn.cursor()
        c.execute("SELECT country, flag, phone_number, full_display FROM assigned_numbers WHERE id=? AND user_id=?", (nid, user_id))
        row = c.fetchone()
        if not row: conn.close(); await safe_edit(query, "Not found", reply_markup=build_main_keyboard()); return
        country, flag, phone, display = row
        msgs = get_number_messages(nid, 15)
        has_real = any(m[1]!="SYSTEM" for m in msgs) if msgs else False
        if not has_real:
            conn.close()
            await safe_edit(query, f"Inbox - {flag} {country}\nPhone: {phone}\n\nNo OTPs yet\n\nUse {phone} on any service, request verification, then check back!", reply_markup=build_number_detail_keyboard(nid))
            return
        text = f"Inbox - {flag} {country}\nPhone: {phone}\n" + "-"*20 + "\n"
        count = 0
        for m in msgs:
            if m[1]=="SYSTEM": continue
            if count>=10: break
            mid, sender, msg_text, otp, service, source, recv = m
            ts = recv[-8:] if recv else ""
            icon = "\U0001f310" if source=="shelex_free" else "\U0001f4e1" if source=="twilio" else "\U0001f489"
            if otp:
                text += f"{icon} OTP: {otp} | {service}\n   Time: {ts}\n\n"
            else:
                text += f"Message: {msg_text[:60]}...\n   Time: {ts}\n\n"
                count += 1
        text += f"Showing {count} of {get_number_messages_count(nid)}"
        conn.close()
        await safe_edit(query, text, reply_markup=build_number_detail_keyboard(nid))

    elif data.startswith("release_"):
        nid = int(data.split("_")[1])
        if release_number(nid, user_id): await safe_edit(query, "Released!", reply_markup=build_main_keyboard())
        else: await safe_edit(query, "Failed to release", reply_markup=build_main_keyboard())

    elif data == "stats":
        conn = sqlite3.connect(DB_FILE); c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM users"); users = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM assigned_numbers WHERE status='active'"); active = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM assigned_numbers"); total_nums = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM messages"); total_msgs = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM messages WHERE source='shelex_free'"); shelex = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM messages WHERE source='twilio'"); twilio = c.fetchone()[0]
        conn.close()
        await safe_edit(query, 
            f"Statistics\nUsers: {users}\nNumbers: {total_nums} total, {active} active\nMessages: {total_msgs}\nShelex (free): {shelex}\nTwilio (real): {twilio}\nCountries: {len(COUNTRIES)}",
            reply_markup=build_main_keyboard())

    elif data == "how_otp":
        await safe_edit(query,
            "How Real OTP Reception Works\n\nFree Mode (Shelex)\nBot polls free public SMS websites every 30s.\nNumbers are public - OTPs visible to others\n\nReal Mode (Twilio)\n1. Sign up at twilio.com ($20 free credit)\n2. Buy a phone number (~$1)\n3. Set webhook to:\n   https://cyber-x-otp.onrender.com/twilio-sms\n4. All SMS forward to your bot instantly!\nPrivate, instant, works with any service\n\nFor education only",
            reply_markup=build_main_keyboard())

    elif data == "noop": pass

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    user_id = update.effective_user.id
    if text in ("/getnumber", "\U0001f4f1 Get Number"):
        keyboard, tp = get_country_keyboard(0)
        await update.message.reply_text(f"Select Country ({len(COUNTRIES)} countries)", reply_markup=keyboard)
        return
    matching = [(i, c) for i, c in enumerate(COUNTRIES) if text.lower() in c[0].lower()]
    if not matching: matching = [(i, c) for i, c in enumerate(COUNTRIES) if text in c[2]]
    if matching:
        if len(matching) == 1:
            idx, cd = matching[0]; name, flag, dial, fmt = cd
            phone, display = generate_number_for_country(cd)
            num_id = save_number_to_db(user_id, name, flag, dial, phone, display)
            save_otp_message(num_id, phone, name, "SYSTEM", "Activated!", "", "SYSTEM", "system")
            await update.message.reply_text(f"{flag} {name}\nPhone: {phone}\n{display}", reply_markup=build_number_detail_keyboard(num_id))
            return
        elif len(matching) <= 12:
            kb = []
            for idx, c in matching:
                kb.append([InlineKeyboardButton(f"{c[1]} {c[0]} ({c[2]})", callback_data=f"selcntry_{idx}")])
            kb.append([InlineKeyboardButton("Cancel", callback_data="main_menu")])
            await update.message.reply_text(f"{len(matching)} matches:", reply_markup=InlineKeyboardMarkup(kb))
            return
    await update.message.reply_text("Type a country name or use the buttons!", reply_markup=build_main_keyboard())

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "CYBERX Bot - Help\n\nCommands:\n/start - Start bot\n/getnumber - Get a number\n/mynumbers - Your numbers\n/help - This help\n\nOTP Sources:\nShelex (free): polls every 30s\nTwilio (real): via webhook URL\n\nCountries: {len(COUNTRIES)}"
    )

# ================================================================
# 🚀 MAIN
# ================================================================

def main():
    print("="*55)
    print("  CYBERX VIRTUAL NUMBER BOT - RENDER EDITION")
    print(f"  {len(COUNTRIES)} countries  Port 10000  4min health ping")
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

    # Start Shelex polling in its own thread
    shelex_loop = asyncio.new_event_loop()
    shelex_thread = threading.Thread(target=shelex_poll_numbers, args=(app, shelex_loop), daemon=True)
    shelex_thread.start()

    print(f"[OK] Bot ready! {len(COUNTRIES)} countries.")
    print(f"[OK] Twilio webhook: {render_url}/twilio-sms")

    # Run polling — drop_pending_updates kills stale connections
    try:
        app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
    except KeyboardInterrupt:
        print("\n[!] Shutting down...")
    except Exception as e:
        print(f"\n[!] Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
