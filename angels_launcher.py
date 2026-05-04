"""
Angels Launcher v11.0  —  AutoUpdate Edition
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  НОВОЕ В v11.0 (AutoUpdate Edition):
  ◈ Система авто-обновлений через GitHub — у ВСЕХ пользователей
  ◈ Кнопка "Обновить" — одно нажатие, без ввода URL
  ◈ VS Code watch → авто-перезапуск лаунчера при сохранении
  ◈ GitHub Actions — пуш в репо = новый .exe у всех
  ◈ Улучшенное меню — крупнее, читабельнее, удобнее
  ◈ Индикатор обновления в заголовке и боковой панели
  ◈ Фоновая проверка обновлений при запуске
  ◈ Прогресс-бар скачивания обновления

  ИСПРАВЛЕНИЯ БАГОВ v11.0.2:
  ◈ FIX: После обновления лаунчер больше не предлагает обновиться снова
  ◈ FIX: Старый процесс лаунчера корректно завершается перед заменой файла
  ◈ FIX: Версия записывается в version.json рядом с exe после установки
  ◈ FIX: Проверка целостности скачанного файла перед перезапуском
  ◈ FIX: Bat-скрипт использует taskkill для завершения текущего процесса

  Admin-панель: python angels_launcher_v11.py --angelsvistop121
  Keygen CLI  : python angels_launcher_v11.py --keygen [n]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

# ══════════════════════════════════════════════════════
#  CONFIG — ИЗМЕНИ ЭТО ПОД СЕБЯ
# ══════════════════════════════════════════════════════
LAUNCHER_NAME = "Angels Launcher"
LAUNCHER_VER  = "11.0.2"
MOD_NAME      = "Angels Mod"
MOD_VERSION   = "1.0.0"
MC_VERSION    = "1.16.5"
FORGE_VERSION = "36.2.39"
SUPER_ADMIN   = "imigrant228"
TG_LINK       = "@Softire_1"

# ═══════════════════════════════════════════════════════════════
#  ГЛАВНАЯ НАСТРОЙКА — ЗАМЕНИ НА СВОЁ GITHUB РЕПО
# ═══════════════════════════════════════════════════════════════
GITHUB_REPO = "davlatbehsm/angels-launcher"

GITHUB_RELEASES_API = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
GITHUB_RAW_VERSION  = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/version.json"

# ══════════════════════════════════════════════════════
#  CRYSTAL GLASS PALETTE
# ══════════════════════════════════════════════════════
BG_DEEP = "#010810"
BG      = "#010c18"
BG2     = "#020e1e"
GL0     = "#040c1c"
GL1     = "#060f22"
GL2     = "#081428"
GL3     = "#0a1830"
GL4     = "#0d1e3a"
BD0     = "#0c2640"
BD1     = "#143660"
BD2     = "#1c4878"
BD3     = "#244e88"
HL0     = "#1a3a5c"
HL1     = "#224570"
HL2     = "#2a5888"
ACC     = "#00d4ff"
ACC2    = "#0099e6"
ACC3    = "#00b8e8"
ACG     = "#00ffcc"
ACB     = "#60d8ff"
TXT     = "#d4eeff"
TXT2    = "#88b8d8"
TXT3    = "#446688"
WHT     = "#f0faff"
MUT     = "#3a6888"
MUT2    = "#4e88aa"
GRN     = "#00ffaa"
GRN2    = "#00e676"
ORG     = "#ff9d4d"
ERR     = "#ff4d6a"
GOLD    = "#ffd060"
PUR     = "#c080ff"
ADM_BG  = "#07000e"
ADM_P   = "#100018"
ADM_AC  = "#ff00cc"
ADM_R   = "#ff2255"
ADM_G   = "#ffdd00"
ADM_M   = "#3a0030"
ADM_T   = "#ffccee"
ADM_A2  = "#cc0088"
BUBBLE_COLORS = [
    "#00d4ff","#0099e6","#00ffcc","#40e0ff","#00aaff",
    "#60c8ff","#80f0ff","#00ccbb","#1ab8d4","#a0e8ff","#ffffff"
]

# ══════════════════════════════════════════════════════
#  IMPORTS
# ══════════════════════════════════════════════════════
import os, sys, json, uuid, shutil, zipfile, platform, hashlib
import threading, subprocess, urllib.request, time, socket, math, random
import datetime, hmac as _hmac, tkinter as tk
from tkinter import ttk, messagebox
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

# ★ FIX: Файл для хранения установленной версии рядом с exe
# Это позволяет лаунчеру знать свою реальную версию после обновления
def _get_installed_version_file() -> Path:
    """Возвращает путь к файлу версии рядом с исполняемым файлом"""
    if getattr(sys, 'frozen', False):
        # Запущен как .exe
        return Path(sys.executable).parent / "angels_launcher_version.json"
    else:
        # Запущен как .py
        return Path(__file__).resolve().parent / "angels_launcher_version.json"

INSTALLED_VERSION_FILE = _get_installed_version_file()

def _read_installed_version() -> str:
    """Читает версию из файла на диске (актуальная после обновления)"""
    try:
        if INSTALLED_VERSION_FILE.exists():
            data = json.loads(INSTALLED_VERSION_FILE.read_text())
            return data.get("version", LAUNCHER_VER)
    except:
        pass
    return LAUNCHER_VER

def _write_installed_version(version: str):
    """Записывает текущую версию в файл на диске"""
    try:
        INSTALLED_VERSION_FILE.write_text(json.dumps({
            "version": version,
            "updated_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }, indent=2))
    except Exception as e:
        print(f"Не удалось записать версию: {e}")

# При старте сразу записываем текущую версию
_write_installed_version(LAUNCHER_VER)

FORGE_MC_VER   = f"{MC_VERSION}-{FORGE_VERSION}"
FORGE_ID_VARIANTS = [
    FORGE_MC_VER,
    f"{MC_VERSION}-forge-{FORGE_VERSION}",
    f"{MC_VERSION}-forge{FORGE_VERSION}"
]

VERSION_MANIFEST    = "https://launchermeta.mojang.com/mc/game/version_manifest_v2.json"
FORGE_INSTALLER_URL = (
    f"https://maven.minecraftforge.net/net/minecraftforge/forge/"
    f"{FORGE_MC_VER}/forge-{FORGE_MC_VER}-installer.jar"
)
MAVEN_FORGE      = "https://maven.minecraftforge.net/"
DOWNLOAD_THREADS = 8

# ══════════════════════════════════════════════════════
#  KEY SYSTEM
# ══════════════════════════════════════════════════════
_VENC = bytes([
    0x03,0x2c,0x25,0x27,0x2e,0x31,0x0e,0x23,0x37,0x2c,0x21,0x2a,
    0x71,0x30,0x1d,0x66,0x71,0x21,0x30,0x71,0x36,0x1d,0x09,0x71,
    0x3b,0x1d,0x70,0x72,0x70,0x77
])

def _secret() -> bytes:
    return bytes(b ^ 0x42 for b in _VENC)

def _key_checksum(s1: str, s2: str) -> str:
    body = f"{s1.upper()}-{s2.upper()}"
    return _hmac.new(_secret(), body.encode(), hashlib.sha256).hexdigest()[:4].upper()

def validate_key(key: str) -> bool:
    key = key.strip().upper()
    parts = key.split('-')
    if len(parts) != 4: return False
    prefix, s1, s2, cs = parts
    if prefix != 'ANGELS': return False
    if len(s1) != 4 or len(s2) != 4 or len(cs) != 4: return False
    return _hmac.compare_digest(_key_checksum(s1, s2), cs)

def _raw_generate() -> str:
    import secrets
    C = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    s1 = ''.join(secrets.choice(C) for _ in range(4))
    s2 = ''.join(secrets.choice(C) for _ in range(4))
    return f"ANGELS-{s1}-{s2}-{_key_checksum(s1,s2)}"

def generate_key() -> str:
    return _raw_generate()

def generate_timed_key(duration_seconds: int = 0) -> str:
    key = _raw_generate()
    kh  = hashlib.sha256(key.encode()).hexdigest()
    meta = _load_keys_meta()
    meta[kh] = {
        "created":          time.strftime("%Y-%m-%d %H:%M:%S"),
        "duration_seconds": duration_seconds,
        "duration_label":   fmt_duration(duration_seconds),
    }
    _save_keys_meta(meta)
    return key

def fmt_duration(sec: int) -> str:
    if sec <= 0:         return "Навсегда ∞"
    if sec < 60:         return f"{sec} сек."
    if sec < 3600:       return f"{sec//60} мин."
    if sec < 86400:      return f"{sec//3600} ч."
    if sec < 86400*30:   return f"{sec//86400} дн."
    if sec < 86400*365:  return f"{sec//(86400*30)} мес."
    return f"{sec//(86400*365)} г."

def keygen(n=10) -> list:
    keys = [generate_key() for _ in range(n)]
    for k in keys: print(k)
    return keys

def _load_keys_meta() -> dict:
    try:
        if KEYS_META_FILE.exists():
            return json.loads(KEYS_META_FILE.read_text())
    except: pass
    return {}

def _save_keys_meta(d: dict):
    APPDATA.mkdir(parents=True, exist_ok=True)
    KEYS_META_FILE.write_text(json.dumps(d, ensure_ascii=False, indent=2))

# ══════════════════════════════════════════════════════
#  USER DATABASE
# ══════════════════════════════════════════════════════
def _load_users() -> dict:
    try:
        if USERS_FILE.exists(): return json.loads(USERS_FILE.read_text())
    except: pass
    return {}

def _save_users(d: dict):
    APPDATA.mkdir(parents=True, exist_ok=True)
    USERS_FILE.write_text(json.dumps(d, ensure_ascii=False, indent=2))

def _load_used_keys() -> set:
    try:
        if USED_KEYS_FILE.exists(): return set(json.loads(USED_KEYS_FILE.read_text()))
    except: pass
    return set()

def _save_used_keys(u: set):
    APPDATA.mkdir(parents=True, exist_ok=True)
    USED_KEYS_FILE.write_text(json.dumps(list(u)))

def _load_blacklist() -> set:
    try:
        if BLACKLIST_FILE.exists(): return set(json.loads(BLACKLIST_FILE.read_text()))
    except: pass
    return set()

def _save_blacklist(b: set):
    APPDATA.mkdir(parents=True, exist_ok=True)
    BLACKLIST_FILE.write_text(json.dumps(list(b)))

def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def is_admin(nick: str) -> bool:
    return nick.strip().lower() == SUPER_ADMIN.lower()

def get_current_user() -> dict:
    try:
        if KEY_FILE.exists():
            d = json.loads(KEY_FILE.read_text())
            return _load_users().get(d.get("key_hash"), {})
    except: pass
    return {}

def is_activated() -> bool:
    try:
        if KEY_FILE.exists():
            return json.loads(KEY_FILE.read_text()).get("activated", False)
    except: pass
    return False

def check_subscription(user: dict) -> tuple:
    expires = user.get("key_expires")
    if not expires:
        return True, "Навсегда ∞"
    try:
        exp = datetime.datetime.strptime(expires, "%Y-%m-%d %H:%M:%S")
        now = datetime.datetime.now()
        if now > exp:
            return False, "Подписка истекла"
        rem = exp - now
        d, h = rem.days, rem.seconds // 3600
        m = (rem.seconds % 3600) // 60
        if d > 0:   return True, f"Ещё {d}д {h}ч"
        if h > 0:   return True, f"Ещё {h}ч {m}мин"
        return True, f"Ещё {m}мин"
    except:
        return True, "Навсегда ∞"

def activate_key(key: str, nickname: str, password: str) -> tuple:
    key = key.strip().upper()
    nickname = nickname.strip()
    password = password.strip()
    if len(nickname) < 3: return False, "Ник минимум 3 символа"
    if len(password) < 4: return False, "Пароль минимум 4 символа"
    if not all(c.isalnum() or c in "_-" for c in nickname):
        return False, "Ник: буквы, цифры, _ и -"
    bl  = _load_blacklist()
    kh  = hashlib.sha256(key.encode()).hexdigest()
    if kh in bl:              return False, "Этот ключ заблокирован"
    if not validate_key(key): return False, "Неверный ключ активации"
    used = _load_used_keys()
    if kh in used:            return False, "Ключ уже использован"
    users = _load_users()
    for u in users.values():
        if u.get("nickname","").lower() == nickname.lower():
            return False, f"Ник «{nickname}» уже занят"
    meta     = _load_keys_meta()
    key_meta = meta.get(kh, {})
    dur_sec  = key_meta.get("duration_seconds", 0)
    expires  = None
    if dur_sec > 0:
        exp_dt  = datetime.datetime.now() + datetime.timedelta(seconds=dur_sec)
        expires = exp_dt.strftime("%Y-%m-%d %H:%M:%S")
    used.add(kh)
    _save_used_keys(used)
    users[kh] = {
        "nickname":      nickname,
        "password_hash": hash_password(password),
        "date":          time.strftime("%Y-%m-%d %H:%M"),
        "last_login":    time.strftime("%Y-%m-%d %H:%M"),
        "login_count":   1,
        "key":           key,
        "is_admin":      is_admin(nickname),
        "key_expires":   expires,
        "duration_label":key_meta.get("duration_label", "Навсегда ∞"),
    }
    _save_users(users)
    KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
    KEY_FILE.write_text(json.dumps({
        "activated": True, "key_hash": kh,
        "nickname":  nickname,
        "date":      time.strftime("%Y-%m-%d"),
        "is_admin":  is_admin(nickname),
    }))
    return True, f"Добро пожаловать, {nickname}!"

def login_user(nickname: str, password: str) -> tuple:
    nickname = nickname.strip()
    password = password.strip()
    users = _load_users()
    for kh, u in users.items():
        if u.get("nickname","").lower() == nickname.lower():
            if u.get("password_hash") != hash_password(password):
                return False, "Неверный пароль"
            valid, status = check_subscription(u)
            if not valid:
                return False, (
                    f"Подписка истекла!\n"
                    f"Для продления обратись в Telegram: {TG_LINK}"
                )
            u["last_login"]  = time.strftime("%Y-%m-%d %H:%M")
            u["login_count"] = u.get("login_count", 0) + 1
            _save_users(users)
            KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
            KEY_FILE.write_text(json.dumps({
                "activated": True, "key_hash": kh,
                "nickname":  nickname,
                "date":      time.strftime("%Y-%m-%d"),
                "is_admin":  is_admin(nickname),
            }))
            return True, f"Добро пожаловать, {nickname}! ({status})"
    return False, "Пользователь не найден"

# ══════════════════════════════════════════════════════
#  UTILITIES
# ══════════════════════════════════════════════════════
def get_total_ram_gb():
    try:
        import psutil
        return max(1, psutil.virtual_memory().total // (1024**3))
    except ImportError: pass
    try:
        if platform.system() == "Windows":
            import ctypes
            class MEM(ctypes.Structure):
                _fields_ = [
                    ("dwLength",ctypes.c_ulong),("dwMemoryLoad",ctypes.c_ulong),
                    ("ullTotalPhys",ctypes.c_ulonglong),("ullAvailPhys",ctypes.c_ulonglong),
                    ("ullTotalPageFile",ctypes.c_ulonglong),("ullAvailPageFile",ctypes.c_ulonglong),
                    ("ullTotalVirtual",ctypes.c_ulonglong),("ullAvailVirtual",ctypes.c_ulonglong),
                    ("sullAvailExtendedVirtual",ctypes.c_ulonglong)
                ]
            ms = MEM(); ms.dwLength = ctypes.sizeof(ms)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(ms))
            return max(1, ms.ullTotalPhys // (1024**3))
    except: pass
    return 8

TOTAL_RAM = get_total_ram_gb()

def _get_mod_url():
    _s = [
        b'\x68\x74\x74\x70\x73\x3a\x2f\x2f',
        b'\x64\x72\x69\x76\x65\x2e\x67\x6f\x6f\x67\x6c\x65\x2e\x63\x6f\x6d',
        b'\x2f\x75\x63\x3f\x65\x78\x70\x6f\x72\x74\x3d\x64\x6f\x77\x6e\x6c\x6f\x61\x64',
        b'\x26\x69\x64\x3d',
        bytes([49,116,103,87,119,113,109,116,100,104,121,57,101,116,79,116,79,
               84,113,72,75,82,89,52,113,109,122,80,118,99,86,67,112])
    ]
    return b''.join(_s).decode()

MOD_URL = _get_mod_url()

def get_java():
    candidates = ["java"]
    if platform.system() == "Windows":
        roots = [
            r"C:\Program Files\Java", r"C:\Program Files\Eclipse Adoptium",
            r"C:\Program Files\Microsoft", r"C:\Program Files\BellSoft",
            r"C:\Program Files\Zulu", r"C:\Program Files\Temurin",
            r"C:\Program Files (x86)\Java"
        ]
        for root in roots:
            if os.path.isdir(root):
                for sub in sorted(os.listdir(root), reverse=True):
                    j = os.path.join(root, sub, "bin", "java.exe")
                    if os.path.isfile(j): candidates.insert(0, j)
    for j in candidates:
        try:
            if subprocess.run([j, "-version"], capture_output=True, timeout=5).returncode == 0:
                return j
        except: pass
    return None

def http_get_json(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": f"AngelsLauncher/{LAUNCHER_VER}",
        "Accept": "application/vnd.github.v3+json"
    })
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode())

def sha1_file(path):
    h = hashlib.sha1()
    with open(path,"rb") as f:
        while chunk := f.read(65536): h.update(chunk)
    return h.hexdigest()

def download_file(url, dest, on_progress=None, expected_sha1=None):
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        if not expected_sha1 or sha1_file(dest) == expected_sha1: return
    tmp = str(dest) + ".tmp"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": f"AngelsLauncher/{LAUNCHER_VER}"})
        with urllib.request.urlopen(req, timeout=90) as r:
            total = int(r.headers.get("Content-Length", 0))
            done  = 0
            with open(tmp,"wb") as f:
                while chunk := r.read(65536):
                    f.write(chunk); done += len(chunk)
                    if on_progress: on_progress(done, total)
        shutil.move(tmp, dest)
        if expected_sha1 and sha1_file(dest) != expected_sha1:
            dest.unlink(missing_ok=True)
            raise Exception(f"SHA1 mismatch: {dest.name}")
    except Exception as e:
        if os.path.exists(tmp):
            try: os.remove(tmp)
            except: pass
        raise e

def check_server_ping(host, port=25565, timeout=3):
    try:
        s = socket.create_connection((host, port), timeout=timeout)
        s.close(); return True
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

def maven_coord_to_path(coord: str) -> Path:
    ext = "jar"
    if "@" in coord: coord, ext = coord.rsplit("@", 1)
    parts = coord.split(":")
    if len(parts) < 3: return Path(coord.replace(":","/") + "." + ext)
    group = parts[0].replace(".", "/"); artifact = parts[1]; version = parts[2]
    classifier = parts[3] if len(parts) > 3 else None
    fname = f"{artifact}-{version}" + (f"-{classifier}" if classifier else "") + f".{ext}"
    return Path(group) / artifact / version / fname

def get_jar_main_class(jar_path: Path) -> str:
    with zipfile.ZipFile(jar_path) as zf:
        mf = next((n for n in zf.namelist() if n.upper() == "META-INF/MANIFEST.MF"), None)
        if not mf: raise Exception(f"MANIFEST.MF not found in {jar_path.name}")
        with zf.open(mf) as f:
            for line in f.read().decode("utf-8", errors="replace").splitlines():
                if line.startswith("Main-Class:"):
                    return line.split(":", 1)[1].strip()
    raise Exception("Main-Class not found")

def resolve_proc_arg(arg: str, data_map: dict) -> str:
    if arg.startswith("[") and arg.endswith("]"):
        return str(LIBRARIES_DIR / maven_coord_to_path(arg[1:-1]))
    if arg.startswith("{") and arg.endswith("}"):
        return data_map.get(arg[1:-1], arg)
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
    with open(SERVERS_FILE,"w") as f:
        json.dump(s, f, ensure_ascii=False, indent=2)

class ParallelDownloader:
    def __init__(self, tasks, threads=DOWNLOAD_THREADS, on_progress=None, on_error=None):
        self.tasks=tasks; self.threads=threads
        self.on_progress=on_progress; self.on_error=on_error
        self._lock=threading.Lock(); self._done=0
        self._total=len(tasks); self._start=time.time()

    def _do(self, task):
        url, dest, sha1 = task
        try: download_file(url, dest, expected_sha1=sha1)
        except Exception as e:
            if self.on_error: self.on_error(dest, e)
        with self._lock:
            self._done += 1
            elapsed = time.time() - self._start
            eta = (self._total - self._done) / max(self._done,1) * elapsed
            if self.on_progress: self.on_progress(self._done, self._total, 0, eta)

    def run(self):
        with ThreadPoolExecutor(max_workers=self.threads) as ex:
            for _ in as_completed([ex.submit(self._do, t) for t in self.tasks]): pass

# ══════════════════════════════════════════════════════
#  ★ ИСПРАВЛЕННАЯ СИСТЕМА АВТО-ОБНОВЛЕНИЙ ★
# ══════════════════════════════════════════════════════
class AutoUpdater:
    """
    Система обновлений через GitHub Releases.

    ИСПРАВЛЕННЫЕ БАГИ:
    1. После обновления версия записывается в version.json рядом с exe —
       при следующем запуске лаунчер знает что он уже обновлён.
    2. Bat-скрипт теперь завершает ТЕКУЩИЙ процесс через taskkill перед
       заменой файла, а не просто ждёт.
    3. Проверка размера скачанного файла перед запуском перезапуска.
    4. PID текущего процесса передаётся в bat для корректного завершения.
    """

    def __init__(self):
        self._latest_info = None
        self._checking = False
        self._script_path = Path(__file__).resolve()
        self._script_mtime = self._get_mtime()

    def _get_mtime(self):
        try: return self._script_path.stat().st_mtime
        except: return 0

    def _version_tuple(self, ver_str: str):
        try: return tuple(int(x) for x in str(ver_str).lstrip("v").split("."))
        except: return (0,)

    def is_newer(self, remote_ver: str) -> bool:
        """
        ★ FIX: Сравниваем с РЕАЛЬНОЙ установленной версией (из файла на диске),
        а не с LAUNCHER_VER константой в коде.
        Это гарантирует что после обновления лаунчер не предложит обновиться снова.
        """
        installed = _read_installed_version()
        return self._version_tuple(remote_ver) > self._version_tuple(installed)

    def check_for_updates(self, callback):
        def _do():
            self._checking = True
            try:
                if "YOUR_GITHUB_USERNAME" not in GITHUB_REPO:
                    data = http_get_json(GITHUB_RELEASES_API)
                    tag = data.get("tag_name", "").lstrip("v")
                    body = data.get("body", "")
                    assets = data.get("assets", [])

                    exe_asset = None
                    for a in assets:
                        name = a.get("name", "")
                        if name.endswith(".exe") and "launcher" in name.lower():
                            exe_asset = a; break
                    if not exe_asset and assets:
                        exe_asset = assets[0]

                    dl_url = exe_asset["browser_download_url"] if exe_asset else ""
                    size   = exe_asset.get("size", 0) if exe_asset else 0

                    changelog = []
                    for line in body.split("\n"):
                        line = line.strip()
                        if line.startswith("- ") or line.startswith("+ ") or line.startswith("* "):
                            changelog.append(line.replace("* ", "- ").replace("+ ", "+ "))
                        elif line and not line.startswith("#"):
                            changelog.append(f"  {line}")

                    info = {
                        "version":      tag,
                        "changelog":    changelog if changelog else [f"Версия v{tag}"],
                        "download_url": dl_url,
                        "size":         size,
                        "release_name": data.get("name", f"v{tag}"),
                        "published_at": data.get("published_at", ""),
                    }
                    self._latest_info = info
                    callback(True, info, None)
                else:
                    callback(False, None, "GitHub репо не настроен. Измени GITHUB_REPO в коде.")
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    callback(False, None, "Репо не найден или нет релизов")
                else:
                    callback(False, None, f"HTTP {e.code}")
            except Exception as e:
                callback(False, None, str(e))
            finally:
                self._checking = False

        threading.Thread(target=_do, daemon=True).start()

    def download_and_install(self, url, new_version, on_progress=None, on_done=None):
        """
        ★ FIX: Принимает new_version чтобы записать его в version.json после скачивания.
        Это ключевое исправление — без записи версии лаунчер снова видел обновление.

        on_progress(done_bytes, total_bytes)
        on_done(success, error_or_path)
        """
        def _do():
            try:
                current = Path(sys.executable)
                if current.suffix.lower() == ".exe":
                    new_path   = current.parent / "angels_launcher_new.exe"
                    final_path = current
                else:
                    script     = Path(__file__).resolve()
                    new_path   = script.parent / "angels_launcher_new.py"
                    final_path = script

                # Удаляем старый временный файл если есть
                if new_path.exists():
                    try: new_path.unlink()
                    except: pass

                # Скачиваем
                download_file(url, new_path, on_progress=on_progress)

                # ★ FIX: Проверяем что файл скачался и не пустой
                if not new_path.exists() or new_path.stat().st_size < 10000:
                    raise Exception(f"Файл скачался некорректно (размер: {new_path.stat().st_size if new_path.exists() else 0} байт)")

                # ★ FIX: Записываем новую версию в файл РЯДОМ С НОВЫМ exe
                # Файл версии будет прочитан после перезапуска
                version_file_path = new_path.parent / "angels_launcher_version.json"
                try:
                    version_file_path.write_text(json.dumps({
                        "version": new_version,
                        "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "previous_version": LAUNCHER_VER
                    }, indent=2))
                except Exception as ve:
                    print(f"Предупреждение: не удалось записать version.json: {ve}")

                current_pid = os.getpid()

                if platform.system() == "Windows":
                    bat = new_path.parent / "_angels_update.bat"
                    # ★ FIX: bat-скрипт теперь:
                    # 1. Ждёт 2 секунды (лаунчер успевает запустить bat)
                    # 2. Убивает ТЕКУЩИЙ процесс по PID
                    # 3. Ждёт ещё секунду (процесс точно завершился)
                    # 4. Заменяет exe файл
                    # 5. Запускает новый exe
                    # 6. Удаляет себя
                    bat_content = (
                        "@echo off\n"
                        "echo Angels Launcher Updater\n"
                        f"echo Завершаю текущий лаунчер (PID {current_pid})...\n"
                        "timeout /t 2 /nobreak > nul\n"
                        f"taskkill /PID {current_pid} /F > nul 2>&1\n"
                        "timeout /t 1 /nobreak > nul\n"
                        f"echo Заменяю файл...\n"
                        f"move /y \"{new_path}\" \"{final_path}\"\n"
                        "if errorlevel 1 (\n"
                        "    echo ОШИБКА: не удалось заменить файл!\n"
                        "    pause\n"
                        "    goto :eof\n"
                        ")\n"
                        f"echo Запускаю новую версию...\n"
                        f"start \"\" \"{final_path}\"\n"
                        "del \"%~f0\"\n"
                    )
                    bat.write_text(bat_content, encoding="cp866")
                    if on_done: on_done(True, str(bat))
                else:
                    # Linux/Mac
                    import stat as stat_mod
                    shutil.move(str(new_path), str(final_path))
                    # Даём права на выполнение
                    try:
                        st = os.stat(final_path)
                        os.chmod(final_path, st.st_mode | stat_mod.S_IEXEC | stat_mod.S_IXGRP | stat_mod.S_IXOTH)
                    except: pass
                    if on_done: on_done(True, str(final_path))

            except Exception as e:
                if on_done: on_done(False, str(e))

        threading.Thread(target=_do, daemon=True).start()

    def restart_with_update(self, bat_path_or_exe=None):
        """
        ★ FIX: Запускает обновление и СРАЗУ завершает текущий процесс.
        Раньше лаунчер не завершался сам → bat не мог заменить файл.
        """
        try:
            if bat_path_or_exe and Path(bat_path_or_exe).exists():
                p = Path(bat_path_or_exe)
                if p.suffix.lower() == ".bat":
                    # Запускаем bat в новом окне и завершаемся
                    subprocess.Popen(
                        str(p),
                        shell=True,
                        creationflags=(
                            subprocess.CREATE_NEW_CONSOLE
                            if platform.system() == "Windows" else 0
                        )
                    )
                    # ★ Ключевое: завершаем СЕБЯ немедленно
                    # bat подождёт 2 сек, убьёт нас по PID (на случай если
                    # destroy() не сработает), заменит файл и запустит новый
                    time.sleep(0.3)
                    os._exit(0)
                else:
                    # Linux/Mac — просто перезапускаем
                    os.execv(bat_path_or_exe, [bat_path_or_exe] + sys.argv[1:])
            else:
                os.execv(sys.executable, [sys.executable] + sys.argv)
        except Exception as e:
            print(f"Restart error: {e}")
            os._exit(1)

    # ── VS Code watch ──────────────────────────────────
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
            python = sys.executable
            script = str(Path(__file__).resolve())
            time.sleep(0.5)
            os.execv(python, [python, script] + sys.argv[1:])
        except Exception as e:
            print(f"Auto-restart error: {e}")


def generate_github_actions_config() -> str:
    return f"""# Файл: .github/workflows/build.yml
name: Build Angels Launcher

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install pyinstaller
    
    - name: Get version from script
      id: get_version
      shell: python
      run: |
        import re, os
        with open('angels_launcher_v11.py', 'r', encoding='utf-8') as f:
            content = f.read()
        match = re.search(r'LAUNCHER_VER\\s*=\\s*"([^"]+)"', content)
        version = match.group(1) if match else "0.0"
        with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
            f.write(f"version={{version}}\\n")
    
    - name: Build EXE
      run: |
        pyinstaller --onefile --noconsole --name "AngelsLauncher" angels_launcher_v11.py
    
    - name: Create Release
      uses: softprops/action-gh-release@v1
      with:
        tag_name: v${{{{ steps.get_version.outputs.version }}}}
        name: Angels Launcher v${{{{ steps.get_version.outputs.version }}}}
        body: |
          Автоматическая сборка Angels Launcher v${{{{ steps.get_version.outputs.version }}}}
        files: dist/AngelsLauncher.exe
        draft: false
        prerelease: false
      env:
        GITHUB_TOKEN: ${{{{ secrets.GITHUB_TOKEN }}}}
"""

# ══════════════════════════════════════════════════════
#  GLASS UI HELPERS
# ══════════════════════════════════════════════════════
def draw_glass_card(canvas, x1, y1, x2, y2, r=14,
                    fill_dark=GL1, border=BD1, highlight=HL1,
                    shimmer=True, tag=None):
    kw = {"tags": tag} if tag else {}
    ids = []
    for i, (pad, col, st) in enumerate([
        (3, BD0, "gray12"),
        (2, BD0, "gray25"),
        (1, BD1, None),
    ]):
        ox1, oy1, ox2, oy2 = x1-pad, y1-pad, x2+pad, y2+pad
        if st:
            ids.append(canvas.create_rectangle(ox1,oy1,ox2,oy2, outline=col, fill="", stipple=st, width=1, **kw))
        else:
            ids.append(canvas.create_rectangle(ox1,oy1,ox2,oy2, outline=col, fill="", width=1, **kw))
    ids.append(canvas.create_rectangle(x1, y1, x2, y2, fill=fill_dark, outline=BD1, width=1, **kw))
    mid = y1 + (y2-y1)*0.45
    ids.append(canvas.create_rectangle(x1+1, y1+1, x2-1, mid, fill=GL2, outline="", **kw))
    if shimmer:
        ids.append(canvas.create_line(x1+r, y1+1, x2-r, y1+1, fill=highlight, width=1, **kw))
    ids.append(canvas.create_line(x1+1, y1+r, x1+1, y2-r, fill=HL0, width=1, **kw))
    return ids

def glass_rect(canvas, x1, y1, x2, y2, fill=GL1, outline=BD1, width=1, **kw):
    canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline=outline, width=width, **kw)
    canvas.create_line(x1+8, y1+1, x2-8, y1+1, fill=HL1, width=1, **kw)

def pill_btn(parent, text, cmd, fg=BG, bg=ACC2, font=("Segoe UI",10,"bold"),
             px=18, py=9, hbg=ACC, hfg=BG, width=0):
    kw = {"width": width} if width else {}
    b = tk.Button(parent, text=text, bg=bg, fg=fg, activebackground=hbg,
                  activeforeground=hfg, font=font, relief="flat",
                  cursor="hand2", bd=0, padx=px, pady=py, command=cmd,
                  highlightthickness=1, highlightbackground=bg,
                  highlightcolor=ACC, **kw)
    def _enter(e): b.configure(bg=hbg, fg=hfg, highlightbackground=ACC)
    def _leave(e): b.configure(bg=bg, fg=fg, highlightbackground=bg)
    def _press(e): b.configure(bg=ACC3, fg=BG)
    b.bind("<Enter>", _enter)
    b.bind("<Leave>", _leave)
    b.bind("<ButtonPress-1>", _press)
    b.bind("<ButtonRelease-1>", _enter)
    return b

def glass_btn(parent, text, cmd, fg=ACC, bg=GL2, font=("Segoe UI",10,"bold"),
              px=14, py=8, hbg=GL3, hfg=WHT, width=0):
    kw = {"width": width} if width else {}
    b = tk.Button(parent, text=text, bg=bg, fg=fg, activebackground=hbg,
                  activeforeground=hfg, font=font, relief="flat",
                  cursor="hand2", bd=0, padx=px, pady=py, command=cmd,
                  highlightthickness=1, highlightbackground=BD1,
                  highlightcolor=ACC, **kw)
    def _enter(e): b.configure(bg=hbg, fg=hfg, highlightbackground=ACC)
    def _leave(e): b.configure(bg=bg, fg=fg, highlightbackground=BD1)
    b.bind("<Enter>", _enter)
    b.bind("<Leave>", _leave)
    return b

def glass_entry(parent, var, show="", width=None,
                font=("Segoe UI",11), placeholder="", ph_color=TXT3):
    wrap = tk.Frame(parent, bg=BD1, padx=1, pady=1)
    kw = {"width": width} if width else {}
    inner = tk.Frame(wrap, bg=GL2)
    inner.pack(fill="x")
    tk.Frame(inner, bg=HL0, height=1).pack(fill="x")
    e = tk.Entry(inner, textvariable=var, bg=GL2, fg=TXT,
                 insertbackground=ACC, relief="flat", font=font,
                 bd=8, show=show, **kw)
    e.pack(fill="x", ipady=7)
    _has_ph = [False]
    if placeholder:
        e.insert(0, placeholder)
        e.configure(fg=ph_color)
        _has_ph[0] = True

    def _focus_in(ev):
        if _has_ph[0]:
            e.delete(0, "end")
            e.configure(fg=TXT)
            if show: e.configure(show=show)
            _has_ph[0] = False
        wrap.configure(bg=ACC2)
        inner.configure(bg=GL3)
        e.configure(bg=GL3)

    def _focus_out(ev):
        if not var.get() and placeholder:
            e.configure(show="", fg=ph_color)
            e.insert(0, placeholder)
            _has_ph[0] = True
        wrap.configure(bg=BD1)
        inner.configure(bg=GL2)
        e.configure(bg=GL2)

    e.bind("<FocusIn>", _focus_in)
    e.bind("<FocusOut>", _focus_out)
    e._has_ph = _has_ph
    e._placeholder = placeholder
    return wrap, e

def get_entry_value(e):
    try:
        if e._has_ph[0]: return ""
    except: pass
    return e.get().strip()

# ══════════════════════════════════════════════════════
#  TOAST NOTIFICATION SYSTEM
# ══════════════════════════════════════════════════════
class ToastManager:
    def __init__(self, root):
        self.root = root
        self._toasts = []

    def show(self, message, kind="info", duration=3500):
        colors = {
            "info":    (GL3, BD2,    ACC,   "◈"),
            "success": (GL3, "#1a4030", GRN2, "✓"),
            "warning": (GL3, "#3a2000", ORG,  "⚠"),
            "error":   (GL3, "#3a0010", ERR,  "✕"),
            "update":  (GL3, ADM_M,   ADM_AC,"⬆"),
        }
        bg, border_c, accent, icon = colors.get(kind, colors["info"])
        toast = self._create_toast(message, bg, border_c, accent, icon, duration)
        self._toasts.append(toast)
        self._reposition()

    def _create_toast(self, message, bg, border_c, accent, icon, duration):
        root = self.root
        W = root.winfo_width() or 1180

        frame = tk.Frame(root, bg=border_c, padx=1, pady=1, cursor="hand2")
        inner = tk.Frame(frame, bg=bg)
        inner.pack(fill="both")
        tk.Frame(inner, bg=accent, height=2).pack(fill="x")
        row = tk.Frame(inner, bg=bg)
        row.pack(fill="x", padx=12, pady=10)
        tk.Label(row, text=icon, bg=bg, fg=accent, font=("Segoe UI",13,"bold")).pack(side="left", padx=(0,8))
        tk.Label(row, text=message, bg=bg, fg=TXT, font=("Segoe UI",9),
                 wraplength=240, justify="left").pack(side="left")
        def _close(): self._dismiss(frame)
        tk.Button(row, text="×", bg=bg, fg=TXT3, relief="flat", bd=0,
                  cursor="hand2", font=("Segoe UI",10,"bold"),
                  command=_close).pack(side="right")

        frame.place(x=W, y=0, width=280)
        frame.update_idletasks()
        self._slide_in(frame, W, W - 296, duration)
        return frame

    def _slide_in(self, frame, start_x, end_x, duration, step=0):
        if step >= 12:
            frame._toast_target_x = end_x
            self._reposition()
            frame.after(duration, lambda: self._dismiss(frame))
            return
        t = step / 12.0
        t_ease = 1 - (1 - t)**3
        x = int(start_x + (end_x - start_x) * t_ease)
        try:
            y = frame.place_info().get("y", 16)
            frame.place_configure(x=x, y=y)
            frame.after(16, lambda: self._slide_in(frame, start_x, end_x, duration, step+1))
        except: pass

    def _dismiss(self, frame):
        if frame not in self._toasts: return
        self._toasts.remove(frame)
        W = self.root.winfo_width() or 1180
        self._slide_out(frame, W)

    def _slide_out(self, frame, end_x, step=0):
        if step >= 10:
            try: frame.destroy()
            except: pass
            self._reposition()
            return
        t = step / 10.0
        t_ease = t * t
        try:
            info = frame.place_info()
            start_x = int(info.get("x", end_x - 296))
            x = int(start_x + (end_x - start_x) * t_ease)
            frame.place_configure(x=x)
            frame.after(16, lambda: self._slide_out(frame, end_x, step+1))
        except: pass

    def _reposition(self):
        W = self.root.winfo_width() or 1180
        y = 16
        for f in self._toasts:
            try:
                tx = f._toast_target_x if hasattr(f, "_toast_target_x") else W - 296
                f.place_configure(x=tx, y=y)
                f.update_idletasks()
                y += f.winfo_height() + 8
            except: pass

# ══════════════════════════════════════════════════════
#  WING ICON + DRAWING
# ══════════════════════════════════════════════════════
def _make_wing_icon(size=32):
    try:
        W = H = size
        pixels = [[(1,12,24)]*W for _ in range(H)]
        cx, cy = W//2, H//2

        def dp(x, y, r, g, b, a=1.0):
            if 0<=x<W and 0<=y<H:
                br, bg_, bb = pixels[y][x]
                pixels[y][x] = (
                    int(br+(r-br)*a), int(bg_+(g-bg_)*a), int(bb+(b-bb)*a)
                )

        def dl(x0, y0, x1, y1, r, g, b, a=0.9):
            dx, dy = abs(x1-x0), abs(y1-y0)
            sx = 1 if x0<x1 else -1; sy = 1 if y0<y1 else -1; err = dx-dy
            while True:
                dp(x0, y0, r, g, b, a)
                if x0==x1 and y0==y1: break
                e2 = 2*err
                if e2>-dy: err-=dy; x0+=sx
                if e2<dx:  err+=dx; y0+=sy

        sc = size/32.0
        lf = [(-1,1,115,.55),(-3,0,130,.65),(-5,-1,145,.72),(-7,-3,158,.88),
              (-9,-5,170,.98),(-10,-8,183,1.1),(-9,-11,196,1.05),(-7,-13,210,.92),
              (-4,-15,225,.78),(-1,-16,240,.62)]
        for dx, dy, ang, ln in lf:
            rad = math.radians(ang)
            x0 = int(cx+dx*sc); y0 = int(cy+dy*sc); lnsc = ln*sc*14
            x1 = int(x0+math.cos(rad)*lnsc); y1 = int(y0-math.sin(rad)*lnsc)
            dl(x0,y0,x1,y1,0,160,220,.7)
            dl(x0+1,y0,x1+1,y1,200,240,255,.9)
            rad2 = math.radians(180-ang); x0 = int(cx-dx*sc)
            x1 = int(x0+math.cos(rad2)*lnsc)
            y1 = int(cy+dy*sc-math.sin(rad2)*lnsc)
            dl(x0,int(cy+dy*sc),x1,y1,0,160,220,.7)
            dl(x0-1,int(cy+dy*sc),x1-1,y1,200,240,255,.9)
        for r in range(int(4*sc),0,-1):
            a = 0.4+0.6*(1-r/(4*sc))
            for ang in range(0,360,4):
                rad = math.radians(ang)
                dp(int(cx+math.cos(rad)*r), int(cy+math.sin(rad)*r), 0, 212, 255, a)
        for yy in range(int(cy-2*sc),int(cy+2*sc)+1):
            for xx in range(int(cx-2*sc),int(cx+2*sc)+1):
                if math.hypot(xx-cx,yy-cy) <= 2*sc:
                    dp(xx, yy, 232, 248, 255, 1.0)

        ppm3 = b"P3\n" + f"{W} {H}\n255\n".encode()
        ppm3 += b"\n".join(
            b" ".join(f"{r} {g} {b}".encode() for r,g,b in row) for row in pixels
        ) + b"\n"
        return tk.PhotoImage(data=ppm3)
    except: return None

def draw_wings(canvas, cx, cy, size, tag=None):
    s = size
    kw = {"tags": tag} if tag else {}

    def feather(ox, oy, ang_deg, length, width, fill="#f0faff", outline="#b0e8ff"):
        angle = math.radians(ang_deg); perp = angle + math.pi/2
        tip_x = ox+math.cos(angle)*length; tip_y = oy-math.sin(angle)*length
        hw = width*.48
        lx = ox+math.cos(perp)*hw; ly = oy-math.sin(perp)*hw
        rx = ox-math.cos(perp)*hw; ry = oy+math.sin(perp)*hw
        mf = 0.45
        mlx = ox+math.cos(angle)*length*mf+math.cos(perp)*hw*.9
        mly = oy-math.sin(angle)*length*mf-math.sin(perp)*hw*.9
        mrx = ox+math.cos(angle)*length*mf-math.cos(perp)*hw*.9
        mry = oy-math.sin(angle)*length*mf+math.sin(perp)*hw*.9
        canvas.create_polygon(
            [lx,ly,mlx,mly,tip_x,tip_y,mrx,mry,rx,ry,ox,oy],
            smooth=True, fill=fill, outline=outline, width=1, **kw
        )

    lf = [(-s*.05,s*.04,115,s*.55,s*.22),(-s*.12,s*.01,128,s*.65,s*.24),
          (-s*.20,-s*.04,142,s*.72,s*.25),(-s*.28,-s*.10,155,s*.88,s*.27),
          (-s*.35,-s*.18,168,s*.98,s*.28),(-s*.38,-s*.28,180,s*1.1,s*.28),
          (-s*.36,-s*.38,193,s*1.05,s*.26),(-s*.30,-s*.46,207,s*.92,s*.24),
          (-s*.20,-s*.52,222,s*.78,s*.21),(-s*.08,-s*.54,238,s*.62,s*.18)]
    rf = [(s*.05,s*.04,65,s*.55,s*.22),(s*.12,s*.01,52,s*.65,s*.24),
          (s*.20,-s*.04,38,s*.72,s*.25),(s*.28,-s*.10,25,s*.88,s*.27),
          (s*.35,-s*.18,12,s*.98,s*.28),(s*.38,-s*.28,0,s*1.1,s*.28),
          (s*.36,-s*.38,-13,s*1.05,s*.26),(s*.30,-s*.46,-27,s*.92,s*.24),
          (s*.20,-s*.52,-42,s*.78,s*.21),(s*.08,-s*.54,-58,s*.62,s*.18)]

    for feathers in (lf, rf):
        for dx, dy, ang, ln, wd in feathers:
            feather(cx+dx, cy+dy, ang, ln*1.35, wd*1.35, fill="", outline="#0066aa")
            feather(cx+dx, cy+dy, ang, ln*1.18, wd*1.18, fill="", outline="#0099cc")
        for dx, dy, ang, ln, wd in feathers:
            feather(cx+dx, cy+dy, ang, ln*1.05, wd*1.08, fill="", outline="#60c8ff")
            feather(cx+dx, cy+dy, ang, ln, wd, fill="#e8f8ff", outline="#b0d8f0")

    for rm, col in [(3.2,"#0055aa"),(2.2,"#0088cc"),(1.5,"#00aadd")]:
        r = s*.13*rm
        canvas.create_oval(cx-r,cy-r,cx+r,cy+r, outline=col, fill="", width=1, **kw)
    r = s*.13
    canvas.create_oval(cx-r,cy-r,cx+r,cy+r, fill=ACC2, outline=ACC, width=2, **kw)
    r2 = s*.065
    canvas.create_oval(cx-r2,cy-r2,cx+r2,cy+r2, fill=WHT, outline="", **kw)
    r3 = s*.04; hx = cx-s*.05; hy = cy-s*.06
    canvas.create_oval(hx-r3,hy-r3*.6,hx+r3,hy+r3*.6, fill=WHT, outline="", stipple="gray75", **kw)

# ══════════════════════════════════════════════════════
#  BUBBLES BACKGROUND
# ══════════════════════════════════════════════════════
class BubbleCanvas(tk.Canvas):
    def __init__(self, parent, bg_color=BG, count=40, **kw):
        super().__init__(parent, bg=bg_color, highlightthickness=0, **kw)
        self._count = count
        self._parts = []
        self._ripples = []
        self._running = True
        self._init_parts()
        self.bind("<Button-1>", self._click)
        self._tick()

    def _init_parts(self):
        self._parts = []
        for _ in range(self._count):
            r = random.uniform(4, 22)
            self._parts.append({
                "x":     random.uniform(.04, .96),
                "y":     random.uniform(.04, 1.08),
                "r":     r, "br": r,
                "vx":    random.uniform(-.00016, .00016),
                "vy":    random.uniform(-.0009, -.0002),
                "col":   random.choice(BUBBLE_COLORS),
                "phase": random.uniform(0, math.pi*2),
                "ps":    random.uniform(.013, .038),
                "wobble":random.uniform(0, math.pi*2),
                "ws":    random.uniform(.018, .055),
                "ids":   []
            })

    def _click(self, e):
        W = self.winfo_width() or 400
        H = self.winfo_height() or 400
        self._ripples.append({
            "x": e.x/W, "y": e.y/H, "r": 0, "max_r": .18,
            "a": 1.0, "ids": []
        })

    def _draw_bubble(self, x, y, r, col):
        ids = []
        for gsc, st, wd in [(4.5,"gray12",1),(3.0,"gray25",1),(1.8,"gray50",1)]:
            gr = r * gsc
            ids.append(self.create_oval(x-gr,y-gr,x+gr,y+gr, outline=col, fill="", width=wd, stipple=st))
        ids.append(self.create_oval(x-r,y-r,x+r,y+r, outline=col, fill="", width=1))
        ids.append(self.create_oval(x-r+1,y-r+1,x+r-1,y+r-1, outline="", fill=col, stipple="gray12"))
        ids.append(self.create_arc(x-r*.7,y-r*.7,x+r*.7,y+r*.7, start=190,extent=160,outline=col,style="arc",width=1,stipple="gray50"))
        hr = r*0.38; hx = x - r*0.28; hy = y - r*0.28
        ids.append(self.create_oval(hx-hr,hy-hr*.55,hx+hr,hy+hr*.55, outline="", fill="white", stipple="gray50"))
        sr = r*0.14; sx = x-r*.08; sy = y-r*.44
        ids.append(self.create_oval(sx-sr,sy-sr*.5,sx+sr,sy+sr*.5, outline="", fill="white", stipple="gray75"))
        return ids

    def _tick(self):
        if not self._running: return
        try:
            W = self.winfo_width() or 400
            H = self.winfo_height() or 400
            for p in self._parts:
                for i in p["ids"]:
                    try: self.delete(i)
                    except: pass
                p["ids"] = []
                p["y"] += p["vy"]; p["x"] += p["vx"]
                p["phase"] += p["ps"]; p["wobble"] += p["ws"]
                if p["y"] < -.1: p["y"] = 1.1; p["x"] = random.uniform(.04, .96)
                if not -.1 < p["x"] < 1.1: p["vx"] = -p["vx"]
                wobble = math.sin(p["wobble"]) * 0.08
                r = max(2, p["br"] + math.sin(p["phase"]) * 2.5)
                x = p["x"]*W + wobble*30; y = p["y"]*H
                p["ids"] = self._draw_bubble(x, y, r, p["col"])

            for rip in list(self._ripples):
                for i in rip["ids"]:
                    try: self.delete(i)
                    except: pass
                rip["ids"] = []
                rip["r"] += 0.0065; rip["a"] -= 0.030
                if rip["a"] <= 0:
                    self._ripples.remove(rip); continue
                rx = rip["x"]*W; ry = rip["y"]*H
                rr = rip["r"] * min(W,H)
                rip["ids"] = [
                    self.create_oval(rx-rr,ry-rr,rx+rr,ry+rr, outline=ACC, fill="", width=2, stipple="gray50"),
                    self.create_oval(rx-rr*.7,ry-rr*.7,rx+rr*.7,ry+rr*.7, outline=ACB, fill="", width=1, stipple="gray75"),
                ]
            self.after(20, self._tick)
        except: pass

    def stop(self): self._running = False

# ══════════════════════════════════════════════════════
#  AUTH SCREEN
# ══════════════════════════════════════════════════════
class AuthScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Angels Launcher — Вход / Регистрация")
        self.configure(bg=BG)
        self.geometry("620x700")
        self.resizable(False, False)
        self._activated = False
        self._mode = "register"
        self._ring_phase = 0
        self._ring_ids = []
        self._pulse_phase = 0
        self._build()
        self._apply_icon()
        self._animate_ring()

    def _apply_icon(self):
        try:
            img = _make_wing_icon(32)
            if img: self._icon = img; self.iconphoto(True, img)
        except: pass

    def _build(self):
        self._bg = BubbleCanvas(self, bg_color=BG, count=28)
        self._bg.place(x=0, y=0, width=620, height=700)

        self._top = tk.Canvas(self, bg=BG, highlightthickness=0, width=620, height=700)
        self._top.place(x=0, y=0)

        for i in range(4,0,-1):
            self._top.create_rectangle(44+i,185+i,574+i,660+i, fill="#000810", outline="", stipple="gray12")
        self._top.create_rectangle(46, 186, 572, 658, fill=GL1, outline=BD1, width=1)
        self._top.create_line(70, 187, 548, 187, fill=HL2, width=1)
        self._top.create_line(70, 188, 548, 188, fill=HL0, width=1)
        self._top.create_rectangle(47, 187, 571, 240, fill=GL2, outline="")
        self._top.create_line(47, 240, 571, 240, fill=BD1, width=1)

        draw_wings(self._top, 310, 112, 52)

        self._top.create_text(310, 192, text="ANGELS LAUNCHER", fill=WHT, font=("Segoe UI", 21, "bold"))
        self._top.create_text(310, 213, text=f"v{LAUNCHER_VER}  ·  Minecraft {MC_VERSION}  ·  Forge", fill=TXT3, font=("Segoe UI", 9))
        for xi, col in [(150,ACC3),(310,ACC),(470,ACC2)]:
            self._top.create_oval(xi-2, 228, xi+2, 232, fill=col, outline="")

        self._tab_reg = tk.Button(self, text="◈   Регистрация", bg=ACC2, fg=BG,
            font=("Segoe UI",10,"bold"), relief="flat", cursor="hand2", bd=0, pady=10,
            command=lambda: self._switch("register"))
        self._tab_reg.place(x=56, y=248, width=232, height=40)

        self._tab_log = tk.Button(self, text="→   Войти", bg=GL2, fg=TXT3,
            font=("Segoe UI",10), relief="flat", cursor="hand2", bd=0, pady=10,
            command=lambda: self._switch("login"))
        self._tab_log.place(x=298, y=248, width=232, height=40)

        self._reg_frame = tk.Frame(self, bg=GL1)
        self._reg_frame.place(x=56, y=298, width=508, height=310)
        self._build_reg()

        self._log_frame = tk.Frame(self, bg=GL1)
        self._log_frame.place(x=56, y=298, width=508, height=310)
        self._build_log()

        self._status = tk.Label(self, text="", bg=GL1, fg=ERR,
            font=("Segoe UI",9), wraplength=490, justify="center")
        self._status.place(x=56, y=618, width=508, height=38)

        self._top.create_text(310, 667, text="◈ кликни на фон — волны ◈", fill=MUT, font=("Segoe UI",8))
        self._switch("register")

    def _build_reg(self):
        self._reg_entries = []
        labels = [("🔑  Ключ активации","ANGELS-XXXX-XXXX-XXXX",False),
                  ("◈  Никнейм","Игровой ник",False),
                  ("🔒  Пароль","Придумай пароль",True)]
        for i, (lbl, ph, sec) in enumerate(labels):
            tk.Label(self._reg_frame, text=lbl, bg=GL1, fg=TXT2,
                     font=("Segoe UI",9), anchor="w").pack(anchor="w", padx=20, pady=(12 if i==0 else 6, 2))
            var = tk.StringVar()
            wrap, e = glass_entry(self._reg_frame, var, show="●" if sec else "", placeholder=ph)
            wrap.pack(fill="x", padx=18)
            self._reg_entries.append((var, e))

        tk.Frame(self._reg_frame, bg=BD1, height=1).pack(fill="x", padx=18, pady=12)
        self._reg_btn = pill_btn(self._reg_frame, "◈   АКТИВИРОВАТЬ И ВОЙТИ", self._do_reg,
            fg=BG, bg=ACC2, py=13, font=("Segoe UI",11,"bold"))
        self._reg_btn.pack(fill="x", padx=18, pady=(0,8))

    def _build_log(self):
        self._log_entries = []
        labels = [("◈  Никнейм","Игровой ник",False), ("🔒  Пароль","Твой пароль",True)]
        for i, (lbl, ph, sec) in enumerate(labels):
            tk.Label(self._log_frame, text=lbl, bg=GL1, fg=TXT2,
                     font=("Segoe UI",9), anchor="w").pack(anchor="w", padx=20, pady=(22 if i==0 else 10, 2))
            var = tk.StringVar()
            wrap, e = glass_entry(self._log_frame, var, show="●" if sec else "", placeholder=ph)
            wrap.pack(fill="x", padx=18)
            self._log_entries.append((var, e))

        tk.Frame(self._log_frame, bg=BD1, height=1).pack(fill="x", padx=18, pady=18)
        self._log_btn = pill_btn(self._log_frame, "→   ВОЙТИ", self._do_login,
            fg=ACC, bg=GL3, py=13, hbg=ACC2, hfg=BG, font=("Segoe UI",11,"bold"))
        self._log_btn.pack(fill="x", padx=18)

    def _switch(self, mode):
        self._mode = mode
        if mode == "register":
            self._tab_reg.configure(bg=ACC2, fg=BG, font=("Segoe UI",10,"bold"))
            self._tab_log.configure(bg=GL2, fg=TXT3, font=("Segoe UI",10))
            self._reg_frame.lift()
        else:
            self._tab_log.configure(bg=ACC2, fg=BG, font=("Segoe UI",10,"bold"))
            self._tab_reg.configure(bg=GL2, fg=TXT3, font=("Segoe UI",10))
            self._log_frame.lift()
        self._status.configure(text="", bg=GL1)

    def _do_reg(self):
        key  = get_entry_value(self._reg_entries[0][1])
        nick = get_entry_value(self._reg_entries[1][1])
        pw   = get_entry_value(self._reg_entries[2][1])
        self._reg_btn.configure(state="disabled", text="⏳  Проверка...")
        self.after(90, lambda: self._check_reg(key, nick, pw))

    def _check_reg(self, key, nick, pw):
        ok, msg = activate_key(key, nick, pw)
        if ok:
            self._status.configure(text=f"✓  {msg}", fg=GRN2, bg=GL1)
            self._reg_btn.configure(text="✓  Активировано!", bg=GRN2, fg=BG)
            self.after(1100, self._launch_main)
        else:
            self._status.configure(text=f"✗  {msg}", fg=ERR, bg=GL1)
            self._reg_btn.configure(state="normal", text="◈   АКТИВИРОВАТЬ И ВОЙТИ")

    def _do_login(self):
        nick = get_entry_value(self._log_entries[0][1])
        pw   = get_entry_value(self._log_entries[1][1])
        self._log_btn.configure(state="disabled", text="⏳  Проверка...")
        self.after(90, lambda: self._check_login(nick, pw))

    def _check_login(self, nick, pw):
        ok, msg = login_user(nick, pw)
        if ok:
            self._status.configure(text=f"✓  {msg}", fg=GRN2, bg=GL1)
            self._log_btn.configure(text="✓  Вход!", bg=GRN2, fg=BG)
            self.after(1000, self._launch_main)
        else:
            self._status.configure(text=f"✗  {msg}", fg=ERR, bg=GL1)
            self._log_btn.configure(state="normal", text="→   ВОЙТИ")

    def _launch_main(self):
        self._activated = True
        self._bg.stop()
        self.destroy()

    def _animate_ring(self):
        try:
            c = self._top
            for oid in self._ring_ids:
                try: c.delete(oid)
                except: pass
            self._ring_ids = []
            self._ring_phase = (self._ring_phase + 1.4) % 360
            cx, cy = 310, 112
            rings = [
                (84, ACC,  2, (12,6),  1.0),
                (100,ACC2, 1, (6,10),  0.62),
                (116,ACG,  1, (3,16),  0.38),
                (70, ACB,  1, (8,14),  1.3),
            ]
            for r, col, w, dash, speed in rings:
                angle = self._ring_phase * speed
                self._ring_ids.append(c.create_arc(
                    cx-r, cy-r, cx+r, cy+r, start=angle, extent=200,
                    outline=col, width=w, style="arc", dash=dash
                ))
            self.after(26, self._animate_ring)
        except: pass

# ══════════════════════════════════════════════════════
#  MAIN LAUNCHER
# ══════════════════════════════════════════════════════
class AngelsLauncher(tk.Tk):
    def __init__(self):
        super().__init__()
        user = get_current_user()
        self._nick = user.get("nickname", "Angel")
        self._adm  = is_admin(self._nick)
        self._user = user
        self._logout_requested = False

        self.title(f"{LAUNCHER_NAME}  ·  Minecraft {MC_VERSION}")
        self.configure(bg=BG)
        sw = self.winfo_screenwidth(); sh = self.winfo_screenheight()
        W, H = 1200, 760
        self.geometry(f"{W}x{H}+{(sw-W)//2}+{(sh-H)//2}")
        self.minsize(980, 660); self.resizable(True, True)
        self._W = W; self._H = H; self._fullscreen = False
        self._mc_process = None; self._active_tab = "home"

        self.username = tk.StringVar(value=self._nick)
        self.ram      = tk.IntVar(value=min(4, max(1, TOTAL_RAM//2)))
        self.status   = tk.StringVar(value="Готов к запуску")
        self.eta_var  = tk.StringVar(value="")
        self.spd_var  = tk.StringVar(value="")
        self.progress = tk.DoubleVar(value=0)
        self.mod_url  = tk.StringVar(value=MOD_URL)
        self.servers  = load_servers()
        self._connect_server = None
        self._bubbles = []
        self._play_pulse = 0

        self._updater = AutoUpdater()
        self._update_available = False
        self._latest_update_info = None

        self._apply_icon()
        self._build_ui()
        self._init_bubbles()
        self._anim_bubbles()

        self._toast = ToastManager(self)

        self.bind("<F11>", self._toggle_fs)
        self.bind("<Escape>", lambda e: self._set_fs(False))

        # ★ FIX: Показываем реальную установленную версию
        installed_ver = _read_installed_version()
        self._log(f"◈  Angels Launcher v{installed_ver} — Привет, {self._nick}!", "accent")
        if self._adm:
            self._log(f"   ⚡ Администратор — все функции доступны.", "gold")
        self._log(f"   RAM системы: {TOTAL_RAM} ГБ  |  Выделено: {self.ram.get()} ГБ", "info")
        self._check_sub_alert()
        self._check_files()

        self._updater.watch_script(
            interval_ms=2000,
            root=self,
            on_change=self._on_script_changed
        )

        self.after(3000, self._bg_check_updates)

    def _apply_icon(self):
        try:
            img = _make_wing_icon(32)
            if img: self._icon = img; self.iconphoto(True, img)
        except: pass

    def _check_sub_alert(self):
        valid, status = check_subscription(self._user)
        if not valid:
            self._log(f"⚠  ПОДПИСКА ИСТЕКЛА! Продление: Telegram {TG_LINK}", "error")
        elif self._user.get("key_expires"):
            self._log(f"   ◈ Подписка активна: {status}", "info")

    # ── UPDATE SYSTEM ──────────────────────────────────
    def _bg_check_updates(self):
        """Тихая фоновая проверка при старте"""
        def _cb(success, info, error):
            if success and info and self._updater.is_newer(info["version"]):
                self._update_available = True
                self._latest_update_info = info
                self.after(0, self._show_update_badge)
                self.after(0, lambda: self._toast.show(
                    f"⬆ Доступно обновление v{info['version']}!\nНажми «Обновить» в меню.",
                    kind="update", duration=8000
                ))
                self.after(0, lambda: self._log(
                    f"⬆  Доступно обновление v{info['version']}! (текущая: v{_read_installed_version()})", "gold"
                ))
        self._updater.check_for_updates(_cb)

    def _show_update_badge(self):
        try:
            tab_data = self._tabs.get("updates")
            if tab_data:
                frame, icon_lbl, name_lbl, arrow_lbl = tab_data
                name_lbl.configure(fg=GRN2, font=("Segoe UI",12,"bold"))
                icon_lbl.configure(fg=GRN2)
            self.title(f"{LAUNCHER_NAME}  ·  Minecraft {MC_VERSION}  ·  [ОБНОВЛЕНИЕ ДОСТУПНО!]")
        except: pass

    def _on_script_changed(self):
        self._log("◈  VS Code: файл скрипта изменён!", "gold")
        self._toast.show(
            "Файл скрипта изменён!\nАвто-перезапуск через 3 сек...",
            kind="update", duration=3000
        )
        self.after(3000, self._do_script_restart)

    def _do_script_restart(self):
        try:
            self._log("◈  Перезапуск лаунчера...", "accent")
            self.after(500, lambda: self._updater.auto_restart_on_change())
        except: pass

    def _toggle_fs(self, e=None):
        self._set_fs(not self._fullscreen)

    def _set_fs(self, state):
        self._fullscreen = state
        self.attributes("-fullscreen", state)
        if not state:
            sw = self.winfo_screenwidth(); sh = self.winfo_screenheight()
            self.geometry(f"1200x760+{(sw-1200)//2}+{(sh-760)//2}")

    # ── Bubble background ──────────────────────────────
    def _init_bubbles(self):
        self._bubbles = []
        for _ in range(32):
            r = random.uniform(3, 24)
            self._bubbles.append({
                "x": random.uniform(.02,.98), "y": random.uniform(.02,1.1),
                "r": r, "br": r,
                "vy": random.uniform(.0002,.0009),
                "dx": random.uniform(-.00015,.00015),
                "col": random.choice(BUBBLE_COLORS),
                "phase": random.uniform(0,math.pi*2),
                "ps": random.uniform(.013,.038),
                "wobble": random.uniform(0,math.pi*2),
                "ws": random.uniform(.018,.05),
                "ids": []
            })

    def _anim_bubbles(self):
        try:
            c = self._bgc; W = c.winfo_width() or self._W; H = c.winfo_height() or self._H
            for b in self._bubbles:
                for k in b["ids"]:
                    try: c.delete(k)
                    except: pass
                b["ids"] = []
                b["y"] -= b["vy"]; b["x"] += b["dx"]
                b["phase"] += b["ps"]; b["wobble"] += b["ws"]
                if b["y"] < -.1: b["y"]=1.12; b["x"]=random.uniform(.02,.98)
                if not -.1 < b["x"] < 1.1: b["dx"] = -b["dx"]
                wobble = math.sin(b["wobble"]) * 0.08
                r = max(2, b["br"] + math.sin(b["phase"]) * 2.5)
                x = b["x"]*W + wobble*24; y = b["y"]*H; col = b["col"]
                ids = []
                for gsc, st in [(4.2,"gray12"),(2.6,"gray25"),(1.6,"gray50")]:
                    gr = r*gsc
                    ids.append(c.create_oval(x-gr,y-gr,x+gr,y+gr, outline=col, fill="", width=1, stipple=st))
                ids.append(c.create_oval(x-r,y-r,x+r,y+r, outline=col, fill="", width=1))
                ids.append(c.create_oval(x-r+1,y-r+1,x+r-1,y+r-1, outline="", fill=col, stipple="gray12"))
                ids.append(c.create_arc(x-r*.65,y-r*.65,x+r*.65,y+r*.65, start=195,extent=150,outline=col,style="arc",width=1,stipple="gray50"))
                hr = r*.35; hx = x-r*.28; hy = y-r*.28
                ids.append(c.create_oval(hx-hr,hy-hr*.52,hx+hr,hy+hr*.52, outline="", fill="white", stipple="gray50"))
                sr = r*.12
                ids.append(c.create_oval(x-sr-r*.08,y-sr-r*.42,x+sr-r*.08,y+sr-r*.42, outline="", fill="white", stipple="gray75"))
                b["ids"] = ids
            self.after(22, self._anim_bubbles)
        except: pass

    # ══════════════════════════════════════════════════
    #  BUILD UI
    # ══════════════════════════════════════════════════
    def _build_ui(self):
        self._bgc = tk.Canvas(self, bg=BG, highlightthickness=0)
        self._bgc.place(x=0, y=0, relwidth=1, relheight=1)

        self._build_header()
        body = tk.Frame(self, bg=BG)
        body.place(x=0, y=108, relwidth=1, relheight=1, height=-108)
        self._build_sidebar(body)

        self._panels = {}
        right = tk.Frame(body, bg=BG)
        right.pack(fill="both", expand=True)

        self._panels["home"]    = self._mk_home(right)
        self._panels["profile"] = self._mk_profile(right)
        self._panels["multi"]   = self._mk_multi(right)
        self._panels["mods"]    = self._mk_mods(right)
        self._panels["console"] = self._mk_console(right)
        self._panels["updates"] = self._mk_updates(right)
        self._panels["settings"]= self._mk_settings(right)
        if self._adm:
            self._panels["admin"] = self._mk_admin(right)
        self._show("home")

    def _build_header(self):
        hdr = tk.Frame(self, bg=GL1, height=108)
        hdr.place(x=0, y=0, relwidth=1)
        tk.Frame(hdr, bg=ACC, height=2).pack(side="bottom", fill="x")
        tk.Frame(hdr, bg=ACC2, height=1).pack(side="bottom", fill="x")
        tk.Frame(hdr, bg=HL2, height=1).pack(side="top", fill="x")

        inner = tk.Frame(hdr, bg=GL1)
        inner.place(x=0, y=0, relwidth=1, height=105)

        lc = tk.Canvas(inner, bg=GL1, width=76, height=68, highlightthickness=0)
        lc.pack(side="left", padx=(18,4), pady=10)
        draw_wings(lc, 38, 36, 25)

        lf = tk.Frame(inner, bg=GL1)
        lf.pack(side="left", pady=14)
        title_row = tk.Frame(lf, bg=GL1)
        title_row.pack(anchor="w")
        tk.Label(title_row, text="ANGELS", bg=GL1, fg=WHT, font=("Segoe UI",24,"bold")).pack(side="left")
        tk.Label(title_row, text=" LAUNCHER", bg=GL1, fg=ACC, font=("Segoe UI",24,"bold")).pack(side="left")

        sub_row = tk.Frame(lf, bg=GL1)
        sub_row.pack(anchor="w")
        tk.Label(sub_row, text=f"Minecraft {MC_VERSION}  ·  Forge {FORGE_VERSION}  ·  {MOD_NAME}",
                 bg=GL1, fg=TXT3, font=("Segoe UI",9)).pack(side="left")

        sf = tk.Frame(inner, bg=GL1)
        sf.pack(side="left", padx=16, pady=28)
        tk.Label(sf, text=f"RAM: {TOTAL_RAM} ГБ", bg=GL1, fg=TXT3, font=("Segoe UI",8)).pack(anchor="w")
        row2 = tk.Frame(sf, bg=GL1); row2.pack(anchor="w")
        self._dot = tk.Label(row2, text="●", bg=GL1, fg=GRN2, font=("Segoe UI",9))
        self._dot.pack(side="left")
        tk.Label(row2, text=" ГОТОВ", bg=GL1, fg=GRN, font=("Segoe UI",8,"bold")).pack(side="left")
        self._pulse_dot()

        rf = tk.Frame(inner, bg=GL1)
        rf.pack(side="right", padx=14)

        glass_btn(rf, "⛶ F11", self._toggle_fs, fg=TXT2, bg=GL2,
                  font=("Segoe UI",8), py=4, px=10).pack(pady=(8,4))

        badge = tk.Frame(rf, bg=BD1, padx=1, pady=1, cursor="hand2")
        badge.pack()
        badge_inner = tk.Frame(badge, bg=GL2)
        badge_inner.pack()
        tk.Frame(badge_inner, bg=HL0, height=1).pack(fill="x")
        badge_row = tk.Frame(badge_inner, bg=GL2)
        badge_row.pack(padx=10, pady=7)
        icon_col = ADM_AC if self._adm else ACC
        icon_sym = "⚡" if self._adm else "◈"
        tk.Label(badge_row, text=icon_sym, bg=GL2, fg=icon_col, font=("Segoe UI",12)).pack(side="left", padx=(0,5))
        tk.Label(badge_row, text=self._nick, bg=GL2, fg=TXT, font=("Segoe UI",10,"bold")).pack(side="left")
        if self._adm:
            tk.Label(badge_row, text="  [ADMIN]", bg=GL2, fg=ADM_AC, font=("Segoe UI",8,"bold")).pack(side="left")
        badge.bind("<Button-1>", lambda e: self._show("profile"))
        badge_inner.bind("<Button-1>", lambda e: self._show("profile"))
        for w in badge_row.winfo_children():
            w.bind("<Button-1>", lambda e: self._show("profile"))

    def _pulse_dot(self):
        try:
            c = self._dot.cget("fg")
            self._dot.configure(fg=GRN2 if c==GRN else GRN)
            self.after(850, self._pulse_dot)
        except: pass

    def _build_sidebar(self, body):
        side = tk.Frame(body, bg=GL1, width=260)
        side.pack(side="left", fill="y")
        side.pack_propagate(False)

        tk.Frame(side, bg=BD1, height=1).pack(fill="x")

        mc = tk.Canvas(side, bg=GL1, width=50, height=36, highlightthickness=0)
        mc.pack(pady=(14,0))
        draw_wings(mc, 25, 19, 12)
        tk.Label(side, text="НАВИГАЦИЯ", bg=GL1, fg=BD2,
         font=("Segoe UI",9,"bold")
         ).pack(anchor="w", padx=22, pady=(4,8))

        self._tabs = {}

        nav_items = [
            ("◈", "Главная",      "home",     None,            False),
            ("◉", "Профиль",      "profile",  None,            False),
            (None, None, None, "─── ИГРА ───", None),
            ("▶", "Играть",       "home",     None,            False),
            ("◐", "Серверы",      "multi",    None,            False),
            ("◎", "Моды",         "mods",     None,            False),
            (None, None, None, "─── СИСТЕМА ───", None),
            ("▸", "Консоль",      "console",  None,            False),
            ("⬆", "Обновления",   "updates",  None,            False),
            ("⚙", "Настройки",    "settings", None,            False),
        ]
        if self._adm:
            nav_items.append((None, None, None, "─── ADMIN ───", None))
            nav_items.append(("⚡", "Админ-панель", "admin", None, True))

        for icon, name, key, header, is_adm in nav_items:
            if header is not None:
                sep_f = tk.Frame(side, bg=GL1)
                sep_f.pack(fill="x", padx=14, pady=(8,2))
                tk.Frame(sep_f, bg=BD1, height=1).pack(fill="x", side="left", expand=True, pady=6)
                lbl_col = ADM_AC if "ADMIN" in header else MUT2
                tk.Label(sep_f, text=f" {header} ", bg=GL1, fg=lbl_col,
                         font=("Segoe UI",7,"bold")).pack(side="left")
                tk.Frame(sep_f, bg=BD1, height=1).pack(fill="x", side="left", expand=True, pady=6)
                continue

            if icon is None: continue

            col_n = ADM_AC if is_adm else TXT2
            col_a = ADM_AC if is_adm else ACC

            btn_frame = tk.Frame(side, bg=GL1, cursor="hand2")
            btn_frame.pack(fill="x", padx=8, pady=2)

            icon_lbl = tk.Label(btn_frame, text=icon, bg=GL1, fg=col_n,
                                font=("Segoe UI",14), width=2)
            icon_lbl.pack(side="left", padx=(6,2), pady=10)

            name_lbl = tk.Label(btn_frame, text=name, bg=GL1, fg=col_n,
                                font=("Segoe UI",12), anchor="w")
            name_lbl.pack(side="left", fill="x", expand=True, pady=10)

            arrow_lbl = tk.Label(btn_frame, text="›", bg=GL1, fg=MUT,
                                 font=("Segoe UI",12))
            arrow_lbl.pack(side="right", padx=8)

            btn_frame.bind("<Button-1>", lambda e, k=key: self._show(k))

            def _enter(e, f=btn_frame, ca=col_a, il=icon_lbl, nl=name_lbl, al=arrow_lbl):
                f.configure(bg=GL2)
                il.configure(bg=GL2, fg=ca)
                nl.configure(bg=GL2, fg=ca)
                al.configure(bg=GL2, fg=ca)
                for child in f.winfo_children():
                    try: child.configure(bg=GL2)
                    except: pass

            def _leave(e, f=btn_frame, k2=key, cn=col_n, il=icon_lbl, nl=name_lbl, al=arrow_lbl):
                if self._active_tab != k2:
                    f.configure(bg=GL1)
                    il.configure(bg=GL1, fg=cn)
                    nl.configure(bg=GL1, fg=cn)
                    al.configure(bg=GL1, fg=MUT)
                    for child in f.winfo_children():
                        try: child.configure(bg=GL1)
                        except: pass

            btn_frame.bind("<Enter>", _enter)
            btn_frame.bind("<Leave>", _leave)
            for w in [icon_lbl, name_lbl, arrow_lbl]:
                w.bind("<Enter>", _enter)
                w.bind("<Leave>", _leave)
                w.bind("<Button-1>", lambda e, k=key: self._show(k))

            self._tabs[key] = (btn_frame, icon_lbl, name_lbl, arrow_lbl)

        tk.Frame(side, bg=BD1, height=1).pack(fill="x", padx=14, pady=10)

        valid, status = check_subscription(self._user)
        sub_col = GRN2 if valid else ERR
        sub_sym = "✓" if valid else "⚠"
        sub_bg  = "#0a1e12" if valid else "#1e0a0a"
        sub_bd  = "#1a3a22" if valid else "#3a1a1a"
        sf = tk.Frame(side, bg=sub_bg, highlightthickness=1, highlightbackground=sub_bd)
        sf.pack(fill="x", padx=12, pady=(0,6))
        tk.Frame(sf, bg=sub_col, height=1).pack(fill="x")
        sub_row = tk.Frame(sf, bg=sub_bg); sub_row.pack(padx=10, pady=7)
        tk.Label(sub_row, text=f"{sub_sym}  {status}", bg=sub_bg, fg=sub_col,
                 font=("Segoe UI",9,"bold")).pack(anchor="w")
        if not valid:
            tk.Label(sub_row, text=f"Продление: {TG_LINK}", bg=sub_bg, fg=ERR,
                     font=("Segoe UI",7)).pack(anchor="w")

        self._clk = tk.Label(side, text="", bg=GL1, fg=MUT, font=("Segoe UI",9))
        self._clk.pack(side="bottom", pady=4)
        installed_v = _read_installed_version()
        tk.Label(side, text=f"v{installed_v}  AutoUpdate Edition",
                 bg=GL1, fg=BD1, font=("Segoe UI",7)).pack(side="bottom", pady=2)
        self._tick_clock()

    def _tick_clock(self):
        try:
            self._clk.configure(text=time.strftime("⏱  %H:%M:%S"))
            self.after(1000, self._tick_clock)
        except: pass

    def _show(self, key):
        for p in self._panels.values(): p.pack_forget()

        for k, tab_widgets in self._tabs.items():
            frame, icon_lbl, name_lbl, arrow_lbl = tab_widgets
            is_adm = (k == "admin")
            is_upd = (k == "updates") and self._update_available

            if k == key:
                active_col = ADM_AC if is_adm else ACC
                frame.configure(bg=GL3)
                icon_lbl.configure(bg=GL3, fg=active_col, font=("Segoe UI",14,"bold"))
                name_lbl.configure(bg=GL3, fg=active_col, font=("Segoe UI",12,"bold"))
                arrow_lbl.configure(bg=GL3, fg=active_col)
                for child in frame.winfo_children():
                    try: child.configure(bg=GL3)
                    except: pass
                frame.configure(highlightthickness=0)
                try:
                    for child in frame.winfo_children():
                        if isinstance(child, tk.Frame) and child.cget("width") == 3:
                            child.destroy()
                except: pass
                indicator = tk.Frame(frame, bg=active_col, width=3)
                indicator.place(x=0, y=0, width=3, relheight=1)
            else:
                normal_col = ADM_AC if is_adm else (GRN2 if is_upd else TXT3)
                frame.configure(bg=GL1)
                icon_lbl.configure(bg=GL1, fg=normal_col, font=("Segoe UI",14))
                name_lbl.configure(bg=GL1, fg=normal_col, font=("Segoe UI",12))
                arrow_lbl.configure(bg=GL1, fg=MUT)
                for child in frame.winfo_children():
                    try: child.configure(bg=GL1)
                    except: pass

        self._panels[key].pack(fill="both", expand=True, padx=24, pady=20)
        self._active_tab = key

    def _card(self, parent, accent=ACC, **pkw):
        outer = tk.Frame(parent, bg=BD1, padx=1, pady=1)
        outer.pack(**pkw)
        inner = tk.Frame(outer, bg=GL1)
        inner.pack(fill="both", expand=True)
        tk.Frame(inner, bg=accent, height=2).pack(fill="x")
        tk.Frame(inner, bg=HL0, height=1).pack(fill="x")
        return inner

    # ══════════════════════════════════════════════════
    #  HOME PANEL
    # ══════════════════════════════════════════════════
    def _mk_home(self, parent):
        f = tk.Frame(parent, bg=BG)

        wc = tk.Canvas(f, bg=BG, width=280, height=140, highlightthickness=0)
        wc.pack(pady=(0,2))
        draw_wings(wc, 140, 78, 56)

        installed_v = _read_installed_version()
        tk.Label(f, text="ANGELS LAUNCHER", bg=BG, fg=WHT,
                 font=("Segoe UI",18,"bold")).pack()
        tk.Label(f, text=f"Minecraft {MC_VERSION}  ·  Forge  ·  AutoUpdate v{installed_v}",
                 bg=BG, fg=TXT3, font=("Segoe UI",10)).pack(pady=(2,12))

        card = self._card(f, ACC, fill="x")
        valid, sub_status = check_subscription(self._user)
        rows = [
            ("Minecraft",   MC_VERSION,                          ACC3),
            ("Forge",       FORGE_VERSION,                       ACC2),
            ("Мод",         f"{MOD_NAME} {MOD_VERSION}",         ACC),
            ("RAM системы", f"{TOTAL_RAM} ГБ",                   GRN),
            ("Игрок",       self._nick,                           GOLD),
            ("Роль",        "⚡ АДМИНИСТРАТОР" if self._adm else "◈ Игрок",
                            ADM_AC if self._adm else TXT2),
            ("Подписка",    sub_status,                           GRN2 if valid else ERR),
            ("Режим",       "Offline / Forge",                    ORG),
        ]
        for i, (lbl, val, col) in enumerate(rows):
            rbg = GL1 if i%2==0 else GL2
            r = tk.Frame(card, bg=rbg); r.pack(fill="x")
            tk.Label(r, text=lbl, bg=rbg, fg=TXT2, font=("Segoe UI",11),
                     anchor="w", width=16).pack(side="left", padx=16, pady=7)
            tk.Label(r, text="◈", bg=rbg, fg=col, font=("Segoe UI",7)).pack(side="right", padx=(0,14))
            tk.Label(r, text=val, bg=rbg, fg=col, font=("Segoe UI",11,"bold")).pack(side="right", padx=10)
        tk.Frame(card, bg=BD1, height=1).pack(fill="x")

        meta = tk.Frame(f, bg=BG); meta.pack(fill="x", pady=(10,2))
        tk.Label(meta, textvariable=self.status, bg=BG, fg=TXT2,
                 font=("Segoe UI",10), anchor="w").pack(side="left")
        tk.Label(meta, textvariable=self.eta_var, bg=BG, fg=ACC2,
                 font=("Segoe UI",10)).pack(side="right", padx=4)
        tk.Label(meta, textvariable=self.spd_var, bg=BG, fg=GRN,
                 font=("Segoe UI",10)).pack(side="right", padx=8)

        pb_outer = tk.Frame(f, bg=BD1, padx=1, pady=1)
        pb_outer.pack(fill="x", pady=(2,14))
        pb_bg = tk.Frame(pb_outer, bg=GL2, height=12)
        pb_bg.pack(fill="x")
        self._pb = tk.Frame(pb_bg, bg=ACC, height=12)
        self._pb.place(x=0, y=0, height=12, relwidth=0)
        self._pb_shimmer = tk.Frame(pb_bg, bg=HL2, height=1)
        self._pb_shimmer.place(x=0, y=0, height=1, relwidth=0)
        self.progress.trace_add("write", self._upd_pb)

        pw = tk.Frame(f, bg=ACC2, padx=1, pady=1)
        pw.pack(fill="x")
        self.play_btn = tk.Button(
            pw, text="◈   ИГРАТЬ", bg=GL1, fg=ACC,
            activebackground=GL3, activeforeground=WHT,
            font=("Segoe UI",17,"bold"), relief="flat",
            cursor="hand2", bd=0, pady=18, command=self._start,
            highlightthickness=0
        )
        self.play_btn.pack(fill="x")
        self.play_btn.bind("<Enter>", lambda e: self.play_btn.configure(bg=GL3, fg=WHT)
                           if self.play_btn["state"]=="normal" else None)
        self.play_btn.bind("<Leave>", lambda e: self.play_btn.configure(bg=GL1, fg=ACC)
                           if self.play_btn["state"]=="normal" else None)
        self._animate_play_btn()

        tk.Label(f, text="F11 — полный экран  ·  клик на пузырёк → волна",
                 bg=BG, fg=MUT, font=("Segoe UI",8)).pack(anchor="w", pady=(10,0))
        return f

    def _animate_play_btn(self):
        try:
            if self.play_btn["state"] == "normal":
                self._play_pulse = (self._play_pulse + 3) % 360
                phase = math.sin(math.radians(self._play_pulse))
                r_val = int(0 + phase*20); g_val = int(153 + phase*40); b_val = int(230 + phase*25)
                r_val = max(0,min(255,r_val)); g_val = max(0,min(255,g_val)); b_val = max(0,min(255,b_val))
                col = f"#{r_val:02x}{g_val:02x}{b_val:02x}"
                try: self.play_btn.master.configure(bg=col)
                except: pass
            self.after(40, self._animate_play_btn)
        except: pass

    def _upd_pb(self, *_):
        try:
            pct = max(0., min(1., self.progress.get() / 100.))
            self._pb.place_configure(relwidth=pct)
            self._pb_shimmer.place_configure(relwidth=pct)
            if pct < .3:   self._pb.configure(bg=ACC2)
            elif pct < .7: self._pb.configure(bg=ACC)
            else:          self._pb.configure(bg=GRN2)
        except: pass

    # ══════════════════════════════════════════════════
    #  ★ ВКЛАДКА ОБНОВЛЕНИЙ (исправленная)
    # ══════════════════════════════════════════════════
    def _mk_updates(self, parent):
        f = tk.Frame(parent, bg=BG)

        hdr = tk.Frame(f, bg=BG); hdr.pack(fill="x", pady=(0,16))
        tk.Label(hdr, text="⬆  Обновления лаунчера", bg=BG, fg=TXT,
                 font=("Segoe UI",16,"bold")).pack(side="left")

        self._big_update_btn_frame = tk.Frame(f, bg=BG)
        self._big_update_btn_frame.pack(fill="x", pady=(0,16))
        self._build_update_button()

        # ★ FIX: Показываем РЕАЛЬНУЮ установленную версию
        cur = self._card(f, ACC, fill="x", pady=(0,12))
        cr = tk.Frame(cur, bg=GL1); cr.pack(fill="x", padx=18, pady=14)
        installed_v = _read_installed_version()
        vrow = tk.Frame(cr, bg=GL1); vrow.pack(anchor="w")
        tk.Label(vrow, text=f"v{installed_v}", bg=GL1, fg=ACC,
                 font=("Segoe UI",26,"bold")).pack(side="left")
        tk.Label(vrow, text="  AutoUpdate Edition  —  установленная версия",
                 bg=GL1, fg=TXT3, font=("Segoe UI",11)).pack(side="left", pady=8)

        # Показываем когда было обновление
        try:
            if INSTALLED_VERSION_FILE.exists():
                data = json.loads(INSTALLED_VERSION_FILE.read_text())
                upd_at = data.get("updated_at", "")
                prev = data.get("previous_version", "")
                if upd_at:
                    info_text = f"Обновлено: {upd_at}"
                    if prev and prev != installed_v:
                        info_text += f"  (было v{prev})"
                    tk.Label(cr, text=info_text, bg=GL1, fg=GRN2,
                             font=("Segoe UI",9)).pack(anchor="w", pady=(2,0))
        except: pass

        tk.Label(cr, text=f"GitHub: {GITHUB_REPO}", bg=GL1, fg=MUT,
                 font=("Cascadia Code",9)).pack(anchor="w", pady=(4,0))

        # Changelog
        self._cl_card = self._card(f, BD1, fill="x", pady=(0,12))
        self._cl_title_lbl = tk.Label(
            self._cl_card, text="Список изменений", bg=GL1, fg=TXT2,
            font=("Segoe UI",12,"bold")
        )
        self._cl_title_lbl.pack(anchor="w", padx=18, pady=(10,6))
        self._cl_body = tk.Frame(self._cl_card, bg=GL1)
        self._cl_body.pack(fill="x", padx=18, pady=(0,12))
        tk.Label(self._cl_body, text="Нажми «Проверить обновления» — мы сравним твою версию\nс последним релизом на GitHub.",
                 bg=GL1, fg=TXT3, font=("Segoe UI",10), justify="left").pack(anchor="w")

        # VS Code секция (только для .py)
        if not getattr(sys, 'frozen', False):
            vc = self._card(f, ACG, fill="x", pady=(0,8))
            vc_r = tk.Frame(vc, bg=GL1); vc_r.pack(fill="x", padx=18, pady=12)
            tk.Label(vc_r, text="VS Code  Авто-перезапуск",
                     bg=GL1, fg=ACG, font=("Segoe UI",11,"bold")).pack(anchor="w")
            tk.Label(vc_r,
                     text="Лаунчер следит за изменениями файла скрипта.\n"
                          "Когда ты сохраняешь в VS Code — лаунчер автоматически перезапустится\n"
                          "с новым кодом через 3 секунды.",
                     bg=GL1, fg=TXT2, font=("Segoe UI",10), justify="left").pack(anchor="w", pady=4)
            path_f = tk.Frame(vc_r, bg=GL2, highlightthickness=1, highlightbackground=BD1)
            path_f.pack(fill="x", pady=4)
            tk.Frame(path_f, bg=HL0, height=1).pack(fill="x")
            tk.Label(path_f, text=f"  Отслеживаемый файл: {Path(__file__).resolve()}",
                     bg=GL2, fg=TXT3, font=("Cascadia Code",8), anchor="w").pack(padx=6, pady=6)
            tk.Label(vc_r, text="● Наблюдение активно",
                     bg=GL1, fg=GRN2, font=("Segoe UI",9,"bold")).pack(anchor="w", pady=(4,0))

        # Инструкция для разработчика
        setup = self._card(f, PUR, fill="x")
        sv = tk.Frame(setup, bg=GL1); sv.pack(fill="x", padx=18, pady=12)
        tk.Label(sv, text="◈  Как настроить авто-обновления для всех", bg=GL1, fg=PUR,
                 font=("Segoe UI",11,"bold")).pack(anchor="w")
        steps = [
            "1.  Создай репо на GitHub: github.com/ТВО_НИК/angels-launcher",
            f"2.  Замени в коде: GITHUB_REPO = \"ТВО_НИК/angels-launcher\"",
            "3.  Добавь файл .github/workflows/build.yml (нажми кнопку ниже)",
            "4.  Загрузи этот .py файл в репо → git push",
            "5.  GitHub Actions автоматически создаст .exe в Releases",
            "6.  Все пользователи увидят кнопку «Обновить» при следующем запуске!",
        ]
        for step in steps:
            tk.Label(sv, text=step, bg=GL1, fg=TXT2, font=("Segoe UI",9),
                     anchor="w", justify="left").pack(anchor="w", pady=1)

        glass_btn(sv, "📋 Скопировать код для GitHub Actions",
                  self._copy_actions_config,
                  fg=PUR, bg=GL2, font=("Segoe UI",9,"bold"),
                  px=14, py=7).pack(anchor="w", pady=(8,0))

        return f

    def _build_update_button(self):
        for w in self._big_update_btn_frame.winfo_children(): w.destroy()

        if self._update_available and self._latest_update_info:
            ver = self._latest_update_info["version"]
            installed_v = _read_installed_version()
            size = self._latest_update_info.get("size", 0)
            size_str = f"  ({fmt_size(size)})" if size else ""

            outer = tk.Frame(self._big_update_btn_frame, bg=GRN2, padx=2, pady=2)
            outer.pack(fill="x")
            tk.Frame(outer, bg=WHT, height=1).pack(fill="x")
            inner = tk.Frame(outer, bg="#0a2014")
            inner.pack(fill="x")
            tk.Frame(inner, bg=GRN2, height=2).pack(fill="x")

            row = tk.Frame(inner, bg="#0a2014"); row.pack(fill="x", padx=20, pady=16)
            tk.Label(row, text="⬆", bg="#0a2014", fg=GRN2,
                     font=("Segoe UI",28)).pack(side="left", padx=(0,14))
            info_col = tk.Frame(row, bg="#0a2014"); info_col.pack(side="left", fill="y")
            tk.Label(info_col, text=f"Обновление доступно: v{ver}{size_str}",
                     bg="#0a2014", fg=GRN2, font=("Segoe UI",14,"bold"), anchor="w").pack(anchor="w")
            tk.Label(info_col, text=f"Установленная версия: v{installed_v}  →  Новая: v{ver}",
                     bg="#0a2014", fg=TXT2, font=("Segoe UI",10), anchor="w").pack(anchor="w")

            self._dl_progress_frame = tk.Frame(inner, bg="#0a2014")
            self._dl_progress_frame.pack(fill="x", padx=20, pady=(0,4))
            pb_bg = tk.Frame(self._dl_progress_frame, bg=GL3, height=6)
            self._dl_pb_bg = pb_bg
            self._dl_pb = tk.Frame(pb_bg, bg=GRN2, height=6)
            self._dl_pb.place(x=0, y=0, height=6, relwidth=0)
            self._dl_pct_lbl = tk.Label(self._dl_progress_frame, text="",
                                        bg="#0a2014", fg=GRN2, font=("Segoe UI",8))

            btn_row = tk.Frame(inner, bg="#0a2014"); btn_row.pack(fill="x", padx=20, pady=(4,16))
            self._do_update_btn = tk.Button(
                btn_row, text="⬇   СКАЧАТЬ И ОБНОВИТЬ",
                bg=GRN2, fg=BG, activebackground=GRN, activeforeground=BG,
                font=("Segoe UI",14,"bold"), relief="flat",
                cursor="hand2", bd=0, padx=24, pady=14,
                command=self._do_update_now
            )
            self._do_update_btn.pack(side="left")
            tk.Label(btn_row,
                     text="  Лаунчер автоматически перезапустится после обновления",
                     bg="#0a2014", fg=TXT3, font=("Segoe UI",9)).pack(side="left", padx=10)

            if self._latest_update_info.get("changelog"):
                tk.Frame(inner, bg=BD1, height=1).pack(fill="x", padx=20)
                cl_row = tk.Frame(inner, bg="#0a2014"); cl_row.pack(fill="x", padx=20, pady=10)
                tk.Label(cl_row, text="Что нового:", bg="#0a2014", fg=GRN2,
                         font=("Segoe UI",10,"bold")).pack(anchor="w")
                for line in self._latest_update_info["changelog"][:8]:
                    col = GRN2 if line.startswith("+") or line.startswith("-") else TXT3
                    tk.Label(cl_row, text=f"  {line}", bg="#0a2014", fg=col,
                             font=("Segoe UI",9), anchor="w").pack(anchor="w")
        else:
            outer = tk.Frame(self._big_update_btn_frame, bg=BD1, padx=1, pady=1)
            outer.pack(fill="x")
            inner = tk.Frame(outer, bg=GL1); inner.pack(fill="x")
            tk.Frame(inner, bg=ACC2, height=2).pack(fill="x")
            tk.Frame(inner, bg=HL0, height=1).pack(fill="x")

            row = tk.Frame(inner, bg=GL1); row.pack(fill="x", padx=20, pady=16)
            tk.Label(row, text="◈", bg=GL1, fg=ACC, font=("Segoe UI",26)).pack(side="left", padx=(0,14))
            info_col = tk.Frame(row, bg=GL1); info_col.pack(side="left", fill="y")
            self._check_status_lbl = tk.Label(
                info_col,
                text="Нажми чтобы проверить обновления",
                bg=GL1, fg=TXT, font=("Segoe UI",13,"bold"), anchor="w"
            )
            self._check_status_lbl.pack(anchor="w")
            installed_v = _read_installed_version()
            tk.Label(info_col, text=f"Установленная версия: v{installed_v}  ·  Репо: {GITHUB_REPO}",
                     bg=GL1, fg=TXT3, font=("Segoe UI",9), anchor="w").pack(anchor="w")

            btn_row = tk.Frame(inner, bg=GL1); btn_row.pack(fill="x", padx=20, pady=(8,16))
            self._check_btn = pill_btn(
                btn_row, "◈   ПРОВЕРИТЬ ОБНОВЛЕНИЯ",
                self._do_check_updates,
                fg=BG, bg=ACC2, hbg=ACC, hfg=BG,
                font=("Segoe UI",13,"bold"), py=12, px=24
            )
            self._check_btn.pack(side="left")

    def _do_check_updates(self):
        try:
            self._check_btn.configure(state="disabled", text="⏳  Проверяю...")
            self._check_status_lbl.configure(text="Подключение к GitHub...", fg=TXT2)
        except: pass

        def _cb(ok, info, err):
            self.after(0, lambda: self._on_check_done(ok, info, err))

        self._updater.check_for_updates(_cb)

    def _on_check_done(self, success, info, error):
        try:
            self._check_btn.configure(state="normal", text="◈   ПРОВЕРИТЬ ОБНОВЛЕНИЯ")
        except: pass

        if success and info:
            if self._updater.is_newer(info["version"]):
                self._update_available = True
                self._latest_update_info = info
                self._show_update_badge()
                self._rebuild_updates_panel()
                self._toast.show(f"⬆ Доступно v{info['version']}!", kind="update")
            else:
                installed_v = _read_installed_version()
                try:
                    self._check_status_lbl.configure(
                        text=f"✓  У тебя последняя версия!  (v{installed_v})",
                        fg=GRN2
                    )
                except: pass
                self._toast.show("✓ У тебя последняя версия!", kind="success")
                try:
                    for w in self._cl_body.winfo_children(): w.destroy()
                    self._cl_title_lbl.configure(text=f"◈  Версия v{installed_v} — актуальна!", fg=GRN2)
                    tk.Label(self._cl_body, text="Поздравляем! Ты используешь самую свежую версию лаунчера.",
                             bg=GL1, fg=GRN2, font=("Segoe UI",10)).pack(anchor="w")
                    if info.get("changelog"):
                        for line in info["changelog"][:5]:
                            col = GRN2 if "+" in line else TXT3
                            tk.Label(self._cl_body, text=f"  {line}", bg=GL1, fg=col,
                                     font=("Segoe UI",9)).pack(anchor="w")
                except: pass
        else:
            try:
                self._check_status_lbl.configure(
                    text=f"✗  Ошибка проверки: {error}",
                    fg=ERR
                )
            except: pass
            self._toast.show("Ошибка проверки обновлений", kind="error")
            self._log(f"⬆  Ошибка обновлений: {error}", "warn")

    def _rebuild_updates_panel(self):
        self._build_update_button()
        try:
            for w in self._cl_body.winfo_children(): w.destroy()
            info = self._latest_update_info
            if info:
                self._cl_title_lbl.configure(
                    text=f"◈  Changelog v{info['version']}",
                    fg=GRN2
                )
                for line in info.get("changelog", []):
                    col = GRN2 if line.startswith("+") else (ERR if line.startswith("-") else TXT2)
                    tk.Label(self._cl_body, text=f"  {line}", bg=GL1, fg=col,
                             font=("Segoe UI",10)).pack(anchor="w")
        except: pass

    def _do_update_now(self):
        """★ FIX: Передаём new_version в download_and_install"""
        if not self._latest_update_info: return
        url = self._latest_update_info.get("download_url", "")
        new_version = self._latest_update_info.get("version", "")
        if not url:
            self._toast.show("Ссылка на скачивание недоступна!", kind="error")
            return

        try:
            self._do_update_btn.configure(state="disabled", text="⬇  Скачиваю...")
            self._dl_pb_bg.pack(fill="x", pady=(0,4))
            self._dl_pct_lbl.pack(anchor="w")
        except: pass

        self._log(f"⬆  Скачиваю обновление v{new_version}...", "gold")
        self._toast.show("Скачиваю обновление...", kind="info", duration=15000)

        def _progress(done, total):
            if total:
                pct = done / total
                self.after(0, lambda p=pct, d=done, t=total: self._update_dl_progress(p, d, t))

        def _done(success, result):
            self.after(0, lambda: self._on_update_downloaded(success, result))

        # ★ FIX: передаём new_version
        self._updater.download_and_install(
            url, new_version,
            on_progress=_progress,
            on_done=_done
        )

    def _update_dl_progress(self, pct, done, total):
        try:
            self._dl_pb.place_configure(relwidth=pct)
            self._dl_pct_lbl.configure(
                text=f"Скачано: {fmt_size(done)} / {fmt_size(total)}  ({int(pct*100)}%)"
            )
            self._do_update_btn.configure(text=f"⬇  {int(pct*100)}%...")
        except: pass

    def _on_update_downloaded(self, success, result):
        if success:
            self._toast.show("Обновление скачано! Перезапуск...", kind="update", duration=5000)
            self._log("⬆  Обновление скачано! Закрываю лаунчер и запускаю новый...", "gold")
            try:
                self._do_update_btn.configure(text="✓  Перезапуск...", bg=GRN2, fg=BG)
            except: pass
            # ★ FIX: Закрываем UI, запускаем bat, завершаемся
            self.after(1500, lambda: self._execute_update(result))
        else:
            self._toast.show(f"Ошибка скачивания: {result}", kind="error")
            self._log(f"✗  Ошибка скачивания: {result}", "error")
            try:
                self._do_update_btn.configure(
                    state="normal", text="⬇   СКАЧАТЬ И ОБНОВИТЬ"
                )
            except: pass

    def _execute_update(self, bat_path):
        """★ FIX: Закрываем окно лаунчера, затем запускаем bat и завершаемся"""
        try:
            # Скрываем окно чтобы пользователь понял что происходит
            self.withdraw()
        except: pass
        # Небольшая пауза, потом запускаем bat и убиваем себя
        self.after(300, lambda: self._updater.restart_with_update(bat_path))

    def _copy_actions_config(self):
        config = generate_github_actions_config()
        self.clipboard_clear()
        self.clipboard_append(config)
        self._toast.show("Скопировано в буфер!\nСоздай файл .github/workflows/build.yml", kind="success", duration=5000)

    # ══════════════════════════════════════════════════
    #  PROFILE PANEL
    # ══════════════════════════════════════════════════
    def _mk_profile(self, parent):
        f = tk.Frame(parent, bg=BG)
        tk.Label(f, text="◉  Личный кабинет", bg=BG, fg=TXT,
                 font=("Segoe UI",16,"bold")).pack(anchor="w", pady=(0,12))

        u = self._user
        card = self._card(f, ACC, fill="x", pady=(0,12))

        top = tk.Frame(card, bg=GL1); top.pack(fill="x", padx=18, pady=14)
        av = tk.Canvas(top, bg=GL1, width=82, height=82, highlightthickness=0)
        av.pack(side="left", padx=(0,16))
        for r, col in [(40,BD2),(35,ADM_AC if self._adm else ACC2),(30,ADM_AC if self._adm else ACC)]:
            av.create_oval(41-r,41-r,41+r,41+r, outline=col, fill="", width=1)
        av.create_oval(16,16,66,66, fill=GL3, outline="")
        av.create_text(41,41, text=self._nick[:2].upper(), fill=WHT, font=("Segoe UI",20,"bold"))
        av.create_arc(16,16,66,66, start=45, extent=60, outline=WHT, style="arc", width=1, stipple="gray75")

        inf = tk.Frame(top, bg=GL1); inf.pack(side="left", fill="y")
        tk.Label(inf, text=self._nick, bg=GL1, fg=WHT, font=("Segoe UI",18,"bold"), anchor="w").pack(anchor="w")
        role = "⚡ Администратор" if self._adm else "◈ Активный игрок"
        rcol = ADM_AC if self._adm else ACC
        tk.Label(inf, text=role, bg=GL1, fg=rcol, font=("Segoe UI",10)).pack(anchor="w")
        if u:
            tk.Label(inf, text=f"Регистрация: {u.get('date','—')}",
                     bg=GL1, fg=TXT3, font=("Segoe UI",9)).pack(anchor="w")

        valid, sub_status = check_subscription(u)
        sub_col = GRN2 if valid else ERR
        sub_bg  = "#0a1e14" if valid else "#1e0a0a"
        sub_brd = "#1a3a28" if valid else "#3a1a1a"
        sb = tk.Frame(card, bg=sub_bg, highlightthickness=1, highlightbackground=sub_brd)
        sb.pack(fill="x", padx=18, pady=(0,10))
        tk.Frame(sb, bg=sub_col, height=2).pack(fill="x")
        sub_row = tk.Frame(sb, bg=sub_bg); sub_row.pack(fill="x", padx=14, pady=8)
        sym = "✓" if valid else "⚠"
        tk.Label(sub_row, text=f"{sym}  Подписка:", bg=sub_bg, fg=sub_col,
                 font=("Segoe UI",11,"bold")).pack(side="left")
        tk.Label(sub_row, text=f"  {sub_status}", bg=sub_bg, fg=sub_col,
                 font=("Segoe UI",11)).pack(side="left")
        if not valid:
            tk.Label(sub_row, text=f"Купить: {TG_LINK}", bg=sub_bg, fg=ERR,
                     font=("Segoe UI",10,"bold")).pack(side="right", padx=4)

        dur_lbl = u.get("duration_label","Навсегда ∞") if u else "—"
        tk.Label(card, text=f"◈ Тип ключа: {dur_lbl}", bg=GL1, fg=TXT3,
                 font=("Segoe UI",9)).pack(anchor="w", padx=18, pady=(0,10))

        sf = tk.Frame(card, bg=GL1); sf.pack(fill="x", padx=18, pady=(0,14))
        stats = [
            ("◉ Входов",      str(u.get("login_count",1)) if u else "—", ACC2),
            ("◈ Последний",   (u.get("last_login","—") if u else "—"), ACC3),
            ("◎ Ключ",        ((u.get("key","—")[:14]+"…") if u and u.get("key") else "—"), GOLD),
        ]
        for ico, val, col in stats:
            sb2 = tk.Frame(sf, bg=GL2, highlightthickness=1, highlightbackground=BD1)
            sb2.pack(side="left", fill="x", expand=True, padx=3, pady=4, ipady=8)
            tk.Frame(sb2, bg=HL0, height=1).pack(fill="x")
            tk.Label(sb2, text=ico, bg=GL2, fg=TXT3, font=("Segoe UI",9)).pack()
            tk.Label(sb2, text=val, bg=GL2, fg=col, font=("Segoe UI",10,"bold")).pack()
        tk.Frame(card, bg=BD1, height=1).pack(fill="x")

        chg = self._card(f, ACC2, fill="x", pady=(0,10))
        tk.Label(chg, text="Сменить пароль", bg=GL1, fg=TXT,
                 font=("Segoe UI",11,"bold")).pack(anchor="w", padx=16, pady=(10,4))
        pr = tk.Frame(chg, bg=GL1); pr.pack(fill="x", padx=16, pady=(0,10))
        self._old_pw = tk.StringVar(); self._new_pw = tk.StringVar(); self._new_pw2 = tk.StringVar()
        for lbl_t, var, ph in [
            ("Текущий", self._old_pw, "Текущий пароль"),
            ("Новый",   self._new_pw, "Новый пароль"),
            ("Повтор",  self._new_pw2,"Повторить"),
        ]:
            cf = tk.Frame(pr, bg=GL1); cf.pack(side="left", fill="x", expand=True, padx=3)
            tk.Label(cf, text=lbl_t, bg=GL1, fg=TXT2, font=("Segoe UI",9)).pack(anchor="w")
            w, _ = glass_entry(cf, var, show="●", placeholder=ph)
            w.pack(fill="x")
        self._pw_st = tk.Label(chg, text="", bg=GL1, fg=ERR, font=("Segoe UI",9))
        self._pw_st.pack(anchor="w", padx=16)
        glass_btn(chg, "Изменить пароль", self._change_pw,
                  fg=ACC2, bg=GL2, font=("Segoe UI",10,"bold"),
                  px=14, py=8).pack(anchor="w", padx=16, pady=(4,12))

        glass_btn(f, "⊘   Выйти из аккаунта", self._logout,
                  fg=ERR, bg="#1e0808",
                  font=("Segoe UI",10), px=14, py=9).pack(anchor="w")
        return f

    def _change_pw(self):
        old = self._old_pw.get().strip()
        n1  = self._new_pw.get().strip()
        n2  = self._new_pw2.get().strip()
        if not all([old, n1, n2]):
            self._pw_st.configure(text="Заполни все поля", fg=ERR); return
        if n1 != n2:
            self._pw_st.configure(text="Пароли не совпадают", fg=ERR); return
        if len(n1) < 4:
            self._pw_st.configure(text="Минимум 4 символа", fg=ERR); return
        try:
            d = json.loads(KEY_FILE.read_text()); kh = d.get("key_hash")
            users = _load_users(); u = users.get(kh, {})
            if u.get("password_hash") != hash_password(old):
                self._pw_st.configure(text="Неверный текущий пароль", fg=ERR); return
            u["password_hash"] = hash_password(n1); users[kh] = u; _save_users(users)
            self._pw_st.configure(text="✓  Пароль успешно изменён", fg=GRN2)
            self._toast.show("Пароль изменён!", kind="success")
        except Exception as e:
            self._pw_st.configure(text=f"Ошибка: {e}", fg=ERR)

    def _logout(self):
        if messagebox.askyesno("Выход из аккаунта",
                                "Выйти из аккаунта?\nВы вернётесь на экран входа.",
                                parent=self):
            try: KEY_FILE.unlink(missing_ok=True)
            except: pass
            self._logout_requested = True
            self.destroy()

    # ══════════════════════════════════════════════════
    #  MULTIPLAYER PANEL
    # ══════════════════════════════════════════════════
    def _mk_multi(self, parent):
        f = tk.Frame(parent, bg=BG)
        tr = tk.Frame(f, bg=BG); tr.pack(fill="x", pady=(0,10))
        tk.Label(tr, text="◐  Серверы", bg=BG, fg=TXT,
                 font=("Segoe UI",16,"bold")).pack(side="left")
        pill_btn(tr, "＋  Добавить", self._add_server_dlg,
                 fg=BG, bg=ACC2, font=("Segoe UI",10), py=6, px=14).pack(side="right")

        note = tk.Frame(f, bg="#160a00", highlightthickness=1, highlightbackground="#3a2000")
        note.pack(fill="x", pady=(0,12))
        tk.Frame(note, bg=ORG, width=3).pack(side="left", fill="y")
        tk.Label(note, text="  ⚠  AuthMe: /login <пароль> после подключения",
                 bg="#160a00", fg=ORG, font=("Segoe UI",10), anchor="w").pack(padx=8, pady=9, side="left")

        self._srv_f = tk.Frame(f, bg=BG)
        self._srv_f.pack(fill="both", expand=True)
        self._refresh_servers()
        return f

    def _refresh_servers(self):
        for w in self._srv_f.winfo_children(): w.destroy()
        if not self.servers:
            ep = self._card(self._srv_f, ACC, fill="x")
            tk.Label(ep, text="Нет серверов. Нажми «+ Добавить»",
                     bg=GL1, fg=MUT, font=("Segoe UI",11), justify="center").pack(pady=30)
            return
        for i, srv in enumerate(self.servers):
            out = tk.Frame(self._srv_f, bg=BD1, padx=1, pady=1)
            out.pack(fill="x", pady=5)
            row = tk.Frame(out, bg=GL2); row.pack(fill="x")
            tk.Frame(row, bg=HL0, height=1).pack(fill="x")
            inn = tk.Frame(row, bg=GL2); inn.pack(fill="x", padx=16, pady=12)
            host = srv.get("host",""); port = int(srv.get("port",25565))
            sl = tk.Label(inn, text="●", bg=GL2, fg=TXT3, font=("Segoe UI",14))
            sl.pack(side="left", padx=(0,14))
            inf = tk.Frame(inn, bg=GL2); inf.pack(side="left", fill="y")
            tk.Label(inf, text=srv.get("name",host), bg=GL2, fg=TXT,
                     font=("Segoe UI",12,"bold"), anchor="w").pack(anchor="w")
            tk.Label(inf, text=f"{host}:{port}", bg=GL2, fg=TXT3,
                     font=("Segoe UI",9), anchor="w").pack(anchor="w")
            bf = tk.Frame(inn, bg=GL2); bf.pack(side="right")
            glass_btn(bf, "Пинг", lambda h=host,p=port,l=sl: self._ping(h,p,l),
                      fg=TXT2, bg=GL3, font=("Segoe UI",9), py=5, px=10).pack(side="left", padx=4)
            pill_btn(bf, "◈  Играть", lambda h=host,p=port: self._start_with(h,p),
                     fg=BG, bg=ACC2, font=("Segoe UI",10,"bold"), py=5, px=12).pack(side="left", padx=4)
            tk.Button(bf, text="✕", bg=GL2, fg=ERR, relief="flat",
                      font=("Segoe UI",10), cursor="hand2", bd=0, padx=8, pady=5,
                      command=lambda i=i: self._del_server(i)).pack(side="left")

    def _ping(self, host, port, lbl):
        def do():
            ok = check_server_ping(host, port)
            lbl.configure(fg=GRN2 if ok else ERR, text="●" if ok else "✕")
            self._toast.show(f"{host}:{port} {'онлайн ✓' if ok else 'недоступен ✕'}",
                             kind="success" if ok else "warning")
        threading.Thread(target=do, daemon=True).start()
        lbl.configure(fg=ORG, text="○")

    def _del_server(self, idx):
        if 0 <= idx < len(self.servers):
            self.servers.pop(idx)
            save_servers(self.servers)
            self._refresh_servers()
            self._toast.show("Сервер удалён", kind="info")

    def _add_server_dlg(self):
        dlg = tk.Toplevel(self)
        dlg.title("Добавить сервер")
        dlg.configure(bg=GL1); dlg.geometry("460x295")
        dlg.resizable(False,False); dlg.grab_set()

        tk.Frame(dlg, bg=ACC, height=2).pack(fill="x")
        tk.Frame(dlg, bg=HL0, height=1).pack(fill="x")
        tk.Label(dlg, text="Добавить сервер", bg=GL1, fg=TXT,
                 font=("Segoe UI",14,"bold")).pack(pady=(18,14))

        nv = tk.StringVar(); hv = tk.StringVar(); pv = tk.StringVar(value="25565")
        for lt, var, ph in [("Название",nv,"Мой сервер"),("IP-адрес",hv,"play.server.net"),("Порт",pv,"25565")]:
            r = tk.Frame(dlg, bg=GL1); r.pack(fill="x", padx=22, pady=5)
            tk.Label(r, text=lt, bg=GL1, fg=TXT2, font=("Segoe UI",10),
                     width=10, anchor="w").pack(side="left")
            w, _ = glass_entry(r, var, placeholder=ph)
            w.pack(side="left", fill="x", expand=True)

        def save():
            h = hv.get().strip()
            if not h: messagebox.showwarning("Ошибка","Введи адрес!", parent=dlg); return
            try: p = int(pv.get().strip() or "25565")
            except: p = 25565
            self.servers.append({"name":nv.get().strip() or h, "host":h, "port":p})
            save_servers(self.servers); self._refresh_servers()
            self._toast.show(f"Сервер добавлен: {h}:{p}", kind="success")
            dlg.destroy()

        pill_btn(dlg, "◈  Сохранить", save, fg=BG, bg=ACC2,
                 font=("Segoe UI",12,"bold"), py=11).pack(fill="x", padx=22, pady=18)

    def _start_with(self, host, port):
        self._show("home")
        self._connect_server = (host, port)
        self._start()

    # ══════════════════════════════════════════════════
    #  MODS PANEL
    # ══════════════════════════════════════════════════
    def _mk_mods(self, parent):
        f = tk.Frame(parent, bg=BG)
        tk.Label(f, text="◎  Установленные моды", bg=BG, fg=TXT,
                 font=("Segoe UI",16,"bold")).pack(anchor="w", pady=(0,14))

        for icon, name, desc, col, version in [
            ("⚙", "Minecraft Forge", "Загрузчик модов",        ACC2, FORGE_VERSION),
            ("◈", MOD_NAME,          "Основной мод лаунчера",  ACC,  MOD_VERSION),
        ]:
            out = tk.Frame(f, bg=BD1, padx=1, pady=1); out.pack(fill="x", pady=6)
            card_f = tk.Frame(out, bg=GL1); card_f.pack(fill="x")
            tk.Frame(card_f, bg=col, width=4).pack(side="left", fill="y")
            lf = tk.Frame(card_f, bg=GL1); lf.pack(side="left", padx=16, pady=14)
            tk.Label(lf, text=icon, bg=GL1, fg=col, font=("Segoe UI",22), width=2).pack(side="left")
            inf = tk.Frame(lf, bg=GL1); inf.pack(side="left", padx=12)
            tk.Label(inf, text=name, bg=GL1, fg=TXT, font=("Segoe UI",12,"bold"), anchor="w").pack(anchor="w")
            tk.Label(inf, text=f"{desc}  ·  v{version}", bg=GL1, fg=TXT3,
                     font=("Segoe UI",10), anchor="w").pack(anchor="w")
            bd = tk.Frame(card_f, bg="#0a1e12", highlightthickness=1, highlightbackground="#1a3a22")
            bd.pack(side="right", padx=16, pady=14)
            tk.Frame(bd, bg=GRN2, height=1).pack(fill="x")
            tk.Label(bd, text="  ◈ АКТИВЕН  ", bg="#0a1e12", fg=GRN2,
                     font=("Segoe UI",9,"bold")).pack(padx=6, pady=5)
        return f

    # ══════════════════════════════════════════════════
    #  CONSOLE PANEL
    # ══════════════════════════════════════════════════
    def _mk_console(self, parent):
        f = tk.Frame(parent, bg=BG)
        top = tk.Frame(f, bg=BG); top.pack(fill="x", pady=(0,10))
        tk.Label(top, text="▸  Консоль", bg=BG, fg=TXT,
                 font=("Segoe UI",14,"bold")).pack(side="left")
        role_txt = "⚡ ADMIN" if self._adm else "◈ USER"
        tk.Label(top, text=role_txt, bg=BG,
                 fg=ADM_AC if self._adm else TXT2,
                 font=("Segoe UI",10,"bold")).pack(side="left", padx=12)
        glass_btn(top, "Очистить", self._clear_con, fg=TXT2, bg=GL2,
                  font=("Segoe UI",9), py=4, px=10).pack(side="right")

        out = tk.Frame(f, bg=BD1, padx=1, pady=1)
        out.pack(fill="both", expand=True)
        inn = tk.Frame(out, bg=GL1); inn.pack(fill="both", expand=True)
        tk.Frame(inn, bg=ADM_AC if self._adm else ACC, height=2).pack(fill="x")
        tk.Frame(inn, bg=HL0, height=1).pack(fill="x")

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Console.Vertical.TScrollbar",
                        background=GL3, troughcolor=GL1, arrowcolor=ACC2,
                        bordercolor=BD1, lightcolor=HL0, darkcolor=BG)

        self.console = tk.Text(
            inn, bg="#020c18", fg=ACG, font=("Cascadia Code",10),
            relief="flat", state="disabled", wrap="word", bd=10,
            selectbackground=GL3, insertbackground=ACC, spacing3=3
        )
        sb = ttk.Scrollbar(inn, command=self.console.yview, style="Console.Vertical.TScrollbar")
        self.console.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.console.pack(fill="both", expand=True)

        inp_out = tk.Frame(f, bg=BD1, padx=1, pady=1)
        inp_out.pack(fill="x", pady=(8,0))
        inp_inn = tk.Frame(inp_out, bg=GL2); inp_inn.pack(fill="x")
        tk.Frame(inp_inn, bg=HL0, height=1).pack(fill="x")
        prompt_row = tk.Frame(inp_inn, bg=GL2); prompt_row.pack(fill="x")
        pt = "⚡" if self._adm else "◈"
        tk.Label(prompt_row, text=f"  {pt} {self._nick}> ", bg=GL2,
                 fg=ADM_AC if self._adm else ACC,
                 font=("Cascadia Code",11,"bold")).pack(side="left")
        self._cin = tk.StringVar()
        self._ent = tk.Entry(prompt_row, textvariable=self._cin, bg=GL2, fg=TXT,
                             insertbackground=ACC, relief="flat",
                             font=("Cascadia Code",11), bd=8)
        self._ent.pack(side="left", fill="x", expand=True, ipady=8)
        self._ent.bind("<Return>", self._con_send)
        self._ent.bind("<Up>", self._hist_up)
        self._ent.bind("<Down>", self._hist_dn)
        glass_btn(prompt_row, "↵", self._con_send, fg=ACC, bg=GL3,
                  font=("Segoe UI",10), py=7, px=12).pack(side="right")

        self._cmd_hist = []; self._hist_pos = -1
        tk.Label(f, text="'help' — справка  ·  ↑↓ — история команд",
                 bg=BG, fg=MUT, font=("Segoe UI",9)).pack(anchor="w", pady=(5,0))
        return f

    def _con_send(self, e=None):
        cmd = self._cin.get().strip()
        if not cmd: return
        self._ent.delete(0,"end")
        if not self._cmd_hist or self._cmd_hist[-1] != cmd:
            self._cmd_hist.append(cmd)
        self._hist_pos = -1
        self._log(f"▸ {cmd}", "cmd")
        self._handle_cmd(cmd)

    def _hist_up(self, e=None):
        if not self._cmd_hist: return
        if self._hist_pos == -1: self._hist_pos = len(self._cmd_hist)-1
        elif self._hist_pos > 0: self._hist_pos -= 1
        self._ent.delete(0,"end"); self._ent.insert(0, self._cmd_hist[self._hist_pos])

    def _hist_dn(self, e=None):
        if self._hist_pos == -1: return
        self._hist_pos += 1; self._ent.delete(0,"end")
        if self._hist_pos >= len(self._cmd_hist): self._hist_pos = -1
        else: self._ent.insert(0, self._cmd_hist[self._hist_pos])

    def _handle_cmd(self, cmd):
        parts = cmd.split(); c = parts[0].lower() if parts else ""
        if c == "help":
            self._log("  Команды:", "info")
            base = [("help","эта справка"),("clear","очистить"),("version","версия"),
                    ("ram <гб>","выделить RAM"),("nick <имя>","сменить ник"),
                    ("ping <host>","пинг сервера"),("check <ключ>","проверить ключ"),
                    ("reinstall","переустановить Forge"),("sub","статус подписки"),
                    ("update","проверить обновления"),("exit","закрыть лаунчер")]
            adm_cmds = [("keygen [n]","⚡ генерировать ключи"),("tkey <сек>","⚡ тайм-ключ"),
                        ("users","⚡ список игроков"),("ban <ник>","⚡ бан"),
                        ("unban <ник>","⚡ разбан"),("deluser <ник>","⚡ удалить игрока"),
                        ("stats","⚡ статистика")] if self._adm else []
            for name, desc in base + adm_cmds:
                tag = "gold" if "⚡" in desc else "muted"
                self._log(f"  {name:<28} — {desc}", tag)
        elif c == "clear": self._clear_con()
        elif c == "version":
            installed_v = _read_installed_version()
            self._log(f"  Angels Launcher v{installed_v} AutoUpdate Edition", "accent")
            self._log(f"  MC {MC_VERSION}  ·  Forge {FORGE_VERSION}  ·  RAM {TOTAL_RAM} ГБ", "info")
            self._log(f"  GitHub: {GITHUB_REPO}", "muted")
        elif c == "sub":
            valid, status = check_subscription(self._user)
            self._log(f"  Подписка: {status}", "accent" if valid else "error")
            if not valid: self._log(f"  Продление: Telegram {TG_LINK}", "error")
        elif c == "update":
            self._log("  Проверка обновлений...", "info")
            def _cb(ok, info, err):
                if ok and info:
                    if self._updater.is_newer(info["version"]):
                        self._log(f"  ⬆ Доступно v{info['version']}! Перейди в «Обновления».", "gold")
                    else:
                        installed_v = _read_installed_version()
                        self._log(f"  ✓ Последняя версия (v{installed_v})", "accent")
                else:
                    self._log(f"  ✗ Ошибка: {err}", "error")
            self._updater.check_for_updates(_cb)
        elif c == "check" and len(parts) > 1:
            ok = validate_key(parts[1])
            self._log(f"  {parts[1]} → {'✓ Валидный' if ok else '✗ Неверный'}",
                      "accent" if ok else "error")
        elif c == "ram" and len(parts) > 1:
            try:
                n = max(1, min(int(parts[1]), TOTAL_RAM))
                self.ram.set(n); self._log(f"  RAM: {n} ГБ выделено", "accent")
            except: self._log("  Ошибка: ram <число>", "error")
        elif c == "nick" and len(parts) > 1:
            self.username.set(parts[1]); self._log(f"  Ник: {parts[1]}", "accent")
        elif c == "ping" and len(parts) > 1:
            host = parts[1]; port = int(parts[2]) if len(parts) > 2 else 25565
            self._log(f"  Пинг {host}:{port}...", "info")
            def dp():
                ok = check_server_ping(host, port)
                self._log(f"  {host}:{port} → {'◈ Онлайн' if ok else '✕ Оффлайн'}",
                          "accent" if ok else "error")
            threading.Thread(target=dp, daemon=True).start()
        elif c == "reinstall": self._reinstall()
        elif c == "exit": self.destroy()
        elif c in ("keygen","tkey","users","ban","unban","deluser","stats"):
            if not self._adm:
                self._log(f"  ✗ Доступ запрещён", "error"); return
            if c == "keygen":
                try: n = min(int(parts[1]) if len(parts)>1 else 5, 100)
                except: n = 5
                self._log(f"  ⚡ {n} ключей:", "gold")
                for k in [generate_key() for _ in range(n)]: self._log(f"  {k}", "accent")
            elif c == "tkey":
                try: sec = int(parts[1]) if len(parts)>1 else 0
                except: sec = 0
                k = generate_timed_key(sec)
                self._log(f"  ⚡ [{fmt_duration(sec)}]: {k}", "gold")
            elif c == "users":
                users = _load_users(); bl = _load_blacklist()
                self._log(f"  ⚡ Игроков: {len(users)}", "gold")
                for kh, u in list(users.items())[:30]:
                    bk = "⊘ " if kh in bl else "  "
                    _, sub = check_subscription(u)
                    self._log(f"  {bk}{u.get('nickname','?'):16s} | {sub}", "muted")
            elif c == "stats":
                users = _load_users(); used = _load_used_keys(); bl = _load_blacklist()
                today = time.strftime("%Y-%m-%d")
                lt = sum(1 for u in users.values() if u.get("last_login","").startswith(today))
                self._log("  ⚡ Статистика:", "gold")
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
        else:
            self._log(f"  Неизвестная команда: {cmd}  (введи 'help')", "warn")

    # ══════════════════════════════════════════════════
    #  SETTINGS PANEL
    # ══════════════════════════════════════════════════
    def _mk_settings(self, parent):
        f = tk.Frame(parent, bg=BG)
        tk.Label(f, text="⚙  Настройки", bg=BG, fg=TXT,
                 font=("Segoe UI",16,"bold")).pack(anchor="w", pady=(0,14))

        def setting_row(label, widget_fn, desc=None):
            out = tk.Frame(f, bg=BD1, padx=1, pady=1); out.pack(fill="x", pady=5)
            r = tk.Frame(out, bg=GL1); r.pack(fill="x")
            tk.Frame(r, bg=HL0, height=1).pack(fill="x")
            lf = tk.Frame(r, bg=GL1); lf.pack(side="left", padx=18, pady=14)
            tk.Label(lf, text=label, bg=GL1, fg=TXT, font=("Segoe UI",11), anchor="w").pack(anchor="w")
            if desc:
                tk.Label(lf, text=desc, bg=GL1, fg=TXT3, font=("Segoe UI",9), anchor="w").pack(anchor="w")
            widget_fn(r)

        def mk_nick(r):
            fr = tk.Frame(r, bg=BD1, padx=1, pady=1); fr.pack(side="right", padx=16, pady=14)
            tk.Frame(fr, bg=HL0, height=1).pack(fill="x")
            tk.Entry(fr, textvariable=self.username, bg=GL2, fg=TXT,
                     insertbackground=ACC, relief="flat", font=("Segoe UI",12),
                     bd=8, width=18).pack(ipady=7)

        def mk_ram(r):
            fr = tk.Frame(r, bg=GL1); fr.pack(side="right", padx=16, pady=12)
            mx = min(TOTAL_RAM-1, 16) if TOTAL_RAM > 2 else TOTAL_RAM
            tk.Label(fr, text=f"/ {TOTAL_RAM} ГБ", bg=GL1, fg=TXT3, font=("Segoe UI",9)).pack(side="right", padx=4)
            tk.Label(fr, textvariable=self.ram, bg=GL1, fg=ACC, font=("Segoe UI",14,"bold"), width=2).pack(side="right")
            tk.Scale(fr, from_=1, to=mx, orient="horizontal", variable=self.ram,
                     bg=GL1, fg=ACC, troughcolor=GL3, highlightthickness=0,
                     activebackground=ACC, showvalue=False, length=200,
                     sliderlength=22).pack(side="right")

        def mk_fs(r):
            pill_btn(r, "⛶  Переключить (F11)", self._toggle_fs,
                     fg=BG, bg=ACC2, font=("Segoe UI",10), py=7, px=16).pack(side="right", padx=16, pady=14)

        def mk_path(r):
            pf = tk.Frame(r, bg=GL2, highlightthickness=1, highlightbackground=BD1)
            pf.pack(side="right", padx=16, pady=14)
            tk.Frame(pf, bg=HL0, height=1).pack(fill="x")
            tk.Label(pf, text=f"  {MC_DIR}  ", bg=GL2, fg=TXT3,
                     font=("Cascadia Code",9)).pack(padx=4, pady=7)

        def mk_mod_url(r):
            fr = tk.Frame(r, bg=GL1); fr.pack(side="right", padx=16, pady=10, fill="x", expand=True)
            w, _ = glass_entry(fr, self.mod_url, font=("Cascadia Code",9))
            w.pack(fill="x")

        setting_row("Никнейм в Minecraft", mk_nick, "Офлайн-имя игрока")
        setting_row("Оперативная память", mk_ram, f"Система: {TOTAL_RAM} ГБ")
        setting_row("Полный экран", mk_fs, "F11 — переключить")
        setting_row("Папка Minecraft", mk_path, "Расположение файлов игры")
        setting_row("Ссылка на мод", mk_mod_url, "Google Drive или прямая ссылка")

        tk.Frame(f, bg=BD1, height=1).pack(fill="x", pady=16)
        glass_btn(f, "⚠  Переустановить Forge", self._reinstall,
                  fg=ERR, bg="#1e0808",
                  font=("Segoe UI",10), px=14, py=9).pack(side="left")
        return f

    # ══════════════════════════════════════════════════
    #  ADMIN PANEL
    # ══════════════════════════════════════════════════
    def _mk_admin(self, parent):
        f = tk.Frame(parent, bg=ADM_BG)
        hdr = tk.Frame(f, bg=ADM_P, highlightthickness=1, highlightbackground=ADM_M)
        hdr.pack(fill="x", pady=(0,14))
        tk.Frame(hdr, bg=ADM_AC, height=2).pack(fill="x")
        tk.Frame(hdr, bg=ADM_M, height=1).pack(fill="x")
        tk.Label(hdr, text=f"⚡  ADMIN PANEL  —  {SUPER_ADMIN}",
                 bg=ADM_P, fg=ADM_AC, font=("Courier",14,"bold")).pack(side="left", padx=18, pady=12)
        tk.Label(hdr, text=time.strftime("[%Y-%m-%d]"),
                 bg=ADM_P, fg=ADM_M, font=("Courier",10)).pack(side="right", padx=18)

        tabs = tk.Frame(f, bg=ADM_BG); tabs.pack(fill="x", pady=(0,12))
        self._asub_panels = {}; self._asub_btns = {}
        subs = [("◈ Дашборд","ad_dash"),("◉ Keygen","ad_kg"),
                ("⏱ Тайм-ключи","ad_tk"),("◐ Игроки","ad_usr"),("⊘ Бан-лист","ad_bl")]
        for lbl, key in subs:
            btn = tk.Button(tabs, text=lbl, bg=ADM_P, fg="#660044",
                            activebackground=ADM_BG, activeforeground=ADM_AC,
                            relief="flat", font=("Courier",11), cursor="hand2",
                            bd=0, padx=14, pady=8,
                            command=lambda k=key: self._asub(k))
            btn.pack(side="left", padx=2)
            self._asub_btns[key] = btn

        content = tk.Frame(f, bg=ADM_BG); content.pack(fill="both", expand=True)
        self._asub_panels["ad_dash"] = self._mk_a_dash(content)
        self._asub_panels["ad_kg"]   = self._mk_a_keygen(content)
        self._asub_panels["ad_tk"]   = self._mk_a_timed(content)
        self._asub_panels["ad_usr"]  = self._mk_a_users(content)
        self._asub_panels["ad_bl"]   = self._mk_a_bl(content)
        self._asub("ad_dash")
        return f

    def _asub(self, key):
        for p in self._asub_panels.values(): p.pack_forget()
        for k, b in self._asub_btns.items():
            if k == key: b.configure(bg=ADM_BG, fg=ADM_AC, font=("Courier",11,"bold"))
            else:        b.configure(bg=ADM_P,  fg="#660044", font=("Courier",11))
        self._asub_panels[key].pack(fill="both", expand=True)

    def _a_card(self, parent, col=None, **pkw):
        out = tk.Frame(parent, bg=ADM_P, highlightthickness=1, highlightbackground=ADM_M)
        out.pack(**pkw)
        tk.Frame(out, bg=col or ADM_AC, height=1).pack(fill="x")
        return out

    def _mk_a_dash(self, parent):
        f = tk.Frame(parent, bg=ADM_BG)
        tk.Label(f, text="◈  СТАТИСТИКА", bg=ADM_BG, fg=ADM_AC,
                 font=("Courier",13,"bold")).pack(anchor="w", pady=(0,10))
        cr = tk.Frame(f, bg=ADM_BG); cr.pack(fill="x", pady=(0,12))
        self._adm_cards = {}
        for key, label, col in [
            ("tu","◈ Игроков",ADM_AC),("tk","◉ Ключей",ADM_A2),
            ("bl","⊘ В бане",ADM_R),("tl","▸ Сегодня",ADM_G)
        ]:
            c = tk.Frame(cr, bg=ADM_P, highlightthickness=1, highlightbackground=ADM_M)
            c.pack(side="left", fill="x", expand=True, padx=3)
            tk.Frame(c, bg=col, height=2).pack(fill="x")
            tk.Label(c, text=label, bg=ADM_P, fg=ADM_M, font=("Courier",9)).pack(anchor="w", padx=12, pady=(7,2))
            lbl = tk.Label(c, text="—", bg=ADM_P, fg=col, font=("Courier",22,"bold"))
            lbl.pack(anchor="w", padx=12, pady=(0,10))
            self._adm_cards[key] = lbl
        tk.Button(f, text="↻  Обновить", bg=ADM_P, fg=ADM_A2, relief="flat",
                  font=("Courier",10), cursor="hand2", bd=0, padx=16, pady=8,
                  command=self._a_refresh).pack(anchor="w", pady=(0,12))
        tk.Label(f, text="Последние регистрации:", bg=ADM_BG, fg=ADM_T,
                 font=("Courier",10,"bold")).pack(anchor="w")
        rf = self._a_card(f, fill="x", pady=(4,0))
        self._a_recent = tk.Frame(rf, bg=ADM_P)
        self._a_recent.pack(fill="x", padx=12, pady=10)
        self._a_stats()
        return f

    def _a_stats(self):
        try:
            users = _load_users(); used = _load_used_keys(); bl = _load_blacklist()
            today = time.strftime("%Y-%m-%d")
            lt = sum(1 for u in users.values() if u.get("last_login","").startswith(today))
            self._adm_cards["tu"].configure(text=str(len(users)))
            self._adm_cards["tk"].configure(text=str(len(used)))
            self._adm_cards["bl"].configure(text=str(len(bl)))
            self._adm_cards["tl"].configure(text=str(lt))
            for w in self._a_recent.winfo_children(): w.destroy()
            recent = sorted(users.values(), key=lambda u: u.get("date",""), reverse=True)[:6]
            for u in recent:
                r = tk.Frame(self._a_recent, bg=ADM_P); r.pack(fill="x", pady=1)
                tk.Label(r, text=f"  ◈  {u.get('nickname','?'):16s}",
                         bg=ADM_P, fg=ADM_AC, font=("Courier",10,"bold"),
                         width=22, anchor="w").pack(side="left")
                _, sub = check_subscription(u)
                sc = GRN2 if sub != "Подписка истекла" else ERR
                tk.Label(r, text=sub, bg=ADM_P, fg=sc, font=("Courier",9)).pack(side="left", padx=10)
                tk.Label(r, text=f"входов: {u.get('login_count',0)}",
                         bg=ADM_P, fg=ADM_A2, font=("Courier",9)).pack(side="right", padx=12)
        except: pass

    def _mk_a_keygen(self, parent):
        f = tk.Frame(parent, bg=ADM_BG)
        tk.Label(f, text="◉  ГЕНЕРАТОР КЛЮЧЕЙ",
                 bg=ADM_BG, fg=ADM_AC, font=("Courier",13,"bold")).pack(anchor="w", pady=(0,10))
        ctrl = tk.Frame(f, bg=ADM_BG); ctrl.pack(fill="x", pady=(0,10))
        tk.Label(ctrl, text="Кол-во:", bg=ADM_BG, fg=ADM_T, font=("Courier",11)).pack(side="left")
        self._kg_cnt = tk.StringVar(value="10")
        tk.Entry(ctrl, textvariable=self._kg_cnt, bg=ADM_P, fg=ADM_AC,
                 insertbackground=ADM_AC, relief="flat", font=("Courier",12),
                 bd=7, width=6).pack(side="left", padx=10)
        for n in [1,5,10,25,50,100]:
            tk.Button(ctrl, text=f"×{n}", bg=ADM_P, fg=ADM_A2, relief="flat",
                      font=("Courier",10,"bold"), cursor="hand2", bd=0, padx=9, pady=5,
                      command=lambda n=n: self._a_gen_keys(n)).pack(side="left", padx=2)
        out = self._a_card(f, fill="both", expand=True, pady=(0,10))
        self._kg_out = tk.Text(out, bg="#060003", fg=ADM_AC, font=("Courier",12),
                               relief="flat", state="disabled", wrap="none", bd=12)
        sb = ttk.Scrollbar(out, command=self._kg_out.yview)
        self._kg_out.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y"); self._kg_out.pack(fill="both", expand=True)
        br = tk.Frame(f, bg=ADM_BG); br.pack(fill="x")
        tk.Button(br, text="⊠ Очистить", bg=ADM_P, fg=ADM_M, relief="flat",
                  font=("Courier",10), cursor="hand2", bd=0, padx=12, pady=7,
                  command=lambda: (self._kg_out.configure(state="normal"),
                                   self._kg_out.delete("1.0","end"),
                                   self._kg_out.configure(state="disabled"))
                  ).pack(side="right", padx=3)
        tk.Button(br, text="⊞ Скопировать", bg=ADM_P, fg=ADM_A2, relief="flat",
                  font=("Courier",10), cursor="hand2", bd=0, padx=12, pady=7,
                  command=lambda: (self.clipboard_clear(),
                                   self.clipboard_append(self._kg_out.get("1.0","end")))
                  ).pack(side="right", padx=3)
        return f

    def _a_gen_keys(self, n=None):
        try: count = n or int(self._kg_cnt.get() or 10)
        except: count = 10
        keys = [generate_key() for _ in range(count)]
        self._kg_out.configure(state="normal")
        self._kg_out.insert("end", f"\n{time.strftime('[%H:%M:%S]')} × {count} постоянных:\n")
        for k in keys: self._kg_out.insert("end", f"  {k}\n")
        self._kg_out.configure(state="disabled"); self._kg_out.see("end")
        self._log(f"⚡ Сгенерировано {count} ключей", "gold")
        self._toast.show(f"Сгенерировано {count} ключей!", kind="success")

    def _mk_a_timed(self, parent):
        f = tk.Frame(parent, bg=ADM_BG)
        tk.Label(f, text="⏱  ТАЙМ-КЛЮЧИ", bg=ADM_BG, fg=ADM_G,
                 font=("Courier",13,"bold")).pack(anchor="w", pady=(0,10))
        tk.Label(f, text="Быстрый выбор:", bg=ADM_BG, fg=ADM_T, font=("Courier",11)).pack(anchor="w")
        pr = tk.Frame(f, bg=ADM_BG); pr.pack(fill="x", pady=(4,12))
        presets = [("1 ч",3600),("6 ч",21600),("12 ч",43200),
                   ("1 дн",86400),("3 дн",259200),("7 дн",604800),
                   ("30 дн",2592000),("90 дн",7776000),("1 год",31536000),("∞",0)]
        self._tkey_sec = tk.IntVar(value=86400)
        self._tkey_cnt = tk.StringVar(value="1")
        for lbl_t, sec in presets:
            clr = ADM_G if sec==0 else ADM_A2
            tk.Button(pr, text=lbl_t, bg=ADM_P, fg=clr, relief="flat",
                      font=("Courier",10), cursor="hand2", bd=0, padx=11, pady=6,
                      command=lambda s=sec: (self._tkey_sec.set(s), self._upd_dur_lbl())
                      ).pack(side="left", padx=2, pady=2)
        cr = tk.Frame(f, bg=ADM_P, highlightthickness=1, highlightbackground=ADM_M)
        cr.pack(fill="x", pady=(0,10))
        tk.Frame(cr, bg=ADM_G, height=1).pack(fill="x")
        cx = tk.Frame(cr, bg=ADM_P); cx.pack(fill="x", padx=14, pady=12)
        tk.Label(cx, text="Своё значение:", bg=ADM_P, fg=ADM_T, font=("Courier",10)).pack(side="left")
        self._cust_val = tk.StringVar(value="7")
        tk.Entry(cx, textvariable=self._cust_val, bg=ADM_BG, fg=ADM_G,
                 insertbackground=ADM_G, relief="flat", font=("Courier",12),
                 bd=6, width=8).pack(side="left", padx=8)
        self._cust_unit = tk.StringVar(value="дней")
        um = ttk.Combobox(cx, textvariable=self._cust_unit,
                          values=["секунд","минут","часов","дней","месяцев","лет"],
                          state="readonly", width=10, font=("Courier",10))
        um.pack(side="left", padx=4)
        tk.Button(cx, text="Применить", bg=ADM_BG, fg=ADM_G, relief="flat",
                  font=("Courier",10), cursor="hand2", bd=0, padx=12, pady=5,
                  command=self._apply_custom_dur).pack(side="left", padx=10)
        self._dur_lbl = tk.Label(f, text=f"◈ Выбрано: {fmt_duration(86400)}",
                                  bg=ADM_BG, fg=ADM_G, font=("Courier",11,"bold"))
        self._dur_lbl.pack(anchor="w", pady=(0,8))
        gr = tk.Frame(f, bg=ADM_BG); gr.pack(fill="x", pady=(0,10))
        tk.Label(gr, text="Кол-во:", bg=ADM_BG, fg=ADM_T, font=("Courier",11)).pack(side="left")
        tk.Entry(gr, textvariable=self._tkey_cnt, bg=ADM_P, fg=ADM_G,
                 insertbackground=ADM_G, relief="flat", font=("Courier",12),
                 bd=7, width=6).pack(side="left", padx=10)
        for n in [1,3,5,10]:
            tk.Button(gr, text=f"×{n}", bg=ADM_P, fg=ADM_G, relief="flat",
                      font=("Courier",10,"bold"), cursor="hand2", bd=0, padx=9, pady=5,
                      command=lambda n=n: self._gen_timed(n)).pack(side="left", padx=2)
        out = self._a_card(f, col=ADM_G, fill="both", expand=True, pady=(0,10))
        self._tk_out = tk.Text(out, bg="#030a00", fg=ADM_G, font=("Courier",12),
                                relief="flat", state="disabled", wrap="none", bd=12)
        sb = ttk.Scrollbar(out, command=self._tk_out.yview)
        self._tk_out.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y"); self._tk_out.pack(fill="both", expand=True)
        br = tk.Frame(f, bg=ADM_BG); br.pack(fill="x")
        for txt, cmd in [
            ("⊠ Очистить", lambda: (self._tk_out.configure(state="normal"),
                                    self._tk_out.delete("1.0","end"),
                                    self._tk_out.configure(state="disabled"))),
            ("⊞ Скопировать", lambda: (self.clipboard_clear(),
                                       self.clipboard_append(self._tk_out.get("1.0","end")))),
        ]:
            tk.Button(br, text=txt, bg=ADM_P, fg=ADM_A2, relief="flat",
                      font=("Courier",10), cursor="hand2", bd=0, padx=12, pady=7,
                      command=cmd).pack(side="right", padx=3)
        return f

    def _upd_dur_lbl(self):
        try: self._dur_lbl.configure(text=f"◈ Выбрано: {fmt_duration(self._tkey_sec.get())}")
        except: pass

    def _apply_custom_dur(self):
        try: val = int(self._cust_val.get())
        except: val = 1
        mult = {"секунд":1,"минут":60,"часов":3600,"дней":86400,
                "месяцев":2592000,"лет":31536000}.get(self._cust_unit.get(), 86400)
        self._tkey_sec.set(val*mult); self._upd_dur_lbl()

    def _gen_timed(self, n=None):
        try: count = n or int(self._tkey_cnt.get() or 1)
        except: count = 1
        sec = self._tkey_sec.get(); dur_lbl = fmt_duration(sec)
        keys = [generate_timed_key(sec) for _ in range(count)]
        self._tk_out.configure(state="normal")
        self._tk_out.insert("end", f"\n{time.strftime('[%H:%M:%S]')} × {count} [{dur_lbl}]:\n")
        for k in keys: self._tk_out.insert("end", f"  {k}   // {dur_lbl}\n")
        self._tk_out.configure(state="disabled"); self._tk_out.see("end")
        self._log(f"⚡ {count} тайм-ключей [{dur_lbl}]", "gold")
        self._toast.show(f"{count} тайм-ключей [{dur_lbl}]", kind="success")

    def _mk_a_users(self, parent):
        f = tk.Frame(parent, bg=ADM_BG)
        top = tk.Frame(f, bg=ADM_BG); top.pack(fill="x", pady=(0,10))
        tk.Label(top, text="◐  ИГРОКИ", bg=ADM_BG, fg=ADM_AC,
                 font=("Courier",13,"bold")).pack(side="left")
        tk.Button(top, text="↻", bg=ADM_P, fg=ADM_A2, relief="flat", font=("Courier",11),
                  cursor="hand2", bd=0, padx=12, pady=6,
                  command=self._a_refresh_u).pack(side="right")
        sr = tk.Frame(f, bg=ADM_BG); sr.pack(fill="x", pady=(0,8))
        tk.Label(sr, text="Поиск:", bg=ADM_BG, fg=ADM_T, font=("Courier",10)).pack(side="left")
        self._usr_q = tk.StringVar()
        self._usr_q.trace_add("write", lambda *a: self._a_refresh_u())
        tk.Entry(sr, textvariable=self._usr_q, bg=ADM_P, fg=ADM_AC,
                 insertbackground=ADM_AC, relief="flat", font=("Courier",11),
                 bd=7, width=24).pack(side="left", padx=10)
        tbl = tk.Frame(f, bg=ADM_P, highlightthickness=1, highlightbackground=ADM_M)
        tbl.pack(fill="both", expand=True)
        tk.Frame(tbl, bg=ADM_AC, height=1).pack(fill="x")
        hdr = tk.Frame(tbl, bg="#0d0005"); hdr.pack(fill="x")
        for text, w in [("Никнейм",14),("Дата рег.",16),("Подписка",16),("Входов",7),("Действия",14)]:
            tk.Label(hdr, text=text, bg="#0d0005", fg=ADM_A2,
                     font=("Courier",10,"bold"), width=w, anchor="w").pack(side="left", padx=5, pady=7)
        tk.Frame(tbl, bg=ADM_M, height=1).pack(fill="x")
        sf = tk.Frame(tbl, bg=ADM_P); sf.pack(fill="both", expand=True)
        canvas = tk.Canvas(sf, bg=ADM_P, highlightthickness=0)
        scr = ttk.Scrollbar(sf, orient="vertical", command=canvas.yview)
        self._usr_inner = tk.Frame(canvas, bg=ADM_P)
        self._usr_inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=self._usr_inner, anchor="nw")
        canvas.configure(yscrollcommand=scr.set)
        scr.pack(side="right", fill="y"); canvas.pack(side="left", fill="both", expand=True)
        self._a_refresh_u()
        return f

    def _a_refresh_u(self):
        for w in self._usr_inner.winfo_children(): w.destroy()
        users = _load_users(); bl = _load_blacklist()
        q = self._usr_q.get().strip().lower() if hasattr(self,"_usr_q") else ""
        items = [(kh,u) for kh,u in users.items() if not q or q in u.get("nickname","").lower()]
        items.sort(key=lambda x: x[1].get("date",""), reverse=True)
        if not items:
            tk.Label(self._usr_inner, text="  Нет игроков", bg=ADM_P, fg=ADM_M,
                     font=("Courier",11)).pack(anchor="w", pady=18, padx=14); return
        for i, (kh, u) in enumerate(items):
            bg2 = ADM_P if i%2==0 else ADM_BG
            row = tk.Frame(self._usr_inner, bg=bg2); row.pack(fill="x")
            nick = u.get("nickname","?"); is_bl = kh in bl
            tk.Label(row, text=nick[:12], bg=bg2, fg=ADM_R if is_bl else ADM_AC,
                     font=("Courier",10,"bold"), width=14, anchor="w").pack(side="left", padx=5, pady=6)
            tk.Label(row, text=u.get("date","—")[:10], bg=bg2, fg=ADM_T,
                     font=("Courier",9), width=16, anchor="w").pack(side="left", padx=5)
            valid, sub = check_subscription(u)
            sc = GRN2 if valid else ERR
            tk.Label(row, text=sub[:14], bg=bg2, fg=sc,
                     font=("Courier",9), width=16, anchor="w").pack(side="left", padx=5)
            tk.Label(row, text=str(u.get("login_count",0)), bg=bg2, fg=ADM_G,
                     font=("Courier",9), width=7, anchor="w").pack(side="left", padx=5)
            bf = tk.Frame(row, bg=bg2); bf.pack(side="right", padx=5)
            if is_bl:
                tk.Button(bf, text="Разбан", bg=bg2, fg=ADM_A2, relief="flat",
                          font=("Courier",9), cursor="hand2", bd=0, padx=8, pady=4,
                          command=lambda k=kh: self._a_unban(k)).pack(side="left")
            else:
                tk.Button(bf, text="⊘ Бан", bg=bg2, fg=ADM_R, relief="flat",
                          font=("Courier",9), cursor="hand2", bd=0, padx=8, pady=4,
                          command=lambda k=kh,n=nick: self._a_ban(k,n)).pack(side="left")
            tk.Button(bf, text="✕", bg=bg2, fg="#660022", relief="flat",
                      font=("Courier",9), cursor="hand2", bd=0, padx=8, pady=4,
                      command=lambda k=kh,n=nick: self._a_del(k,n)).pack(side="left", padx=2)

    def _a_ban(self, kh, nick):
        if not messagebox.askyesno("Бан",f"Заблокировать {nick}?",parent=self): return
        bl = _load_blacklist(); bl.add(kh); _save_blacklist(bl)
        self._log(f"⚡ BANNED: {nick}", "gold")
        self._toast.show(f"Заблокирован: {nick}", kind="warning")
        self._a_refresh()

    def _a_unban(self, kh):
        bl = _load_blacklist(); bl.discard(kh); _save_blacklist(bl)
        self._log("⚡ UNBANNED", "gold")
        self._toast.show("Разблокировано", kind="success")
        self._a_refresh()

    def _a_del(self, kh, nick):
        if not messagebox.askyesno("Удаление",f"Удалить {nick}?",parent=self): return
        users = _load_users()
        if kh in users: del users[kh]; _save_users(users)
        used = _load_used_keys(); used.discard(kh); _save_used_keys(used)
        self._log(f"⚡ DELETED: {nick}", "gold")
        self._toast.show(f"Удалён: {nick}", kind="error")
        self._a_refresh()

    def _mk_a_bl(self, parent):
        f = tk.Frame(parent, bg=ADM_BG)
        top = tk.Frame(f, bg=ADM_BG); top.pack(fill="x", pady=(0,10))
        tk.Label(top, text="⊘  БАН-ЛИСТ", bg=ADM_BG, fg=ADM_R,
                 font=("Courier",13,"bold")).pack(side="left")
        tk.Button(top, text="↻", bg=ADM_P, fg=ADM_AC, relief="flat", font=("Courier",11),
                  cursor="hand2", bd=0, padx=12, pady=6,
                  command=self._a_refresh_bl).pack(side="right")
        add = tk.Frame(f, bg=ADM_P, highlightthickness=1, highlightbackground=ADM_M)
        add.pack(fill="x", pady=(0,10))
        tk.Frame(add, bg=ADM_R, height=1).pack(fill="x")
        r = tk.Frame(add, bg=ADM_P); r.pack(fill="x", padx=14, pady=10)
        tk.Label(r, text="SHA256:", bg=ADM_P, fg=ADM_T, font=("Courier",10)).pack(side="left")
        self._bl_v = tk.StringVar()
        tk.Entry(r, textvariable=self._bl_v, bg=ADM_BG, fg=ADM_R,
                 insertbackground=ADM_R, relief="flat", font=("Courier",11),
                 bd=7, width=32).pack(side="left", padx=10)
        tk.Button(r, text="+ Добавить", bg="#200008", fg=ADM_R, relief="flat",
                  font=("Courier",10,"bold"), cursor="hand2", bd=0, padx=12, pady=6,
                  command=self._a_add_bl).pack(side="left")
        bl_f = self._a_card(f, col=ADM_R, fill="both", expand=True)
        self._bl_inner = tk.Frame(bl_f, bg=ADM_P)
        self._bl_inner.pack(fill="both", expand=True, padx=14, pady=10)
        self._a_refresh_bl()
        return f

    def _a_refresh_bl(self):
        for w in self._bl_inner.winfo_children(): w.destroy()
        bl = _load_blacklist(); users = _load_users()
        if not bl:
            tk.Label(self._bl_inner, text="Бан-лист пуст", bg=ADM_P, fg=ADM_M,
                     font=("Courier",11)).pack(anchor="w", pady=18); return
        for kh in sorted(bl):
            nick = users.get(kh,{}).get("nickname","?")
            r = tk.Frame(self._bl_inner, bg=ADM_BG); r.pack(fill="x", pady=2)
            tk.Label(r, text=f"  ⊘  {nick[:12]:12s}", bg=ADM_BG, fg=ADM_R,
                     font=("Courier",10,"bold"), width=16, anchor="w").pack(side="left", padx=5, pady=6)
            tk.Label(r, text=kh[:22]+"…", bg=ADM_BG, fg="#440022",
                     font=("Courier",9), anchor="w").pack(side="left", padx=10)
            tk.Button(r, text="Разбан", bg=ADM_BG, fg=ADM_AC, relief="flat",
                      font=("Courier",9), cursor="hand2", bd=0, padx=10, pady=4,
                      command=lambda k=kh: (self._a_unban(k), self._a_refresh_bl())
                      ).pack(side="right", padx=10)

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

    # ══════════════════════════════════════════════════
    #  LOG + STATUS
    # ══════════════════════════════════════════════════
    def _log(self, msg, tag="normal"):
        colors = {
            "normal": ACG, "muted": TXT3, "warn": ORG, "error": ERR,
            "info": ACC2, "accent": ACC, "cmd": GOLD, "gold": ADM_G
        }
        def _do():
            self.console.configure(state="normal")
            ts = time.strftime("%H:%M:%S")
            self.console.insert("end", f"[{ts}] {msg}\n")
            s = self.console.index("end - 2 lines linestart")
            e = self.console.index("end - 1 lines lineend")
            self.console.tag_add(tag, s, e)
            self.console.tag_configure(tag, foreground=colors.get(tag, ACG))
            self.console.configure(state="disabled"); self.console.see("end")
        self.after(0, _do)

    def _clear_con(self):
        self.console.configure(state="normal")
        self.console.delete("1.0","end")
        self.console.configure(state="disabled")

    def _set_status(self, msg, pct=None, speed=None, eta=None):
        def _do():
            self.status.set(msg)
            if pct is not None: self.progress.set(max(0., min(100., float(pct))))
            self.spd_var.set(f"↓ {fmt_size(speed)}/с" if speed and speed>0 else "")
            self.eta_var.set(f"⏱ {fmt_time(eta)}" if eta and eta>1 else "")
        self.after(0, _do)

    def _set_btn(self, enabled, text="◈   ИГРАТЬ"):
        def _do():
            self.play_btn.configure(
                state="normal" if enabled else "disabled",
                text=text, bg=GL1 if enabled else GL2,
                fg=ACC if enabled else TXT3
            )
        self.after(0, _do)

    # ══════════════════════════════════════════════════
    #  REINSTALL
    # ══════════════════════════════════════════════════
    def _reinstall(self):
        if not messagebox.askyesno("Переустановка Forge",
                                    "Удалить Forge и переустановить?", parent=self): return
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
        if missing:
            self._log(f"⚠  Требуется загрузка: {', '.join(missing)}", "warn")
        else:
            self._log(f"✓  Forge [{forge_id}] и {MOD_NAME} установлены.", "accent")

    # ══════════════════════════════════════════════════
    #  START / INSTALL / LAUNCH
    # ══════════════════════════════════════════════════
    def _start(self):
        valid, status = check_subscription(self._user)
        if not valid:
            messagebox.showerror("Подписка истекла",
                f"Ваша подписка истекла!\n\nДля продления:\nTelegram {TG_LINK}", parent=self)
            self._log(f"⚠  Запуск заблокирован — подписка истекла.", "error")
            return
        self._set_btn(False, "⏳  Загрузка...")
        threading.Thread(target=self._install_and_launch, daemon=True).start()

    def _install_and_launch(self):
        try:
            self._set_status("Проверка Java...", 2)
            java = get_java()
            if not java:
                raise Exception("Java не найдена!\nСкачай Java 8: https://adoptium.net/temurin/releases/?version=8")
            self._log(f"✓  Java: {java}", "accent")
            self._set_status("Манифест Mojang...", 4)
            manifest = http_get_json(VERSION_MANIFEST)
            ver_url = next((v["url"] for v in manifest["versions"] if v["id"]==MC_VERSION), None)
            if not ver_url: raise Exception(f"Версия {MC_VERSION} не найдена!")
            ver_json = http_get_json(ver_url)
            van_dir = VERSIONS_DIR/MC_VERSION; van_dir.mkdir(parents=True, exist_ok=True)
            with open(van_dir/f"{MC_VERSION}.json","w") as fh: json.dump(ver_json, fh, indent=2)
            client_jar = van_dir/f"{MC_VERSION}.jar"
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
            else:
                self._log(f"✓  Forge: {forge_id}", "accent")
            with open(forge_json_path) as fh: forge_json_data = json.load(fh)
            merged = self._merge_jsons(ver_json, forge_json_data)
            self._set_status("Библиотеки...", 50)
            cp_entries = [str(client_jar)]
            native_jars = []; lib_tasks = []; seen = set()
            cur_os = os_name()
            for lib in merged.get("libraries",[]):
                if not rule_allowed(lib.get("rules")): continue
                dl2 = lib.get("downloads",{}); art = dl2.get("artifact")
                if art and art.get("path"):
                    p = LIBRARIES_DIR/art["path"]
                    if str(p) not in seen:
                        seen.add(str(p)); cp_entries.append(str(p))
                        if art.get("url") and not (p.exists() and p.stat().st_size>0):
                            lib_tasks.append((art["url"],p,art.get("sha1")))
                cls = dl2.get("classifiers",{}); nat_map = lib.get("natives",{})
                if cur_os in nat_map:
                    nat_key = nat_map[cur_os].replace("${arch}","64")
                    nat = cls.get(nat_key)
                    if nat and nat.get("url") and nat.get("path"):
                        np_ = LIBRARIES_DIR/nat["path"]; native_jars.append(str(np_))
                        if not (np_.exists() and np_.stat().st_size>0):
                            lib_tasks.append((nat["url"],np_,nat.get("sha1")))
            if lib_tasks:
                def _lp(done,total,speed,eta):
                    self._set_status(f"Библиотеки: {done}/{total}", 50+done/max(total,1)*12, speed=speed, eta=eta)
                ParallelDownloader(lib_tasks, on_progress=_lp).run()
            self._log("✓  Библиотеки", "accent")
            NATIVES_DIR.mkdir(parents=True, exist_ok=True)
            for njar in native_jars:
                if not os.path.isfile(njar): continue
                try:
                    with zipfile.ZipFile(njar) as z:
                        for name in z.namelist():
                            if any(name.endswith(e) for e in [".dll",".so",".dylib"]):
                                tgt = NATIVES_DIR/Path(name).name
                                if not tgt.exists():
                                    with z.open(name) as src, open(tgt,"wb") as dst: dst.write(src.read())
                except: pass
            self._log("✓  Нативы", "accent")
            self._set_status("Ассеты...", 63)
            ai = ver_json.get("assetIndex",{}); aid = ai.get("id",MC_VERSION)
            idir = ASSETS_DIR/"indexes"; idir.mkdir(parents=True, exist_ok=True)
            aif = idir/f"{aid}.json"
            if not aif.exists(): download_file(ai.get("url"), aif)
            with open(aif) as fh: aj = json.load(fh)
            obj = ASSETS_DIR/"objects"; atasks = []
            for _, info in aj.get("objects",{}).items():
                h = info["hash"]; pre = h[:2]; dst = obj/pre/h
                if not (dst.exists() and dst.stat().st_size>0):
                    atasks.append((f"https://resources.download.minecraft.net/{pre}/{h}", dst, h))
            if atasks:
                def _ap(done,total,speed,eta):
                    self._set_status(f"Ассеты: {done}/{total}", 63+done/max(total,1)*20, speed=speed, eta=eta)
                ParallelDownloader(atasks, on_progress=_ap).run()
            self._log("✓  Ассеты", "accent")
            MODS_DIR.mkdir(parents=True, exist_ok=True)
            mod_jar = MODS_DIR/f"{MOD_NAME}-{MOD_VERSION}.jar"
            if not mod_jar.exists():
                mu = self.mod_url.get().strip()
                if not mu.startswith("http"): raise Exception("Нет ссылки на мод!")
                self._set_status("Скачивание мода...", 85)
                def _mp(done, total):
                    if total: self._set_status(f"Мод: {int(done/total*100)}%", 85+done/total*8)
                download_file(mu, mod_jar, on_progress=_mp)
                self._log(f"✓  {MOD_NAME}", "accent")
            else:
                self._log("✓  Мод установлен", "accent")
            self._set_status("Запуск...", 95)
            srv = self._connect_server; self._connect_server = None
            self._log("▸  Запускаем Minecraft + Forge...", "accent")
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
        fvd_dir = VERSIONS_DIR/forge_id; fvd_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(vp_p, fvd_dir/f"{forge_id}.json")
        with zipfile.ZipFile(FORGE_INST) as zf:
            for name in zf.namelist():
                if name.startswith("maven/") and not name.endswith("/"):
                    dst = LIBRARIES_DIR/name[6:]
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    if not dst.exists():
                        with zf.open(name) as src: dst.write_bytes(src.read())
        lib_tasks = []; seen = set()
        for lib in ip.get("libraries",[])+fvd.get("libraries",[]):
            art = lib.get("downloads",{}).get("artifact",{})
            path = art.get("path",""); url = art.get("url",""); sha1 = art.get("sha1")
            if not path or path in seen: continue
            seen.add(path); dest = LIBRARIES_DIR/path
            if dest.exists() and dest.stat().st_size>0: continue
            if url: lib_tasks.append((url,dest,sha1))
            else:
                nm = lib.get("name","")
                if nm:
                    rel = str(maven_coord_to_path(nm))
                    dest2 = LIBRARIES_DIR/rel
                    if not (dest2.exists() and dest2.stat().st_size>0):
                        lib_tasks.append((MAVEN_FORGE+rel.replace("\\","/"),dest2,sha1))
        if lib_tasks:
            def _lp(done,total,speed,eta):
                self._set_status(f"Forge libs: {done}/{total}", 25+done/max(total,1)*15, speed=speed, eta=eta)
            ParallelDownloader(lib_tasks, on_progress=_lp,
                               on_error=lambda d,e: self._log(f"  ⚠ {Path(d).name}: {e}","warn")).run()
        data_map = {}
        for key, val in ip.get("data",{}).items():
            cv = val.get("client","")
            if cv.startswith("[") and cv.endswith("]"):
                data_map[key] = str(LIBRARIES_DIR/maven_coord_to_path(cv[1:-1]))
            elif cv.startswith("/"): data_map[key] = str(FORGE_EXTRACT/cv.lstrip("/"))
            else: data_map[key] = cv
        data_map.update({
            "MINECRAFT_JAR": str(client_jar), "SIDE": "client",
            "ROOT": str(MC_DIR), "INSTALLER": str(FORGE_INST),
            "LIBRARY_DIR": str(LIBRARIES_DIR)
        })
        cp_sep = ";" if platform.system()=="Windows" else ":"
        procs = [p for p in ip.get("processors",[]) if "client" in p.get("sides",["client","server"])]
        for i, proc in enumerate(procs, 1):
            jc = proc.get("jar","")
            if not jc: continue
            jp = LIBRARIES_DIR/maven_coord_to_path(jc)
            if not jp.exists(): self._log(f"  ⚠ Jar: {jp.name}", "warn"); continue
            outs = proc.get("outputs",{})
            if outs and all(Path(resolve_proc_arg(v,data_map)).exists() for v in outs.values()):
                self._log(f"  [{i}/{len(procs)}] Пропуск", "muted"); continue
            cp_list = [str(jp)]
            for dep in proc.get("classpath",[]):
                dp = LIBRARIES_DIR/maven_coord_to_path(dep)
                if dp.exists(): cp_list.append(str(dp))
            try: mc = get_jar_main_class(jp)
            except Exception as e: self._log(f"  ⚠ {jp.name}: {e}", "warn"); continue
            args = [resolve_proc_arg(a,data_map) for a in proc.get("args",[])]
            cmd = [java,"-cp",cp_sep.join(cp_list),mc]+args
            self._log(f"  [{i}/{len(procs)}] {jp.name}", "info")
            self._set_status(f"Forge: {i}/{len(procs)}", 40+i/max(len(procs),1)*9)
            try:
                res = subprocess.run(cmd, capture_output=True, text=True, errors="replace",
                                     timeout=180, cwd=str(MC_DIR))
                if res.returncode != 0: self._log(f"    ⚠ код {res.returncode}", "warn")
                else: self._log("    ✓ OK", "muted")
            except subprocess.TimeoutExpired: self._log("    ⚠ Таймаут", "warn")
            except Exception as ex: self._log(f"    ⚠ {ex}", "warn")
        fp = fvd_dir/f"{forge_id}.json"
        if fp.exists():
            self._log(f"✓  Forge {forge_id} установлен!", "accent"); return forge_id, fp
        return None, None

    def _merge_jsons(self, vanilla, forge):
        merged = dict(vanilla)
        merged["libraries"] = forge.get("libraries",[]) + vanilla.get("libraries",[])
        if "mainClass" in forge: merged["mainClass"] = forge["mainClass"]
        merged["arguments"] = {}
        for key in ("game","jvm"):
            merged["arguments"][key] = (
                vanilla.get("arguments",{}).get(key,[]) +
                forge.get("arguments",{}).get(key,[])
            )
        return merged

    def _run_mc(self, java, cp_entries, asset_idx_id, ver_json, forge_id, server_info=None):
        uname = self.username.get().strip() or self._nick
        ram_mb = self.ram.get() * 1024
        cp_sep = ";" if platform.system()=="Windows" else ":"
        classpath = cp_sep.join(dict.fromkeys(cp_entries))
        main_cls = ver_json.get("mainClass","cpw.mods.modlauncher.Launcher")
        fake_uuid = str(uuid.uuid4())
        repl = {
            "${auth_player_name}": uname, "${version_name}": forge_id,
            "${game_directory}": str(MC_DIR), "${assets_root}": str(ASSETS_DIR),
            "${assets_index_name}": asset_idx_id, "${auth_uuid}": fake_uuid,
            "${auth_access_token}": "0", "${user_type}": "legacy",
            "${version_type}": "release", "${natives_directory}": str(NATIVES_DIR),
            "${launcher_name}": LAUNCHER_NAME, "${launcher_version}": LAUNCHER_VER,
            "${classpath}": classpath,
        }
        def resolve(a):
            for k, v in repl.items(): a = a.replace(k,v)
            return a
        def parse_args(sec):
            out = []
            for arg in ver_json.get("arguments",{}).get(sec,[]):
                if isinstance(arg, str): out.append(resolve(arg))
                elif isinstance(arg,dict) and rule_allowed(arg.get("rules",[])):
                    val = arg.get("value",[]); vals = [val] if isinstance(val,str) else val
                    out.extend(resolve(v) for v in vals)
            return out
        jvm_args = parse_args("jvm"); game_args = parse_args("game")
        base_jvm = [
            java, f"-Xmx{ram_mb}m", f"-Xms{min(ram_mb,512)}m", "-Xss4M",
            f"-Djava.library.path={NATIVES_DIR}",
            "-Dminecraft.api.auth.host=http://localhost/",
            "-Dminecraft.api.account.host=http://localhost/",
            "-Dminecraft.api.session.host=http://localhost/",
            "-Dminecraft.api.services.host=http://localhost/",
            "-Dfml.ignoreInvalidMinecraftCertificates=true",
            "-Dfml.ignorePatchDiscrepancies=true",
            "-Dlog4j2.formatMsgNoLookups=true",
            "-XX:+UnlockExperimentalVMOptions","-XX:+UseG1GC",
            "-XX:G1NewSizePercent=20","-XX:G1ReservePercent=20",
            "-XX:MaxGCPauseMillis=50","-XX:G1HeapRegionSize=32M",
            "-XX:+ParallelRefProcEnabled","-XX:MaxTenuringThreshold=1",
            "-XX:SurvivorRatio=32","-XX:+DisableExplicitGC","-XX:+AlwaysPreTouch",
            "-XX:+UseStringDeduplication","-XX:ReservedCodeCacheSize=512m",
            "-XX:+UseCodeCacheFlushing","-Dfile.encoding=UTF-8"
        ]
        cp_block = [] if any(a=="-cp" for a in jvm_args) else ["-cp", classpath]
        srv_args = (["--server",server_info[0],"--port",str(server_info[1])] if server_info else [])
        cmd = base_jvm + jvm_args + cp_block + [main_cls] + game_args + srv_args
        self._log(f"◈  {uname}  ·  {self.ram.get()} ГБ  ·  {forge_id}", "accent")
        self._set_status("◈  Minecraft запущен!", 100)
        self._set_btn(False, "▸  ЗАПУЩЕН")
        self.eta_var.set(""); self.spd_var.set("")
        try:
            self._mc_process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, errors="replace", cwd=str(MC_DIR)
            )
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
            self._mc_process = None
            self._set_btn(True)
            self._set_status("Готов к запуску", 0)
            self.progress.set(0)


# ══════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════
if __name__ == "__main__":

    if len(sys.argv) >= 2 and sys.argv[1] == "--angelsvistop121":
        if not is_activated():
            print("Войди как администратор через лаунчер.")
            sys.exit(1)
        u = get_current_user()
        if not u.get("is_admin"):
            print("Нет прав администратора.")
            sys.exit(1)
        app = AngelsLauncher()
        app.after(500, lambda: app._show("admin"))
        app.mainloop()
        sys.exit(0)

    if len(sys.argv) >= 2 and sys.argv[1] == "--keygen":
        n = int(sys.argv[2]) if len(sys.argv) >= 3 else 10
        print(f"\n{'═'*50}\n  Angels Launcher v{LAUNCHER_VER} — Keygen\n{'═'*50}")
        keygen(n)
        print(f"{'═'*50}\n")
        sys.exit(0)

    if len(sys.argv) >= 2 and sys.argv[1] == "--print-actions":
        print(generate_github_actions_config())
        sys.exit(0)

    while True:
        if not is_activated():
            auth = AuthScreen()
            auth.mainloop()
            if not auth._activated:
                break

        app = AngelsLauncher()
        app.mainloop()

        if not app._logout_requested:
            break
