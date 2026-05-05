"""
╔══════════════════════════════════════════════════════════════╗
║          Angels Launcher — ПАТЧ v13.2 (FULL)                ║
║══════════════════════════════════════════════════════════════║
║  ИСПРАВЛЕНИЯ:                                                ║
║    ✓ WinError 32 — retry + robocopy fallback                 ║
║    ✓ Атомарная замена файла через уникальный temp            ║
║    ✓ Проверка целостности скачанного файла                   ║
║    ✓ Прогресс с %, скоростью и байтами                       ║
║                                                              ║
║  ВИЗУАЛЬНЫЕ УЛУЧШЕНИЯ v13.2:                                 ║
║    ✓ RoundedButton — Canvas-кнопки с анимацией               ║
║    ✓ RoundedProgressBar — пульсирующий прогресс-бар          ║
║    ✓ RoundedToastManager — уведомления со слайд-анимацией    ║
║    ✓ make_neon_entry_rounded — поле ввода с glow-фокусом     ║
║    ✓ GlowLabel — текст с неоновым свечением                  ║
║    ✓ AnimatedCard — карточка с hover-эффектом                ║
║                                                              ║
║  КАК ПРИМЕНИТЬ:                                              ║
║    В angels_launcher.py заменить:                            ║
║      make_pill_button    → make_pill_button_rounded          ║
║      make_action_button  → make_action_button_rounded        ║
║      make_neon_entry     → make_neon_entry_rounded           ║
║      NeonProgressBar     → RoundedProgressBar                ║
║      ToastManager        → RoundedToastManager               ║
╚══════════════════════════════════════════════════════════════╝
"""

import os, sys, shutil, time, platform, subprocess, threading, math, json
from pathlib import Path

# ══════════════════════════════════════════════════════════════════
#  ЦВЕТОВАЯ ПАЛИТРА
# ══════════════════════════════════════════════════════════════════

BG_VOID   = "#00040c"
BG_BASE   = "#000810"
BG_CARD   = "#040d1c"
BG_PANEL  = "#060f20"
BG_ITEM   = "#081428"
BG_HOVER  = "#0c1e38"
BD_DARK   = "#0c1e36"
BD_MID    = "#123060"
BD_GLOW   = "#1a4080"
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


# ══════════════════════════════════════════════════════════════════
#  ПАТЧ 1: AutoUpdater.download_and_install (WinError 32 fix)
# ══════════════════════════════════════════════════════════════════

def _patched_download_and_install(self, url, new_version, on_progress=None, on_done=None):
    """
    Исправлено:
    - WinError 32: уникальное имя temp-файла + retry loop
    - Windows: bat-скрипт с robocopy fallback
    - Двухэтапная загрузка: .dl → temp → final
    - Проверка размера файла после скачивания
    - on_progress(done, total, speed) — реальная скорость
    """
    def _do():
        new_path = None
        tmp_dl   = None
        try:
            current = Path(sys.executable)
            is_exe  = current.suffix.lower() == ".exe"
            ts      = str(int(time.time() * 1000))   # миллисекунды — больше уникальности

            if is_exe:
                new_path   = current.parent / f"_upd_{ts}.exe"
                final_path = current
            else:
                script     = Path(__file__).resolve()
                new_path   = script.parent / f"_upd_{ts}.py"
                final_path = script

            parent = new_path.parent

            # Чистим старые temp-файлы обновления
            for pattern in ("_upd_*.exe", "_upd_*.py",
                            "angels_launcher_update_*.exe",
                            "angels_launcher_update_*.py"):
                for old in parent.glob(pattern):
                    if old != new_path:
                        try: old.unlink()
                        except: pass

            # ── Скачивание ─────────────────────────────────────────
            import urllib.request
            tmp_dl = str(new_path) + ".dl"
            start_t = time.time()

            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": f"AngelsLauncher/{new_version}",
                    "Accept": "*/*",
                }
            )
            with urllib.request.urlopen(req, timeout=120) as r:
                total = int(r.headers.get("Content-Length", 0))
                done  = 0
                with open(tmp_dl, "wb") as f:
                    while True:
                        chunk = r.read(65536)
                        if not chunk:
                            break
                        f.write(chunk)
                        done += len(chunk)
                        elapsed = max(0.01, time.time() - start_t)
                        speed   = done / elapsed
                        if on_progress:
                            on_progress(done, total, speed)

            # ── Проверка целостности ───────────────────────────────
            dl_size = Path(tmp_dl).stat().st_size
            if dl_size < 50_000:
                raise RuntimeError(
                    f"Файл скачался некорректно ({dl_size:,} байт). "
                    "Возможно, URL неверный или GitHub вернул HTML вместо EXE."
                )

            # ── .dl → temp ─────────────────────────────────────────
            try:
                shutil.move(tmp_dl, str(new_path))
            except Exception:
                shutil.copy2(tmp_dl, str(new_path))
                try: Path(tmp_dl).unlink()
                except: pass
            tmp_dl = None   # уже перенесён, не чистить в except

            # ── version.json ───────────────────────────────────────
            try:
                (new_path.parent / "angels_launcher_version.json").write_text(
                    json.dumps({
                        "version":    new_version,
                        "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                    }, indent=2),
                    encoding="utf-8"
                )
            except: pass

            current_pid = os.getpid()

            if platform.system() == "Windows":
                # ── BAT: move + robocopy fallback ──────────────────
                bat_path = parent / f"_angels_upd_{int(time.time())}.bat"
                # Экранируем пути для bat
                src  = str(new_path)
                dst  = str(final_path)
                dstp = str(final_path.parent)
                dstf = final_path.name
                srcn = new_path.name

                bat = (
                    "@echo off\n"
                    "chcp 65001 >nul 2>&1\n"
                    "echo [Angels Updater] Waiting for launcher to close...\n"
                    f"timeout /t 3 /nobreak >nul\n"
                    f"taskkill /PID {current_pid} /F >nul 2>&1\n"
                    f"timeout /t 2 /nobreak >nul\n"
                    "\n"
                    ":retry\n"
                    f"move /y \"{src}\" \"{dst}\" >nul 2>&1\n"
                    "if %errorlevel%==0 goto launch\n"
                    "\n"
                    "echo [Angels Updater] move failed, trying robocopy...\n"
                    f"robocopy \"{parent}\" \"{dstp}\" \"{srcn}\" /MOV /R:5 /W:1 >nul 2>&1\n"
                    f"if exist \"{dstp}\\{srcn}\" (\n"
                    f"    rename \"{dstp}\\{srcn}\" \"{dstf}\" >nul 2>&1\n"
                    ")\n"
                    "\n"
                    ":launch\n"
                    f"if exist \"{dst}\" start \"\" \"{dst}\"\n"
                    "del \"%~f0\"\n"
                )
                bat_path.write_text(bat, encoding="cp866")
                if on_done:
                    on_done(True, str(bat_path))

            else:
                # ── Linux / macOS ──────────────────────────────────
                import stat as _stat
                for attempt in range(6):
                    try:
                        shutil.move(str(new_path), str(final_path))
                        break
                    except PermissionError:
                        if attempt < 5:
                            time.sleep(0.5)
                        else:
                            raise
                try:
                    st = os.stat(final_path)
                    os.chmod(final_path,
                             st.st_mode | _stat.S_IEXEC | _stat.S_IXGRP | _stat.S_IXOTH)
                except: pass
                if on_done:
                    on_done(True, str(final_path))

        except Exception as ex:
            # Чистим мусор при ошибке
            for p in filter(None, [
                new_path,
                Path(tmp_dl) if tmp_dl else None,
            ]):
                try:
                    if p and Path(p).exists():
                        Path(p).unlink()
                except: pass
            if on_done:
                on_done(False, str(ex))

    threading.Thread(target=_do, daemon=True).start()


# ══════════════════════════════════════════════════════════════════
#  ПАТЧ 2: UI-компоненты — скруглённые Canvas-виджеты
# ══════════════════════════════════════════════════════════════════

try:
    import tkinter as tk
    import tkinter.font as tkfont
    from tkinter import ttk

    # ── Цветовые утилиты ──────────────────────────────────────────

    def _hex_rgb(h):
        h = h.lstrip("#")
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

    def _rgb_hex(r, g, b):
        return f"#{int(r):02x}{int(g):02x}{int(b):02x}"

    def _lerp_color(c1, c2, t):
        t = max(0.0, min(1.0, t))
        r1, g1, b1 = _hex_rgb(c1)
        r2, g2, b2 = _hex_rgb(c2)
        return _rgb_hex(r1 + (r2-r1)*t, g1 + (g2-g1)*t, b1 + (b2-b1)*t)

    # Псевдоним для совместимости с основным файлом (lerp_color)
    lerp_color = _lerp_color


    # ── Базовые рисовальщики ──────────────────────────────────────

    def _draw_rounded_rect(canvas, x1, y1, x2, y2, r=8, **kw):
        """Скруглённый прямоугольник через polygon + smooth."""
        r = max(1, min(r, (x2-x1)//2, (y2-y1)//2))
        pts = [
            x1+r, y1,   x2-r, y1,
            x2,   y1,   x2,   y1+r,
            x2,   y2-r, x2,   y2,
            x2-r, y2,   x1+r, y2,
            x1,   y2,   x1,   y2-r,
            x1,   y1+r, x1,   y1,
        ]
        return canvas.create_polygon(pts, smooth=True, **kw)

    def _draw_glow_rect(canvas, x1, y1, x2, y2, r=8, color=AC_MAIN, layers=3):
        """Мягкое свечение вокруг прямоугольника."""
        for i in range(layers, 0, -1):
            t = i / (layers + 1)
            glow = _lerp_color(BG_VOID, color, t * 0.25)
            d = (layers - i + 1) * 2
            _draw_rounded_rect(canvas, x1-d, y1-d, x2+d, y2+d,
                               r=r+d, fill=glow, outline="")


    # ══════════════════════════════════════════════════════════════
    #  RoundedButton — анимированная Canvas-кнопка
    # ══════════════════════════════════════════════════════════════

    class RoundedButton(tk.Canvas):
        """
        Полностью скруглённая кнопка.
        Hover-анимация, эффект нажатия, опциональный accent-stripe.
        Совместима с make_pill_button/make_action_button API.
        """

        def __init__(self, parent, text, command=None,
                     bg=BG_ITEM, fg=AC_MAIN,
                     hover_bg=BG_HOVER, hover_fg=TX_WHITE,
                     font=("Segoe UI", 10, "bold"),
                     radius=10, px=18, py=9,
                     icon=None, accent=None,
                     width=None, height=None,
                     **kw):

            # Состояние
            self._btn_bg    = bg
            self._btn_fg    = fg
            self._hover_bg  = hover_bg
            self._hover_fg  = hover_fg
            self._radius    = radius
            self._command   = command
            self._text      = text
            self._icon      = icon
            self._font      = font
            self._px        = px
            self._py        = py
            self._accent    = accent
            self._hovered   = False
            self._pressed   = False
            self._cur_bg    = bg
            self._cur_fg    = fg
            self._anim_id   = None

            # Замер размера по тексту
            try:
                fnt = tkfont.Font(family=font[0], size=abs(font[1]),
                                  weight=font[2] if len(font) > 2 else "normal")
                label = ((icon + "  ") if icon else "") + text
                tw = fnt.measure(label)
                th = fnt.metrics("linespace")
            except Exception:
                tw, th = 120, 20

            _w = width  or (tw + px * 2 + (6 if accent else 0))
            _h = height or (th + py * 2)

            super().__init__(parent,
                             bg=BG_VOID, width=_w, height=_h,
                             highlightthickness=0, cursor="hand2", **kw)
            self._w = _w
            self._h = _h

            self.bind("<Configure>",      self._redraw)
            self.bind("<Enter>",          self._on_enter)
            self.bind("<Leave>",          self._on_leave)
            self.bind("<Button-1>",       self._on_press)
            self.bind("<ButtonRelease-1>",self._on_release)

            # Совместимость со старым API
            self._labels    = [_LabelStub()]
            self._inner     = self
            self._row       = self
            self._active_bar = None

            self._redraw()

        # ── Обработчики ──────────────────────────────────────────

        def _on_enter(self, _=None):
            self._hovered = True
            self._start_anim(self._hover_bg, self._hover_fg)

        def _on_leave(self, _=None):
            self._hovered = False
            self._start_anim(self._btn_bg, self._btn_fg)

        def _on_press(self, _=None):
            self._pressed = True
            self._redraw()
            if self._command:
                self.after(80, self._safe_command)

        def _safe_command(self):
            try:
                if self._command:
                    self._command()
            except Exception:
                pass

        def _on_release(self, _=None):
            self._pressed = False
            self._redraw()

        # ── Анимация ─────────────────────────────────────────────

        def _start_anim(self, target_bg, target_fg):
            if self._anim_id:
                try: self.after_cancel(self._anim_id)
                except: pass
            self._anim_step(target_bg, target_fg, 0, 8)

        def _anim_step(self, tbg, tfg, step, steps):
            if step > steps:
                self._cur_bg = tbg
                self._cur_fg = tfg
                self._redraw()
                return
            t = step / steps
            self._cur_bg = _lerp_color(self._cur_bg, tbg, t)
            self._cur_fg = _lerp_color(self._cur_fg, tfg, t)
            self._redraw()
            self._anim_id = self.after(
                14, lambda: self._anim_step(tbg, tfg, step+1, steps)
            )

        # ── Отрисовка ────────────────────────────────────────────

        def _redraw(self, _=None):
            W = self.winfo_width()  or self._w
            H = self.winfo_height() or self._h
            self.delete("all")

            bg = self._cur_bg
            fg = self._cur_fg
            r  = self._radius

            # Нажатие — затемняем
            if self._pressed:
                bg = _lerp_color(bg, BG_VOID, 0.35)

            # Тень
            shadow = _lerp_color(BG_VOID, bg, 0.2)
            _draw_rounded_rect(self, 2, 3, W-1, H-1, r=r,
                               fill=shadow, outline="")

            # Glow при hover
            if self._hovered and not self._pressed:
                _draw_glow_rect(self, 1, 1, W-2, H-2, r=r,
                                color=fg, layers=2)

            # Основной фон
            _draw_rounded_rect(self, 1, 1, W-2, H-2, r=r,
                               fill=bg, outline="")

            # Граница
            border = _lerp_color(bg, fg, 0.3 if self._hovered else 0.18)
            _draw_rounded_rect(self, 1, 1, W-2, H-2, r=r,
                               fill="", outline=border, width=1)

            # Accent-полоска слева
            if self._accent:
                ar = min(r, 6)
                self.create_rectangle(1, ar, 4, H-ar,
                                      fill=self._accent, outline="")
                self.create_oval(1, 1, 7, ar*2,
                                 fill=self._accent, outline="")
                self.create_oval(1, H-ar*2, 7, H-1,
                                 fill=self._accent, outline="")

            # Блик сверху (тонкая светлая полоска)
            if not self._pressed:
                shine = _lerp_color(bg, TX_WHITE, 0.06)
                _draw_rounded_rect(self, 2, 2, W-3, H//2, r=r,
                                   fill=shine, outline="")

            # Текст
            label = ((self._icon + "  ") if self._icon else "") + self._text
            cx = W // 2
            cy = H // 2

            # Тень текста
            self.create_text(cx+1, cy+2, text=label,
                             fill=_lerp_color(BG_VOID, bg, 0.4),
                             font=self._font, anchor="center")
            # Основной текст
            self.create_text(cx, cy, text=label,
                             fill=fg, font=self._font, anchor="center")

        # ── Совместимость с API ──────────────────────────────────

        def configure(self, **kw):
            changed = False
            if "bg" in kw:
                self._btn_bg = kw.pop("bg")
                self._cur_bg = self._btn_bg
                changed = True
            if "text" in kw:
                self._text = kw.pop("text")
                changed = True
            super().configure(**kw)
            if changed:
                self._redraw()

        config = configure

        def _set_active(self, active, accent_col=None):
            if active and accent_col:
                ab = _lerp_color(BG_VOID, accent_col, 0.18)
                self._cur_bg   = ab
                self._btn_bg   = ab
                self._cur_fg   = accent_col
                self._accent   = accent_col
            else:
                self._cur_bg   = BG_CARD
                self._btn_bg   = BG_CARD
                self._cur_fg   = self._btn_fg
                self._accent   = None
            self._redraw()

        @property
        def _normal_fg(self): return self._btn_fg
        @_normal_fg.setter
        def _normal_fg(self, v): self._btn_fg = v


    # ── Заглушка для совместимости ────────────────────────────────

    class _LabelStub:
        def configure(self, **kw): pass
        def config(self, **kw):    pass
        def cget(self, k):         return ""


    # ══════════════════════════════════════════════════════════════
    #  Фабричные функции (замены для старых make_* функций)
    # ══════════════════════════════════════════════════════════════

    def make_pill_button_rounded(parent, text, command=None,
                                 bg=BG_ITEM, fg=AC_MAIN,
                                 hover_bg=BG_HOVER, hover_fg=TX_WHITE,
                                 font=("Segoe UI", 10, "bold"),
                                 px=18, py=8,
                                 icon=None, accent_left=None,
                                 width=None, **kw):
        """Замена make_pill_button — скруглённая кнопка навигации."""
        btn = RoundedButton(
            parent, text, command=command,
            bg=bg, fg=fg,
            hover_bg=hover_bg, hover_fg=hover_fg,
            font=font, radius=12,
            px=px, py=py,
            icon=icon, accent=accent_left,
            width=width, **kw
        )
        btn._bg        = bg
        btn._fg        = fg
        btn._hover_bg  = hover_bg
        btn._hover_fg  = hover_fg
        return btn


    def make_action_button_rounded(parent, text, command=None,
                                   style="primary",
                                   font=("Segoe UI", 10, "bold"),
                                   px=20, py=10, icon=None, **kw):
        """Замена make_action_button — кнопка действия со стилем."""
        _styles = {
            "primary": (BG_ITEM,   AC_MAIN,   BG_HOVER,  "#00e8ff"),
            "danger":  (BG_ITEM,   AC_RED,    "#1a0010",  "#ff6688"),
            "success": (BG_ITEM,   AC_GREEN,  "#001a10",  "#44ffaa"),
            "warning": (BG_ITEM,   AC_ORANGE, "#1a0800",  "#ffaa55"),
            "ghost":   (BG_VOID,   TX_MID,    BG_HOVER,   TX_WHITE),
            "admin":   (ADM_BG,    ADM_ACC,   ADM_PANEL,  "#ff44ee"),
        }
        nbg, nfg, hbg, hfg = _styles.get(style, _styles["ghost"])

        btn = RoundedButton(
            parent, text, command=command,
            bg=nbg, fg=nfg,
            hover_bg=hbg, hover_fg=hfg,
            font=font, radius=10,
            px=px, py=py,
            icon=icon, **kw
        )
        return btn

    # Псевдонимы для обратной совместимости (если старый код ещё импортирует старые имена)
    make_pill_button   = make_pill_button_rounded
    make_action_button = make_action_button_rounded


    # ══════════════════════════════════════════════════════════════
    #  make_neon_entry_rounded — поле ввода с glow-эффектом
    # ══════════════════════════════════════════════════════════════

    def make_neon_entry_rounded(parent, textvariable, show="",
                                placeholder="", width=None,
                                icon=None, bg=BG_ITEM,
                                fg=TX_MAIN, accent=AC_MAIN):
        """
        Поле ввода со скруглёнными углами, glow при фокусе, placeholder.
        Возвращает Frame с методом .get_value() и атрибутом ._entry.
        """
        RADIUS = 10
        outer  = tk.Frame(parent, bg=BG_VOID)

        bg_canvas = tk.Canvas(outer, bg=BG_VOID, highlightthickness=0, height=44)
        bg_canvas.pack(fill="x", expand=True)

        def _draw(focused=False):
            bg_canvas.delete("all")
            W  = bg_canvas.winfo_width() or 300
            H  = 42
            bc = accent if focused else BD_DARK
            fc = BG_HOVER if focused else bg

            # Glow при фокусе
            if focused:
                for d in range(4, 0, -1):
                    gc = _lerp_color(BG_VOID, accent, d * 0.06)
                    _draw_rounded_rect(bg_canvas, 0-d, 0-d, W+d, H+d,
                                       r=RADIUS+d, fill=gc, outline="")

            # Тень
            _draw_rounded_rect(bg_canvas, 2, 3, W-1, H+1, r=RADIUS,
                               fill=_lerp_color(BG_VOID, fc, 0.25), outline="")
            # Фон + граница
            _draw_rounded_rect(bg_canvas, 1, 1, W-2, H-1, r=RADIUS,
                               fill=fc, outline=bc, width=1)

        bg_canvas.bind("<Configure>", lambda e: _draw())

        # Внутренний frame с виджетами
        inner = tk.Frame(outer, bg=bg)
        inner.place(x=8, y=7, relwidth=1.0, width=-16, height=28)

        if icon:
            icon_lbl = tk.Label(inner, text=icon, bg=bg, fg=TX_DIM,
                                font=("Segoe UI", 11))
            icon_lbl.pack(side="left", padx=(4, 2))
        else:
            icon_lbl = None

        entry_kw = dict(
            textvariable=textvariable, bg=bg, fg=fg,
            insertbackground=accent, relief="flat",
            font=("Segoe UI", 10), bd=0,
        )
        if width:  entry_kw["width"] = width
        if show:   entry_kw["show"]  = show

        ent = tk.Entry(inner, **entry_kw)
        ent.pack(side="left", fill="x", expand=True, ipady=2)

        # Placeholder
        _ph = [False]
        if placeholder:
            ent.insert(0, placeholder)
            ent.configure(fg=TX_DIM)
            _ph[0] = True

        def _focus_in(_):
            if _ph[0]:
                ent.delete(0, "end")
                if show: ent.configure(show=show)
                ent.configure(fg=fg)
                _ph[0] = False
            inner.configure(bg=BG_HOVER)
            ent.configure(bg=BG_HOVER)
            if icon_lbl:
                icon_lbl.configure(bg=BG_HOVER, fg=accent)
            _draw(focused=True)

        def _focus_out(_):
            if not textvariable.get() and placeholder:
                ent.configure(show="")
                ent.delete(0, "end")
                ent.insert(0, placeholder)
                ent.configure(fg=TX_DIM)
                _ph[0] = True
            inner.configure(bg=bg)
            ent.configure(bg=bg)
            if icon_lbl:
                icon_lbl.configure(bg=bg, fg=TX_DIM)
            _draw(focused=False)

        ent.bind("<FocusIn>",  _focus_in)
        ent.bind("<FocusOut>", _focus_out)

        def get_value():
            return "" if _ph[0] else ent.get().strip()

        outer.get_value = get_value
        outer._entry    = ent
        return outer

    # Псевдоним
    make_neon_entry = make_neon_entry_rounded


    # ══════════════════════════════════════════════════════════════
    #  RoundedProgressBar — пульсирующий прогресс-бар с %
    # ══════════════════════════════════════════════════════════════

    class RoundedProgressBar(tk.Canvas):
        def __init__(self, parent, height=10, fg=AC_MAIN, radius=5, **kw):
            super().__init__(parent, bg=BG_VOID,
                             height=height + 8,
                             highlightthickness=0, **kw)
            self._fg      = fg
            self._radius  = radius
            self._val     = 0.0
            self._phase   = 0.0
            self._running = True
            self.bind("<Configure>", self._redraw)
            self._tick()

        def set(self, val):
            self._val = max(0.0, min(1.0, val))
            self._redraw()

        def get(self):
            return self._val

        def _redraw(self, _=None):
            W = self.winfo_width()  or 400
            H = self.winfo_height() or 18
            self.delete("all")
            r = self._radius

            # Трек
            _draw_rounded_rect(self, 2, 3, W-2, H-3, r=r,
                               fill=BG_VOID, outline=BD_DARK, width=1)

            if self._val <= 0:
                return

            fw = max(r*2+2, int((W-6) * self._val) + 3)

            # Цвет по прогрессу
            if self._val < 0.4:
                col = _lerp_color(AC_GLOW, AC_MAIN, self._val / 0.4)
            elif self._val < 0.75:
                col = AC_MAIN
            else:
                col = _lerp_color(AC_MAIN, AC_MINT, (self._val - 0.75) / 0.25)

            glow_t = (math.sin(self._phase) + 1) / 2

            # Glow слой
            glow_col = _lerp_color(BG_VOID, col, 0.12 + glow_t * 0.08)
            _draw_rounded_rect(self, 1, 1, fw+4, H-1, r=r,
                               fill=glow_col, outline="")

            # Основная полоса
            _draw_rounded_rect(self, 3, 4, fw, H-4, r=r,
                               fill=col, outline="")

            # Блик (shimmer)
            shimmer = _lerp_color(col, TX_WHITE, 0.3 + glow_t * 0.2)
            mid = (H-4+4) // 2
            if fw > 6 and mid > 4:
                self.create_rectangle(4, 4, fw-2, mid,
                                      fill=shimmer, outline="")

            # Процент
            if self._val > 0.04:
                self.create_text(W//2 + 1, H//2 + 1,
                                 text=f"{int(self._val*100)}%",
                                 fill=_lerp_color(BG_VOID, TX_WHITE, 0.4),
                                 font=("Segoe UI", 7, "bold"))
                self.create_text(W//2, H//2,
                                 text=f"{int(self._val*100)}%",
                                 fill=TX_WHITE,
                                 font=("Segoe UI", 7, "bold"))

        def _tick(self):
            if not self._running:
                return
            try:
                self._phase += 0.055
                self._redraw()
                self.after(33, self._tick)
            except Exception:
                pass

        def destroy(self):
            self._running = False
            super().destroy()

    # Псевдоним
    NeonProgressBar = RoundedProgressBar


    # ══════════════════════════════════════════════════════════════
    #  GlowLabel — tk.Label с неоновым свечением (через Canvas)
    # ══════════════════════════════════════════════════════════════

    class GlowLabel(tk.Canvas):
        """Текстовый лейбл с анимированным неоновым свечением."""

        def __init__(self, parent, text, fg=AC_MAIN, bg=BG_VOID,
                     font=("Segoe UI", 12, "bold"), glow=True, **kw):
            try:
                fnt  = tkfont.Font(family=font[0], size=abs(font[1]),
                                   weight=font[2] if len(font) > 2 else "normal")
                tw   = fnt.measure(text) + 20
                th   = fnt.metrics("linespace") + 12
            except Exception:
                tw, th = 160, 30

            super().__init__(parent, bg=bg, width=tw, height=th,
                             highlightthickness=0, **kw)
            self._text   = text
            self._fg     = fg
            self._bg     = bg
            self._font   = font
            self._glow   = glow
            self._phase  = 0.0
            self._run    = True
            self.bind("<Configure>", self._redraw)
            if glow:
                self._tick()
            else:
                self._redraw()

        def _redraw(self, _=None):
            W = self.winfo_width()  or 160
            H = self.winfo_height() or 30
            self.delete("all")
            cx, cy = W//2, H//2

            if self._glow:
                t = (math.sin(self._phase) + 1) / 2
                for d in range(4, 0, -1):
                    gc = _lerp_color(self._bg, self._fg, (0.08 + t*0.06) * d/4)
                    self.create_text(cx, cy, text=self._text,
                                     fill=gc, font=self._font)

            self.create_text(cx+1, cy+1, text=self._text,
                             fill=_lerp_color(BG_VOID, self._fg, 0.3),
                             font=self._font)
            self.create_text(cx, cy, text=self._text,
                             fill=self._fg, font=self._font)

        def _tick(self):
            if not self._run:
                return
            try:
                self._phase += 0.04
                self._redraw()
                self.after(40, self._tick)
            except Exception:
                pass

        def set_text(self, t):
            self._text = t
            self._redraw()

        def destroy(self):
            self._run = False
            super().destroy()


    # ══════════════════════════════════════════════════════════════
    #  AnimatedCard — карточка с hover-подсветкой
    # ══════════════════════════════════════════════════════════════

    class AnimatedCard(tk.Canvas):
        """
        Скруглённая карточка-контейнер с hover-анимацией.
        Дочерние виджеты добавляются через .inner (tk.Frame).
        """

        def __init__(self, parent, bg=BG_CARD, accent=AC_MAIN,
                     radius=14, border=True, **kw):
            height = kw.pop("height", 100)
            super().__init__(parent, bg=BG_VOID,
                             height=height, highlightthickness=0, **kw)
            self._cbg     = bg
            self._accent  = accent
            self._radius  = radius
            self._border  = border
            self._hovered = False
            self._phase   = 0.0
            self._run     = True

            # Внутренний frame для дочерних виджетов
            self.inner = tk.Frame(self, bg=bg)
            self.inner.place(x=6, y=6, relwidth=1.0, width=-12,
                             relheight=1.0, height=-12)

            self.bind("<Configure>", self._redraw)
            self.bind("<Enter>",     self._on_enter)
            self.bind("<Leave>",     self._on_leave)
            self._tick()

        def _on_enter(self, _=None):
            self._hovered = True

        def _on_leave(self, _=None):
            self._hovered = False

        def _redraw(self, _=None):
            W = self.winfo_width()  or 400
            H = self.winfo_height() or 100
            self.delete("all")
            r = self._radius

            t = (math.sin(self._phase) + 1) / 2
            glow_str = (0.08 + t * 0.06) if self._hovered else (0.02 + t * 0.02)

            # Тень
            _draw_rounded_rect(self, 3, 4, W-1, H-1, r=r,
                               fill=_lerp_color(BG_VOID, self._accent, 0.04),
                               outline="")

            # Glow
            if self._hovered or glow_str > 0.02:
                for d in range(3, 0, -1):
                    gc = _lerp_color(BG_VOID, self._accent, glow_str * d/3)
                    _draw_rounded_rect(self, 0, 0, W, H, r=r+d,
                                       fill=gc, outline="")

            # Фон
            _draw_rounded_rect(self, 1, 1, W-2, H-2, r=r,
                               fill=self._cbg, outline="")

            # Граница
            if self._border:
                bc = _lerp_color(BD_DARK, self._accent,
                                 0.35 if self._hovered else 0.12)
                _draw_rounded_rect(self, 1, 1, W-2, H-2, r=r,
                                   fill="", outline=bc, width=1)

            # Верхняя accent-линия
            ax = min(r, 14)
            self.create_arc(2, 2, ax*2+2, ax*2+2,
                            start=90, extent=90,
                            fill=self._accent, outline=self._accent)
            self.create_arc(W-ax*2-2, 2, W-2, ax*2+2,
                            start=0, extent=90,
                            fill=self._accent, outline=self._accent)
            self.create_rectangle(ax+2, 2, W-ax-2, 4,
                                  fill=self._accent, outline="")

            self.inner.lift()

        def _tick(self):
            if not self._run:
                return
            try:
                self._phase += 0.03
                self._redraw()
                self.after(40, self._tick)
            except Exception:
                pass

        def destroy(self):
            self._run = False
            super().destroy()


    # ══════════════════════════════════════════════════════════════
    #  RoundedToastManager — уведомления со слайд-анимацией
    # ══════════════════════════════════════════════════════════════

    class RoundedToastManager:
        """Toast-уведомления с анимацией появления/исчезновения."""

        STYLES = {
            "info":    (BG_PANEL, BD_MID,     AC_MAIN,   "◈"),
            "success": (BG_PANEL, "#0a2818",  AC_GREEN,  "✓"),
            "warning": (BG_PANEL, "#281800",  AC_ORANGE, "⚠"),
            "error":   (BG_PANEL, "#280010",  AC_RED,    "✕"),
            "update":  (BG_PANEL, "#180828",  AC_PURPLE, "⬆"),
            "admin":   (ADM_BG,   ADM_MUTE,   ADM_ACC,   "★"),
        }

        def __init__(self, root):
            self.root    = root
            self._toasts = []

        def show(self, message, kind="info", duration=3500):
            bg, brd, acc, icon = self.STYLES.get(kind, self.STYLES["info"])
            t = self._make_toast(message, bg, brd, acc, icon, duration)
            self._toasts.append(t)
            self._restack()

        def _make_toast(self, msg, bg, brd, acc, icon, dur):
            W  = self.root.winfo_width() or 1200
            TW = 300
            R  = 12

            c = tk.Canvas(self.root, bg=BG_VOID,
                          width=TW, height=72, highlightthickness=0)

            def _draw(cw=TW, ch=72):
                c.delete("all")
                # Тень
                _draw_rounded_rect(c, 3, 5, cw-1, ch+1, r=R,
                                   fill=_lerp_color(BG_VOID, brd, 0.5), outline="")
                # Фон
                _draw_rounded_rect(c, 1, 1, cw-2, ch-2, r=R,
                                   fill=bg, outline=brd, width=1)
                # Верхняя accent-линия
                c.create_arc(2, 2, R*2+2, R*2+2,
                             start=90, extent=90, fill=acc, outline=acc)
                c.create_arc(cw-R*2-2, 2, cw-2, R*2+2,
                             start=0, extent=90, fill=acc, outline=acc)
                c.create_rectangle(R+2, 2, cw-R-2, 4, fill=acc, outline="")
                # Иконка — тень + текст
                c.create_text(22, ch//2+1, text=icon,
                              fill=_lerp_color(BG_VOID, acc, 0.4),
                              font=("Segoe UI", 13, "bold"), anchor="center")
                c.create_text(22, ch//2, text=icon, fill=acc,
                              font=("Segoe UI", 13, "bold"), anchor="center")
                # Сообщение
                c.create_text(42, ch//2, text=msg,
                              fill=TX_MAIN, font=("Segoe UI", 9),
                              width=cw-60, anchor="w")
                # Кнопка ×
                c.create_text(cw-11, 11, text="×",
                              fill=TX_DIM, font=("Segoe UI", 11, "bold"),
                              anchor="center", tags="close")

            c.bind("<Configure>", lambda e: _draw(e.width, e.height))
            _draw()

            def _close(_=None):
                self._dismiss(c)

            c.tag_bind("close", "<Button-1>", _close)
            c.bind("<Button-1>", lambda e: (
                _close() if abs(e.x-(TW-11)) < 14 and abs(e.y-11) < 14 else None
            ))

            c._tx = W - TW - 16
            c.place(x=W+10, y=16, width=TW)
            c.after(16, lambda: self._slide_in(c, W+10, dur))
            return c

        def _slide_in(self, c, sx, dur, step=0, steps=12):
            if step >= steps:
                c.after(dur, lambda: self._dismiss(c))
                return
            t = 1 - (1 - step/steps)**3
            try:
                info = c.place_info()
                y = int(info.get("y", 16))
                x = int(sx + (c._tx - sx) * t)
                c.place_configure(x=x, y=y)
                c.after(15, lambda: self._slide_in(c, sx, dur, step+1, steps))
            except Exception:
                pass

        def _dismiss(self, c):
            if c not in self._toasts:
                return
            self._toasts.remove(c)
            W = self.root.winfo_width() or 1200
            self._slide_out(c, W+10)

        def _slide_out(self, c, ex, step=0, steps=10):
            if step >= steps:
                try: c.destroy()
                except: pass
                self._restack()
                return
            t = (step/steps)**2
            try:
                info = c.place_info()
                sx = int(info.get("x", c._tx))
                c.place_configure(x=int(sx + (ex-sx)*t))
                c.after(15, lambda: self._slide_out(c, ex, step+1, steps))
            except Exception:
                pass

        def _restack(self):
            W = self.root.winfo_width() or 1200
            y = 16
            for c in list(self._toasts):
                try:
                    c.place_configure(x=c._tx, y=y)
                    c.update_idletasks()
                    y += (c.winfo_height() or 72) + 8
                except Exception:
                    pass

    # Псевдоним
    ToastManager = RoundedToastManager


    # ══════════════════════════════════════════════════════════════
    #  ПАТЧ 3: _build_update_button + _do_update_now
    #  Вставить в класс AngelsLauncher вместо старых методов
    # ══════════════════════════════════════════════════════════════

    UPDATE_PANEL_PATCH = '''
    # ── Вставить в класс AngelsLauncher ─────────────────────────

    def _build_update_button(self):
        for w in self._upd_btn_frame.winfo_children():
            w.destroy()

        if self._update_available and self._latest_update_info:
            ver    = self._latest_update_info["version"]
            iv     = _read_installed_version()
            size   = self._latest_update_info.get("size", 0)
            sz_str = f"  ({fmt_size(size)})" if size else ""

            # Карточка обновления
            card_canvas = tk.Canvas(self._upd_btn_frame, bg=BG_VOID,
                                    height=100, highlightthickness=0)
            card_canvas.pack(fill="x", padx=0, pady=(0, 6))

            def _draw_card(_=None):
                W = card_canvas.winfo_width() or 600
                H = 96
                card_canvas.delete("all")
                _draw_rounded_rect(card_canvas, 3, 4, W-1, H+1, r=14,
                                   fill=_lerp_color(BG_VOID, AC_GREEN, 0.05), outline="")
                _draw_rounded_rect(card_canvas, 1, 1, W-2, H-1, r=14,
                                   fill=_lerp_color(BG_VOID, AC_GREEN, 0.10),
                                   outline=_lerp_color(BG_VOID, AC_GREEN, 0.45), width=1)
                ax = 14
                card_canvas.create_arc(2, 2, ax*2+2, ax*2+2,
                                       start=90, extent=90, fill=AC_GREEN, outline=AC_GREEN)
                card_canvas.create_arc(W-ax*2-2, 2, W-2, ax*2+2,
                                       start=0, extent=90, fill=AC_GREEN, outline=AC_GREEN)
                card_canvas.create_rectangle(ax+2, 2, W-ax-2, 4,
                                             fill=AC_GREEN, outline="")
                card_canvas.create_text(W//2+1, 36,
                    text=f"⬆  Доступно обновление  v{ver}{sz_str}",
                    fill=_lerp_color(BG_VOID, AC_GREEN, 0.4),
                    font=("Segoe UI", 13, "bold"), anchor="center")
                card_canvas.create_text(W//2, 35,
                    text=f"⬆  Доступно обновление  v{ver}{sz_str}",
                    fill=AC_GREEN,
                    font=("Segoe UI", 13, "bold"), anchor="center")
                card_canvas.create_text(W//2, 58,
                    text=f"Установлена:  v{iv}   →   v{ver}",
                    fill=TX_MID, font=("Segoe UI", 10), anchor="center")

            card_canvas.bind("<Configure>", _draw_card)
            _draw_card()

            prog_row = tk.Frame(self._upd_btn_frame, bg=BG_VOID)
            prog_row.pack(fill="x")

            self._upd_prog_bar = RoundedProgressBar(prog_row, height=12, fg=AC_GREEN)
            self._upd_prog_bar.pack(fill="x", padx=2, pady=(0, 4))

            self._upd_speed_lbl = tk.Label(prog_row, text="", bg=BG_VOID,
                                           fg=TX_DIM, font=("Segoe UI", 8))
            self._upd_speed_lbl.pack(anchor="e", padx=6)

            self._do_upd_btn = make_action_button_rounded(
                self._upd_btn_frame,
                "⬇   СКАЧАТЬ И УСТАНОВИТЬ ОБНОВЛЕНИЕ",
                command=self._do_update_now,
                style="success",
                font=("Segoe UI", 12, "bold"),
                px=22, py=14,
            )
            self._do_upd_btn.pack(fill="x", padx=0, pady=(4, 0))

        else:
            card_canvas = tk.Canvas(self._upd_btn_frame, bg=BG_VOID,
                                    height=90, highlightthickness=0)
            card_canvas.pack(fill="x", padx=0, pady=(0, 6))

            def _draw_no_upd(_=None):
                W = card_canvas.winfo_width() or 600
                H = 86
                card_canvas.delete("all")
                _draw_rounded_rect(card_canvas, 3, 4, W-1, H+1, r=14,
                                   fill=_lerp_color(BG_VOID, BD_MID, 0.3), outline="")
                _draw_rounded_rect(card_canvas, 1, 1, W-2, H-1, r=14,
                                   fill=BG_CARD, outline=BD_MID, width=1)
                ax = 14
                card_canvas.create_arc(2, 2, ax*2+2, ax*2+2,
                                       start=90, extent=90, fill=AC_MAIN, outline=AC_MAIN)
                card_canvas.create_arc(W-ax*2-2, 2, W-2, ax*2+2,
                                       start=0, extent=90, fill=AC_MAIN, outline=AC_MAIN)
                card_canvas.create_rectangle(ax+2, 2, W-ax-2, 4,
                                             fill=AC_MAIN, outline="")
                iv = _read_installed_version()
                card_canvas.create_text(W//2, 36,
                    text="◈   Проверить обновления",
                    fill=TX_MAIN, font=("Segoe UI", 13, "bold"), anchor="center")
                card_canvas.create_text(W//2, 57,
                    text=f"Установлена: v{iv}   ·   {GITHUB_REPO}",
                    fill=TX_DIM, font=("Segoe UI", 9), anchor="center")

            card_canvas.bind("<Configure>", _draw_no_upd)
            _draw_no_upd()

            self._chk_btn_w = make_action_button_rounded(
                self._upd_btn_frame,
                "◈   ПРОВЕРИТЬ ОБНОВЛЕНИЯ",
                command=self._do_check_updates,
                style="primary",
                font=("Segoe UI", 12, "bold"),
                px=22, py=12,
            )
            self._chk_btn_w.pack(fill="x")


    def _do_update_now(self):
        """Скачивает и устанавливает обновление с прогрессом."""
        if not self._latest_update_info:
            return
        url     = self._latest_update_info.get("download_url", "")
        new_ver = self._latest_update_info.get("version", "")
        if not url:
            self._toast.show("Ссылка на обновление недоступна!", kind="error")
            return

        self._log(f"⬆  Скачиваю обновление v{new_ver}...", "gold")

        try:
            self._do_upd_btn.configure(text="⏳  Скачиваю...")
        except Exception:
            pass

        def _prog(done, total, speed=0):
            def _ui():
                try:
                    pct = done / max(total, 1) if total else 0
                    self._upd_prog_bar.set(pct)
                    sz    = fmt_size(done)
                    tot_s = f"/ {fmt_size(total)}" if total else ""
                    spd_s = f"  ↓ {fmt_size(speed)}/с" if speed > 0 else ""
                    self._upd_speed_lbl.configure(text=f"{sz} {tot_s}{spd_s}")
                except Exception:
                    pass
            self.after(0, _ui)

        def _done(ok, result):
            self.after(0, lambda: self._on_upd_downloaded(ok, result))

        _patched_download_and_install(
            self._updater, url, new_ver,
            on_progress=_prog,
            on_done=_done,
        )
    '''

    print("╔══════════════════════════════════════════════════════════╗")
    print("║      Angels Launcher Patch v13.2 — загружен успешно      ║")
    print("╠══════════════════════════════════════════════════════════╣")
    print("║  Компоненты:                                             ║")
    print("║    RoundedButton        — кнопка с анимацией             ║")
    print("║    RoundedProgressBar   — прогресс-бар с %               ║")
    print("║    RoundedToastManager  — toast-уведомления              ║")
    print("║    GlowLabel            — неоновый текст                 ║")
    print("║    AnimatedCard         — карточка с hover               ║")
    print("║    make_neon_entry_rounded — поле ввода с glow           ║")
    print("╠══════════════════════════════════════════════════════════╣")
    print("║  Замените в angels_launcher.py:                         ║")
    print("║    make_pill_button    → make_pill_button_rounded        ║")
    print("║    make_action_button  → make_action_button_rounded      ║")
    print("║    make_neon_entry     → make_neon_entry_rounded         ║")
    print("║    NeonProgressBar     → RoundedProgressBar              ║")
    print("║    ToastManager        → RoundedToastManager             ║")
    print("╚══════════════════════════════════════════════════════════╝")

except ImportError as e:
    print(f"[Патч] tkinter недоступен: {e} — UI-компоненты не загружены.")
    print("[Патч] _patched_download_and_install доступен без tkinter.")
