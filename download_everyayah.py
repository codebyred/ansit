import os
import json
import time
import requests
from tqdm import tqdm
import logging
from logging.handlers import RotatingFileHandler
import os
import subprocess

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger("everyayah_downloader")
logger.setLevel(logging.DEBUG)

# Formatter
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s"
)

# Main log (rotating)
file_handler = RotatingFileHandler(
    f"{LOG_DIR}/downloader.log",
    maxBytes=5 * 1024 * 1024,  # 5MB
    backupCount=3
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

# Error-only log
error_handler = RotatingFileHandler(
    f"{LOG_DIR}/errors.log",
    maxBytes=2 * 1024 * 1024,
    backupCount=5
)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(formatter)

# Console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(error_handler)
logger.addHandler(console_handler)

BASE_URL = "https://everyayah.com/data"
RECITER = "Alafasy_128kbps"
OUT_DIR = "audio"
DELAY = 0.3  # seconds between requests

with open("surah_ayah_count.json", "r") as f:
    SURAH_AYAH = json.load(f)

def normalize_audio(input_mp3, output_wav):
    subprocess.run([
        "ffmpeg", "-y",
        "-i", input_mp3,
        "-ac", "1",
        "-ar", "16000",
        output_wav
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def download_ayah(surah, ayah):
    filename = f"{surah:03}{ayah:03}.mp3"
    url = f"{BASE_URL}/{RECITER}/{filename}"

    surah_dir = os.path.join(OUT_DIR, RECITER, f"{surah:03}")
    os.makedirs(surah_dir, exist_ok=True)

    mp3_path = os.path.join(surah_dir, filename)
    wav_path = mp3_path.replace(".mp3", ".wav")

    # Skip if already processed
    if os.path.exists(wav_path):
        logger.info(f"SKIP {filename}")
        return

    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            with open(mp3_path, "wb") as f:
                f.write(r.content)

            normalize_audio(mp3_path, wav_path)
            logger.info(f"OK {filename}")
        else:
            logger.error(f"HTTP {r.status_code} | {filename}")

    except Exception as e:
        logger.error(f"EXCEPTION {filename} | {e}")

for surah, ayah_count in SURAH_AYAH.items():
    surah = int(surah)
    print(f"📖 Surah {surah}")
    for ayah in tqdm(range(1, ayah_count + 1)):
        download_ayah(surah, ayah)
        time.sleep(DELAY)

print("✅ Download complete")

