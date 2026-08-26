import tkinter as tk
import threading
import time
import pyautogui

class AutoChunkSenderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Авто-отправщик больших текстов")
        self.root.geometry("450x320")
        
        self.is_active = False
        self.is_sending = False
        self.draft_text = ""
        self.chunk_size = 500000  # Лимит символов за раз
        self.last_clipboard = ""

        # Статус
        self.status_label = tk.Label(root, text="Статус: ВЫКЛЮЧЕН", fg="red", font=("Arial", 14, "bold"))
        self.status_label.pack(pady=10)

        # Кнопка Включить / Выключить перехват
        self.btn_on = tk.Button(root, text="ВКЛЮЧИТЬ ПЕРЕХВАТ", bg="green", fg="white", font=("Arial", 11), width=25, command=self.turn_on)
        self.btn_on.pack(pady=5)

        self.btn_off = tk.Button(root, text="ВЫКЛЮЧИТЬ", bg="gray", fg="white", font=("Arial", 11), width=25, command=self.turn_off)
        self.btn_off.pack(pady=5)

        # Кнопка АВТО-ОТПРАВКИ (то самое волшебство)
        self.btn_start_send = tk.Button(root, text="ЗАПУСТИТЬ АВТО-ВСТАВКУ (5 сек)", bg="blue", fg="white", font=("Arial", 11, "bold"), width=25, command=self.start_auto_sending)
        self.btn_start_send.pack(pady=15)

        # Индикатор черновика
        self.info_label = tk.Label(root, text="В черновике символов: 0", font=("Arial", 10))
        self.info_label.pack(pady=5)

        # Предупреждение
        self.warn_label = tk.Label(root, text="Инструкция:\n1. Включи -> Скопируй текст 1 раз.\n2. Кликни в чат мышей.\n3. Нажми 'Запустить' (есть 5 сек на клик).", fg="gray", font=("Arial", 9))
        self.warn_label.pack(pady=5)

        # Фоновый поток для слежки за буфером
        self.monitor_thread = threading.Thread(target=self.clipboard_watcher, daemon=True)
        self.monitor_thread.start()

    def turn_on(self):
        self.is_active = True
        self.status_label.config(text="Статус: ПЕРЕХВАТ ВКЛЮЧЕН", fg="green")

    def turn_off(self):
        self.is_active = False
        self.is_sending = False
        self.status_label.config(text="Статус: ВЫКЛЮЧЕН", fg="red")

    def clipboard_watcher(self):
        while True:
            if self.is_active and not self.is_sending:
                try:
                    current_clip = self.root.clipboard_get()
                    # Если пользователь скопировал что-то новое и объемное
                    if current_clip != self.last_clipboard and len(current_clip) > 50:
                        self.draft_text = current_clip
                        self.last_clipboard = current_clip
                        self.update_info()
                except Exception:
                    pass
            time.sleep(0.5)

    def update_info(self):
        self.info_label.config(text=f"В черновике символов: {len(self.draft_text)}")

    def start_auto_sending(self):
        if len(self.draft_text) == 0:
            self.status_label.config(text="Черновик пустой! Скопируй текст.", fg="orange")
            return
        
        if self.is_sending:
            return

        # Запускаем отправку в отдельном потоке, чтобы интерфейс программы не завис
        threading.Thread(target=self.auto_send_process, daemon=True).start()

    def auto_send_process(self):
        self.is_sending = True
        self.status_label.config(text="Статус: ПОДГОТОВКА (Кликни в чат!)", fg="purple")
        
        # Даем пользователю 5 секунд, чтобы кликнуть мышкой в нужное поле ввода (например, в WhatsApp)
        for i in range(5, 0, -1):
            self.status_label.config(text=f"Старт через {i} сек... Кликни в чат!", fg="purple")
            time.sleep(1)

        self.status_label.config(text="Статус: АВТО-ОТПРАВКА ИДЕТ...", fg="blue")

        # Отключаем защиту pyautogui, чтобы мышка не срывалась
        pyautogui.FAILSAFE = True 

        while len(self.draft_text) > 0 and self.is_sending:
            # Берем первый кусок по 500 000 символов
            chunk = self.draft_text[:self.chunk_size]
            # Остаток оставляем на потом
            self.draft_text = self.draft_text[self.chunk_size:]

            # Кладём текущий кусок в буфер обмена
            self.root.clipboard_clear()
            self.root.clipboard_append(chunk)
            self.last_clipboard = chunk
            
            # Обновляем интерфейс
            self.root.after(0, self.update_info)

            # Симулируем нажатие клавиш вставки (Ctrl + V)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.5)  # Небольшая пауза, чтобы система успела вставить текст

            # Нажимаем Enter (отправка сообщения)
            pyautogui.press('enter')
            
            # Пауза между кусками, чтобы мессенджер не заблокировал за спам
            time.sleep(1.5)

        self.is_sending = False
        if len(self.draft_text) == 0:
            self.status_label.config(text="Статус: ВСЁ УСПЕШНО ОТПРАВЛЕНО!", fg="green")
        else:
            self.status_label.config(text="Статус: ОСТАНОВЛЕНО", fg="orange")

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoChunkSenderApp(root)
    root.mainloop()











БОТ АРХИТЕКТОР

import colorsys
import os
import re
import subprocess
import sys
import tkinter as tk
from tkinter import scrolledtext, messagebox
from difflib import get_close_matches

# ============================================================
# КОНФИГУРАЦИЯ
# ============================================================
LLM_MODEL = os.environ.get("CODEGEN_LLM_MODEL", "claude-sonnet-4-6")
LLM_MAX_TOKENS = 300

MODE_OFFLINE = "offline"
MODE_SCALE = "scale"

# ---------------------------------------------------------- киберпанк-палитра
# (совпадает с главным ботом-кодером - тот же визуальный язык)
BG_BLACK = "#000000"
NEON_CYAN = "#00fff2"
NEON_MAGENTA = "#ff00ea"
NEON_GREEN = "#39ff14"
NEON_YELLOW = "#fff400"
NEON_RED = "#ff2b4e"
NEON_PURPLE = "#b967ff"
NEON_BLUE = "#00d9ff"
TEXT_WHITE = "#ffffff"


def _hue_to_hex(h):
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, 0.85, 1.0)
    return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"


# ============================================================
# СЛОВАРИ - ДОЛЖНЫ СОВПАДАТЬ С ComponentLibrary ГЛАВНОГО БОТА-КОДЕРА
# (pro7.py). Если там появятся новые строительные блоки - их нужно
# продублировать и здесь, иначе Черновик №1 будет "чистым", но не будет
# реально соответствовать словарю бота-кодера.
# ============================================================
COMPONENT_KEYWORDS = {
    "main_menu": {"меню"},
    "balance_display": {"баланс", "деньги", "монеты", "счет", "счёт"},
    "cards_module": {"карт", "карты", "карточ", "колода"},
    "server_panel": {"сервер"},
    "panel_layout": {"панель", "раздел"},
    "play_button": {"играть", "старт"},
    "folder_action": {"папка", "директория"},
    "file_action": {"файл", "документ"},
}

DELETE_KEYWORDS = {
    "удали", "удалить", "удаляем", "убери", "убрать", "сотри", "стереть",
    "снеси", "снести", "отмени", "убрали", "удалено",
}

MODIFY_KEYWORDS = {
    "измени", "изменить", "поменяй", "поменять", "замени", "заменить",
    "переделай", "переделать", "обнови", "обновить",
}

_ALL_COMPONENT_WORDS = sorted({w for kws in COMPONENT_KEYWORDS.values() for w in kws})


# ============================================================
# МОДУЛЬ 1: Лёгкая коррекция ввода
# ============================================================
class InputCorrector:
    """ВАЖНО: это эвристическая коррекция опечаток/сленга по словарю
    (fuzzy-match словами), а НЕ настоящая проверка грамматики - оффлайн
    NLP-грамматики здесь нет и быть не может. Она чинит явные опечатки в
    ключевых словах бота-кодера и убирает лишние пробелы/капитализацию,
    не более того."""

    SLANG_MAP = {
        "прога": "программа", "кнопа": "кнопка", "виндоу": "окно",
        "плз": "", "плиз": "", "чтоб": "чтобы",
    }

    VOCAB = sorted(
        set(_ALL_COMPONENT_WORDS) | DELETE_KEYWORDS | MODIFY_KEYWORDS
        | {"добавь", "добавить", "создай", "создать", "сделай", "сделать",
           "окно", "кнопка", "текст", "интерфейс"}
    )

    def clean(self, text):
        t = re.sub(r"\s+", " ", text.strip())
        if not t:
            return "", []
        words = t.split(" ")
        fixed, log = [], []
        for w in words:
            low = w.lower().strip(".,;!?")
            if low in self.SLANG_MAP:
                repl = self.SLANG_MAP[low]
                if repl:
                    fixed.append(repl)
                    log.append(f"'{w}' -> '{repl}'")
                continue
            if low and low not in self.VOCAB:
                match = get_close_matches(low, self.VOCAB, n=1, cutoff=0.8)
                if match:
                    fixed.append(match[0])
                    log.append(f"'{w}' -> '{match[0]}'")
                    continue
            fixed.append(w)
        cleaned = " ".join(fixed).strip()
        if cleaned:
            cleaned = cleaned[0].upper() + cleaned[1:]
        return cleaned, log


# ============================================================
# МОДУЛЬ 2: Разбивка сырого текста на отдельные пункты
# ============================================================
def split_into_items(raw_text):
    raw_text = raw_text.strip()
    if not raw_text:
        return []
    lines = [l.strip() for l in raw_text.splitlines() if l.strip()]

    def is_numbered(l):
        return ":" in l and l.split(":", 1)[0].strip().isdigit()

    if lines and all(is_numbered(l) for l in lines):
        return [l.split(":", 1)[1].strip() for l in lines]

    if len(lines) > 1:
        parts = lines
    else:
        raw = lines[0] if lines else raw_text
        parts = re.split(
            r'[;.!?]+\s*|,?\s+(?:и\s+)?затем\s+|,?\s+потом\s+',
            raw, flags=re.IGNORECASE,
        )
        parts = [p.strip(" .,;!?") for p in parts if p.strip(" .,;!?")]
    return parts


def _tokenize(text):
    return set(re.findall(r"[а-яёa-z0-9]+", text.lower()))


def classify_action(tokens):
    if DELETE_KEYWORDS & tokens:
        return "удалить"
    if MODIFY_KEYWORDS & tokens:
        return "изменить"
    return "добавить"


def match_components(tokens):
    return [name for name, kws in COMPONENT_KEYWORDS.items() if kws & tokens]


# ============================================================
# МОДУЛЬ 3: Бот-выдумщик (только для режима "Масштаб")
# ============================================================
class IdeaGenerator:
    """Придумывает переформулировку для пунктов, которые не легли ни на
    один компонент бота-кодера. Есть два источника: LLM (если задан
    ANTHROPIC_API_KEY и установлен пакет anthropic) или, по умолчанию,
    честный rule-based запасной вариант - нечёткий поиск ближайшего
    известного слова-триггера бота-кодера. Источник всегда указывается
    явно рядом с результатом, ничего не выдаётся за LLM, если это не он."""

    SYSTEM_PROMPT = (
        "Ты помогаешь переформулировать нестандартную идею пользователя в "
        "команду для простого бота-конструктора tkinter-интерфейсов. У "
        "бота есть только эти строительные блоки: меню, баланс, карты, "
        "серверная панель, панель-раздел, кнопка 'играть', создание папки/"
        "файла, а также общий каркас-заглушка для всего остального. "
        "Предложи ОДНУ короткую строку - переформулировку идеи в терминах "
        "ближайшего подходящего блока, или честно скажи, что подходящего "
        "блока нет, и опиши задачу для каркаса-заглушки. Только сама "
        "переформулировка, без пояснений и без markdown."
    )

    def __init__(self):
        self._client = None
        self._error = None
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            self._error = "ANTHROPIC_API_KEY не задан"
            return
        try:
            import anthropic
            self._client = anthropic.Anthropic(api_key=api_key)
        except ImportError:
            self._error = "пакет 'anthropic' не установлен"
        except Exception as e:
            self._error = str(e)

    @property
    def available(self):
        return self._client is not None

    def suggest(self, text):
        if self.available:
            try:
                resp = self._client.messages.create(
                    model=LLM_MODEL, max_tokens=LLM_MAX_TOKENS,
                    system=self.SYSTEM_PROMPT,
                    messages=[{"role": "user", "content": text}],
                )
                parts = [b.text for b in resp.content if getattr(b, "type", "") == "text"]
                suggestion = "\n".join(parts).strip()
                if suggestion:
                    return suggestion, "LLM"
            except Exception:
                pass  # тихо уходим в rule-based запасной вариант ниже

        tokens = re.findall(r"[а-яёa-z0-9]+", text.lower())
        for tok in tokens:
            match = get_close_matches(tok, _ALL_COMPONENT_WORDS, n=1, cutoff=0.6)
            if match:
                best = match[0]
                comp_name = next(name for name, kws in COMPONENT_KEYWORDS.items() if best in kws)
                return f"добавь {best} ({comp_name}), реализующий: {text}", "правило (ближайший компонент)"
        return f"добавь именной каркас под задачу: {text}", "правило (каркас-заглушка)"


# ============================================================
# ОРКЕСТРАТОР
# ============================================================
class EditorBot:
    def __init__(self):
        self.corrector = InputCorrector()
        self.idea_generator = IdeaGenerator()

    def process(self, raw_text, mode):
        items = split_into_items(raw_text)
        draft1_lines, draft2_lines, all_corrections = [], [], []

        for idx, raw_item in enumerate(items, start=1):
            cleaned, corrections = self.corrector.clean(raw_item)
            if corrections:
                all_corrections.extend(corrections)
            if not cleaned:
                continue

            tokens = _tokenize(cleaned)
            action = classify_action(tokens)
            components = match_components(tokens)

            if action == "удалить":
                draft1_lines.append(f"{idx}: удали — {cleaned}")
                continue

            if components:
                comp_label = "+".join(components)
                draft1_lines.append(
                    f"{idx}: {action} — {cleaned}  [компонент(ы) бота-кодера: {comp_label}]"
                )
                continue

            if mode == MODE_OFFLINE:
                # офлайн = строго под реальный функционал бота-кодера, без
                # выдумок: неопознанные пункты всё равно уходят в Черновик 1
                # как есть - бот-кодер сам соберёт под них именной каркас
                draft1_lines.append(
                    f"{idx}: {action} — {cleaned}  "
                    f"[точного компонента нет - бот-кодер соберёт каркас-заглушку]"
                )
            else:
                suggestion, source = self.idea_generator.suggest(cleaned)
                draft2_lines.append(
                    f"{idx}: [ИДЕЯ, источник: {source}]\n"
                    f"    предложение: {suggestion}\n"
                    f"    исходная формулировка: {cleaned}"
                )

        return draft1_lines, draft2_lines, all_corrections


# ============================================================
# GUI
# ============================================================
class EditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Форматировщик-Редактор — второй бот, тот же стиль")
        self.root.geometry("1500x900")
        self.root.minsize(1150, 680)
        self.root.configure(bg=BG_BLACK)

        self.bot = EditorBot()
        self.mode = MODE_OFFLINE

        self._glow_hue = 0.0
        self._neon_frames = []

        self._build_ui()
        self._set_mode(self.mode)
        self._animate_neon()

    # ------------------------------------------------------------------ UI

    def _register_neon(self, widget, hue_offset):
        self._neon_frames.append((widget, hue_offset))

    def _build_ui(self):
        self.bg_canvas = tk.Canvas(self.root, highlightthickness=0, bg=BG_BLACK, bd=0)
        self.bg_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

        outer = tk.Frame(self.root, bg=BG_BLACK)
        outer.pack(fill="both", expand=True, padx=18, pady=18)

        top_bar = tk.Frame(outer, bg=BG_BLACK, highlightthickness=2, highlightbackground=NEON_CYAN)
        top_bar.pack(fill="x", pady=(0, 8))
        self._register_neon(top_bar, 0.0)

        self.btn_process = tk.Button(
            top_bar, text="▶ Обработать", font=("Segoe UI", 10, "bold"),
            fg=TEXT_WHITE, bg="#111111", activeforeground=TEXT_WHITE, activebackground="#222222",
            command=self.run_process)
        self.btn_process.pack(side="left", padx=6, pady=6)

        self.btn_paste = tk.Button(
            top_bar, text="📋 Вставить", font=("Segoe UI", 10, "bold"),
            fg=TEXT_WHITE, bg="#12314a", activeforeground=TEXT_WHITE, activebackground="#1a4a6e",
            highlightthickness=2, highlightbackground=NEON_BLUE,
            command=lambda: self._paste_clipboard(self.main_text))
        self.btn_paste.pack(side="left", padx=6, pady=6)

        self.btn_copy_ready = tk.Button(
            top_bar, text="📋 Скопировать готовый текст", font=("Segoe UI", 10, "bold"),
            fg=TEXT_WHITE, bg="#123312", activeforeground=TEXT_WHITE, activebackground="#1c4a1c",
            highlightthickness=2, highlightbackground=NEON_GREEN,
            command=lambda: self.copy_text(self.draft1_text))
        self.btn_copy_ready.pack(side="left", padx=6, pady=6)

        self.btn_clear_all = tk.Button(
            top_bar, text="🧹 Полная очистка", font=("Segoe UI", 10, "bold"),
            fg=TEXT_WHITE, bg="#3a1414", activeforeground=TEXT_WHITE, activebackground="#5a1c1c",
            highlightthickness=2, highlightbackground=NEON_RED,
            command=self.clear_everything)
        self.btn_clear_all.pack(side="left", padx=6, pady=6)

        mode_frame = tk.Frame(top_bar, bg=BG_BLACK)
        mode_frame.pack(side="left", padx=14)
        tk.Label(mode_frame, text="Режим:", font=("Segoe UI", 9), bg=BG_BLACK, fg=TEXT_WHITE).pack(side="left", padx=(0, 4))
        self.btn_offline = tk.Button(mode_frame, text="Оффлайн", fg=TEXT_WHITE,
                                      activeforeground=TEXT_WHITE, command=lambda: self._set_mode(MODE_OFFLINE))
        self.btn_offline.pack(side="left", padx=2)
        self.btn_scale = tk.Button(mode_frame, text="Масштаб", fg=TEXT_WHITE,
                                    activeforeground=TEXT_WHITE, command=lambda: self._set_mode(MODE_SCALE))
        self.btn_scale.pack(side="left", padx=2)

        self.mode_status_var = tk.StringVar(value="")
        tk.Label(top_bar, textvariable=self.mode_status_var, fg=NEON_CYAN, bg=BG_BLACK,
                 font=("Consolas", 9)).pack(side="right", padx=10)

        main_area = tk.Frame(outer, bg=BG_BLACK)
        main_area.pack(fill="both", expand=True)

        left_frame = tk.Frame(main_area, bg=BG_BLACK, highlightthickness=2, highlightbackground=NEON_PURPLE)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 8))
        self._register_neon(left_frame, 0.15)
        tk.Label(left_frame, text="Сырой текст задумки — как есть, с опечатками и не по порядку",
                 bg=BG_BLACK, fg=NEON_PURPLE, font=("Consolas", 9, "bold")).pack(anchor="w", padx=6, pady=(6, 2))

        self.main_text = scrolledtext.ScrolledText(
            left_frame, wrap="word", font=("Consolas", 10),
            bg=BG_BLACK, fg=TEXT_WHITE, insertbackground=NEON_GREEN,
            highlightthickness=1, highlightbackground=NEON_PURPLE, bd=0)
        self.main_text.pack(fill="both", expand=True, padx=6, pady=(0, 4))
        self.main_text.bind("<Control-Return>", lambda e: (self.run_process(), "break")[1])
        self.main_text.bind("<KeyRelease>", lambda e: self._apply_char_rainbow(self.main_text))
        self.main_text.tag_config("char_odd", foreground=NEON_PURPLE)
        self.main_text.tag_config("char_even", foreground=NEON_BLUE)
        self._bind_clipboard_shortcuts(self.main_text, editable=True)
        self._attach_context_menu(self.main_text, editable=True)

        hint = ("Пишите как угодно - списком, одной фразой через 'затем', с\n"
                "опечатками. «Обработать» почистит текст, разложит по пунктам,\n"
                "распознает удали/измени/добавь и разложит по двум черновикам.")
        tk.Label(left_frame, text=hint, wraplength=500, justify="left",
                 fg="#8899aa", bg=BG_BLACK, font=("Consolas", 8)).pack(fill="x", padx=6, pady=(0, 6))

        right_frame = tk.Frame(main_area, bg=BG_BLACK)
        right_frame.pack(side="left", fill="both", expand=True)

        self.draft1_text = self._build_draft_panel(
            right_frame,
            "Черновик №1 — для бота-кодера (чистый, точный, по словарю компонентов)",
            NEON_MAGENTA, 0.4)
        self.draft2_text = self._build_draft_panel(
            right_frame,
            "Черновик №2 — бот-выдумщик (альтернативы для того, с чем бот-кодер сам не справится)",
            NEON_CYAN, 0.7)

        self.status_var = tk.StringVar(
            value="Готов. Впишите задумку слева и нажмите «Обработать» (или Ctrl+Enter).")
        tk.Label(outer, textvariable=self.status_var, anchor="w", bg=BG_BLACK, fg=TEXT_WHITE,
                 wraplength=1450, justify="left", font=("Consolas", 9)).pack(fill="x", side="bottom", pady=(8, 0))

    def _build_draft_panel(self, parent, title, hue_color, hue_offset):
        frame = tk.Frame(parent, bg=BG_BLACK, highlightthickness=2, highlightbackground=hue_color)
        frame.pack(fill="both", expand=True, padx=2, pady=4)
        self._register_neon(frame, hue_offset)
        tk.Label(frame, text=title, bg=BG_BLACK, fg=hue_color,
                 font=("Consolas", 9, "bold"), wraplength=650, justify="left").pack(anchor="w", padx=6, pady=(6, 2))
        text_widget = scrolledtext.ScrolledText(
            frame, wrap="word", height=16, font=("Consolas", 9), state="disabled",
            bg=BG_BLACK, fg=TEXT_WHITE, highlightthickness=0, bd=0)
        text_widget.pack(fill="both", expand=True, padx=6, pady=(0, 2))
        self._bind_clipboard_shortcuts(text_widget, editable=False)
        self._attach_context_menu(text_widget, editable=False)
        tk.Button(frame, text="Скопировать текст", fg=TEXT_WHITE, bg="#111111",
                  activeforeground=TEXT_WHITE,
                  command=lambda w=text_widget: self.copy_text(w)).pack(anchor="e", padx=6, pady=(0, 6))
        return text_widget

    # ------------------------------------------------------- анимация неона

    def _animate_neon(self):
        try:
            w = max(self.bg_canvas.winfo_width(), 100)
            h = max(self.bg_canvas.winfo_height(), 100)
            self.bg_canvas.delete("glow")
            for i in range(12):
                hue = (self._glow_hue + i * 0.03) % 1.0
                color = _hue_to_hex(hue)
                inset = i * 1.5
                self.bg_canvas.create_rectangle(inset, inset, w - inset, h - inset,
                                                 outline=color, width=2, tags="glow")
            for widget, offset in self._neon_frames:
                try:
                    color = _hue_to_hex((self._glow_hue + offset) % 1.0)
                    widget.configure(highlightbackground=color, highlightcolor=color)
                except tk.TclError:
                    pass
            self._glow_hue = (self._glow_hue + 0.004) % 1.0
        except tk.TclError:
            pass
        self.root.after(90, self._animate_neon)

    def _apply_char_rainbow(self, widget):
        try:
            content = widget.get("1.0", "end-1c")
        except tk.TclError:
            return
        widget.tag_remove("char_odd", "1.0", "end")
        widget.tag_remove("char_even", "1.0", "end")
        line, col, idx = 1, 0, 0
        for ch in content:
            if ch == "\n":
                line += 1
                col = 0
                idx += 1
                continue
            tag = "char_odd" if idx % 2 == 0 else "char_even"
            widget.tag_add(tag, f"{line}.{col}", f"{line}.{col + 1}")
            col += 1
            idx += 1

    # --------------------------------------------------------- режимы работы

    def _set_mode(self, mode):
        self.mode = mode
        if mode == MODE_OFFLINE:
            self.btn_offline.config(relief="sunken", bg="#123312")
            self.btn_scale.config(relief="raised", bg="#111111")
            self.mode_status_var.set("Режим: Оффлайн — строго под реальный функционал бота-кодера")
        else:
            self.btn_offline.config(relief="raised", bg="#111111")
            self.btn_scale.config(relief="sunken", bg="#122233")
            llm_note = "LLM доступен" if self.bot.idea_generator.available else "LLM недоступен, работает правило"
            self.mode_status_var.set(f"Режим: Масштаб — бот-выдумщик включён ({llm_note})")
        self.status_var.set(f"Режим переключён на «{'Оффлайн' if mode == MODE_OFFLINE else 'Масштаб'}».")

    # ============================================================ ОБРАБОТКА

    def run_process(self):
        raw = self.main_text.get("1.0", "end").strip()
        if not raw:
            messagebox.showwarning("Пусто", "Впишите задумку в главное поле слева.")
            return

        draft1_lines, draft2_lines, corrections = self.bot.process(raw, self.mode)

        d1_text = "\n\n".join(draft1_lines) if draft1_lines else "(нет пунктов, готовых для бота-кодера)"
        d2_text = "\n\n".join(draft2_lines) if draft2_lines else (
            "(пусто — в офлайн-режиме бот-выдумщик не используется)" if self.mode == MODE_OFFLINE
            else "(все пункты легли на известные компоненты — выдумывать было не для чего)"
        )

        self._set_widget_text(self.draft1_text, d1_text)
        self._set_widget_text(self.draft2_text, d2_text)

        note = f" Исправлено слов: {len(corrections)}." if corrections else ""
        self.status_var.set(
            f"Обработано пунктов: {len(draft1_lines) + len(draft2_lines)} "
            f"(бот-кодер: {len(draft1_lines)}, бот-выдумщик: {len(draft2_lines)}).{note}"
        )

    def clear_everything(self):
        """Полная очистка: главное поле ввода И оба черновика - буквально
        всё, что есть в приложении."""
        self.main_text.delete("1.0", "end")
        self._apply_char_rainbow(self.main_text)
        self._set_widget_text(self.draft1_text, "")
        self._set_widget_text(self.draft2_text, "")
        self.status_var.set("Полная очистка выполнена: поле ввода и оба черновика пусты.")

    # ------------------------------------------------------------ утилиты

    def _set_widget_text(self, widget, text):
        widget.config(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", text)
        widget.config(state="disabled")

    def copy_text(self, widget):
        text = widget.get("1.0", "end").strip()
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.status_var.set("Текст скопирован в буфер обмена.")

    # --------------------------------------------------------- буфер обмена
    # (тот же надёжный многоступенчатый механизм, что и в главном боте:
    # Ctrl+V/C по физическому keycode - устойчиво к русской раскладке;
    # чтение буфера - в несколько шагов с системным фолбэком по ОС)

    def _bind_clipboard_shortcuts(self, widget, editable):
        def handler(event):
            code = event.keycode
            if code == 86:
                if editable:
                    self._paste_clipboard(widget)
                return "break"
            if code == 67:
                self._copy_selection(widget)
                return "break"
            if code == 88 and editable:
                self._cut_selection(widget)
                return "break"
            if code == 65:
                widget.tag_add("sel", "1.0", "end")
                return "break"
            return None
        widget.bind("<Control-KeyPress>", handler)

    def _attach_context_menu(self, widget, editable):
        menu = tk.Menu(widget, tearoff=0, bg="#111111", fg=TEXT_WHITE,
                        activebackground="#222222", activeforeground=TEXT_WHITE)
        if editable:
            menu.add_command(label="Вставить", command=lambda: self._paste_clipboard(widget))
            menu.add_command(label="Вырезать", command=lambda: self._cut_selection(widget))
        menu.add_command(label="Копировать", command=lambda: self._copy_selection(widget))
        menu.add_command(label="Выделить всё", command=lambda: widget.tag_add("sel", "1.0", "end"))

        def show_menu(event):
            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()
        widget.bind("<Button-3>", show_menu)

    def _read_clipboard_text(self):
        try:
            text = self.root.clipboard_get()
            if text:
                return text
        except tk.TclError:
            pass
        try:
            text = self.main_text.clipboard_get()
            if text:
                return text
        except tk.TclError:
            pass
        try:
            if sys.platform.startswith("win"):
                result = subprocess.run(
                    ["powershell", "-NoProfile", "-Command", "Get-Clipboard"],
                    capture_output=True, text=True, timeout=2,
                )
                if result.returncode == 0 and result.stdout:
                    return result.stdout.rstrip("\r\n")
            elif sys.platform == "darwin":
                result = subprocess.run(["pbpaste"], capture_output=True, text=True, timeout=2)
                if result.returncode == 0 and result.stdout:
                    return result.stdout
            else:
                for cmd in (["xclip", "-selection", "clipboard", "-o"],
                            ["xsel", "--clipboard", "--output"],
                            ["wl-paste"]):
                    try:
                        result = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
                        if result.returncode == 0 and result.stdout:
                            return result.stdout
                    except FileNotFoundError:
                        continue
        except Exception:
            pass
        return None

    def _paste_clipboard(self, widget):
        text = self._read_clipboard_text()
        if text is None:
            messagebox.showwarning(
                "Буфер обмена недоступен",
                "Не удалось прочитать текст ни одним из доступных способов. "
                "Скопируйте текст заново и нажмите «📋 Вставить» ещё раз.",
            )
            self.status_var.set("Вставка не удалась: буфер обмена пуст или недоступен.")
            return
        widget.focus_set()
        was_disabled = widget.cget("state") == "disabled"
        if was_disabled:
            widget.config(state="normal")
        try:
            if widget.tag_ranges("sel"):
                widget.delete("sel.first", "sel.last")
            widget.insert(tk.INSERT, text)
        finally:
            if was_disabled:
                widget.config(state="disabled")
        if widget is self.main_text:
            self._apply_char_rainbow(self.main_text)
        self.status_var.set(f"Вставлено из буфера обмена: {len(text)} симв.")

    def _copy_selection(self, widget):
        try:
            if widget.tag_ranges("sel"):
                text = widget.get("sel.first", "sel.last")
                self.root.clipboard_clear()
                self.root.clipboard_append(text)
        except tk.TclError:
            pass

    def _cut_selection(self, widget):
        self._copy_selection(widget)
        was_disabled = widget.cget("state") == "disabled"
        if was_disabled:
            widget.config(state="normal")
        try:
            if widget.tag_ranges("sel"):
                widget.delete("sel.first", "sel.last")
        finally:
            if was_disabled:
                widget.config(state="disabled")
        if widget is self.main_text:
            self._apply_char_rainbow(self.main_text)


def main():
    root = tk.Tk()
    EditorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()




БОТ ПЕРЕВОДЧИК ТЕКСТА

import ast
import colorsys
import datetime
import difflib
import hashlib
import json
import math
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import tkinter as tk
from tkinter import scrolledtext, messagebox
from collections import Counter, defaultdict
from difflib import get_close_matches

# ============================================================
# КОНФИГУРАЦИЯ
# ============================================================
LLM_MODEL = os.environ.get("CODEGEN_LLM_MODEL", "claude-sonnet-4-6")
LLM_MAX_TOKENS = int(os.environ.get("CODEGEN_LLM_MAX_TOKENS", "4000"))

BACKUPS_DIR = "backups"
VCS_DIR = ".local_vcs"
SANDBOX_TMP_DIR = "sandbox_tmp"

MODE_OFFLINE = "offline"
MODE_HYBRID = "hybrid"

HOUSEKEEPING_INTERVAL_MS = 5 * 60 * 1000
MAX_BACKUPS_PER_FILE = 5
MAX_SNAPSHOTS_PER_FILE = 5
MAX_ARTIFACT_AGE_DAYS = 30
MAX_SANDBOX_TMP_AGE_SECONDS = 60 * 60

STREAM_CHUNK_SIZE = 8192  # размер порции при потоковой записи на диск

DELETE_KEYWORDS = {
    "удали", "удалить", "удаляем", "убери", "убрать", "сотри", "стереть",
    "снеси", "снести", "отмени", "убрали", "удалено",
}

# ---------------------------------------------------------- киберпанк-палитра
BG_BLACK = "#000000"
NEON_CYAN = "#00fff2"
NEON_MAGENTA = "#ff00ea"
NEON_GREEN = "#39ff14"
NEON_YELLOW = "#fff400"
NEON_RED = "#ff2b4e"
NEON_PURPLE = "#b967ff"
NEON_BLUE = "#00d9ff"
FINAL_GREEN = "#00ff66"
TEXT_WHITE = "#ffffff"

PULSE_DELAY_MS = 550


def _hue_to_hex(h):
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, 0.85, 1.0)
    return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"


def _stream_write_text(path, text, chunk_size=STREAM_CHUNK_SIZE):
    """Потоковая запись текста на диск небольшими порциями вместо одного
    большого f.write(). Не держит на диске лишнего буфера и позволяет
    писать сколь угодно длинный итоговый файл без пикового расхода
    памяти на стороне ОС при записи."""
    with open(path, "w", encoding="utf-8") as f:
        for i in range(0, len(text), chunk_size):
            f.write(text[i:i + chunk_size])


# ============================================================
# МОДУЛЬ 1: Локальный интерпретатор ввода с коррекцией ошибок
# ============================================================
class InputInterpreter:
    SLANG_MAP = {
        "прога": "программа", "апп": "приложение", "апка": "приложение",
        "калк": "калькулятор", "тудушка": "список задач", "туду": "список задач",
        "гуй": "интерфейс", "гейм": "игра", "плз": "", "плиз": "",
        "чтоб": "чтобы", "оконное": "оконное",
    }

    VOCAB = [
        "калькулятор", "список", "задач", "игра", "окно", "приложение",
        "интерфейс", "программа", "файлы", "файл", "класс", "ооп", "модули",
        "инвентарь", "персонаж", "уровень", "графика", "физика", "сервер",
        "клиент", "база", "данных", "парсер", "алгоритм", "бот", "апи",
        "папка", "директория", "панель", "играть", "середина", "центр",
        "кнопка", "заголовок", "раздел", "меню", "баланс", "карты",
        "карточ", "колода", "деньги", "монеты", "счет", "счёт",
        "удали", "удалить", "убери", "убрать", "сотри", "стереть",
    ]

    def __init__(self):
        self.log = []

    def _fix_typos(self, tokens):
        fixed = []
        for tok in tokens:
            if tok in self.VOCAB:
                fixed.append(tok)
                continue
            match = get_close_matches(tok, self.VOCAB, n=1, cutoff=0.75)
            if match:
                self.log.append(f"опечатка исправлена: '{tok}' -> '{match[0]}'")
                fixed.append(match[0])
            else:
                fixed.append(tok)
        return fixed

    def _expand_slang(self, text):
        words = text.split()
        expanded = []
        for w in words:
            low = w.lower()
            if low in self.SLANG_MAP:
                repl = self.SLANG_MAP[low]
                if repl:
                    self.log.append(f"сленг раскрыт: '{w}' -> '{repl}'")
                    expanded.append(repl)
            else:
                expanded.append(w)
        return " ".join(expanded)

    def process(self, raw_text):
        self.log = []
        text = raw_text.strip().lower()
        text = re.sub(r"[^\w\sа-яё]", " ", text, flags=re.IGNORECASE)
        text = re.sub(r"\s+", " ", text).strip()
        text = self._expand_slang(text)
        tokens = text.split()
        tokens = self._fix_typos(tokens)
        cleaned = " ".join(tokens)
        return {
            "raw": raw_text, "cleaned": cleaned, "tokens": tokens,
            "corrections": list(self.log),
        }


# ============================================================
# МОДУЛЬ 2: Контекст сборки одного пункта
# ============================================================
class ComponentContext:
    """Передаётся каждому строителю компонента: даёт уникальный на весь
    прогон счётчик (для имён переменных) и исходный текст пункта."""

    def __init__(self, item_num, raw_description):
        self.item_num = item_num
        self.raw_description = raw_description

    def unique(self, prefix):
        return f"{prefix}_{self.item_num}"


# ============================================================
# МОДУЛЬ 3: Библиотека compose-able строительных блоков
# ============================================================
class ComponentLibrary:
    """НЕ хранилище готовых цельных программ (как раньше 'Список задач'
    или 'Угадай число'). Это набор МЕЛКИХ строительных блоков tkinter-
    интерфейса. По ключевым словам пункта подбирается один или несколько
    блоков; они превращаются в фрагмент {imports, init_lines, body_lines,
    helper_defs}, который потом вставляется в ОБЩИЙ класс GeneratedApp.
    Никаких отдельных run_x() функций и никаких заранее написанных целых
    программ под конкретные заявки здесь нет."""

    def __init__(self):
        self._defs = [
            {"name": "main_menu", "keywords": {"меню"}, "build": self._main_menu},
            {"name": "balance_display",
             "keywords": {"баланс", "деньги", "монеты", "счет", "счёт"},
             "build": self._balance},
            {"name": "cards_module",
             "keywords": {"карт", "карты", "карточ", "колода"},
             "build": self._cards},
            {"name": "server_panel", "keywords": {"сервер"}, "build": self._server_panel},
            {"name": "panel_layout", "keywords": {"панель", "раздел"}, "build": self._panel_layout},
            {"name": "play_button", "keywords": {"играть", "старт"}, "build": self._play_button},
            {"name": "folder_action", "keywords": {"папка", "директория"}, "build": self._folder_action},
            {"name": "file_action", "keywords": {"файл", "документ"}, "build": self._file_action},
        ]

    def match(self, tokens):
        tok_set = set(tokens)
        return [c for c in self._defs if c["keywords"] & tok_set]

    def compose(self, matched, ctx):
        fragment = {"imports": [], "init_lines": [], "body_lines": [], "helper_defs": []}
        seen_names = set()
        for comp in matched:
            if comp["name"] in seen_names:
                continue
            seen_names.add(comp["name"])
            piece = comp["build"](ctx)
            fragment["imports"].extend(piece.get("imports", []))
            fragment["init_lines"].extend(piece.get("init_lines", []))
            fragment["body_lines"].extend(piece.get("body_lines", []))
            fragment["helper_defs"].extend(piece.get("helper_defs", []))
        return fragment

    def build_custom_placeholder(self, ctx):
        """Гарантированный, всегда синтаксически валидный каркас под ТЕКСТ
        КОНКРЕТНОГО пункта - используется только когда ни один компонент не
        подошёл и LLM недоступна. Это не заготовка из старого набора: текст
        виджета берётся из формулировки пользователя."""
        var = ctx.unique("section")
        text = ctx.raw_description.replace('"', "'").strip() or "без описания"
        return {
            "imports": [{"module": "tkinter", "asname": "tk"}],
            "init_lines": [],
            "body_lines": [
                f'{var} = tk.LabelFrame(self.root, text="Пункт: {text}")',
                f'{var}.pack(fill="x", padx=8, pady=4)',
                f'tk.Label({var}, text="Каркас под требование: {text}").pack(padx=6, pady=6)',
            ],
            "helper_defs": [],
        }

    # ---- строительные блоки (всегда одноуровневые body_lines: без вложенных
    #      def/for/while, чтобы не ломать плоское форматирование сборщика) --

    def _main_menu(self, ctx):
        var = ctx.unique("menubar")
        sub = ctx.unique("menu_file")
        return {
            "imports": [{"module": "tkinter", "asname": "tk"}],
            "init_lines": [],
            "body_lines": [
                f"{var} = tk.Menu(self.root)",
                f"self.root.config(menu={var})",
                f"{sub} = tk.Menu({var}, tearoff=0)",
                f'{sub}.add_command(label="Выход", command=self.root.quit)',
                f'{var}.add_cascade(label="Меню", menu={sub})',
            ],
            "helper_defs": [],
        }

    def _balance(self, ctx):
        return {
            "imports": [{"module": "tkinter", "asname": "tk"}],
            "init_lines": ["self.balance = 1000"],
            "body_lines": [
                'self.balance_label = tk.Label(self.root, text=f"Баланс: {self.balance}", '
                'font=("Segoe UI", 12, "bold"))',
                "self.balance_label.pack(pady=6)",
                'tk.Button(self.root, text="+100", command=lambda: self._increase_balance()).pack()',
            ],
            "helper_defs": [
                "    def _increase_balance(self):\n"
                "        self.balance += 100\n"
                "        self.balance_label.config(text=f\"Баланс: {self.balance}\")"
            ],
        }

    def _cards(self, ctx):
        return {
            "imports": [{"module": "tkinter", "asname": "tk"}, {"module": "random", "asname": None}],
            "init_lines": [
                'self.deck = [f"{r}{s}" for r in "6789TJQKA" for s in "SHDC"]',
                "self.hand = []",
            ],
            "body_lines": [
                'self.cards_label = tk.Label(self.root, text="Карты: -", font=("Consolas", 11))',
                "self.cards_label.pack(pady=4)",
                'tk.Button(self.root, text="Раздать карты", command=lambda: self._deal_cards()).pack()',
            ],
            "helper_defs": [
                "    def _deal_cards(self):\n"
                "        random.shuffle(self.deck)\n"
                "        self.hand = self.deck[:5]\n"
                '        self.cards_label.config(text="Карты: " + " ".join(self.hand))'
            ],
        }

    def _server_panel(self, ctx):
        return {
            "imports": [{"module": "tkinter", "asname": "tk"}],
            "init_lines": ["self.server_running = False"],
            "body_lines": [
                'self.server_status_label = tk.Label(self.root, text="Сервер: остановлен", fg="red")',
                "self.server_status_label.pack(pady=4)",
                'tk.Button(self.root, text="Старт/Стоп сервера", command=lambda: self._toggle_server()).pack()',
            ],
            "helper_defs": [
                "    def _toggle_server(self):\n"
                "        self.server_running = not self.server_running\n"
                "        if self.server_running:\n"
                '            self.server_status_label.config(text="Сервер: запущен", fg="green")\n'
                "        else:\n"
                '            self.server_status_label.config(text="Сервер: остановлен", fg="red")'
            ],
        }

    def _panel_layout(self, ctx):
        var = ctx.unique("panel")
        return {
            "imports": [{"module": "tkinter", "asname": "tk"}],
            "init_lines": [],
            "body_lines": [
                f'{var} = tk.Frame(self.root, bg="#222222")',
                f'{var}.pack(fill="x", padx=4, pady=4)',
                f'tk.Label({var}, text="Панель", fg="white", bg="#222222").pack(pady=6)',
            ],
            "helper_defs": [],
        }

    def _play_button(self, ctx):
        return {
            "imports": [{"module": "tkinter", "asname": "tk"}],
            "init_lines": [],
            "body_lines": [
                'self.play_button = tk.Button(self.root, text="Играть", font=("Segoe UI", 14, "bold"), '
                'command=lambda: self._on_play())',
                "self.play_button.pack(pady=20)",
            ],
            "helper_defs": [
                "    def _on_play(self):\n"
                '        print("Игра запущена!")'
            ],
        }

    def _folder_action(self, ctx):
        var = ctx.unique("folder_name")
        return {
            "imports": [{"module": "os", "asname": None}],
            "init_lines": [],
            "body_lines": [
                f'{var} = os.path.join(os.getcwd(), "Новая_папка_{ctx.item_num}")',
                f"os.makedirs({var}, exist_ok=True)",
                f'print(f"Папка реально создана: {{{var}}}")',
            ],
            "helper_defs": [],
        }

    def _file_action(self, ctx):
        var = ctx.unique("file_name")
        return {
            "imports": [{"module": "os", "asname": None}],
            "init_lines": [],
            "body_lines": [
                f'{var} = os.path.join(os.getcwd(), "новый_файл_{ctx.item_num}.txt")',
                f'open({var}, "w", encoding="utf-8").write("Файл создан ботом-генератором.\\n")',
                f'print(f"Файл реально создан: {{{var}}}")',
            ],
            "helper_defs": [],
        }


# ============================================================
# МОДУЛЬ 4: AST-трансформатор (вставка импортов в единственном экземпляре)
# ============================================================
class ASTAssembler:
    """Обёртка над ast.unparse (Python 3.9+). На более старом Python этой
    функции не существует - вместо падения с AttributeError используется
    честный текстовый fallback: недостающие импорты дописываются простыми
    строками в начало файла, без AST-пересборки (адаптация назад)."""

    def build(self, source_code, extra_imports):
        tree = ast.parse(source_code)
        existing = set()
        for node in tree.body:
            if isinstance(node, ast.Import):
                existing.update(a.name for a in node.names)
            elif isinstance(node, ast.ImportFrom):
                existing.add(node.module or "")

        new_import_nodes = []
        missing_imports = []
        for imp in extra_imports:
            if imp["module"] in existing:
                continue
            alias = ast.alias(name=imp["module"], asname=imp.get("asname"))
            new_import_nodes.append(ast.Import(names=[alias]))
            missing_imports.append(imp)
            existing.add(imp["module"])

        tree.body = new_import_nodes + tree.body
        ast.fix_missing_locations(tree)

        if hasattr(ast, "unparse"):
            return ast.unparse(tree)

        # fallback для Python < 3.9 (ast.unparse появился в 3.9)
        import_lines = "\n".join(
            f"import {imp['module']}" + (f" as {imp['asname']}" if imp.get("asname") else "")
            for imp in missing_imports
        )
        return (import_lines + "\n\n" + source_code) if import_lines else source_code

    def self_check(self, code):
        try:
            ast.parse(code)
            return True, None
        except SyntaxError as e:
            return False, str(e)


# ============================================================
# МОДУЛЬ 5: Сборщик единого монолитного приложения
# ============================================================
class AppAssembler:
    """Собирает произвольное число фрагментов в ОДНО монолитное tkinter-
    приложение: один класс GeneratedApp, один self.root, один mainloop.

    Барьеры неделимости: каждый фрагмент - неделимый блок (сам он никогда
    не разрезается на части); переупорядочиваются только ЦЕЛЫЕ фрагменты
    между собой, никогда их содержимое.

    Проверка зависимостей: перед сборкой строится граф "кто на self.<attr>
    ссылается / кто его определяет" и фрагменты сортируются топологически,
    чтобы использование виджета/атрибута никогда не оказалось раньше его
    создания - без ручных барьеров-маркеров, чистой зависимостью по имени.

    Правило неизменности: содержимое строк фрагмента (imports/init_lines/
    body_lines/helper_defs) здесь не переписывается и не 'адаптируется' -
    меняется только порядок фрагментов и то, какие импорты/инициализации
    оказались дублями (и потому убраны)."""

    def __init__(self, ast_assembler):
        self.ast_assembler = ast_assembler

    @staticmethod
    def _var_name(line):
        if "=" not in line:
            return None
        return line.split("=", 1)[0].strip()

    @staticmethod
    def _def_signature(block):
        stripped = block.strip()
        return stripped.splitlines()[0].strip() if stripped else ""

    @staticmethod
    def _self_writes(text):
        return set(re.findall(r"self\.(\w+)\s*=(?!=)", text))

    @staticmethod
    def _self_reads(text):
        return set(re.findall(r"self\.(\w+)", text))

    def _dependency_order(self, fragments):
        """Топологическая сортировка ФРАГМЕНТОВ (не строк) так, чтобы
        self.<attr>, созданный в body_lines одного фрагмента, не
        использовался в body_lines фрагмента, стоящего раньше него."""
        n = len(fragments)
        if n <= 1:
            return list(range(n))

        init_defines_globally = set()
        for frag in fragments:
            for line in frag.get("init_lines", []):
                init_defines_globally |= self._self_writes(line)

        body_defines, body_uses = [], []
        for frag in fragments:
            text = "\n".join(frag.get("body_lines", [])) + "\n" + "\n".join(frag.get("helper_defs", []))
            defines = self._self_writes(text)
            uses = self._self_reads(text) - defines - init_defines_globally
            body_defines.append(defines)
            body_uses.append(uses)

        # edges[j] = множество индексов, которые зависят от фрагмента j
        edges = defaultdict(set)
        indegree = [0] * n
        for i in range(n):
            for name in body_uses[i]:
                for j in range(n):
                    if j != i and name in body_defines[j] and i not in edges[j]:
                        edges[j].add(i)
                        indegree[i] += 1

        order = []
        remaining = set(range(n))
        progressed = True
        while remaining and progressed:
            progressed = False
            for i in sorted(remaining):
                if indegree[i] == 0:
                    order.append(i)
                    remaining.discard(i)
                    for k in edges[i]:
                        indegree[k] -= 1
                    progressed = True
                    break
        if remaining:
            # цикл зависимостей - не должно случаться для простых
            # компонентов, но сборка не должна падать: остаток дописываем
            # в исходном порядке, ничего не теряя
            order.extend(sorted(remaining))
        return order

    def _describe_dependency_order(self, fragments, order):
        """Человекочитаемое объяснение результата _dependency_order для
        Черновика №4 - ничего не пересчитывает и не меняет порядок,
        только описывает уже принятое решение."""
        if not fragments:
            return ["Нет фрагментов для расстановки."]
        notes = []
        moved = False
        for new_pos, orig_idx in enumerate(order):
            if new_pos != orig_idx:
                moved = True
                notes.append(
                    f"Фрагмент (исходная позиция {orig_idx + 1}) переставлен на позицию "
                    f"{new_pos + 1} - обнаружена зависимость по self.<атрибут>."
                )
        if not moved:
            notes.append(
                "Проверка зависимостей: пересечений self.<атрибут> между фрагментами не "
                "найдено, порядок ввода сохранён без изменений."
            )
        return notes

    def build(self, fragments):
        if not fragments:
            return None, [], ["Нет фрагментов для расстановки."]

        order = self._dependency_order(fragments)
        order_notes = self._describe_dependency_order(fragments, order)
        ordered_fragments = [fragments[i] for i in order]
        total_barriers = len(ordered_fragments)

        seen_init_vars, seen_helper_sigs, seen_import_keys = set(), set(), set()
        imports, init_lines, body_lines, helper_defs = [], [], [], []

        for barrier_idx, frag in enumerate(ordered_fragments, start=1):
            for imp in frag.get("imports", []):
                key = (imp["module"], imp.get("asname"))
                if key not in seen_import_keys:
                    seen_import_keys.add(key)
                    imports.append(imp)

            for line in frag.get("init_lines", []):
                var = self._var_name(line)
                if var and var in seen_init_vars:
                    continue
                if var:
                    seen_init_vars.add(var)
                init_lines.append(line)

            # барьер неделимости: содержимое фрагмента между этими двумя
            # маркерами никогда не разрезается и не переписывается - можно
            # переставить только сам фрагмент целиком (см. _dependency_order).
            # Маркеры записаны как строки-выражения (не '#'-комментарии),
            # т.к. итоговый код проходит через ast.unparse при форматировании,
            # а тот безвозвратно вырезает обычные комментарии.
            body_lines.append(f'"[БАРЬЕР_{barrier_idx}_ИЗ_{total_barriers} - НАЧАЛО НЕДЕЛИМОГО БЛОКА]"')
            body_lines.extend(frag.get("body_lines", []))
            body_lines.append(f'"[БАРЬЕР_{barrier_idx}_ПРОЙДЕН_ИЗ_{total_barriers}]"')

            for block in frag.get("helper_defs", []):
                sig = self._def_signature(block)
                if sig and sig in seen_helper_sigs:
                    continue
                if sig:
                    seen_helper_sigs.add(sig)
                helper_defs.append(block)

        indent = " " * 8
        init_block = "\n".join(f"{indent}{l}" for l in init_lines) if init_lines else f"{indent}pass"
        body_block = "\n".join(f"{indent}{l}" for l in body_lines) if body_lines else f"{indent}pass"
        helpers_block = ("\n\n" + "\n\n".join(helper_defs)) if helper_defs else ""

        skeleton = f'''class GeneratedApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Единое сгенерированное приложение")
{init_block}
        self._build()

    def _build(self):
{body_block}
{helpers_block}

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    GeneratedApp().run()
'''
        try:
            source = self.ast_assembler.build(skeleton, imports)
        except SyntaxError:
            source = skeleton  # диагностика ниже, в self_check/corrector

        return source, imports, order_notes


# ============================================================
# МОДУЛЬ 6: Система анализа импортов (для фрагментов LLM)
# ============================================================
class DependencyAnalyzer:
    KNOWN_LIBS = {
        "tk": {"module": "tkinter", "asname": "tk"},
        "tkinter": {"module": "tkinter", "asname": None},
        "random": {"module": "random", "asname": None},
        "math": {"module": "math", "asname": None},
        "json": {"module": "json", "asname": None},
        "os": {"module": "os", "asname": None},
        "sys": {"module": "sys", "asname": None},
        "datetime": {"module": "datetime", "asname": None},
        "time": {"module": "time", "asname": None},
        "re": {"module": "re", "asname": None},
        "itertools": {"module": "itertools", "asname": None},
        "functools": {"module": "functools", "asname": None},
        "collections": {"module": "collections", "asname": None},
        "messagebox": {"module": "tkinter.messagebox", "asname": "messagebox"},
        "ttk": {"module": "tkinter.ttk", "asname": "ttk"},
        "filedialog": {"module": "tkinter.filedialog", "asname": "filedialog"},
    }

    def scan(self, source_code):
        tree = ast.parse(source_code)
        used_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
                used_names.add(node.value.id)
            elif isinstance(node, ast.Name):
                used_names.add(node.id)
        needed, seen = [], set()
        for name in used_names:
            if name in self.KNOWN_LIBS:
                spec = self.KNOWN_LIBS[name]
                if spec["module"] not in seen:
                    needed.append(spec)
                    seen.add(spec["module"])
        return needed


# ============================================================
# МОДУЛЬ 7: Локальные бэкапы (.bak перед любой перезаписью)
# ============================================================
class BackupManager:
    def __init__(self, backup_dir=BACKUPS_DIR):
        self.backup_dir = backup_dir

    def backup(self, filepath):
        if not os.path.exists(filepath):
            return None
        os.makedirs(self.backup_dir, exist_ok=True)
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(self.backup_dir, f"{os.path.basename(filepath)}.{ts}.bak")
        shutil.copy2(filepath, backup_path)
        return backup_path

    def restore(self, filepath, backup_path):
        shutil.copy2(backup_path, filepath)


# ============================================================
# МОДУЛЬ 8: Самодиагностика и автоисправление (Self-Correction Loop)
# ============================================================
class SelfCorrector:
    """ВАЖНО: правит только механику синтаксиса (табы, ':', скобки,
    markdown-обёртки) - никогда не переписывает смысл/содержание кода.
    Это и есть техническая реализация 'правила неизменности' контента."""

    MAX_ATTEMPTS = 4
    BLOCK_KEYWORDS = ("if", "elif", "else", "for", "while", "def", "class", "try", "except", "finally", "with")

    def _fix_tabs(self, code):
        return code.replace("\t", "    ")

    def _fix_missing_colons(self, code):
        fixed = []
        for line in code.split("\n"):
            stripped = line.rstrip()
            head = stripped.strip()
            starts_block = any(head.startswith(kw + " ") or head == kw for kw in self.BLOCK_KEYWORDS)
            if starts_block and stripped and not stripped.endswith(":") and not stripped.endswith("\\"):
                fixed.append(stripped + ":")
            else:
                fixed.append(line)
        return "\n".join(fixed)

    def _fix_unbalanced_brackets(self, code):
        pairs = {"(": ")", "[": "]", "{": "}"}
        stack = []
        for ch in code:
            if ch in pairs:
                stack.append(pairs[ch])
            elif ch in pairs.values() and stack and stack[-1] == ch:
                stack.pop()
        return code + "".join(reversed(stack)) if stack else code

    def _strip_markdown_fences(self, code):
        stripped = code.strip()
        if stripped.startswith("```"):
            stripped = re.sub(r"^```[a-zA-Z]*\n?", "", stripped)
            stripped = re.sub(r"```$", "", stripped.rstrip())
        return stripped.strip()

    def correct(self, code):
        applied = []
        code = self._strip_markdown_fences(code)
        try:
            ast.parse(code)
            return code, True, applied
        except SyntaxError:
            pass

        fixes = [
            ("сняты markdown-обрамления ```", self._strip_markdown_fences),
            ("развёрнуты табы в пробелы", self._fix_tabs),
            ("дописаны пропущенные ':' после if/for/while/def/...", self._fix_missing_colons),
            ("сбалансированы незакрытые скобки", self._fix_unbalanced_brackets),
        ]
        current = code
        for _ in range(self.MAX_ATTEMPTS):
            progressed = False
            for label, fn in fixes:
                candidate = fn(current)
                if candidate == current:
                    continue
                try:
                    ast.parse(candidate)
                    applied.append(label)
                    return candidate, True, applied
                except SyntaxError:
                    current = candidate
                    applied.append(label)
                    progressed = True
            if not progressed:
                break
        try:
            ast.parse(current)
            return current, True, applied
        except SyntaxError as e:
            return current, False, applied + [f"не удалось исправить: {e}"]


# ============================================================
# МОДУЛЬ 9: Изолированная локальная песочница (Sandbox)
# ============================================================
_SANDBOX_GUI_HARNESS = (
    "try:\n"
    "    import tkinter as _sandbox_tk_probe\n"
    "    _sandbox_orig_tk_init = _sandbox_tk_probe.Tk.__init__\n"
    "    def _sandbox_patched_tk_init(self, *a, **kw):\n"
    "        _sandbox_orig_tk_init(self, *a, **kw)\n"
    "        try:\n"
    "            self.withdraw()\n"
    "        except Exception:\n"
    "            pass\n"
    "        try:\n"
    "            self.after(200, self.destroy)\n"
    "        except Exception:\n"
    "            pass\n"
    "    _sandbox_tk_probe.Tk.__init__ = _sandbox_patched_tk_init\n"
    "except Exception:\n"
    "    pass\n\n"
)


class Sandbox:
    """Запускает сгенерированный код отдельным процессом. Проверочный
    прогон получает поверх кода небольшую 'обвязку' (_SANDBOX_GUI_HARNESS),
    которая сразу прячет любое созданное tk.Tk()-окно и закрывает его через
    200мс - никаких моргающих окон во время автопроверки. Обвязка живёт
    ТОЛЬКО во временном файле песочницы: код, который в итоге попадает в
    Черновик №1/№3/№4/№5 и на диск, её не содержит вообще."""

    def __init__(self, timeout=3.0, tmp_dir=SANDBOX_TMP_DIR):
        self.timeout = timeout
        self.tmp_dir = tmp_dir
        os.makedirs(self.tmp_dir, exist_ok=True)

    def run(self, code):
        fd, path = tempfile.mkstemp(suffix=".py", dir=self.tmp_dir)
        os.close(fd)
        with open(path, "w", encoding="utf-8") as f:
            f.write(_SANDBOX_GUI_HARNESS + code)
        try:
            proc = subprocess.Popen(
                [sys.executable, path],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                cwd=os.getcwd(),
            )
            try:
                out, err = proc.communicate(input="", timeout=self.timeout)
                if proc.returncode == 0:
                    return {"status": "ok_exit", "detail": (out.strip()[-400:] if out.strip() else
                            "Приложение завершилось само, без ошибок")}
                if "EOFError" in err:
                    return {"status": "needs_input", "detail": "Нужен интерактивный ввод - автопроверка неубедительна"}
                return {"status": "crash", "detail": err.strip()[-800:] or "процесс упал без сообщения в stderr"}
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.communicate()
                return {"status": "timeout_ok", "detail": f"Не упало за {self.timeout} сек - нормально для GUI-цикла"}
        except Exception as e:
            return {"status": "sandbox_error", "detail": str(e)}
        finally:
            try:
                os.remove(path)
            except OSError:
                pass


# ============================================================
# МОДУЛЬ 10: Diff-Viewer
# ============================================================
class DiffViewer:
    def diff(self, old_code, new_code, filename="file.py"):
        old_lines = old_code.splitlines(keepends=True) if old_code else []
        new_lines = new_code.splitlines(keepends=True)
        result = difflib.unified_diff(
            old_lines, new_lines,
            fromfile=f"{filename} (текущий)", tofile=f"{filename} (новый)",
        )
        text = "".join(result)
        return text if text else "(изменений нет)"


# ============================================================
# МОДУЛЬ 11: PEP 8 линтер/форматтер
# ============================================================
class PEP8Linter:
    def format(self, code):
        # ast.unparse существует только в Python 3.9+; на более старом
        # интерпретаторе просто пропускаем AST-переформатирование и
        # переходим к построчной чистке ниже (адаптация назад).
        if hasattr(ast, "unparse"):
            try:
                code = ast.unparse(ast.parse(code))
            except SyntaxError:
                pass
        lines = [ln.rstrip() for ln in code.split("\n")]
        cleaned, blank_run = [], 0
        for ln in lines:
            if ln == "":
                blank_run += 1
                if blank_run > 2:
                    continue
            else:
                blank_run = 0
            cleaned.append(ln)
        return "\n".join(cleaned).strip() + "\n"

    def check(self, code):
        issues = []
        for i, line in enumerate(code.split("\n"), start=1):
            if len(line) > 99:
                issues.append(f"строка {i}: длиннее 99 символов")
            if line != line.rstrip():
                issues.append(f"строка {i}: пробелы в конце строки")
            if "\t" in line:
                issues.append(f"строка {i}: используется таб вместо пробелов")
        return issues


# ============================================================
# МОДУЛЬ 12: Многофайловый рефакторинг (для плоских функций старого стиля)
# ============================================================
class MultiFileRefactor:
    """Доступен как утилита, но НЕ вызывается автоматически для нового
    монолитного класса GeneratedApp: безопасно растащить единый живой
    tkinter-класс с общим self.root по нескольким файлам простыми
    эвристиками нельзя - разделяемое состояние виджетов легко сломать.
    Годится для плоских top-level функций старого образца."""

    def split(self, main_code, module_name="helpers"):
        tree = ast.parse(main_code)
        func_defs = [n for n in tree.body if isinstance(n, ast.FunctionDef)]
        other = [n for n in tree.body if not isinstance(n, ast.FunctionDef)]
        if len(func_defs) < 2:
            return None

        helper_funcs = func_defs[:-1]
        main_func = func_defs[-1]

        helper_tree = ast.Module(body=helper_funcs, type_ignores=[])
        ast.fix_missing_locations(helper_tree)
        helper_code = ast.unparse(helper_tree)

        import_node = ast.ImportFrom(
            module=module_name,
            names=[ast.alias(name=fn.name, asname=None) for fn in helper_funcs],
            level=0,
        )
        main_tree = ast.Module(body=[import_node] + other + [main_func], type_ignores=[])
        ast.fix_missing_locations(main_tree)
        main_out = ast.unparse(main_tree)
        return {module_name + ".py": helper_code, "main.py": main_out}


# ============================================================
# МОДУЛЬ 13: Кэш успешных фрагментов (Few-Shot Memory)
# ============================================================
class FewShotMemory:
    """Кэширует уже проверенные ФРАГМЕНТЫ (не готовые программы) по
    токенам запроса. Потокобезопасно: запись под мьютексом, автоматический
    .bak файла кэша перед каждой перезаписью."""

    def __init__(self, path="fewshot_cache.json"):
        self.path = path
        self._lock = threading.Lock()
        self.cache = self._load()

    def _load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _save(self):
        try:
            if os.path.exists(self.path):
                try:
                    shutil.copy2(self.path, self.path + ".bak")
                except OSError:
                    pass
            _stream_write_text(self.path, json.dumps(self.cache, ensure_ascii=False, indent=2))
        except OSError:
            pass

    def remember(self, query_tokens, fragment, component_names):
        with self._lock:
            self.cache.append({"tokens": query_tokens, "fragment": fragment, "template": component_names})
            self.cache = self.cache[-200:]
            self._save()

    def recall(self, query_tokens, min_overlap=0.6):
        with self._lock:
            qset = set(query_tokens)
            if not qset:
                return None
            best, best_score = None, 0.0
            for entry in self.cache:
                eset = set(entry["tokens"])
                if not eset:
                    continue
                overlap = len(qset & eset) / len(qset | eset)
                if overlap > best_score:
                    best_score, best = overlap, entry
            return best if best and best_score >= min_overlap else None


# ============================================================
# МОДУЛЬ 14: Локальная система контроля версий (авто-коммиты)
# ============================================================
class VersionControl:
    def __init__(self, repo_dir="."):
        self.repo_dir = repo_dir
        self.use_git = self._git_available()
        if self.use_git:
            self._ensure_git_repo()
        else:
            self.log_dir = os.path.join(repo_dir, VCS_DIR)
            os.makedirs(self.log_dir, exist_ok=True)

    def _git_available(self):
        try:
            subprocess.run(["git", "--version"], capture_output=True, timeout=3)
            return True
        except Exception:
            return False

    def _ensure_git_repo(self):
        if not os.path.isdir(os.path.join(self.repo_dir, ".git")):
            subprocess.run(["git", "init"], cwd=self.repo_dir, capture_output=True)

    def commit(self, filepath, message):
        if self.use_git:
            try:
                subprocess.run(["git", "add", filepath], cwd=self.repo_dir, capture_output=True, timeout=5)
                subprocess.run(["git", "commit", "-m", message], cwd=self.repo_dir, capture_output=True, timeout=5)
                return "git"
            except Exception:
                pass
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        snap_path = os.path.join(self.log_dir, f"{os.path.basename(filepath)}.{ts}.snapshot")
        if os.path.exists(filepath):
            shutil.copy2(filepath, snap_path)
        with open(os.path.join(self.log_dir, "log.txt"), "a", encoding="utf-8") as f:
            f.write(f"{ts} | {filepath} | {message}\n")
        return "local"


# ============================================================
# МОДУЛЬ 15: LLM-бэкенд для синтеза ФРАГМЕНТА (только Гибрид)
# ============================================================
class LLMSynthesizer:
    """Возвращает не целый скрипт, а тело метода: набор плоских
    инструкций, которые AppAssembler вставит внутрь self._build() уже
    существующего класса. Используется только когда ни один компонент
    из ComponentLibrary не подошёл, и только в гибридном режиме."""

    FRAGMENT_SYSTEM_PROMPT = (
        "Ты пишешь ФРАГМЕНТ кода для вставки в уже существующий метод "
        "self._build() класса tkinter-приложения (self.root уже создан). "
        "Верни ТОЛЬКО плоские Python-инструкции (без 'def', без отступа "
        "класса, без markdown, без пояснений) - никаких вложенных def/for/"
        "while: для колбэков используй lambda в одну строку. Создавай "
        "виджеты через self.<имя> = ... и вызывай .pack()/.place() сразу. "
        "Если задача про создание файлов/папок - используй реальные "
        "os.makedirs / open(...).write(...). Код должен быть корректным "
        "Python 3."
    )

    def __init__(self, model=LLM_MODEL, max_tokens=LLM_MAX_TOKENS):
        self.model = model
        self.max_tokens = max_tokens
        self._client = None
        self._init_error = None
        self._try_init_client()

    def _try_init_client(self):
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            self._init_error = "переменная окружения ANTHROPIC_API_KEY не задана"
            return
        try:
            import anthropic
        except ImportError:
            self._init_error = "пакет 'anthropic' не установлен (pip install anthropic)"
            return
        try:
            self._client = anthropic.Anthropic(api_key=api_key)
        except Exception as e:
            self._init_error = f"не удалось создать клиента anthropic: {e}"

    @property
    def available(self):
        return self._client is not None

    @property
    def unavailable_reason(self):
        return self._init_error

    @staticmethod
    def _strip_fences(text):
        t = text.strip()
        if t.startswith("```"):
            t = re.sub(r"^```[a-zA-Z]*\n?", "", t)
            t = re.sub(r"```$", "", t.rstrip())
        return t.strip()

    def synthesize_fragment(self, description):
        if not self.available:
            return None, self._init_error or "LLM-бэкенд не инициализирован"
        try:
            response = self._client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=self.FRAGMENT_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": f"Требование пункта: {description}"}],
            )
            text_parts = [b.text for b in response.content if getattr(b, "type", "") == "text"]
            snippet = self._strip_fences("\n".join(text_parts).strip())
            if not snippet:
                return None, "модель вернула пустой фрагмент"
            return snippet, None
        except Exception as e:
            return None, f"ошибка обращения к LLM: {e}"


# ============================================================
# МОДУЛЬ 16: Самоочистка (Housekeeper)
# ============================================================
# ============================================================
# МОДУЛЬ: Проверка совместимости окружения (авто при старте + периодически)
# ============================================================
class CompatibilityChecker:
    """Реальная, честная проверка окружения при запуске и периодически
    далее - НЕ выдуманная 'адаптация синтаксиса под версию Windows'
    (синтаксис Python от версии ОС не зависит). Проверяет: версию Python
    (нужна для ast.unparse), доступность tkinter/ast/subprocess и т.д.,
    наличие git, пакета anthropic для гибридного режима и системных
    утилит буфера обмена - и делает эти проверки ВИДИМЫМИ в интерфейсе,
    а не молчаливыми. Основная защита от падений на устаревшем окружении
    уже встроена по всему коду через try/except (LLMSynthesizer,
    VersionControl, буфер обмена) - этот модуль лишь явно докладывает
    о результате, ничего не переписывая на лету."""

    MIN_PYTHON = (3, 9)  # ast.unparse появился в 3.9

    def run(self):
        findings = []
        ok = True

        py = sys.version_info
        if (py.major, py.minor) < self.MIN_PYTHON:
            ok = False
            findings.append(
                f"Python {py.major}.{py.minor} слишком старый - нужен "
                f"{self.MIN_PYTHON[0]}.{self.MIN_PYTHON[1]}+ (используется ast.unparse)."
            )
        else:
            findings.append(f"Python {py.major}.{py.minor}.{py.micro}: OK")

        try:
            import tkinter as _tk_check
            findings.append(f"tkinter (Tcl/Tk {_tk_check.TclVersion}): OK")
        except Exception as e:
            ok = False
            findings.append(f"tkinter недоступен: {e}")

        for mod_name in ("ast", "subprocess", "threading", "tempfile", "json"):
            try:
                __import__(mod_name)
            except Exception as e:
                ok = False
                findings.append(f"{mod_name} недоступен: {e}")

        git_ok = shutil.which("git") is not None
        findings.append(
            "git: найден" if git_ok else
            "git: не найден - используется локальный журнал версий .local_vcs/"
        )

        try:
            import anthropic  # noqa: F401
            findings.append("пакет anthropic: доступен (гибридный режим может работать)")
        except ImportError:
            findings.append("пакет anthropic: не установлен (офлайн-режим работает как обычно)")

        clip_tool = None
        if sys.platform.startswith("win"):
            clip_tool = "powershell" if shutil.which("powershell") else None
        elif sys.platform == "darwin":
            clip_tool = "pbpaste" if shutil.which("pbpaste") else None
        else:
            for candidate in ("xclip", "xsel", "wl-paste"):
                if shutil.which(candidate):
                    clip_tool = candidate
                    break
        findings.append(
            f"резервная утилита буфера обмена: {clip_tool}" if clip_tool else
            "резервная утилита буфера обмена не найдена - сработает штатный Tkinter-буфер"
        )

        return {
            "ok": ok,
            "platform": f"{platform.system()} {platform.release()}",
            "findings": findings,
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
        }


class Housekeeper:
    def __init__(self, backups_dir=BACKUPS_DIR, vcs_dir=VCS_DIR, sandbox_tmp_dir=SANDBOX_TMP_DIR,
                 max_backups_per_file=MAX_BACKUPS_PER_FILE, max_snapshots_per_file=MAX_SNAPSHOTS_PER_FILE,
                 max_age_days=MAX_ARTIFACT_AGE_DAYS, max_sandbox_tmp_age_seconds=MAX_SANDBOX_TMP_AGE_SECONDS):
        self.backups_dir = backups_dir
        self.vcs_dir = vcs_dir
        self.sandbox_tmp_dir = sandbox_tmp_dir
        self.max_backups_per_file = max_backups_per_file
        self.max_snapshots_per_file = max_snapshots_per_file
        self.max_age_days = max_age_days
        self.max_sandbox_tmp_age_seconds = max_sandbox_tmp_age_seconds

    def _prune_dated_artifacts(self, directory, pattern_suffixes, max_per_group):
        removed = []
        if not os.path.isdir(directory):
            return removed
        groups = defaultdict(list)
        now = time.time()
        max_age_seconds = self.max_age_days * 86400
        for fname in os.listdir(directory):
            if not any(fname.endswith(suf) for suf in pattern_suffixes):
                continue
            path = os.path.join(directory, fname)
            if not os.path.isfile(path):
                continue
            base = re.split(r"\.\d{8}_\d{6}\.", fname)[0]
            groups[base].append(path)
        for base, paths in groups.items():
            paths.sort(key=lambda p: os.path.getmtime(p), reverse=True)
            for i, path in enumerate(paths):
                age = now - os.path.getmtime(path)
                if age > max_age_seconds or i >= max_per_group:
                    try:
                        os.remove(path)
                        removed.append(os.path.basename(path))
                    except OSError:
                        pass
        return removed

    def prune_backups(self):
        return self._prune_dated_artifacts(self.backups_dir, (".bak",), self.max_backups_per_file)

    def prune_vcs_snapshots(self):
        return self._prune_dated_artifacts(self.vcs_dir, (".snapshot",), self.max_snapshots_per_file)

    def sweep_sandbox_tmp(self):
        removed = []
        if not os.path.isdir(self.sandbox_tmp_dir):
            return removed
        now = time.time()
        for fname in os.listdir(self.sandbox_tmp_dir):
            path = os.path.join(self.sandbox_tmp_dir, fname)
            if not os.path.isfile(path):
                continue
            if now - os.path.getmtime(path) > self.max_sandbox_tmp_age_seconds:
                try:
                    os.remove(path)
                    removed.append(fname)
                except OSError:
                    pass
        return removed

    def run_full_sweep(self):
        summary = {
            "backups_removed": self.prune_backups(),
            "snapshots_removed": self.prune_vcs_snapshots(),
            "sandbox_tmp_removed": self.sweep_sandbox_tmp(),
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
        }
        summary["total"] = sum(len(v) for v in summary.values() if isinstance(v, list))
        return summary


# ============================================================
# Папка-читалка с исходной спецификацией бота
# ============================================================
class DocsFolder:
    SPEC_TEXT = """СПЕЦИФИКАЦИЯ БОТА-ГЕНЕРАТОРА КОДА v5 (текстовая копия для пересборки)

ГЕНЕРАЦИЯ: жёстких целых шаблонов-программ больше нет. Каждый пункт
разбирается на ключевые слова и собирается из МЕЛКИХ compose-able
компонентов (ComponentLibrary): меню, баланс, карты, серверная панель,
панель-раздел, кнопка "играть", создание папки/файла. Один пункт может
одновременно задействовать несколько компонентов ("главное меню с
балансом" -> меню + баланс). Если ни один компонент не подошёл: в
гибридном режиме - фрагмент пишет LLM (только тело метода, не целый
скрипт); иначе создаётся именной каркас под точный текст пункта.

СБОРКА: все пункты Черновика №1 объединяются в ОДНО монолитное tkinter-
приложение (AppAssembler) - один класс GeneratedApp, один self.root,
один mainloop, никаких отдельных run_x() функций. Импорты собираются
один раз и дедуплицируются. Порядок фрагментов внутри одного приложения
определяется не порядком ввода, а зависимостями: если один фрагмент
использует self.<атрибут>, который создаёт другой фрагмент, сборщик
переставляет ФРАГМЕНТЫ ЦЕЛИКОМ (никогда не разрезая их содержимое) так,
чтобы создание всегда шло раньше использования. Содержимое фрагмента при
этом никогда не переписывается - меняется только его позиция.

ВАЛИДАЦИЯ: перед тем как готовый код может попасть в Черновик №3, он
обязательно проходит ast.parse (проверка скобок/отступов/ключевых слов),
при необходимости - автоисправление (SelfCorrector, который правит только
механику синтаксиса, никогда не смысл), затем прогон в локальной
песочнице. Если проверка не проходит даже после автоисправления - сборка
останавливается с понятной ошибкой, а не переносит нерабочий код дальше.

НАДЁЖНОСТЬ ЗАПИСИ: любая запись на диск (кэш фрагментов, итоговый файл)
выполняется под мьютексом и всегда предваряется автоматическим .bak
бэкапом уже существующего файла. Запись итогового текста идёт小 порциями
(потоково), а не одним большим f.write().

Модули: InputInterpreter, ComponentContext, ComponentLibrary, ASTAssembler,
AppAssembler, DependencyAnalyzer, BackupManager, SelfCorrector, Sandbox,
DiffViewer, PEP8Linter, MultiFileRefactor (доступен, но не вызывается
автоматически для монолитного класса - безопасно растащить единый живой
GUI-класс по файлам простыми эвристиками нельзя), FewShotMemory,
VersionControl, LLMSynthesizer (только фрагменты, только гибридный режим),
Housekeeper.

Черновой конвейер (панели интерфейса) не менялся: разбивка на подпункты,
Черновик №1 (мастер-список, ✓ навсегда), Черновик №2 (стадия текущего
шага, красный/зелёный, амнезия), Черновик №3 (финал, ярко-зелёный,
единое приложение целиком).

Если этот .py файл утерян - скопируйте данный текст и попросите
пересобрать бота заново по этой спецификации, модуль за модулем.
"""

    def ensure(self, docs_dir="docs"):
        os.makedirs(docs_dir, exist_ok=True)
        path = os.path.join(docs_dir, "bot_spec_readonly.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.SPEC_TEXT)
        return path


# ============================================================
# ОРКЕСТРАТОР
# ============================================================
class CodeGenBot:
    def __init__(self):
        self.interpreter = InputInterpreter()
        self.components = ComponentLibrary()
        self.assembler = ASTAssembler()
        self.app_assembler = AppAssembler(self.assembler)
        self.dep_analyzer = DependencyAnalyzer()
        self.backup_mgr = BackupManager()
        self.corrector = SelfCorrector()
        self.sandbox = Sandbox()
        self.diff_viewer = DiffViewer()
        self.multifile = MultiFileRefactor()
        self.memory = FewShotMemory()
        self.linter = PEP8Linter()
        self.vcs = VersionControl()
        self.llm = LLMSynthesizer()
        self.housekeeper = Housekeeper()
        self.compat_checker = CompatibilityChecker()
        self.docs = DocsFolder()
        self.docs.ensure()

        self._fragment_counter = 0
        self._write_lock = threading.Lock()

        self.last_housekeeping_summary = self.housekeeper.run_full_sweep()
        self.last_compatibility_report = self.compat_checker.run()

    def run_housekeeping(self):
        summary = self.housekeeper.run_full_sweep()
        self.last_housekeeping_summary = summary
        return summary

    def run_compatibility_check(self):
        report = self.compat_checker.run()
        self.last_compatibility_report = report
        return report

    def is_deletion_request(self, text):
        tokens = self.interpreter.process(text)["tokens"]
        return any(t in DELETE_KEYWORDS for t in tokens)

    def _preview_script(self, fragment):
        """Однострочная обёртка вокруг ОДНОГО фрагмента - только для
        человекочитаемого предпросмотра/самопроверки этого конкретного
        пункта. Настоящая сборка НЕСКОЛЬКИХ фрагментов в одно приложение
        происходит в assemble_final_application()."""
        source, _, _ = self.app_assembler.build([fragment])
        return source

    def _validate_and_sandbox(self, source):
        ok, err = self.assembler.self_check(source)
        corrections = []
        if not ok:
            source, ok, corrections = self.corrector.correct(source)
            if not ok:
                return None, corrections, {"status": "syntax_error", "detail": err}
        source = self.linter.format(source)
        sandbox_result = self.sandbox.run(source)
        return source, corrections, sandbox_result

    def _llm_fragment(self, description):
        if not self.llm.available:
            return None, self.llm.unavailable_reason
        snippet, err = self.llm.synthesize_fragment(description)
        if snippet is None:
            return None, err
        try:
            wrapped = "def _tmp(self):\n" + "\n".join(f"    {l}" for l in snippet.splitlines())
            imports = self.dep_analyzer.scan(wrapped)
        except SyntaxError:
            imports = [{"module": "tkinter", "asname": "tk"}]
        fragment = {"imports": imports, "init_lines": [], "body_lines": snippet.splitlines(), "helper_defs": []}
        return fragment, None

    def generate(self, user_text, mode=MODE_HYBRID):
        with self._write_lock:
            self._fragment_counter += 1
            counter = self._fragment_counter

        interp = self.interpreter.process(user_text)
        meta = {"corrections": interp["corrections"], "notes": [], "mode": mode}

        cached = self.memory.recall(interp["tokens"])
        if cached:
            meta["template"] = cached["template"]
            meta["score"] = "из кэша"
            meta["notes"].append(f"найден похожий проверенный фрагмент в памяти (компоненты: {cached['template']})")
            fragment = cached["fragment"]
            preview = self._preview_script(fragment)
            preview, corrections, sandbox_result = self._validate_and_sandbox(preview)
            meta["self_correction"] = corrections
            meta["sandbox"] = sandbox_result
            if preview is None:
                meta["error"] = "Кэшированный фрагмент не прошёл повторную проверку."
                return None, interp, meta
            meta["fragment"] = fragment
            return preview, interp, meta

        ctx = ComponentContext(counter, user_text)
        matched = self.components.match(interp["tokens"])
        source_label = "component"
        fragment = None

        if matched:
            fragment = self.components.compose(matched, ctx)
        else:
            if mode == MODE_HYBRID and self.llm.available:
                fragment, err = self._llm_fragment(user_text)
                if fragment is not None:
                    source_label = "llm"
                else:
                    meta["notes"].append(f"LLM-синтез фрагмента не удался: {err}")
            elif mode == MODE_OFFLINE:
                meta["notes"].append("режим 'Полный офлайн': обращение к LLM пропущено намеренно")

            if fragment is None:
                fragment = self.components.build_custom_placeholder(ctx)
                source_label = "custom_placeholder"
                meta["notes"].append(
                    "под формулировку пункта не нашлось готовых компонентов - создан "
                    "именной каркас конкретно под этот текст (не заготовка из старого набора)"
                )

        component_names = (
            "custom_placeholder" if source_label == "custom_placeholder"
            else "llm-fragment" if source_label == "llm"
            else "+".join(c["name"] for c in matched)
        )
        meta["template"] = component_names
        meta["score"] = "n/a (сборка компонентов, не жёсткий шаблон)"

        preview = self._preview_script(fragment)
        preview, corrections, sandbox_result = self._validate_and_sandbox(preview)
        meta["self_correction"] = corrections
        meta["sandbox"] = sandbox_result

        if preview is None:
            meta["error"] = f"Самопроверка не прошла даже после автоисправления ({source_label})."
            return None, interp, meta

        meta["fragment"] = fragment

        if sandbox_result.get("status") not in ("crash", "sandbox_error"):
            self.memory.remember(interp["tokens"], fragment, component_names)

        return preview, interp, meta

    def assemble_final_application(self, entries):
        """Финальная сборка: берёт фрагменты ВСЕХ переданных записей (их
        порядок и состав задаёт вызывающая сторона - актуальный список
        Черновика №1, включая уже применённые удаления), строит из них
        ОДНО монолитное приложение и проводит обязательную валидацию
        ПЕРЕД тем, как результат может попасть в Черновик №3."""
        fragments = [e["meta"]["fragment"] for e in entries if e.get("meta", {}).get("fragment")]
        if not fragments:
            return None, {"error": "Нет ни одного валидного фрагмента для сборки."}

        source, _, order_notes = self.app_assembler.build(fragments)

        ok, err = self.assembler.self_check(source)
        corrections = []
        if not ok:
            source, ok, corrections = self.corrector.correct(source)
            if not ok:
                return None, {
                    "error": f"Итоговая сборка не прошла синтаксическую проверку даже после "
                             f"автоисправления: {err}",
                    "self_correction": corrections,
                }

        source = self.linter.format(source)
        lint_issues = self.linter.check(source)
        sandbox_result = self.sandbox.run(source)

        return source, {
            "self_correction": corrections,
            "lint_issues": lint_issues,
            "sandbox": sandbox_result,
            "barrier_count": len(fragments),
            "order_notes": order_notes,
        }

    def save_to_file(self, code, filepath):
        with self._write_lock:
            old_code = None
            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8") as f:
                    old_code = f.read()
            backup_path = self.backup_mgr.backup(filepath)
            diff_text = self.diff_viewer.diff(old_code or "", code, filename=filepath)
            return backup_path, diff_text

    def write_file(self, code, filepath, commit_message="auto-update"):
        with self._write_lock:
            self.backup_mgr.backup(filepath)         # автоматический .bak перед ЛЮБОЙ перезаписью
            _stream_write_text(filepath, code)        # потоковая запись небольшими порциями
            return self.vcs.commit(filepath, commit_message)


# ============================================================
# GUI: киберпанк-интерфейс, автопилот с постоянными галочками
# (не изменялось в рамках этого обновления - только логика генерации/
#  сборки в CodeGenBot и модулях выше)
# ============================================================
class AutoPipelineApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Бот-генератор кода v5 — компоненты вместо шаблонов, единая сборка")
        self.root.geometry("1600x1180")
        self.root.minsize(1250, 900)
        self.root.configure(bg=BG_BLACK)

        self.bot = CodeGenBot()
        self.mode = MODE_OFFLINE

        self.draft1_entries = []
        self._locked_nums = set()
        self._touched_this_run = set()
        self._next_num = 1
        self._busy = False

        self._code_cache = None
        self._code_visible = False
        self._code_window = None

        self._glow_hue = 0.0
        self._neon_frames = []

        self._build_ui()
        self._load_demo_data()
        self._set_mode(self.mode)
        self._update_housekeeping_label(self.bot.last_housekeeping_summary)
        self._update_compat_label(self.bot.last_compatibility_report)
        self._schedule_periodic_housekeeping()
        self._animate_neon()

    # ------------------------------------------------------------------ UI

    def _register_neon(self, widget, hue_offset):
        self._neon_frames.append((widget, hue_offset))

    def _build_ui(self):
        self.bg_canvas = tk.Canvas(self.root, highlightthickness=0, bg=BG_BLACK, bd=0)
        self.bg_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

        outer = tk.Frame(self.root, bg=BG_BLACK)
        outer.pack(fill="both", expand=True, padx=18, pady=18)

        top_bar = tk.Frame(outer, bg=BG_BLACK, highlightthickness=2, highlightbackground=NEON_CYAN)
        top_bar.pack(fill="x", pady=(0, 8))
        self._register_neon(top_bar, 0.0)

        self.btn_send = tk.Button(
            top_bar, text="▶ Отправить (весь цикл автоматически)",
            font=("Segoe UI", 10, "bold"), command=self.run_all,
            bg="#111111", fg=TEXT_WHITE, activeforeground=TEXT_WHITE, activebackground="#222222")
        self.btn_send.pack(side="left", padx=6, pady=6)

        self.btn_paste = tk.Button(
            top_bar, text="📋 Вставить", font=("Segoe UI", 10, "bold"),
            fg=TEXT_WHITE, bg="#12314a", activeforeground=TEXT_WHITE, activebackground="#1a4a6e",
            highlightthickness=2, highlightbackground=NEON_BLUE,
            command=lambda: self._paste_clipboard(self.main_text))
        self.btn_paste.pack(side="left", padx=6, pady=6)

        self.btn_clear_drafts = tk.Button(
            top_bar, text="🧹 Очистить черновики", font=("Segoe UI", 10, "bold"),
            fg=TEXT_WHITE, bg="#3a1414", activeforeground=TEXT_WHITE, activebackground="#5a1c1c",
            highlightthickness=2, highlightbackground=NEON_RED,
            command=self._clear_all_drafts)
        self.btn_clear_drafts.pack(side="left", padx=6, pady=6)

        mode_frame = tk.Frame(top_bar, bg=BG_BLACK)
        mode_frame.pack(side="left", padx=14)
        tk.Label(mode_frame, text="Режим:", font=("Segoe UI", 9), bg=BG_BLACK, fg=TEXT_WHITE).pack(side="left", padx=(0, 4))
        self.btn_offline = tk.Button(mode_frame, text="🔒 Полный офлайн", fg=TEXT_WHITE,
                                      activeforeground=TEXT_WHITE, command=lambda: self._set_mode(MODE_OFFLINE))
        self.btn_offline.pack(side="left", padx=2)
        self.btn_hybrid = tk.Button(mode_frame, text="🌐 Гибридный режим", fg=TEXT_WHITE,
                                     activeforeground=TEXT_WHITE, command=lambda: self._set_mode(MODE_HYBRID))
        self.btn_hybrid.pack(side="left", padx=2)

        self.toggle_code_btn = tk.Button(top_bar, text="▶ Открыть весь код", fg=TEXT_WHITE,
                                          activeforeground=TEXT_WHITE, bg="#111111",
                                          command=self._toggle_code_view)
        self.toggle_code_btn.pack(side="right", padx=6)

        status_col = tk.Frame(top_bar, bg=BG_BLACK)
        status_col.pack(side="right", padx=10)
        self.mode_status_var = tk.StringVar(value="")
        tk.Label(status_col, textvariable=self.mode_status_var, fg=NEON_CYAN, bg=BG_BLACK,
                 font=("Consolas", 9), anchor="e", justify="right").pack(anchor="e")
        self.housekeeping_var = tk.StringVar(value="")
        tk.Label(status_col, textvariable=self.housekeeping_var, fg=NEON_GREEN, bg=BG_BLACK,
                 font=("Consolas", 8), anchor="e", justify="right").pack(anchor="e")
        self.compat_var = tk.StringVar(value="")
        self.compat_label = tk.Label(status_col, textvariable=self.compat_var, bg=BG_BLACK,
                                      font=("Consolas", 8), anchor="e", justify="right")
        self.compat_label.pack(anchor="e")

        main_area = tk.Frame(outer, bg=BG_BLACK)
        main_area.pack(fill="both", expand=True)

        left_frame = tk.Frame(main_area, bg=BG_BLACK, highlightthickness=2, highlightbackground=NEON_PURPLE)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 8))
        self._register_neon(left_frame, 0.15)
        tk.Label(left_frame, text="Главный экран — введите запрос(ы) и нажмите «Отправить» (Ctrl+Enter)",
                 bg=BG_BLACK, fg=NEON_PURPLE, font=("Consolas", 9, "bold")).pack(anchor="w", padx=6, pady=(6, 2))

        self.main_text = scrolledtext.ScrolledText(
            left_frame, wrap="word", font=("Consolas", 10),
            bg=BG_BLACK, fg=TEXT_WHITE, insertbackground=NEON_GREEN,
            highlightthickness=1, highlightbackground=NEON_PURPLE, bd=0)
        self.main_text.pack(fill="both", expand=True, padx=6, pady=(0, 4))
        self.main_text.bind("<Control-Return>", self._on_ctrl_enter)
        self.main_text.bind("<KeyRelease>", lambda e: self._apply_char_rainbow(self.main_text))
        self.main_text.tag_config("char_odd", foreground=NEON_PURPLE)
        self.main_text.tag_config("char_even", foreground=NEON_BLUE)
        self._bind_clipboard_shortcuts(self.main_text, editable=True)
        self._attach_context_menu(self.main_text, editable=True)

        hint = ("Формат: 'N: описание', например «1 добавь главное меню с балансом,\n"
                "2 добавь модуль карт, 3 добавь панель сервера». Слова удали/убери/сотри\n"
                "в описании пункта стирают эту строку из всех черновиков навсегда.\n"
                "Однажды обработанный номер получает несгораемую галочку - изменить\n"
                "его текстом больше нельзя, только удалить и завести заново.")
        tk.Label(left_frame, text=hint, wraplength=540, justify="left",
                 fg="#8899aa", bg=BG_BLACK, font=("Consolas", 8)).pack(fill="x", padx=6, pady=(0, 2))

        self.memory_var = tk.StringVar(value="")
        tk.Label(left_frame, textvariable=self.memory_var, anchor="w",
                 fg=NEON_GREEN, bg=BG_BLACK, font=("Consolas", 9, "bold")).pack(fill="x", padx=6, pady=(0, 6))

        right_frame = tk.Frame(main_area, bg=BG_BLACK)
        right_frame.pack(side="left", fill="both", expand=True)

        # Черновики №1-4: компактная "квадратная" сетка, друг под другом,
        # в узкой левой колонке правой панели.
        right_stack_frame = tk.Frame(right_frame, bg=BG_BLACK, width=440)
        right_stack_frame.pack(side="left", fill="y", padx=(0, 8))
        right_stack_frame.pack_propagate(False)

        # Черновик №5: освободившееся пространство справа, в полный рост.
        right_final_frame = tk.Frame(right_frame, bg=BG_BLACK)
        right_final_frame.pack(side="left", fill="both", expand=True)

        self.draft1_text = self._build_draft_panel(
            right_stack_frame, "Черновик №1 — мастер-список (✓ = навсегда заблокировано)",
            NEON_MAGENTA, 0.35, height=6)
        self.draft2_text = self._build_draft_panel(
            right_stack_frame, "Черновик №2 — стадия текущего шага (амнезия после паузы)",
            NEON_YELLOW, 0.55, height=6)
        self.draft3_text = self._build_draft_panel(
            right_stack_frame, "Черновик №3 — защищённые неделимые блоки (барьеры)",
            NEON_GREEN, 0.75, height=6)
        self.draft4_text = self._build_draft_panel(
            right_stack_frame, "Черновик №4 — новые команды расставлены (проверка зависимостей)",
            NEON_CYAN, 0.85, height=6)
        self.draft5_text = self._build_draft_panel(
            right_final_frame, "Черновик №5 (финал) — единая сборка, весь текст ярко-зелёный",
            NEON_BLUE, 0.95, height=30)

        self.status_var = tk.StringVar(
            value="Готов. Введите запрос(ы) и нажмите «Отправить» — всё остальное бот сделает сам.")
        tk.Label(outer, textvariable=self.status_var, anchor="w", bg=BG_BLACK, fg=TEXT_WHITE,
                 wraplength=1550, justify="left", font=("Consolas", 9)).pack(fill="x", side="bottom", pady=(8, 0))

    def _build_draft_panel(self, parent, title, hue_color, hue_offset, height=10):
        frame = tk.Frame(parent, bg=BG_BLACK, highlightthickness=2, highlightbackground=hue_color)
        frame.pack(fill="both", expand=True, padx=2, pady=4)
        self._register_neon(frame, hue_offset)
        tk.Label(frame, text=title, bg=BG_BLACK, fg=hue_color,
                 font=("Consolas", 9, "bold")).pack(anchor="w", padx=6, pady=(6, 2))
        text_widget = scrolledtext.ScrolledText(
            frame, wrap="word", height=height, font=("Consolas", 9), state="disabled",
            bg=BG_BLACK, fg=TEXT_WHITE, highlightthickness=0, bd=0)
        text_widget.pack(fill="both", expand=True, padx=6, pady=(0, 2))
        self._bind_clipboard_shortcuts(text_widget, editable=False)
        self._attach_context_menu(text_widget, editable=False)
        tk.Button(frame, text="Скопировать текст", fg=TEXT_WHITE, bg="#111111",
                  activeforeground=TEXT_WHITE,
                  command=lambda w=text_widget: self.copy_text(w)).pack(anchor="e", padx=6, pady=(0, 6))
        return text_widget

    def _load_demo_data(self):
        demo = "1: добавь главное меню с балансом\n2: добавь модуль карт\n3: добавь панель сервера"
        self.main_text.insert("1.0", demo)
        self._apply_char_rainbow(self.main_text)
        self._update_memory_label()

    # ------------------------------------------------------- анимация неона

    def _animate_neon(self):
        try:
            w = max(self.bg_canvas.winfo_width(), 100)
            h = max(self.bg_canvas.winfo_height(), 100)
            self.bg_canvas.delete("glow")
            steps = 12
            for i in range(steps):
                hue = (self._glow_hue + i * 0.03) % 1.0
                color = _hue_to_hex(hue)
                inset = i * 1.5
                self.bg_canvas.create_rectangle(inset, inset, w - inset, h - inset,
                                                 outline=color, width=2, tags="glow")

            for widget, offset in self._neon_frames:
                try:
                    color = _hue_to_hex((self._glow_hue + offset) % 1.0)
                    widget.configure(highlightbackground=color, highlightcolor=color)
                except tk.TclError:
                    pass

            self._glow_hue = (self._glow_hue + 0.004) % 1.0
        except tk.TclError:
            pass
        self.root.after(90, self._animate_neon)

    def _apply_char_rainbow(self, widget):
        try:
            content = widget.get("1.0", "end-1c")
        except tk.TclError:
            return
        widget.tag_remove("char_odd", "1.0", "end")
        widget.tag_remove("char_even", "1.0", "end")
        line, col, idx = 1, 0, 0
        for ch in content:
            if ch == "\n":
                line += 1
                col = 0
                idx += 1
                continue
            tag = "char_odd" if idx % 2 == 0 else "char_even"
            widget.tag_add(tag, f"{line}.{col}", f"{line}.{col + 1}")
            col += 1
            idx += 1

    # --------------------------------------------------------- режимы работы

    def _set_mode(self, mode):
        if mode == MODE_HYBRID and not self.bot.llm.available:
            messagebox.showwarning(
                "Гибридный режим недоступен",
                "LLM-бэкенд не настроен: "
                f"{self.bot.llm.unavailable_reason}.\n\n"
                "Бот останется в офлайн-режиме, пока не будут заданы "
                "ANTHROPIC_API_KEY и установлен пакет anthropic.",
            )
            mode = MODE_OFFLINE

        self.mode = mode
        if mode == MODE_OFFLINE:
            self.btn_offline.config(relief="sunken", bg="#123312")
            self.btn_hybrid.config(relief="raised", bg="#111111")
            self.mode_status_var.set("Активен режим: 🔒 Полный офлайн (без сети, только компоненты)")
        else:
            self.btn_offline.config(relief="raised", bg="#111111")
            self.btn_hybrid.config(relief="sunken", bg="#122233")
            self.mode_status_var.set(f"Активен режим: 🌐 Гибридный ({self.bot.llm.model})")

        self.status_var.set(f"Режим переключён на «{self._mode_label(mode)}». "
                             f"Локальный конвейер (черновики, песочница, самоочистка) работает как обычно.")

    def _mode_label(self, mode):
        return "Полный офлайн" if mode == MODE_OFFLINE else "Гибридный режим"

    # --------------------------------------------------------- буфер обмена

    def _bind_clipboard_shortcuts(self, widget, editable):
        def handler(event):
            code = event.keycode
            if code == 86:
                if editable:
                    self._paste_clipboard(widget)
                return "break"
            if code == 67:
                self._copy_selection(widget)
                return "break"
            if code == 88 and editable:
                self._cut_selection(widget)
                return "break"
            if code == 65:
                widget.tag_add("sel", "1.0", "end")
                return "break"
            return None
        widget.bind("<Control-KeyPress>", handler)

    def _attach_context_menu(self, widget, editable):
        menu = tk.Menu(widget, tearoff=0, bg="#111111", fg=TEXT_WHITE,
                        activebackground="#222222", activeforeground=TEXT_WHITE)
        if editable:
            menu.add_command(label="Вставить", command=lambda: self._paste_clipboard(widget))
            menu.add_command(label="Вырезать", command=lambda: self._cut_selection(widget))
        menu.add_command(label="Копировать", command=lambda: self._copy_selection(widget))
        menu.add_command(label="Выделить всё", command=lambda: widget.tag_add("sel", "1.0", "end"))

        def show_menu(event):
            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()
        widget.bind("<Button-3>", show_menu)

    def _read_clipboard_text(self):
        try:
            text = self.root.clipboard_get()
            if text:
                return text
        except tk.TclError:
            pass
        try:
            text = self.main_text.clipboard_get()
            if text:
                return text
        except tk.TclError:
            pass
        try:
            if sys.platform.startswith("win"):
                result = subprocess.run(
                    ["powershell", "-NoProfile", "-Command", "Get-Clipboard"],
                    capture_output=True, text=True, timeout=2,
                )
                if result.returncode == 0 and result.stdout:
                    return result.stdout.rstrip("\r\n")
            elif sys.platform == "darwin":
                result = subprocess.run(["pbpaste"], capture_output=True, text=True, timeout=2)
                if result.returncode == 0 and result.stdout:
                    return result.stdout
            else:
                for cmd in (["xclip", "-selection", "clipboard", "-o"],
                            ["xsel", "--clipboard", "--output"],
                            ["wl-paste"]):
                    try:
                        result = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
                        if result.returncode == 0 and result.stdout:
                            return result.stdout
                    except FileNotFoundError:
                        continue
        except Exception:
            pass
        return None

    def _paste_clipboard(self, widget):
        text = self._read_clipboard_text()
        if text is None:
            messagebox.showwarning(
                "Буфер обмена недоступен",
                "Не удалось прочитать текст ни одним из доступных способов "
                "(Tkinter, а также системные утилиты ОС). Скопируйте текст "
                "заново (Ctrl+C или через контекстное меню источника) и "
                "нажмите «📋 Вставить» ещё раз.",
            )
            self.status_var.set("Вставка не удалась: буфер обмена пуст или недоступен.")
            return
        widget.focus_set()
        was_disabled = widget.cget("state") == "disabled"
        if was_disabled:
            widget.config(state="normal")
        try:
            if widget.tag_ranges("sel"):
                widget.delete("sel.first", "sel.last")
            widget.insert(tk.INSERT, text)
        finally:
            if was_disabled:
                widget.config(state="disabled")
        if widget is self.main_text:
            self._apply_char_rainbow(self.main_text)
            self._update_memory_label()
        self.status_var.set(f"Вставлено из буфера обмена: {len(text)} симв.")

    def _copy_selection(self, widget):
        try:
            if widget.tag_ranges("sel"):
                text = widget.get("sel.first", "sel.last")
                self.root.clipboard_clear()
                self.root.clipboard_append(text)
        except tk.TclError:
            pass

    def _cut_selection(self, widget):
        self._copy_selection(widget)
        was_disabled = widget.cget("state") == "disabled"
        if was_disabled:
            widget.config(state="normal")
        try:
            if widget.tag_ranges("sel"):
                widget.delete("sel.first", "sel.last")
        finally:
            if was_disabled:
                widget.config(state="disabled")
        if widget is self.main_text:
            self._apply_char_rainbow(self.main_text)
            self._update_memory_label()

    # --------------------------------------------------------- самоочистка

    def _update_housekeeping_label(self, summary):
        if not summary:
            self.housekeeping_var.set("")
            return
        self.housekeeping_var.set(
            f"Самоочистка [{summary['timestamp']}]: удалено объектов - {summary['total']}"
        )

    def _update_compat_label(self, report):
        if not report:
            self.compat_var.set("")
            return
        color = NEON_GREEN if report["ok"] else NEON_RED
        status_word = "OK" if report["ok"] else "ЕСТЬ ПРОБЛЕМЫ"
        self.compat_var.set(
            f"Совместимость [{report['timestamp']}]: {status_word} — {report['platform']}"
        )
        self.compat_label.config(fg=color)

    def _schedule_periodic_housekeeping(self):
        self.root.after(HOUSEKEEPING_INTERVAL_MS, self._run_periodic_housekeeping)

    def _run_periodic_housekeeping(self):
        def worker():
            summary = self.bot.run_housekeeping()
            compat_report = self.bot.run_compatibility_check()

            def done():
                self._update_housekeeping_label(summary)
                self._update_compat_label(compat_report)
                if summary["total"] > 0:
                    self.status_var.set(
                        f"Автоочистка выполнена: удалено {summary['total']} устаревших/дублирующих "
                        f"объектов (backups/, .local_vcs/, sandbox_tmp/)."
                    )
            self.root.after(0, done)

        threading.Thread(target=worker, daemon=True).start()
        self._schedule_periodic_housekeeping()

    def _on_ctrl_enter(self, event=None):
        self.run_all()
        return "break"

    # -------------------------------------------------------------- парсинг

    def _parse_lines(self, widget):
        items = {}
        for raw_line in widget.get("1.0", "end").splitlines():
            line = raw_line.strip()
            if not line or ":" not in line:
                continue
            num_part, text_part = line.split(":", 1)
            num_part = num_part.strip()
            if not num_part.isdigit():
                continue
            num = int(num_part)
            text = text_part.strip()
            if not text:
                continue
            items[num] = text
        return items

    def _set_widget_text(self, widget, text, fg=None):
        widget.config(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", text)
        if fg:
            widget.tag_add("plain_color", "1.0", "end")
            widget.tag_config("plain_color", foreground=fg)
        widget.config(state="disabled")

    def _replace_main_text(self, text):
        self.main_text.delete("1.0", "end")
        self.main_text.insert("1.0", text)
        self._apply_char_rainbow(self.main_text)

    def _remove_line_for_num(self, widget, num):
        lines = widget.get("1.0", "end").splitlines()
        new_lines = []
        removed = False
        for line in lines:
            stripped = line.strip()
            if not removed and ":" in stripped:
                num_part = stripped.split(":", 1)[0].strip()
                if num_part.isdigit() and int(num_part) == num:
                    removed = True
                    continue
            new_lines.append(line)
        widget.delete("1.0", "end")
        widget.insert("1.0", "\n".join(new_lines))
        if widget is self.main_text:
            self._apply_char_rainbow(self.main_text)

    # -------------------------------------------------------- разбивка на подпункты

    def _split_long_request_text(self, raw_text):
        raw_text = raw_text.strip()
        if not raw_text:
            return None
        lines = [l.strip() for l in raw_text.splitlines() if l.strip()]

        def is_numbered(l):
            return ":" in l and l.split(":", 1)[0].strip().isdigit()

        if lines and all(is_numbered(l) for l in lines):
            return None

        if len(lines) > 1:
            parts = lines
        else:
            raw = lines[0] if lines else raw_text
            parts = re.split(
                r'[;.!?]+\s*|,?\s+(?:и\s+)?затем\s+|,?\s+потом\s+',
                raw, flags=re.IGNORECASE,
            )
            parts = [p.strip(" .,;!?") for p in parts if p.strip(" .,;!?")]
        return parts

    # ------------------------------------------------------------ занятость

    def _set_busy(self, flag):
        self._busy = flag
        self.btn_send.config(state="disabled" if flag else "normal")

    def _update_memory_label(self):
        pending = len(self._parse_lines(self.main_text))
        in_draft1 = len(self.draft1_entries)
        locked = len(self._locked_nums)
        self.memory_var.set(
            f"На экране: {pending}  |  В Черновике №1: {in_draft1} (заблокировано: {locked})"
        )

    # ======================================================= ТОЧКА ВХОДА

    def run_all(self):
        if self._busy:
            return

        raw = self.main_text.get("1.0", "end")
        parts = self._split_long_request_text(raw)
        if parts is not None:
            if not parts:
                messagebox.showwarning("Пусто", "Введите запрос для обработки.")
                return
            numbered_lines = []
            for part in parts:
                numbered_lines.append(f"{self._next_num}: {part}")
                self._next_num += 1
            self._replace_main_text("\n".join(numbered_lines) + "\n")

        items = self._parse_lines(self.main_text)
        if not items and not self.draft1_entries:
            messagebox.showwarning("Пусто", "Введите хотя бы один запрос.")
            return

        self._touched_this_run = set()
        self._set_busy(True)
        self.status_var.set(
            f"[{self._mode_label(self.mode)}] Бот выполняет весь цикл автоматически: "
            f"сверка → замена/удаление → амнезия → сборка..."
        )
        self._auto_step()

    # --------------------------------------------------- автоматический цикл

    def _find_deletion_candidate(self, current_items):
        for num in sorted(current_items):
            if self.bot.is_deletion_request(current_items[num]):
                return num, current_items[num]
        return None, None

    def _auto_step(self):
        current_items = self._parse_lines(self.main_text)

        del_num, del_desc = self._find_deletion_candidate(current_items)
        if del_num is not None:
            self._perform_deletion(del_num, del_desc)
            return

        draft1_lookup = {e["num"]: e for e in self.draft1_entries}
        candidates = sorted(
            num for num, desc in current_items.items()
            if num not in self._locked_nums
            and (num not in draft1_lookup or draft1_lookup[num]["desc"] != desc)
        )

        if not candidates:
            self._finalize_cycle()
            return

        num = candidates[0]
        desc = current_items[num]

        threading.Thread(target=self._auto_step_worker, args=(num, desc), daemon=True).start()

    def _perform_deletion(self, num, desc):
        preview = (
            f"[✗ УДАЛЕНИЕ] Пункт {num}: {desc}\n"
            f"Эта команда будет полностью стёрта из Черновика №1, Черновика №2\n"
            f"и с главного экрана. Номер {num} освобождается для повторного использования."
        )
        self._set_widget_text(self.draft2_text, preview, fg=NEON_RED)
        self.draft2_text.see("end")

        self.draft1_entries = [e for e in self.draft1_entries if e["num"] != num]
        self._locked_nums.discard(num)
        self._touched_this_run.discard(num)
        self._remove_line_for_num(self.main_text, num)
        self._render_draft1()
        self._update_memory_label()
        self.status_var.set(f"Пункт {num}: помечен на удаление — стёрт из всех черновиков. Продолжаю...")

        def clear_and_continue():
            self._set_widget_text(self.draft2_text, "(Черновик №2 пуст — амнезия)")
            self._auto_step()

        self.root.after(PULSE_DELAY_MS, clear_and_continue)

    def _auto_step_worker(self, num, desc):
        code, interp, meta = self.bot.generate(desc, mode=self.mode)
        if code is None:
            action = ("error", num, {"desc": desc, "error": meta.get("error")})
        else:
            action = ("merge", num, {"desc": desc, "code": code, "meta": meta})

        def done():
            self._apply_step(action)

        self.root.after(0, done)

    def _merge_into_draft1(self, entry):
        num = entry["num"]
        for i, existing in enumerate(self.draft1_entries):
            if existing["num"] == num:
                self.draft1_entries[i] = entry
                return "replaced_in_place"
        self.draft1_entries.append(entry)
        return "appended_at_end"

    def _apply_step(self, action):
        kind, num, payload = action

        if kind == "error":
            messagebox.showwarning("Ошибка генерации", f"Пункт {num}: {payload['error']}")
            self._remove_line_for_num(self.main_text, num)
            self.status_var.set(f"Пункт {num}: ошибка генерации — пропущен, продолжаю...")
            self._update_memory_label()
            self._auto_step()
            return

        entry = {"num": num, "desc": payload["desc"], "code": payload["code"], "meta": payload["meta"]}

        preview = self._describe_entry(entry, "УСПЕШНАЯ ЗАМЕНА / ДОБАВЛЕНИЕ")
        self._set_widget_text(self.draft2_text, preview, fg=NEON_GREEN)
        self.draft2_text.see("end")

        merge_result = self._merge_into_draft1(entry)
        self._locked_nums.add(num)
        self._touched_this_run.add(num)

        self._remove_line_for_num(self.main_text, num)
        self._render_draft1()

        result_ru = ("заменила старую запись на том же месте" if merge_result == "replaced_in_place"
                     else "добавлена в самый конец Черновика №1")
        self.status_var.set(
            f"Пункт {num} ✓ (галочка закреплена навсегда) — {result_ru}. Продолжаю...")
        self._update_memory_label()

        def clear_and_continue():
            self._set_widget_text(self.draft2_text, "(Черновик №2 пуст — амнезия)")
            self._auto_step()

        self.root.after(PULSE_DELAY_MS, clear_and_continue)

    def _describe_entry(self, entry, label):
        meta = entry.get("meta") or {}
        sb = meta.get("sandbox", {})
        source = "синтез LLM" if meta.get("template") == "llm-fragment" else f"компоненты: {meta.get('template')}"
        return (
            f"[{label}] Пункт {entry['num']}: {entry['desc']}\n"
            f"    режим: {self._mode_label(meta.get('mode', self.mode))} | источник: {source} "
            f"(сходство {meta.get('score')}) | песочница: {sb.get('status')}\n"
            f"----- предпросмотр -----\n{entry['code']}\n"
        )

    # --------------------------------------------------------- рендер черновика №1

    def _render_draft1(self):
        self.draft1_text.config(state="normal")
        self.draft1_text.delete("1.0", "end")
        self.draft1_text.tag_config("status_green", foreground=NEON_GREEN)
        self.draft1_text.tag_config("status_yellow", foreground=NEON_YELLOW)

        for e in self.draft1_entries:
            meta = e.get("meta") or {}
            sb = meta.get("sandbox", {})
            source = "синтез LLM" if meta.get("template") == "llm-fragment" else f"компоненты: {meta.get('template')}"
            block = (
                f"[Пункт {e['num']}] ✓ {e['desc']}\n"
                f"    источник: {source} | песочница: {sb.get('status')}\n"
                f"----- предпросмотр -----\n{e['code']}\n\n"
            )
            tag = "status_green" if e["num"] in self._touched_this_run else "status_yellow"
            self.draft1_text.insert("end", block, (tag,))

        if not self.draft1_entries:
            self.draft1_text.insert("end", "(Черновик №1 пуст)")

        self.draft1_text.see("end")
        self.draft1_text.config(state="disabled")

    # ------------------------------------------------- финальная сборка (Черновик №3)

    def _finalize_cycle(self):
        """Единственное место в этом обновлении, где менялась логика
        СБОРКИ (не оформление/цвета/автопрокрутка/галочки): вместо
        конкатенации отдельных независимых скриптов каждого пункта здесь
        теперь вызывается CodeGenBot.assemble_final_application(), которая
        строит ОДНО монолитное приложение и обязательно валидирует его
        перед тем, как текст попадёт в Черновик №3."""
        if not self.draft1_entries:
            self._set_widget_text(self.draft3_text, "(Черновик №1 пуст — нечего собирать)")
            self._set_widget_text(self.draft4_text, "(Черновик №1 пуст — нечего собирать)")
            self._set_widget_text(self.draft5_text, "(Черновик №1 пуст — нечего собирать)")
            self.status_var.set("Нечего собирать — Черновик №1 пуст.")
            self._set_busy(False)
            return

        final_source, assembly_meta = self.bot.assemble_final_application(self.draft1_entries)

        if final_source is None:
            messagebox.showwarning(
                "Сборка не удалась",
                assembly_meta.get("error", "Не удалось собрать единое приложение."),
            )
            self.status_var.set(
                "Сборка Черновика №3 остановлена: итоговый код не прошёл проверку. Черновики не тронуты."
            )
            self._set_busy(False)
            return

        sb = assembly_meta.get("sandbox", {})
        barrier_count = assembly_meta.get("barrier_count", len(self.draft1_entries))
        order_notes = assembly_meta.get("order_notes", [])
        summary_lines = [f"[✓] Пункт {e['num']}: {e['desc']}" for e in self.draft1_entries]

        # ------- Черновик №3: барьеры зафиксированы (видно сразу) -------
        barrier_markers = "\n".join(
            f"[БАРЬЕР_{i}_ПРОЙДЕН_ИЗ_{barrier_count}]" for i in range(1, barrier_count + 1)
        )
        draft3_text = "\n".join([
            "ЧЕРНОВИК №3 — ЗАЩИЩЁННЫЕ НЕДЕЛИМЫЕ БЛОКИ (барьеры зафиксированы)",
            "=" * 72, "",
            barrier_markers, "",
            "-" * 72, "ИТОГОВЫЙ СПИСОК ПУНКТОВ:", "-" * 72, "",
            "\n".join(summary_lines),
        ])
        self.draft3_text.config(state="normal")
        self.draft3_text.delete("1.0", "end")
        self.draft3_text.tag_config("final_green", foreground=FINAL_GREEN)
        self.draft3_text.insert("1.0", draft3_text, ("final_green",))
        self.draft3_text.see("1.0")
        self.draft3_text.config(state="disabled")
        self.status_var.set("Черновик №3 заполнен: барьеры между пунктами зафиксированы. Продолжаю...")

        # ------- Черновик №4: расстановка новых команд (проверка зависимостей) -------
        def fill_draft4():
            draft4_text = "\n".join([
                "ЧЕРНОВИК №4 — НОВЫЕ КОМАНДЫ РАССТАВЛЕНЫ ПО МЕСТАМ",
                "Фрагменты переставляются ТОЛЬКО целиком (барьеры не разрываются),",
                "содержимое каждой команды при этом не меняется - только позиция.",
                "=" * 72, "",
                "\n".join(f"- {note}" for note in order_notes),
            ])
            self.draft4_text.config(state="normal")
            self.draft4_text.delete("1.0", "end")
            self.draft4_text.tag_config("final_green", foreground=FINAL_GREEN)
            self.draft4_text.insert("1.0", draft4_text, ("final_green",))
            self.draft4_text.see("1.0")
            self.draft4_text.config(state="disabled")
            self.status_var.set("Черновик №4 заполнен: проверка зависимостей выполнена. Продолжаю...")
            self.root.after(PULSE_DELAY_MS, fill_draft5)

        # ------- Черновик №5: финальная монолитная сборка -------
        def fill_draft5():
            draft5_text = "\n".join([
                "ЧЕРНОВИК №5 — ФИНАЛЬНАЯ МОНОЛИТНАЯ СБОРКА",
                "Единое tkinter-приложение: один класс, один mainloop, импорты в",
                "единственном экземпляре.",
                f"Синтаксическая проверка перед сборкой: пройдена. Песочница: {sb.get('status')}",
                "=" * 72, "",
                "-" * 72, "ЕДИНЫЙ СОБРАННЫЙ КОД ПРИЛОЖЕНИЯ:", "-" * 72, "",
                final_source,
            ])
            self.draft5_text.config(state="normal")
            self.draft5_text.delete("1.0", "end")
            self.draft5_text.tag_config("final_green", foreground=FINAL_GREEN)
            self.draft5_text.insert("1.0", draft5_text, ("final_green",))
            self.draft5_text.see("1.0")
            self.draft5_text.config(state="disabled")

            self._set_widget_text(self.draft1_text, "(Черновик №1 очищен — итог перенесён в Черновики №3–5)")
            self._set_widget_text(self.draft2_text, "(Черновик №2 очищен — амнезия)")

            self.status_var.set(
                "Готово автоматически: все пункты обработаны, единое приложение собрано в Черновик №5."
            )
            self._update_memory_label()
            self._set_busy(False)

        self.root.after(PULSE_DELAY_MS, fill_draft4)

    # ------------------------------------------------------------ утилиты

    def copy_text(self, widget):
        text = widget.get("1.0", "end").strip()
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.status_var.set("Текст скопирован в буфер обмена.")

    def _clear_all_drafts(self):
        """Стирает содержимое всех 5 черновиков. Строго не трогает
        self.main_text (главное окно ввода) - ни при каких условиях."""
        self.draft1_entries = []
        self._locked_nums = set()
        self._touched_this_run = set()

        placeholder = "(очищено вручную кнопкой «🧹 Очистить черновики»)"
        self._set_widget_text(self.draft1_text, placeholder)
        self._set_widget_text(self.draft2_text, placeholder)
        self._set_widget_text(self.draft3_text, placeholder)
        self._set_widget_text(self.draft4_text, placeholder)
        self._set_widget_text(self.draft5_text, placeholder)

        self._update_memory_label()
        self.status_var.set(
            "Все 5 черновиков очищены. Главное окно ввода не тронуто - можно отправлять заново."
        )

    def _toggle_code_view(self):
        """Открывает ПОЛНЫЙ исходный код приложения в отдельном (втором)
        окне: текст можно выделять и копировать, но нельзя редактировать
        (state='disabled' - Tkinter при этом всё равно разрешает выделение
        и копирование мышью/горячими клавишами, редактирование блокирует)."""
        if self._code_cache is None:
            self._code_cache = self._read_own_source()

        if self._code_window is not None:
            try:
                if self._code_window.winfo_exists():
                    self._code_window.deiconify()
                    self._code_window.lift()
                    self._code_window.focus_force()
                    return
            except tk.TclError:
                pass

        win = tk.Toplevel(self.root)
        win.title("Полный исходный код приложения — только для чтения")
        win.geometry("1000x820")
        win.configure(bg=BG_BLACK)

        tk.Label(
            win, bg=BG_BLACK, fg=NEON_CYAN, font=("Consolas", 9, "bold"), anchor="w",
            text="Полный код бота. Выделение и копирование разрешены, редактирование заблокировано.",
        ).pack(fill="x", padx=8, pady=(8, 2))

        code_view = scrolledtext.ScrolledText(
            win, wrap="none", font=("Consolas", 9),
            bg=BG_BLACK, fg=TEXT_WHITE, insertbackground=TEXT_WHITE,
            highlightthickness=1, highlightbackground=NEON_CYAN, bd=0)
        code_view.pack(fill="both", expand=True, padx=8, pady=(0, 4))
        code_view.insert("1.0", self._code_cache)
        code_view.config(state="disabled")  # только чтение: выделение/копирование не блокируются
        self._bind_clipboard_shortcuts(code_view, editable=False)
        self._attach_context_menu(code_view, editable=False)

        btn_bar = tk.Frame(win, bg=BG_BLACK)
        btn_bar.pack(fill="x")
        tk.Button(
            btn_bar, text="Скопировать весь код", fg=TEXT_WHITE, bg="#111111",
            activeforeground=TEXT_WHITE,
            command=lambda: self.copy_text(code_view),
        ).pack(anchor="e", padx=8, pady=6)

        self._code_window = win

    def _read_own_source(self):
        try:
            path = os.path.abspath(__file__)
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"Не удалось прочитать исходный файл: {e}"


def main():
    root = tk.Tk()
    AutoPipelineApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
