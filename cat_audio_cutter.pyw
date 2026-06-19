import os
import random
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import tkinter as tk
import ctypes
import json
import mimetypes
import uuid
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk

import pyautogui
import pyperclip


APP_TITLE = "Pink Cat Audio Cutter"
UPDATE_REPO_URL = "https://github.com/Shai7net/PinkCatAudioCutter"
UPDATE_BRANCH = "main"
UPDATE_ZIP_URL = f"{UPDATE_REPO_URL}/archive/refs/heads/{UPDATE_BRANCH}.zip"
UPDATE_SOURCE_FILES = [
    ".gitignore",
    "README.md",
    "api_keys.example.json",
    "menu_2.png",
    "cat_audio_cutter.pyw",
    "launch_cat_audio_cutter_bundled.ps1",
    "open_cat_audio_cutter.bat",
    "open_cat_audio_cutter_silent.vbs",
    "download_whisper_model.bat",
    "install_cat_audio_cutter.bat",
    "run_cat_audio_cutter.bat",
    "run_cat_audio_cutter_silent.vbs",
    "build_release.ps1",
    "PinkCatAudioCutter.spec",
]
BG = "#f6e8f0"
PANEL = "#fffafd"
CARD = "#f2ddea"
STRONG_PINK = "#c73b7f"
DARK_PINK = "#8f2f62"
TEXT = "#44213a"
SOFT_PINK = "#ffd7e9"
LIGHT_PANEL = "#fff6fb"
TEAL = "#95d8e6"
ACTION_SHADOW = "#ead9e3"

EMPOWERING_MESSAGES = [
    "את חזקה, חכמה, ומסוגלת לכל מה שבא לך.",
    "הקול שלך חשוב, וראוי שישמעו אותו.",
    "את לא צריכה רשות כדי לזרוח.",
    "העדינות שלך היא כוח, לא חולשה.",
    "כל צעד קטן שלך בונה מציאות חדשה.",
    "את מביאה לעולם יופי, אומץ ולב.",
    "מותר לך לתפוס מקום, בדיוק כמו שאת.",
    "את יכולה להתחיל קטן ועדיין להגיע רחוק.",
]

BITRATE_OPTIONS = ["24k", "32k", "48k", "64k", "96k", "128k", "160k", "192k", "256k", "320k"]
SAMPLE_RATE_OPTIONS = ["22050", "32000", "44100", "48000"]
AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac"}
DEFAULT_OUTPUT_FORMAT = "mp3"
DEFAULT_MP3_BITRATE = "192k"
DEFAULT_MP3_SAMPLE_RATE = "44100"
DEFAULT_OGG_BITRATE = "32k"
DEFAULT_OGG_SAMPLE_RATE = "48000"
DEFAULT_WHATSAPP_BOT_OPTION = "בוט תמלול ישראלי - +972 55-957-1223"
WHATSAPP_BOT_OPTIONS = {
    DEFAULT_WHATSAPP_BOT_OPTION: {
        "phone": "972559571223",
        "label": "+972 55-957-1223",
    },
    "Transcribe Bot - +1 413-600-0076 (100 שניות חינם)": {
        "phone": "14136000076",
        "label": "+1 413-600-0076",
    },
}
WHATSAPP_PRIMARY_FORMAT = "mp3"
WHATSAPP_FALLBACK_FORMAT = "ogg"
TRANSCRIPTION_LOCAL = "local"
TRANSCRIPTION_EXTERNAL = "external"
TRANSCRIPTION_WHATSAPP = "whatsapp"
TRANSCRIPTION_NONE = "none"
LOCAL_MODEL_OPTIONS = {
    "מהיר ומתאים למחשב הזה - Whisper small": "small",
    "קליל מאוד - Whisper base": "base",
    "מדויק יותר לעברית - Ivrit AI large-v3-turbo": "ivrit-ai/whisper-large-v3-turbo-ct2",
}
DEFAULT_LOCAL_MODEL_LABEL = "מהיר ומתאים למחשב הזה - Whisper small"
TRANSCRIPTION_ENGINE_LOCAL = "local_whisper"
TRANSCRIPTION_ENGINE_AZURE_OPENAI = "azure_openai"
TRANSCRIPTION_ENGINE_OPTIONS = {
    "Local Whisper - במחשב": TRANSCRIPTION_ENGINE_LOCAL,
    "Azure Cloud Whisper": TRANSCRIPTION_ENGINE_AZURE_OPENAI,
}
DEFAULT_TRANSCRIPTION_ENGINE_LABEL = "Local Whisper - במחשב"
EXTERNAL_PROVIDER_OPENAI = "openai"
EXTERNAL_PROVIDER_GEMINI = "gemini"
EXTERNAL_PROVIDER_OPENROUTER = "openrouter"
EXTERNAL_PROVIDER_OPTIONS = {
    "OpenAI-compatible text API": EXTERNAL_PROVIDER_OPENAI,
    "Google Gemini": EXTERNAL_PROVIDER_GEMINI,
    "OpenRouter": EXTERNAL_PROVIDER_OPENROUTER,
}
DEFAULT_EXTERNAL_TRANSCRIPTION_URL = "https://api.openai.com/v1/chat/completions"
DEFAULT_EXTERNAL_TRANSCRIPTION_MODEL = "gpt-4o-mini"
DEFAULT_GEMINI_TRANSCRIPTION_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"
DEFAULT_GEMINI_TRANSCRIPTION_MODEL = "gemini-flash-latest"
DEFAULT_OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_OPENROUTER_TEXT_MODEL = "openrouter/auto"
AZURE_OPENAI_CONFIG_KEY = "azure_openai"
DEFAULT_AZURE_OPENAI_DEPLOYMENT_NAME = "whisper"
DEFAULT_AZURE_OPENAI_API_VERSION = "2024-02-01"
EXTERNAL_TRANSCRIPTION_TIMEOUT_SECONDS = 1800
GEMINI_RETRY_DELAYS_SECONDS = [8, 18, 35]
API_KEY_FAILOVER_STATUS_CODES = {401, 402, 403, 429, 500, 502, 503, 504}
GEMINI_API_KEY_FILE_NAME = "gemini_api_key.txt"
GEMINI_API_KEY_PLACEHOLDER = "PASTE_GEMINI_API_KEY_HERE"
API_KEYS_FILE_NAME = "api_keys.json"
SETTINGS_FILE_NAME = "cat_audio_cutter_settings.json"
HISTORY_FILE_NAME = "cat_audio_cutter_history.json"
HISTORY_LIMIT = 25
GEMINI_TEXT_FIX_PROMPT = (
    "אתה מקבל תמלול גולמי בעברית שנוצר ממודל זיהוי דיבור מקומי, ולעיתים יש בו ג'יבריש, "
    "מילים שנשמעו דומה אך זוהו לא נכון, פיסוק חסר ותחביר שבור. "
    "שחזר ממנו תמלול עברי ברור, טבעי ומקצועי ככל האפשר לפי ההקשר. "
    "שמור על המשמעות והדברים שנאמרו, אל תמציא מידע חדש, ואל תוסיף הסברים חיצוניים. "
    "תקן מילים משובשות, תחביר, פיסוק וחלוקה לפסקאות. אם יש ספק, העדף ניסוח שמרני. "
    "החזר רק את התמלול המתוקן, בלי כותרות ובלי הסברים."
)
GEMINI_SUMMARY_PROMPT = (
    "כתוב סיכום מקצועי, ברור ותמציתי של השיחה לפי התמלול הבא. "
    "כלול: נושא השיחה, נקודות מרכזיות, החלטות/בקשות, ומשימות המשך אם יש. "
    "אל תמציא מידע שלא מופיע בתמלול."
)


def get_runtime_base_dir() -> str:
    if getattr(sys, "frozen", False):
        if hasattr(sys, "_MEIPASS"):
            return sys._MEIPASS
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def get_app_config_dir() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def get_gemini_api_key_file_path() -> str:
    return os.path.join(get_app_config_dir(), GEMINI_API_KEY_FILE_NAME)


def get_api_keys_file_path() -> str:
    return os.path.join(get_app_config_dir(), API_KEYS_FILE_NAME)


def get_menu_design_image_path() -> str:
    candidates = [
        os.path.join(get_app_config_dir(), "menu_2.png"),
        os.path.join(get_app_config_dir(), "menu 2.png"),
        os.path.join(os.path.dirname(get_app_config_dir()), "menu 2.png"),
        os.path.join(get_runtime_base_dir(), "menu_2.png"),
    ]
    for candidate in candidates:
        if candidate and os.path.exists(candidate):
            return candidate
    return ""


def get_settings_file_path() -> str:
    return os.path.join(get_app_config_dir(), SETTINGS_FILE_NAME)


def get_history_file_path() -> str:
    return os.path.join(get_app_config_dir(), HISTORY_FILE_NAME)


def load_json_file(path: str, default):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as handle:
                return json.load(handle)
    except (OSError, json.JSONDecodeError):
        return default
    return default


def save_json_file(path: str, payload):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def load_app_settings():
    settings = load_json_file(get_settings_file_path(), {})
    return settings if isinstance(settings, dict) else {}


def save_app_settings(settings):
    save_json_file(get_settings_file_path(), settings)


def load_transcription_history():
    records = load_json_file(get_history_file_path(), [])
    return records if isinstance(records, list) else []


def save_transcription_history(records):
    save_json_file(get_history_file_path(), records[:HISTORY_LIMIT])


def parse_api_key_lines(raw_text: str):
    keys = []
    seen = set()
    normalized = (raw_text or "").replace(",", "\n").replace(";", "\n")
    for line in normalized.splitlines():
        value = line.strip()
        if not value or value.startswith("#"):
            continue
        if value not in seen:
            seen.add(value)
            keys.append(value)
    return keys


def normalize_azure_openai_config(record):
    if not isinstance(record, dict):
        return None

    api_key = str(record.get("api_key", "")).strip()
    azure_endpoint = str(record.get("azure_endpoint", "")).strip().rstrip("/")
    deployment_name = str(record.get("deployment_name", "") or DEFAULT_AZURE_OPENAI_DEPLOYMENT_NAME).strip()
    api_version = str(record.get("api_version", "") or DEFAULT_AZURE_OPENAI_API_VERSION).strip()
    if not api_key or not azure_endpoint:
        return None

    return {
        "api_key": api_key,
        "azure_endpoint": azure_endpoint,
        "deployment_name": deployment_name or DEFAULT_AZURE_OPENAI_DEPLOYMENT_NAME,
        "api_version": api_version or DEFAULT_AZURE_OPENAI_API_VERSION,
    }


def normalize_azure_openai_configs(value):
    if isinstance(value, dict):
        values = [value]
    elif isinstance(value, list):
        values = value
    else:
        values = []

    configs = []
    seen = set()
    for item in values:
        config = normalize_azure_openai_config(item)
        if not config:
            continue
        identity = (
            config["api_key"],
            config["azure_endpoint"],
            config["deployment_name"],
            config["api_version"],
        )
        if identity in seen:
            continue
        seen.add(identity)
        configs.append(config)
    return configs


def load_api_key_store():
    store = load_json_file(get_api_keys_file_path(), {})
    if not isinstance(store, dict):
        return {}

    normalized = {}
    for provider, value in store.items():
        provider_name = str(provider).strip()
        if not provider_name:
            continue
        if provider_name == AZURE_OPENAI_CONFIG_KEY:
            normalized[provider_name] = normalize_azure_openai_configs(value)
            continue
        if isinstance(value, list):
            keys = parse_api_key_lines("\n".join(str(item) for item in value))
        elif isinstance(value, str):
            keys = parse_api_key_lines(value)
        else:
            keys = []
        normalized[provider_name] = keys
    return normalized


def save_api_key_store(store):
    normalized = {}
    for provider, keys in (store or {}).items():
        provider_name = str(provider).strip()
        if provider_name:
            if provider_name == AZURE_OPENAI_CONFIG_KEY:
                normalized[provider_name] = normalize_azure_openai_configs(keys)
            else:
                normalized[provider_name] = parse_api_key_lines("\n".join(keys or []))
    save_json_file(get_api_keys_file_path(), normalized)


def read_api_keys_for_provider(provider: str):
    provider = (provider or "").strip()
    if provider == AZURE_OPENAI_CONFIG_KEY:
        return []
    store = load_api_key_store()
    keys = store.get(provider, [])
    if provider == EXTERNAL_PROVIDER_GEMINI:
        legacy_key = read_gemini_api_key_from_file()
        if legacy_key and legacy_key not in keys:
            keys = [legacy_key, *keys]
    return keys


def read_azure_openai_configs():
    store = load_api_key_store()
    return normalize_azure_openai_configs(store.get(AZURE_OPENAI_CONFIG_KEY, []))


def build_azure_openai_configs_from_values(api_keys, azure_endpoint: str, deployment_name: str, api_version: str):
    return normalize_azure_openai_configs(
        [
            {
                "api_key": api_key,
                "azure_endpoint": azure_endpoint,
                "deployment_name": deployment_name,
                "api_version": api_version,
            }
            for api_key in parse_api_key_lines("\n".join(api_keys or []))
        ]
    )


def write_azure_openai_configs(configs):
    store = load_api_key_store()
    store[AZURE_OPENAI_CONFIG_KEY] = normalize_azure_openai_configs(configs)
    save_api_key_store(store)


def write_api_keys_for_provider(provider: str, keys):
    provider = (provider or "").strip()
    if not provider or provider == AZURE_OPENAI_CONFIG_KEY:
        return
    store = load_api_key_store()
    store[provider] = parse_api_key_lines("\n".join(keys or []))
    save_api_key_store(store)


def ensure_api_keys_file_exists() -> str:
    key_path = get_api_keys_file_path()
    if not os.path.exists(key_path):
        save_api_key_store(
            {
                EXTERNAL_PROVIDER_OPENAI: [],
                EXTERNAL_PROVIDER_GEMINI: [],
                EXTERNAL_PROVIDER_OPENROUTER: [],
                AZURE_OPENAI_CONFIG_KEY: [],
            }
        )
    return key_path


def ensure_gemini_api_key_file_exists() -> str:
    key_path = get_gemini_api_key_file_path()
    if not os.path.exists(key_path):
        with open(key_path, "w", encoding="utf-8") as handle:
            handle.write(
                "# Put your Gemini API key on the next line.\n"
                "# The app ignores lines that start with #.\n"
                f"{GEMINI_API_KEY_PLACEHOLDER}\n"
            )
    return key_path


def read_gemini_api_key_from_file() -> str:
    key_path = ensure_gemini_api_key_file_exists()
    try:
        with open(key_path, "r", encoding="utf-8") as handle:
            for line in handle:
                value = line.strip()
                if not value or value.startswith("#") or value == GEMINI_API_KEY_PLACEHOLDER:
                    continue
                return value
    except OSError:
        return ""
    return ""


def resolve_runtime_binary(name: str) -> str:
    base_dir = get_runtime_base_dir()
    candidates = [
        os.path.join(base_dir, name),
        os.path.join(base_dir, "_internal", name),
        os.path.join(base_dir, "bin", name),
    ]
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(sys.executable)
        candidates.extend(
            [
                os.path.join(exe_dir, name),
                os.path.join(exe_dir, "_internal", name),
                os.path.join(exe_dir, "bin", name),
            ]
        )

    for candidate in candidates:
        if candidate and os.path.exists(candidate):
            return candidate
    return name


def resolve_bundled_certifi_path() -> str:
    config_dir = get_app_config_dir()
    runtime_home = os.environ.get("PYTHONHOME", "")
    parent_dir = os.path.dirname(config_dir)
    candidates = [
        os.path.join(runtime_home, "certifi", "cacert.pem") if runtime_home else "",
        os.path.join(get_runtime_base_dir(), "certifi", "cacert.pem"),
        os.path.join(get_runtime_base_dir(), "_internal", "certifi", "cacert.pem"),
        os.path.join(config_dir, "dist", "PinkCatAudioCutter", "_internal", "certifi", "cacert.pem"),
        os.path.join(config_dir, "release", "PinkCatAudioCutter", "_internal", "certifi", "cacert.pem"),
        os.path.join(config_dir, "PinkCatAudioCutter", "_internal", "certifi", "cacert.pem"),
        os.path.join(parent_dir, "PinkCatAudioCutter", "_internal", "certifi", "cacert.pem"),
        os.path.join(os.path.dirname(sys.executable), "certifi", "cacert.pem") if getattr(sys, "frozen", False) else "",
        os.path.join(os.path.dirname(sys.executable), "_internal", "certifi", "cacert.pem") if getattr(sys, "frozen", False) else "",
    ]
    for candidate in candidates:
        if candidate and os.path.exists(candidate):
            return candidate
    return ""


def configure_certifi_for_bundled_runtime():
    cacert_path = resolve_bundled_certifi_path()
    if not cacert_path:
        return
    os.environ.setdefault("SSL_CERT_FILE", cacert_path)
    os.environ.setdefault("REQUESTS_CA_BUNDLE", cacert_path)
    try:
        import certifi
        import certifi.core

        certifi.where = lambda: cacert_path
        certifi.core.where = lambda: cacert_path
    except Exception:
        pass


def configure_huggingface_cache():
    local_cache_root = os.path.join(get_app_config_dir(), "model_cache", "huggingface")
    local_hub_cache = os.path.join(local_cache_root, "hub")

    def cache_path_is_usable(path: str) -> bool:
        if not path:
            return False
        drive, _tail = os.path.splitdrive(os.path.abspath(path))
        if drive and not os.path.exists(drive + os.sep):
            return False
        try:
            os.makedirs(path, exist_ok=True)
            return os.path.isdir(path)
        except OSError:
            return False

    current_home = os.environ.get("HF_HOME", "")
    current_hub = os.environ.get("HF_HUB_CACHE", "")
    if cache_path_is_usable(current_home or current_hub):
        return

    os.makedirs(local_hub_cache, exist_ok=True)
    os.environ["HF_HOME"] = local_cache_root
    os.environ["HF_HUB_CACHE"] = local_hub_cache


def run_command(command, cwd=None):
    if command and command[0] in {"ffmpeg", "ffprobe", "ffmpeg.exe", "ffprobe.exe"}:
        command = [resolve_runtime_binary(command[0]), *command[1:]]
    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=cwd,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Unknown command error")
    return result.stdout.strip()


def get_audio_duration_seconds(audio_path: str) -> float:
    output = run_command(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            audio_path,
        ]
    )
    return float(output)


def parse_time_value(raw_value: str) -> float:
    value = raw_value.strip()
    if not value:
        raise ValueError("ערך זמן ריק.")

    parts = value.split(":")
    try:
        if len(parts) == 1:
            return float(parts[0])
        if len(parts) == 2:
            minutes = int(parts[0])
            seconds = float(parts[1])
            return minutes * 60 + seconds
        if len(parts) == 3:
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = float(parts[2])
            return hours * 3600 + minutes * 60 + seconds
    except ValueError as error:
        raise ValueError(f"זמן לא תקין: {raw_value}") from error

    raise ValueError(f"זמן לא תקין: {raw_value}")


def format_seconds(seconds: float) -> str:
    total_seconds = max(0, seconds)
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    secs = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"


def format_player_time(milliseconds: int) -> str:
    total_seconds = max(0, int(milliseconds or 0) // 1000)
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes:02d}:{seconds:02d}"


def parse_ranges_input(ranges_text: str):
    ranges = []
    normalized = ranges_text.replace(",", "\n").replace(";", "\n")
    for line in normalized.splitlines():
        chunk = line.strip()
        if not chunk:
            continue
        if "-" not in chunk:
            raise ValueError("בחיתוך לפי זמנים צריך לכתוב טווחים בפורמט 00:00-00:30.")
        start_raw, end_raw = chunk.split("-", 1)
        start_seconds = parse_time_value(start_raw)
        end_seconds = parse_time_value(end_raw)
        if end_seconds <= start_seconds:
            raise ValueError(f"בטווח {chunk} זמן הסיום חייב להיות אחרי זמן ההתחלה.")
        ranges.append((start_seconds, end_seconds))

    if not ranges:
        raise ValueError("לא הוזנו טווחי זמן לחיתוך.")

    return ranges


def build_ffmpeg_output_args(output_format: str, bitrate: str, sample_rate: str):
    if output_format == "mp3":
        return ["-acodec", "libmp3lame", "-b:a", bitrate, "-ar", sample_rate]
    if output_format == "ogg":
        return [
            "-acodec",
            "libopus",
            "-b:a",
            bitrate,
            "-vbr",
            "on",
            "-application",
            "voip",
            "-ac",
            "1",
            "-ar",
            sample_rate,
        ]
    if output_format == "wav":
        return ["-acodec", "pcm_s16le", "-ar", sample_rate]
    raise ValueError("פורמט פלט לא נתמך.")


def get_whatsapp_bot_config(option_label: str):
    return WHATSAPP_BOT_OPTIONS.get(option_label, WHATSAPP_BOT_OPTIONS[DEFAULT_WHATSAPP_BOT_OPTION])


def prepare_whatsapp_audio_files(file_paths, temp_dir: str, output_format: str):
    if output_format not in {WHATSAPP_PRIMARY_FORMAT, WHATSAPP_FALLBACK_FORMAT}:
        raise ValueError("פורמט WhatsApp לא נתמך.")

    valid_paths = [path for path in file_paths if path and os.path.isfile(path)]
    if not valid_paths:
        raise FileNotFoundError("לא נמצאו קבצי שמע תקינים לשליחה ל-WhatsApp.")

    prepared_dir = os.path.join(temp_dir, f"whatsapp_{output_format}")
    os.makedirs(prepared_dir, exist_ok=True)
    prepared_paths = []
    for index, source_path in enumerate(valid_paths, start=1):
        target_path = os.path.join(prepared_dir, f"segment_{index:02d}.{output_format}")
        if output_format == WHATSAPP_PRIMARY_FORMAT:
            codec_args = ["-acodec", "libmp3lame", "-b:a", "96k", "-ac", "1", "-ar", "44100"]
        else:
            codec_args = [
                "-acodec",
                "libopus",
                "-b:a",
                "32k",
                "-vbr",
                "on",
                "-application",
                "voip",
                "-ac",
                "1",
                "-ar",
                "48000",
            ]
        run_command(
            [
                "ffmpeg",
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-i",
                source_path,
                "-vn",
                *codec_args,
                target_path,
            ]
        )
        if not os.path.exists(target_path) or os.path.getsize(target_path) == 0:
            raise RuntimeError(f"לא הצלחתי להכין את מקטע {index} לשליחה ל-WhatsApp.")
        prepared_paths.append(target_path)
    return prepared_paths


def build_segment_plan(mode: str, audio_path: str, segments_count: int, ranges_text: str):
    duration = get_audio_duration_seconds(audio_path)
    if duration <= 0:
        raise RuntimeError("לא הצלחתי לקרוא את אורך קובץ הקול.")

    if mode == "count":
        if segments_count < 2:
            raise ValueError("כדי לחתוך לפי מספר צריך לפחות 2 מקטעים.")
        segment_length = duration / segments_count
        ranges = []
        for index in range(segments_count):
            start = index * segment_length
            end = duration if index == segments_count - 1 else min(duration, (index + 1) * segment_length)
            ranges.append((start, end))
        return ranges

    ranges = parse_ranges_input(ranges_text)
    for start, end in ranges:
        if end > duration + 0.05:
            raise ValueError("אחד מטווחי הזמן חורג מאורך קובץ הקול.")
    return ranges


def split_audio_file(audio_path: str, segment_plan, temp_dir: str, output_format: str, bitrate: str, sample_rate: str, progress_callback):
    output_paths = []
    total = len(segment_plan)
    ffmpeg_output_args = build_ffmpeg_output_args(output_format, bitrate, sample_rate)

    for index, (start, end) in enumerate(segment_plan, start=1):
        segment_duration = end - start
        if segment_duration <= 0:
            raise RuntimeError(f"אורך לא תקין למקטע {index}.")
        output_name = f"segment_{index:02d}.{output_format}"
        output_path = os.path.join(temp_dir, output_name)
        command = [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-ss",
            format_seconds(start),
            "-i",
            audio_path,
            "-t",
            format_seconds(segment_duration),
            "-vn",
            *ffmpeg_output_args,
            output_path,
        ]
        run_command(command)
        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            raise RuntimeError(f"החיתוך של מקטע {index} לא הושלם ולא נוצר קובץ תקין.")
        output_paths.append(output_path)
        progress_callback(index, total)

    if not output_paths:
        raise RuntimeError("לא נוצרו קבצי שמע אחרי החיתוך.")

    return output_paths


def export_full_audio_file(audio_path: str, temp_dir: str, output_format: str, bitrate: str, sample_rate: str, progress_callback):
    output_name = f"segment_01.{output_format}"
    output_path = os.path.join(temp_dir, output_name)
    command = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        audio_path,
        "-vn",
        *build_ffmpeg_output_args(output_format, bitrate, sample_rate),
        output_path,
    ]
    run_command(command)
    if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
        raise RuntimeError("לא נוצר קובץ שמע תקין לתמלול/שמירה ללא חיתוך.")
    progress_callback(1, 1)
    return [output_path]


def copy_results_to_folder(source_files, target_dir: str):
    os.makedirs(target_dir, exist_ok=True)
    copied = []
    for path in source_files:
        destination = os.path.join(target_dir, os.path.basename(path))
        shutil.copy2(path, destination)
        copied.append(destination)
    return copied


def is_git_checkout(project_root: str) -> bool:
    return os.path.isdir(os.path.join(project_root, ".git"))


def update_from_git_checkout(project_root: str, progress_callback):
    progress_callback("בודקת עדכונים דרך Git...")
    status = run_command(["git", "status", "--porcelain"], cwd=project_root)
    if status.strip():
        raise RuntimeError(
            "יש שינויים מקומיים בתיקיית התוכנה, ולכן העדכון נעצר כדי לא לדרוס עבודה קיימת.\n"
            "שמרי/גבי את השינויים ואז נסי שוב."
        )

    progress_callback("מורידה מידע עדכני מ-GitHub...")
    run_command(["git", "fetch", "origin", UPDATE_BRANCH], cwd=project_root)
    local_revision = run_command(["git", "rev-parse", "HEAD"], cwd=project_root).strip()
    remote_revision = run_command(["git", "rev-parse", f"origin/{UPDATE_BRANCH}"], cwd=project_root).strip()
    if local_revision and local_revision == remote_revision:
        return "כבר מותקנת הגרסה האחרונה מ-GitHub."

    progress_callback("מעדכנת את קבצי התוכנה...")
    run_command(["git", "pull", "--ff-only", "origin", UPDATE_BRANCH], cwd=project_root)
    return "העדכון הושלם. כדי להשתמש בגרסה החדשה צריך להפעיל את התוכנה מחדש."


def safe_copy_update_file(source_root: str, project_root: str, relative_path: str):
    source_path = os.path.abspath(os.path.join(source_root, relative_path))
    target_path = os.path.abspath(os.path.join(project_root, relative_path))
    project_root_abs = os.path.abspath(project_root)
    if os.path.commonpath([project_root_abs, target_path]) != project_root_abs:
        raise RuntimeError(f"נתיב עדכון לא בטוח: {relative_path}")
    if not os.path.exists(source_path):
        return False
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    shutil.copy2(source_path, target_path)
    return True


def update_from_github_zip(project_root: str, progress_callback):
    progress_callback("מורידה עדכון מ-GitHub...")
    with tempfile.TemporaryDirectory(prefix="cat_audio_update_") as temp_dir:
        archive_path = os.path.join(temp_dir, "source.zip")
        request = urllib.request.Request(
            UPDATE_ZIP_URL,
            headers={
                "User-Agent": APP_TITLE,
                "Accept": "application/zip, application/octet-stream",
            },
        )
        with urllib.request.urlopen(request, timeout=EXTERNAL_TRANSCRIPTION_TIMEOUT_SECONDS) as response:
            with open(archive_path, "wb") as handle:
                shutil.copyfileobj(response, handle)

        progress_callback("פותחת את חבילת העדכון...")
        extract_dir = os.path.join(temp_dir, "extract")
        with zipfile.ZipFile(archive_path) as archive:
            extract_root = os.path.abspath(extract_dir)
            for member in archive.infolist():
                target_path = os.path.abspath(os.path.join(extract_dir, member.filename))
                if os.path.commonpath([extract_root, target_path]) != extract_root:
                    raise RuntimeError("חבילת העדכון מכילה נתיב לא בטוח ולכן נעצרה.")
            archive.extractall(extract_dir)

        roots = [
            os.path.join(extract_dir, name)
            for name in os.listdir(extract_dir)
            if os.path.isdir(os.path.join(extract_dir, name))
        ]
        if not roots:
            raise RuntimeError("לא נמצא תוכן תקין בחבילת העדכון.")
        source_root = roots[0]

        progress_callback("מעדכנת קבצי מקור בלי לגעת בהגדרות ובמפתחות...")
        copied_count = 0
        for relative_path in UPDATE_SOURCE_FILES:
            if safe_copy_update_file(source_root, project_root, relative_path):
                copied_count += 1

        if copied_count == 0:
            raise RuntimeError("חבילת העדכון לא הכילה קבצים מוכרים לעדכון.")

    return f"העדכון הושלם ({copied_count} קבצים עודכנו). כדי להשתמש בגרסה החדשה צריך להפעיל את התוכנה מחדש."


def update_application_from_github(progress_callback):
    project_root = get_app_config_dir()
    if is_git_checkout(project_root):
        return update_from_git_checkout(project_root, progress_callback)
    return update_from_github_zip(project_root, progress_callback)


def get_local_model_name(model_label: str) -> str:
    return LOCAL_MODEL_OPTIONS.get(model_label, model_label.strip() or LOCAL_MODEL_OPTIONS[DEFAULT_LOCAL_MODEL_LABEL])


def get_transcription_engine_value(engine_label: str) -> str:
    return TRANSCRIPTION_ENGINE_OPTIONS.get(engine_label, (engine_label or "").strip() or TRANSCRIPTION_ENGINE_LOCAL)


def get_transcription_engine_label(engine_value: str) -> str:
    for label, value in TRANSCRIPTION_ENGINE_OPTIONS.items():
        if value == engine_value:
            return label
    return DEFAULT_TRANSCRIPTION_ENGINE_LABEL


def write_transcript_files(audio_path: str, output_dir: str, text: str):
    clean_text = (text or "").strip()
    if not clean_text:
        clean_text = "(לא זוהה דיבור ברור במקטע הזה.)"

    transcript_path = os.path.join(output_dir, f"{Path(audio_path).stem}_transcript.txt")
    with open(transcript_path, "w", encoding="utf-8") as handle:
        handle.write(clean_text + "\n")
    return transcript_path, clean_text


def write_combined_transcript(output_dir: str, sections):
    combined_path = os.path.join(output_dir, "transcript_all_segments.txt")
    with open(combined_path, "w", encoding="utf-8") as handle:
        handle.write("\n\n".join(sections).strip() + "\n")
    return combined_path


def format_download_size(byte_count):
    if byte_count is None:
        return ""
    value = float(byte_count)
    for unit in ("B", "KB", "MB", "GB"):
        if value < 1024 or unit == "GB":
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} {unit}"
        value /= 1024
    return f"{value:.1f} GB"


def resolve_faster_whisper_repo_id(model_name: str):
    from faster_whisper import utils as faster_whisper_utils

    if "/" in model_name:
        return model_name
    model_map = getattr(faster_whisper_utils, "_MODELS", {})
    repo_id = model_map.get(model_name)
    if not repo_id:
        raise ValueError(f"מודל מקומי לא מוכר: {model_name}")
    return repo_id


def ensure_faster_whisper_model(model_name: str, progress_callback):
    configure_certifi_for_bundled_runtime()
    configure_huggingface_cache()

    import huggingface_hub
    from tqdm.auto import tqdm

    repo_id = resolve_faster_whisper_repo_id(model_name)
    allow_patterns = [
        "config.json",
        "preprocessor_config.json",
        "model.bin",
        "tokenizer.json",
        "vocabulary.*",
    ]

    class QuietWriter:
        def write(self, _text):
            return None

        def flush(self):
            return None

        def isatty(self):
            return False

    class DownloadProgress(tqdm):
        def __init__(self, *args, **kwargs):
            kwargs["file"] = QuietWriter()
            kwargs["mininterval"] = 0.4
            super().__init__(*args, **kwargs)
            self._last_gui_update = 0
            progress_callback(self._build_label(), self._percent())

        def _percent(self):
            if not self.total:
                return None
            return max(0, min(100, (self.n / self.total) * 100))

        def _build_label(self):
            desc = (getattr(self, "desc", "") or "מודל").strip()
            unit = str(getattr(self, "unit", "") or "").lower()
            is_byte_progress = unit.startswith("b") or (self.total and self.total > 1024 * 1024)
            if self.total:
                percent = self._percent()
                if is_byte_progress:
                    return (
                        f"מורידה {desc}: {format_download_size(self.n)} מתוך "
                        f"{format_download_size(self.total)} ({percent:.0f}%)"
                    )
                return f"מורידה {desc}: {int(self.n)} מתוך {int(self.total)} ({percent:.0f}%)"
            if is_byte_progress:
                return f"מורידה {desc}: {format_download_size(self.n)}"
            return f"מורידה {desc}..."

        def update(self, n=1):
            result = super().update(n)
            now = time.time()
            if now - self._last_gui_update >= 0.4:
                self._last_gui_update = now
                progress_callback(self._build_label(), self._percent())
            return result

        def close(self):
            if self.n:
                progress_callback(self._build_label(), self._percent())
            return super().close()

    progress_callback("בודקת אם מודל התמלול כבר קיים במחשב...", 0)
    try:
        model_path = huggingface_hub.snapshot_download(
            repo_id,
            local_files_only=True,
            allow_patterns=allow_patterns,
            tqdm_class=DownloadProgress,
        )
        progress_callback("מודל התמלול כבר קיים במחשב. טוענת אותו עכשיו...", 100)
        return model_path
    except Exception:
        progress_callback("המודל לא נמצא במחשב. מתחילה הורדה מהאינטרנט...", 0)

    try:
        model_path = huggingface_hub.snapshot_download(
            repo_id,
            local_files_only=False,
            allow_patterns=allow_patterns,
            tqdm_class=DownloadProgress,
        )
        progress_callback("הורדת המודל הסתיימה. טוענת אותו לזיכרון...", 100)
        return model_path
    except Exception as error:
        raise RuntimeError(
            "לא הצלחתי להוריד את מודל התמלול מהאינטרנט.\n"
            "בדקי שיש חיבור אינטרנט פתוח, ואז נסי שוב."
        ) from error


def error_details(error: Exception) -> str:
    return str(error).strip() or repr(error)


class ExternalApiBusyError(RuntimeError):
    pass


class ExternalApiHttpError(RuntimeError):
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code


def get_api_error_status_code(error: Exception):
    for attr in ("status_code", "status", "code"):
        value = getattr(error, attr, None)
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)

    response = getattr(error, "response", None)
    for attr in ("status_code", "status"):
        value = getattr(response, attr, None)
        if isinstance(value, int):
            return value
    return None


def redact_secrets_from_message(message: str, secrets):
    redacted = str(message or "")
    for secret in secrets or []:
        secret = str(secret or "").strip()
        if secret and len(secret) >= 8:
            redacted = redacted.replace(secret, "***")
    return redacted


def record_api_state_metric(provider: str, state: str, error: Exception = None, config_index: int = None):
    try:
        from ddtrace import tracer
    except Exception:
        return

    try:
        span = tracer.current_span()
        if not span:
            return
        span.set_tag("pinkcat.api.provider", provider)
        span.set_tag("pinkcat.api.state", state)
        if config_index is not None:
            span.set_tag("pinkcat.api.config_index", config_index)
        if error is not None:
            span.set_tag("pinkcat.api.error_type", type(error).__name__)
            span.set_tag("pinkcat.api.error", True)
    except Exception:
        return


def should_try_next_api_key(error: Exception) -> bool:
    if isinstance(error, ExternalApiBusyError):
        return True
    if isinstance(error, ExternalApiHttpError):
        return error.status_code in API_KEY_FAILOVER_STATUS_CODES
    return False


def call_with_api_key_pool(api_keys, service_label: str, call_factory):
    keys = parse_api_key_lines("\n".join(api_keys or []))
    if not keys:
        keys = [""]

    last_error = None
    for index, api_key in enumerate(keys, start=1):
        try:
            return call_factory(api_key)
        except Exception as error:
            last_error = error
            if index < len(keys) and should_try_next_api_key(error):
                continue
            raise

    raise RuntimeError(f"כל מפתחות ה-API עבור {service_label} נכשלו.") from last_error


def call_with_azure_openai_config_pool(configs, call_factory):
    azure_configs = normalize_azure_openai_configs(configs)
    if not azure_configs:
        raise RuntimeError("לא נמצאו הגדרות Azure OpenAI תקינות בקובץ api_keys.json.")

    last_error = None
    for index, config in enumerate(azure_configs, start=1):
        try:
            record_api_state_metric("azure_openai_whisper", "attempt", config_index=index)
            result = call_factory(config)
            record_api_state_metric("azure_openai_whisper", "success", config_index=index)
            return result
        except Exception as error:
            last_error = error
            record_api_state_metric("azure_openai_whisper", "error", error=error, config_index=index)
            if index < len(azure_configs) and should_try_next_api_key(error):
                continue
            raise

    raise RuntimeError("כל הגדרות Azure OpenAI Whisper נכשלו.") from last_error


def prepare_audio_for_local_transcription(audio_path: str, working_dir: str, index: int):
    normalized_dir = os.path.join(working_dir, "transcription_wav")
    os.makedirs(normalized_dir, exist_ok=True)
    wav_path = os.path.join(normalized_dir, f"transcribe_{index:02d}.wav")
    run_command(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            audio_path,
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-f",
            "wav",
            wav_path,
        ]
    )
    if not os.path.exists(wav_path) or os.path.getsize(wav_path) == 0:
        raise RuntimeError("לא נוצר קובץ WAV זמני תקין לתמלול.")
    return wav_path


def transcribe_audio_files_locally(
    audio_paths,
    output_dir: str,
    model_name: str,
    progress_callback,
    model_progress_callback,
    working_dir: str,
):
    try:
        from faster_whisper import WhisperModel
    except ImportError as error:
        raise RuntimeError("מודול התמלול המקומי לא נמצא בחבילת ההפעלה של הכלי.") from error

    try:
        model_path = ensure_faster_whisper_model(model_name, model_progress_callback)
        model_progress_callback("טוענת את מודל התמלול לזיכרון...", 100)
        model = WhisperModel(model_path, device="cpu", compute_type="int8")
    except Exception as error:
        raise RuntimeError(
            "לא הצלחתי לטעון את מודל התמלול המקומי.\n"
            "אם זו ההפעלה הראשונה, ודאי שהורדת המודל הסתיימה ושיש חיבור אינטרנט.\n\n"
            f"פרטים טכניים:\n{error_details(error)}"
        ) from error

    transcript_files = []
    combined_sections = []
    total = len(audio_paths)

    for index, audio_path in enumerate(audio_paths, start=1):
        try:
            progress_callback(index, total, f"מכינה מקטע {index}/{total} לתמלול")
            transcription_source = prepare_audio_for_local_transcription(audio_path, working_dir, index)
            progress_callback(index, total, f"מתמללת מקטע {index}/{total}")
            segments, _info = model.transcribe(
                transcription_source,
                language="he",
                task="transcribe",
                beam_size=5,
                vad_filter=False,
                condition_on_previous_text=False,
            )
            text = " ".join(segment.text.strip() for segment in segments if segment.text.strip())
        except Exception as error:
            raise RuntimeError(
                f"לא הצלחתי לתמלל את מקטע {index}: {os.path.basename(audio_path)}\n\n"
                f"פרטים טכניים:\n{error_details(error)}"
            ) from error

        transcript_path, clean_text = write_transcript_files(audio_path, output_dir, text)
        transcript_files.append(transcript_path)
        combined_sections.append(f"--- {os.path.basename(audio_path)} ---\n{clean_text}")

    combined_path = write_combined_transcript(output_dir, combined_sections)
    transcript_files.append(combined_path)
    return transcript_files, "\n\n".join(combined_sections), combined_path


def encode_multipart_form(fields, file_field_name: str, file_path: str):
    boundary = uuid.uuid4().hex
    body = bytearray()

    for name, value in fields.items():
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("utf-8"))
        body.extend(str(value).encode("utf-8"))
        body.extend(b"\r\n")

    filename = os.path.basename(file_path)
    content_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
    body.extend(f"--{boundary}\r\n".encode("utf-8"))
    body.extend(
        (
            f'Content-Disposition: form-data; name="{file_field_name}"; filename="{filename}"\r\n'
            f"Content-Type: {content_type}\r\n\r\n"
        ).encode("utf-8")
    )
    with open(file_path, "rb") as handle:
        body.extend(handle.read())
    body.extend(b"\r\n")
    body.extend(f"--{boundary}--\r\n".encode("utf-8"))

    return bytes(body), f"multipart/form-data; boundary={boundary}"


def build_azure_whisper_transcription_url(config_dict):
    config = normalize_azure_openai_config(config_dict)
    if not config:
        raise RuntimeError("הגדרות Azure OpenAI אינן תקינות.")

    endpoint = config["azure_endpoint"].rstrip("/")
    deployment = urllib.parse.quote(config["deployment_name"], safe="")
    api_version = urllib.parse.quote(config["api_version"], safe="-_.")
    return f"{endpoint}/openai/deployments/{deployment}/audio/transcriptions?api-version={api_version}"


def transcribe_via_azure_whisper_http(audio_file_path: str, config_dict):
    config = normalize_azure_openai_config(config_dict)
    if not config:
        raise RuntimeError("הגדרות Azure OpenAI אינן תקינות.")

    body, content_type = encode_multipart_form(
        {
            "language": "he",
        },
        "file",
        audio_file_path,
    )
    headers = {
        "Content-Type": content_type,
        "Accept": "application/json, text/plain",
        "api-key": config["api_key"],
    }
    request = urllib.request.Request(
        build_azure_whisper_transcription_url(config),
        data=body,
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=EXTERNAL_TRANSCRIPTION_TIMEOUT_SECONDS) as response:
            return extract_transcript_text(response.read().decode("utf-8", errors="replace"))
    except urllib.error.HTTPError as error:
        details = error.read().decode("utf-8", errors="replace")
        clean_details = redact_secrets_from_message(details[:700], [config["api_key"]])
        if error.code in API_KEY_FAILOVER_STATUS_CODES:
            raise ExternalApiBusyError(f"Azure OpenAI Whisper לא זמין כרגע או נחסם. קוד {error.code}: {clean_details}") from error
        raise ExternalApiHttpError(f"Azure OpenAI Whisper החזיר שגיאה {error.code}: {clean_details}", error.code) from error
    except urllib.error.URLError as error:
        clean_error = redact_secrets_from_message(error, [config["api_key"]])
        raise ExternalApiBusyError(f"לא הצלחתי להתחבר ל-Azure OpenAI Whisper: {clean_error}") from error


def transcribe_via_azure_whisper(audio_file_path: str, config_dict):
    if not os.path.exists(audio_file_path):
        raise FileNotFoundError(f"Normalized audio segment missing: {audio_file_path}")

    config = normalize_azure_openai_config(config_dict)
    if not config:
        raise RuntimeError("הגדרות Azure OpenAI אינן תקינות.")

    configure_certifi_for_bundled_runtime()
    try:
        from openai import AzureOpenAI
    except ImportError:
        return transcribe_via_azure_whisper_http(audio_file_path, config)

    try:
        client = AzureOpenAI(
            api_key=config["api_key"],
            api_version=config["api_version"],
            azure_endpoint=config["azure_endpoint"],
        )

        with open(audio_file_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model=config["deployment_name"],
                file=audio_file,
                language="he",
            )

        text = getattr(response, "text", None)
        if isinstance(text, str):
            return text.strip()
        if isinstance(response, dict):
            return extract_transcript_text(json.dumps(response, ensure_ascii=False))
        return extract_transcript_text(str(response))

    except Exception as error:
        status_code = get_api_error_status_code(error)
        clean_error = redact_secrets_from_message(error_details(error), [config["api_key"]])
        print(f"[Azure Whisper Error] API call failed: {clean_error}")
        if status_code is None or status_code in API_KEY_FAILOVER_STATUS_CODES:
            raise ExternalApiBusyError(f"Azure API error: {clean_error}") from error
        raise ExternalApiHttpError(f"Azure API error {status_code}: {clean_error}", status_code) from error


def transcribe_audio_files_with_azure_whisper(
    audio_paths,
    output_dir: str,
    azure_configs,
    progress_callback,
    working_dir: str,
):
    transcript_files = []
    combined_sections = []
    total = len(audio_paths)

    for index, audio_path in enumerate(audio_paths, start=1):
        try:
            progress_callback(index, total, f"מכינה מקטע {index}/{total} ל-Azure Whisper")
            transcription_source = prepare_audio_for_local_transcription(audio_path, working_dir, index)
            progress_callback(index, total, f"מתמללת מקטע {index}/{total} ב-Azure Whisper")
            text = call_with_azure_openai_config_pool(
                azure_configs,
                lambda config: transcribe_via_azure_whisper(transcription_source, config),
            )
        except Exception as error:
            raise RuntimeError(
                f"לא הצלחתי לתמלל את מקטע {index} דרך Azure Whisper: {os.path.basename(audio_path)}\n\n"
                f"פרטים טכניים:\n{error_details(error)}"
            ) from error

        transcript_path, clean_text = write_transcript_files(audio_path, output_dir, text)
        transcript_files.append(transcript_path)
        combined_sections.append(f"--- {os.path.basename(audio_path)} ---\n{clean_text}")

    combined_path = write_combined_transcript(output_dir, combined_sections)
    transcript_files.append(combined_path)
    return transcript_files, "\n\n".join(combined_sections), combined_path


def get_external_provider_value(provider_label: str) -> str:
    return EXTERNAL_PROVIDER_OPTIONS.get(provider_label, provider_label.strip() or EXTERNAL_PROVIDER_OPENAI)


def get_external_provider_label(provider_value: str) -> str:
    for label, value in EXTERNAL_PROVIDER_OPTIONS.items():
        if value == provider_value:
            return label
    return "OpenAI / Whisper compatible"


def extract_transcript_text(response_text: str) -> str:
    try:
        payload = json.loads(response_text)
    except json.JSONDecodeError:
        return response_text.strip()

    if isinstance(payload, str):
        return payload.strip()
    if not isinstance(payload, dict):
        return response_text.strip()

    for key in ("text", "transcript", "transcription", "output_text"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    segments = payload.get("segments")
    if isinstance(segments, list):
        text = " ".join(
            item.get("text", "").strip()
            for item in segments
            if isinstance(item, dict) and item.get("text", "").strip()
        )
        if text:
            return text

    data = payload.get("data")
    if isinstance(data, dict):
        nested_text = extract_transcript_text(json.dumps(data, ensure_ascii=False))
        if nested_text:
            return nested_text

    return response_text.strip()


def extract_gemini_transcript_text(response_text: str) -> str:
    try:
        payload = json.loads(response_text)
    except json.JSONDecodeError:
        return response_text.strip()

    candidates = payload.get("candidates") if isinstance(payload, dict) else None
    if isinstance(candidates, list):
        parts_text = []
        for candidate in candidates:
            content = candidate.get("content") if isinstance(candidate, dict) else None
            parts = content.get("parts") if isinstance(content, dict) else None
            if not isinstance(parts, list):
                continue
            for part in parts:
                if isinstance(part, dict) and isinstance(part.get("text"), str):
                    parts_text.append(part["text"].strip())
        text = "\n".join(part for part in parts_text if part).strip()
        if text:
            return text

    return extract_transcript_text(response_text)


def extract_chat_completion_text(response_text: str) -> str:
    try:
        payload = json.loads(response_text)
    except json.JSONDecodeError:
        return response_text.strip()

    choices = payload.get("choices") if isinstance(payload, dict) else None
    if isinstance(choices, list):
        parts_text = []
        for choice in choices:
            message = choice.get("message") if isinstance(choice, dict) else None
            if not isinstance(message, dict):
                continue
            content = message.get("content")
            if isinstance(content, str):
                parts_text.append(content.strip())
            elif isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and isinstance(item.get("text"), str):
                        parts_text.append(item["text"].strip())
        text = "\n".join(part for part in parts_text if part).strip()
        if text:
            return text

    return extract_transcript_text(response_text)


def build_openrouter_chat_payload(prompt_text: str, model_name: str):
    return {
        "model": (model_name or DEFAULT_OPENROUTER_TEXT_MODEL).strip(),
        "messages": [
            {
                "role": "user",
                "content": prompt_text.strip(),
            }
        ],
        "temperature": 0,
    }


def build_gemini_text_fix_payload(transcript_text: str):
    return {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": f"{GEMINI_TEXT_FIX_PROMPT}\n\n--- תמלול לתיקון ---\n{transcript_text.strip()}",
                    }
                ],
            }
        ],
        "generationConfig": {
            "temperature": 0,
        },
    }


def build_gemini_summary_payload(transcript_text: str):
    return {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": f"{GEMINI_SUMMARY_PROMPT}\n\n--- תמלול ---\n{transcript_text.strip()}",
                    }
                ],
            }
        ],
        "generationConfig": {
            "temperature": 0,
        },
    }


def build_gemini_generate_content_url(endpoint_url: str, model_name: str) -> str:
    clean_endpoint = endpoint_url.strip()
    clean_model = (model_name or DEFAULT_GEMINI_TRANSCRIPTION_MODEL).strip()
    clean_model = clean_model.removeprefix("models/")
    if "{model}" in clean_endpoint:
        return clean_endpoint.replace("{model}", urllib.parse.quote(clean_model, safe="-_."))
    if clean_endpoint in {"", DEFAULT_GEMINI_TRANSCRIPTION_URL}:
        return f"https://generativelanguage.googleapis.com/v1beta/models/{clean_model}:generateContent"
    return clean_endpoint


def post_gemini_generate_content(endpoint_url: str, model_name: str, api_key: str, payload):
    if not api_key.strip():
        raise RuntimeError("ב-Gemini צריך API key.")

    endpoint_url = build_gemini_generate_content_url(endpoint_url, model_name)
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-goog-api-key": api_key.strip(),
    }

    request = urllib.request.Request(endpoint_url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=EXTERNAL_TRANSCRIPTION_TIMEOUT_SECONDS) as response:
            return response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as error:
        details = error.read().decode("utf-8", errors="replace")
        if error.code in {429, 500, 502, 503, 504}:
            raise ExternalApiBusyError(f"Gemini לא זמין כרגע או עמוס מדי. קוד {error.code}: {details[:700]}") from error
        raise ExternalApiHttpError(f"Gemini החזיר שגיאה {error.code}: {details[:700]}", error.code) from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"לא הצלחתי להתחבר ל-Gemini: {error}") from error


def post_openrouter_json(endpoint_url: str, api_key: str, payload):
    if not api_key.strip():
        raise RuntimeError("ב-OpenRouter צריך API key.")

    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain",
        "Authorization": f"Bearer {api_key.strip()}",
        "X-OpenRouter-Title": APP_TITLE,
    }
    request = urllib.request.Request(endpoint_url.strip(), data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=EXTERNAL_TRANSCRIPTION_TIMEOUT_SECONDS) as response:
            return response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as error:
        details = error.read().decode("utf-8", errors="replace")
        if error.code in {429, 500, 502, 503, 504}:
            raise ExternalApiBusyError(f"OpenRouter לא זמין כרגע או עמוס מדי. קוד {error.code}: {details[:700]}") from error
        raise ExternalApiHttpError(f"OpenRouter החזיר שגיאה {error.code}: {details[:700]}", error.code) from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"לא הצלחתי להתחבר ל-OpenRouter: {error}") from error


def complete_text_with_openrouter(prompt_text: str, model_name: str, api_key: str):
    raw_response = post_openrouter_json(
        DEFAULT_OPENROUTER_CHAT_URL,
        api_key,
        build_openrouter_chat_payload(prompt_text, model_name),
    )
    return extract_chat_completion_text(raw_response)


def post_openai_compatible_chat(endpoint_url: str, api_key: str, payload):
    endpoint = endpoint_url.strip() or DEFAULT_EXTERNAL_TRANSCRIPTION_URL
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain",
    }
    if api_key.strip():
        headers["Authorization"] = f"Bearer {api_key.strip()}"

    request = urllib.request.Request(endpoint, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=EXTERNAL_TRANSCRIPTION_TIMEOUT_SECONDS) as response:
            return response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as error:
        details = error.read().decode("utf-8", errors="replace")
        if error.code in {429, 500, 502, 503, 504}:
            raise ExternalApiBusyError(f"שירות הטקסט החיצוני עמוס כרגע. קוד {error.code}: {details[:700]}") from error
        raise ExternalApiHttpError(f"שירות הטקסט החיצוני החזיר שגיאה {error.code}: {details[:700]}", error.code) from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"לא הצלחתי להתחבר לשירות הטקסט החיצוני: {error}") from error


def complete_text_with_openai_compatible(prompt_text: str, endpoint_url: str, model_name: str, api_key: str):
    raw_response = post_openai_compatible_chat(
        endpoint_url,
        api_key,
        build_openrouter_chat_payload(prompt_text, model_name or DEFAULT_EXTERNAL_TRANSCRIPTION_MODEL),
    )
    return extract_chat_completion_text(raw_response)


def correct_transcript_text_with_gemini(transcript_text: str, endpoint_url: str, model_name: str, api_key: str, progress_callback):
    if not transcript_text.strip():
        return ""

    total_attempts = len(GEMINI_RETRY_DELAYS_SECONDS) + 1
    for attempt in range(1, total_attempts + 1):
        try:
            progress_callback(f"שולחת את הטקסט לתיקון ב-Gemini - ניסיון {attempt}/{total_attempts}")
            raw_response = post_gemini_generate_content(
                endpoint_url,
                model_name,
                api_key,
                build_gemini_text_fix_payload(transcript_text),
            )
            return extract_gemini_transcript_text(raw_response)
        except ExternalApiBusyError:
            if attempt >= total_attempts:
                raise
            wait_seconds = GEMINI_RETRY_DELAYS_SECONDS[attempt - 1]
            for remaining in range(wait_seconds, 0, -1):
                progress_callback(f"Gemini עמוס כרגע. תיקון הטקסט ינסה שוב בעוד {remaining} שניות")
                time.sleep(1)

    return transcript_text


def summarize_transcript_with_gemini(transcript_text: str, endpoint_url: str, model_name: str, api_key: str, progress_callback):
    if not transcript_text.strip():
        return ""

    total_attempts = len(GEMINI_RETRY_DELAYS_SECONDS) + 1
    for attempt in range(1, total_attempts + 1):
        try:
            progress_callback(f"שולחת את התמלול לסיכום מקצועי ב-Gemini - ניסיון {attempt}/{total_attempts}")
            raw_response = post_gemini_generate_content(
                endpoint_url,
                model_name,
                api_key,
                build_gemini_summary_payload(transcript_text),
            )
            return extract_gemini_transcript_text(raw_response)
        except ExternalApiBusyError:
            if attempt >= total_attempts:
                raise
            wait_seconds = GEMINI_RETRY_DELAYS_SECONDS[attempt - 1]
            for remaining in range(wait_seconds, 0, -1):
                progress_callback(f"Gemini עמוס כרגע. הסיכום ינסה שוב בעוד {remaining} שניות")
                time.sleep(1)

    return ""


def correct_transcript_text_with_ai_provider(transcript_text: str, provider: str, endpoint_url: str, text_model: str, api_keys, progress_callback):
    if not transcript_text.strip():
        return ""

    if provider == EXTERNAL_PROVIDER_OPENROUTER:
        prompt = f"{GEMINI_TEXT_FIX_PROMPT}\n\n--- תמלול לתיקון ---\n{transcript_text.strip()}"
        progress_callback("שולחת את הטקסט לתיקון דרך OpenRouter")
        return call_with_api_key_pool(
            api_keys,
            "OpenRouter",
            lambda api_key: complete_text_with_openrouter(prompt, text_model, api_key),
        )

    if provider == EXTERNAL_PROVIDER_OPENAI:
        prompt = f"{GEMINI_TEXT_FIX_PROMPT}\n\n--- תמלול לתיקון ---\n{transcript_text.strip()}"
        progress_callback("שולחת את הטקסט לתיקון דרך API תואם OpenAI")
        return call_with_api_key_pool(
            api_keys,
            "API תואם OpenAI",
            lambda api_key: complete_text_with_openai_compatible(prompt, endpoint_url, text_model, api_key),
        )

    return call_with_api_key_pool(
        api_keys,
        "Gemini",
        lambda api_key: correct_transcript_text_with_gemini(
            transcript_text,
            DEFAULT_GEMINI_TRANSCRIPTION_URL,
            text_model or DEFAULT_GEMINI_TRANSCRIPTION_MODEL,
            api_key,
            progress_callback,
        ),
    )


def summarize_transcript_with_ai_provider(transcript_text: str, provider: str, endpoint_url: str, text_model: str, api_keys, progress_callback):
    if not transcript_text.strip():
        return ""

    if provider == EXTERNAL_PROVIDER_OPENROUTER:
        prompt = f"{GEMINI_SUMMARY_PROMPT}\n\n--- תמלול ---\n{transcript_text.strip()}"
        progress_callback("שולחת את התמלול לסיכום מקצועי דרך OpenRouter")
        return call_with_api_key_pool(
            api_keys,
            "OpenRouter",
            lambda api_key: complete_text_with_openrouter(prompt, text_model, api_key),
        )

    if provider == EXTERNAL_PROVIDER_OPENAI:
        prompt = f"{GEMINI_SUMMARY_PROMPT}\n\n--- תמלול ---\n{transcript_text.strip()}"
        progress_callback("שולחת את התמלול לסיכום מקצועי דרך API תואם OpenAI")
        return call_with_api_key_pool(
            api_keys,
            "API תואם OpenAI",
            lambda api_key: complete_text_with_openai_compatible(prompt, endpoint_url, text_model, api_key),
        )

    return call_with_api_key_pool(
        api_keys,
        "Gemini",
        lambda api_key: summarize_transcript_with_gemini(
            transcript_text,
            DEFAULT_GEMINI_TRANSCRIPTION_URL,
            text_model or DEFAULT_GEMINI_TRANSCRIPTION_MODEL,
            api_key,
            progress_callback,
        ),
    )


def format_transcript_with_summary(summary_text: str, transcript_text: str):
    return (
        "סיכום מקצועי\n"
        "================\n"
        f"{summary_text.strip()}\n\n"
        "תמלול מלא\n"
        "================\n"
        f"{transcript_text.strip()}\n"
    )


def write_gemini_fixed_transcript(output_dir: str, corrected_text: str):
    fixed_path = os.path.join(output_dir, "transcript_all_segments_gemini_fixed.txt")
    with open(fixed_path, "w", encoding="utf-8") as handle:
        handle.write(corrected_text.strip() + "\n")
    return fixed_path


def write_summary_transcript(output_dir: str, transcript_path: str, summary_text: str, transcript_text: str):
    summary_path = os.path.join(output_dir, "summary_professional.txt")
    with open(summary_path, "w", encoding="utf-8") as handle:
        handle.write(summary_text.strip() + "\n")

    target_path = transcript_path or os.path.join(output_dir, "transcript_all_segments_with_summary.txt")
    with open(target_path, "w", encoding="utf-8") as handle:
        handle.write(format_transcript_with_summary(summary_text, transcript_text))
    return summary_path, target_path


def set_files_to_clipboard(file_paths):
    escaped_paths = []
    for path in file_paths:
        escaped_paths.append("'" + path.replace("'", "''") + "'")
    escaped = ",".join(escaped_paths)
    powershell = (
        "Add-Type -AssemblyName PresentationCore;"
        f"$files=@({escaped});"
        "$collection=New-Object System.Collections.Specialized.StringCollection;"
        "foreach($file in $files){[void]$collection.Add($file)};"
        "[System.Windows.Clipboard]::SetFileDropList($collection)"
    )
    subprocess.run(
        ["powershell", "-NoProfile", "-STA", "-Command", powershell],
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        check=True,
    )


def open_whatsapp_chat_by_phone(phone_number: str):
    targets = [f"whatsapp://send?phone={phone_number}"]
    for target in targets:
        try:
            os.startfile(target)
            return True
        except OSError:
            continue
    return False


def get_whatsapp_composer_point(left: int, top: int, width: int, height: int):
    return (
        left + int(width * 0.68),
        top + max(40, height - 68),
    )


def focus_whatsapp_message_box():
    target_window = None
    try:
        windows = [
            window
            for window in pyautogui.getWindowsWithTitle("WhatsApp")
            if window.width >= 500 and window.height >= 400
        ]
        if windows:
            target_window = max(windows, key=lambda window: window.width * window.height)
        else:
            active_window = pyautogui.getActiveWindow()
            if active_window and active_window.width >= 500 and active_window.height >= 400:
                target_window = active_window
    except Exception:
        target_window = None

    if target_window is not None:
        try:
            if target_window.isMinimized:
                target_window.restore()
            target_window.activate()
            time.sleep(1)
        except Exception:
            pass

    if target_window is not None:
        click_x, click_y = get_whatsapp_composer_point(
            target_window.left,
            target_window.top,
            target_window.width,
            target_window.height,
        )
    else:
        screen_width, screen_height = pyautogui.size()
        click_x, click_y = get_whatsapp_composer_point(0, 0, screen_width, screen_height)

    pyautogui.click(click_x, click_y)
    time.sleep(0.8)


def automate_whatsapp_send_to_bot(file_paths, phone_number: str, bot_label: str):
    direct_opened = open_whatsapp_chat_by_phone(phone_number)
    if not direct_opened:
        try:
            os.startfile("whatsapp:")
        except OSError as error:
            raise RuntimeError("לא הצלחתי לפתוח את אפליקציית WhatsApp שמותקנת במחשב.") from error

    time.sleep(7.5)
    pyautogui.PAUSE = 0.4
    if not direct_opened:
        pyautogui.hotkey("ctrl", "f")
        time.sleep(1)
        pyperclip.copy(bot_label)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(1.2)
        pyautogui.press("enter")
        time.sleep(1.8)
    if file_paths:
        set_files_to_clipboard(file_paths)
        time.sleep(0.8)
        focus_whatsapp_message_box()
        pyautogui.hotkey("ctrl", "v")
        time.sleep(3.2)


def send_audio_files_to_whatsapp_bot(file_paths, temp_dir: str, bot_config):
    phone_number = bot_config["phone"]
    bot_label = bot_config["label"]
    mp3_paths = prepare_whatsapp_audio_files(file_paths, temp_dir, WHATSAPP_PRIMARY_FORMAT)
    try:
        automate_whatsapp_send_to_bot(mp3_paths, phone_number, bot_label)
        return WHATSAPP_PRIMARY_FORMAT
    except Exception as mp3_error:
        ogg_paths = prepare_whatsapp_audio_files(file_paths, temp_dir, WHATSAPP_FALLBACK_FORMAT)
        try:
            automate_whatsapp_send_to_bot(ogg_paths, phone_number, bot_label)
            return WHATSAPP_FALLBACK_FORMAT
        except Exception as ogg_error:
            raise RuntimeError(
                "לא הצלחתי לשלוח את קבצי השמע ל-WhatsApp כ-MP3 וגם לא כ-OGG. "
                f"MP3: {mp3_error}; OGG: {ogg_error}"
            ) from ogg_error


def send_audio_files_to_whatsapp_bot_as_format(file_paths, temp_dir: str, bot_config, output_format: str):
    prepared_paths = prepare_whatsapp_audio_files(file_paths, temp_dir, output_format)
    automate_whatsapp_send_to_bot(prepared_paths, bot_config["phone"], bot_config["label"])
    return output_format


class AudioPreviewPlayer:
    def __init__(self):
        self.alias = f"pinkcat_preview_{os.getpid()}"
        self.path = ""
        self.is_open = False

    def _send(self, command: str, return_length: int = 0) -> str:
        if not hasattr(ctypes, "windll"):
            raise RuntimeError("נגן פנימי זמין כרגע רק ב-Windows.")
        buffer = ctypes.create_unicode_buffer(return_length or 1)
        result = ctypes.windll.winmm.mciSendStringW(command, buffer, return_length, None)
        if result:
            error_buffer = ctypes.create_unicode_buffer(256)
            ctypes.windll.winmm.mciGetErrorStringW(result, error_buffer, 256)
            raise RuntimeError(error_buffer.value or f"MCI error {result}")
        return buffer.value if return_length else ""

    def open(self, audio_path: str):
        self.close()
        if not audio_path or not os.path.exists(audio_path):
            raise FileNotFoundError("קובץ האודיו לא נמצא.")
        self.path = audio_path
        quoted_path = audio_path.replace('"', "")
        self._send(f'open "{quoted_path}" alias {self.alias}')
        self.is_open = True
        try:
            self._send(f"set {self.alias} time format milliseconds")
        except RuntimeError:
            pass

    def close(self):
        if self.is_open:
            try:
                self._send(f"close {self.alias}")
            except RuntimeError:
                pass
        self.is_open = False
        self.path = ""

    def play(self):
        if not self.is_open:
            raise RuntimeError("לא נטען קובץ לנגן.")
        self._send(f"play {self.alias}")

    def pause(self):
        if self.is_open:
            self._send(f"pause {self.alias}")

    def stop(self):
        if self.is_open:
            self._send(f"stop {self.alias}")
            try:
                self._send(f"seek {self.alias} to start")
            except RuntimeError:
                pass

    def status(self) -> str:
        if not self.is_open:
            return "closed"
        return self._send(f"status {self.alias} mode", 64).strip().lower()

    def length(self) -> int:
        if not self.is_open:
            return 0
        value = self._send(f"status {self.alias} length", 64).strip()
        return int(value) if value.isdigit() else 0

    def position(self) -> int:
        if not self.is_open:
            return 0
        value = self._send(f"status {self.alias} position", 64).strip()
        return int(value) if value.isdigit() else 0


class ResultDialog(tk.Toplevel):
    def __init__(self, master, folder_path, transcript_path=None, allow_whatsapp_fallback=False):
        super().__init__(master)
        self.title("מה לעשות עכשיו?")
        self.result = None
        self.folder_path = folder_path
        self.transcript_path = transcript_path
        self.configure(bg=PANEL)
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        wrapper = tk.Frame(self, bg=PANEL, padx=24, pady=22)
        wrapper.pack(fill="both", expand=True)

        tk.Label(
            wrapper,
            text="הפעולה הסתיימה בהצלחה",
            bg=PANEL,
            fg=TEXT,
            font=("Segoe UI", 15, "bold"),
        ).pack(pady=(0, 10))

        tk.Label(
            wrapper,
            text=f"הקבצים כבר נשמרו כאן:\n{folder_path}",
            bg=PANEL,
            fg=TEXT,
            font=("Segoe UI", 10),
            justify="center",
            wraplength=420,
        ).pack(pady=(0, 16))

        button_row = tk.Frame(wrapper, bg=PANEL)
        button_row.pack(fill="x")

        ttk.Button(button_row, text="פתחי את התיקייה", command=lambda: self.choose("open_folder")).pack(fill="x", pady=4)
        if transcript_path:
            ttk.Button(button_row, text="פתחי את קובץ התמלול", command=lambda: self.choose("open_transcript")).pack(fill="x", pady=4)
        ttk.Button(button_row, text="פתחי את בוט התמלול ב-WhatsApp", command=lambda: self.choose("whatsapp_bot")).pack(fill="x", pady=4)
        if allow_whatsapp_fallback:
            ttk.Button(
                button_row,
                text="הבוט לא תמלל? שלחי שוב כ-OGG",
                command=lambda: self.choose("whatsapp_ogg"),
            ).pack(fill="x", pady=4)
        ttk.Button(button_row, text="סיימתי", command=lambda: self.choose("close")).pack(fill="x", pady=4)

        self.protocol("WM_DELETE_WINDOW", lambda: self.choose("close"))

    def choose(self, value):
        self.result = value
        self.destroy()


class CatAudioCutterApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(APP_TITLE)
        self.root.geometry("590x900")
        self.root.minsize(540, 700)
        self.root.configure(bg=BG)

        self.app_settings = load_app_settings()
        self.history_records = load_transcription_history()
        setting = self.app_settings.get

        self.audio_path_var = tk.StringVar()
        self.save_dir_var = tk.StringVar(value=setting("save_dir", ""))
        self.cut_audio_var = tk.BooleanVar(value=setting("cut_audio", True))
        self.split_mode_var = tk.StringVar(value=setting("split_mode", "count"))
        self.segments_var = tk.StringVar(value=setting("segments_count", "2"))
        self.time_ranges_var = tk.StringVar(value=setting("time_ranges", "00:00-00:30\n00:30-01:00"))
        self.output_format_var = tk.StringVar(value=setting("output_format", DEFAULT_OUTPUT_FORMAT))
        self.bitrate_var = tk.StringVar(value=setting("bitrate", DEFAULT_MP3_BITRATE))
        self.sample_rate_var = tk.StringVar(value=setting("sample_rate", DEFAULT_MP3_SAMPLE_RATE))
        self.transcription_mode_var = tk.StringVar(value=setting("transcription_mode", TRANSCRIPTION_LOCAL))
        saved_whatsapp_bot = setting("whatsapp_bot", DEFAULT_WHATSAPP_BOT_OPTION)
        if saved_whatsapp_bot not in WHATSAPP_BOT_OPTIONS:
            saved_whatsapp_bot = DEFAULT_WHATSAPP_BOT_OPTION
        self.whatsapp_bot_var = tk.StringVar(value=saved_whatsapp_bot)
        self.transcription_engine_var = tk.StringVar(
            value=get_transcription_engine_label(setting("transcription_engine", TRANSCRIPTION_ENGINE_LOCAL))
        )
        self.local_model_var = tk.StringVar(value=setting("local_model_label", DEFAULT_LOCAL_MODEL_LABEL))
        self.improve_local_transcript_with_gemini_var = tk.BooleanVar(value=setting("improve_local_with_gemini", False))
        self.add_professional_summary_var = tk.BooleanVar(value=setting("add_professional_summary", False))
        self.external_provider_var = tk.StringVar(
            value=get_external_provider_label(setting("external_provider", EXTERNAL_PROVIDER_OPENAI))
        )
        self.external_api_url_var = tk.StringVar(value=setting("external_api_url", DEFAULT_EXTERNAL_TRANSCRIPTION_URL))
        self.external_model_var = tk.StringVar(value=setting("external_model", DEFAULT_EXTERNAL_TRANSCRIPTION_MODEL))
        self.external_text_model_var = tk.StringVar(value=setting("external_text_model", DEFAULT_GEMINI_TRANSCRIPTION_MODEL))
        self.active_external_provider_value = get_external_provider_value(self.external_provider_var.get())
        self.external_api_key_var = tk.StringVar(
            value="\n".join(read_api_keys_for_provider(self.active_external_provider_value))
        )
        azure_openai_configs = read_azure_openai_configs()
        azure_primary_config = azure_openai_configs[0] if azure_openai_configs else {}
        self.azure_endpoint_var = tk.StringVar(
            value=azure_primary_config.get("azure_endpoint") or setting("azure_endpoint", "")
        )
        self.azure_deployment_var = tk.StringVar(
            value=azure_primary_config.get("deployment_name") or setting("azure_deployment_name", DEFAULT_AZURE_OPENAI_DEPLOYMENT_NAME)
        )
        self.azure_api_version_var = tk.StringVar(
            value=azure_primary_config.get("api_version") or setting("azure_api_version", DEFAULT_AZURE_OPENAI_API_VERSION)
        )
        self.azure_api_keys_var = tk.StringVar(
            value="\n".join(config["api_key"] for config in azure_openai_configs)
        )
        self.azure_openai_form_dirty = False
        self.empowering_messages_enabled_var = tk.BooleanVar(value=setting("empowering_messages_enabled", True))
        self.status_var = tk.StringVar(value="מחכה לקובץ שמע")
        self.progress_var = tk.DoubleVar(value=0)
        self.selected_file_label_var = tk.StringVar(value="")
        self.player_progress_var = tk.DoubleVar(value=0)
        self.player_time_var = tk.StringVar(value="")
        self.player_status_var = tk.StringVar(value="בחרי קובץ כדי להאזין מתוך האפליקציה")

        self.temp_dir = None
        self.audio_player = AudioPreviewPlayer()
        self.audio_player_path = ""
        self.audio_player_update_job = None
        self.menu_design_image = None
        self.menu_design_source_image = None
        self.menu_ui_scale = 1.0
        self.settings_dialog = None
        self.random_message_job = None
        self.last_saved_dir = None
        self.last_output_files = []
        self.last_transcript_text = ""
        self.last_transcript_path = None
        self.is_processing = False
        self.processing_animation_job = None
        self.processing_animation_frames = [
            "מריצה פעולה   ",
            "מריצה פעולה.  ",
            "מריצה פעולה.. ",
            "מריצה פעולה...",
        ]
        self.processing_animation_index = 0
        self.processing_status_suffix = ""
        self.canvas_window_id = None

        self.build_styles()
        self.build_menu()
        self.build_ui()
        self.apply_loaded_text_settings()
        self.refresh_history_panel()
        self.toggle_split_mode()
        self.toggle_cut_controls()
        self.toggle_encoding_controls()
        self.toggle_transcription_settings()
        self.on_external_provider_change(initial=True)
        self.toggle_random_messages()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.after(120, self.update_scroll_helpers)

    def build_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Pink.TButton", font=("Segoe UI", 11, "bold"), padding=8)
        style.configure("Compact.TButton", font=("Segoe UI", 9, "bold"), padding=5)
        style.configure("Soft.TNotebook", background=PANEL, borderwidth=0)
        style.configure(
            "Soft.TNotebook.Tab",
            font=("Segoe UI", 10, "bold"),
            padding=(12, 8),
            background=SOFT_PINK,
            foreground=TEXT,
        )
        style.map("Soft.TNotebook.Tab", background=[("selected", "white")], foreground=[("selected", DARK_PINK)])
        style.configure(
            "Pink.Horizontal.TProgressbar",
            troughcolor="#ffe8f2",
            background=STRONG_PINK,
            bordercolor="#ffe8f2",
            lightcolor=STRONG_PINK,
            darkcolor=STRONG_PINK,
        )

    def build_menu(self):
        menubar = tk.Menu(self.root)
        update_menu = tk.Menu(menubar, tearoff=False)
        update_menu.add_command(label="בדוק ועדכן עכשיו", command=self.start_software_update)
        update_menu.add_command(label="פתח עמוד GitHub", command=self.open_github_page)
        menubar.add_cascade(label="עדכון תוכנה", menu=update_menu)
        self.root.config(menu=menubar)

    def build_ui(self):
        shell = tk.Frame(self.root, bg=BG)
        shell.pack(fill="both", expand=True)

        self.main_canvas = tk.Canvas(shell, bg=BG, highlightthickness=0)
        self.main_scrollbar = ttk.Scrollbar(shell, orient="vertical", command=self.main_canvas.yview)
        self.main_canvas.configure(yscrollcommand=self.main_scrollbar.set)
        self.main_canvas.pack(side="left", fill="both", expand=True)
        self.main_scrollbar.pack(side="right", fill="y")
        self.main_canvas.bind("<Configure>", self.on_canvas_configure)
        self.main_canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        self.quick_scroll_button = ttk.Button(self.root, text="↓", width=3, command=self.scroll_to_actions, style="Pink.TButton")

        self.build_mockup_canvas()
        self.build_settings_dialog()

    def build_mockup_canvas(self):
        image_path = get_menu_design_image_path()
        if not image_path:
            fallback = tk.Frame(self.main_canvas, bg=BG, padx=30, pady=26)
            self.canvas_window_id = self.main_canvas.create_window((0, 0), window=fallback, anchor="nw")
            fallback.bind("<Configure>", self.on_content_configure)
            self.build_main_action_panel(fallback)
            return

        self.menu_design_source_image = tk.PhotoImage(file=image_path)
        self.menu_design_image = self.menu_design_source_image.subsample(2, 2)
        self.menu_ui_scale = self.menu_design_image.width() / max(self.menu_design_source_image.width(), 1)
        width = self.menu_design_image.width()
        height = self.menu_design_image.height()
        self.menu_image_item = self.main_canvas.create_image(0, 0, image=self.menu_design_image, anchor="nw")
        self.main_canvas.configure(scrollregion=(0, 0, width, height + self.s(120)))
        self.canvas_window_id = None

        self.create_mockup_hotspot("settings", 35, 35, 274, 183, self.open_settings_dialog)
        self.create_mockup_hotspot("upload", 67, 262, 1015, 691, self.pick_audio_file)
        self.create_mockup_hotspot("player", 38, 716, 1030, 805, self.toggle_audio_preview)
        self.create_mockup_hotspot("cut", 67, 822, 1015, 1252, self.start_cut_audio_only)
        self.create_mockup_hotspot("transcribe", 75, 1356, 1018, 1788, self.start_transcribe_audio_now)

        self.player_fill_item = self.main_canvas.create_rectangle(self.s(60), self.s(729), self.s(60), self.s(783), fill="#f4a9c7", outline="")
        self.player_time_canvas_item = self.main_canvas.create_text(
            self.s(1000),
            self.s(786),
            text=self.player_time_var.get(),
            anchor="e",
            fill=TEXT,
            font=("Segoe UI", self.sf(10), "bold"),
        )
        self.selected_file_canvas_item = self.main_canvas.create_text(
            self.s(540),
            self.s(792),
            text=self.selected_file_label_var.get(),
            anchor="center",
            fill=TEXT,
            font=("Segoe UI", self.sf(10), "bold"),
            width=self.s(660),
        )
        self.status_canvas_item = self.main_canvas.create_text(
            self.s(540),
            self.s(1850),
            text=self.status_var.get(),
            anchor="center",
            fill=TEXT,
            font=("Segoe UI", self.sf(11), "bold"),
            width=self.s(900),
        )
        self.progress_canvas_item = self.main_canvas.create_rectangle(self.s(80), self.s(1872), self.s(80), self.s(1888), fill=TEAL, outline="")
        self.progress_track_canvas_item = self.main_canvas.create_rectangle(self.s(80), self.s(1872), self.s(1000), self.s(1888), outline="#ff9ec9", width=2)
        self.folder_canvas_item = self.main_canvas.create_text(
            self.s(1040),
            self.s(1838),
            text="📁",
            anchor="e",
            font=("Segoe UI Emoji", self.sf(34)),
            tags=("open_output_folder",),
        )
        self.main_canvas.tag_bind(self.folder_canvas_item, "<Button-1>", lambda _event: self.open_output_folder())
        self.main_canvas.tag_bind(
            self.folder_canvas_item,
            "<Enter>",
            lambda _event: self.main_canvas.configure(cursor="hand2"),
        )
        self.main_canvas.tag_bind(
            self.folder_canvas_item,
            "<Leave>",
            lambda _event: self.main_canvas.configure(cursor=""),
        )
        self.processing_label_var = tk.StringVar(value="")
        self.progress_bar = ttk.Progressbar(self.root, variable=self.progress_var, maximum=100)
        self.player_play_button = None
        self.message_button = None
        self.open_folder_button = None
        self.action_row = self.main_canvas
        self.cut_button = self.transcribe_button = self.main_canvas
        self.cut_audio_button = self.upload_action_button = self.main_canvas

        screen_height = max(720, self.root.winfo_screenheight())
        target_width = width + 34
        target_height = min(height + 90, screen_height - 70)
        self.root.geometry(f"{target_width}x{target_height}")

    def s(self, value: float) -> int:
        return int(round(value * self.menu_ui_scale))

    def sf(self, value: int) -> int:
        return max(7, int(round(value * self.menu_ui_scale)))

    def create_mockup_hotspot(self, tag: str, x1: int, y1: int, x2: int, y2: int, command):
        item = self.main_canvas.create_rectangle(self.s(x1), self.s(y1), self.s(x2), self.s(y2), fill="", outline="", tags=(tag, "hotspot"))
        self.main_canvas.tag_bind(item, "<Button-1>", lambda _event: command())
        self.main_canvas.tag_bind(item, "<Enter>", lambda _event: self.main_canvas.configure(cursor="hand2"))
        self.main_canvas.tag_bind(item, "<Leave>", lambda _event: self.main_canvas.configure(cursor=""))
        return item

    def build_settings_dialog(self):
        self.settings_dialog = tk.Toplevel(self.root)
        self.settings_dialog.title("הגדרות")
        self.settings_dialog.configure(bg=PANEL)
        self.settings_dialog.geometry("470x760")
        self.settings_dialog.withdraw()
        self.settings_dialog.protocol("WM_DELETE_WINDOW", self.hide_settings_dialog)
        self.build_settings_panel(self.settings_dialog)

    def open_settings_dialog(self):
        if not self.settings_dialog:
            return
        self.settings_dialog.deiconify()
        self.settings_dialog.lift()
        self.settings_dialog.focus_force()

    def hide_settings_dialog(self):
        if self.settings_dialog:
            self.settings_dialog.withdraw()

    def build_settings_panel(self, parent):
        tk.Label(
            parent,
            text="הגדרות",
            bg=PANEL,
            fg=DARK_PINK,
            font=("Segoe UI", 20, "bold"),
        ).pack(anchor="e", pady=(0, 4))
        tk.Label(
            parent,
            text="כל מה שלא צריך לגעת בו בכל פעולה נמצא כאן בטאבים.",
            bg=PANEL,
            fg=TEXT,
            font=("Segoe UI", 9),
            wraplength=310,
            justify="right",
        ).pack(anchor="e", pady=(0, 12))

        self.settings_notebook = ttk.Notebook(parent, style="Soft.TNotebook")
        self.settings_notebook.pack(fill="both", expand=True)

        general_tab = tk.Frame(self.settings_notebook, bg=PANEL, padx=8, pady=10)
        split_tab = tk.Frame(self.settings_notebook, bg=PANEL, padx=8, pady=10)
        transcription_tab = tk.Frame(self.settings_notebook, bg=PANEL, padx=8, pady=10)
        history_tab = tk.Frame(self.settings_notebook, bg=PANEL, padx=8, pady=10)

        self.settings_notebook.add(general_tab, text="כללי")
        self.settings_notebook.add(split_tab, text="חיתוך")
        self.settings_notebook.add(transcription_tab, text="תמלול")
        self.settings_notebook.add(history_tab, text="היסטוריה")

        self.build_save_section(general_tab)
        self.build_split_section(split_tab)
        self.build_options_section(transcription_tab)
        self.build_history_panel(history_tab)

    def build_main_action_panel(self, parent):
        header = tk.Frame(parent, bg=BG)
        header.pack(fill="x", pady=(0, 22))

        tk.Label(
            header,
            text="תמלול אודיו",
            bg=BG,
            fg="#df255c",
            font=("Segoe UI", 42, "bold"),
        ).pack(anchor="e")
        tk.Label(
            header,
            text="בחרי פעולה",
            bg=BG,
            fg=TEXT,
            font=("Segoe UI", 19, "bold"),
        ).pack(anchor="e")

        actions = tk.Frame(parent, bg=BG)
        actions.pack(fill="both", expand=True)

        self.upload_action_button = self.build_action_card(
            actions,
            title="העלאת קובץ",
            subtitle="בחרי את קובץ האודיו לתמלול",
            button_color=SOFT_PINK,
            command=self.pick_audio_file,
        )
        self.build_audio_player_section(actions)
        self.cut_audio_button = self.build_action_card(
            actions,
            title="חיתוך אודיו",
            subtitle="חיתוך מהיר למספר חלקים שתבחרי",
            button_color=SOFT_PINK,
            command=self.start_cut_audio_only,
        )
        self.transcribe_button = self.build_action_card(
            actions,
            title="תמלל",
            subtitle="תמלול לפי ההגדרות שבטאבים",
            button_color=TEAL,
            command=self.start_transcribe_audio_now,
        )
        self.cut_button = self.transcribe_button
        self.build_status_section(actions)

    def bind_click_recursive(self, widget, command):
        widget.configure(cursor="hand2")
        widget.bind("<Button-1>", lambda _event: command())
        for child in widget.winfo_children():
            self.bind_click_recursive(child, command)

    def build_action_card(self, parent, title: str, subtitle: str, button_color: str, command):
        shadow = tk.Frame(parent, bg=ACTION_SHADOW)
        shadow.pack(fill="x", padx=(10, 0), pady=(0, 20))

        card = tk.Frame(
            shadow,
            bg="white",
            height=210,
            highlightthickness=3,
            highlightbackground="#ff9ec9",
            highlightcolor="#ff9ec9",
            padx=22,
            pady=18,
        )
        card.pack(fill="x", padx=(0, 10), pady=(0, 10))
        card.pack_propagate(False)

        tk.Label(
            card,
            text="♪",
            bg="white",
            fg="#e87aa9",
            font=("Segoe UI", 46, "bold"),
        ).pack(anchor="center", pady=(2, 0))
        tk.Label(
            card,
            text=subtitle,
            bg="white",
            fg=TEXT,
            font=("Segoe UI", 10),
        ).pack(anchor="center", pady=(0, 12))

        label_shell = tk.Frame(
            card,
            bg=button_color,
            highlightthickness=2,
            highlightbackground="#ff9ec9",
            padx=22,
            pady=4,
        )
        label_shell.pack(anchor="center", fill="x", padx=90, pady=(0, 4))
        tk.Label(
            label_shell,
            text=title,
            bg=button_color,
            fg="#df255c",
            font=("Segoe UI", 28, "bold"),
        ).pack(anchor="center")

        self.bind_click_recursive(card, command)
        return card

    def build_audio_player_section(self, parent):
        player = tk.Frame(parent, bg="white", padx=18, pady=12)
        player.pack(fill="x", pady=(0, 22))

        self.player_play_button = ttk.Button(
            player,
            text="▶",
            command=self.toggle_audio_preview,
            width=4,
            style="Pink.TButton",
        )
        self.player_play_button.pack(side="left", padx=(0, 10))
        ttk.Button(
            player,
            text="■",
            command=self.stop_audio_preview,
            width=4,
            style="Compact.TButton",
        ).pack(side="left", padx=(0, 10))

        meter = tk.Frame(player, bg="white")
        meter.pack(side="left", fill="x", expand=True)
        self.player_progress_bar = ttk.Progressbar(
            meter,
            variable=self.player_progress_var,
            maximum=100,
            style="Pink.Horizontal.TProgressbar",
        )
        self.player_progress_bar.pack(fill="x", pady=(0, 5))
        info_row = tk.Frame(meter, bg="white")
        info_row.pack(fill="x")
        tk.Label(
            info_row,
            textvariable=self.selected_file_label_var,
            bg="white",
            fg=TEXT,
            font=("Segoe UI", 9, "bold"),
            anchor="e",
        ).pack(side="right", fill="x", expand=True)
        tk.Label(
            info_row,
            textvariable=self.player_time_var,
            bg="white",
            fg=TEXT,
            font=("Segoe UI", 9),
        ).pack(side="left")
        tk.Label(
            player,
            textvariable=self.player_status_var,
            bg="white",
            fg=DARK_PINK,
            font=("Segoe UI", 9),
            wraplength=220,
            justify="right",
        ).pack(side="right", padx=(12, 0))

    def build_history_panel(self, parent):
        tk.Label(
            parent,
            text="שיחות אחרונות",
            bg=PANEL,
            fg=TEXT,
            font=("Segoe UI", 13, "bold"),
        ).pack(anchor="w", pady=(0, 8))

        self.history_listbox = tk.Listbox(
            parent,
            height=22,
            bg="white",
            fg=TEXT,
            relief="flat",
            activestyle="none",
            font=("Segoe UI", 9),
            exportselection=False,
        )
        self.history_listbox.pack(fill="both", expand=True)
        self.history_listbox.bind("<Double-Button-1>", lambda _event: self.open_selected_history_transcript())

        button_row = tk.Frame(parent, bg=PANEL)
        button_row.pack(fill="x", pady=(10, 0))

        ttk.Button(
            button_row,
            text="פתח תמלול",
            command=self.open_selected_history_transcript,
            style="Compact.TButton",
        ).pack(side="left", fill="x", expand=True, padx=(0, 4))
        ttk.Button(
            button_row,
            text="פתח תיקייה",
            command=self.open_selected_history_folder,
            style="Compact.TButton",
        ).pack(side="left", fill="x", expand=True, padx=(4, 0))

    def build_file_section(self, parent):
        tk.Label(parent, text="🎧 קובץ שמע", bg=PANEL, fg=TEXT, font=("Segoe UI", 12, "bold")).pack(anchor="w")

        file_row = tk.Frame(parent, bg=PANEL)
        file_row.pack(fill="x", pady=(8, 18))

        tk.Entry(
            file_row,
            textvariable=self.audio_path_var,
            font=("Segoe UI", 10),
            bg="white",
            fg=TEXT,
            relief="flat",
        ).pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 10))

        ttk.Button(file_row, text="בחרי קובץ", command=self.pick_audio_file, style="Pink.TButton").pack(side="left")

    def build_split_section(self, parent):
        section = tk.Frame(parent, bg=CARD, padx=14, pady=14)
        section.pack(fill="x", pady=(0, 16))

        tk.Label(section, text="חיתוך מקטעים", bg=CARD, fg=TEXT, font=("Segoe UI", 12, "bold")).pack(anchor="w")
        tk.Checkbutton(
            section,
            text="לחתוך את קובץ השמע לפני התמלול/שמירה",
            variable=self.cut_audio_var,
            command=self.toggle_cut_controls,
            bg=CARD,
            fg=TEXT,
            activebackground=CARD,
            activeforeground=TEXT,
            selectcolor="#fff6fb",
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", pady=(10, 0))

        self.split_controls_frame = tk.Frame(section, bg=CARD)
        self.split_controls_frame.pack(fill="x")

        radio_row = tk.Frame(self.split_controls_frame, bg=CARD)
        radio_row.pack(fill="x", pady=(10, 10))

        tk.Radiobutton(
            radio_row,
            text="לפי מספר מקטעים",
            variable=self.split_mode_var,
            value="count",
            command=self.toggle_split_mode,
            bg=CARD,
            fg=TEXT,
            activebackground=CARD,
            selectcolor="#fff6fb",
            font=("Segoe UI", 10, "bold"),
        ).pack(side="left", padx=(0, 18))

        tk.Radiobutton(
            radio_row,
            text="לפי זמנים",
            variable=self.split_mode_var,
            value="times",
            command=self.toggle_split_mode,
            bg=CARD,
            fg=TEXT,
            activebackground=CARD,
            selectcolor="#fff6fb",
            font=("Segoe UI", 10, "bold"),
        ).pack(side="left")

        self.count_frame = tk.Frame(self.split_controls_frame, bg=CARD)
        self.count_frame.pack(fill="x", pady=(0, 8))

        tk.Entry(
            self.count_frame,
            textvariable=self.segments_var,
            width=10,
            justify="center",
            font=("Segoe UI", 14, "bold"),
            bg="white",
            fg=DARK_PINK,
            relief="flat",
        ).pack(side="left", ipady=8)

        tk.Label(
            self.count_frame,
            text="לדוגמה: 2 לחצי, 10 לעשרה חלקים שווים.",
            bg=CARD,
            fg=TEXT,
            font=("Segoe UI", 10),
        ).pack(side="left", padx=12)

        self.times_frame = tk.Frame(self.split_controls_frame, bg=CARD)

        tk.Label(
            self.times_frame,
            text="כתבי טווחי זמן, כל טווח בשורה נפרדת או מופרד בפסיקים. דוגמה: 00:00-00:30",
            bg=CARD,
            fg=TEXT,
            font=("Segoe UI", 10),
            wraplength=700,
            justify="left",
        ).pack(anchor="w", pady=(0, 8))

        self.times_text = tk.Text(
            self.times_frame,
            height=5,
            font=("Consolas", 10),
            bg="white",
            fg=TEXT,
            relief="flat",
            wrap="word",
        )
        self.times_text.pack(fill="x")
        self.times_text.insert("1.0", self.time_ranges_var.get())

    def build_save_section(self, parent):
        section = tk.Frame(parent, bg=CARD, padx=14, pady=14)
        section.pack(fill="x", pady=(0, 16))

        tk.Label(section, text="💖 איפה ואיך לשמור?", bg=CARD, fg=TEXT, font=("Segoe UI", 12, "bold")).pack(anchor="w")

        save_row = tk.Frame(section, bg=CARD)
        save_row.pack(fill="x", pady=(10, 12))

        tk.Entry(
            save_row,
            textvariable=self.save_dir_var,
            font=("Segoe UI", 10),
            bg="white",
            fg=TEXT,
            relief="flat",
        ).pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 10))

        ttk.Button(save_row, text="בחרי תיקייה", command=self.pick_save_dir, style="Pink.TButton").pack(side="left")
        ttk.Button(save_row, text="📁 פתחי תיקייה", command=self.open_output_folder, style="Pink.TButton").pack(side="left", padx=(10, 0))

        format_row = tk.Frame(section, bg=CARD)
        format_row.pack(fill="x", pady=(0, 10))

        tk.Label(format_row, text="פורמט פלט", bg=CARD, fg=TEXT, font=("Segoe UI", 10, "bold")).pack(side="left")
        self.format_combo = ttk.Combobox(
            format_row,
            textvariable=self.output_format_var,
            values=["ogg", "mp3", "wav"],
            state="readonly",
            width=10,
        )
        self.format_combo.pack(side="left", padx=(8, 22))
        self.format_combo.bind("<<ComboboxSelected>>", lambda _event: self.toggle_encoding_controls())

        tk.Label(format_row, text="קצב סיביות", bg=CARD, fg=TEXT, font=("Segoe UI", 10, "bold")).pack(side="left")
        self.bitrate_combo = ttk.Combobox(
            format_row,
            textvariable=self.bitrate_var,
            values=BITRATE_OPTIONS,
            state="readonly",
            width=10,
        )
        self.bitrate_combo.pack(side="left", padx=(8, 22))
        tk.Label(format_row, text="קצב דגימה", bg=CARD, fg=TEXT, font=("Segoe UI", 10, "bold")).pack(side="left")
        self.sample_rate_combo = ttk.Combobox(
            format_row,
            textvariable=self.sample_rate_var,
            values=SAMPLE_RATE_OPTIONS,
            state="readonly",
            width=10,
        )
        self.sample_rate_combo.pack(side="left", padx=(8, 0))

    def build_options_section(self, parent):
        section = tk.Frame(parent, bg=CARD, padx=14, pady=14)
        section.pack(fill="x", pady=(0, 14))

        tk.Label(section, text="תמלול וסיכום", bg=CARD, fg=TEXT, font=("Segoe UI", 12, "bold")).pack(anchor="w")

        mode_row = tk.Frame(section, bg=CARD)
        mode_row.pack(fill="x", pady=(10, 8))

        mode_options = [
            ("תמלול בלבד", TRANSCRIPTION_LOCAL),
            ("תמלול + תיקון API", TRANSCRIPTION_EXTERNAL),
            ("WhatsApp", TRANSCRIPTION_WHATSAPP),
            ("רק לשמור", TRANSCRIPTION_NONE),
        ]
        for label, value in mode_options:
            tk.Radiobutton(
                mode_row,
                text=label,
                variable=self.transcription_mode_var,
                value=value,
                command=self.toggle_transcription_settings,
                bg=CARD,
                fg=TEXT,
                activebackground=CARD,
                selectcolor="#fff6fb",
                font=("Segoe UI", 10, "bold"),
            ).pack(side="left", padx=(0, 14))

        tk.Checkbutton(
            section,
            text="להוסיף סיכום מקצועי בתחילת קובץ התמלול",
            variable=self.add_professional_summary_var,
            command=self.toggle_transcription_settings,
            bg=CARD,
            fg=TEXT,
            activebackground=CARD,
            activeforeground=TEXT,
            selectcolor="#fff6fb",
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", pady=(2, 8))

        self.local_transcription_frame = tk.Frame(section, bg=CARD)
        engine_row = tk.Frame(self.local_transcription_frame, bg=CARD)
        engine_row.pack(fill="x", pady=(0, 8))
        tk.Label(
            engine_row,
            text="מנוע תמלול",
            bg=CARD,
            fg=TEXT,
            font=("Segoe UI", 10, "bold"),
        ).pack(side="left", padx=(0, 8))
        self.transcription_engine_combo = ttk.Combobox(
            engine_row,
            textvariable=self.transcription_engine_var,
            values=list(TRANSCRIPTION_ENGINE_OPTIONS.keys()),
            state="readonly",
            width=28,
        )
        self.transcription_engine_combo.pack(side="left")
        self.transcription_engine_combo.bind("<<ComboboxSelected>>", lambda _event: self.toggle_transcription_engine_settings())

        self.local_model_row = tk.Frame(self.local_transcription_frame, bg=CARD)
        self.local_model_row.pack(fill="x")
        tk.Label(
            self.local_model_row,
            text="מודל מקומי",
            bg=CARD,
            fg=TEXT,
            font=("Segoe UI", 10, "bold"),
        ).pack(side="left", padx=(0, 8))
        self.local_model_combo = ttk.Combobox(
            self.local_model_row,
            textvariable=self.local_model_var,
            values=list(LOCAL_MODEL_OPTIONS.keys()),
            state="readonly",
            width=42,
        )
        self.local_model_combo.pack(side="left")
        self.local_model_download_button = ttk.Button(
            self.local_model_row,
            text="בדוק/הורד מודל",
            command=self.start_model_download,
            style="Compact.TButton",
        )
        self.local_model_download_button.pack(side="left", padx=(10, 0))
        tk.Checkbutton(
            self.local_transcription_frame,
            text="אחרי התמלול, לתקן את הטקסט עם Gemini/OpenRouter",
            variable=self.improve_local_transcript_with_gemini_var,
            command=self.toggle_transcription_settings,
            bg=CARD,
            fg=TEXT,
            activebackground=CARD,
            activeforeground=TEXT,
            selectcolor="#fff6fb",
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", pady=(10, 0))
        self.transcription_engine_note_var = tk.StringVar()
        tk.Label(
            self.local_transcription_frame,
            textvariable=self.transcription_engine_note_var,
            bg=CARD,
            fg=TEXT,
            font=("Segoe UI", 9),
            wraplength=680,
            justify="left",
        ).pack(anchor="w", pady=(8, 0))

        self.azure_openai_frame = tk.Frame(self.local_transcription_frame, bg=CARD)
        azure_grid = tk.Frame(self.azure_openai_frame, bg=CARD)
        azure_grid.pack(fill="x", pady=(10, 0))
        tk.Label(azure_grid, text="Azure endpoint", bg=CARD, fg=TEXT, font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", pady=4)
        self.azure_endpoint_entry = tk.Entry(
            azure_grid,
            textvariable=self.azure_endpoint_var,
            font=("Segoe UI", 9),
            bg="white",
            fg=TEXT,
            relief="flat",
        )
        self.azure_endpoint_entry.grid(row=0, column=1, columnspan=2, sticky="ew", padx=(10, 0), ipady=6, pady=4)
        tk.Label(azure_grid, text="Deployment", bg=CARD, fg=TEXT, font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky="w", pady=4)
        tk.Entry(
            azure_grid,
            textvariable=self.azure_deployment_var,
            font=("Segoe UI", 9),
            bg="white",
            fg=TEXT,
            relief="flat",
        ).grid(row=1, column=1, sticky="ew", padx=(10, 0), ipady=6, pady=4)
        tk.Label(azure_grid, text="API version", bg=CARD, fg=TEXT, font=("Segoe UI", 10, "bold")).grid(row=2, column=0, sticky="w", pady=4)
        tk.Entry(
            azure_grid,
            textvariable=self.azure_api_version_var,
            font=("Segoe UI", 9),
            bg="white",
            fg=TEXT,
            relief="flat",
        ).grid(row=2, column=1, sticky="ew", padx=(10, 0), ipady=6, pady=4)
        tk.Label(azure_grid, text="Azure API keys", bg=CARD, fg=TEXT, font=("Segoe UI", 10, "bold")).grid(row=3, column=0, sticky="nw", pady=4)
        self.azure_api_key_entry = tk.Text(
            azure_grid,
            height=4,
            font=("Segoe UI", 9),
            bg="white",
            fg=TEXT,
            relief="flat",
            wrap="none",
        )
        self.azure_api_key_entry.grid(row=3, column=1, sticky="ew", padx=(10, 0), pady=4)
        self.azure_api_key_entry.insert("1.0", self.azure_api_keys_var.get())
        self.azure_api_key_entry.bind("<<Modified>>", self.on_azure_text_modified)
        ttk.Button(
            azure_grid,
            text="שמור Azure",
            command=lambda: self.save_current_azure_openai_configs(silent=False, force=True),
            style="Pink.TButton",
            width=12,
        ).grid(row=3, column=2, sticky="new", padx=(8, 0), pady=4)
        ttk.Button(
            azure_grid,
            text="טען מהקובץ",
            command=self.load_azure_openai_configs_from_file,
            style="Pink.TButton",
            width=12,
        ).grid(row=4, column=1, sticky="w", padx=(10, 0), pady=(2, 4))
        ttk.Button(
            azure_grid,
            text="פתח קובץ מפתחות",
            command=self.open_api_key_file,
            style="Pink.TButton",
            width=14,
        ).grid(row=4, column=2, sticky="ew", padx=(8, 0), pady=(2, 4))
        azure_grid.columnconfigure(1, weight=1)
        tk.Label(
            self.azure_openai_frame,
            text=(
                "שימי כאן את ה-Endpoint של Azure, שם ה-Deployment של Whisper, גרסת API, ומפתח אחד בכל שורה. "
                "אם יש כמה מפתחות לאותו Azure resource, הכלי ינסה אותם לפי הסדר."
            ),
            bg=CARD,
            fg=TEXT,
            font=("Segoe UI", 9),
            wraplength=700,
            justify="left",
        ).pack(anchor="w", pady=(6, 0))
        for variable in (self.azure_endpoint_var, self.azure_deployment_var, self.azure_api_version_var):
            variable.trace_add("write", lambda *_args: self.mark_azure_openai_form_dirty())

        self.external_transcription_frame = tk.Frame(section, bg=CARD)
        external_grid = tk.Frame(self.external_transcription_frame, bg=CARD)
        external_grid.pack(fill="x")
        tk.Label(external_grid, text="ספק שיפור טקסט", bg=CARD, fg=TEXT, font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", pady=4)
        self.external_provider_combo = ttk.Combobox(
            external_grid,
            textvariable=self.external_provider_var,
            values=list(EXTERNAL_PROVIDER_OPTIONS.keys()),
            state="readonly",
            width=28,
        )
        self.external_provider_combo.grid(row=0, column=1, sticky="w", padx=(10, 0), pady=4)
        self.external_provider_combo.bind("<<ComboboxSelected>>", lambda _event: self.on_external_provider_change())

        tk.Label(external_grid, text="כתובת API לטקסט", bg=CARD, fg=TEXT, font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky="w", pady=4)
        tk.Entry(
            external_grid,
            textvariable=self.external_api_url_var,
            font=("Segoe UI", 9),
            bg="white",
            fg=TEXT,
            relief="flat",
        ).grid(row=1, column=1, sticky="ew", padx=(10, 0), ipady=6, pady=4)
        tk.Label(external_grid, text="מודל תיקון/סיכום", bg=CARD, fg=TEXT, font=("Segoe UI", 10, "bold")).grid(row=2, column=0, sticky="w", pady=4)
        tk.Entry(
            external_grid,
            textvariable=self.external_model_var,
            font=("Segoe UI", 9),
            bg="white",
            fg=TEXT,
            relief="flat",
        ).grid(row=2, column=1, sticky="ew", padx=(10, 0), ipady=6, pady=4)
        tk.Label(external_grid, text="מודל טקסט חלופי", bg=CARD, fg=TEXT, font=("Segoe UI", 10, "bold")).grid(row=3, column=0, sticky="w", pady=4)
        tk.Entry(
            external_grid,
            textvariable=self.external_text_model_var,
            font=("Segoe UI", 9),
            bg="white",
            fg=TEXT,
            relief="flat",
        ).grid(row=3, column=1, sticky="ew", padx=(10, 0), ipady=6, pady=4)
        tk.Label(external_grid, text="API keys", bg=CARD, fg=TEXT, font=("Segoe UI", 10, "bold")).grid(row=4, column=0, sticky="nw", pady=4)
        self.external_api_key_entry = tk.Text(
            external_grid,
            height=4,
            font=("Segoe UI", 9),
            bg="white",
            fg=TEXT,
            relief="flat",
            wrap="none",
        )
        self.external_api_key_entry.grid(row=4, column=1, sticky="ew", padx=(10, 0), pady=4)
        self.external_api_key_entry.insert("1.0", self.external_api_key_var.get())
        self.external_api_key_entry.bind("<Control-v>", self.paste_external_api_key_event)
        self.external_api_key_entry.bind("<Control-V>", self.paste_external_api_key_event)
        self.external_api_key_entry.bind("<Button-3>", self.show_api_key_context_menu)
        ttk.Button(
            external_grid,
            text="הדבק",
            command=self.paste_external_api_key,
            style="Pink.TButton",
            width=8,
        ).grid(row=4, column=2, sticky="new", padx=(8, 0), pady=4)
        ttk.Button(
            external_grid,
            text="טען מפתחות",
            command=self.load_api_key_from_file,
            style="Pink.TButton",
            width=12,
        ).grid(row=5, column=1, sticky="w", padx=(10, 0), pady=(2, 4))
        ttk.Button(
            external_grid,
            text="פתח קובץ מפתחות",
            command=self.open_api_key_file,
            style="Pink.TButton",
            width=14,
        ).grid(row=5, column=2, sticky="ew", padx=(8, 0), pady=(2, 4))
        external_grid.columnconfigure(1, weight=1)
        tk.Label(
            self.external_transcription_frame,
            text="ספק תיקון הטקסט לא מקבל אודיו. אחרי שלב התמלול הכלי שולח רק את הטקסט לניקוי ג'יבריש, תחביר וסיכום. אפשר לשמור כמה מפתחות לכל ספק, מפתח אחד בכל שורה; אם מפתח נחסם או נגמר לו quota, הכלי ינסה את הבא.",
            bg=CARD,
            fg=TEXT,
            font=("Segoe UI", 9),
            wraplength=700,
            justify="left",
        ).pack(anchor="w", pady=(6, 0))

        self.whatsapp_transcription_frame = tk.Frame(section, bg=CARD)
        whatsapp_bot_row = tk.Frame(self.whatsapp_transcription_frame, bg=CARD)
        whatsapp_bot_row.pack(fill="x", pady=(0, 6))
        tk.Label(
            whatsapp_bot_row,
            text="בוט תמלול",
            bg=CARD,
            fg=TEXT,
            font=("Segoe UI", 10, "bold"),
        ).pack(side="left", padx=(0, 8))
        self.whatsapp_bot_combo = ttk.Combobox(
            whatsapp_bot_row,
            textvariable=self.whatsapp_bot_var,
            values=list(WHATSAPP_BOT_OPTIONS.keys()),
            state="readonly",
            width=43,
        )
        self.whatsapp_bot_combo.pack(side="left", fill="x", expand=True)
        tk.Label(
            self.whatsapp_transcription_frame,
            text=(
                "המקטעים יישמרו במחשב, יומרו ל-MP3 ויודבקו בשורת ההודעה של הבוט. "
                "אחרי שהקובץ מופיע ב-WhatsApp צריך רק ללחוץ Enter."
            ),
            bg=CARD,
            fg=TEXT,
            font=("Segoe UI", 9),
            wraplength=700,
            justify="left",
        ).pack(anchor="w")

        self.no_transcription_frame = tk.Frame(section, bg=CARD)
        tk.Label(
            self.no_transcription_frame,
            text="הכלי רק יחתוך וישמור את קבצי האודיו בתיקייה שבחרת.",
            bg=CARD,
            fg=TEXT,
            font=("Segoe UI", 9),
            wraplength=700,
            justify="left",
        ).pack(anchor="w")

    def build_status_section(self, parent):
        self.action_anchor = tk.Frame(parent, bg=BG, height=1)
        self.action_anchor.pack(fill="x")

        status_card = tk.Frame(parent, bg=PANEL, padx=18, pady=16)
        status_card.pack(fill="x", pady=(0, 18))
        self.progress_bar = ttk.Progressbar(
            status_card,
            variable=self.progress_var,
            maximum=100,
            style="Pink.Horizontal.TProgressbar",
        )
        self.progress_bar.pack(fill="x", pady=(8, 10))

        self.processing_label_var = tk.StringVar(value="")
        self.processing_label = tk.Label(
            status_card,
            textvariable=self.processing_label_var,
            bg=PANEL,
            fg=DARK_PINK,
            font=("Segoe UI", 10, "bold"),
        )
        self.processing_label.pack(anchor="w", pady=(0, 6))

        tk.Label(
            status_card,
            textvariable=self.status_var,
            bg=PANEL,
            fg=TEXT,
            font=("Segoe UI", 10),
            wraplength=720,
            justify="left",
        ).pack(anchor="w", pady=(0, 18))

        action_row = tk.Frame(status_card, bg=PANEL)
        action_row.pack(fill="x")
        self.action_row = action_row

        self.open_folder_button = ttk.Button(
            action_row, text="פתחי תיקיית שמירה", command=self.open_output_folder, style="Compact.TButton"
        )
        self.open_folder_button.pack(side="left", padx=(0, 8))
        self.message_button = ttk.Button(
            action_row, text="הודעה מעצימה", command=self.show_random_message, style="Compact.TButton"
        )
        self.message_button.pack(side="left", padx=10)
        tk.Checkbutton(
            status_card,
            text="להציג הודעות מעצימות אוטומטיות",
            variable=self.empowering_messages_enabled_var,
            command=self.toggle_random_messages,
            bg=PANEL,
            fg=TEXT,
            activebackground=PANEL,
            activeforeground=TEXT,
            selectcolor="#fff6fb",
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w", pady=(12, 0))

    def apply_loaded_text_settings(self):
        if hasattr(self, "times_text"):
            self.times_text.delete("1.0", "end")
            self.times_text.insert("1.0", self.time_ranges_var.get())

    def get_current_api_keys(self):
        if hasattr(self, "external_api_key_entry"):
            raw_text = self.external_api_key_entry.get("1.0", "end")
        else:
            raw_text = self.external_api_key_var.get()
        return parse_api_key_lines(raw_text)

    def set_current_api_keys(self, keys):
        text = "\n".join(parse_api_key_lines("\n".join(keys or [])))
        self.external_api_key_var.set(text)
        if hasattr(self, "external_api_key_entry"):
            self.external_api_key_entry.delete("1.0", "end")
            self.external_api_key_entry.insert("1.0", text)

    def save_current_api_keys(self, silent=False, provider=None):
        provider = provider or get_external_provider_value(self.external_provider_var.get())
        keys = self.get_current_api_keys()
        write_api_keys_for_provider(provider, keys)
        if not silent:
            self.set_status(f"שמרתי {len(keys)} מפתחות API מקומיים עבור הספק הנוכחי.")

    def mark_azure_openai_form_dirty(self):
        self.azure_openai_form_dirty = True

    def on_azure_text_modified(self, _event=None):
        if hasattr(self, "azure_api_key_entry") and self.azure_api_key_entry.edit_modified():
            self.mark_azure_openai_form_dirty()
            self.azure_api_key_entry.edit_modified(False)
        return None

    def get_current_azure_api_keys(self):
        if hasattr(self, "azure_api_key_entry"):
            raw_text = self.azure_api_key_entry.get("1.0", "end")
        else:
            raw_text = self.azure_api_keys_var.get()
        return parse_api_key_lines(raw_text)

    def get_current_azure_openai_configs(self):
        return build_azure_openai_configs_from_values(
            self.get_current_azure_api_keys(),
            self.azure_endpoint_var.get().strip(),
            self.azure_deployment_var.get().strip() or DEFAULT_AZURE_OPENAI_DEPLOYMENT_NAME,
            self.azure_api_version_var.get().strip() or DEFAULT_AZURE_OPENAI_API_VERSION,
        )

    def set_azure_openai_form_configs(self, configs):
        azure_configs = normalize_azure_openai_configs(configs)
        primary = azure_configs[0] if azure_configs else {}
        self.azure_endpoint_var.set(primary.get("azure_endpoint", ""))
        self.azure_deployment_var.set(primary.get("deployment_name", DEFAULT_AZURE_OPENAI_DEPLOYMENT_NAME))
        self.azure_api_version_var.set(primary.get("api_version", DEFAULT_AZURE_OPENAI_API_VERSION))
        key_text = "\n".join(config["api_key"] for config in azure_configs)
        self.azure_api_keys_var.set(key_text)
        if hasattr(self, "azure_api_key_entry"):
            self.azure_api_key_entry.delete("1.0", "end")
            self.azure_api_key_entry.insert("1.0", key_text)
            self.azure_api_key_entry.edit_modified(False)
        self.azure_openai_form_dirty = False

    def save_current_azure_openai_configs(self, silent=False, force=False):
        if not force and not self.azure_openai_form_dirty:
            return
        configs = self.get_current_azure_openai_configs()
        if force and not configs:
            if not silent:
                messagebox.showinfo(
                    "Azure OpenAI",
                    "כדי לשמור Azure צריך למלא endpoint ומפתח API אחד לפחות.",
                )
            return
        write_azure_openai_configs(configs)
        self.azure_openai_form_dirty = False
        if not silent:
            self.set_status(f"שמרתי {len(configs)} הגדרות Azure OpenAI Whisper בקובץ המפתחות.")

    def load_azure_openai_configs_from_file(self):
        configs = read_azure_openai_configs()
        if not configs:
            messagebox.showinfo(
                "Azure OpenAI",
                f"לא מצאתי הגדרות Azure OpenAI תקינות בקובץ:\n{get_api_keys_file_path()}",
            )
            return
        self.set_azure_openai_form_configs(configs)
        self.set_status(f"טענתי {len(configs)} הגדרות Azure OpenAI מהקובץ המקומי.")

    def collect_settings(self):
        time_ranges = self.times_text.get("1.0", "end").strip() if hasattr(self, "times_text") else self.time_ranges_var.get()
        return {
            "save_dir": self.save_dir_var.get().strip(),
            "cut_audio": self.cut_audio_var.get(),
            "split_mode": self.split_mode_var.get(),
            "segments_count": self.segments_var.get().strip(),
            "time_ranges": time_ranges,
            "output_format": self.output_format_var.get().strip(),
            "bitrate": self.bitrate_var.get().strip(),
            "sample_rate": self.sample_rate_var.get().strip(),
            "transcription_mode": self.transcription_mode_var.get(),
            "whatsapp_bot": self.whatsapp_bot_var.get(),
            "transcription_engine": get_transcription_engine_value(self.transcription_engine_var.get()),
            "local_model_label": self.local_model_var.get(),
            "azure_endpoint": self.azure_endpoint_var.get().strip(),
            "azure_deployment_name": self.azure_deployment_var.get().strip(),
            "azure_api_version": self.azure_api_version_var.get().strip(),
            "improve_local_with_gemini": self.improve_local_transcript_with_gemini_var.get(),
            "add_professional_summary": self.add_professional_summary_var.get(),
            "external_provider": get_external_provider_value(self.external_provider_var.get()),
            "external_api_url": self.external_api_url_var.get().strip(),
            "external_model": self.external_model_var.get().strip(),
            "external_text_model": self.external_text_model_var.get().strip(),
            "empowering_messages_enabled": self.empowering_messages_enabled_var.get(),
        }

    def save_current_settings(self):
        try:
            self.save_current_api_keys(silent=True)
            self.save_current_azure_openai_configs(silent=True)
            save_app_settings(self.collect_settings())
        except OSError:
            pass

    def refresh_history_panel(self):
        if not hasattr(self, "history_listbox"):
            return
        self.history_listbox.delete(0, "end")
        for record in self.history_records[:HISTORY_LIMIT]:
            title = record.get("title") or "תמלול"
            timestamp = record.get("timestamp", "")
            self.history_listbox.insert("end", f"{timestamp} | {title}")

    def get_selected_history_record(self):
        if not hasattr(self, "history_listbox"):
            return None
        selection = self.history_listbox.curselection()
        if not selection:
            return None
        index = selection[0]
        if index >= len(self.history_records):
            return None
        return self.history_records[index]

    def open_selected_history_transcript(self):
        record = self.get_selected_history_record()
        if not record:
            messagebox.showinfo("היסטוריה", "בחרי שיחה מהרשימה.")
            return
        transcript_path = record.get("transcript_path")
        if transcript_path and os.path.exists(transcript_path):
            os.startfile(transcript_path)
        else:
            messagebox.showwarning("היסטוריה", "קובץ התמלול כבר לא נמצא במיקום שנשמר.")

    def open_selected_history_folder(self):
        record = self.get_selected_history_record()
        if not record:
            messagebox.showinfo("היסטוריה", "בחרי שיחה מהרשימה.")
            return
        output_dir = record.get("output_dir")
        if output_dir and os.path.isdir(output_dir):
            os.startfile(output_dir)
        else:
            messagebox.showwarning("היסטוריה", "תיקיית השיחה כבר לא נמצאת במיקום שנשמר.")

    def add_history_record(self, output_dir, transcript_path, transcription_mode, audio_count):
        title = Path(output_dir).name
        if transcript_path and os.path.exists(transcript_path):
            title = Path(transcript_path).stem.replace("_", " ")
        record = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M"),
            "title": title,
            "output_dir": output_dir,
            "transcript_path": transcript_path,
            "mode": transcription_mode,
            "audio_count": audio_count,
        }
        self.history_records = [record, *self.history_records]
        unique_records = []
        seen_dirs = set()
        for item in self.history_records:
            item_dir = item.get("output_dir")
            if item_dir in seen_dirs:
                continue
            seen_dirs.add(item_dir)
            unique_records.append(item)
        self.history_records = unique_records[:HISTORY_LIMIT]
        save_transcription_history(self.history_records)
        self.refresh_history_panel()

    def pick_audio_file(self):
        if self.is_processing:
            messagebox.showinfo("קובץ שמע", "אי אפשר להחליף קובץ בזמן שהתוכנה עובדת על פעולה.")
            return
        file_path = filedialog.askopenfilename(
            title="בחרי קובץ שמע",
            filetypes=[("Audio files", "*.mp3 *.wav *.m4a *.aac *.ogg *.flac"), ("All files", "*.*")],
        )
        if file_path:
            self.audio_path_var.set(file_path)
            self.reset_audio_preview(file_path)
            if not self.save_dir_var.get().strip():
                self.save_dir_var.set(str(Path(file_path).parent))
            self.set_status("קובץ נבחר בהצלחה. מוכנה להפעלה 💗")

    def reset_audio_preview(self, file_path: str = ""):
        self.stop_audio_preview(close_player=True)
        self.audio_player_path = ""
        self.player_progress_var.set(0)
        self.update_player_canvas_progress(0)
        self.player_time_var.set("00:00 / 00:00")
        if hasattr(self, "player_time_canvas_item"):
            self.main_canvas.itemconfigure(self.player_time_canvas_item, text=self.player_time_var.get())
        if file_path:
            self.selected_file_label_var.set(Path(file_path).name)
            self.player_status_var.set("אפשר ללחוץ Play כדי לשמוע את הקובץ שנבחר")
        else:
            self.selected_file_label_var.set("")
            self.player_status_var.set("בחרי קובץ כדי להאזין מתוך האפליקציה")
        if hasattr(self, "selected_file_canvas_item"):
            self.main_canvas.itemconfigure(self.selected_file_canvas_item, text=self.selected_file_label_var.get())

    def ensure_audio_preview_loaded(self):
        audio_path = self.audio_path_var.get().strip()
        if not audio_path or not os.path.exists(audio_path):
            raise RuntimeError("בחרי קודם קובץ שמע.")
        if self.audio_player_path == audio_path and self.audio_player.is_open:
            return
        self.audio_player.open(audio_path)
        self.audio_player_path = audio_path

    def toggle_audio_preview(self):
        try:
            self.ensure_audio_preview_loaded()
            mode = self.audio_player.status()
            if mode == "playing":
                self.audio_player.pause()
                if self.player_play_button is not None:
                    self.player_play_button.configure(text="▶")
                self.player_status_var.set("ההשמעה מושהית")
                return
            self.audio_player.play()
            if self.player_play_button is not None:
                self.player_play_button.configure(text="⏸")
            self.player_status_var.set("משמיעה את הקובץ שנבחר")
            self.schedule_audio_player_update()
        except Exception as error:
            self.player_status_var.set("לא הצלחתי להשמיע את הקובץ")
            messagebox.showwarning("נגן אודיו", f"לא הצלחתי להשמיע את הקובץ מתוך האפליקציה.\n\n{error_details(error)}")

    def schedule_audio_player_update(self):
        if self.audio_player_update_job:
            self.root.after_cancel(self.audio_player_update_job)
        self.update_audio_player_progress()

    def update_player_canvas_progress(self, percent: float):
        if hasattr(self, "player_fill_item"):
            self.main_canvas.coords(
                self.player_fill_item,
                self.s(60),
                self.s(729),
                self.s(60) + (self.s(962) * (max(0, min(100, percent)) / 100)),
                self.s(783),
            )

    def update_audio_player_progress(self):
        self.audio_player_update_job = None
        if not self.audio_player.is_open:
            return
        try:
            length = self.audio_player.length()
            position = self.audio_player.position()
            if length > 0:
                percent = max(0, min(100, (position / length) * 100))
                self.player_progress_var.set(percent)
                self.update_player_canvas_progress(percent)
                self.player_time_var.set(f"{format_player_time(position)} / {format_player_time(length)}")
                if hasattr(self, "player_time_canvas_item"):
                    self.main_canvas.itemconfigure(self.player_time_canvas_item, text=self.player_time_var.get())
            mode = self.audio_player.status()
            if mode == "playing":
                self.audio_player_update_job = self.root.after(500, self.update_audio_player_progress)
            else:
                if self.player_play_button is not None:
                    self.player_play_button.configure(text="▶")
                if mode == "stopped" and length > 0 and position >= max(length - 500, 0):
                    self.player_progress_var.set(0)
                    self.update_player_canvas_progress(0)
                    self.player_time_var.set(f"00:00 / {format_player_time(length)}")
                    if hasattr(self, "player_time_canvas_item"):
                        self.main_canvas.itemconfigure(self.player_time_canvas_item, text=self.player_time_var.get())
        except Exception:
            if self.player_play_button is not None:
                self.player_play_button.configure(text="▶")

    def stop_audio_preview(self, close_player: bool = False):
        if self.audio_player_update_job:
            self.root.after_cancel(self.audio_player_update_job)
            self.audio_player_update_job = None
        try:
            if close_player:
                self.audio_player.close()
            else:
                self.audio_player.stop()
        except Exception:
            pass
        if getattr(self, "player_play_button", None) is not None:
            self.player_play_button.configure(text="▶")
        self.player_progress_var.set(0)
        self.update_player_canvas_progress(0)

    def pick_save_dir(self):
        folder = filedialog.askdirectory(title="בחרי תיקיית שמירה")
        if folder:
            self.save_dir_var.set(folder)
            self.set_status("תיקיית השמירה עודכנה 🐾")

    def get_folder_to_open(self):
        if self.last_saved_dir and os.path.isdir(self.last_saved_dir):
            return self.last_saved_dir
        selected_dir = self.save_dir_var.get().strip()
        if selected_dir and os.path.isdir(selected_dir):
            return selected_dir
        return None

    def open_output_folder(self):
        folder = self.get_folder_to_open()
        if not folder:
            messagebox.showinfo("תיקייה", "בחרי קודם תיקיית שמירה או סיימי פעולה אחת כדי לפתוח את התיקייה הנכונה.")
            return
        try:
            os.startfile(folder)
            self.set_status(f"פתחתי את התיקייה: {folder}")
        except OSError:
            messagebox.showwarning("תיקייה", "לא הצלחתי לפתוח את תיקיית השמירה.")

    def toggle_split_mode(self):
        if not self.cut_audio_var.get():
            return
        if self.split_mode_var.get() == "count":
            self.times_frame.pack_forget()
            self.count_frame.pack(fill="x", pady=(0, 8))
        else:
            self.count_frame.pack_forget()
            self.times_frame.pack(fill="x", pady=(0, 8))

    def toggle_cut_controls(self):
        if not hasattr(self, "split_controls_frame"):
            return
        if self.cut_audio_var.get():
            self.split_controls_frame.pack(fill="x")
            self.toggle_split_mode()
        else:
            self.split_controls_frame.pack_forget()
        self.update_scroll_helpers()

    def toggle_encoding_controls(self):
        selected_format = self.output_format_var.get().strip().lower()
        if selected_format == "ogg":
            self.sample_rate_var.set(DEFAULT_OGG_SAMPLE_RATE)
            if self.bitrate_var.get() not in BITRATE_OPTIONS:
                self.bitrate_var.set(DEFAULT_OGG_BITRATE)
            self.bitrate_combo.configure(state="readonly")
            self.sample_rate_combo.configure(state="disabled")
        elif selected_format == "wav":
            self.bitrate_combo.configure(state="disabled")
            self.sample_rate_combo.configure(state="readonly")
        else:
            self.bitrate_combo.configure(state="readonly")
            self.sample_rate_combo.configure(state="readonly")

    def toggle_transcription_settings(self):
        if not hasattr(self, "local_transcription_frame"):
            return

        for frame in (
            self.local_transcription_frame,
            self.external_transcription_frame,
            self.whatsapp_transcription_frame,
            self.no_transcription_frame,
        ):
            frame.pack_forget()

        mode = self.transcription_mode_var.get()
        needs_api_settings = (
            mode == TRANSCRIPTION_EXTERNAL
            or self.improve_local_transcript_with_gemini_var.get()
            or self.add_professional_summary_var.get()
        )

        if mode in {TRANSCRIPTION_LOCAL, TRANSCRIPTION_EXTERNAL}:
            self.local_transcription_frame.pack(fill="x", pady=(8, 0))
            if needs_api_settings:
                self.external_transcription_frame.pack(fill="x", pady=(8, 0))
        elif mode == TRANSCRIPTION_WHATSAPP:
            self.whatsapp_transcription_frame.pack(fill="x", pady=(8, 0))
        elif mode == TRANSCRIPTION_NONE:
            self.no_transcription_frame.pack(fill="x", pady=(8, 0))

        self.toggle_transcription_engine_settings()
        self.update_scroll_helpers()

    def toggle_transcription_engine_settings(self):
        if not hasattr(self, "local_model_combo"):
            return

        engine = get_transcription_engine_value(self.transcription_engine_var.get())
        if engine == TRANSCRIPTION_ENGINE_AZURE_OPENAI:
            self.local_model_combo.configure(state="disabled")
            self.local_model_download_button.configure(state="disabled")
            self.azure_openai_frame.pack(fill="x", pady=(8, 0))
            self.transcription_engine_note_var.set(
                "Azure Cloud Whisper מתמלל בענן במקום המודל המקומי. לפני השליחה הכלי מייצר בתיקייה זמנית "
                "קובץ WAV מונו 16k כדי למנוע בעיות נתיב/Unicode ולשמור על יציבות. תיקון וסיכום API עדיין "
                "מקבלים רק טקסט, לא אודיו."
            )
        else:
            self.azure_openai_frame.pack_forget()
            self.local_model_combo.configure(state="readonly")
            self.local_model_download_button.configure(state="normal")
            self.transcription_engine_note_var.set(
                "התמלול מתחיל במודל המקומי. בפעם הראשונה המודל יורד מהאינטרנט; אחר כך הוא רץ מהמחשב. "
                "תיקון עם API שולח רק את טקסט התמלול, לא את קובץ האודיו."
            )

    def on_external_provider_change(self, initial=False):
        provider = get_external_provider_value(self.external_provider_var.get())
        if hasattr(self, "external_api_key_entry") and not initial:
            self.save_current_api_keys(silent=True, provider=self.active_external_provider_value)

        legacy_audio_url = "https://api.openai.com/v1/audio/transcriptions"
        legacy_audio_model = "whisper-1"
        if provider == EXTERNAL_PROVIDER_GEMINI:
            if self.external_api_url_var.get().strip() in {"", DEFAULT_EXTERNAL_TRANSCRIPTION_URL, DEFAULT_OPENROUTER_CHAT_URL, legacy_audio_url}:
                self.external_api_url_var.set(DEFAULT_GEMINI_TRANSCRIPTION_URL)
            if self.external_model_var.get().strip() in {"", DEFAULT_EXTERNAL_TRANSCRIPTION_MODEL, DEFAULT_OPENROUTER_TEXT_MODEL, legacy_audio_model}:
                self.external_model_var.set(DEFAULT_GEMINI_TRANSCRIPTION_MODEL)
            if self.external_text_model_var.get().strip() in {"", DEFAULT_OPENROUTER_TEXT_MODEL}:
                self.external_text_model_var.set(DEFAULT_GEMINI_TRANSCRIPTION_MODEL)
        elif provider == EXTERNAL_PROVIDER_OPENROUTER:
            if self.external_api_url_var.get().strip() in {"", DEFAULT_EXTERNAL_TRANSCRIPTION_URL, DEFAULT_GEMINI_TRANSCRIPTION_URL, legacy_audio_url}:
                self.external_api_url_var.set(DEFAULT_OPENROUTER_CHAT_URL)
            if self.external_model_var.get().strip() in {"", DEFAULT_EXTERNAL_TRANSCRIPTION_MODEL, DEFAULT_GEMINI_TRANSCRIPTION_MODEL, legacy_audio_model}:
                self.external_model_var.set(DEFAULT_OPENROUTER_TEXT_MODEL)
            if self.external_text_model_var.get().strip() in {"", DEFAULT_GEMINI_TRANSCRIPTION_MODEL}:
                self.external_text_model_var.set(DEFAULT_OPENROUTER_TEXT_MODEL)
        else:
            if self.external_api_url_var.get().strip() in {"", DEFAULT_GEMINI_TRANSCRIPTION_URL, DEFAULT_OPENROUTER_CHAT_URL, legacy_audio_url}:
                self.external_api_url_var.set(DEFAULT_EXTERNAL_TRANSCRIPTION_URL)
            if self.external_model_var.get().strip() in {"", DEFAULT_GEMINI_TRANSCRIPTION_MODEL, DEFAULT_OPENROUTER_TEXT_MODEL, legacy_audio_model}:
                self.external_model_var.set(DEFAULT_EXTERNAL_TRANSCRIPTION_MODEL)
            if not self.external_text_model_var.get().strip():
                self.external_text_model_var.set(DEFAULT_EXTERNAL_TRANSCRIPTION_MODEL)

        if hasattr(self, "external_api_key_entry"):
            self.set_current_api_keys(read_api_keys_for_provider(provider))
        self.active_external_provider_value = provider
        self.update_scroll_helpers()

    def paste_external_api_key(self):
        try:
            clipboard_text = self.root.clipboard_get()
        except tk.TclError:
            clipboard_text = pyperclip.paste()

        clipboard_text = (clipboard_text or "").strip()
        if not clipboard_text:
            messagebox.showinfo("API key", "לא מצאתי טקסט ב-Clipboard להדבקה.")
            return

        self.set_current_api_keys(parse_api_key_lines(clipboard_text))
        self.save_current_api_keys(silent=True)
        self.set_status("הדבקתי ושמרתי את מפתחות ה-API מה-Clipboard עבור הספק הנוכחי.")

    def paste_external_api_key_event(self, _event=None):
        self.paste_external_api_key()
        return "break"

    def load_api_key_from_file(self):
        provider = get_external_provider_value(self.external_provider_var.get())
        keys = read_api_keys_for_provider(provider)
        if not keys:
            messagebox.showinfo(
                "API keys",
                f"לא מצאתי מפתחות תקינים עבור הספק הנוכחי בקובץ:\n{get_api_keys_file_path()}",
            )
            return
        self.set_current_api_keys(keys)
        self.set_status(f"טענתי {len(keys)} מפתחות API מהקובץ המקומי.")

    def open_api_key_file(self):
        key_path = ensure_api_keys_file_exists()
        try:
            os.startfile(key_path)
            self.set_status(f"פתחתי את קובץ המפתחות: {key_path}")
        except OSError:
            messagebox.showwarning("API keys", f"לא הצלחתי לפתוח את קובץ המפתחות:\n{key_path}")

    def show_api_key_context_menu(self, event):
        menu = tk.Menu(self.root, tearoff=False)
        menu.add_command(label="הדבק API keys", command=self.paste_external_api_key)
        menu.add_command(label="טען API keys מקובץ", command=self.load_api_key_from_file)
        menu.add_command(label="שמור API keys", command=lambda: self.save_current_api_keys(silent=False))
        menu.tk_popup(event.x_root, event.y_root)
        menu.grab_release()
        return "break"

    def set_status(self, text):
        self.status_var.set(text)
        if hasattr(self, "status_canvas_item"):
            self.main_canvas.itemconfigure(self.status_canvas_item, text=text)
        self.root.update_idletasks()
        self.update_scroll_helpers()

    def set_progress(self, value):
        percent = max(0, min(100, value))
        self.progress_var.set(percent)
        if hasattr(self, "progress_canvas_item"):
            self.main_canvas.coords(
                self.progress_canvas_item,
                self.s(80),
                self.s(1872),
                self.s(80) + (self.s(920) * (percent / 100)),
                self.s(1888),
            )
        self.root.update_idletasks()

    def on_content_configure(self, _event=None):
        self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        self.update_scroll_helpers()

    def on_canvas_configure(self, event):
        if self.canvas_window_id:
            self.main_canvas.itemconfigure(self.canvas_window_id, width=event.width)
        self.update_scroll_helpers()

    def on_mousewheel(self, event):
        if self.main_canvas.winfo_exists():
            self.main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            self.update_scroll_helpers()

    def update_scroll_helpers(self):
        if not hasattr(self, "main_canvas") or not self.main_canvas.winfo_exists():
            return
        if hasattr(self, "menu_image_item"):
            if hasattr(self, "quick_scroll_button"):
                self.quick_scroll_button.place_forget()
            return
        self.root.update_idletasks()
        bbox = self.main_canvas.bbox("all")
        if not bbox:
            return
        content_height = bbox[3] - bbox[1]
        canvas_height = self.main_canvas.winfo_height()
        needs_scroll = content_height > canvas_height + 40
        if needs_scroll:
            self.quick_scroll_button.place(relx=0.985, rely=0.5, anchor="e")
        else:
            self.quick_scroll_button.place_forget()

    def _widget_y_in_content(self, widget):
        y = 0
        current = widget
        while current and current is not self.main_canvas:
            y += current.winfo_y()
            current = current.master
            if current is self.main_canvas:
                break
        return y

    def scroll_to_actions(self):
        if hasattr(self, "transcribe_button") and self.transcribe_button is self.main_canvas:
            bbox = self.main_canvas.bbox("all")
            if bbox:
                content_height = max(bbox[3] - bbox[1], 1)
                canvas_height = max(self.main_canvas.winfo_height(), 1)
                max_scroll = max(content_height - canvas_height, 1)
                self.main_canvas.yview_moveto(max(0.0, min(self.s(1356) / max_scroll, 1.0)))
            return
        if not hasattr(self, "action_row"):
            return
        self.root.update_idletasks()
        bbox = self.main_canvas.bbox("all")
        if not bbox:
            return
        content_height = bbox[3] - bbox[1]
        canvas_height = self.main_canvas.winfo_height()
        max_scroll = max(content_height - canvas_height, 1)
        target_y = self._widget_y_in_content(self.action_row)
        self.main_canvas.yview_moveto(max(0.0, min(target_y / max_scroll, 1.0)))
        self.update_scroll_helpers()

    def set_processing_state(self, is_processing: bool):
        self.is_processing = is_processing
        new_state = "disabled" if is_processing else "normal"
        for button_name in (
            "cut_button",
            "transcribe_button",
            "cut_audio_button",
            "upload_action_button",
            "message_button",
        ):
            button = getattr(self, button_name, None)
            if button is not None:
                try:
                    button.configure(state=new_state)
                except tk.TclError:
                    pass
        if is_processing:
            if hasattr(self, "progress_bar"):
                self.progress_bar.configure(mode="indeterminate")
                self.progress_bar.start(10)
            self.processing_status_suffix = ""
            self.processing_animation_index = 0
            self.animate_processing_label()
        else:
            if self.processing_animation_job:
                self.root.after_cancel(self.processing_animation_job)
                self.processing_animation_job = None
            if hasattr(self, "progress_bar"):
                self.progress_bar.stop()
                self.progress_bar.configure(mode="determinate")
            self.processing_label_var.set("")

    def animate_processing_label(self):
        if not self.is_processing:
            self.processing_label_var.set("")
            self.processing_animation_job = None
            return
        frame = self.processing_animation_frames[self.processing_animation_index % len(self.processing_animation_frames)]
        self.processing_label_var.set(f"{frame}{self.processing_status_suffix}".strip())
        self.processing_animation_index += 1
        self.processing_animation_job = self.root.after(220, self.animate_processing_label)

    def set_processing_hint(self, text=""):
        self.processing_status_suffix = f" | {text}" if text else ""

    def open_github_page(self):
        try:
            os.startfile(UPDATE_REPO_URL)
        except OSError:
            messagebox.showwarning("GitHub", f"לא הצלחתי לפתוח את עמוד GitHub:\n{UPDATE_REPO_URL}")

    def start_software_update(self):
        if self.is_processing:
            messagebox.showinfo("עדכון תוכנה", "אי אפשר לעדכן בזמן שהכלי עובד על קובץ. חכי לסיום הפעולה ואז נסי שוב.")
            return
        should_update = messagebox.askyesno(
            "עדכון תוכנה",
            "הכלי יבדוק עדכון מ-GitHub ויעדכן רק את קבצי התוכנה.\n"
            "מפתחות API, היסטוריה, הגדרות וקבצי שמע לא יימחקו.\n\n"
            "להמשיך?",
        )
        if not should_update:
            return

        self.set_progress(0)
        self.set_processing_state(True)
        self.set_processing_hint("בודקת עדכונים")
        self.set_status("בודקת עדכון תוכנה מ-GitHub...")
        worker = threading.Thread(target=self.software_update_worker, daemon=True)
        worker.start()

    def software_update_worker(self):
        def report(label):
            self.root.after(
                0,
                lambda label=label: (
                    self.set_processing_hint(label),
                    self.set_status(label),
                ),
            )

        try:
            update_message = update_application_from_github(report)
            self.root.after(0, lambda update_message=update_message: self.finish_software_update(update_message))
        except Exception as error:
            error_message = error_details(error)
            self.root.after(0, lambda error_message=error_message: self.fail_software_update(error_message))

    def finish_software_update(self, update_message: str):
        self.set_processing_state(False)
        self.set_progress(100)
        self.set_status(update_message)
        if "כבר מותקנת" in update_message:
            messagebox.showinfo("עדכון תוכנה", update_message)
            return
        restart_now = messagebox.askyesno(
            "עדכון תוכנה",
            f"{update_message}\n\nלהפעיל מחדש עכשיו?",
        )
        if restart_now:
            self.restart_application()

    def fail_software_update(self, error_message: str):
        self.set_processing_state(False)
        self.set_progress(0)
        self.set_status("עדכון התוכנה לא הושלם.")
        messagebox.showerror(
            "עדכון תוכנה",
            "לא הצלחתי להשלים את העדכון מ-GitHub.\n\n"
            f"פרטים:\n{error_message}",
        )

    def restart_application(self):
        project_root = get_app_config_dir()
        launcher_path = os.path.join(project_root, "open_cat_audio_cutter.bat")
        try:
            if os.path.exists(launcher_path):
                subprocess.Popen(
                    ["cmd", "/c", "start", "", launcher_path],
                    cwd=project_root,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                )
            else:
                subprocess.Popen(
                    [sys.executable, os.path.abspath(__file__)],
                    cwd=project_root,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                )
            self.on_close()
        except Exception as error:
            messagebox.showwarning("עדכון תוכנה", f"העדכון הושלם, אבל ההפעלה מחדש לא הצליחה:\n{error_details(error)}")

    def start_model_download(self):
        if self.is_processing:
            messagebox.showinfo("מודל תמלול", "אי אפשר לבדוק/להוריד מודל בזמן שהכלי עובד על פעולה אחרת.")
            return

        model_name = get_local_model_name(self.local_model_var.get())
        self.set_progress(0)
        self.set_processing_state(True)
        self.set_processing_hint("בודקת מודל מקומי")
        self.set_status("בודקת אם מודל התמלול המקומי כבר קיים במחשב...")
        worker = threading.Thread(target=self.model_download_worker, args=(model_name,), daemon=True)
        worker.start()

    def model_download_worker(self, model_name: str):
        def report(label, percent=None):
            self.root.after(
                0,
                lambda label=label, percent=percent: (
                    self.set_processing_hint(label),
                    self.set_status(label),
                    self.set_progress(percent if percent is not None else self.progress_var.get()),
                ),
            )

        try:
            model_path = ensure_faster_whisper_model(model_name, report)
            self.root.after(0, lambda model_path=model_path: self.finish_model_download(model_path))
        except Exception as error:
            error_message = error_details(error)
            self.root.after(0, lambda error_message=error_message: self.fail_model_download(error_message))

    def finish_model_download(self, model_path: str):
        self.set_processing_state(False)
        self.set_progress(100)
        self.set_status("מודל התמלול המקומי מוכן במחשב ואפשר להתחיל תמלול.")
        messagebox.showinfo(
            "מודל תמלול מוכן",
            "מודל התמלול המקומי נמצא ומוכן לשימוש.\n\n"
            f"מיקום במחשב:\n{model_path}",
        )

    def fail_model_download(self, error_message: str):
        self.set_processing_state(False)
        self.set_progress(0)
        self.set_status("מודל התמלול המקומי עדיין לא מוכן.")
        messagebox.showerror(
            "מודל תמלול",
            "לא הצלחתי להכין את מודל התמלול המקומי.\n\n"
            f"פרטים:\n{error_message}",
        )

    def build_target_output_dir(self):
        base_dir = self.save_dir_var.get().strip()
        if not base_dir:
            raise ValueError("בחרי תיקיית שמירה לפני ההפעלה.")
        if not os.path.isdir(base_dir):
            raise ValueError("תיקיית השמירה שנבחרה לא קיימת.")

        target_dir = os.path.join(base_dir, f"cat_audio_result_{time.strftime('%Y%m%d_%H%M%S')}")
        os.makedirs(target_dir, exist_ok=False)
        return target_dir

    def validate_inputs(self, overrides=None):
        overrides = overrides or {}
        audio_path = self.audio_path_var.get().strip()
        if not audio_path or not os.path.exists(audio_path):
            raise ValueError("בחרי קודם קובץ שמע תקין.")

        cut_audio = overrides.get("cut_audio", self.cut_audio_var.get())
        split_mode = overrides.get("split_mode", self.split_mode_var.get())
        segments_count = 0
        ranges_text = ""

        if not cut_audio:
            segments_count = 1
        elif split_mode == "count":
            try:
                segments_count = int(str(overrides.get("segments_count", self.segments_var.get().strip())).strip())
            except ValueError as error:
                raise ValueError("כתבי מספר שלם כמו 2 או 10.") from error
        else:
            ranges_text = overrides.get("ranges_text", self.times_text.get("1.0", "end").strip())
            self.time_ranges_var.set(ranges_text)

        output_format = str(overrides.get("output_format", self.output_format_var.get().strip())).strip().lower()
        if output_format not in {"mp3", "wav", "ogg"}:
            raise ValueError("בחרי פורמט פלט תקין.")

        bitrate = str(overrides.get("bitrate", self.bitrate_var.get().strip())).strip()
        if output_format in {"mp3", "ogg"} and bitrate not in BITRATE_OPTIONS:
            raise ValueError("בחרי קצב סיביות תקין.")

        sample_rate = str(overrides.get("sample_rate", self.sample_rate_var.get().strip())).strip()
        if sample_rate not in SAMPLE_RATE_OPTIONS:
            raise ValueError("בחרי קצב דגימה תקין.")
        if output_format == "ogg":
            sample_rate = DEFAULT_OGG_SAMPLE_RATE

        transcription_mode = overrides.get("transcription_mode", self.transcription_mode_var.get())
        if transcription_mode not in {TRANSCRIPTION_LOCAL, TRANSCRIPTION_EXTERNAL, TRANSCRIPTION_WHATSAPP, TRANSCRIPTION_NONE}:
            raise ValueError("בחרי מצב תמלול תקין.")
        whatsapp_bot_option = overrides.get("whatsapp_bot", self.whatsapp_bot_var.get())
        if whatsapp_bot_option not in WHATSAPP_BOT_OPTIONS:
            raise ValueError("בחרי בוט WhatsApp תקין.")
        whatsapp_bot_config = get_whatsapp_bot_config(whatsapp_bot_option)

        transcription_engine = overrides.get(
            "transcription_engine",
            get_transcription_engine_value(self.transcription_engine_var.get()),
        )
        if transcription_engine not in {TRANSCRIPTION_ENGINE_LOCAL, TRANSCRIPTION_ENGINE_AZURE_OPENAI}:
            raise ValueError("בחרי מנוע תמלול תקין.")

        local_model_name = get_local_model_name(self.local_model_var.get())
        azure_openai_configs = []
        if transcription_mode in {TRANSCRIPTION_LOCAL, TRANSCRIPTION_EXTERNAL} and transcription_engine == TRANSCRIPTION_ENGINE_AZURE_OPENAI:
            azure_openai_configs = (
                self.get_current_azure_openai_configs()
                if self.azure_openai_form_dirty
                else read_azure_openai_configs()
            )
            if not azure_openai_configs:
                azure_openai_configs = self.get_current_azure_openai_configs()
            if not azure_openai_configs:
                raise ValueError(
                    "בחרת Azure Cloud Whisper, אבל לא נמצאו הגדרות Azure OpenAI תקינות.\n\n"
                    "מלאי בממשק את Azure endpoint, Deployment, API version ומפתח אחד לפחות, "
                    f"או הוסיפי בלוק azure_openai בקובץ:\n{get_api_keys_file_path()}"
                )

        external_provider = get_external_provider_value(self.external_provider_var.get())
        external_api_url = self.external_api_url_var.get().strip()
        external_model = self.external_model_var.get().strip()
        external_text_model = self.external_text_model_var.get().strip()
        external_api_keys = self.get_current_api_keys() or read_api_keys_for_provider(external_provider)
        improve_local_with_gemini = self.improve_local_transcript_with_gemini_var.get()
        add_professional_summary = self.add_professional_summary_var.get()

        if "/audio/transcriptions" in external_api_url:
            if external_provider == EXTERNAL_PROVIDER_OPENROUTER:
                external_api_url = DEFAULT_OPENROUTER_CHAT_URL
                self.external_api_url_var.set(external_api_url)
            elif external_provider == EXTERNAL_PROVIDER_OPENAI:
                external_api_url = DEFAULT_EXTERNAL_TRANSCRIPTION_URL
                self.external_api_url_var.set(external_api_url)

        if external_provider in {EXTERNAL_PROVIDER_OPENAI, EXTERNAL_PROVIDER_GEMINI, EXTERNAL_PROVIDER_OPENROUTER}:
            if external_provider == EXTERNAL_PROVIDER_OPENAI and not external_api_keys:
                legacy_gemini_keys = read_api_keys_for_provider(EXTERNAL_PROVIDER_GEMINI)
                text_provider = EXTERNAL_PROVIDER_GEMINI
                text_endpoint_url = DEFAULT_GEMINI_TRANSCRIPTION_URL
                text_api_keys = legacy_gemini_keys
                text_model = DEFAULT_GEMINI_TRANSCRIPTION_MODEL
            else:
                text_provider = external_provider
                text_endpoint_url = external_api_url
                text_api_keys = external_api_keys
                text_model = external_text_model or external_model
        else:
            text_provider = EXTERNAL_PROVIDER_GEMINI
            text_endpoint_url = DEFAULT_GEMINI_TRANSCRIPTION_URL
            text_api_keys = read_api_keys_for_provider(EXTERNAL_PROVIDER_GEMINI)
            text_model = DEFAULT_GEMINI_TRANSCRIPTION_MODEL

        needs_text_api = (
            transcription_mode == TRANSCRIPTION_EXTERNAL
            or (transcription_mode == TRANSCRIPTION_LOCAL and improve_local_with_gemini)
            or (transcription_mode in {TRANSCRIPTION_LOCAL, TRANSCRIPTION_EXTERNAL} and add_professional_summary)
        )

        if needs_text_api and not text_api_keys:
            raise ValueError("כדי לתקן או לסכם את התמלול צריך לפחות API key אחד עבור ספק הטקסט שנבחר.")

        if transcription_mode == TRANSCRIPTION_EXTERNAL:
            if external_provider not in {EXTERNAL_PROVIDER_OPENAI, EXTERNAL_PROVIDER_GEMINI, EXTERNAL_PROVIDER_OPENROUTER}:
                raise ValueError("בחרי ספק API חיצוני תקין.")
            if not external_api_url:
                raise ValueError("במצב תיקון API צריך כתובת API לטקסט.")
            if not text_model:
                raise ValueError("במצב תיקון API צריך שם מודל טקסט.")

        output_dir = self.build_target_output_dir()

        return {
            "audio_path": audio_path,
            "cut_audio": cut_audio,
            "split_mode": split_mode,
            "segments_count": segments_count,
            "ranges_text": ranges_text,
            "output_format": output_format,
            "bitrate": bitrate,
            "sample_rate": sample_rate,
            "output_dir": output_dir,
            "transcription_mode": transcription_mode,
            "whatsapp_bot": whatsapp_bot_option,
            "whatsapp_bot_config": whatsapp_bot_config,
            "transcription_engine": transcription_engine,
            "local_model_name": local_model_name,
            "azure_openai_configs": azure_openai_configs,
            "improve_local_with_gemini": improve_local_with_gemini,
            "add_professional_summary": add_professional_summary,
            "external_provider": external_provider,
            "external_api_url": external_api_url,
            "external_model": external_model,
            "external_text_model": external_text_model,
            "external_api_keys": external_api_keys,
            "text_provider": text_provider,
            "text_endpoint_url": text_endpoint_url,
            "text_model": text_model,
            "text_api_keys": text_api_keys,
        }

    def start_transcribe_audio_now(self):
        self.start_processing()

    def start_cut_audio_only(self):
        if self.is_processing:
            return
        if not self.audio_path_var.get().strip():
            self.pick_audio_file()
        if not self.audio_path_var.get().strip():
            return
        parts_count = simpledialog.askinteger(
            "חיתוך אודיו",
            "לכמה חלקים לחתוך את הקובץ?",
            initialvalue=max(2, int(self.segments_var.get() or 2) if str(self.segments_var.get()).isdigit() else 2),
            minvalue=2,
            maxvalue=200,
            parent=self.root,
        )
        if not parts_count:
            return
        self.start_processing(
            overrides={
                "cut_audio": True,
                "split_mode": "count",
                "segments_count": parts_count,
                "transcription_mode": TRANSCRIPTION_NONE,
            },
            save_settings=False,
        )

    def start_processing(self, overrides=None, save_settings=True):
        if self.is_processing:
            return
        try:
            settings = self.validate_inputs(overrides)
        except Exception as error:
            messagebox.showerror("בדקי את ההגדרות", str(error))
            return

        if save_settings:
            self.save_current_settings()
        self.cleanup_temp_dir()
        self.temp_dir = tempfile.mkdtemp(prefix="cat_audio_cutter_")
        self.last_saved_dir = settings["output_dir"]
        self.last_output_files = []
        self.last_transcript_text = ""
        self.last_transcript_path = None
        self.set_progress(0)
        self.set_processing_state(True)
        self.set_processing_hint("מכינה את הקובץ")
        self.set_status("מתחילה לעבד את קובץ השמע...")

        worker = threading.Thread(target=self.process_audio_worker, args=(settings,), daemon=True)
        worker.start()

    def process_audio_worker(self, settings):
        generated_files = []
        copied_files = []

        try:
            if settings["cut_audio"]:
                segment_plan = build_segment_plan(
                    settings["split_mode"],
                    settings["audio_path"],
                    settings["segments_count"],
                    settings["ranges_text"],
                )

                self.root.after(
                    0,
                    lambda: (
                        self.set_processing_hint(f"{len(segment_plan)} מקטעים בפורמט {settings['output_format'].upper()}"),
                        self.set_status(f"מכינה {len(segment_plan)} מקטעים לשמירה בפורמט {settings['output_format'].upper()}..."),
                    ),
                )

                split_paths = split_audio_file(
                    settings["audio_path"],
                    segment_plan,
                    self.temp_dir,
                    settings["output_format"],
                    settings["bitrate"],
                    settings["sample_rate"],
                    lambda current, total: self.root.after(
                        0,
                        lambda current=current, total=total: (
                            self.set_processing_hint(f"מקטע {current}/{total}"),
                            self.set_progress((current / max(total, 1)) * 55),
                            self.set_status(f"חתכתי {current} מתוך {total} מקטעים..."),
                        ),
                    ),
                )
            else:
                self.root.after(
                    0,
                    lambda: (
                        self.set_processing_hint("ללא חיתוך"),
                        self.set_status("שומרת עותק אחד של הקובץ ומתמללת אותו כיחידה אחת..."),
                    ),
                )
                split_paths = export_full_audio_file(
                    settings["audio_path"],
                    self.temp_dir,
                    settings["output_format"],
                    settings["bitrate"],
                    settings["sample_rate"],
                    lambda current, total: self.root.after(
                        0,
                        lambda current=current, total=total: (
                            self.set_processing_hint("קובץ מלא"),
                            self.set_progress(55),
                            self.set_status("הקובץ המלא מוכן לשמירה ולתמלול."),
                        ),
                    ),
                )
            generated_files.extend(split_paths)

            self.root.after(
                0,
                lambda: (
                    self.set_processing_hint("שומרת את הקבצים"),
                    self.set_status("שומרת את הקבצים לתיקייה שבחרת..."),
                ),
            )
            copied_files = copy_results_to_folder(generated_files, settings["output_dir"])
            audio_files = [path for path in copied_files if Path(path).suffix.lower() in AUDIO_EXTENSIONS]
            if not audio_files:
                raise RuntimeError("הפעולה הסתיימה בלי שנוצרו קבצי שמע בתיקיית היעד.")

            transcript_text = ""
            transcript_path = None
            whatsapp_format_used = ""
            transcription_mode = settings["transcription_mode"]

            if transcription_mode in {TRANSCRIPTION_LOCAL, TRANSCRIPTION_EXTERNAL}:
                transcription_engine = settings.get("transcription_engine", TRANSCRIPTION_ENGINE_LOCAL)
                if transcription_engine == TRANSCRIPTION_ENGINE_AZURE_OPENAI:
                    self.root.after(
                        0,
                        lambda: (
                            self.set_processing_hint("מכינה Azure Whisper"),
                            self.set_status("מכינה WAV זמני מונו 16k ושולחת את המקטעים ל-Azure Cloud Whisper..."),
                            self.set_progress(62),
                        ),
                    )
                    transcript_files, transcript_text, transcript_path = transcribe_audio_files_with_azure_whisper(
                        split_paths,
                        settings["output_dir"],
                        settings["azure_openai_configs"],
                        lambda current, total, label: self.root.after(
                            0,
                            lambda current=current, total=total, label=label: (
                                self.set_processing_hint(label),
                                self.set_progress(72 + (current / max(total, 1)) * 23),
                                self.set_status(f"מתמללת מקטע {current} מתוך {total} דרך Azure Whisper..."),
                            ),
                        ),
                        self.temp_dir,
                    )
                else:
                    self.root.after(
                        0,
                        lambda: (
                            self.set_processing_hint("טוענת מודל תמלול מקומי"),
                            self.set_status("מתמללת בעברית על המחשב. אחר כך, אם נבחר API, רק הטקסט יישלח לתיקון..."),
                            self.set_progress(62),
                        ),
                    )
                    transcript_files, transcript_text, transcript_path = transcribe_audio_files_locally(
                        split_paths,
                        settings["output_dir"],
                        settings["local_model_name"],
                        lambda current, total, label: self.root.after(
                            0,
                            lambda current=current, total=total, label=label: (
                                self.set_processing_hint(label),
                                self.set_progress(78 + (current / max(total, 1)) * 17),
                                self.set_status(f"מתמללת מקטע {current} מתוך {total} בעברית..."),
                            ),
                        ),
                        lambda label, percent=None: self.root.after(
                            0,
                            lambda label=label, percent=percent: (
                                self.set_processing_hint(label),
                                self.set_progress(58 + ((percent or 0) / 100) * 20),
                                self.set_status(label),
                            ),
                        ),
                        self.temp_dir,
                    )
                copied_files.extend(transcript_files)
                should_improve_text = (
                    transcription_mode == TRANSCRIPTION_EXTERNAL
                    or settings["improve_local_with_gemini"]
                )
                if should_improve_text:
                    self.root.after(
                        0,
                        lambda: (
                            self.set_processing_hint("מתקן את הטקסט"),
                            self.set_status("התמלול נשמר. ספק ה-AI מקבל עכשיו רק טקסט ומתקן ג'יבריש, תחביר ופיסוק..."),
                            self.set_progress(96),
                        ),
                    )
                    try:
                        corrected_text = correct_transcript_text_with_ai_provider(
                            transcript_text,
                            settings["text_provider"],
                            settings["text_endpoint_url"],
                            settings["text_model"],
                            settings["text_api_keys"],
                            lambda label: self.root.after(
                                0,
                                lambda label=label: (
                                    self.set_processing_hint(label),
                                    self.set_status(label),
                                ),
                            ),
                        )
                        if corrected_text.strip():
                            fixed_path = write_gemini_fixed_transcript(settings["output_dir"], corrected_text)
                            copied_files.append(fixed_path)
                            transcript_text = corrected_text
                            transcript_path = fixed_path
                    except Exception as error:
                        warning_path = os.path.join(settings["output_dir"], "text_fix_error.txt")
                        with open(warning_path, "w", encoding="utf-8") as handle:
                            handle.write(
                                "התמלול המקומי הצליח, אבל תיקון הטקסט דרך ספק ה-AI לא הושלם.\n\n"
                                f"פרטים:\n{error_details(error)}\n"
                            )
                        copied_files.append(warning_path)
            elif transcription_mode == TRANSCRIPTION_WHATSAPP:
                whatsapp_bot_label = settings["whatsapp_bot_config"]["label"]
                self.root.after(
                    0,
                    lambda whatsapp_bot_label=whatsapp_bot_label: (
                        self.set_processing_hint("מדביקה ב-WhatsApp"),
                        self.set_status(f"מכינה MP3, פותחת את הבוט {whatsapp_bot_label} ומדביקה בשורת ההודעה..."),
                        self.set_progress(90),
                    ),
                )
                whatsapp_format_used = send_audio_files_to_whatsapp_bot(
                    audio_files,
                    self.temp_dir,
                    settings["whatsapp_bot_config"],
                )

            if (
                settings["add_professional_summary"]
                and transcript_path
                and transcript_text.strip()
                and transcription_mode in {TRANSCRIPTION_LOCAL, TRANSCRIPTION_EXTERNAL}
            ):
                self.root.after(
                    0,
                    lambda: (
                        self.set_processing_hint("מכין סיכום מקצועי"),
                        self.set_status("מוסיף סיכום מקצועי בתחילת קובץ התמלול..."),
                        self.set_progress(98),
                    ),
                )
                try:
                    summary_text = summarize_transcript_with_ai_provider(
                        transcript_text,
                        settings["text_provider"],
                        settings["text_endpoint_url"],
                        settings["text_model"],
                        settings["text_api_keys"],
                        lambda label: self.root.after(
                            0,
                            lambda label=label: (
                                self.set_processing_hint(label),
                                self.set_status(label),
                            ),
                        ),
                    )
                    if summary_text.strip():
                        summary_path, transcript_path = write_summary_transcript(
                            settings["output_dir"],
                            transcript_path,
                            summary_text,
                            transcript_text,
                        )
                        transcript_text = format_transcript_with_summary(summary_text, transcript_text)
                        copied_files.append(summary_path)
                        if transcript_path not in copied_files:
                            copied_files.append(transcript_path)
                except Exception as error:
                    summary_error_path = os.path.join(settings["output_dir"], "summary_error.txt")
                    with open(summary_error_path, "w", encoding="utf-8") as handle:
                        handle.write(
                            "התמלול הצליח, אבל הסיכום דרך ספק ה-AI לא הושלם.\n\n"
                            f"פרטים:\n{error_details(error)}\n"
                        )
                    copied_files.append(summary_error_path)

            self.root.after(
                0,
                lambda: self.finish_processing(
                    copied_files,
                    settings["output_dir"],
                    transcription_mode,
                    transcript_text,
                    transcript_path,
                    settings.get("whatsapp_bot_config"),
                    whatsapp_format_used,
                ),
            )
        except Exception as error:
            error_message = str(error)
            output_dir = settings.get("output_dir")
            has_saved_audio = bool(
                copied_files
                and any(Path(path).suffix.lower() in AUDIO_EXTENSIONS and os.path.exists(path) for path in copied_files)
            )

            self.root.after(
                0,
                lambda error_message=error_message, output_dir=output_dir, has_saved_audio=has_saved_audio: (
                    self.set_processing_state(False),
                    self.set_progress(100 if has_saved_audio else 0),
                    self.set_status(
                        "קבצי השמע נשמרו, אבל התמלול לא הושלם."
                        if has_saved_audio
                        else "קרה משהו בדרך, אבל אני כאן איתך."
                    ),
                    messagebox.showerror(
                        "שגיאה",
                        (
                            f"{error_message}\n\n"
                            f"קבצי האודיו נשמרו כאן:\n{output_dir}"
                            if has_saved_audio and output_dir
                            else error_message
                        ),
                    ),
                ),
            )
            if has_saved_audio and output_dir:
                self.last_saved_dir = output_dir
                self.last_output_files = copied_files
            elif output_dir and os.path.isdir(output_dir):
                shutil.rmtree(output_dir, ignore_errors=True)

    def finish_processing(
        self,
        copied_files,
        output_dir,
        transcription_mode,
        transcript_text="",
        transcript_path=None,
        whatsapp_bot_config=None,
        whatsapp_format_used="",
    ):
        self.last_saved_dir = output_dir
        self.last_output_files = copied_files
        self.last_transcript_text = transcript_text or ""
        self.last_transcript_path = transcript_path
        self.set_processing_state(False)
        self.set_progress(100)
        audio_files = [path for path in copied_files if Path(path).suffix.lower() in AUDIO_EXTENSIONS]
        if transcription_mode == TRANSCRIPTION_WHATSAPP:
            bot_label = (whatsapp_bot_config or {}).get("label", "הבוט שנבחר")
            format_label = whatsapp_format_used.upper() if whatsapp_format_used else "קובץ שמע"
            self.set_status(
                f"קובצי {format_label} הודבקו אצל הבוט {bot_label}. לחצי Enter בחלון WhatsApp כדי לשלוח."
            )
            self.save_current_settings()
            return

        transcript_note = " והתמלול נשמר כקובץ TXT" if transcript_path else ""
        self.set_status(f"הפעולה הסתיימה ונשמרו {len(audio_files)} קבצי שמע{transcript_note}. 🐱💗")

        message_lines = [
            "הפעולה הושלמה בהצלחה.",
            "",
            f"נשמרו {len(audio_files)} קבצי שמע כאן:",
            output_dir,
        ]
        if transcript_path:
            message_lines.extend(["", "התמלול נשמר כאן:", transcript_path])
        messagebox.showinfo(
            "הפעולה הסתיימה",
            "\n".join(message_lines).strip(),
        )

        if transcript_path:
            self.add_history_record(output_dir, transcript_path, transcription_mode, len(audio_files))
        self.save_current_settings()

        dialog = ResultDialog(
            self.root,
            output_dir,
            transcript_path,
            allow_whatsapp_fallback=transcription_mode == TRANSCRIPTION_WHATSAPP,
        )
        self.root.wait_window(dialog)

        if dialog.result == "open_folder":
            try:
                os.startfile(output_dir)
            except OSError:
                messagebox.showwarning("תיקייה", "לא הצלחתי לפתוח את תיקיית השמירה.")
        elif dialog.result == "open_transcript" and transcript_path:
            try:
                os.startfile(transcript_path)
            except OSError:
                messagebox.showwarning("תמלול", "לא הצלחתי לפתוח את קובץ התמלול.")
        elif dialog.result == "whatsapp_bot":
            audio_files = [path for path in copied_files if Path(path).suffix.lower() in AUDIO_EXTENSIONS]
            try:
                bot_config = get_whatsapp_bot_config(self.whatsapp_bot_var.get())
                self.set_status(f"מכינה MP3 ופותחת את בוט התמלול ב-WhatsApp ({bot_config['label']})...")
                format_used = send_audio_files_to_whatsapp_bot(audio_files, self.temp_dir, bot_config)
                self.set_status(
                    f"קובצי {format_used.upper()} הודבקו ב-WhatsApp. לחצי Enter בחלון WhatsApp כדי לשלוח."
                )
            except Exception as error:
                messagebox.showwarning(
                    "WhatsApp",
                    "ניסיתי לפתוח את בוט התמלול ב-WhatsApp, אבל האוטומציה לא הושלמה עד הסוף.\n\n"
                    f"פרטים:\n{error}\n\n"
                    "הקבצים כבר שמורים אצלך בתיקייה וניתן לשלוח ידנית.",
                )
        elif dialog.result == "whatsapp_ogg":
            audio_files = [path for path in copied_files if Path(path).suffix.lower() in AUDIO_EXTENSIONS]
            try:
                bot_config = whatsapp_bot_config or get_whatsapp_bot_config(self.whatsapp_bot_var.get())
                self.set_status(f"מכינה OGG ושולחת שוב לבוט {bot_config['label']}...")
                send_audio_files_to_whatsapp_bot_as_format(
                    audio_files,
                    self.temp_dir,
                    bot_config,
                    WHATSAPP_FALLBACK_FORMAT,
                )
                self.set_status("קובצי OGG/Opus הודבקו ב-WhatsApp. לחצי Enter כדי לשלוח.")
            except Exception as error:
                messagebox.showwarning(
                    "WhatsApp",
                    "לא הצלחתי לבצע את השליחה החוזרת כ-OGG.\n\n"
                    f"פרטים:\n{error}\n\n"
                    "הקבצים המקוריים עדיין שמורים בתיקייה.",
                )

    def schedule_random_message(self, initial_delay=False):
        if not self.empowering_messages_enabled_var.get():
            return
        if self.random_message_job:
            self.root.after_cancel(self.random_message_job)
        delay = random.randint(14000, 24000) if initial_delay else random.randint(25000, 45000)
        self.random_message_job = self.root.after(delay, self.random_message_tick)

    def random_message_tick(self):
        if not self.empowering_messages_enabled_var.get():
            self.random_message_job = None
            return
        self.show_random_message()
        self.schedule_random_message()

    def show_random_message(self):
        if not self.empowering_messages_enabled_var.get():
            self.set_status("ההודעות המעצימות כבויות כרגע. אפשר להפעיל אותן שוב מהמסך.")
            return
        message = random.choice(EMPOWERING_MESSAGES)
        toast = tk.Toplevel(self.root)
        toast.title("💗")
        toast.configure(bg="#fff5fa")
        toast.resizable(False, False)
        toast.attributes("-topmost", True)

        frame = tk.Frame(toast, bg="#fff5fa", padx=18, pady=16)
        frame.pack(fill="both", expand=True)

        tk.Label(
            frame,
            text="🐱💖 הודעה מעצימה",
            bg="#fff5fa",
            fg=DARK_PINK,
            font=("Segoe UI", 13, "bold"),
        ).pack(anchor="w", pady=(0, 8))

        tk.Label(
            frame,
            text=message,
            bg="#fff5fa",
            fg=TEXT,
            font=("Segoe UI", 11),
            wraplength=320,
            justify="right",
        ).pack(anchor="w")

        ttk.Button(frame, text="סבבה", command=toast.destroy, style="Pink.TButton").pack(anchor="e", pady=(12, 0))
        toast.after(9000, lambda: toast.destroy() if toast.winfo_exists() else None)

    def toggle_random_messages(self):
        if not self.empowering_messages_enabled_var.get():
            if self.random_message_job:
                self.root.after_cancel(self.random_message_job)
                self.random_message_job = None
        elif not self.random_message_job:
            self.schedule_random_message(initial_delay=True)
        self.save_current_settings()

    def cleanup_temp_dir(self):
        if self.temp_dir and os.path.isdir(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        self.temp_dir = None

    def on_close(self):
        self.save_current_settings()
        self.stop_audio_preview(close_player=True)
        self.cleanup_temp_dir()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = CatAudioCutterApp()
    app.run()
