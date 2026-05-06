"""
Angels Launcher v14.0  —  Neon Edition
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ИСПРАВЛЕНО В v14.0:
  ◈ DEMO MODE FIX — полностью убран демо-режим
  ◈ Пиратский запуск как в Legacy Launcher (--accessToken, --uuid, --userType legacy)
  ◈ Корректный auth_access_token и user_type для обхода проверки
  ◈ Новая ссылка на мод (Google Drive прямая)
  ◈ Автопроверка и обновление мода при смене ссылки
  ◈ Улучшенное меню — быстрые кнопки, компактный layout
  ◈ Оптимизирован код
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Admin: python angels_launcher_v14.py --angelsvistop121
  Keygen: python angels_launcher_v14.py --keygen [n]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

# ══════════════════════════════════════════════════════
#  CONFIG
# ══════════════════════════════════════════════════════
LAUNCHER_NAME = "Angels Launcher"
LAUNCHER_VER  = "14.0.0"
MOD_NAME      = "Angels Mod"
MOD_VERSION   = "1.2.0"
MC_VERSION    = "1.16.5"
FORGE_VERSION = "36.2.39"
SUPER_ADMIN   = "validka3"
TG_LINK       = "@Softire_1"
GITHUB_REPO   = "davlatbehsm/angels-launcher"
GITHUB_RELEASES_API = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"

# ══════════════════════════════════════════════════════
#  NEON PALETTE
# ══════════════════════════════════════════════════════
BG_VOID   = "#00040c"
BG_BASE   = "#000810"
BG_CARD   = "#040d1c"
BG_PANEL  = "#060f20"
BG_ITEM   = "#081428"
BG_HOVER  = "#0c1e38"
BG_ACTIVE = "#0f2448"
BD_DARK   = "#0c1e36"
BD_MID    = "#123060"
BD_LIGHT  = "#1a4878"
BD_GLOW   = "#2060a0"
AC_MAIN   = "#00c8ff"
AC_GLOW   = "#00a8e8"
AC_DIM    = "#0080b8"
AC_CYAN   = "#00ffee"
AC_MINT   = "#00ffaa"
AC_PURPLE = "#8844ff"
AC_GOLD   = "#ffcc00"
AC_RED    = "#ff3355"
AC_ORANGE = "#ff8833"
AC_GREEN  = "#00e87a"
TX_WHITE  = "#f4faff"
TX_MAIN   = "#c8e8ff"
TX_MID    = "#7aaccc"
TX_DIM    = "#3a6888"
TX_DARK   = "#1a3850"
ADM_BG    = "#060010"
ADM_PANEL = "#0c0020"
ADM_ACC   = "#ff00cc"
ADM_RED   = "#ff2244"
ADM_GOLD  = "#ffdd00"
ADM_MUTE  = "#3a0038"
ADM_TEXT  = "#ffccee"
ADM_ACC2  = "#cc0088"
BUBBLE_COLS = ["#00c8ff","#0088d4","#00ffee","#00aaff","#40d8ff","#80f0ff","#00ccbb","#60d0ff","#ffffff","#00ffaa"]

# ══════════════════════════════════════════════════════
#  IMPORTS
# ══════════════════════════════════════════════════════
import os, sys, json, uuid, shutil, zipfile, platform, hashlib
import threading, subprocess, urllib.request, time, socket, math, random
import datetime, hmac as _hmac, tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# ══════════════════════════════════════════════════════
#  PATHS
# ══════════════════════════════════════════════════════
APPDATA        = Path(os.getenv("APPDATA", str(Path.home()))) / ".angels-launcher"
MC_DIR         = APPDATA / "minecraft"
VERSIONS_DIR   = MC_DIR / "versions"
LIBRARIES_DIR  = MC_DIR / "libraries"
ASSETS_DIR     = MC_DIR / "assets"
MODS_DIR       = MC_DIR / "mods"
NATIVES_DIR    = MC_DIR / "natives"
FORGE_INST     = APPDATA / f"forge-{MC_VERSION}-{FORGE_VERSION}-installer.jar"
FORGE_EXTRACT  = APPDATA / f"forge-{MC_VERSION}-{FORGE_VERSION}-extract"
KEY_FILE       = APPDATA / "activation.key"
USERS_FILE     = APPDATA / "users.json"
USED_KEYS_FILE = APPDATA / "used_keys.json"
BLACKLIST_FILE = APPDATA / "blacklist.json"
KEYS_META_FILE = APPDATA / "keys_meta.json"
SERVERS_FILE   = APPDATA / "servers.json"
MOD_URL_FILE   = APPDATA / "mod_url.json"

def _get_installed_version_file() -> Path:
    base = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).resolve().parent
    return base / "angels_launcher_version.json"

INSTALLED_VERSION_FILE = _get_installed_version_file()

def _read_installed_version() -> str:
    try:
        if INSTALLED_VERSION_FILE.exists():
            return json.loads(INSTALLED_VERSION_FILE.read_text()).get("version", LAUNCHER_VER)
    except: pass
    return LAUNCHER_VER

def _write_installed_version(version: str):
    try:
        INSTALLED_VERSION_FILE.write_text(json.dumps(
            {"version": version, "updated_at": time.strftime("%Y-%m-%d %H:%M:%S")}, indent=2))
    except: pass

_write_installed_version(LAUNCHER_VER)

FORGE_MC_VER = f"{MC_VERSION}-{FORGE_VERSION}"
FORGE_ID_VARIANTS = [FORGE_MC_VER, f"{MC_VERSION}-forge-{FORGE_VERSION}", f"{MC_VERSION}-forge{FORGE_VERSION}"]
VERSION_MANIFEST    = "https://launchermeta.mojang.com/mc/game/version_manifest_v2.json"
FORGE_INSTALLER_URL = (f"https://maven.minecraftforge.net/net/minecraftforge/forge/"
                       f"{FORGE_MC_VER}/forge-{FORGE_MC_VER}-installer.jar")
MAVEN_FORGE      = "https://maven.minecraftforge.net/"
DOWNLOAD_THREADS = 8

# ══════════════════════════════════════════════════════
#  MOD URL — новая ссылка v14.0
#  Конвертируем Google Drive share → прямой download URL
# ══════════════════════════════════════════════════════
MOD_URL_DEFAULT = "https://drive.google.com/uc?export=download&id=1c1S3MSGSblcZr02fMdyGIR96MsLtnlg9"

def _gdrive_direct(url: str) -> str:
    """Конвертирует любую Google Drive ссылку в прямой download URL."""
    import re
    m = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
    if m:
        return f"https://drive.google.com/uc?export=download&id={m.group(1)}"
    m = re.search(r'id=([a-zA-Z0-9_-]+)', url)
    if m:
        return f"https://drive.google.com/uc?export=download&id={m.group(1)}"
    return url

def _load_mod_url_config() -> dict:
    try:
        if MOD_URL_FILE.exists():
            return json.loads(MOD_URL_FILE.read_text())
    except: pass
    return {"url": MOD_URL_DEFAULT, "url_hash": ""}

def _save_mod_url_config(url: str):
    APPDATA.mkdir(parents=True, exist_ok=True)
    h = hashlib.md5(url.encode()).hexdigest()
    MOD_URL_FILE.write_text(json.dumps({"url": url, "url_hash": h}, indent=2))

def _get_mod_url() -> str:
    cfg = _load_mod_url_config()
    return cfg.get("url", MOD_URL_DEFAULT)

def check_mod_url_changed(new_url: str) -> bool:
    """Возвращает True если URL изменился."""
    cfg = _load_mod_url_config()
    old_h = cfg.get("url_hash", "")
    new_h = hashlib.md5(new_url.encode()).hexdigest()
    return old_h != new_h

# ══════════════════════════════════════════════════════
#  KEY SYSTEM
# ══════════════════════════════════════════════════════
_VENC = bytes([0x03,0x2c,0x25,0x27,0x2e,0x31,0x0e,0x23,0x37,0x2c,0x21,0x2a,
               0x71,0x30,0x1d,0x66,0x71,0x21,0x30,0x71,0x36,0x1d,0x09,0x71,
               0x3b,0x1d,0x70,0x72,0x70,0x77])
def _secret() -> bytes: return bytes(b ^ 0x42 for b in _VENC)
def _key_checksum(s1, s2):
    return _hmac.new(_secret(), f"{s1.upper()}-{s2.upper()}".encode(), hashlib.sha256).hexdigest()[:4].upper()
def validate_key(key):
    key = key.strip().upper(); parts = key.split('-')
    if len(parts) != 4: return False
    prefix, s1, s2, cs = parts
    if prefix != 'ANGELS' or len(s1)!=4 or len(s2)!=4 or len(cs)!=4: return False
    return _hmac.compare_digest(_key_checksum(s1, s2), cs)
def _raw_generate():
    import secrets
    C = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    s1 = ''.join(secrets.choice(C) for _ in range(4))
    s2 = ''.join(secrets.choice(C) for _ in range(4))
    return f"ANGELS-{s1}-{s2}-{_key_checksum(s1,s2)}"
def generate_key(): return _raw_generate()
def fmt_duration(sec):
    if sec <= 0: return "Навсегда ∞"
    if sec < 60: return f"{sec} сек."
    if sec < 3600: return f"{sec//60} мин."
    if sec < 86400: return f"{sec//3600} ч."
    if sec < 86400*30: return f"{sec//86400} дн."
    if sec < 86400*365: return f"{sec//(86400*30)} мес."
    return f"{sec//(86400*365)} г."
def generate_timed_key(duration_seconds=0):
    key = _raw_generate(); kh = hashlib.sha256(key.encode()).hexdigest()
    meta = _load_keys_meta()
    meta[kh] = {"created": time.strftime("%Y-%m-%d %H:%M:%S"),
                "duration_seconds": duration_seconds,
                "duration_label": fmt_duration(duration_seconds)}
    _save_keys_meta(meta); return key
def keygen(n=10):
    keys = [generate_key() for _ in range(n)]
    for k in keys: print(k)
    return keys
def _load_keys_meta():
    try:
        if KEYS_META_FILE.exists(): return json.loads(KEYS_META_FILE.read_text())
    except: pass
    return {}
def _save_keys_meta(d):
    APPDATA.mkdir(parents=True, exist_ok=True)
    KEYS_META_FILE.write_text(json.dumps(d, ensure_ascii=False, indent=2))

# ══════════════════════════════════════════════════════
#  USER DATABASE
# ══════════════════════════════════════════════════════
def _load_users():
    try:
        if USERS_FILE.exists(): return json.loads(USERS_FILE.read_text(encoding='utf-8'))
    except: pass
    return {}
def _save_users(d):
    APPDATA.mkdir(parents=True, exist_ok=True)
    USERS_FILE.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding='utf-8')
def _load_used_keys():
    try:
        if USED_KEYS_FILE.exists(): return set(json.loads(USED_KEYS_FILE.read_text()))
    except: pass
    return set()
def _save_used_keys(u):
    APPDATA.mkdir(parents=True, exist_ok=True)
    USED_KEYS_FILE.write_text(json.dumps(list(u)))
def _load_blacklist():
    try:
        if BLACKLIST_FILE.exists(): return set(json.loads(BLACKLIST_FILE.read_text()))
    except: pass
    return set()
def _save_blacklist(b):
    APPDATA.mkdir(parents=True, exist_ok=True)
    BLACKLIST_FILE.write_text(json.dumps(list(b)))
def hash_password(pw): return hashlib.sha256(pw.encode()).hexdigest()
def is_admin(nick): return nick.strip().lower() == SUPER_ADMIN.lower()
def get_current_user():
    try:
        if KEY_FILE.exists():
            d = json.loads(KEY_FILE.read_text())
            return _load_users().get(d.get("key_hash"), {})
    except: pass
    return {}
def is_activated():
    try:
        if KEY_FILE.exists(): return json.loads(KEY_FILE.read_text()).get("activated", False)
    except: pass
    return False
def check_subscription(user):
    expires = user.get("key_expires")
    if not expires: return True, "Навсегда ∞"
    try:
        exp = datetime.datetime.strptime(expires, "%Y-%m-%d %H:%M:%S")
        now = datetime.datetime.now()
        if now > exp: return False, "Подписка истекла"
        rem = exp - now; d, h = rem.days, rem.seconds // 3600; m = (rem.seconds % 3600) // 60
        if d > 0: return True, f"Ещё {d}д {h}ч"
        if h > 0: return True, f"Ещё {h}ч {m}мин"
        return True, f"Ещё {m}мин"
    except: return True, "Навсегда ∞"

def activate_key(key, nickname, password):
    key = key.strip().upper(); nickname = nickname.strip(); password = password.strip()
    if len(nickname) < 3: return False, "Ник минимум 3 символа"
    if len(password) < 4: return False, "Пароль минимум 4 символа"
    if not all(c.isalnum() or c in "_-" for c in nickname): return False, "Ник: буквы, цифры, _ и -"
    bl = _load_blacklist(); kh = hashlib.sha256(key.encode()).hexdigest()
    if kh in bl: return False, "Этот ключ заблокирован"
    if not validate_key(key): return False, "Неверный ключ активации"
    used = _load_used_keys()
    if kh in used: return False, "Ключ уже использован"
    users = _load_users()
    for u in users.values():
        if u.get("nickname","").lower() == nickname.lower():
            return False, f"Ник «{nickname}» уже занят"
    meta = _load_keys_meta(); key_meta = meta.get(kh, {}); dur_sec = key_meta.get("duration_seconds", 0)
    expires = None
    if dur_sec > 0:
        exp_dt = datetime.datetime.now() + datetime.timedelta(seconds=dur_sec)
        expires = exp_dt.strftime("%Y-%m-%d %H:%M:%S")
    used.add(kh); _save_used_keys(used)
    users[kh] = {
        "nickname": nickname, "password_hash": hash_password(password),
        "date": time.strftime("%Y-%m-%d %H:%M"), "last_login": time.strftime("%Y-%m-%d %H:%M"),
        "login_count": 1, "key": key, "is_admin": is_admin(nickname),
        "key_expires": expires, "duration_label": key_meta.get("duration_label", "Навсегда ∞"),
        "hw_id": str(uuid.getnode())
    }
    _save_users(users)
    KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
    KEY_FILE.write_text(json.dumps({
        "activated": True, "key_hash": kh, "nickname": nickname,
        "date": time.strftime("%Y-%m-%d"), "is_admin": is_admin(nickname)
    }))
    return True, f"Добро пожаловать, {nickname}!"

def login_user(nickname, password):
    nickname = nickname.strip(); password = password.strip(); users = _load_users()
    for kh, u in users.items():
        if u.get("nickname","").lower() == nickname.lower():
            if u.get("password_hash") != hash_password(password): return False, "Неверный пароль"
            valid, status = check_subscription(u)
            if not valid: return False, f"Подписка истекла!\nПродление: {TG_LINK}"
            u["last_login"] = time.strftime("%Y-%m-%d %H:%M")
            u["login_count"] = u.get("login_count",0)+1
            _save_users(users)
            KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
            KEY_FILE.write_text(json.dumps({
                "activated": True, "key_hash": kh, "nickname": nickname,
                "date": time.strftime("%Y-%m-%d"), "is_admin": is_admin(nickname)
            }))
            return True, f"Добро пожаловать, {nickname}! ({status})"
    return False, "Пользователь не найден"

# ══════════════════════════════════════════════════════
#  UTILITIES
# ══════════════════════════════════════════════════════
def get_total_ram_gb():
    try:
        import psutil; return max(1, psutil.virtual_memory().total // (1024**3))
    except ImportError: pass
    try:
        if platform.system() == "Windows":
            import ctypes
            class MEM(ctypes.Structure):
                _fields_ = [("dwLength",ctypes.c_ulong),("dwMemoryLoad",ctypes.c_ulong),
                             ("ullTotalPhys",ctypes.c_ulonglong),("ullAvailPhys",ctypes.c_ulonglong),
                             ("ullTotalPageFile",ctypes.c_ulonglong),("ullAvailPageFile",ctypes.c_ulonglong),
                             ("ullTotalVirtual",ctypes.c_ulonglong),("ullAvailVirtual",ctypes.c_ulonglong),
                             ("sullAvailExtendedVirtual",ctypes.c_ulonglong)]
            ms = MEM(); ms.dwLength = ctypes.sizeof(ms)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(ms))
            return max(1, ms.ullTotalPhys // (1024**3))
    except: pass
    return 8

TOTAL_RAM = get_total_ram_gb()

def get_java():
    candidates = ["java"]
    if platform.system() == "Windows":
        roots = [r"C:\Program Files\Java", r"C:\Program Files\Eclipse Adoptium",
                 r"C:\Program Files\Microsoft", r"C:\Program Files\BellSoft",
                 r"C:\Program Files\Zulu", r"C:\Program Files\Temurin",
                 r"C:\Program Files (x86)\Java"]
        for root in roots:
            if os.path.isdir(root):
                for sub in sorted(os.listdir(root), reverse=True):
                    j = os.path.join(root, sub, "bin", "java.exe")
                    if os.path.isfile(j): candidates.insert(0, j)
    for j in candidates:
        try:
            if subprocess.run([j, "-version"], capture_output=True, timeout=5).returncode == 0: return j
        except: pass
    return None

def http_get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": f"AngelsLauncher/{LAUNCHER_VER}",
                                               "Accept": "application/vnd.github.v3+json"})
    with urllib.request.urlopen(req, timeout=15) as r: return json.loads(r.read().decode())

def sha1_file(path):
    h = hashlib.sha1()
    with open(path,"rb") as f:
        while chunk := f.read(65536): h.update(chunk)
    return h.hexdigest()

def download_file(url, dest, on_progress=None, expected_sha1=None):
    dest = Path(dest); dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        if not expected_sha1 or sha1_file(dest) == expected_sha1: return
    tmp = str(dest) + ".tmp"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": f"AngelsLauncher/{LAUNCHER_VER}"})
        with urllib.request.urlopen(req, timeout=90) as r:
            total = int(r.headers.get("Content-Length", 0)); done = 0
            with open(tmp,"wb") as f:
                while chunk := r.read(65536):
                    f.write(chunk); done += len(chunk)
                    if on_progress: on_progress(done, total)
        shutil.move(tmp, dest)
        if expected_sha1 and sha1_file(dest) != expected_sha1:
            dest.unlink(missing_ok=True); raise Exception(f"SHA1 mismatch: {dest.name}")
    except Exception as e:
        if os.path.exists(tmp):
            try: os.remove(tmp)
            except: pass
        raise e

def check_server_ping(host, port=25565, timeout=3):
    try: s = socket.create_connection((host, port), timeout=timeout); s.close(); return True
    except: return False

def os_name():
    s = platform.system()
    return "windows" if s=="Windows" else ("osx" if s=="Darwin" else "linux")

def rule_allowed(rules):
    if not rules: return True
    result = False; cur = os_name()
    for rule in rules:
        action = rule.get("action") == "allow"
        if "os" in rule:
            if rule["os"].get("name") == cur: result = action
        else: result = action
    return result

def fmt_time(s):
    if s < 0 or s > 7200: return "..."
    m, s = divmod(int(s), 60)
    return f"{m}м {s}с" if m > 0 else f"{s}с"

def fmt_size(b):
    return f"{b/1024**2:.1f} МБ" if b >= 1024**2 else f"{b/1024:.0f} КБ"

def maven_coord_to_path(coord):
    ext = "jar"
    if "@" in coord: coord, ext = coord.rsplit("@", 1)
    parts = coord.split(":")
    if len(parts) < 3: return Path(coord.replace(":","/") + "." + ext)
    group = parts[0].replace(".", "/"); artifact = parts[1]; version = parts[2]
    classifier = parts[3] if len(parts) > 3 else None
    fname = f"{artifact}-{version}" + (f"-{classifier}" if classifier else "") + f".{ext}"
    return Path(group) / artifact / version / fname

def get_jar_main_class(jar_path):
    with zipfile.ZipFile(jar_path) as zf:
        mf = next((n for n in zf.namelist() if n.upper() == "META-INF/MANIFEST.MF"), None)
        if not mf: raise Exception(f"MANIFEST.MF not found in {jar_path.name}")
        with zf.open(mf) as f:
            for line in f.read().decode("utf-8", errors="replace").splitlines():
                if line.startswith("Main-Class:"): return line.split(":", 1)[1].strip()
    raise Exception("Main-Class not found")

def resolve_proc_arg(arg, data_map):
    if arg.startswith("[") and arg.endswith("]"): return str(LIBRARIES_DIR / maven_coord_to_path(arg[1:-1]))
    if arg.startswith("{") and arg.endswith("}"): return data_map.get(arg[1:-1], arg)
    return arg

def find_forge_json():
    search = [VERSIONS_DIR]
    default = Path(os.getenv("APPDATA", str(Path.home()))) / ".minecraft" / "versions"
    if default.exists() and default != VERSIONS_DIR: search.append(default)
    for vdir in search:
        if not vdir.exists(): continue
        for fid in FORGE_ID_VARIANTS:
            p = vdir / fid / f"{fid}.json"
            if p.exists(): return fid, p
        for d in vdir.iterdir():
            if not d.is_dir(): continue
            if MC_VERSION in d.name and ("forge" in d.name.lower() or FORGE_VERSION in d.name):
                p = d / f"{d.name}.json"
                if p.exists(): return d.name, p
    return None, None

def load_servers():
    try:
        if SERVERS_FILE.exists():
            with open(SERVERS_FILE) as f: return json.load(f)
    except: pass
    return []

def save_servers(s):
    APPDATA.mkdir(parents=True, exist_ok=True)
    with open(SERVERS_FILE,"w") as f: json.dump(s, f, ensure_ascii=False, indent=2)

class ParallelDownloader:
    def __init__(self, tasks, threads=DOWNLOAD_THREADS, on_progress=None, on_error=None):
        self.tasks=tasks; self.threads=threads; self.on_progress=on_progress; self.on_error=on_error
        self._lock=threading.Lock(); self._done=0; self._total=len(tasks); self._start=time.time()
    def _do(self, task):
        url, dest, sha1 = task
        try: download_file(url, dest, expected_sha1=sha1)
        except Exception as e:
            if self.on_error: self.on_error(dest, e)
        with self._lock:
            self._done += 1; elapsed = time.time() - self._start
            eta = (self._total - self._done) / max(self._done,1) * elapsed
            if self.on_progress: self.on_progress(self._done, self._total, 0, eta)
    def run(self):
        with ThreadPoolExecutor(max_workers=self.threads) as ex:
            for _ in as_completed([ex.submit(self._do, t) for t in self.tasks]): pass

# ══════════════════════════════════════════════════════
#  AUTO UPDATER
# ══════════════════════════════════════════════════════
class AutoUpdater:
    def __init__(self):
        self._latest_info = None
        self._script_path = Path(__file__).resolve(); self._script_mtime = self._get_mtime()
    def _get_mtime(self):
        try: return self._script_path.stat().st_mtime
        except: return 0
    def _version_tuple(self, ver_str):
        try: return tuple(int(x) for x in str(ver_str).lstrip("v").split("."))
        except: return (0,)
    def is_newer(self, remote_ver):
        return self._version_tuple(remote_ver) > self._version_tuple(_read_installed_version())
    def check_for_updates(self, callback):
        def _do():
            try:
                data = http_get_json(GITHUB_RELEASES_API)
                tag = data.get("tag_name","").lstrip("v"); body = data.get("body","")
                assets = data.get("assets",[]); exe_asset = None
                for a in assets:
                    if a.get("name","").endswith(".exe") and "launcher" in a.get("name","").lower():
                        exe_asset = a; break
                if not exe_asset and assets: exe_asset = assets[0]
                dl_url = exe_asset["browser_download_url"] if exe_asset else ""
                size = exe_asset.get("size",0) if exe_asset else 0
                changelog = []
                for line in body.split("\n"):
                    line = line.strip()
                    if line.startswith(("- ","+ ","* ")): changelog.append(line)
                    elif line and not line.startswith("#"): changelog.append(f"  {line}")
                info = {"version": tag, "changelog": changelog or [f"Версия v{tag}"],
                        "download_url": dl_url, "size": size,
                        "release_name": data.get("name", f"v{tag}"),
                        "published_at": data.get("published_at","")}
                self._latest_info = info; callback(True, info, None)
            except Exception as e:
                callback(False, None, str(e))
        threading.Thread(target=_do, daemon=True).start()
    def download_and_install(self, url, new_version, on_progress=None, on_done=None):
        def _do():
            try:
                current = Path(sys.executable)
                if current.suffix.lower() == ".exe":
                    new_path = current.parent / "angels_launcher_new.exe"; final_path = current
                else:
                    script = Path(__file__).resolve()
                    new_path = script.parent / "angels_launcher_new.py"; final_path = script
                if new_path.exists(): new_path.unlink()
                download_file(url, new_path, on_progress=on_progress)
                if not new_path.exists() or new_path.stat().st_size < 10000:
                    raise Exception("Файл скачался некорректно")
                try:
                    (new_path.parent / "angels_launcher_version.json").write_text(
                        json.dumps({"version": new_version, "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                                    "previous_version": LAUNCHER_VER}, indent=2))
                except: pass
                current_pid = os.getpid()
                if platform.system() == "Windows":
                    bat = new_path.parent / "_angels_update.bat"
                    bat.write_text(
                        f"@echo off\ntimeout /t 2 /nobreak > nul\ntaskkill /PID {current_pid} /F > nul 2>&1\n"
                        f"timeout /t 1 /nobreak > nul\nmove /y \"{new_path}\" \"{final_path}\"\n"
                        f"start \"\" \"{final_path}\"\ndel \"%~f0\"\n", encoding="cp866")
                    if on_done: on_done(True, str(bat))
                else:
                    import stat as stat_mod; shutil.move(str(new_path), str(final_path))
                    try:
                        st = os.stat(final_path)
                        os.chmod(final_path, st.st_mode | stat_mod.S_IEXEC | stat_mod.S_IXGRP | stat_mod.S_IXOTH)
                    except: pass
                    if on_done: on_done(True, str(final_path))
            except Exception as e:
                if on_done: on_done(False, str(e))
        threading.Thread(target=_do, daemon=True).start()
    def restart_with_update(self, bat_path_or_exe=None):
        try:
            if bat_path_or_exe and Path(bat_path_or_exe).exists():
                p = Path(bat_path_or_exe)
                if p.suffix.lower() == ".bat":
                    subprocess.Popen(str(p), shell=True,
                                     creationflags=(subprocess.CREATE_NEW_CONSOLE if platform.system()=="Windows" else 0))
                    time.sleep(0.3); os._exit(0)
                else: os.execv(bat_path_or_exe, [bat_path_or_exe] + sys.argv[1:])
            else: os.execv(sys.executable, [sys.executable] + sys.argv)
        except: os._exit(1)
    def watch_script(self, interval_ms=3000, root=None, on_change=None):
        if root is None: return
        def _check():
            try:
                mt = self._get_mtime()
                if mt and mt != self._script_mtime:
                    self._script_mtime = mt
                    if on_change: on_change()
            except: pass
            root.after(interval_ms, _check)
        root.after(interval_ms, _check)
    def auto_restart_on_change(self):
        try:
            time.sleep(0.5)
            os.execv(sys.executable, [sys.executable, str(Path(__file__).resolve())] + sys.argv[1:])
        except: pass

# ══════════════════════════════════════════════════════
#  UI HELPERS
# ══════════════════════════════════════════════════════
def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def blend_color(c1, c2, t):
    r1,g1,b1 = hex_to_rgb(c1); r2,g2,b2 = hex_to_rgb(c2)
    return f"#{int(r1+(r2-r1)*t):02x}{int(g1+(g2-g1)*t):02x}{int(b1+(b2-b1)*t):02x}"

def lerp_color(c1, c2, t): return blend_color(c1, c2, max(0,min(1,t)))

def _draw_rounded_rect(canvas, x1, y1, x2, y2, r=8, **kw):
    r = min(r, (x2-x1)//2, (y2-y1)//2)
    points = [x1+r,y1, x2-r,y1, x2,y1, x2,y1+r, x2,y2-r, x2,y2,
              x2-r,y2, x1+r,y2, x1,y2, x1,y2-r, x1,y1+r, x1,y1]
    return canvas.create_polygon(points, smooth=True, **kw)

def make_pill_button(parent, text, command=None, bg=BG_ITEM, fg=AC_MAIN,
                     hover_bg=BG_HOVER, hover_fg=TX_WHITE,
                     font=("Segoe UI", 10, "bold"), px=18, py=8,
                     icon=None, accent_left=None, width=None, **kw):
    outer = tk.Frame(parent, bg=bg, cursor="hand2", **kw)
    if width: outer.configure(width=width)
    inner = tk.Frame(outer, bg=bg); inner.pack(fill="both", expand=True, padx=1, pady=1)
    if accent_left:
        tk.Frame(inner, bg=accent_left, width=3).pack(side="left", fill="y")
    row = tk.Frame(inner, bg=bg); row.pack(fill="both", expand=True, padx=px, pady=py)
    labels = []
    if icon:
        il = tk.Label(row, text=icon, bg=bg, fg=fg, font=("Segoe UI", 12))
        il.pack(side="left", padx=(0, 7)); labels.append(il)
    lbl = tk.Label(row, text=text, bg=bg, fg=fg, font=font, anchor="w")
    lbl.pack(side="left", fill="x", expand=True); labels.append(lbl)
    def on_enter(e):
        outer.configure(bg=hover_bg); inner.configure(bg=hover_bg); row.configure(bg=hover_bg)
        for l in labels: l.configure(bg=hover_bg, fg=hover_fg)
    def on_leave(e):
        outer.configure(bg=bg); inner.configure(bg=bg); row.configure(bg=bg)
        for l in labels: l.configure(bg=bg, fg=fg)
    def on_click(e):
        if command: outer.after(80, command)
    for w in [outer, inner, row] + labels:
        w.bind("<Enter>", on_enter); w.bind("<Leave>", on_leave); w.bind("<Button-1>", on_click)
    outer._labels = labels; outer._bg = bg; outer._fg = fg
    outer._hover_bg = hover_bg; outer._hover_fg = hover_fg
    outer._inner = inner; outer._row = row; outer._accent_bar = None
    return outer

def make_action_button(parent, text, command=None, style="primary",
                        font=("Segoe UI", 10, "bold"), px=20, py=10, icon=None, **kw):
    styles = {
        "primary":  (AC_MAIN,   BG_VOID, "#00e0ff", "#001020"),
        "danger":   (AC_RED,    BG_VOID, "#ff6688", "#1a0010"),
        "success":  (AC_GREEN,  BG_VOID, "#44ffaa", "#001a10"),
        "warning":  (AC_ORANGE, BG_VOID, "#ffaa55", "#1a0800"),
        "ghost":    (BG_ITEM,   TX_MID,  BG_HOVER,  TX_WHITE),
        "admin":    (ADM_ACC,   BG_VOID, "#ff44ee", "#100018"),
    }
    norm_bg, norm_fg, h_bg, h_fg = styles.get(style, styles["ghost"])
    btn = tk.Frame(parent, bg=norm_bg, cursor="hand2", **kw)
    inner = tk.Frame(btn, bg=norm_bg); inner.pack(fill="both", padx=1, pady=1)
    row = tk.Frame(inner, bg=norm_bg); row.pack(fill="both", padx=px, pady=py)
    labels = []
    if icon:
        il = tk.Label(row, text=icon, bg=norm_bg, fg=norm_fg, font=("Segoe UI", 13))
        il.pack(side="left", padx=(0, 8)); labels.append(il)
    lbl = tk.Label(row, text=text, bg=norm_bg, fg=norm_fg, font=font)
    lbl.pack(side="left"); labels.append(lbl)
    def on_enter(e):
        btn.configure(bg=h_bg); inner.configure(bg=h_bg); row.configure(bg=h_bg)
        for l in labels: l.configure(bg=h_bg, fg=h_fg)
    def on_leave(e):
        btn.configure(bg=norm_bg); inner.configure(bg=norm_bg); row.configure(bg=norm_bg)
        for l in labels: l.configure(bg=norm_bg, fg=norm_fg)
    def on_click(e):
        if command: btn.after(80, command)
    for w in [btn, inner, row] + labels:
        w.bind("<Enter>", on_enter); w.bind("<Leave>", on_leave); w.bind("<Button-1>", on_click)
    btn._inner = inner; btn._row = row; btn._labels = labels
    btn._norm_bg = norm_bg; btn._norm_fg = norm_fg; btn._h_bg = h_bg; btn._h_fg = h_fg
    return btn

class GlowButton(tk.Frame):
    def __init__(self, parent, text, command=None,
                 bg=BG_CARD, fg=AC_MAIN, glow=AC_MAIN, font=("Segoe UI",14,"bold"),
                 height=60, **kw):
        super().__init__(parent, bg=bg, cursor="hand2", **kw)
        self._bg=bg; self._fg=fg; self._glow=glow; self._phase=0.0; self._running=True
        self._hover=False; self._command=command
        self._canvas = tk.Canvas(self, bg=bg, highlightthickness=0, height=height)
        self._canvas.pack(fill="both", expand=True)
        self._text = text; self._font = font; self._height = height
        self._canvas.bind("<Configure>", self._redraw)
        self._canvas.bind("<Enter>", self._on_enter)
        self._canvas.bind("<Leave>", self._on_leave)
        self._canvas.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self._tick()
    def _on_enter(self, e): self._hover = True
    def _on_leave(self, e): self._hover = False
    def _on_click(self, e):
        if self._command: self.after(100, self._command)
    def _redraw(self, e=None):
        W = self._canvas.winfo_width() or 400; H = self._height
        c = self._canvas; c.delete("all")
        t = (math.sin(self._phase) + 1) / 2
        intensity = 0.6 + t * 0.4 + (0.3 if self._hover else 0)
        bg2 = lerp_color(self._bg, "#101828", 0.8)
        _draw_rounded_rect(c, 0, 0, W, H, r=14, fill=bg2, outline="")
        glow_r, glow_g, glow_b = hex_to_rgb(self._glow)
        for i in range(6, 0, -1):
            col = f"#{min(255,glow_r*i//10):02x}{min(255,glow_g*i//10):02x}{min(255,glow_b*i//10):02x}"
            _draw_rounded_rect(c, i*2, i, W-i*2, H-i, r=14-i, outline=col, fill="")
        border_col = lerp_color(AC_DIM, self._glow, intensity * 0.7)
        _draw_rounded_rect(c, 2, 2, W-2, H-2, r=12, outline=border_col, fill="", width=2)
        text_col = lerp_color(self._fg, TX_WHITE, min(1, intensity * 0.8))
        c.create_text(W//2, H//2+1, text=self._text, fill=lerp_color("#001020","#002040",0.5),
                      font=self._font, anchor="center")
        c.create_text(W//2, H//2, text=self._text, fill=text_col, font=self._font, anchor="center")
    def _tick(self):
        if not self._running: return
        try:
            self._phase += 0.04; self._redraw()
            self.after(33, self._tick)
        except: pass
    def destroy(self): self._running = False; super().destroy()
    def configure_state(self, enabled, text=None):
        if text: self._text = text
        self._fg = AC_MAIN if enabled else TX_DIM
        self._glow = AC_MAIN if enabled else BG_PANEL
        self.configure(cursor="hand2" if enabled else "arrow")

class NeonProgressBar(tk.Frame):
    def __init__(self, parent, height=8, bg=BG_ITEM, fg=AC_MAIN, **kw):
        super().__init__(parent, bg=bg, height=height+4, **kw)
        self._bg=bg; self._fg=fg; self._val=0.0; self._running=True; self._glow_phase=0.0
        self._canvas = tk.Canvas(self, bg=bg, highlightthickness=0, height=height+4)
        self._canvas.pack(fill="both", expand=True)
        self._canvas.bind("<Configure>", self._redraw)
        self._tick()
    def set(self, val):
        self._val = max(0.0, min(1.0, val)); self._redraw()
    def _redraw(self, e=None):
        W = self._canvas.winfo_width() or 400; H = self._canvas.winfo_height() or 12
        c = self._canvas; c.delete("all")
        _draw_rounded_rect(c, 0, 0, W, H, r=H//2, fill=BG_VOID, outline=BD_DARK)
        if self._val <= 0: return
        fw = max(H, int((W-4) * self._val))
        glow_t = (math.sin(self._glow_phase) + 1) / 2
        fg = self._fg
        if self._val < 0.33: fg = lerp_color(AC_GLOW, AC_MAIN, self._val * 3)
        elif self._val < 0.66: fg = AC_MAIN
        else: fg = lerp_color(AC_MAIN, AC_MINT, (self._val - 0.66) * 3)
        _draw_rounded_rect(c, 2, 2, fw+2, H-2, r=(H-4)//2, fill=fg, outline="")
        shimmer_x = int(fw * 0.3 + fw * 0.4 * glow_t) + 2
        _draw_rounded_rect(c, 2, 2, shimmer_x, H//2, r=(H-4)//2,
                           fill=lerp_color(fg, TX_WHITE, 0.3), outline="")
    def _tick(self):
        if not self._running: return
        try:
            self._glow_phase += 0.06; self._redraw()
            self.after(33, self._tick)
        except: pass
    def destroy(self): self._running = False; super().destroy()

class StarfieldCanvas(tk.Canvas):
    def __init__(self, parent, **kw):
        super().__init__(parent, bg=BG_VOID, highlightthickness=0, **kw)
        self._stars = []; self._bubbles = []; self._running = True
        self._init_stars(); self._init_bubbles(); self._ripples = []
        self.bind("<Button-1>", self._on_click)
        self._tick()
    def _init_stars(self):
        self._stars = []
        for _ in range(80):
            self._stars.append({
                "x": random.random(), "y": random.random(),
                "r": random.uniform(0.5, 2.2),
                "phase": random.uniform(0, math.pi*2),
                "speed": random.uniform(0.008, 0.025),
                "col": random.choice(["#1a3050","#0a2040","#163070","#0d2860"])
            })
    def _init_bubbles(self):
        self._bubbles = []
        for _ in range(28):
            r = random.uniform(4, 22)
            self._bubbles.append({
                "x": random.random(), "y": random.uniform(0.05, 1.1),
                "r": r, "br": r, "vy": random.uniform(0.0003, 0.0009),
                "vx": random.uniform(-0.0001, 0.0001),
                "col": random.choice(BUBBLE_COLS),
                "phase": random.uniform(0, math.pi*2), "ps": random.uniform(0.01, 0.035),
                "wobble": random.uniform(0, math.pi*2), "ws": random.uniform(0.02, 0.05),
                "ids": []
            })
    def _on_click(self, e):
        W = self.winfo_width() or 400; H = self.winfo_height() or 400
        self._ripples.append({"x": e.x/W, "y": e.y/H, "r": 0, "max_r": 0.2, "a": 1.0, "ids": []})
    def _draw_bubble(self, x, y, r, col):
        ids = []
        for gsc, st in [(4.0,"gray12"), (2.5,"gray25"), (1.6,"gray50")]:
            gr = r * gsc
            ids.append(self.create_oval(x-gr, y-gr, x+gr, y+gr, outline=col, fill="", width=1, stipple=st))
        ids.append(self.create_oval(x-r, y-r, x+r, y+r, outline=col, fill="", width=1))
        ids.append(self.create_oval(x-r+1, y-r+1, x+r-1, y+r-1, outline="", fill=col, stipple="gray12"))
        hr = r*0.38; hx = x-r*0.28; hy = y-r*0.28
        ids.append(self.create_oval(hx-hr, hy-hr*0.55, hx+hr, hy+hr*0.55, outline="", fill="white", stipple="gray50"))
        return ids
    def _tick(self):
        if not self._running: return
        try:
            W = self.winfo_width() or 400; H = self.winfo_height() or 400
            for s in self._stars:
                s["phase"] += s["speed"]
                t = (math.sin(s["phase"]) + 1) / 2
                col = lerp_color(s["col"], "#2a4878", t)
                x = s["x"]*W; y = s["y"]*H; r = s["r"]
                try: self.itemconfig(s.get("id"), fill=col, outline=col)
                except: s["id"] = self.create_oval(x-r, y-r, x+r, y+r, fill=col, outline="")
            for b in self._bubbles:
                for i in b["ids"]:
                    try: self.delete(i)
                    except: pass
                b["ids"] = []
                b["y"] -= b["vy"]; b["x"] += b["vx"]
                b["phase"] += b["ps"]; b["wobble"] += b["ws"]
                if b["y"] < -0.1: b["y"] = 1.1; b["x"] = random.random()
                if not -0.1 < b["x"] < 1.1: b["vx"] = -b["vx"]
                wobble = math.sin(b["wobble"]) * 0.07
                r = max(2, b["br"] + math.sin(b["phase"]) * 2.5)
                x = b["x"]*W + wobble*25; y = b["y"]*H
                b["ids"] = self._draw_bubble(x, y, r, b["col"])
            for rip in list(self._ripples):
                for i in rip["ids"]:
                    try: self.delete(i)
                    except: pass
                rip["ids"] = []
                rip["r"] += 0.007; rip["a"] -= 0.025
                if rip["a"] <= 0: self._ripples.remove(rip); continue
                rx = rip["x"]*W; ry = rip["y"]*H; rr = rip["r"]*min(W,H)
                col = lerp_color(BG_VOID, AC_MAIN, rip["a"] * 0.6)
                rip["ids"] = [self.create_oval(rx-rr, ry-rr, rx+rr, ry+rr,
                                               outline=col, fill="", width=2, stipple="gray50")]
            self.after(20, self._tick)
        except: pass
    def stop(self): self._running = False

class ToastManager:
    def __init__(self, root):
        self.root = root; self._toasts = []
    def show(self, message, kind="info", duration=3500):
        styles = {
            "info":    (BG_PANEL, BD_MID,    AC_MAIN,  "◈"),
            "success": (BG_PANEL, "#103820",  AC_GREEN, "✓"),
            "warning": (BG_PANEL, "#302000",  AC_ORANGE,"⚠"),
            "error":   (BG_PANEL, "#301020",  AC_RED,   "✕"),
            "update":  (BG_PANEL, "#200830",  AC_PURPLE,"⬆"),
        }
        bg, brd, acc, icon = styles.get(kind, styles["info"])
        self._toasts.append(self._create(message, bg, brd, acc, icon, duration))
        self._reposition()
    def _create(self, message, bg, brd, acc, icon, duration):
        W = self.root.winfo_width() or 1200
        frame = tk.Frame(self.root, bg=brd, padx=1, pady=1)
        inner = tk.Frame(frame, bg=bg); inner.pack(fill="both")
        tk.Frame(inner, bg=acc, height=2).pack(fill="x")
        row = tk.Frame(inner, bg=bg); row.pack(fill="x", padx=12, pady=9)
        tk.Label(row, text=icon, bg=bg, fg=acc, font=("Segoe UI",13,"bold")).pack(side="left", padx=(0,8))
        tk.Label(row, text=message, bg=bg, fg=TX_MAIN, font=("Segoe UI",9),
                 wraplength=220, justify="left").pack(side="left")
        tk.Button(row, text="×", bg=bg, fg=TX_DIM, relief="flat", bd=0,
                  cursor="hand2", font=("Segoe UI",10,"bold"),
                  command=lambda: self._dismiss(frame)).pack(side="right")
        frame.place(x=W+10, y=0, width=270)
        frame._target_x = W - 286
        frame.after(20, lambda: self._slide_in(frame, W+10, duration))
        return frame
    def _slide_in(self, frame, start_x, duration, step=0):
        if step >= 14:
            frame.after(duration, lambda: self._dismiss(frame)); return
        t = 1-(1-step/14)**3
        try:
            ti = frame.place_info(); y = int(ti.get("y","16"))
            x = int(start_x + (frame._target_x - start_x) * t)
            frame.place_configure(x=x, y=y)
            frame.after(18, lambda: self._slide_in(frame, start_x, duration, step+1))
        except: pass
    def _dismiss(self, frame):
        if frame not in self._toasts: return
        self._toasts.remove(frame); W = self.root.winfo_width() or 1200
        self._slide_out(frame, W+10)
    def _slide_out(self, frame, end_x, step=0):
        if step >= 10:
            try: frame.destroy()
            except: pass
            self._reposition(); return
        t = (step/10)**2
        try:
            ti = frame.place_info(); sx = int(ti.get("x", frame._target_x))
            frame.place_configure(x=int(sx + (end_x-sx)*t))
            frame.after(18, lambda: self._slide_out(frame, end_x, step+1))
        except: pass
    def _reposition(self):
        W = self.root.winfo_width() or 1200; y = 16
        for f in self._toasts:
            try:
                f.place_configure(x=f._target_x, y=y)
                f.update_idletasks(); y += f.winfo_height() + 6
            except: pass

def make_neon_entry(parent, textvariable, show="", placeholder="", width=None,
                    icon=None, bg=BG_ITEM, fg=TX_MAIN, accent=AC_MAIN):
    outer = tk.Frame(parent, bg=BD_DARK, padx=1, pady=1)
    inner = tk.Frame(outer, bg=bg); inner.pack(fill="x")
    row = tk.Frame(inner, bg=bg); row.pack(fill="x", padx=4, pady=2)
    if icon:
        tk.Label(row, text=icon, bg=bg, fg=TX_DIM, font=("Segoe UI", 11)).pack(side="left", padx=(6, 4))
    kw = dict(textvariable=textvariable, bg=bg, fg=fg, insertbackground=accent,
              relief="flat", font=("Segoe UI", 11), bd=6, show=show)
    if width: kw["width"] = width
    e = tk.Entry(row, **kw); e.pack(side="left", fill="x", expand=True, ipady=7)
    accent_line = tk.Frame(inner, bg=BD_DARK, height=2); accent_line.pack(fill="x", side="bottom")
    _hp = [False]
    if placeholder:
        e.insert(0, placeholder); e.configure(fg=TX_DIM); _hp[0] = True
    def _fi(ev):
        if _hp[0]: e.delete(0, "end"); e.configure(fg=fg); _hp[0] = False
        outer.configure(bg=accent); accent_line.configure(bg=accent)
        inner.configure(bg=BG_HOVER); row.configure(bg=BG_HOVER); e.configure(bg=BG_HOVER)
        if icon: row.winfo_children()[0].configure(bg=BG_HOVER, fg=accent)
    def _fo(ev):
        if not textvariable.get() and placeholder:
            e.configure(show=""); e.insert(0, placeholder); e.configure(fg=TX_DIM); _hp[0] = True
        outer.configure(bg=BD_DARK); accent_line.configure(bg=BD_DARK)
        inner.configure(bg=bg); row.configure(bg=bg); e.configure(bg=bg)
        if icon: row.winfo_children()[0].configure(bg=bg, fg=TX_DIM)
    e.bind("<FocusIn>", _fi); e.bind("<FocusOut>", _fo)
    e._hp = _hp; e._placeholder = placeholder
    outer.get_value = lambda: ("" if _hp[0] else e.get().strip())
    outer._entry = e
    return outer

def make_badge(parent, text, color=AC_MAIN, bg=None):
    _bg = bg or lerp_color(BG_VOID, color, 0.15)
    _brd = lerp_color(BG_VOID, color, 0.4)
    f = tk.Frame(parent, bg=_brd, padx=1, pady=1)
    inner = tk.Frame(f, bg=_bg); inner.pack()
    tk.Label(inner, text=text, bg=_bg, fg=color, font=("Segoe UI", 8, "bold"),
             padx=8, pady=3).pack()
    return f

def make_stat_card(parent, icon, title, value, color=AC_MAIN):
    _bg = lerp_color(BG_VOID, color, 0.08)
    outer = tk.Frame(parent, bg=color, padx=1, pady=1)
    inner = tk.Frame(outer, bg=_bg); inner.pack(fill="both", expand=True)
    tk.Frame(inner, bg=color, height=2).pack(fill="x")
    content = tk.Frame(inner, bg=_bg); content.pack(fill="both", padx=12, pady=10)
    top = tk.Frame(content, bg=_bg); top.pack(fill="x")
    tk.Label(top, text=icon, bg=_bg, fg=color, font=("Segoe UI", 16)).pack(side="left", padx=(0, 8))
    tk.Label(top, text=title, bg=_bg, fg=TX_DIM, font=("Segoe UI", 9)).pack(side="left", pady=4)
    val_lbl = tk.Label(content, text=value, bg=_bg, fg=color, font=("Segoe UI", 22, "bold"))
    val_lbl.pack(anchor="w", pady=(2, 0))
    return outer, val_lbl

# ══════════════════════════════════════════════════════
#  WING DRAWING HELPERS
# ══════════════════════════════════════════════════════
def draw_wings(canvas, cx, cy, s, fill_col="#d8f0ff", outline_col="#60b8e0",
               outline_shadow="#003366"):
    def feather(ox, oy, ang_deg, length, width):
        angle = math.radians(ang_deg); perp = angle + math.pi/2
        tip_x = ox + math.cos(angle)*length; tip_y = oy - math.sin(angle)*length
        hw = width*.48
        lx = ox + math.cos(perp)*hw; ly = oy - math.sin(perp)*hw
        rx = ox - math.cos(perp)*hw; ry = oy + math.sin(perp)*hw
        mf = 0.45
        mlx = ox + math.cos(angle)*length*mf + math.cos(perp)*hw*.9
        mly = oy - math.sin(angle)*length*mf - math.sin(perp)*hw*.9
        mrx = ox + math.cos(angle)*length*mf - math.cos(perp)*hw*.9
        mry = oy - math.sin(angle)*length*mf + math.sin(perp)*hw*.9
        canvas.create_polygon([lx,ly,mlx,mly,tip_x,tip_y,mrx,mry,rx,ry,ox,oy],
                              smooth=True, fill=fill_col, outline=outline_col, width=1)

    lf = [(-.05,.04,115,.55,.22),(-.12,.01,128,.65,.24),(-.20,-.04,142,.72,.25),
          (-.28,-.10,155,.88,.27),(-.35,-.18,168,.98,.28),(-.38,-.28,180,1.1,.28),
          (-.36,-.38,193,1.05,.26),(-.30,-.46,207,.92,.24),(-.20,-.52,222,.78,.21),(-.08,-.54,238,.62,.18)]
    rf = [(.05,.04,65,.55,.22),(.12,.01,52,.65,.24),(.20,-.04,38,.72,.25),
          (.28,-.10,25,.88,.27),(.35,-.18,12,.98,.28),(.38,-.28,0,1.1,.28),
          (.36,-.38,-13,1.05,.26),(.30,-.46,-27,.92,.24),(.20,-.52,-42,.78,.21),(.08,-.54,-58,.62,.18)]

    for feathers in (lf, rf):
        for dx, dy, ang, ln, wd in feathers:
            feather(cx+dx*s, cy+dy*s, ang, ln*s*1.35, wd*s*1.35)

    for rm, col in [(3.2, outline_shadow),(2.2, "#005588"),(1.5, "#0077aa")]:
        r = s*.13*rm
        canvas.create_oval(cx-r, cy-r, cx+r, cy+r, outline=col, fill="", width=1)
    r = s*.13
    canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill=AC_GLOW, outline=AC_MAIN, width=2)
    r2 = s*.065
    canvas.create_oval(cx-r2, cy-r2, cx+r2, cy+r2, fill=TX_WHITE, outline="")

# ══════════════════════════════════════════════════════
#  AUTH SCREEN
# ══════════════════════════════════════════════════════
class AuthScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Angels Launcher — Вход")
        self.configure(bg=BG_VOID)
        self.geometry("540x680"); self.resizable(False, False)
        self._activated = False; self._mode = "register"
        self._build(); self._apply_icon()

    def _apply_icon(self):
        try:
            img = self._make_icon(32)
            if img: self._icon = img; self.iconphoto(True, img)
        except: pass

    def _make_icon(self, size=32):
        try:
            W = H = size; pixels = [[(0,4,12)]*W for _ in range(H)]
            cx, cy = W//2, H//2
            def dp(x,y,r,g,b,a=1.0):
                if 0<=x<W and 0<=y<H:
                    br,bg_,bb = pixels[y][x]
                    pixels[y][x] = (int(br+(r-br)*a), int(bg_+(g-bg_)*a), int(bb+(b-bb)*a))
            def dl(x0,y0,x1,y1,r,g,b,a=0.9):
                dx,dy=abs(x1-x0),abs(y1-y0); sx=1 if x0<x1 else -1; sy=1 if y0<y1 else -1; err=dx-dy
                while True:
                    dp(x0,y0,r,g,b,a)
                    if x0==x1 and y0==y1: break
                    e2=2*err
                    if e2>-dy: err-=dy; x0+=sx
                    if e2<dx: err+=dx; y0+=sy
            sc=size/32.0
            for r in range(int(4*sc),0,-1):
                a=0.4+0.6*(1-r/(4*sc))
                for ang in range(0,360,4):
                    rad=math.radians(ang)
                    dp(int(cx+math.cos(rad)*r), int(cy+math.sin(rad)*r), 0, 200, 255, a)
            ppm3=b"P3\n"+f"{W} {H}\n255\n".encode()
            ppm3+=b"\n".join(b" ".join(f"{r} {g} {b}".encode() for r,g,b in row) for row in pixels)+b"\n"
            return tk.PhotoImage(data=ppm3)
        except: return None

    def _build(self):
        self._bg = StarfieldCanvas(self)
        self._bg.place(x=0, y=0, width=540, height=680)

        card = tk.Frame(self, bg=BD_MID, padx=1, pady=1)
        card.place(x=40, y=100, width=460, height=560)
        card_inner = tk.Frame(card, bg=BG_CARD); card_inner.pack(fill="both", expand=True)
        tk.Frame(card_inner, bg=AC_MAIN, height=3).pack(fill="x")

        hdr = tk.Frame(card_inner, bg=BG_PANEL); hdr.pack(fill="x")
        tk.Frame(hdr, bg=BD_DARK, height=1).pack(fill="x", side="bottom")

        wc = tk.Canvas(hdr, bg=BG_PANEL, width=50, height=50, highlightthickness=0)
        wc.pack(side="left", padx=(16, 8), pady=10)
        draw_wings(wc, 25, 28, 18)

        tf = tk.Frame(hdr, bg=BG_PANEL); tf.pack(side="left", pady=12)
        row_t = tk.Frame(tf, bg=BG_PANEL); row_t.pack(anchor="w")
        tk.Label(row_t, text="ANGELS", bg=BG_PANEL, fg=TX_WHITE,
                 font=("Segoe UI", 18, "bold")).pack(side="left")
        tk.Label(row_t, text=" LAUNCHER", bg=BG_PANEL, fg=AC_MAIN,
                 font=("Segoe UI", 18, "bold")).pack(side="left")
        tk.Label(tf, text=f"v{LAUNCHER_VER}  ·  Minecraft {MC_VERSION}",
                 bg=BG_PANEL, fg=TX_DIM, font=("Segoe UI", 9)).pack(anchor="w")

        tab_row = tk.Frame(card_inner, bg=BG_CARD); tab_row.pack(fill="x")
        self._tab_reg = tk.Label(tab_row, text="Регистрация", bg=BG_CARD, fg=AC_MAIN,
                                  font=("Segoe UI", 11, "bold"), cursor="hand2", padx=20, pady=12)
        self._tab_reg.pack(side="left")
        self._tab_log = tk.Label(tab_row, text="Войти", bg=BG_CARD, fg=TX_DIM,
                                  font=("Segoe UI", 11), cursor="hand2", padx=20, pady=12)
        self._tab_log.pack(side="left")
        self._tab_line = tk.Frame(tab_row, bg=AC_MAIN, height=2)
        tk.Frame(card_inner, bg=BD_DARK, height=1).pack(fill="x")

        self._reg_f = tk.Frame(card_inner, bg=BG_CARD)
        self._log_f = tk.Frame(card_inner, bg=BG_CARD)
        self._build_reg(self._reg_f)
        self._build_log(self._log_f)

        self._status_lbl = tk.Label(card_inner, text="", bg=BG_CARD, fg=AC_RED,
                                     font=("Segoe UI", 9), wraplength=420, justify="center", pady=6)
        self._status_lbl.pack(fill="x", padx=16, side="bottom")

        self._tab_reg.bind("<Button-1>", lambda e: self._switch("register"))
        self._tab_log.bind("<Button-1>", lambda e: self._switch("login"))
        self._switch("register")

    def _build_reg(self, f):
        self._reg_vars = []
        entries_cfg = [
            ("🔑", "Ключ активации", "ANGELS-XXXX-XXXX-XXXX", False),
            ("◈",  "Никнейм",        "Игровой ник",            False),
            ("🔒", "Пароль",          "Придумай пароль",         True),
        ]
        for icon, label, ph, secret in entries_cfg:
            block = tk.Frame(f, bg=BG_CARD); block.pack(fill="x", padx=20, pady=(12, 0))
            tk.Label(block, text=label, bg=BG_CARD, fg=TX_MID,
                     font=("Segoe UI", 9), anchor="w").pack(anchor="w", pady=(0, 4))
            var = tk.StringVar()
            entry_w = make_neon_entry(block, var, show="●" if secret else "", placeholder=ph, icon=icon)
            entry_w.pack(fill="x")
            self._reg_vars.append((var, entry_w))
        tk.Frame(f, bg=BD_DARK, height=1).pack(fill="x", padx=20, pady=16)
        make_action_button(f, "◈   АКТИВИРОВАТЬ И ВОЙТИ", command=self._do_reg, style="primary",
                            font=("Segoe UI", 12, "bold"), px=24, py=14).pack(fill="x", padx=20, pady=(0, 10))

    def _build_log(self, f):
        self._log_vars = []
        entries_cfg = [
            ("◈",  "Никнейм", "Игровой ник",  False),
            ("🔒", "Пароль",  "Твой пароль",   True),
        ]
        for icon, label, ph, secret in entries_cfg:
            block = tk.Frame(f, bg=BG_CARD); block.pack(fill="x", padx=20, pady=(16, 0))
            tk.Label(block, text=label, bg=BG_CARD, fg=TX_MID,
                     font=("Segoe UI", 9), anchor="w").pack(anchor="w", pady=(0, 4))
            var = tk.StringVar()
            entry_w = make_neon_entry(block, var, show="●" if secret else "", placeholder=ph, icon=icon)
            entry_w.pack(fill="x")
            self._log_vars.append((var, entry_w))
        tk.Frame(f, bg=BD_DARK, height=1).pack(fill="x", padx=20, pady=18)
        make_action_button(f, "→   ВОЙТИ", command=self._do_login, style="primary",
                            font=("Segoe UI", 12, "bold"), px=24, py=14).pack(fill="x", padx=20, pady=(0, 10))

    def _switch(self, mode):
        self._mode = mode
        self._reg_f.pack_forget(); self._log_f.pack_forget()
        if mode == "register":
            self._tab_reg.configure(fg=AC_MAIN, font=("Segoe UI", 11, "bold"))
            self._tab_log.configure(fg=TX_DIM, font=("Segoe UI", 11))
            self._tab_line.place(in_=self._tab_reg, x=0, rely=1.0, relwidth=1.0, height=2)
            self._reg_f.pack(fill="both", expand=True)
        else:
            self._tab_log.configure(fg=AC_MAIN, font=("Segoe UI", 11, "bold"))
            self._tab_reg.configure(fg=TX_DIM, font=("Segoe UI", 11))
            self._tab_line.place(in_=self._tab_log, x=0, rely=1.0, relwidth=1.0, height=2)
            self._log_f.pack(fill="both", expand=True)
        self._status_lbl.configure(text="")

    def _do_reg(self):
        key = self._reg_vars[0][1].get_value()
        nick = self._reg_vars[1][1].get_value()
        pw = self._reg_vars[2][1].get_value()
        self.after(90, lambda: self._check_reg(key, nick, pw))

    def _check_reg(self, key, nick, pw):
        ok, msg = activate_key(key, nick, pw)
        if ok:
            self._status_lbl.configure(text=f"✓  {msg}", fg=AC_GREEN)
            self.after(1000, self._launch_main)
        else:
            self._status_lbl.configure(text=f"✗  {msg}", fg=AC_RED)

    def _do_login(self):
        nick = self._log_vars[0][1].get_value()
        pw = self._log_vars[1][1].get_value()
        self.after(90, lambda: self._check_login(nick, pw))

    def _check_login(self, nick, pw):
        ok, msg = login_user(nick, pw)
        if ok:
            self._status_lbl.configure(text=f"✓  {msg}", fg=AC_GREEN)
            self.after(900, self._launch_main)
        else:
            self._status_lbl.configure(text=f"✗  {msg}", fg=AC_RED)

    def _launch_main(self):
        self._activated = True; self._bg.stop(); self.destroy()

# ══════════════════════════════════════════════════════
#  MAIN LAUNCHER
# ══════════════════════════════════════════════════════
class AngelsLauncher(tk.Tk):
    def __init__(self):
        super().__init__()
        user = get_current_user(); self._nick = user.get("nickname", "Angel")
        self._adm = is_admin(self._nick); self._user = user; self._logout_requested = False
        self.title(f"{LAUNCHER_NAME}  ·  Minecraft {MC_VERSION}")
        self.configure(bg=BG_VOID)
        sw = self.winfo_screenwidth(); sh = self.winfo_screenheight()
        W, H = 1240, 780
        self.geometry(f"{W}x{H}+{(sw-W)//2}+{(sh-H)//2}")
        self.minsize(1000, 680); self.resizable(True, True)
        self._mc_process = None; self._active_tab = "home"; self._fullscreen = False
        self.username = tk.StringVar(value=self._nick)
        self.ram = tk.IntVar(value=min(4, max(1, TOTAL_RAM//2)))
        self.status = tk.StringVar(value="Готов к запуску")
        self.eta_var = tk.StringVar(value="")
        self.spd_var = tk.StringVar(value="")
        self.progress = tk.DoubleVar(value=0)
        self.mod_url = tk.StringVar(value=_get_mod_url())
        self.servers = load_servers()
        self._connect_server = None
        self._updater = AutoUpdater()
        self._update_available = False; self._latest_update_info = None
        self._apply_icon(); self._build_ui()
        self._toast = ToastManager(self)
        self.bind("<F11>", self._toggle_fs)
        self.bind("<Escape>", lambda e: self._set_fs(False))
        self._log(f"◈  Angels Launcher v{LAUNCHER_VER} — Привет, {self._nick}!", "accent")
        if self._adm: self._log(f"   ⚡ Администратор", "gold")
        self._log(f"   RAM: {TOTAL_RAM} ГБ  |  Выделено: {self.ram.get()} ГБ", "info")
        self._log(f"   ◈ Пиратский режим АКТИВЕН — демо-режим отключён", "accent")
        self._check_sub_alert(); self._check_files()
        self._updater.watch_script(interval_ms=2000, root=self, on_change=self._on_script_changed)
        self.after(3000, self._bg_check_updates)

    def _apply_icon(self):
        try:
            img = AuthScreen._make_icon(self, 32)
            if img: self._icon = img; self.iconphoto(True, img)
        except: pass

    def _check_sub_alert(self):
        valid, status = check_subscription(self._user)
        if not valid: self._log(f"⚠  ПОДПИСКА ИСТЕКЛА! Продление: {TG_LINK}", "error")
        elif self._user.get("key_expires"): self._log(f"   ◈ Подписка: {status}", "info")

    def _bg_check_updates(self):
        def _cb(ok, info, err):
            if ok and info and self._updater.is_newer(info["version"]):
                self._update_available = True; self._latest_update_info = info
                self.after(0, self._show_update_badge)
                self.after(0, lambda: self._toast.show(
                    f"⬆ Доступно обновление v{info['version']}!", kind="update", duration=7000))
        self._updater.check_for_updates(_cb)

    def _show_update_badge(self):
        try:
            self._update_dot.configure(text="● ОБНОВЛЕНИЕ", fg=AC_GREEN)
            self.title(f"{LAUNCHER_NAME}  ·  MC {MC_VERSION}  ·  [ОБНОВЛЕНИЕ!]")
        except: pass

    def _on_script_changed(self):
        self._log("◈  Файл изменён — перезапуск через 3с...", "gold")
        self._toast.show("Файл изменён! Авто-перезапуск через 3с...", kind="update", duration=3000)
        self.after(3000, lambda: self._updater.auto_restart_on_change())

    def _toggle_fs(self, e=None): self._set_fs(not self._fullscreen)
    def _set_fs(self, state):
        self._fullscreen = state; self.attributes("-fullscreen", state)
        if not state:
            sw = self.winfo_screenwidth(); sh = self.winfo_screenheight()
            self.geometry(f"1240x780+{(sw-1240)//2}+{(sh-780)//2}")

    # ──────────────────────────────────────────────────
    #  BUILD UI
    # ──────────────────────────────────────────────────
    def _build_ui(self):
        self._bgc = StarfieldCanvas(self)
        self._bgc.place(x=0, y=0, relwidth=1, relheight=1)
        self._build_header()
        body = tk.Frame(self, bg=BG_VOID)
        body.place(x=0, y=100, relwidth=1, relheight=1, height=-100)
        self._build_sidebar(body)
        self._panels = {}
        right = tk.Frame(body, bg=BG_VOID)
        right.pack(fill="both", expand=True)
        self._panels["home"]    = self._mk_home(right)
        self._panels["profile"] = self._mk_profile(right)
        self._panels["multi"]   = self._mk_multi(right)
        self._panels["mods"]    = self._mk_mods(right)
        self._panels["console"] = self._mk_console(right)
        self._panels["updates"] = self._mk_updates(right)
        self._panels["settings"] = self._mk_settings(right)
        if self._adm: self._panels["admin"] = self._mk_admin(right)
        self._show("home")

    def _build_header(self):
        hdr = tk.Frame(self, bg=BG_CARD, height=100)
        hdr.place(x=0, y=0, relwidth=1)
        hdr.pack_propagate(False)
        tk.Frame(hdr, bg=AC_MAIN, height=2).pack(side="bottom", fill="x")
        inner = tk.Frame(hdr, bg=BG_CARD); inner.pack(fill="both", expand=True, padx=16)

        wc = tk.Canvas(inner, bg=BG_CARD, width=60, height=60, highlightthickness=0)
        wc.pack(side="left", pady=18, padx=(0, 8))
        draw_wings(wc, 30, 34, 20)

        tf = tk.Frame(inner, bg=BG_CARD); tf.pack(side="left", pady=20)
        title_row = tk.Frame(tf, bg=BG_CARD); title_row.pack(anchor="w")
        tk.Label(title_row, text="ANGELS", bg=BG_CARD, fg=TX_WHITE,
                 font=("Segoe UI", 20, "bold")).pack(side="left")
        tk.Label(title_row, text=" LAUNCHER", bg=BG_CARD, fg=AC_MAIN,
                 font=("Segoe UI", 20, "bold")).pack(side="left")
        sub_row = tk.Frame(tf, bg=BG_CARD); sub_row.pack(anchor="w")
        tk.Label(sub_row, text=f"MC {MC_VERSION}  ·  Forge {FORGE_VERSION}  ·  {MOD_NAME}  ·  🏴‍☠️ Pirate Mode",
                 bg=BG_CARD, fg=TX_DIM, font=("Segoe UI", 9)).pack(side="left")

        tk.Frame(inner, bg=BD_DARK, width=1).pack(side="left", fill="y", padx=20, pady=16)

        sf = tk.Frame(inner, bg=BG_CARD); sf.pack(side="left", pady=22)
        tk.Label(sf, text=f"RAM: {TOTAL_RAM} ГБ", bg=BG_CARD, fg=TX_DIM, font=("Segoe UI", 8)).pack(anchor="w")
        dot_row = tk.Frame(sf, bg=BG_CARD); dot_row.pack(anchor="w")
        self._dot = tk.Label(dot_row, text="●", bg=BG_CARD, fg=AC_GREEN, font=("Segoe UI", 9))
        self._dot.pack(side="left")
        tk.Label(dot_row, text=" ГОТОВ", bg=BG_CARD, fg=AC_MINT, font=("Segoe UI", 8, "bold")).pack(side="left")
        self._update_dot = tk.Label(sf, text="", bg=BG_CARD, fg=AC_GREEN, font=("Segoe UI", 8))
        self._update_dot.pack(anchor="w")
        self._pulse_dot()

        rf = tk.Frame(inner, bg=BG_CARD); rf.pack(side="right", pady=12)
        is_adm = self._adm
        prof_bg = lerp_color(BG_VOID, ADM_ACC if is_adm else AC_MAIN, 0.12)
        badge_brd = ADM_ACC if is_adm else AC_MAIN
        badge_outer = tk.Frame(rf, bg=badge_brd, padx=1, pady=1, cursor="hand2")
        badge_outer.pack(pady=(0, 4))
        badge_in = tk.Frame(badge_outer, bg=prof_bg); badge_in.pack(fill="both")
        tk.Frame(badge_in, bg=badge_brd, height=1).pack(fill="x")
        badge_row = tk.Frame(badge_in, bg=prof_bg); badge_row.pack(padx=14, pady=8)
        icon_c = ADM_ACC if is_adm else AC_MAIN
        tk.Label(badge_row, text="⚡" if is_adm else "◈", bg=prof_bg, fg=icon_c,
                 font=("Segoe UI", 11)).pack(side="left", padx=(0, 7))
        tk.Label(badge_row, text=self._nick, bg=prof_bg, fg=TX_WHITE,
                 font=("Segoe UI", 10, "bold")).pack(side="left")
        if is_adm: make_badge(badge_in, "ADMIN", ADM_ACC).pack(padx=10, pady=(0, 6), anchor="e")
        for w in [badge_outer, badge_in, badge_row]:
            try: w.bind("<Button-1>", lambda e: self._show("profile"))
            except: pass

        self._clk = tk.Label(rf, text="", bg=BG_CARD, fg=TX_DIM, font=("Segoe UI", 9))
        self._clk.pack(side="bottom")
        make_pill_button(rf, "⛶ F11", command=self._toggle_fs,
                          bg=BG_ITEM, fg=TX_DIM, hover_bg=BG_HOVER, hover_fg=TX_MID,
                          font=("Segoe UI", 8), px=10, py=4).pack(side="bottom", pady=3)
        self._tick_clock()

    def _pulse_dot(self):
        try:
            c = self._dot.cget("fg")
            self._dot.configure(fg=AC_GREEN if c==AC_MINT else AC_MINT)
            self.after(900, self._pulse_dot)
        except: pass

    def _tick_clock(self):
        try: self._clk.configure(text=time.strftime("⏱  %H:%M:%S")); self.after(1000, self._tick_clock)
        except: pass

    def _build_sidebar(self, body):
        side = tk.Frame(body, bg=BG_CARD, width=244)
        side.pack(side="left", fill="y"); side.pack_propagate(False)
        tk.Frame(side, bg=BD_MID, width=1).pack(side="right", fill="y")

        mc = tk.Canvas(side, bg=BG_CARD, width=36, height=26, highlightthickness=0)
        mc.pack(pady=(12, 0), padx=16, anchor="w")
        draw_wings(mc, 18, 15, 8)
        tk.Label(side, text="НАВИГАЦИЯ", bg=BG_CARD, fg=TX_DARK,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=18, pady=(2, 6))
        tk.Frame(side, bg=BD_DARK, height=1).pack(fill="x", padx=12)

        self._tabs = {}
        sections = [
            ("─── ГЛАВНАЯ ───", None),
            ("◈", "Главная",     "home",     False, AC_MAIN),
            ("◉", "Профиль",     "profile",  False, AC_CYAN),
            ("─── ИГРА ───", None),
            ("◐", "Серверы",     "multi",    False, AC_GLOW),
            ("◎", "Моды",        "mods",     False, AC_MINT),
            ("─── СИСТЕМА ───", None),
            ("▸", "Консоль",     "console",  False, AC_GOLD),
            ("⬆", "Обновления",  "updates",  False, AC_PURPLE),
            ("⚙", "Настройки",   "settings", False, TX_MID),
        ]
        if self._adm:
            sections += [("─── ADMIN ───", None), ("⚡", "Админ-панель", "admin", True, ADM_ACC)]

        for item in sections:
            if len(item) == 2:
                sf = tk.Frame(side, bg=BG_CARD); sf.pack(fill="x", padx=10, pady=(8, 2))
                tk.Frame(sf, bg=BD_DARK, height=1).pack(fill="x", side="left", expand=True, pady=6)
                lbl_col = ADM_ACC if "ADMIN" in item[0] else TX_DARK
                tk.Label(sf, text=f"  {item[0]}  ", bg=BG_CARD, fg=lbl_col,
                         font=("Segoe UI", 7, "bold")).pack(side="left")
                tk.Frame(sf, bg=BD_DARK, height=1).pack(fill="x", side="left", expand=True, pady=6)
                continue
            icon, name, key, is_adm_item, acc = item
            accent_col = ADM_ACC if is_adm_item else acc
            normal_fg = ADM_ACC if is_adm_item else TX_MID
            btn_bg = lerp_color(BG_VOID, ADM_BG, 0.5) if is_adm_item else BG_CARD
            btn = make_pill_button(side, name, command=lambda k=key: self._show(k),
                                    bg=btn_bg, fg=normal_fg, hover_bg=BG_HOVER, hover_fg=TX_WHITE,
                                    font=("Segoe UI", 11), px=14, py=8, icon=icon)
            btn.pack(fill="x", padx=6, pady=2)
            btn._key = key; btn._accent = accent_col; btn._normal_fg = normal_fg
            self._tabs[key] = btn

        tk.Frame(side, bg=BD_DARK, height=1).pack(fill="x", padx=12, pady=8)
        valid, status = check_subscription(self._user)
        sub_col = AC_GREEN if valid else AC_RED
        sub_bg = lerp_color(BG_VOID, sub_col, 0.08)
        sub_brd = lerp_color(BG_VOID, sub_col, 0.3)
        sf = tk.Frame(side, bg=sub_brd, padx=1, pady=1); sf.pack(fill="x", padx=10, pady=(0, 6))
        si = tk.Frame(sf, bg=sub_bg); si.pack(fill="both")
        tk.Frame(si, bg=sub_col, height=1).pack(fill="x")
        sr = tk.Frame(si, bg=sub_bg); sr.pack(padx=10, pady=7)
        tk.Label(sr, text=f"{'✓' if valid else '⚠'}  {status}", bg=sub_bg, fg=sub_col,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        if not valid:
            tk.Label(sr, text=f"Продление: {TG_LINK}", bg=sub_bg, fg=AC_RED,
                     font=("Segoe UI", 7)).pack(anchor="w")
        tk.Label(side, text=f"v{_read_installed_version()}  Neon Edition",
                 bg=BG_CARD, fg=TX_DARK, font=("Segoe UI", 7)).pack(side="bottom", pady=(0, 4))
        tk.Frame(side, bg=BD_DARK, height=1).pack(side="bottom", fill="x", padx=10)

    def _show(self, key):
        for p in self._panels.values(): p.pack_forget()
        for k, btn in self._tabs.items():
            is_active = (k == key)
            acc = getattr(btn, '_accent', AC_MAIN)
            normal_fg = getattr(btn, '_normal_fg', TX_MID)
            active_bg = lerp_color(BG_VOID, acc, 0.15)
            if is_active:
                btn.configure(bg=active_bg); btn._inner.configure(bg=active_bg); btn._row.configure(bg=active_bg)
                for lbl in btn._labels: lbl.configure(bg=active_bg, fg=acc)
                if not hasattr(btn, '_active_bar') or btn._active_bar is None:
                    bar = tk.Frame(btn, bg=acc, width=3)
                    bar.place(x=0, y=0, width=3, relheight=1); btn._active_bar = bar
                else:
                    btn._active_bar.configure(bg=acc); btn._active_bar.place(x=0, y=0, width=3, relheight=1)
            else:
                btn.configure(bg=BG_CARD); btn._inner.configure(bg=BG_CARD); btn._row.configure(bg=BG_CARD)
                for lbl in btn._labels: lbl.configure(bg=BG_CARD, fg=normal_fg)
                if hasattr(btn, '_active_bar') and btn._active_bar:
                    btn._active_bar.place_forget()
        self._panels[key].pack(fill="both", expand=True, padx=20, pady=16)
        self._active_tab = key

    def _section_header(self, parent, text, icon="◈", color=AC_MAIN):
        f = tk.Frame(parent, bg=BG_VOID); f.pack(fill="x", pady=(0, 14))
        row = tk.Frame(f, bg=BG_VOID); row.pack(fill="x")
        tk.Label(row, text=icon, bg=BG_VOID, fg=color, font=("Segoe UI", 14)).pack(side="left", padx=(0, 8))
        tk.Label(row, text=text, bg=BG_VOID, fg=TX_WHITE,
                 font=("Segoe UI", 15, "bold")).pack(side="left")
        tk.Frame(f, bg=BD_DARK, height=1).pack(fill="x", pady=(8, 0))
        return f

    def _neon_card(self, parent, accent=AC_MAIN, title=None, **pkw):
        outer = tk.Frame(parent, bg=accent, padx=1, pady=1); outer.pack(**pkw)
        inner = tk.Frame(outer, bg=BG_CARD); inner.pack(fill="both", expand=True)
        tk.Frame(inner, bg=accent, height=2).pack(fill="x")
        if title:
            th = tk.Frame(inner, bg=BG_PANEL); th.pack(fill="x")
            tk.Label(th, text=title, bg=BG_PANEL, fg=TX_MID,
                     font=("Segoe UI", 9, "bold"), anchor="w").pack(padx=14, pady=8, side="left")
            tk.Frame(inner, bg=BD_DARK, height=1).pack(fill="x")
        return inner

    # ──────────────────────────────────────────────────
    #  HOME PANEL — улучшенное меню с быстрыми кнопками
    # ──────────────────────────────────────────────────
    def _mk_home(self, parent):
        f = tk.Frame(parent, bg=BG_VOID)

        # Верхняя часть — информация + крылья
        top = tk.Frame(f, bg=BG_VOID); top.pack(fill="x", pady=(0, 8))

        left_top = tk.Frame(top, bg=BG_VOID); left_top.pack(side="left", fill="y")
        wc = tk.Canvas(left_top, bg=BG_VOID, width=120, height=70, highlightthickness=0)
        wc.pack()
        draw_wings(wc, 60, 42, 26)
        tk.Label(left_top, text="ANGELS LAUNCHER", bg=BG_VOID, fg=TX_WHITE,
                 font=("Segoe UI", 11, "bold")).pack()
        tk.Label(left_top, text=f"v{_read_installed_version()}  ·  MC {MC_VERSION}",
                 bg=BG_VOID, fg=TX_DIM, font=("Segoe UI", 8)).pack()

        # Быстрая информация справа
        right_top = tk.Frame(top, bg=BG_VOID); right_top.pack(side="left", fill="both", expand=True, padx=(16, 0))
        valid, sub_status = check_subscription(self._user)
        info_rows = [
            ("◈ Игрок",    self._nick,                           AC_MAIN),
            ("◉ Роль",     "⚡ ADMIN" if self._adm else "Игрок", ADM_ACC if self._adm else TX_MID),
            ("◎ Forge",    FORGE_VERSION,                         AC_GLOW),
            ("◈ Подписка", sub_status,                            AC_GREEN if valid else AC_RED),
            ("◈ RAM",      f"{self.ram.get()} / {TOTAL_RAM} ГБ", AC_MINT),
        ]
        info_card_outer = tk.Frame(right_top, bg=BD_MID, padx=1, pady=1)
        info_card_outer.pack(fill="both", expand=True)
        info_card = tk.Frame(info_card_outer, bg=BG_CARD); info_card.pack(fill="both")
        tk.Frame(info_card, bg=AC_MAIN, height=2).pack(fill="x")
        for i, (lbl, val, col) in enumerate(info_rows):
            rbg = BG_CARD if i%2==0 else lerp_color(BG_VOID, BG_ITEM, 0.5)
            r = tk.Frame(info_card, bg=rbg); r.pack(fill="x")
            tk.Label(r, text=lbl, bg=rbg, fg=TX_DIM, font=("Segoe UI", 9),
                     anchor="w", width=12).pack(side="left", padx=10, pady=4)
            tk.Label(r, text=val, bg=rbg, fg=col,
                     font=("Segoe UI", 9, "bold")).pack(side="right", padx=10)

        # Быстрые кнопки действий
        quick = tk.Frame(f, bg=BG_VOID); quick.pack(fill="x", pady=(6, 8))
        for icon, lbl, cmd, style in [
            ("◐", "Серверы",   lambda: self._show("multi"),    "ghost"),
            ("◎", "Моды",      lambda: self._show("mods"),     "ghost"),
            ("⚙", "Настройки", lambda: self._show("settings"), "ghost"),
            ("▸", "Консоль",   lambda: self._show("console"),  "ghost"),
        ]:
            btn = make_action_button(quick, f"{icon} {lbl}", command=cmd, style=style,
                                      font=("Segoe UI", 9), px=12, py=6)
            btn.pack(side="left", padx=3)

        # Статус и прогресс-бар
        meta = tk.Frame(f, bg=BG_VOID); meta.pack(fill="x", pady=(2, 2))
        tk.Label(meta, textvariable=self.status, bg=BG_VOID, fg=TX_MID,
                 font=("Segoe UI", 9), anchor="w").pack(side="left")
        tk.Label(meta, textvariable=self.eta_var, bg=BG_VOID, fg=AC_GLOW,
                 font=("Segoe UI", 9)).pack(side="right", padx=4)
        tk.Label(meta, textvariable=self.spd_var, bg=BG_VOID, fg=AC_MINT,
                 font=("Segoe UI", 9)).pack(side="right", padx=8)

        self._pb = NeonProgressBar(f, height=8, bg=BG_VOID, fg=AC_MAIN)
        self._pb.pack(fill="x", pady=(2, 8))
        self.progress.trace_add("write", lambda *_: self._pb.set(self.progress.get()/100))

        # Кнопка ИГРАТЬ — главная
        self.play_btn = GlowButton(f, "◈   ИГРАТЬ", command=self._start,
                                    bg=BG_CARD, fg=AC_MAIN, glow=AC_MAIN,
                                    font=("Segoe UI", 15, "bold"), height=68)
        self.play_btn.pack(fill="x")

        # Пиратский статус
        pirate_f = tk.Frame(f, bg=lerp_color(BG_VOID, AC_GOLD, 0.08),
                             highlightthickness=1,
                             highlightbackground=lerp_color(BG_VOID, AC_GOLD, 0.3))
        pirate_f.pack(fill="x", pady=(8, 0))
        tk.Frame(pirate_f, bg=AC_GOLD, height=1).pack(fill="x")
        tk.Label(pirate_f, text="  🏴‍☠️  Pirate Mode — демо-режим ОТКЛЮЧЁН  ·  Legacy запуск активен",
                 bg=lerp_color(BG_VOID, AC_GOLD, 0.08), fg=AC_GOLD,
                 font=("Segoe UI", 9), anchor="w").pack(padx=12, pady=8, side="left")
        return f

    # ──────────────────────────────────────────────────
    #  PROFILE
    # ──────────────────────────────────────────────────
    def _mk_profile(self, parent):
        f = tk.Frame(parent, bg=BG_VOID)
        self._section_header(f, "Личный кабинет", "◉", AC_CYAN)
        u = self._user

        card = self._neon_card(f, AC_MAIN, fill="x", pady=(0, 10))
        top = tk.Frame(card, bg=BG_CARD); top.pack(fill="x", padx=16, pady=14)

        av = tk.Canvas(top, bg=BG_CARD, width=80, height=80, highlightthickness=0)
        av.pack(side="left", padx=(0, 16))
        for r, col in [(39, BD_MID), (33, ADM_ACC if self._adm else AC_DIM), (27, ADM_ACC if self._adm else AC_MAIN)]:
            av.create_oval(40-r, 40-r, 40+r, 40+r, outline=col, fill="", width=1)
        av.create_oval(14, 14, 66, 66, fill=lerp_color(BG_VOID, BG_ITEM, 0.7), outline="")
        av.create_text(40, 40, text=self._nick[:2].upper(), fill=TX_WHITE, font=("Segoe UI", 18, "bold"))

        inf = tk.Frame(top, bg=BG_CARD); inf.pack(side="left", fill="y")
        tk.Label(inf, text=self._nick, bg=BG_CARD, fg=TX_WHITE,
                 font=("Segoe UI", 16, "bold"), anchor="w").pack(anchor="w")
        role_col = ADM_ACC if self._adm else AC_MAIN
        tk.Label(inf, text="⚡ Администратор" if self._adm else "◈ Игрок",
                 bg=BG_CARD, fg=role_col, font=("Segoe UI", 10)).pack(anchor="w")
        if u: tk.Label(inf, text=f"С нами с: {u.get('date', '—')[:10]}",
                        bg=BG_CARD, fg=TX_DIM, font=("Segoe UI", 9)).pack(anchor="w")

        valid, sub_status = check_subscription(u)
        sub_col = AC_GREEN if valid else AC_RED
        make_badge(top, f"{'✓' if valid else '⚠'} {sub_status}", sub_col).pack(side="right", padx=4)

        stats_row = tk.Frame(card, bg=BG_CARD); stats_row.pack(fill="x", padx=16, pady=(0, 14))
        stats_data = [
            ("◉", "Входов",        str(u.get("login_count", 1)) if u else "—", AC_MAIN),
            ("◈", "Последний вход", u.get("last_login","—")[:10] if u else "—", AC_CYAN),
            ("◎", "Тип ключа",     u.get("duration_label","∞") if u else "—", AC_GOLD),
        ]
        for icon, title, val, col in stats_data:
            sb = tk.Frame(stats_row, bg=lerp_color(BG_VOID, col, 0.08),
                          highlightthickness=1, highlightbackground=lerp_color(BG_VOID, col, 0.3))
            sb.pack(side="left", fill="x", expand=True, padx=4, ipady=8)
            tk.Frame(sb, bg=col, height=1).pack(fill="x")
            tk.Label(sb, text=f"{icon}  {title}", bg=lerp_color(BG_VOID, col, 0.08),
                     fg=TX_DIM, font=("Segoe UI", 8)).pack(pady=(4, 2))
            tk.Label(sb, text=val, bg=lerp_color(BG_VOID, col, 0.08),
                     fg=col, font=("Segoe UI", 10, "bold")).pack(pady=(0, 4))

        pw_card = self._neon_card(f, AC_GLOW, title="Изменить пароль", fill="x", pady=(0, 10))
        pr = tk.Frame(pw_card, bg=BG_CARD); pr.pack(fill="x", padx=16, pady=(8, 0))
        self._old_pw = tk.StringVar(); self._new_pw = tk.StringVar(); self._new_pw2 = tk.StringVar()
        for lbl_t, var, ph in [("Текущий", self._old_pw, "Текущий пароль"),
                                ("Новый",   self._new_pw, "Новый пароль"),
                                ("Повтор",  self._new_pw2, "Повторить")]:
            cf = tk.Frame(pr, bg=BG_CARD); cf.pack(side="left", fill="x", expand=True, padx=4)
            tk.Label(cf, text=lbl_t, bg=BG_CARD, fg=TX_DIM, font=("Segoe UI", 9)).pack(anchor="w")
            make_neon_entry(cf, var, show="●", placeholder=ph, icon="🔒").pack(fill="x")

        self._pw_st = tk.Label(pw_card, text="", bg=BG_CARD, fg=AC_RED, font=("Segoe UI", 9))
        self._pw_st.pack(anchor="w", padx=16, pady=(6, 0))
        btn_row = tk.Frame(pw_card, bg=BG_CARD); btn_row.pack(fill="x", padx=16, pady=(8, 14))
        make_action_button(btn_row, "Изменить пароль", command=self._change_pw,
                            style="ghost", font=("Segoe UI", 10, "bold"),
                            px=16, py=8, icon="🔒").pack(side="left")

        make_action_button(f, "⊘   Выйти из аккаунта", command=self._logout,
                            style="danger", font=("Segoe UI", 10), px=16, py=10).pack(anchor="w", pady=(6, 0))
        return f

    def _change_pw(self):
        old = self._old_pw.get().strip(); n1 = self._new_pw.get().strip(); n2 = self._new_pw2.get().strip()
        if not all([old, n1, n2]): self._pw_st.configure(text="Заполни все поля", fg=AC_RED); return
        if n1 != n2: self._pw_st.configure(text="Пароли не совпадают", fg=AC_RED); return
        if len(n1) < 4: self._pw_st.configure(text="Минимум 4 символа", fg=AC_RED); return
        try:
            d = json.loads(KEY_FILE.read_text()); kh = d.get("key_hash")
            users = _load_users(); u = users.get(kh, {})
            if u.get("password_hash") != hash_password(old):
                self._pw_st.configure(text="Неверный текущий пароль", fg=AC_RED); return
            u["password_hash"] = hash_password(n1); users[kh] = u; _save_users(users)
            self._pw_st.configure(text="✓  Пароль успешно изменён", fg=AC_GREEN)
            self._toast.show("Пароль изменён!", kind="success")
        except Exception as e:
            self._pw_st.configure(text=f"Ошибка: {e}", fg=AC_RED)

    def _logout(self):
        if messagebox.askyesno("Выход", "Выйти из аккаунта?", parent=self):
            try: KEY_FILE.unlink(missing_ok=True)
            except: pass
            self._logout_requested = True; self.destroy()

    # ──────────────────────────────────────────────────
    #  MULTI (SERVERS)
    # ──────────────────────────────────────────────────
    def _mk_multi(self, parent):
        f = tk.Frame(parent, bg=BG_VOID)
        tr = tk.Frame(f, bg=BG_VOID); tr.pack(fill="x", pady=(0, 10))
        tk.Label(tr, text="◐  Серверы", bg=BG_VOID, fg=TX_WHITE,
                 font=("Segoe UI", 15, "bold")).pack(side="left")
        make_action_button(tr, "+ Добавить", command=self._add_server_dlg,
                            style="ghost", font=("Segoe UI", 10, "bold"), px=14, py=7).pack(side="right")

        note = tk.Frame(f, bg=lerp_color(BG_VOID, AC_ORANGE, 0.08),
                        highlightthickness=1, highlightbackground=lerp_color(BG_VOID, AC_ORANGE, 0.4))
        note.pack(fill="x", pady=(0, 10))
        tk.Frame(note, bg=AC_ORANGE, height=2).pack(fill="x")
        tk.Label(note, text="  ⚠  AuthMe: введи /login <пароль> после подключения",
                 bg=lerp_color(BG_VOID, AC_ORANGE, 0.08), fg=AC_ORANGE,
                 font=("Segoe UI", 10), anchor="w").pack(padx=12, pady=9, side="left")

        self._srv_f = tk.Frame(f, bg=BG_VOID); self._srv_f.pack(fill="both", expand=True)
        self._refresh_servers()
        return f

    def _refresh_servers(self):
        for w in self._srv_f.winfo_children(): w.destroy()
        if not self.servers:
            ep = self._neon_card(self._srv_f, BD_MID, fill="x")
            tk.Label(ep, text="Нет серверов. Нажми «+ Добавить»",
                     bg=BG_CARD, fg=TX_DIM, font=("Segoe UI", 11), justify="center").pack(pady=28)
            return
        for i, srv in enumerate(self.servers):
            host = srv.get("host", ""); port = int(srv.get("port", 25565))
            out = tk.Frame(self._srv_f, bg=BD_MID, padx=1, pady=1); out.pack(fill="x", pady=5)
            row = tk.Frame(out, bg=BG_CARD); row.pack(fill="x")
            tk.Frame(row, bg=BD_DARK, height=1).pack(fill="x")
            inn = tk.Frame(row, bg=BG_CARD); inn.pack(fill="x", padx=14, pady=12)
            sl = tk.Label(inn, text="●", bg=BG_CARD, fg=TX_DIM, font=("Segoe UI", 14))
            sl.pack(side="left", padx=(0, 12))
            inf = tk.Frame(inn, bg=BG_CARD); inf.pack(side="left", fill="y")
            tk.Label(inf, text=srv.get("name", host), bg=BG_CARD, fg=TX_MAIN,
                     font=("Segoe UI", 11, "bold"), anchor="w").pack(anchor="w")
            tk.Label(inf, text=f"{host}:{port}", bg=BG_CARD, fg=TX_DIM,
                     font=("Segoe UI", 9), anchor="w").pack(anchor="w")
            bf = tk.Frame(inn, bg=BG_CARD); bf.pack(side="right")
            make_action_button(bf, "Пинг", command=lambda h=host,p=port,l=sl: self._ping(h,p,l),
                                style="ghost", px=10, py=5, font=("Segoe UI", 9)).pack(side="left", padx=3)
            make_action_button(bf, "▶ Играть", command=lambda h=host,p=port: self._start_with(h,p),
                                style="primary", px=12, py=5, font=("Segoe UI", 10, "bold")).pack(side="left", padx=3)
            make_action_button(bf, "✕", command=lambda i=i: self._del_server(i),
                                style="danger", px=8, py=5, font=("Segoe UI", 10)).pack(side="left", padx=3)

    def _ping(self, host, port, lbl):
        def do():
            ok = check_server_ping(host, port)
            lbl.configure(fg=AC_GREEN if ok else AC_RED)
            self._toast.show(f"{host}:{port} {'онлайн ✓' if ok else 'недоступен ✕'}",
                             kind="success" if ok else "warning")
        threading.Thread(target=do, daemon=True).start()
        lbl.configure(fg=AC_ORANGE)

    def _del_server(self, idx):
        if 0 <= idx < len(self.servers):
            self.servers.pop(idx); save_servers(self.servers); self._refresh_servers()
            self._toast.show("Сервер удалён", kind="info")

    def _add_server_dlg(self):
        dlg = tk.Toplevel(self); dlg.title("Добавить сервер")
        dlg.configure(bg=BG_CARD); dlg.geometry("460x300"); dlg.resizable(False, False); dlg.grab_set()
        tk.Frame(dlg, bg=AC_MAIN, height=2).pack(fill="x")
        tk.Label(dlg, text="Добавить сервер", bg=BG_CARD, fg=TX_WHITE,
                 font=("Segoe UI", 13, "bold")).pack(pady=(16, 12))
        nv = tk.StringVar(); hv = tk.StringVar(); pv = tk.StringVar(value="25565")
        for lt, var, ph, icon in [("Название", nv, "Мой сервер", "◈"),
                                    ("IP-адрес", hv, "play.server.net", "◐"),
                                    ("Порт",     pv, "25565", "◎")]:
            r = tk.Frame(dlg, bg=BG_CARD); r.pack(fill="x", padx=20, pady=4)
            tk.Label(r, text=lt, bg=BG_CARD, fg=TX_MID, font=("Segoe UI", 10),
                     width=9, anchor="w").pack(side="left")
            make_neon_entry(r, var, placeholder=ph, icon=icon).pack(side="left", fill="x", expand=True)
        def save():
            h = hv.get().strip()
            if not h: messagebox.showwarning("Ошибка", "Введи адрес!", parent=dlg); return
            try: p = int(pv.get().strip() or "25565")
            except: p = 25565
            self.servers.append({"name": nv.get().strip() or h, "host": h, "port": p})
            save_servers(self.servers); self._refresh_servers()
            self._toast.show(f"Сервер добавлен: {h}:{p}", kind="success"); dlg.destroy()
        make_action_button(dlg, "◈  Сохранить", command=save, style="primary",
                            font=("Segoe UI", 11, "bold"), px=20, py=12).pack(fill="x", padx=20, pady=14)

    def _start_with(self, host, port):
        self._show("home"); self._connect_server = (host, port); self._start()

    # ──────────────────────────────────────────────────
    #  MODS
    # ──────────────────────────────────────────────────
    def _mk_mods(self, parent):
        f = tk.Frame(parent, bg=BG_VOID)
        self._section_header(f, "Установленные моды", "◎", AC_MINT)
        for icon, name, desc, col, version in [
            ("⚙", "Minecraft Forge", "Загрузчик модов", AC_GLOW, FORGE_VERSION),
            ("◈", MOD_NAME, "Основной мод лаунчера — Angels Mod", AC_MAIN, MOD_VERSION)
        ]:
            out = tk.Frame(f, bg=lerp_color(BG_VOID, col, 0.25), padx=1, pady=1)
            out.pack(fill="x", pady=6)
            cf = tk.Frame(out, bg=BG_CARD); cf.pack(fill="x")
            tk.Frame(cf, bg=col, width=4).pack(side="left", fill="y")
            lf_ = tk.Frame(cf, bg=BG_CARD); lf_.pack(side="left", padx=14, pady=14)
            tk.Label(lf_, text=icon, bg=BG_CARD, fg=col, font=("Segoe UI", 22), width=2).pack(side="left")
            inf = tk.Frame(lf_, bg=BG_CARD); inf.pack(side="left", padx=10)
            tk.Label(inf, text=name, bg=BG_CARD, fg=TX_WHITE,
                     font=("Segoe UI", 11, "bold"), anchor="w").pack(anchor="w")
            tk.Label(inf, text=f"{desc}  ·  v{version}", bg=BG_CARD, fg=TX_DIM,
                     font=("Segoe UI", 10), anchor="w").pack(anchor="w")
            make_badge(cf, "◈ АКТИВЕН", AC_GREEN).pack(side="right", padx=14, pady=14)

        # Информация об URL мода
        url_info = tk.Frame(f, bg=lerp_color(BG_VOID, AC_GLOW, 0.08),
                             highlightthickness=1, highlightbackground=lerp_color(BG_VOID, AC_GLOW, 0.3))
        url_info.pack(fill="x", pady=(8, 0))
        tk.Frame(url_info, bg=AC_GLOW, height=1).pack(fill="x")
        tk.Label(url_info, text=f"  ◈  URL мода: {_get_mod_url()[:60]}...",
                 bg=lerp_color(BG_VOID, AC_GLOW, 0.08), fg=AC_GLOW,
                 font=("Cascadia Code", 8), anchor="w").pack(padx=12, pady=8)
        return f

    # ──────────────────────────────────────────────────
    #  CONSOLE
    # ──────────────────────────────────────────────────
    def _mk_console(self, parent):
        f = tk.Frame(parent, bg=BG_VOID)
        top = tk.Frame(f, bg=BG_VOID); top.pack(fill="x", pady=(0, 8))
        tk.Label(top, text="▸  Консоль", bg=BG_VOID, fg=TX_WHITE,
                 font=("Segoe UI", 14, "bold")).pack(side="left")
        make_badge(top, "⚡ ADMIN" if self._adm else "◈ USER",
                    ADM_ACC if self._adm else TX_MID).pack(side="left", padx=10, pady=2)
        make_action_button(top, "Очистить", command=self._clear_con,
                            style="ghost", px=10, py=4, font=("Segoe UI", 9)).pack(side="right")

        out = tk.Frame(f, bg=lerp_color(BG_VOID, ADM_ACC if self._adm else AC_MAIN, 0.4), padx=1, pady=1)
        out.pack(fill="both", expand=True)
        inn = tk.Frame(out, bg=BG_VOID); inn.pack(fill="both", expand=True)
        tk.Frame(inn, bg=ADM_ACC if self._adm else AC_MAIN, height=2).pack(fill="x")

        style = ttk.Style(); style.theme_use("default")
        style.configure("Con.Vertical.TScrollbar", background=BG_ITEM, troughcolor=BG_VOID,
                        arrowcolor=AC_MAIN, bordercolor=BD_DARK)
        self.console = tk.Text(inn, bg="#000c18", fg=AC_MINT, font=("Cascadia Code", 10),
                               relief="flat", state="disabled", wrap="word", bd=10,
                               selectbackground=BG_HOVER, insertbackground=AC_MAIN, spacing3=2)
        sb = ttk.Scrollbar(inn, command=self.console.yview, style="Con.Vertical.TScrollbar")
        self.console.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y"); self.console.pack(fill="both", expand=True)

        inp_out = tk.Frame(f, bg=BD_MID, padx=1, pady=1); inp_out.pack(fill="x", pady=(6, 0))
        inp_inn = tk.Frame(inp_out, bg=BG_ITEM); inp_inn.pack(fill="x")
        tk.Frame(inp_inn, bg=BD_DARK, height=1).pack(fill="x")
        prow = tk.Frame(inp_inn, bg=BG_ITEM); prow.pack(fill="x")
        pt = "⚡" if self._adm else "◈"
        tk.Label(prow, text=f"  {pt} {self._nick}> ", bg=BG_ITEM,
                 fg=ADM_ACC if self._adm else AC_MAIN,
                 font=("Cascadia Code", 10, "bold")).pack(side="left")
        self._cin = tk.StringVar()
        self._ent = tk.Entry(prow, textvariable=self._cin, bg=BG_ITEM, fg=TX_MAIN,
                             insertbackground=AC_MAIN, relief="flat",
                             font=("Cascadia Code", 10), bd=8)
        self._ent.pack(side="left", fill="x", expand=True, ipady=7)
        self._ent.bind("<Return>", self._con_send)
        self._ent.bind("<Up>", self._hist_up)
        self._ent.bind("<Down>", self._hist_dn)
        make_action_button(prow, "↵", command=self._con_send, style="ghost",
                            px=12, py=7, font=("Segoe UI", 10)).pack(side="right")
        self._cmd_hist = []; self._hist_pos = -1
        tk.Label(f, text="'help' — справка  ·  ↑↓ — история",
                 bg=BG_VOID, fg=TX_DARK, font=("Segoe UI", 8)).pack(anchor="w", pady=(4, 0))
        return f

    def _con_send(self, e=None):
        cmd = self._cin.get().strip()
        if not cmd: return
        self._ent.delete(0, "end")
        if not self._cmd_hist or self._cmd_hist[-1] != cmd: self._cmd_hist.append(cmd)
        self._hist_pos = -1; self._log(f"▸ {cmd}", "cmd"); self._handle_cmd(cmd)

    def _hist_up(self, e=None):
        if not self._cmd_hist: return
        if self._hist_pos == -1: self._hist_pos = len(self._cmd_hist)-1
        elif self._hist_pos > 0: self._hist_pos -= 1
        self._ent.delete(0, "end"); self._ent.insert(0, self._cmd_hist[self._hist_pos])

    def _hist_dn(self, e=None):
        if self._hist_pos == -1: return
        self._hist_pos += 1; self._ent.delete(0, "end")
        if self._hist_pos >= len(self._cmd_hist): self._hist_pos = -1
        else: self._ent.insert(0, self._cmd_hist[self._hist_pos])

    def _handle_cmd(self, cmd):
        parts = cmd.split(); c = parts[0].lower() if parts else ""
        if c == "help":
            self._log("  Команды:", "info")
            base = [("help","справка"),("clear","очистить"),("version","версия"),
                    ("ram <гб>","RAM"),("nick <имя>","ник"),("ping <host>","пинг"),
                    ("check <ключ>","проверить ключ"),("reinstall","Forge"),
                    ("sub","подписка"),("update","обновления"),("exit","закрыть")]
            adm = [("keygen [n]","⚡ ключи"),("tkey <сек>","⚡ тайм-ключ"),
                   ("users","⚡ игроки"),("ban <ник>","⚡ бан"),
                   ("unban <ник>","⚡ разбан"),("deluser <ник>","⚡ удалить"),
                   ("stats","⚡ статистика")] if self._adm else []
            for name, desc in base + adm:
                self._log(f"  {name:<26} — {desc}", "gold" if "⚡" in desc else "muted")
        elif c == "clear": self._clear_con()
        elif c == "version":
            self._log(f"  Angels Launcher v{_read_installed_version()} Neon Edition", "accent")
            self._log(f"  MC {MC_VERSION}  ·  Forge {FORGE_VERSION}", "info")
        elif c == "sub":
            valid, status = check_subscription(self._user)
            self._log(f"  Подписка: {status}", "accent" if valid else "error")
        elif c == "update":
            self._log("  Проверка...", "info")
            def _cb(ok, info, err):
                if ok and info:
                    if self._updater.is_newer(info["version"]): self._log(f"  ⬆ Доступно v{info['version']}!", "gold")
                    else: self._log(f"  ✓ Последняя версия", "accent")
                else: self._log(f"  ✗ Ошибка: {err}", "error")
            self._updater.check_for_updates(_cb)
        elif c == "check" and len(parts) > 1:
            ok = validate_key(parts[1])
            self._log(f"  {parts[1]} → {'✓ Валидный' if ok else '✗ Неверный'}", "accent" if ok else "error")
        elif c == "ram" and len(parts) > 1:
            try: n = max(1, min(int(parts[1]), TOTAL_RAM)); self.ram.set(n); self._log(f"  RAM: {n} ГБ", "accent")
            except: self._log("  Ошибка: ram <число>", "error")
        elif c == "nick" and len(parts) > 1:
            self.username.set(parts[1]); self._log(f"  Ник: {parts[1]}", "accent")
        elif c == "ping" and len(parts) > 1:
            host = parts[1]; port = int(parts[2]) if len(parts) > 2 else 25565
            self._log(f"  Пинг {host}:{port}...", "info")
            def dp():
                ok = check_server_ping(host, port)
                self._log(f"  {host}:{port} → {'◈ Онлайн' if ok else '✕ Оффлайн'}", "accent" if ok else "error")
            threading.Thread(target=dp, daemon=True).start()
        elif c == "reinstall": self._reinstall()
        elif c == "exit": self.destroy()
        elif c in ("keygen","tkey","users","ban","unban","deluser","stats"):
            if not self._adm: self._log("  ✗ Доступ запрещён", "error"); return
            if c == "keygen":
                try: n = min(int(parts[1]) if len(parts) > 1 else 5, 100)
                except: n = 5
                self._log(f"  ⚡ {n} ключей:", "gold")
                for k in [generate_key() for _ in range(n)]: self._log(f"  {k}", "accent")
            elif c == "tkey":
                try: sec = int(parts[1]) if len(parts) > 1 else 0
                except: sec = 0
                k = generate_timed_key(sec); self._log(f"  ⚡ [{fmt_duration(sec)}]: {k}", "gold")
            elif c == "users":
                users = _load_users(); bl = _load_blacklist()
                self._log(f"  ⚡ Игроков: {len(users)}", "gold")
                for kh, u in list(users.items())[:30]:
                    bk = "⊘ " if kh in bl else "  "; _, sub = check_subscription(u)
                    self._log(f"  {bk}{u.get('nickname','?'):16s} | {sub}", "muted")
            elif c == "stats":
                users = _load_users(); used = _load_used_keys(); bl = _load_blacklist()
                today = time.strftime("%Y-%m-%d")
                lt = sum(1 for u in users.values() if u.get("last_login","").startswith(today))
                self._log(f"  Игроков: {len(users)}  Ключей: {len(used)}  Бан: {len(bl)}  Сегодня: {lt}", "info")
            elif c in ("ban","unban","deluser") and len(parts) > 1:
                target = parts[1].lower(); users = _load_users()
                for kh, u in list(users.items()):
                    if u.get("nickname","").lower() == target:
                        if c == "ban":
                            bl = _load_blacklist(); bl.add(kh); _save_blacklist(bl)
                            self._log(f"  ⚡ Заблокирован: {u.get('nickname')}", "gold")
                        elif c == "unban":
                            bl = _load_blacklist(); bl.discard(kh); _save_blacklist(bl)
                            self._log(f"  ⚡ Разблокирован: {u.get('nickname')}", "gold")
                        else:
                            del users[kh]; _save_users(users)
                            used = _load_used_keys(); used.discard(kh); _save_used_keys(used)
                            self._log(f"  ⚡ Удалён: {u.get('nickname')}", "gold")
                        return
                self._log(f"  ✗ Не найден: {parts[1]}", "error")
        else: self._log(f"  Неизвестная команда: {cmd}  (введи 'help')", "warn")

    # ──────────────────────────────────────────────────
    #  SETTINGS — улучшенные
    # ──────────────────────────────────────────────────
    def _mk_settings(self, parent):
        f = tk.Frame(parent, bg=BG_VOID)
        self._section_header(f, "Настройки", "⚙", TX_MID)

        def setting_row(label, desc, widget_fn):
            outer = tk.Frame(f, bg=lerp_color(BG_VOID, BD_MID, 0.5), padx=1, pady=1)
            outer.pack(fill="x", pady=4)
            row = tk.Frame(outer, bg=BG_CARD); row.pack(fill="x")
            tk.Frame(row, bg=BD_DARK, height=1).pack(fill="x")
            lf_ = tk.Frame(row, bg=BG_CARD); lf_.pack(side="left", padx=16, pady=12)
            tk.Label(lf_, text=label, bg=BG_CARD, fg=TX_MAIN, font=("Segoe UI", 11), anchor="w").pack(anchor="w")
            if desc: tk.Label(lf_, text=desc, bg=BG_CARD, fg=TX_DIM, font=("Segoe UI", 9), anchor="w").pack(anchor="w")
            widget_fn(row)

        def mk_nick(r):
            make_neon_entry(r, self.username, placeholder="Никнейм", icon="◈").pack(
                side="right", padx=14, pady=10, ipadx=6)

        def mk_ram(r):
            fr = tk.Frame(r, bg=BG_CARD); fr.pack(side="right", padx=14, pady=10)
            mx = min(TOTAL_RAM-1, 16) if TOTAL_RAM > 2 else TOTAL_RAM
            tk.Label(fr, text=f"/ {TOTAL_RAM} ГБ", bg=BG_CARD, fg=TX_DIM, font=("Segoe UI", 9)).pack(side="right", padx=4)
            tk.Label(fr, textvariable=self.ram, bg=BG_CARD, fg=AC_MAIN,
                     font=("Segoe UI", 13, "bold"), width=2).pack(side="right")
            tk.Scale(fr, from_=1, to=mx, orient="horizontal", variable=self.ram,
                     bg=BG_CARD, fg=AC_MAIN, troughcolor=BG_ITEM, highlightthickness=0,
                     activebackground=AC_MAIN, showvalue=False, length=180, sliderlength=20).pack(side="right")

        def mk_fs(r):
            make_action_button(r, "⛶  F11 — переключить", command=self._toggle_fs,
                                style="ghost", px=14, py=7, font=("Segoe UI", 10)).pack(side="right", padx=14, pady=12)

        def mk_path(r):
            pf = tk.Frame(r, bg=BG_ITEM, highlightthickness=1, highlightbackground=BD_DARK)
            pf.pack(side="right", padx=14, pady=12)
            tk.Frame(pf, bg=BD_DARK, height=1).pack(fill="x")
            tk.Label(pf, text=f"  {MC_DIR}  ", bg=BG_ITEM, fg=TX_DIM, font=("Cascadia Code", 8)).pack(padx=4, pady=6)

        def mk_url(r):
            fr = tk.Frame(r, bg=BG_CARD); fr.pack(side="right", padx=14, pady=10, fill="x", expand=True)
            make_neon_entry(fr, self.mod_url, icon="🔗").pack(fill="x")
            def save_url():
                new_url = self.mod_url.get().strip()
                if new_url:
                    _save_mod_url_config(new_url)
                    self._toast.show("URL мода сохранён!", kind="success")
            make_action_button(fr, "Сохранить URL", command=save_url,
                                style="ghost", px=10, py=4, font=("Segoe UI", 9)).pack(anchor="e", pady=(4, 0))

        setting_row("Никнейм в Minecraft", "Офлайн-имя игрока (Pirate Mode)", mk_nick)
        setting_row("Оперативная память", f"Система: {TOTAL_RAM} ГБ", mk_ram)
        setting_row("Полный экран", "F11 — переключить", mk_fs)
        setting_row("Папка Minecraft", "Расположение файлов", mk_path)
        setting_row("Ссылка на мод", "Google Drive или прямая ссылка (сохрани для обновления)", mk_url)

        # Информация о пиратском режиме
        pirate_info = self._neon_card(f, AC_GOLD, title="🏴‍☠️ Pirate Mode Info", fill="x", pady=(14, 0))
        info_rows = [
            "✓  --userType legacy  — отключает проверку лицензии",
            "✓  --accessToken 0    — не требует настоящего токена",
            "✓  --uuid <random>    — случайный UUID для каждой сессии",
            "✓  Demo Mode DISABLED — убраны флаги isDemoUser",
            "✓  Работает как Legacy Launcher",
        ]
        for row_txt in info_rows:
            tk.Label(pirate_info, text=f"  {row_txt}", bg=BG_CARD, fg=TX_MID,
                     font=("Cascadia Code", 9), anchor="w").pack(fill="x", padx=8, pady=2)

        tk.Frame(f, bg=BD_DARK, height=1).pack(fill="x", pady=14)
        make_action_button(f, "⚠  Переустановить Forge", command=self._reinstall,
                            style="danger", px=14, py=9, font=("Segoe UI", 10)).pack(anchor="w")
        return f

    # ──────────────────────────────────────────────────
    #  UPDATES
    # ──────────────────────────────────────────────────
    def _mk_updates(self, parent):
        f = tk.Frame(parent, bg=BG_VOID)
        self._section_header(f, "Обновления лаунчера", "⬆", AC_PURPLE)

        cur_card = self._neon_card(f, AC_MAIN, fill="x", pady=(0, 10))
        cr = tk.Frame(cur_card, bg=BG_CARD); cr.pack(fill="x", padx=16, pady=12)
        installed_v = _read_installed_version()
        vrow = tk.Frame(cr, bg=BG_CARD); vrow.pack(anchor="w")
        tk.Label(vrow, text=f"v{installed_v}", bg=BG_CARD, fg=AC_MAIN,
                 font=("Segoe UI", 24, "bold")).pack(side="left")
        tk.Label(vrow, text="  Neon Edition  —  установленная", bg=BG_CARD, fg=TX_DIM,
                 font=("Segoe UI", 10)).pack(side="left", pady=8)
        tk.Label(cr, text=f"GitHub: {GITHUB_REPO}", bg=BG_CARD, fg=TX_DIM,
                 font=("Cascadia Code", 8)).pack(anchor="w", pady=(4, 0))

        self._upd_status_frame = tk.Frame(f, bg=BG_VOID)
        self._upd_status_frame.pack(fill="x", pady=(0, 8))
        self._upd_prog_bar = NeonProgressBar(f, height=6, bg=BG_VOID, fg=AC_PURPLE)
        self._upd_prog_bar.pack(fill="x", pady=(0, 4))
        self._upd_prog_lbl = tk.Label(f, text="", bg=BG_VOID, fg=TX_MID, font=("Segoe UI", 9))
        self._upd_prog_lbl.pack(anchor="w", pady=(0, 8))

        self._upd_btn_frame = tk.Frame(f, bg=BG_VOID)
        self._upd_btn_frame.pack(fill="x", pady=(0, 12))
        self._build_update_button()

        self._upd_log_card = self._neon_card(f, AC_PURPLE, title="Список изменений", fill="both", pady=(0, 0), expand=True)
        self._upd_log_text = tk.Text(self._upd_log_card, bg=BG_VOID, fg=TX_MID,
                                     font=("Cascadia Code", 9), relief="flat",
                                     state="disabled", wrap="word", bd=10, height=8)
        self._upd_log_text.pack(fill="both", expand=True)
        self._upd_log_text.configure(state="normal")
        self._upd_log_text.insert("end", "Нажми «Проверить обновления» для просмотра changelog.")
        self._upd_log_text.configure(state="disabled")
        return f

    def _build_update_button(self):
        for w in self._upd_btn_frame.winfo_children(): w.destroy()
        if self._update_available and self._latest_update_info:
            ver = self._latest_update_info["version"]; iv = _read_installed_version()
            size = self._latest_update_info.get("size", 0); sz_str = f"  ({fmt_size(size)})" if size else ""
            outer = tk.Frame(self._upd_btn_frame, bg=AC_GREEN, padx=2, pady=2); outer.pack(fill="x")
            inn = tk.Frame(outer, bg=lerp_color(BG_VOID, AC_GREEN, 0.1)); inn.pack(fill="x")
            tk.Frame(inn, bg=AC_GREEN, height=2).pack(fill="x")
            r = tk.Frame(inn, bg=lerp_color(BG_VOID, AC_GREEN, 0.1)); r.pack(fill="x", padx=18, pady=14)
            tk.Label(r, text="⬆", bg=lerp_color(BG_VOID, AC_GREEN, 0.1), fg=AC_GREEN,
                     font=("Segoe UI", 28)).pack(side="left", padx=(0, 12))
            ic = tk.Frame(r, bg=lerp_color(BG_VOID, AC_GREEN, 0.1)); ic.pack(side="left", fill="y")
            tk.Label(ic, text=f"Обновление v{ver}{sz_str}",
                     bg=lerp_color(BG_VOID, AC_GREEN, 0.1), fg=AC_GREEN,
                     font=("Segoe UI", 13, "bold"), anchor="w").pack(anchor="w")
            tk.Label(ic, text=f"v{iv}  →  v{ver}",
                     bg=lerp_color(BG_VOID, AC_GREEN, 0.1), fg=TX_MID,
                     font=("Segoe UI", 10), anchor="w").pack(anchor="w")
            br = tk.Frame(inn, bg=lerp_color(BG_VOID, AC_GREEN, 0.1)); br.pack(fill="x", padx=18, pady=(4, 14))
            self._do_upd_btn = make_action_button(br, "⬇  СКАЧАТЬ И ОБНОВИТЬ",
                                                   command=self._do_update_now, style="success",
                                                   font=("Segoe UI", 13, "bold"), px=22, py=13)
            self._do_upd_btn.pack(side="left")
        else:
            outer = tk.Frame(self._upd_btn_frame, bg=BD_MID, padx=1, pady=1); outer.pack(fill="x")
            inn = tk.Frame(outer, bg=BG_CARD); inn.pack(fill="x")
            tk.Frame(inn, bg=AC_MAIN, height=2).pack(fill="x")
            r = tk.Frame(inn, bg=BG_CARD); r.pack(fill="x", padx=18, pady=14)
            tk.Label(r, text="◈", bg=BG_CARD, fg=AC_MAIN, font=("Segoe UI", 24)).pack(side="left", padx=(0, 12))
            ic = tk.Frame(r, bg=BG_CARD); ic.pack(side="left", fill="y")
            self._chk_status = tk.Label(ic, text="Нажми чтобы проверить обновления",
                                         bg=BG_CARD, fg=TX_MAIN, font=("Segoe UI", 12, "bold"), anchor="w")
            self._chk_status.pack(anchor="w")
            tk.Label(ic, text=f"Установлена: v{_read_installed_version()}  ·  {GITHUB_REPO}",
                     bg=BG_CARD, fg=TX_DIM, font=("Segoe UI", 9), anchor="w").pack(anchor="w")
            br = tk.Frame(inn, bg=BG_CARD); br.pack(fill="x", padx=18, pady=(8, 14))
            self._chk_btn_w = make_action_button(br, "◈   ПРОВЕРИТЬ ОБНОВЛЕНИЯ",
                                                   command=self._do_check_updates, style="primary",
                                                   font=("Segoe UI", 12, "bold"), px=22, py=12)
            self._chk_btn_w.pack(side="left")

    def _do_check_updates(self):
        try:
            for lbl in self._chk_btn_w._labels: lbl.configure(text="⏳  Проверяю...")
        except: pass
        try: self._chk_status.configure(text="Подключение к GitHub...", fg=TX_MID)
        except: pass
        self._updater.check_for_updates(lambda ok,info,err: self.after(0, lambda: self._on_check_done(ok,info,err)))

    def _on_check_done(self, ok, info, err):
        if ok and info:
            try:
                self._upd_log_text.configure(state="normal")
                self._upd_log_text.delete("1.0", "end")
                self._upd_log_text.insert("end", f"Версия v{info['version']}\n")
                pub = info.get("published_at","")[:10]
                if pub: self._upd_log_text.insert("end", f"Дата: {pub}\n\n")
                for line in (info.get("changelog", []) or ["Changelog недоступен."]):
                    self._upd_log_text.insert("end", f"{line}\n")
                self._upd_log_text.configure(state="disabled")
            except: pass
            if self._updater.is_newer(info["version"]):
                self._update_available = True; self._latest_update_info = info
                self._show_update_badge(); self._build_update_button()
                self._toast.show(f"⬆ Доступно v{info['version']}!", kind="update")
                try: self._upd_prog_lbl.configure(text=f"⬆ Доступно обновление v{info['version']}!", fg=AC_GREEN)
                except: pass
            else:
                iv = _read_installed_version()
                try: self._chk_status.configure(text=f"✓  Последняя версия v{iv}!", fg=AC_GREEN)
                except: pass
                try: self._upd_prog_lbl.configure(text=f"✓ У тебя последняя версия v{iv}", fg=AC_MINT)
                except: pass
                self._toast.show("✓ У тебя последняя версия!", kind="success")
        else:
            try: self._chk_status.configure(text=f"✗  Ошибка: {err}", fg=AC_RED)
            except: pass
            self._toast.show("Ошибка проверки обновлений", kind="error")

    def _do_update_now(self):
        if not self._latest_update_info: return
        url = self._latest_update_info.get("download_url", ""); new_ver = self._latest_update_info.get("version", "")
        if not url: self._toast.show("Ссылка недоступна!", kind="error"); return
        try:
            for lbl in self._do_upd_btn._labels: lbl.configure(text="⏳  Скачивание...")
        except: pass
        self._log(f"⬆  Скачиваю v{new_ver}...", "gold")
        self._upd_prog_bar.set(0)
        def _prog(done, total):
            if total:
                pct = done/total
                self.after(0, lambda p=pct,d=done,t=total: self._upd_dl_prog(p,d,t))
        self._updater.download_and_install(url, new_ver,
                                            on_progress=_prog,
                                            on_done=lambda ok,res: self.after(0, lambda: self._on_upd_downloaded(ok,res)))

    def _upd_dl_prog(self, pct, done, total):
        try:
            self._upd_prog_bar.set(pct)
            self._upd_prog_lbl.configure(
                text=f"⬇ {fmt_size(done)} / {fmt_size(total)}  ({int(pct*100)}%)", fg=AC_GLOW)
        except: pass

    def _on_upd_downloaded(self, ok, result):
        if ok:
            self._upd_prog_bar.set(1.0)
            try: self._upd_prog_lbl.configure(text="✓ Скачано! Перезапуск...", fg=AC_GREEN)
            except: pass
            self._toast.show("Обновление скачано! Перезапуск...", kind="update", duration=5000)
            self._log("⬆  Готово! Перезапускаю...", "gold")
            self.after(1500, lambda: self._updater.restart_with_update(result))
        else:
            try: self._upd_prog_lbl.configure(text=f"✗ Ошибка: {result}", fg=AC_RED)
            except: pass
            self._toast.show(f"Ошибка: {result}", kind="error")

    # ──────────────────────────────────────────────────
    #  ADMIN PANEL
    # ──────────────────────────────────────────────────
    def _mk_admin(self, parent):
        f = tk.Frame(parent, bg=ADM_BG)
        hdr = tk.Frame(f, bg=ADM_PANEL, highlightthickness=1, highlightbackground=ADM_MUTE)
        hdr.pack(fill="x", pady=(0, 12))
        tk.Frame(hdr, bg=ADM_ACC, height=3).pack(fill="x")
        hdr_row = tk.Frame(hdr, bg=ADM_PANEL); hdr_row.pack(fill="x", padx=16, pady=10)
        tk.Label(hdr_row, text="⚡  ADMIN PANEL", bg=ADM_PANEL, fg=ADM_ACC,
                 font=("Courier", 14, "bold")).pack(side="left")
        make_badge(hdr_row, SUPER_ADMIN, ADM_GOLD).pack(side="left", padx=10)
        tk.Label(hdr_row, text=time.strftime("[%Y-%m-%d  %H:%M]"), bg=ADM_PANEL, fg=ADM_MUTE,
                 font=("Courier", 9)).pack(side="right")

        tabs_row = tk.Frame(f, bg=ADM_BG); tabs_row.pack(fill="x", pady=(0, 10))
        self._asub_panels = {}; self._asub_btns = {}
        subs = [("◈ Дашборд","ad_dash"),("◉ Keygen","ad_kg"),("⏱ Тайм","ad_tk"),
                ("◐ Игроки","ad_usr"),("⊘ Бан-лист","ad_bl"),("📤 Экспорт","ad_export")]
        for lbl, key in subs:
            btn = make_action_button(tabs_row, lbl, command=lambda k=key: self._asub(k),
                                      style="ghost", font=("Courier", 10), px=12, py=6)
            btn.pack(side="left", padx=2)
            self._asub_btns[key] = btn

        content = tk.Frame(f, bg=ADM_BG); content.pack(fill="both", expand=True)
        self._asub_panels["ad_dash"]   = self._mk_a_dash(content)
        self._asub_panels["ad_kg"]     = self._mk_a_keygen(content)
        self._asub_panels["ad_tk"]     = self._mk_a_timed(content)
        self._asub_panels["ad_usr"]    = self._mk_a_users(content)
        self._asub_panels["ad_bl"]     = self._mk_a_bl(content)
        self._asub_panels["ad_export"] = self._mk_a_export(content)
        self._asub("ad_dash")
        return f

    def _asub(self, key):
        for p in self._asub_panels.values(): p.pack_forget()
        for k, b in self._asub_btns.items():
            is_active = (k == key)
            bg = lerp_color(ADM_BG, ADM_ACC, 0.15) if is_active else ADM_PANEL
            fg = ADM_ACC if is_active else "#660044"
            font = ("Courier", 10, "bold") if is_active else ("Courier", 10)
            try:
                b.configure(bg=bg); b._inner.configure(bg=bg); b._row.configure(bg=bg)
                for lbl in b._labels: lbl.configure(bg=bg, fg=fg, font=font)
            except: pass
        self._asub_panels[key].pack(fill="both", expand=True)

    def _mk_a_dash(self, parent):
        f = tk.Frame(parent, bg=ADM_BG)
        tk.Label(f, text="◈  СТАТИСТИКА СИСТЕМЫ", bg=ADM_BG, fg=ADM_ACC,
                 font=("Courier", 12, "bold")).pack(anchor="w", pady=(0, 8))
        cr = tk.Frame(f, bg=ADM_BG); cr.pack(fill="x", pady=(0, 10))
        self._adm_stat_lbls = {}
        stats_cfg = [("tu","◈","Игроков всего","0",ADM_ACC),("tk","◉","Использ. ключей","0",ADM_ACC2),
                     ("bl","⊘","В бан-листе","0",ADM_RED),("tl","▸","Сегодня онлайн","0",ADM_GOLD),
                     ("ac","✓","Активных","0",AC_GREEN),("ex","✕","Просрочено","0",AC_RED)]
        for key, icon, title, val, col in stats_cfg:
            card_outer, val_lbl = make_stat_card(cr, icon, title, val, col)
            card_outer.pack(side="left", fill="x", expand=True, padx=3)
            self._adm_stat_lbls[key] = val_lbl

        make_action_button(f, "↻  Обновить данные", command=self._a_refresh,
                            style="ghost", font=("Courier", 9), px=14, py=7).pack(anchor="w", pady=(0, 10))

        path_frame = tk.Frame(f, bg=ADM_PANEL, highlightthickness=1, highlightbackground=ADM_MUTE)
        path_frame.pack(fill="x", pady=(0, 8))
        tk.Frame(path_frame, bg=ADM_ACC2, height=1).pack(fill="x")
        pr = tk.Frame(path_frame, bg=ADM_PANEL); pr.pack(fill="x", padx=12, pady=8)
        tk.Label(pr, text="📁 База данных:", bg=ADM_PANEL, fg=ADM_TEXT, font=("Courier", 9)).pack(side="left")
        tk.Label(pr, text=str(USERS_FILE), bg=ADM_PANEL, fg=ADM_ACC, font=("Courier", 8)).pack(side="left", padx=8)

        tk.Label(f, text="Последние регистрации:", bg=ADM_BG, fg=ADM_TEXT,
                 font=("Courier", 10, "bold")).pack(anchor="w", pady=(4, 4))
        rf = tk.Frame(f, bg=ADM_PANEL, highlightthickness=1, highlightbackground=ADM_MUTE)
        rf.pack(fill="x")
        tk.Frame(rf, bg=ADM_ACC, height=1).pack(fill="x")
        self._a_recent = tk.Frame(rf, bg=ADM_PANEL); self._a_recent.pack(fill="x", padx=10, pady=8)
        self._a_stats()
        return f

    def _a_stats(self):
        try:
            users = _load_users(); used = _load_used_keys(); bl = _load_blacklist()
            today = time.strftime("%Y-%m-%d")
            lt = sum(1 for u in users.values() if u.get("last_login","").startswith(today))
            active_cnt = sum(1 for u in users.values() if check_subscription(u)[0])
            expired_cnt = len(users) - active_cnt
            for key, val in [("tu",len(users)),("tk",len(used)),("bl",len(bl)),
                              ("tl",lt),("ac",active_cnt),("ex",expired_cnt)]:
                if key in self._adm_stat_lbls:
                    try: self._adm_stat_lbls[key].configure(text=str(val))
                    except: pass
            for w in self._a_recent.winfo_children(): w.destroy()
            recent = sorted(users.values(), key=lambda u: u.get("date",""), reverse=True)[:8]
            for u in recent:
                r = tk.Frame(self._a_recent, bg=ADM_PANEL); r.pack(fill="x", pady=1)
                tk.Label(r, text=f"  ◈  {u.get('nickname','?')[:14]:14s}",
                         bg=ADM_PANEL, fg=ADM_ACC, font=("Courier", 9, "bold"),
                         width=18, anchor="w").pack(side="left")
                _, sub = check_subscription(u)
                sc = AC_GREEN if sub != "Подписка истекла" else AC_RED
                tk.Label(r, text=sub, bg=ADM_PANEL, fg=sc, font=("Courier", 8)).pack(side="left", padx=8)
                tk.Label(r, text=f"  {u.get('date','')[:10]}", bg=ADM_PANEL, fg=ADM_MUTE,
                         font=("Courier", 8)).pack(side="left", padx=4)
                tk.Label(r, text=f"входов: {u.get('login_count',0)}", bg=ADM_PANEL, fg=ADM_ACC2,
                         font=("Courier", 8)).pack(side="right", padx=10)
        except Exception as e:
            self._log(f"Admin stats error: {e}", "warn")

    def _mk_a_keygen(self, parent):
        f = tk.Frame(parent, bg=ADM_BG)
        tk.Label(f, text="◉  ГЕНЕРАТОР КЛЮЧЕЙ", bg=ADM_BG, fg=ADM_ACC,
                 font=("Courier", 12, "bold")).pack(anchor="w", pady=(0, 8))
        ctrl = tk.Frame(f, bg=ADM_BG); ctrl.pack(fill="x", pady=(0, 8))
        tk.Label(ctrl, text="Кол-во:", bg=ADM_BG, fg=ADM_TEXT, font=("Courier", 10)).pack(side="left")
        self._kg_cnt = tk.StringVar(value="10")
        tk.Entry(ctrl, textvariable=self._kg_cnt, bg=ADM_PANEL, fg=ADM_ACC,
                 insertbackground=ADM_ACC, relief="flat", font=("Courier", 11), bd=6, width=5).pack(side="left", padx=8)
        for n in [1, 5, 10, 25, 50]:
            make_action_button(ctrl, f"×{n}", command=lambda n=n: self._a_gen_keys(n),
                                style="ghost", font=("Courier", 9, "bold"), px=8, py=4).pack(side="left", padx=2)

        out_frame = tk.Frame(f, bg=ADM_PANEL, highlightthickness=1, highlightbackground=ADM_MUTE)
        out_frame.pack(fill="both", expand=True, pady=(0, 8))
        tk.Frame(out_frame, bg=ADM_ACC, height=1).pack(fill="x")
        self._kg_out = tk.Text(out_frame, bg="#060003", fg=ADM_ACC, font=("Courier", 11),
                               relief="flat", state="disabled", wrap="none", bd=10)
        sb = ttk.Scrollbar(out_frame, command=self._kg_out.yview)
        self._kg_out.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y"); self._kg_out.pack(fill="both", expand=True)

        br = tk.Frame(f, bg=ADM_BG); br.pack(fill="x")
        make_action_button(br, "⊠ Очистить",
                            command=lambda: (self._kg_out.configure(state="normal"),
                                            self._kg_out.delete("1.0","end"),
                                            self._kg_out.configure(state="disabled")),
                            style="ghost", font=("Courier", 9), px=10, py=6).pack(side="right", padx=2)
        make_action_button(br, "⊞ Скопировать",
                            command=lambda: (self.clipboard_clear(),
                                            self.clipboard_append(self._kg_out.get("1.0","end"))),
                            style="ghost", font=("Courier", 9), px=10, py=6).pack(side="right", padx=2)
        return f

    def _a_gen_keys(self, n=None):
        try: count = n or int(self._kg_cnt.get() or 10)
        except: count = 10
        keys = [generate_key() for _ in range(count)]
        self._kg_out.configure(state="normal")
        self._kg_out.insert("end", f"\n{time.strftime('[%H:%M:%S]')} × {count}:\n")
        for k in keys: self._kg_out.insert("end", f"  {k}\n")
        self._kg_out.configure(state="disabled"); self._kg_out.see("end")
        self._toast.show(f"Сгенерировано {count} ключей!", kind="success")

    def _mk_a_timed(self, parent):
        f = tk.Frame(parent, bg=ADM_BG)
        tk.Label(f, text="⏱  ТАЙМ-КЛЮЧИ", bg=ADM_BG, fg=ADM_GOLD,
                 font=("Courier", 12, "bold")).pack(anchor="w", pady=(0, 8))
        pr = tk.Frame(f, bg=ADM_BG); pr.pack(fill="x", pady=(0, 8))
        presets = [("1 ч",3600),("6 ч",21600),("12 ч",43200),("1 дн",86400),
                   ("7 дн",604800),("30 дн",2592000),("∞",0)]
        self._tkey_sec = tk.IntVar(value=86400); self._tkey_cnt = tk.StringVar(value="1")
        for lbl_t, sec in presets:
            make_action_button(pr, lbl_t,
                                command=lambda s=sec: (self._tkey_sec.set(s), self._upd_dur()),
                                style="ghost", font=("Courier", 9), px=10, py=5).pack(side="left", padx=2)
        self._dur_lbl = tk.Label(f, text=f"◈ Выбрано: {fmt_duration(86400)}",
                                  bg=ADM_BG, fg=ADM_GOLD, font=("Courier", 10, "bold"))
        self._dur_lbl.pack(anchor="w", pady=(0, 6))
        gr = tk.Frame(f, bg=ADM_BG); gr.pack(fill="x", pady=(0, 8))
        tk.Label(gr, text="Кол-во:", bg=ADM_BG, fg=ADM_TEXT, font=("Courier", 10)).pack(side="left")
        tk.Entry(gr, textvariable=self._tkey_cnt, bg=ADM_PANEL, fg=ADM_GOLD,
                 insertbackground=ADM_GOLD, relief="flat", font=("Courier", 11), bd=6, width=5).pack(side="left", padx=8)
        for n in [1, 3, 5, 10]:
            make_action_button(gr, f"×{n}", command=lambda n=n: self._gen_timed(n),
                                style="ghost", font=("Courier", 9, "bold"), px=8, py=4).pack(side="left", padx=2)

        out_f = tk.Frame(f, bg=ADM_PANEL, highlightthickness=1, highlightbackground=ADM_MUTE)
        out_f.pack(fill="both", expand=True, pady=(0, 8))
        tk.Frame(out_f, bg=ADM_GOLD, height=1).pack(fill="x")
        self._tk_out = tk.Text(out_f, bg="#030a00", fg=ADM_GOLD, font=("Courier", 11),
                               relief="flat", state="disabled", wrap="none", bd=10)
        sb = ttk.Scrollbar(out_f, command=self._tk_out.yview)
        self._tk_out.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y"); self._tk_out.pack(fill="both", expand=True)

        br = tk.Frame(f, bg=ADM_BG); br.pack(fill="x")
        make_action_button(br, "⊠ Очистить",
                            command=lambda: (self._tk_out.configure(state="normal"),
                                            self._tk_out.delete("1.0","end"),
                                            self._tk_out.configure(state="disabled")),
                            style="ghost", font=("Courier", 9), px=10, py=6).pack(side="right", padx=2)
        make_action_button(br, "⊞ Скопировать",
                            command=lambda: (self.clipboard_clear(),
                                            self.clipboard_append(self._tk_out.get("1.0","end"))),
                            style="ghost", font=("Courier", 9), px=10, py=6).pack(side="right", padx=2)
        return f

    def _upd_dur(self):
        try: self._dur_lbl.configure(text=f"◈ Выбрано: {fmt_duration(self._tkey_sec.get())}")
        except: pass

    def _gen_timed(self, n=None):
        try: count = n or int(self._tkey_cnt.get() or 1)
        except: count = 1
        sec = self._tkey_sec.get(); dur = fmt_duration(sec)
        keys = [generate_timed_key(sec) for _ in range(count)]
        self._tk_out.configure(state="normal")
        self._tk_out.insert("end", f"\n{time.strftime('[%H:%M:%S]')} × {count} [{dur}]:\n")
        for k in keys: self._tk_out.insert("end", f"  {k}   // {dur}\n")
        self._tk_out.configure(state="disabled"); self._tk_out.see("end")
        self._toast.show(f"{count} тайм-ключей [{dur}]", kind="success")

    def _mk_a_users(self, parent):
        f = tk.Frame(parent, bg=ADM_BG)
        top = tk.Frame(f, bg=ADM_BG); top.pack(fill="x", pady=(0, 8))
        tk.Label(top, text="◐  ВСЕ ИГРОКИ", bg=ADM_BG, fg=ADM_ACC,
                 font=("Courier", 12, "bold")).pack(side="left")
        self._usr_count_lbl = tk.Label(top, text="", bg=ADM_BG, fg=ADM_TEXT, font=("Courier", 10))
        self._usr_count_lbl.pack(side="left", padx=12)
        make_action_button(top, "↻ Обновить", command=self._a_refresh_u,
                            style="ghost", font=("Courier", 9), px=10, py=5).pack(side="right")

        sr = tk.Frame(f, bg=ADM_BG); sr.pack(fill="x", pady=(0, 6))
        tk.Label(sr, text="Поиск:", bg=ADM_BG, fg=ADM_TEXT, font=("Courier", 10)).pack(side="left")
        self._usr_q = tk.StringVar()
        self._usr_q.trace_add("write", lambda *a: self._a_refresh_u())
        tk.Entry(sr, textvariable=self._usr_q, bg=ADM_PANEL, fg=ADM_ACC,
                 insertbackground=ADM_ACC, relief="flat", font=("Courier", 10), bd=6, width=24).pack(side="left", padx=8, ipady=4)
        self._usr_filter = tk.StringVar(value="all")
        for lbl_t, val in [("Все","all"),("Активные","active"),("Истекло","expired"),("Забанен","banned")]:
            make_action_button(sr, lbl_t,
                                command=lambda v=val: (self._usr_filter.set(v), self._a_refresh_u()),
                                style="ghost", font=("Courier", 8), px=8, py=3).pack(side="left", padx=2)

        tbl = tk.Frame(f, bg=ADM_PANEL, highlightthickness=1, highlightbackground=ADM_MUTE)
        tbl.pack(fill="both", expand=True)
        tk.Frame(tbl, bg=ADM_ACC, height=1).pack(fill="x")
        hdr = tk.Frame(tbl, bg="#0d0005"); hdr.pack(fill="x")
        for text, w in [("#",3),("Никнейм",14),("Дата рег.",11),("Послед. вход",11),
                        ("Подписка",14),("Входов",6),("Тип ключа",12),("Действия",14)]:
            tk.Label(hdr, text=text, bg="#0d0005", fg=ADM_ACC2, font=("Courier", 8, "bold"),
                     width=w, anchor="w").pack(side="left", padx=4, pady=6)
        tk.Frame(tbl, bg=ADM_MUTE, height=1).pack(fill="x")

        sf = tk.Frame(tbl, bg=ADM_PANEL); sf.pack(fill="both", expand=True)
        canvas = tk.Canvas(sf, bg=ADM_PANEL, highlightthickness=0)
        scr = ttk.Scrollbar(sf, orient="vertical", command=canvas.yview)
        self._usr_inner = tk.Frame(canvas, bg=ADM_PANEL)
        self._usr_inner.bind("<Configure>",
                              lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self._usr_inner, anchor="nw")
        canvas.configure(yscrollcommand=scr.set)
        scr.pack(side="right", fill="y"); canvas.pack(side="left", fill="both", expand=True)
        canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        self._a_refresh_u()
        return f

    def _a_refresh_u(self):
        for w in self._usr_inner.winfo_children(): w.destroy()
        users = _load_users(); bl = _load_blacklist()
        q = self._usr_q.get().strip().lower() if hasattr(self, "_usr_q") else ""
        flt = self._usr_filter.get() if hasattr(self, "_usr_filter") else "all"
        items = []
        for kh, u in users.items():
            if q and q not in u.get("nickname","").lower(): continue
            if flt == "active" and not check_subscription(u)[0]: continue
            if flt == "expired" and check_subscription(u)[0]: continue
            if flt == "banned" and kh not in bl: continue
            items.append((kh, u))
        items.sort(key=lambda x: x[1].get("date",""), reverse=True)
        try: self._usr_count_lbl.configure(text=f"Показано: {len(items)} / {len(users)}")
        except: pass
        if not items:
            tk.Label(self._usr_inner, text="  Нет игроков",
                     bg=ADM_PANEL, fg=ADM_MUTE, font=("Courier", 10)).pack(anchor="w", pady=16, padx=12)
            return
        for idx, (kh, u) in enumerate(items):
            bg2 = ADM_PANEL if idx%2==0 else lerp_color(ADM_PANEL, ADM_BG, 0.5)
            if idx > 0: tk.Frame(self._usr_inner, bg=lerp_color(ADM_PANEL, ADM_MUTE, 0.3), height=1).pack(fill="x")
            row = tk.Frame(self._usr_inner, bg=bg2); row.pack(fill="x")
            nick = u.get("nickname", "?"); is_bl = kh in bl; is_adm_u = u.get("is_admin", False)
            tk.Label(row, text=str(idx+1), bg=bg2, fg=ADM_MUTE,
                     font=("Courier", 8), width=3, anchor="w").pack(side="left", padx=4, pady=6)
            nick_color = ADM_RED if is_bl else (ADM_GOLD if is_adm_u else ADM_ACC)
            nick_prefix = "⊘" if is_bl else ("⚡" if is_adm_u else "◈")
            nf = tk.Frame(row, bg=bg2); nf.pack(side="left", padx=2)
            tk.Label(nf, text=f"{nick_prefix} {nick[:12]}",
                     bg=bg2, fg=nick_color, font=("Courier", 9, "bold"), width=14, anchor="w").pack()
            tk.Label(row, text=u.get("date","—")[:10], bg=bg2, fg=ADM_TEXT,
                     font=("Courier", 8), width=11, anchor="w").pack(side="left", padx=4)
            tk.Label(row, text=u.get("last_login","—")[:10], bg=bg2, fg=ADM_MUTE,
                     font=("Courier", 8), width=11, anchor="w").pack(side="left", padx=4)
            valid, sub = check_subscription(u)
            sc = AC_GREEN if valid else AC_RED
            tk.Label(row, text=sub[:13], bg=bg2, fg=sc, font=("Courier", 8), width=14, anchor="w").pack(side="left", padx=4)
            tk.Label(row, text=str(u.get("login_count",0)), bg=bg2, fg=ADM_GOLD,
                     font=("Courier", 8), width=6, anchor="w").pack(side="left", padx=4)
            tk.Label(row, text=u.get("duration_label","∞")[:11], bg=bg2, fg=ADM_ACC2,
                     font=("Courier", 8), width=12, anchor="w").pack(side="left", padx=4)
            bf = tk.Frame(row, bg=bg2); bf.pack(side="right", padx=6)
            if is_bl:
                make_action_button(bf, "Разбан", command=lambda k=kh: self._a_unban(k),
                                    style="ghost", font=("Courier", 8), px=6, py=2).pack(side="left", padx=1)
            else:
                make_action_button(bf, "⊘ Бан", command=lambda k=kh, n=nick: self._a_ban(k, n),
                                    style="danger", font=("Courier", 8), px=6, py=2).pack(side="left", padx=1)
            make_action_button(bf, "✕", command=lambda k=kh, n=nick: self._a_del(k, n),
                                style="danger", font=("Courier", 8), px=6, py=2).pack(side="left", padx=1)

    def _mk_a_export(self, parent):
        f = tk.Frame(parent, bg=ADM_BG)
        tk.Label(f, text="📤  ЭКСПОРТ / ИМПОРТ БАЗЫ", bg=ADM_BG, fg=ADM_ACC,
                 font=("Courier", 12, "bold")).pack(anchor="w", pady=(0, 8))

        info_card = tk.Frame(f, bg=ADM_PANEL, highlightthickness=1, highlightbackground=ADM_MUTE)
        info_card.pack(fill="x", pady=(0, 12))
        tk.Frame(info_card, bg=ADM_ACC, height=1).pack(fill="x")
        ic = tk.Frame(info_card, bg=ADM_PANEL); ic.pack(fill="x", padx=14, pady=10)
        tk.Label(ic, text="Файл базы:", bg=ADM_PANEL, fg=ADM_TEXT, font=("Courier", 9)).pack(anchor="w")
        tk.Label(ic, text=str(USERS_FILE), bg=ADM_PANEL, fg=ADM_ACC, font=("Courier", 8)).pack(anchor="w")
        users = _load_users()
        tk.Label(ic, text=f"Записей: {len(users)}", bg=ADM_PANEL, fg=ADM_GOLD,
                 font=("Courier", 10, "bold")).pack(anchor="w", pady=(4, 0))

        exp_card = tk.Frame(f, bg=ADM_PANEL, highlightthickness=1, highlightbackground=ADM_MUTE)
        exp_card.pack(fill="x", pady=(0, 8))
        tk.Frame(exp_card, bg=ADM_ACC2, height=1).pack(fill="x")
        ec = tk.Frame(exp_card, bg=ADM_PANEL); ec.pack(fill="x", padx=14, pady=10)
        tk.Label(ec, text="Экспорт данных:", bg=ADM_PANEL, fg=ADM_TEXT,
                 font=("Courier", 10, "bold")).pack(anchor="w", pady=(0, 8))
        btn_row = tk.Frame(ec, bg=ADM_PANEL); btn_row.pack(fill="x")
        make_action_button(btn_row, "💾 Экспорт пользователей (JSON)",
                            command=self._export_users, style="admin",
                            font=("Courier", 10, "bold"), px=16, py=10).pack(side="left", padx=4)
        make_action_button(btn_row, "📋 Экспорт ников (TXT)",
                            command=self._export_nicks, style="ghost",
                            font=("Courier", 10), px=14, py=10).pack(side="left", padx=4)

        imp_card = tk.Frame(f, bg=ADM_PANEL, highlightthickness=1, highlightbackground=ADM_MUTE)
        imp_card.pack(fill="x", pady=(0, 8))
        tk.Frame(imp_card, bg=ADM_GOLD, height=1).pack(fill="x")
        imc = tk.Frame(imp_card, bg=ADM_PANEL); imc.pack(fill="x", padx=14, pady=10)
        tk.Label(imc, text="⚠ Импорт / слияние баз:", bg=ADM_PANEL, fg=ADM_GOLD,
                 font=("Courier", 10, "bold")).pack(anchor="w", pady=(0, 4))
        make_action_button(imc, "📂 Импортировать users.json",
                            command=self._import_users, style="warning",
                            font=("Courier", 10), px=14, py=10).pack(anchor="w")

        self._export_status = tk.Label(f, text="", bg=ADM_BG, fg=ADM_ACC, font=("Courier", 9))
        self._export_status.pack(anchor="w", pady=(8, 0))
        return f

    def _export_users(self):
        try:
            path = filedialog.asksaveasfilename(parent=self, title="Сохранить базу",
                defaultextension=".json", filetypes=[("JSON файлы", "*.json"), ("Все", "*.*")],
                initialfile=f"angels_users_{time.strftime('%Y%m%d_%H%M%S')}.json")
            if not path: return
            users = _load_users()
            with open(path, 'w', encoding='utf-8') as fp:
                json.dump({"export_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                           "launcher_version": LAUNCHER_VER, "total_users": len(users), "users": users},
                          fp, ensure_ascii=False, indent=2)
            self._export_status.configure(text=f"✓ Экспортировано {len(users)} пользователей", fg=AC_GREEN)
            self._toast.show(f"Экспорт завершён! {len(users)} записей", kind="success")
        except Exception as e:
            self._export_status.configure(text=f"✗ Ошибка: {e}", fg=AC_RED)

    def _export_nicks(self):
        try:
            path = filedialog.asksaveasfilename(parent=self, title="Сохранить ники",
                defaultextension=".txt", filetypes=[("Текст", "*.txt"), ("Все", "*.*")],
                initialfile=f"angels_nicks_{time.strftime('%Y%m%d_%H%M%S')}.txt")
            if not path: return
            users = _load_users(); bl = _load_blacklist()
            lines = [f"# Angels Launcher — список игроков ({time.strftime('%Y-%m-%d %H:%M:%S')})\n",
                     f"# Всего: {len(users)}\n\n"]
            for kh, u in sorted(users.items(), key=lambda x: x[1].get("date",""), reverse=True):
                nick = u.get("nickname","?")
                status = "ЗАБАНЕН" if kh in bl else ("ADMIN" if u.get("is_admin") else "active")
                _, sub = check_subscription(u)
                lines.append(f"{nick:<20} | {status:<10} | {sub:<20} | рег: {u.get('date','')[:10]}\n")
            with open(path, 'w', encoding='utf-8') as fp: fp.writelines(lines)
            self._export_status.configure(text=f"✓ Экспортировано {len(users)} ников", fg=AC_GREEN)
            self._toast.show(f"Список ников сохранён!", kind="success")
        except Exception as e:
            self._export_status.configure(text=f"✗ Ошибка: {e}", fg=AC_RED)

    def _import_users(self):
        try:
            path = filedialog.askopenfilename(parent=self, title="Выбрать users.json",
                filetypes=[("JSON файлы", "*.json"), ("Все", "*.*")])
            if not path: return
            with open(path, 'r', encoding='utf-8') as fp: data = json.load(fp)
            if "users" in data and isinstance(data["users"], dict):
                import_users = data["users"]
            elif isinstance(data, dict) and all(len(k) == 64 for k in list(data.keys())[:3] if k):
                import_users = data
            else:
                self._export_status.configure(text="✗ Неверный формат файла", fg=AC_RED); return
            current = _load_users(); added = 0; skipped = 0
            for kh, u in import_users.items():
                if kh not in current: current[kh] = u; added += 1
                else: skipped += 1
            _save_users(current)
            self._export_status.configure(text=f"✓ Импортировано: +{added} новых, {skipped} пропущено", fg=AC_GREEN)
            self._toast.show(f"Импорт завершён! +{added} пользователей", kind="success")
            self._a_refresh()
        except Exception as e:
            self._export_status.configure(text=f"✗ Ошибка импорта: {e}", fg=AC_RED)

    def _a_ban(self, kh, nick):
        if not messagebox.askyesno("Бан", f"Заблокировать {nick}?", parent=self): return
        bl = _load_blacklist(); bl.add(kh); _save_blacklist(bl)
        self._toast.show(f"Заблокирован: {nick}", kind="warning"); self._a_refresh()

    def _a_unban(self, kh):
        bl = _load_blacklist(); bl.discard(kh); _save_blacklist(bl)
        self._toast.show("Разблокировано", kind="success"); self._a_refresh()

    def _a_del(self, kh, nick):
        if not messagebox.askyesno("Удаление", f"Удалить {nick}?", parent=self): return
        users = _load_users()
        if kh in users: del users[kh]; _save_users(users)
        used = _load_used_keys(); used.discard(kh); _save_used_keys(used)
        self._toast.show(f"Удалён: {nick}", kind="error"); self._a_refresh()

    def _mk_a_bl(self, parent):
        f = tk.Frame(parent, bg=ADM_BG)
        top = tk.Frame(f, bg=ADM_BG); top.pack(fill="x", pady=(0, 8))
        tk.Label(top, text="⊘  БАН-ЛИСТ", bg=ADM_BG, fg=ADM_RED,
                 font=("Courier", 12, "bold")).pack(side="left")
        make_action_button(top, "↻", command=self._a_refresh_bl,
                            style="ghost", font=("Courier", 10), px=10, py=5).pack(side="right")

        add = tk.Frame(f, bg=ADM_PANEL, highlightthickness=1, highlightbackground=ADM_MUTE)
        add.pack(fill="x", pady=(0, 8))
        tk.Frame(add, bg=ADM_RED, height=1).pack(fill="x")
        r = tk.Frame(add, bg=ADM_PANEL); r.pack(fill="x", padx=12, pady=8)
        tk.Label(r, text="SHA256 хэш:", bg=ADM_PANEL, fg=ADM_TEXT, font=("Courier", 9)).pack(side="left")
        self._bl_v = tk.StringVar()
        tk.Entry(r, textvariable=self._bl_v, bg=ADM_BG, fg=ADM_RED, insertbackground=ADM_RED,
                 relief="flat", font=("Courier", 10), bd=6, width=32).pack(side="left", padx=8, ipady=4)
        make_action_button(r, "+ Добавить", command=self._a_add_bl,
                            style="danger", font=("Courier", 9, "bold"), px=10, py=5).pack(side="left")

        bl_f = tk.Frame(f, bg=ADM_PANEL, highlightthickness=1, highlightbackground=ADM_MUTE)
        bl_f.pack(fill="both", expand=True)
        tk.Frame(bl_f, bg=ADM_RED, height=1).pack(fill="x")
        self._bl_inner = tk.Frame(bl_f, bg=ADM_PANEL); self._bl_inner.pack(fill="both", expand=True, padx=12, pady=8)
        self._a_refresh_bl()
        return f

    def _a_refresh_bl(self):
        for w in self._bl_inner.winfo_children(): w.destroy()
        bl = _load_blacklist(); users = _load_users()
        if not bl:
            tk.Label(self._bl_inner, text="Бан-лист пуст", bg=ADM_PANEL, fg=ADM_MUTE,
                     font=("Courier", 10)).pack(anchor="w", pady=16); return
        for kh in sorted(bl):
            nick = users.get(kh, {}).get("nickname", "?")
            r = tk.Frame(self._bl_inner, bg=ADM_BG); r.pack(fill="x", pady=2)
            tk.Label(r, text=f"  ⊘  {nick[:12]:12s}", bg=ADM_BG, fg=ADM_RED,
                     font=("Courier", 9, "bold"), width=16, anchor="w").pack(side="left", padx=4, pady=5)
            tk.Label(r, text=kh[:28]+"…", bg=ADM_BG, fg="#440022",
                     font=("Courier", 8), anchor="w").pack(side="left", padx=8)
            make_action_button(r, "Разбан",
                                command=lambda k=kh: (self._a_unban(k), self._a_refresh_bl()),
                                style="ghost", font=("Courier", 8), px=8, py=3).pack(side="right", padx=8)

    def _a_add_bl(self):
        val = self._bl_v.get().strip()
        if not val: return
        bl = _load_blacklist(); bl.add(val); _save_blacklist(bl)
        self._bl_v.set(""); self._a_refresh_bl(); self._a_stats()

    def _a_refresh(self):
        try: self._a_stats()
        except: pass
        try: self._a_refresh_u()
        except: pass
        try: self._a_refresh_bl()
        except: pass

    # ──────────────────────────────────────────────────
    #  LOG + STATUS
    # ──────────────────────────────────────────────────
    def _log(self, msg, tag="normal"):
        colors = {"normal":AC_MINT,"muted":TX_DIM,"warn":AC_ORANGE,"error":AC_RED,
                  "info":AC_GLOW,"accent":AC_MAIN,"cmd":AC_GOLD,"gold":ADM_GOLD}
        def _do():
            try:
                self.console.configure(state="normal")
                ts = time.strftime("%H:%M:%S")
                self.console.insert("end", f"[{ts}] {msg}\n")
                s = self.console.index("end - 2 lines linestart")
                e = self.console.index("end - 1 lines lineend")
                self.console.tag_add(tag, s, e)
                self.console.tag_configure(tag, foreground=colors.get(tag, AC_MINT))
                self.console.configure(state="disabled")
                self.console.see("end")
            except: pass
        self.after(0, _do)

    def _clear_con(self):
        self.console.configure(state="normal"); self.console.delete("1.0","end")
        self.console.configure(state="disabled")

    def _set_status(self, msg, pct=None, speed=None, eta=None):
        def _do():
            self.status.set(msg)
            if pct is not None: self.progress.set(max(0., min(100., float(pct))))
            self.spd_var.set(f"↓ {fmt_size(speed)}/с" if speed and speed > 0 else "")
            self.eta_var.set(f"⏱ {fmt_time(eta)}" if eta and eta > 1 else "")
        self.after(0, _do)

    def _set_btn(self, enabled, text="◈   ИГРАТЬ"):
        def _do(): self.play_btn.configure_state(enabled, text)
        self.after(0, _do)

    # ──────────────────────────────────────────────────
    #  REINSTALL + FILES
    # ──────────────────────────────────────────────────
    def _reinstall(self):
        if not messagebox.askyesno("Переустановка", "Удалить Forge и переустановить?", parent=self): return
        for fid in FORGE_ID_VARIANTS:
            d = VERSIONS_DIR / fid
            if d.exists(): shutil.rmtree(d, ignore_errors=True)
        FORGE_INST.unlink(missing_ok=True)
        if FORGE_EXTRACT.exists(): shutil.rmtree(FORGE_EXTRACT, ignore_errors=True)
        self._log("⚠  Forge удалён. Нажми «Играть» для переустановки.", "warn")
        self._toast.show("Forge удалён. Нажми Играть.", kind="warning")

    def _check_files(self):
        forge_id, forge_json = find_forge_json()
        mod_jar = MODS_DIR / f"{MOD_NAME}-{MOD_VERSION}.jar"
        missing = []
        if forge_json is None: missing.append("Forge")
        if not mod_jar.exists(): missing.append("Мод")
        if missing: self._log(f"⚠  Требуется загрузка: {', '.join(missing)}", "warn")
        else: self._log(f"✓  Forge [{forge_id}] и {MOD_NAME} установлены.", "accent")

    # ──────────────────────────────────────────────────
    #  START / INSTALL / LAUNCH
    # ──────────────────────────────────────────────────
    def _start(self):
        valid, status = check_subscription(self._user)
        if not valid:
            messagebox.showerror("Подписка истекла",
                                  f"Подписка истекла!\nПродление: {TG_LINK}", parent=self)
            return
        self._set_btn(False, "⏳  Загрузка...")
        threading.Thread(target=self._install_and_launch, daemon=True).start()

    def _install_and_launch(self):
        try:
            self._set_status("Проверка Java...", 2)
            java = get_java()
            if not java: raise Exception("Java не найдена!\nhttps://adoptium.net/temurin/releases/?version=8")
            self._log(f"✓  Java: {java}", "accent")

            self._set_status("Манифест Mojang...", 4)
            manifest = http_get_json(VERSION_MANIFEST)
            ver_url = next((v["url"] for v in manifest["versions"] if v["id"]==MC_VERSION), None)
            if not ver_url: raise Exception(f"Версия {MC_VERSION} не найдена!")
            ver_json = http_get_json(ver_url)
            van_dir = VERSIONS_DIR / MC_VERSION; van_dir.mkdir(parents=True, exist_ok=True)
            with open(van_dir/f"{MC_VERSION}.json","w") as fh: json.dump(ver_json, fh, indent=2)
            client_jar = van_dir / f"{MC_VERSION}.jar"
            if not client_jar.exists():
                self._set_status("Скачивание Minecraft...", 7)
                dl = ver_json["downloads"]["client"]
                def _cj(done, total):
                    if total: self._set_status(f"Minecraft: {int(done/total*100)}%", 7+done/total*9)
                download_file(dl["url"], client_jar, on_progress=_cj, expected_sha1=dl.get("sha1"))
            self._log("✓  client.jar", "accent")

            forge_id, forge_json_path = find_forge_json()
            if forge_json_path is None:
                self._log("Forge не найден — устанавливаю...", "warn")
                forge_id, forge_json_path = self._install_forge_auto(java, client_jar)
                if forge_json_path is None: raise Exception("Не удалось установить Forge!")
            else: self._log(f"✓  Forge: {forge_id}", "accent")

            with open(forge_json_path) as fh: forge_json_data = json.load(fh)
            merged = self._merge_jsons(ver_json, forge_json_data)

            self._set_status("Библиотеки...", 50)
            cp_entries = [str(client_jar)]; native_jars = []; lib_tasks = []; seen = set(); cur_os = os_name()
            for lib in merged.get("libraries",[]):
                if not rule_allowed(lib.get("rules")): continue
                dl2 = lib.get("downloads",{}); art = dl2.get("artifact")
                if art and art.get("path"):
                    p = LIBRARIES_DIR / art["path"]
                    if str(p) not in seen:
                        seen.add(str(p)); cp_entries.append(str(p))
                        if art.get("url") and not (p.exists() and p.stat().st_size>0):
                            lib_tasks.append((art["url"], p, art.get("sha1")))
                cls = dl2.get("classifiers",{}); nat_map = lib.get("natives",{})
                if cur_os in nat_map:
                    nat_key = nat_map[cur_os].replace("${arch}","64"); nat = cls.get(nat_key)
                    if nat and nat.get("url") and nat.get("path"):
                        np_ = LIBRARIES_DIR / nat["path"]; native_jars.append(str(np_))
                        if not (np_.exists() and np_.stat().st_size>0):
                            lib_tasks.append((nat["url"], np_, nat.get("sha1")))
            if lib_tasks:
                def _lp(done, total, speed, eta):
                    self._set_status(f"Библиотеки: {done}/{total}", 50+done/max(total,1)*12)
                ParallelDownloader(lib_tasks, on_progress=_lp).run()
            self._log("✓  Библиотеки", "accent")

            NATIVES_DIR.mkdir(parents=True, exist_ok=True)
            for njar in native_jars:
                if not os.path.isfile(njar): continue
                try:
                    with zipfile.ZipFile(njar) as z:
                        for name in z.namelist():
                            if any(name.endswith(e) for e in [".dll",".so",".dylib"]):
                                tgt = NATIVES_DIR / Path(name).name
                                if not tgt.exists():
                                    with z.open(name) as src, open(tgt,"wb") as dst: dst.write(src.read())
                except: pass
            self._log("✓  Нативы", "accent")

            self._set_status("Ассеты...", 63)
            ai = ver_json.get("assetIndex",{}); aid = ai.get("id", MC_VERSION)
            idir = ASSETS_DIR / "indexes"; idir.mkdir(parents=True, exist_ok=True)
            aif = idir / f"{aid}.json"
            if not aif.exists(): download_file(ai.get("url"), aif)
            with open(aif) as fh: aj = json.load(fh)
            obj = ASSETS_DIR / "objects"; atasks = []
            for _, info in aj.get("objects",{}).items():
                h = info["hash"]; pre = h[:2]; dst = obj / pre / h
                if not (dst.exists() and dst.stat().st_size>0):
                    atasks.append((f"https://resources.download.minecraft.net/{pre}/{h}", dst, h))
            if atasks:
                def _ap(done, total, speed, eta):
                    self._set_status(f"Ассеты: {done}/{total}", 63+done/max(total,1)*20)
                ParallelDownloader(atasks, on_progress=_ap).run()
            self._log("✓  Ассеты", "accent")

            # ━━━ МОД — ПРОВЕРКА И ОБНОВЛЕНИЕ ━━━
            MODS_DIR.mkdir(parents=True, exist_ok=True)
            mod_jar = MODS_DIR / f"{MOD_NAME}-{MOD_VERSION}.jar"
            new_url = self.mod_url.get().strip()
            if not new_url: new_url = MOD_URL_DEFAULT
            new_url = _gdrive_direct(new_url)

            url_changed = check_mod_url_changed(new_url)

            if url_changed and mod_jar.exists():
                self._log("⚠  URL мода изменился — удаляю старый мод...", "warn")
                self.after(0, lambda: self._toast.show("Новый URL мода — обновляю...", kind="info"))
                mod_jar.unlink(missing_ok=True)

            if not mod_jar.exists():
                self._set_status("Скачивание мода...", 85)
                self._log(f"◈  Загружаю мод с: {new_url}", "info")
                def _mp(done, total):
                    if total: self._set_status(f"Мод: {int(done/total*100)}%", 85+done/total*8)
                download_file(new_url, mod_jar, on_progress=_mp)
                _save_mod_url_config(new_url)
                self._log(f"✓  {MOD_NAME} загружен и установлен", "accent")
            else:
                self._log(f"✓  Мод установлен (URL не изменился)", "accent")

            self._set_status("Запуск...", 95)
            srv = self._connect_server; self._connect_server = None
            self._log("▸  Запускаем Minecraft + Forge (Pirate Mode)...", "accent")
            self.after(0, lambda: self._toast.show("Minecraft запущен!", kind="success"))
            self._run_mc(java, cp_entries, aid, merged, forge_id, srv)
        except Exception as e:
            msg = str(e); self._log(f"✗  ОШИБКА: {msg}", "error")
            self.after(0, lambda m=msg: messagebox.showerror("Ошибка", m, parent=self))
            self.after(0, lambda: self._toast.show("Ошибка запуска!", kind="error"))
            self._set_btn(True); self._set_status("Ошибка — см. консоль", 0)
            self.eta_var.set(""); self.spd_var.set("")

    def _install_forge_auto(self, java, client_jar):
        if not FORGE_INST.exists() or FORGE_INST.stat().st_size < 10000:
            self._set_status("Скачивание Forge...", 16)
            def _fp(done, total):
                if total: self._set_status(f"Forge: {int(done/total*100)}%", 16+done/total*4)
            download_file(FORGE_INSTALLER_URL, FORGE_INST, on_progress=_fp)
        self._set_status("Распаковка Forge...", 21)
        if FORGE_EXTRACT.exists(): shutil.rmtree(FORGE_EXTRACT, ignore_errors=True)
        FORGE_EXTRACT.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(FORGE_INST) as zf: zf.extractall(FORGE_EXTRACT)
        ip_p = FORGE_EXTRACT/"install_profile.json"; vp_p = FORGE_EXTRACT/"version.json"
        if not ip_p.exists(): raise Exception("install_profile.json не найден!")
        if not vp_p.exists(): raise Exception("version.json не найден!")
        with open(ip_p) as f: ip = json.load(f)
        with open(vp_p) as f: fvd = json.load(f)
        forge_id = ip.get("version") or f"{MC_VERSION}-forge-{FORGE_VERSION}"
        fvd_dir = VERSIONS_DIR / forge_id; fvd_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(vp_p, fvd_dir/f"{forge_id}.json")
        with zipfile.ZipFile(FORGE_INST) as zf:
            for name in zf.namelist():
                if name.startswith("maven/") and not name.endswith("/"):
                    dst = LIBRARIES_DIR / name[6:]; dst.parent.mkdir(parents=True, exist_ok=True)
                    if not dst.exists():
                        with zf.open(name) as src: dst.write_bytes(src.read())
        lib_tasks = []; seen = set()
        for lib in ip.get("libraries",[]) + fvd.get("libraries",[]):
            art = lib.get("downloads",{}).get("artifact",{}); path = art.get("path","")
            url = art.get("url",""); sha1 = art.get("sha1")
            if not path or path in seen: continue
            seen.add(path); dest = LIBRARIES_DIR / path
            if dest.exists() and dest.stat().st_size > 0: continue
            if url: lib_tasks.append((url, dest, sha1))
            else:
                nm = lib.get("name","")
                if nm:
                    rel = str(maven_coord_to_path(nm)); dest2 = LIBRARIES_DIR / rel
                    if not (dest2.exists() and dest2.stat().st_size > 0):
                        lib_tasks.append((MAVEN_FORGE+rel.replace("\\","/"), dest2, sha1))
        if lib_tasks:
            def _lp(done, total, speed, eta):
                self._set_status(f"Forge libs: {done}/{total}", 25+done/max(total,1)*15)
            ParallelDownloader(lib_tasks, on_progress=_lp,
                               on_error=lambda d,e: self._log(f"  ⚠ {Path(d).name}: {e}", "warn")).run()
        data_map = {}
        for key, val in ip.get("data",{}).items():
            cv = val.get("client","")
            if cv.startswith("[") and cv.endswith("]"):
                data_map[key] = str(LIBRARIES_DIR/maven_coord_to_path(cv[1:-1]))
            elif cv.startswith("/"):
                data_map[key] = str(FORGE_EXTRACT/cv.lstrip("/"))
            else: data_map[key] = cv
        data_map.update({"MINECRAFT_JAR":str(client_jar),"SIDE":"client","ROOT":str(MC_DIR),
                          "INSTALLER":str(FORGE_INST),"LIBRARY_DIR":str(LIBRARIES_DIR)})
        cp_sep = ";" if platform.system()=="Windows" else ":"
        procs = [p for p in ip.get("processors",[]) if "client" in p.get("sides",["client","server"])]
        for i, proc in enumerate(procs, 1):
            jc = proc.get("jar","")
            if not jc: continue
            jp = LIBRARIES_DIR / maven_coord_to_path(jc)
            if not jp.exists(): self._log(f"  ⚠ Jar: {jp.name}", "warn"); continue
            outs = proc.get("outputs",{})
            if outs and all(Path(resolve_proc_arg(v,data_map)).exists() for v in outs.values()):
                continue
            cp_list = [str(jp)]
            for dep in proc.get("classpath",[]):
                dp = LIBRARIES_DIR / maven_coord_to_path(dep)
                if dp.exists(): cp_list.append(str(dp))
            try: mc = get_jar_main_class(jp)
            except Exception as e: self._log(f"  ⚠ {jp.name}: {e}", "warn"); continue
            args = [resolve_proc_arg(a, data_map) for a in proc.get("args",[])]
            cmd = [java, "-cp", cp_sep.join(cp_list), mc] + args
            self._log(f"  [{i}/{len(procs)}] {jp.name}", "info")
            self._set_status(f"Forge: {i}/{len(procs)}", 40+i/max(len(procs),1)*9)
            try:
                res = subprocess.run(cmd, capture_output=True, text=True, errors="replace",
                                     timeout=180, cwd=str(MC_DIR))
                if res.returncode != 0: self._log(f"    ⚠ код {res.returncode}", "warn")
                else: self._log("    ✓ OK", "muted")
            except subprocess.TimeoutExpired: self._log("    ⚠ Таймаут", "warn")
            except Exception as ex: self._log(f"    ⚠ {ex}", "warn")
        fp = fvd_dir / f"{forge_id}.json"
        if fp.exists():
            self._log(f"✓  Forge {forge_id} установлен!", "accent"); return forge_id, fp
        return None, None

    def _merge_jsons(self, vanilla, forge):
        merged = dict(vanilla)
        merged["libraries"] = forge.get("libraries",[]) + vanilla.get("libraries",[])
        if "mainClass" in forge: merged["mainClass"] = forge["mainClass"]
        merged["arguments"] = {}
        for key in ("game","jvm"):
            merged["arguments"][key] = (vanilla.get("arguments",{}).get(key,[]) +
                                         forge.get("arguments",{}).get(key,[]))
        return merged

    def _run_mc(self, java, cp_entries, asset_idx_id, ver_json, forge_id, server_info=None):
        uname = self.username.get().strip() or self._nick
        ram_mb = self.ram.get() * 1024
        cp_sep = ";" if platform.system()=="Windows" else ":"
        classpath = cp_sep.join(dict.fromkeys(cp_entries))
        main_cls = ver_json.get("mainClass","cpw.mods.modlauncher.Launcher")

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        #  PIRATE MODE — Legacy Launcher стиль
        #  Ключевые флаги для обхода лицензии:
        #  --userType legacy  → не msa/mojang, значит не проверяет лицензию
        #  --accessToken 0    → fake токен (любая непустая строка)
        #  --uuid <random>    → случайный UUID
        #  НЕ передаём --demo → Demo Mode отключён
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        fake_uuid = str(uuid.uuid4()).replace("-","")
        fake_token = "0" * 32  # 32 нуля — fake access token

        repl = {
            "${auth_player_name}":    uname,
            "${version_name}":        forge_id,
            "${game_directory}":      str(MC_DIR),
            "${assets_root}":         str(ASSETS_DIR),
            "${assets_index_name}":   asset_idx_id,
            "${auth_uuid}":           fake_uuid,
            "${auth_access_token}":   fake_token,   # fake, но непустой → не Demo
            "${user_type}":           "legacy",      # ← КЛЮЧЕВОЙ ФЛАГ
            "${version_type}":        "release",
            "${natives_directory}":   str(NATIVES_DIR),
            "${launcher_name}":       LAUNCHER_NAME,
            "${launcher_version}":    LAUNCHER_VER,
            "${classpath}":           classpath,
        }
        def resolve(a):
            for k, v in repl.items(): a = a.replace(k, v)
            return a

        def parse_args(sec):
            out = []
            for arg in ver_json.get("arguments",{}).get(sec,[]):
                if isinstance(arg, str):
                    # Фильтруем --demo флаг если он вдруг есть
                    resolved = resolve(arg)
                    if resolved != "--demo": out.append(resolved)
                elif isinstance(arg, dict) and rule_allowed(arg.get("rules",[])):
                    val = arg.get("value",[]); vals = [val] if isinstance(val,str) else val
                    for v in vals:
                        r = resolve(v)
                        if r != "--demo": out.append(r)
            return out

        jvm_args = parse_args("jvm"); game_args = parse_args("game")

        # Убеждаемся что в game args есть нужные флаги для пиратского режима
        # Если их нет — добавляем вручную (как делает Legacy Launcher)
        def ensure_arg(args_list, flag, value=None):
            """Добавляет флаг если его нет."""
            if flag not in args_list:
                args_list.append(flag)
                if value is not None: args_list.append(value)

        ensure_arg(game_args, "--username", uname)
        ensure_arg(game_args, "--uuid", fake_uuid)
        ensure_arg(game_args, "--accessToken", fake_token)
        ensure_arg(game_args, "--userType", "legacy")

        base_jvm = [
            java,
            f"-Xmx{ram_mb}m", f"-Xms{min(ram_mb,512)}m", "-Xss4M",
            f"-Djava.library.path={NATIVES_DIR}",
            # Полное отключение проверки Mojang аутентификации
            "-Dminecraft.api.auth.host=http://localhost/",
            "-Dminecraft.api.account.host=http://localhost/",
            "-Dminecraft.api.session.host=http://localhost/",
            "-Dminecraft.api.services.host=http://localhost/",
            # Forge
            "-Dfml.ignoreInvalidMinecraftCertificates=true",
            "-Dfml.ignorePatchDiscrepancies=true",
            "-Dlog4j2.formatMsgNoLookups=true",
            # Производительность
            "-XX:+UnlockExperimentalVMOptions","-XX:+UseG1GC",
            "-XX:G1NewSizePercent=20","-XX:G1ReservePercent=20",
            "-XX:MaxGCPauseMillis=50","-XX:G1HeapRegionSize=32M",
            "-XX:+ParallelRefProcEnabled","-XX:MaxTenuringThreshold=1",
            "-XX:SurvivorRatio=32","-XX:+DisableExplicitGC","-XX:+AlwaysPreTouch",
            "-XX:+UseStringDeduplication","-XX:ReservedCodeCacheSize=512m",
            "-XX:+UseCodeCacheFlushing","-Dfile.encoding=UTF-8",
        ]

        cp_block = [] if any(a=="-cp" for a in jvm_args) else ["-cp", classpath]
        srv_args = (["--server",server_info[0],"--port",str(server_info[1])] if server_info else [])

        cmd = base_jvm + jvm_args + cp_block + [main_cls] + game_args + srv_args

        self._log(f"◈  {uname}  ·  {self.ram.get()} ГБ  ·  {forge_id}", "accent")
        self._log(f"   🏴‍☠️  userType=legacy  accessToken=<fake>  uuid={fake_uuid[:8]}...", "info")
        self._set_status("◈  Minecraft запущен!", 100); self._set_btn(False, "▸  ЗАПУЩЕН")
        self.eta_var.set(""); self.spd_var.set("")

        try:
            self._mc_process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, errors="replace", cwd=str(MC_DIR))
            for line in self._mc_process.stdout:
                line = line.rstrip()
                if not line: continue
                tag = ("error" if any(w in line for w in ["ERROR","Exception","FATAL"])
                       else "warn" if "WARN" in line
                       else "muted" if any(w in line for w in ["INFO","]: ["]) else "normal")
                self._log(line, tag)
            self._mc_process.wait()
            self._log(f"Minecraft завершён (код {self._mc_process.returncode}).", "muted")
            self.after(0, lambda: self._toast.show("Minecraft закрыт.", kind="info"))
        except Exception as e:
            self._log(f"Ошибка: {e}", "error")
        finally:
            self._mc_process = None; self._set_btn(True)
            self._set_status("Готов к запуску", 0); self.progress.set(0)


# ══════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════
if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "--angelsvistop121":
        if not is_activated(): print("Войди как администратор."); sys.exit(1)
        u = get_current_user()
        if not u.get("is_admin"): print("Нет прав."); sys.exit(1)
        app = AngelsLauncher(); app.after(500, lambda: app._show("admin")); app.mainloop(); sys.exit(0)
    if len(sys.argv) >= 2 and sys.argv[1] == "--keygen":
        n = int(sys.argv[2]) if len(sys.argv) >= 3 else 10
        print(f"\n{'═'*50}\n  Angels Launcher v{LAUNCHER_VER} — Keygen\n{'═'*50}")
        keygen(n); print(f"{'═'*50}\n"); sys.exit(0)
    while True:
        if not is_activated():
            auth = AuthScreen(); auth.mainloop()
            if not auth._activated: break
        app = AngelsLauncher(); app.mainloop()
        if not app._logout_requested: break
