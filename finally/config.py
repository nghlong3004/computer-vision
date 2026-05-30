# -*- coding: utf-8 -*-
"""Central configuration for the posture monitoring system."""

# ── Telegram ──────────────────────────────────────────
# 1. Open Telegram -> @BotFather -> /newbot -> get TOKEN
# 2. Open @userinfobot -> /start -> get CHAT_ID
TELEGRAM_BOT_TOKEN = ""
TELEGRAM_CHAT_ID = ""

# ── Posture thresholds ────────────────────────────────
NECK_ANGLE_THRESHOLD = 25       # Max neck inclination (degrees)
TORSO_ANGLE_THRESHOLD = 10      # Max torso inclination (degrees)
SHOULDER_OFFSET_THRESHOLD = 100  # Max shoulder distance (px)

# ── Alert timing ─────────────────────────────────────
ALERT_TIME = 15                  # Seconds of bad posture before alert
ALERT_SOUND_COOLDOWN = 5         # Seconds between beeps
SCREENSHOT_COOLDOWN = 30         # Seconds between screenshots
TELEGRAM_COOLDOWN = 60           # Seconds between Telegram messages

# ── Display colors (BGR) ─────────────────────────────
COLOR_RED = (50, 50, 255)
COLOR_GREEN = (127, 255, 0)
COLOR_LIGHT_GREEN = (127, 233, 100)
COLOR_YELLOW = (0, 255, 255)
COLOR_PINK = (255, 0, 255)
COLOR_WHITE = (255, 255, 255)

# ── Paths ────────────────────────────────────────────
SCREENSHOT_DIR = "screenshots"
DEFAULT_FPS = 30
