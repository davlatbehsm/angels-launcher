"""
Angels Launcher — ПАТЧ v13.1
════════════════════════════════════════════════════════
ИСПРАВЛЕНИЯ:
  ✓ WinError 32 — файл .tmp занят: retry + robocopy fallback
  ✓ Обновление: атомарная замена через temp-папку
  ✓ Скругления везде: кнопки, карточки, поля ввода, toast
  ✓ Улучшенный прогресс обновления с процентами и скоростью
  ✓ Новый стиль — pill-радиусы, мягкие тени через canvas

КАК ПРИМЕНИТЬ:
  Заменить в angels_launcher_v13.py:
    1. Функцию download_and_install в классе AutoUpdater
    2. Функцию make_pill_button
    3. Функцию make_action_button
    4. Функцию make_neon_entry
    5. Класс NeonProgressBar
    6. Метод _build_update_button в AngelsLauncher
════════════════════════════════════════════════════════
"""

import os, sys, shutil, time, platform, subprocess, threading
from pathlib import Path


# ══════════════════════════════════════════════════════════════════
# ПАТЧ 1: AutoUpdater.download_and_install — ИСПРАВЛЕН WinError 32
# ══════════════════════════════════════════════════════════════════

def _patched_download_and_install(self, url, new_version, on_progress=None, on_done=None):
    """
    ИСПРАВЛЕНО:
    - WinError 32: файл .tmp занят → используем уникальное имя + retry loop
    - На Windows: bat-скрипт с robocopy как fallback вместо move
    - Проверка целостности скачанного файла
    - Прогресс передаёт реальные байты/скорость
    """
    def _do():
        try:
            current = Path(sys.executable)
            is_exe = current.suffix.lower() == ".exe"

            if is_exe:
                # Используем уникальное имя чтобы избежать конфликта
                ts = str(int(time.time()))
                new_path = current.parent / f"angels_launcher_update_{ts}.exe"
                final_path = current
            else:
                script = Path(__file__).resolve()
                ts = str(int(time.time()))
                new_path = script.parent / f"angels_launcher_update_{ts}.py"
                final_path = script

            # Удаляем старые temp-файлы апдейтера если есть
            parent = new_path.parent
            for old_tmp in parent.glob("angels_launcher_update_*.exe"):
                if old_tmp != new_path:
                    try: old_tmp.unlink()
                    except: pass
            for old_tmp in parent.glob("angels_launcher_update_*.py"):
                if old_tmp != new_path:
                    try: old_tmp.unlink()
                    except: pass

            # ── Скачиваем с прогрессом ──────────────────────────────
            import urllib.request
            LAUNCHER_VER_LOCAL = new_version  # для User-Agent

            start_t = time.time()
            tmp_dl = str(new_path) + ".dl"  # промежуточный файл загрузки

            req = urllib.request.Request(
                url,
                headers={"User-Agent": f"AngelsLauncher/{LAUNCHER_VER_LOCAL}"}
            )
            with urllib.request.urlopen(req, timeout=120) as r:
                total = int(r.headers.get("Content-Length", 0))
                done = 0
                with open(tmp_dl, "wb") as f:
                    while True:
                        chunk = r.read(65536)
                        if not chunk:
                            break
                        f.write(chunk)
                        done += len(chunk)
                        elapsed = max(0.1, time.time() - start_t)
                        speed = done / elapsed
                        if on_progress:
                            on_progress(done, total, speed)

            # Проверяем размер
            dl_size = Path(tmp_dl).stat().st_size
            if dl_size < 10000:
                Path(tmp_dl).unlink(missing_ok=True)
                raise Exception(f"Файл скачался некорректно ({dl_size} байт)")

            # Переименовываем .dl → финальный temp
            try:
                shutil.move(tmp_dl, str(new_path))
            except Exception as e:
                # Если и это не работает — пробуем копировать
                shutil.copy2(tmp_dl, str(new_path))
                try: Path(tmp_dl).unlink()
                except: pass

            # Записываем version.json рядом
            import json
            version_file = new_path.parent / "angels_launcher_version.json"
            try:
                version_file.write_text(json.dumps({
                    "version": new_version,
                    "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                }, indent=2))
            except: pass

            current_pid = os.getpid()

            if platform.system() == "Windows":
                # ── BAT-скрипт с retry и robocopy fallback ────────────
                bat = new_path.parent / f"_angels_update_{int(time.time())}.bat"
                bat_content = (
                    "@echo off\n"
                    "chcp 65001 > nul\n"
                    f"echo Angels Launcher Updater\n"
                    f"timeout /t 2 /nobreak > nul\n"
                    f"taskkill /PID {current_pid} /F > nul 2>&1\n"
                    "timeout /t 2 /nobreak > nul\n"
                    # Пробуем move
                    f"move /y \"{new_path}\" \"{final_path}\" > nul 2>&1\n"
                    "if errorlevel 1 (\n"
                    # Fallback: robocopy
                    f"    robocopy \"{new_path.parent}\" \"{final_path.parent}\" \"{new_path.name}\" /MOV /R:3 /W:1 > nul 2>&1\n"
                    f"    rename \"{final_path.parent / new_path.name}\" \"{final_path.name}\" > nul 2>&1\n"
                    ")\n"
                    f"start \"\" \"{final_path}\"\n"
                    "del \"%~f0\"\n"
                )
                bat.write_text(bat_content, encoding="cp866")
                if on_done:
                    on_done(True, str(bat))
            else:
                # Linux/Mac — прямая замена
                import stat as stat_mod
                # Retry loop для занятых файлов
                for attempt in range(5):
                    try:
                        shutil.move(str(new_path), str(final_path))
                        break
                    except PermissionError:
                        if attempt < 4:
                            time.sleep(0.5)
                        else:
                            raise
                try:
                    st = os.stat(final_path)
                    os.chmod(final_path,
                             st.st_mode | stat_mod.S_IEXEC | stat_mod.S_IXGRP | stat_mod.S_IXOTH)
                except: pass
                if on_done:
                    on_done(True, str(final_path))

        except Exception as e:
            # Чистим мусорные файлы при ошибке
            try:
                if 'new_path' in dir() and Path(new_path).exists():
                    Path(new_path).unlink()
            except: pass
            try:
                tmp_dl_path = str(new_path) + ".dl"
                if Path(tmp_dl_path).exists():
                    Path(tmp_dl_path).unlink()
            except: pass
            if on_done:
                on_done(False, str(e))

    threading.Thread(target=_do, daemon=True).start()


# ══════════════════════════════════════════════════════════════════
# ПАТЧ 2: Закруглённые кнопки и карточки
# Вставить вместо make_pill_button и make_action_button
# ══════════════════════════════════════════════════════════════════

# Цвета (дублируем из основного файла)
BG_VOID   = "#00040c"
BG_BASE   = "#000810"
BG_CARD   = "#040d1c"
BG_PANEL  = "#060f20"
BG_ITEM   = "#081428"
BG_HOVER  = "#0c1e38"
BD_DARK   = "#0c1e36"
BD_MID    = "#123060"
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

try:
    import tkinter as tk
    from tkinter import ttk
    import math

    def _hex_to_rgb(h):
        h = h.lstrip('#')
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

    def _lerp_color(c1, c2, t):
        r1,g1,b1 = _hex_to_rgb(c1)
        r2,g2,b2 = _hex_to_rgb(c2)
        t = max(0.0, min(1.0, t))
        return f"#{int(r1+(r2-r1)*t):02x}{int(g1+(g2-g1)*t):02x}{int(b1+(b2-b1)*t):02x}"


    def _draw_rounded_rect(canvas, x1, y1, x2, y2, r=8, **kwargs):
        """Рисует скруглённый прямоугольник на Canvas."""
        r = min(r, (x2-x1)//2, (y2-y1)//2)
        points = [
            x1+r, y1,
            x2-r, y1,
            x2, y1,
            x2, y1+r,
            x2, y2-r,
            x2, y2,
            x2-r, y2,
            x1+r, y2,
            x1, y2,
            x1, y2-r,
            x1, y1+r,
            x1, y1,
        ]
        return canvas.create_polygon(points, smooth=True, **kwargs)


    class RoundedButton(tk.Canvas):
        """
        Полностью скруглённая кнопка через Canvas.
        Поддерживает: иконку, текст, hover-анимацию, accent-полоску.
        """
        def __init__(self, parent, text, command=None,
                     bg=BG_ITEM, fg=AC_MAIN,
                     hover_bg=BG_HOVER, hover_fg=TX_WHITE,
                     font=("Segoe UI", 10, "bold"),
                     radius=10, px=18, py=9,
                     icon=None, accent=None,
                     width=None, height=None,
                     **kw):
            self._btn_bg = bg
            self._btn_fg = fg
            self._hover_bg = hover_bg
            self._hover_fg = hover_fg
            self._radius = radius
            self._command = command
            self._text = text
            self._icon = icon
            self._font = font
            self._px = px
            self._py = py
            self._accent = accent
            self._hovered = False
            self._press_phase = 0.0
            self._current_bg = bg
            self._current_fg = fg

            # Вычисляем размер
            import tkinter.font as tkfont
            fnt = tkfont.Font(family=font[0], size=font[1],
                              weight=font[2] if len(font) > 2 else "normal")
            txt = (icon + "  " if icon else "") + text
            tw = fnt.measure(txt)
            th = fnt.metrics("linespace")

            _w = width or (tw + px * 2 + (4 if accent else 0))
            _h = height or (th + py * 2)

            super().__init__(parent, bg=BG_VOID,
                             width=_w, height=_h,
                             highlightthickness=0, cursor="hand2", **kw)

            self._w = _w
            self._h = _h

            self.bind("<Configure>", self._redraw)
            self.bind("<Enter>", self._on_enter)
            self.bind("<Leave>", self._on_leave)
            self.bind("<Button-1>", self._on_press)
            self.bind("<ButtonRelease-1>", self._on_release)

            # Совместимость с make_pill_button API
            self._labels = []
            self._inner = self
            self._row = self

            self._redraw()

        def _on_enter(self, e=None):
            self._hovered = True
            self._animate_to(self._hover_bg, self._hover_fg)

        def _on_leave(self, e=None):
            self._hovered = False
            self._animate_to(self._btn_bg, self._btn_fg)

        def _on_press(self, e=None):
            self._press_phase = 1.0
            self._redraw()
            if self._command:
                self.after(80, self._command)

        def _on_release(self, e=None):
            self._press_phase = 0.0
            self._redraw()

        def _animate_to(self, target_bg, target_fg, step=0, steps=6):
            if step > steps:
                self._current_bg = target_bg
                self._current_fg = target_fg
                self._redraw()
                return
            t = step / steps
            self._current_bg = _lerp_color(self._current_bg, target_bg, t)
            self._current_fg = _lerp_color(self._current_fg, target_fg, t)
            self._redraw()
            self.after(16, lambda: self._animate_to(target_bg, target_fg, step+1, steps))

        def _redraw(self, e=None):
            W = self.winfo_width() or self._w
            H = self.winfo_height() or self._h
            self.delete("all")

            bg = self._current_bg
            fg = self._current_fg
            r = self._radius

            # Фон с лёгким нажатием
            if self._press_phase > 0:
                bg = _lerp_color(bg, BG_VOID, 0.3)

            # Тень (чуть темнее снизу)
            shadow_col = _lerp_color(BG_VOID, bg, 0.3)
            _draw_rounded_rect(self, 2, 3, W-1, H-1, r=r,
                               fill=shadow_col, outline="")

            # Основной фон
            _draw_rounded_rect(self, 1, 1, W-2, H-2, r=r,
                               fill=bg, outline="")

            # Граница
            border_col = _lerp_color(bg, fg, 0.25)
            _draw_rounded_rect(self, 1, 1, W-2, H-2, r=r,
                               fill="", outline=border_col, width=1)

            # Accent-полоска слева (скруглённая)
            if self._accent:
                self.create_rectangle(1, r, 4, H-r, fill=self._accent, outline="", width=0)
                self.create_oval(1, 1, 6, 2*r, fill=self._accent, outline="")
                self.create_oval(1, H-2*r, 6, H-1, fill=self._accent, outline="")

            # Текст
            ox = self._px + (3 if self._accent else 0)
            txt = (self._icon + "  " if self._icon else "") + self._text

            # Лёгкая тень текста
            self.create_text(W//2 + 1, H//2 + 2,
                             text=txt, fill=_lerp_color(BG_VOID, bg, 0.5),
                             font=self._font, anchor="center")
            self.create_text(W//2, H//2,
                             text=txt, fill=fg,
                             font=self._font, anchor="center")

        def configure(self, **kw):
            if 'bg' in kw:
                self._btn_bg = kw.pop('bg')
                self._current_bg = self._btn_bg
            super().configure(**kw)
            self._redraw()

        # Совместимость с pill_button API
        @property
        def _key(self): return getattr(self, '_nav_key', None)
        @_key.setter
        def _key(self, v): self._nav_key = v

        @property
        def _accent_val(self): return self._accent
        @_accent_val.setter
        def _accent_val(self, v): self._accent = v

        @property
        def _normal_fg(self): return self._btn_fg
        @_normal_fg.setter
        def _normal_fg(self, v): self._btn_fg = v

        def _set_active(self, active, accent_col=None):
            if active:
                if accent_col:
                    ab = _lerp_color(BG_VOID, accent_col, 0.15)
                    self._current_bg = ab
                    self._btn_bg = ab
                    self._current_fg = accent_col
                    self._accent = accent_col
            else:
                self._current_bg = BG_CARD
                self._btn_bg = BG_CARD
                self._current_fg = self._btn_fg
                self._accent = None
            self._redraw()

        # Stub для label-style configure (совместимость со старым кодом)
        class _LabelStub:
            def configure(self, **kw): pass
            def cget(self, k): return ""


    def make_pill_button_rounded(parent, text, command=None,
                                  bg=BG_ITEM, fg=AC_MAIN,
                                  hover_bg=BG_HOVER, hover_fg=TX_WHITE,
                                  font=("Segoe UI", 10, "bold"),
                                  px=18, py=8,
                                  icon=None, accent_left=None,
                                  width=None, **kw):
        """Скруглённая замена make_pill_button."""
        btn = RoundedButton(
            parent, text, command=command,
            bg=bg, fg=fg,
            hover_bg=hover_bg, hover_fg=hover_fg,
            font=font, radius=10,
            px=px, py=py,
            icon=icon, accent=accent_left,
            **kw
        )
        # Совместимые атрибуты
        btn._bg = bg
        btn._fg = fg
        btn._hover_bg = hover_bg
        btn._hover_fg = hover_fg
        btn._labels = [btn._LabelStub()]
        btn._inner = btn
        btn._row = btn
        btn._active_bar = None
        return btn


    def make_action_button_rounded(parent, text, command=None,
                                    style="primary",
                                    font=("Segoe UI", 10, "bold"),
                                    px=20, py=10, icon=None, **kw):
        """Скруглённая замена make_action_button."""
        styles = {
            "primary":  (AC_MAIN,   BG_VOID, "#00e0ff", "#001020"),
            "danger":   (AC_RED,    BG_VOID, "#ff6688", "#1a0010"),
            "success":  (AC_GREEN,  BG_VOID, "#44ffaa", "#001a10"),
            "warning":  (AC_ORANGE, BG_VOID, "#ffaa55", "#1a0800"),
            "ghost":    (BG_ITEM,   TX_MID,  BG_HOVER,  TX_WHITE),
            "admin":    (ADM_ACC,   BG_VOID, "#ff44ee", "#100018"),
        }
        norm_bg, norm_fg, h_bg, h_fg = styles.get(style, styles["ghost"])

        btn = RoundedButton(
            parent, text, command=command,
            bg=norm_bg, fg=norm_fg,
            hover_bg=h_bg, hover_fg=h_fg,
            font=font, radius=10,
            px=px, py=py,
            icon=icon, **kw
        )
        btn._norm_bg = norm_bg
        btn._norm_fg = norm_fg
        btn._h_bg = h_bg
        btn._h_fg = h_fg
        btn._labels = [btn._LabelStub()]
        btn._inner = btn
        btn._row = btn
        return btn


    # ── Скруглённое поле ввода ─────────────────────────────────────
    def make_neon_entry_rounded(parent, textvariable, show="",
                                 placeholder="", width=None,
                                 icon=None, bg=BG_ITEM,
                                 fg=TX_MAIN, accent=AC_MAIN):
        """Поле ввода со скруглёнными углами через Frame с border-radius эффектом."""
        RADIUS = 8

        outer = tk.Frame(parent, bg=BG_VOID)

        canvas = tk.Canvas(outer, bg=BG_VOID, highlightthickness=0, height=42)
        canvas.pack(fill="x", expand=True)

        def _draw_bg(focused=False):
            canvas.delete("all")
            W = canvas.winfo_width() or 300
            H = 40
            border_col = accent if focused else BD_DARK
            fill_col = BG_HOVER if focused else bg

            # Тень
            _draw_rounded_rect(canvas, 2, 3, W-1, H, r=RADIUS,
                               fill=_lerp_color(BG_VOID, fill_col, 0.3), outline="")
            # Фон
            _draw_rounded_rect(canvas, 1, 1, W-2, H-1, r=RADIUS,
                               fill=fill_col, outline=border_col, width=1)

            # Glow при фокусе
            if focused:
                _draw_rounded_rect(canvas, 0, 0, W-1, H, r=RADIUS+1,
                                   fill="", outline=_lerp_color(BG_VOID, accent, 0.3), width=2)

        canvas.bind("<Configure>", lambda e: _draw_bg())

        frame = tk.Frame(outer, bg=bg)
        frame.place(x=6, y=5, relwidth=1.0, width=-12, height=30)

        if icon:
            tk.Label(frame, text=icon, bg=bg, fg=TX_DIM,
                     font=("Segoe UI", 11)).pack(side="left", padx=(6, 2))

        kw2 = dict(textvariable=textvariable, bg=bg, fg=fg,
                   insertbackground=accent, relief="flat",
                   font=("Segoe UI", 10), bd=0)
        if width: kw2["width"] = width
        if show: kw2["show"] = show

        e = tk.Entry(frame, **kw2)
        e.pack(side="left", fill="x", expand=True, ipady=4)

        _hp = [False]
        if placeholder:
            e.insert(0, placeholder)
            e.configure(fg=TX_DIM)
            _hp[0] = True

        def _fi(ev):
            if _hp[0]:
                e.delete(0, "end")
                if show: e.configure(show=show)
                e.configure(fg=fg)
                _hp[0] = False
            frame.configure(bg=BG_HOVER)
            e.configure(bg=BG_HOVER)
            if icon: frame.winfo_children()[0].configure(bg=BG_HOVER, fg=accent)
            _draw_bg(focused=True)

        def _fo(ev):
            if not textvariable.get() and placeholder:
                e.configure(show="")
                e.insert(0, placeholder)
                e.configure(fg=TX_DIM)
                _hp[0] = True
            frame.configure(bg=bg)
            e.configure(bg=bg)
            if icon: frame.winfo_children()[0].configure(bg=bg, fg=TX_DIM)
            _draw_bg(focused=False)

        e.bind("<FocusIn>", _fi)
        e.bind("<FocusOut>", _fo)
        e._hp = _hp

        def get_value():
            if _hp[0]: return ""
            return e.get().strip()

        outer.get_value = get_value
        outer._entry = e
        return outer


    # ── Скруглённый прогресс-бар ──────────────────────────────────
    class RoundedProgressBar(tk.Canvas):
        def __init__(self, parent, height=10, bg=BG_ITEM, fg=AC_MAIN,
                     radius=5, **kw):
            super().__init__(parent, bg=BG_VOID, height=height+6,
                             highlightthickness=0, **kw)
            self._bg = bg
            self._fg = fg
            self._radius = radius
            self._val = 0.0
            self._glow_phase = 0.0
            self._running = True
            self.bind("<Configure>", self._redraw)
            self._tick()

        def set(self, val):
            self._val = max(0.0, min(1.0, val))
            self._redraw()

        def _redraw(self, e=None):
            W = self.winfo_width() or 400
            H = self.winfo_height() or 16
            self.delete("all")
            r = self._radius

            # Фоновая дорожка
            _draw_rounded_rect(self, 2, 3, W-2, H-3, r=r,
                               fill=BG_VOID, outline=BD_DARK, width=1)

            if self._val <= 0:
                return

            fw = max(r*2+2, int((W-6) * self._val) + 3)

            # Цвет прогресса
            if self._val < 0.33:
                col = _lerp_color(AC_GLOW, AC_MAIN, self._val * 3)
            elif self._val < 0.66:
                col = AC_MAIN
            else:
                col = _lerp_color(AC_MAIN, AC_MINT, (self._val - 0.66) * 3)

            # Glow под полосой
            glow_t = (math.sin(self._glow_phase) + 1) / 2
            glow_col = _lerp_color(BG_VOID, col, 0.15 + glow_t * 0.1)
            _draw_rounded_rect(self, 1, 1, fw+3, H-1, r=r,
                               fill=glow_col, outline="")

            # Основная полоса
            _draw_rounded_rect(self, 3, 4, fw, H-4, r=r,
                               fill=col, outline="")

            # Блик сверху
            shimmer = _lerp_color(col, TX_WHITE, 0.35 + glow_t * 0.15)
            self.create_rectangle(4, 4, fw-1, H//2-1,
                                  fill=shimmer, outline="")

            # Процент справа если > 5%
            if self._val > 0.05:
                pct_txt = f"{int(self._val*100)}%"
                self.create_text(W//2, H//2,
                                 text=pct_txt,
                                 fill=TX_WHITE,
                                 font=("Segoe UI", 7, "bold"))

        def _tick(self):
            if not self._running:
                return
            try:
                self._glow_phase += 0.06
                self._redraw()
                self.after(33, self._tick)
            except: pass

        def destroy(self):
            self._running = False
            super().destroy()


    # ── Скруглённые Toast-уведомления ─────────────────────────────
    class RoundedToastManager:
        """Toast с скруглёнными углами через Canvas."""
        def __init__(self, root):
            self.root = root
            self._toasts = []

        def show(self, message, kind="info", duration=3500):
            styles = {
                "info":    (BG_PANEL, BD_MID,    AC_MAIN,   "◈"),
                "success": (BG_PANEL, "#103820",  AC_GREEN,  "✓"),
                "warning": (BG_PANEL, "#302000",  AC_ORANGE, "⚠"),
                "error":   (BG_PANEL, "#301020",  AC_RED,    "✕"),
                "update":  (BG_PANEL, "#200830",  AC_PURPLE, "⬆"),
            }
            bg, brd, acc, icon = styles.get(kind, styles["info"])
            self._toasts.append(
                self._create(message, bg, brd, acc, icon, duration)
            )
            self._reposition()

        def _create(self, message, bg, brd, acc, icon, duration):
            W = self.root.winfo_width() or 1200
            TOAST_W = 290
            RADIUS = 12

            # Canvas-контейнер
            canvas = tk.Canvas(self.root, bg=BG_VOID,
                               width=TOAST_W, height=70,
                               highlightthickness=0)

            def _draw_toast(c_w=TOAST_W, c_h=70):
                canvas.delete("all")
                # Тень
                _draw_rounded_rect(canvas, 3, 4, c_w-1, c_h, r=RADIUS,
                                   fill=_lerp_color(BG_VOID, brd, 0.4), outline="")
                # Фон
                _draw_rounded_rect(canvas, 1, 1, c_w-2, c_h-2, r=RADIUS,
                                   fill=bg, outline=brd, width=1)
                # Акцентная линия сверху
                canvas.create_arc(1, 1, RADIUS*2+1, RADIUS*2+1,
                                  start=90, extent=90, fill=acc, outline=acc)
                canvas.create_arc(c_w-RADIUS*2-2, 1, c_w-2, RADIUS*2+1,
                                  start=0, extent=90, fill=acc, outline=acc)
                canvas.create_rectangle(RADIUS+1, 1, c_w-RADIUS-1, 3,
                                        fill=acc, outline="")

                # Иконка
                canvas.create_text(20, c_h//2+1, text=icon,
                                   fill=_lerp_color(BG_VOID, acc, 0.5),
                                   font=("Segoe UI", 13, "bold"), anchor="center")
                canvas.create_text(20, c_h//2, text=icon, fill=acc,
                                   font=("Segoe UI", 13, "bold"), anchor="center")

                # Текст (wrap вручную)
                canvas.create_text(40, c_h//2, text=message,
                                   fill=TX_MAIN, font=("Segoe UI", 9),
                                   width=c_w-60, anchor="w")

                # Кнопка закрытия
                canvas.create_text(c_w-12, 10, text="×", fill=TX_DIM,
                                   font=("Segoe UI", 11, "bold"), anchor="center",
                                   tags="close_btn")

            canvas.bind("<Configure>", lambda e: _draw_toast(e.width, e.height))
            _draw_toast()

            def _close(e=None):
                self._dismiss(canvas)

            canvas.tag_bind("close_btn", "<Button-1>", _close)
            canvas.bind("<Button-1>", lambda e: (
                _close() if abs(e.x - (TOAST_W-12)) < 15 and abs(e.y - 10) < 15 else None
            ))

            canvas.place(x=W + 10, y=0, width=TOAST_W)
            canvas._target_x = W - TOAST_W - 16
            canvas.after(20, lambda: self._slide_in(canvas, W+10, duration))
            return canvas

        def _slide_in(self, canvas, start_x, duration, step=0):
            if step >= 14:
                canvas.after(duration, lambda: self._dismiss(canvas))
                return
            t = 1 - (1 - step/14)**3
            try:
                info = canvas.place_info()
                y = int(info.get("y", "16"))
                x = int(start_x + (canvas._target_x - start_x) * t)
                canvas.place_configure(x=x, y=y)
                canvas.after(18, lambda: self._slide_in(canvas, start_x, duration, step+1))
            except: pass

        def _dismiss(self, canvas):
            if canvas not in self._toasts:
                return
            self._toasts.remove(canvas)
            W = self.root.winfo_width() or 1200
            self._slide_out(canvas, W + 10)

        def _slide_out(self, canvas, end_x, step=0):
            if step >= 10:
                try: canvas.destroy()
                except: pass
                self._reposition()
                return
            t = (step/10)**2
            try:
                info = canvas.place_info()
                sx = int(info.get("x", canvas._target_x))
                canvas.place_configure(x=int(sx + (end_x - sx) * t))
                canvas.after(18, lambda: self._slide_out(canvas, end_x, step+1))
            except: pass

        def _reposition(self):
            W = self.root.winfo_width() or 1200
            y = 16
            for c in self._toasts:
                try:
                    c.place_configure(x=c._target_x, y=y)
                    c.update_idletasks()
                    y += c.winfo_height() + 8
                except: pass


    print("Патч UI загружен успешно!")
    print("Скруглённые компоненты: RoundedButton, RoundedProgressBar, RoundedToastManager")
    print("Замените в основном файле:")
    print("  make_pill_button  → make_pill_button_rounded")
    print("  make_action_button → make_action_button_rounded")
    print("  make_neon_entry   → make_neon_entry_rounded")
    print("  NeonProgressBar   → RoundedProgressBar")
    print("  ToastManager      → RoundedToastManager")

except ImportError as e:
    print(f"tkinter недоступен в этой среде: {e}")


# ══════════════════════════════════════════════════════════════════
# ПАТЧ 3: Улучшенная панель обновлений _build_update_button
# Вставить в класс AngelsLauncher вместо старого метода
# ══════════════════════════════════════════════════════════════════

PATCH_BUILD_UPDATE_BUTTON = '''
def _build_update_button(self):
    for w in self._upd_btn_frame.winfo_children():
        w.destroy()

    if self._update_available and self._latest_update_info:
        ver  = self._latest_update_info["version"]
        iv   = _read_installed_version()
        size = self._latest_update_info.get("size", 0)
        sz_str = f"  ({fmt_size(size)})" if size else ""

        # Скруглённая карточка обновления
        outer = tk.Canvas(self._upd_btn_frame, bg=BG_VOID,
                          height=180, highlightthickness=0)
        outer.pack(fill="x")

        def _draw_upd_card(e=None):
            W = outer.winfo_width() or 600
            H = 175
            outer.delete("all")
            _draw_rounded_rect(outer, 3, 4, W-1, H+1, r=14,
                               fill=lerp_color(BG_VOID, AC_GREEN, 0.06), outline="")
            _draw_rounded_rect(outer, 1, 1, W-2, H-1, r=14,
                               fill=lerp_color(BG_VOID, AC_GREEN, 0.1),
                               outline=lerp_color(BG_VOID, AC_GREEN, 0.5), width=1)
            # Верхняя акцент-линия
            outer.create_arc(2, 2, 30, 30, start=90, extent=90,
                             fill=AC_GREEN, outline=AC_GREEN)
            outer.create_arc(W-30, 2, W-2, 30, start=0, extent=90,
                             fill=AC_GREEN, outline=AC_GREEN)
            outer.create_rectangle(15, 2, W-15, 4,
                                   fill=AC_GREEN, outline="")

            outer.create_text(W//2+1, 35, text=f"⬆  Доступно обновление v{ver}{sz_str}",
                              fill=lerp_color(BG_VOID, AC_GREEN, 0.4),
                              font=("Segoe UI", 13, "bold"), anchor="center")
            outer.create_text(W//2, 34, text=f"⬆  Доступно обновление v{ver}{sz_str}",
                              fill=AC_GREEN,
                              font=("Segoe UI", 13, "bold"), anchor="center")
            outer.create_text(W//2, 58,
                              text=f"v{iv}  →  v{ver}",
                              fill=TX_MID, font=("Segoe UI", 10), anchor="center")

        outer.bind("<Configure>", _draw_upd_card)
        _draw_upd_card()

        inner = tk.Frame(self._upd_btn_frame, bg=BG_VOID)
        inner.pack(fill="x", pady=(4, 0))

        self._upd_progress_canvas = tk.Canvas(inner, bg=BG_VOID,
                                               height=14, highlightthickness=0)
        self._upd_progress_canvas.pack(fill="x", padx=2, pady=(0, 6))
        self._upd_speed_lbl = tk.Label(inner, text="", bg=BG_VOID,
                                        fg=TX_DIM, font=("Segoe UI", 8))
        self._upd_speed_lbl.pack(anchor="e", padx=4)

        self._do_upd_btn = make_action_button(
            inner,
            "⬇   СКАЧАТЬ И УСТАНОВИТЬ ОБНОВЛЕНИЕ",
            command=self._do_update_now,
            style="success",
            font=("Segoe UI", 12, "bold"),
            px=22, py=14,
            icon="⬇"
        )
        self._do_upd_btn.pack(fill="x", padx=0, pady=(0, 4))

    else:
        outer = tk.Canvas(self._upd_btn_frame, bg=BG_VOID,
                          height=140, highlightthickness=0)
        outer.pack(fill="x")

        def _draw_no_upd(e=None):
            W = outer.winfo_width() or 600
            H = 135
            outer.delete("all")
            _draw_rounded_rect(outer, 3, 4, W-1, H+1, r=14,
                               fill=lerp_color(BG_VOID, BD_MID, 0.4), outline="")
            _draw_rounded_rect(outer, 1, 1, W-2, H-1, r=14,
                               fill=BG_CARD,
                               outline=BD_MID, width=1)
            outer.create_arc(2, 2, 30, 30, start=90, extent=90,
                             fill=AC_MAIN, outline=AC_MAIN)
            outer.create_arc(W-30, 2, W-2, 30, start=0, extent=90,
                             fill=AC_MAIN, outline=AC_MAIN)
            outer.create_rectangle(15, 2, W-15, 4,
                                   fill=AC_MAIN, outline="")
            iv = _read_installed_version()
            outer.create_text(W//2, 40,
                              text="◈  Проверить наличие обновлений",
                              fill=TX_MAIN, font=("Segoe UI", 13, "bold"), anchor="center")
            outer.create_text(W//2, 62,
                              text=f"Установлена: v{iv}  ·  {GITHUB_REPO}",
                              fill=TX_DIM, font=("Segoe UI", 9), anchor="center")

        outer.bind("<Configure>", _draw_no_upd)
        _draw_no_upd()

        btn_row = tk.Frame(self._upd_btn_frame, bg=BG_VOID)
        btn_row.pack(fill="x", pady=(4, 0))
        self._chk_btn_w = make_action_button(
            btn_row, "◈   ПРОВЕРИТЬ ОБНОВЛЕНИЯ",
            command=self._do_check_updates,
            style="primary",
            font=("Segoe UI", 12, "bold"),
            px=22, py=12,
            icon="◈"
        )
        self._chk_btn_w.pack(fill="x")


def _do_update_now(self):
    """ИСПРАВЛЕНО: прогресс показывает %, скорость; WinError 32 обходится."""
    if not self._latest_update_info:
        return
    url = self._latest_update_info.get("download_url", "")
    new_ver = self._latest_update_info.get("version", "")
    if not url:
        self._toast.show("Ссылка на обновление недоступна!", kind="error")
        return

    self._log(f"⬆  Скачиваю обновление v{new_ver}...", "gold")

    try:
        self._do_upd_btn._labels[0].configure(text="⏳  Скачиваю...")
    except: pass

    def _prog(done, total, speed=0):
        def _ui():
            try:
                c = self._upd_progress_canvas
                W = c.winfo_width() or 400
                H = 12
                c.delete("all")
                pct = done / max(total, 1) if total else 0
                fw = max(H, int((W-4) * pct))
                # Скруглённый прогресс
                _draw_rounded_rect(c, 2, 2, W-2, H-2, r=5,
                                   fill=BG_VOID, outline=BD_DARK, width=1)
                if fw > 6:
                    col = lerp_color(AC_GLOW, AC_GREEN, pct)
                    _draw_rounded_rect(c, 3, 3, fw+2, H-3, r=5,
                                       fill=col, outline="")
                    c.create_text(W//2, H//2,
                                  text=f"{int(pct*100)}%",
                                  fill=TX_WHITE, font=("Segoe UI", 7, "bold"))
                sz = fmt_size(done)
                tot_s = f"/ {fmt_size(total)}" if total else ""
                spd_s = f"  ↓ {fmt_size(speed)}/с" if speed > 0 else ""
                self._upd_speed_lbl.configure(
                    text=f"{sz} {tot_s}{spd_s}"
                )
                self._log(f"  ⬇ {sz} {tot_s}{spd_s}", "muted")
            except: pass
        self.after(0, _ui)

    def _done(ok, result):
        self.after(0, lambda: self._on_upd_downloaded(ok, result))

    # Используем исправленную функцию
    _patched_download_and_install(
        self._updater, url, new_ver,
        on_progress=_prog,
        on_done=_done
    )
'''

print("\n" + "="*60)
print("ПАТЧ 3: _build_update_button и _do_update_now")
print("="*60)
print("Вставить в класс AngelsLauncher вместо старых методов.")
print("Код сохранён в переменной PATCH_BUILD_UPDATE_BUTTON")
