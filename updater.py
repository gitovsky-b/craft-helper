import requests
import os
import sys
import subprocess
import tempfile
import json
import re
from pathlib import Path
from packaging import version
from version import __version__, GITHUB_REPO

def get_latest_release_info():
    """Получает информацию о последнем релизе с GitHub."""
    api_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    try:
        resp = requests.get(api_url, timeout=60)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка проверки обновлений: {e}")
        return None

def get_update_details(latest_info):
    """
    Возвращает словарь с ключами:
      - asset: данные ассета для платформы
      - version: строка версии (без 'v')
      - changelog: текст изменений (либо из коммитов, либо из body релиза)
    Если нет доступного обновления или подходящего ассета — возвращает None.
    """
    if not latest_info or not is_new_version_available(latest_info):
        return None

    asset = find_asset_for_platform(latest_info)
    if not asset:
        return None

    tag = latest_info.get("tag_name", "").lstrip("v")
    base_tag = f"v{__version__}"   # предполагаем, что текущая версия имеет такой тег
    head_tag = latest_info.get("tag_name", "")

    changelog = get_changelog_from_commits(base_tag, head_tag)
    if not changelog:
        # Запасной вариант — описание из тела релиза
        changelog = latest_info.get("body", "").strip()

    return {
        "asset": asset,
        "version": tag,
        "changelog": changelog
    }

def is_new_version_available(latest_info):
    """Сравнивает версии. Возвращает True, если найденная версия выше текущей."""
    if not latest_info:
        return False
    tag = latest_info.get("tag_name", "").lstrip("v")
    try:
        return version.parse(tag) > version.parse(__version__)
    except version.InvalidVersion:
        return False

def find_asset_for_platform(release_info):
    """Ищет в релизе файл, подходящий для текущей ОС."""
    if not release_info or "assets" not in release_info:
        return None
    for asset in release_info["assets"]:
        name = asset["name"].lower()
        if sys.platform.startswith("win") and name.endswith(".exe"):
            return asset
        if sys.platform.startswith("linux") and "linux" in name:
            return asset
    return None

def download_update(asset, save_path, progress_callback=None):
    """Скачивает файл обновления."""
    try:
        url = asset["browser_download_url"]
        total = int(asset["size"])
        downloaded = 0
        with requests.get(url, stream=True, timeout=120) as r:
            r.raise_for_status()
            with open(save_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_callback and total:
                        progress_callback(min(downloaded / total, 1.0))
        return True
    except Exception as e:
        print(f"Ошибка загрузки: {e}")
        return False

def apply_update_and_restart(saved_file_path):
    """Создаёт bat-скрипт для замены исполняемого файла и перезапускает приложение."""
    if not getattr(sys, 'frozen', False):
        return
    current_exe = sys.executable
    script = f"""@echo off
timeout /t 2 /nobreak > nul
move /y "{saved_file_path}" "{current_exe}"
start "" "{current_exe}"
del "%~f0" & exit
"""
    updater_script = os.path.join(tempfile.gettempdir(), "craft_helper_update.bat")
    with open(updater_script, 'w') as f:
        f.write(script)
    subprocess.Popen([updater_script], shell=True)
    sys.exit(0)

def get_changelog_from_commits(base_tag: str, head_tag: str):
    compare_url = f"https://api.github.com/repos/{GITHUB_REPO}/compare/{base_tag}...{head_tag}"
    try:
        resp = requests.get(compare_url, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        commits = data.get("commits", [])
        lines = []
        pattern = re.compile(r'^(feat|fix)(\(.+\))?!?: (.+)$')
        for commit in commits:
            first_line = commit['commit']['message'].splitlines()[0]
            match = pattern.match(first_line)
            if match:
                description = match.group(3).strip()
                if description:
                    lines.append(f"• {description}")
        if not lines:
            return ""
        if len(lines) > 20:
            lines = lines[:20]
            lines.append("... и ещё значимые изменения")
        return "\n".join(lines)
    except requests.exceptions.RequestException:
        return ""

DB_PATH = Path("database.json")

def get_ignored_version():
    try:
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get("ignored_version", "")
    except (FileNotFoundError, json.JSONDecodeError):
        return ""

def set_ignored_version(ver: str):
    try:
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    data["ignored_version"] = ver
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)