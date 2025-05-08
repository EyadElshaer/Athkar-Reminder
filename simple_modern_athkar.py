import tkinter as tk
from tkinter import ttk, font, messagebox
import json
import os
import random
import time
from PIL import Image, ImageTk, ImageDraw

class ModernUI:
    """Helper class for modern UI elements"""
    @staticmethod
    def create_rounded_rect(width, height, radius, fill_color, outline=None, outline_width=0):
        """Create a rounded rectangle image"""
        image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle([(0, 0), (width-1, height-1)], radius,
                              fill=fill_color, outline=outline, width=outline_width)
        return ImageTk.PhotoImage(image)

    @staticmethod
    def create_circle(diameter, fill_color, outline=None, outline_width=0):
        """Create a circle image"""
        image = Image.new("RGBA", (diameter, diameter), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.ellipse([(0, 0), (diameter-1, diameter-1)],
                    fill=fill_color, outline=outline, width=outline_width)
        return ImageTk.PhotoImage(image)

class ModernButton(tk.Canvas):
    """A modern button with rounded corners and hover effects"""
    def __init__(self, parent, text, command, width=120, height=36,
                 bg_color="#4361ee", hover_color="#3a56d4", text_color="white",
                 radius=18, icon=None, **kwargs):
        super().__init__(parent, width=width, height=height,
                         highlightthickness=0, bd=0, **kwargs)

        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.command = command
        self.width = width
        self.height = height

        # Create button images
        self.normal_img = ModernUI.create_rounded_rect(width, height, radius, bg_color)
        self.hover_img = ModernUI.create_rounded_rect(width, height, radius, hover_color)

        # Create button
        self.bg_id = self.create_image(width//2, height//2, image=self.normal_img)

        # Add icon if provided
        if icon:
            self.icon_id = self.create_image(width//4, height//2, image=icon)
            self.text_id = self.create_text(width//2 + 10, height//2, text=text,
                                          fill=text_color, font=("Segoe UI", 10, "bold"))
        else:
            self.text_id = self.create_text(width//2, height//2, text=text,
                                          fill=text_color, font=("Segoe UI", 10, "bold"))

        # Bind events
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)

    def _on_enter(self, event=None):
        self.itemconfig(self.bg_id, image=self.hover_img)

    def _on_leave(self, event=None):
        self.itemconfig(self.bg_id, image=self.normal_img)

    def _on_click(self, event=None):
        if self.command:
            self.command()

class ModernToggle(tk.Canvas):
    """A modern toggle switch"""
    def __init__(self, parent, command=None, width=60, height=30,
                 initial_state=False, **kwargs):
        super().__init__(parent, width=width, height=height,
                         highlightthickness=0, bd=0, **kwargs)

        self.width = width
        self.height = height
        self.command = command
        self.is_on = initial_state

        # Colors
        self.on_color = "#4361ee"
        self.off_color = "#cccccc"
        self.handle_color = "#ffffff"

        # Create track
        self.track_radius = height // 2
        self.track_on_img = ModernUI.create_rounded_rect(width, height,
                                                      self.track_radius, self.on_color)
        self.track_off_img = ModernUI.create_rounded_rect(width, height,
                                                       self.track_radius, self.off_color)

        # Create handle
        self.handle_radius = (height - 8) // 2
        self.handle_img = ModernUI.create_circle(self.handle_radius * 2, self.handle_color)

        # Initial positions
        self.track_id = self.create_image(width//2, height//2,
                                        image=self.track_on_img if self.is_on else self.track_off_img)

        handle_x = width - self.handle_radius - 4 if self.is_on else self.handle_radius + 4
        self.handle_id = self.create_image(handle_x, height//2, image=self.handle_img)

        # Bind events
        self.bind("<Button-1>", self.toggle)

    def toggle(self, event=None):
        self.is_on = not self.is_on

        # Update visuals
        self.itemconfig(self.track_id,
                       image=self.track_on_img if self.is_on else self.track_off_img)

        # Move handle with animation
        target_x = self.width - self.handle_radius - 4 if self.is_on else self.handle_radius + 4
        current_x = self.coords(self.handle_id)[0]

        # Simple animation
        self._animate_handle(current_x, target_x)

        # Call command if provided
        if self.command:
            self.command(self.is_on)

    def _animate_handle(self, current_x, target_x, steps=10):
        if abs(current_x - target_x) < 2:
            self.coords(self.handle_id, target_x, self.height//2)
            return

        # Calculate step size
        step = (target_x - current_x) / steps
        new_x = current_x + step

        # Move handle
        self.coords(self.handle_id, new_x, self.height//2)

        # Continue animation
        self.after(10, lambda: self._animate_handle(new_x, target_x, steps-1))

    def get(self):
        return self.is_on

    def set(self, state):
        if self.is_on != state:
            self.toggle()

class ModernCard(tk.Frame):
    """A modern card with rounded corners and optional shadow"""
    def __init__(self, parent, bg_color="#ffffff", border_radius=10,
                 padding=15, shadow=True, **kwargs):
        super().__init__(parent, **kwargs)

        self.bg_color = bg_color
        self.border_radius = border_radius
        self.padding = padding

        # Get parent background color safely
        parent_bg = "#f0f0f0"  # Default fallback color
        try:
            # Try to get bg from parent if it's a tk widget
            parent_bg = parent["bg"]
        except (tk.TclError, KeyError):
            try:
                # For ttk widgets, try to get their style's background
                style_name = parent.winfo_class()
                parent_bg = ttk.Style().lookup(style_name, 'background') or parent_bg
            except:
                pass  # Use default fallback color

        # Configure frame
        self.configure(bg=parent_bg, bd=0, highlightthickness=0)

        # Create canvas for rounded corners
        self.canvas = tk.Canvas(self, bg=parent_bg,
                              highlightthickness=0, bd=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Create rounded rectangle
        self.rect_id = None

        # Content frame
        self.content = tk.Frame(self.canvas, bg=bg_color, bd=0, highlightthickness=0)
        self.content_id = self.canvas.create_window(padding, padding,
                                                  anchor=tk.NW, window=self.content)

        # Bind resize event
        self.bind("<Configure>", self._on_resize)

    def _on_resize(self, event):
        # Update canvas size
        width, height = event.width, event.height

        # Create rounded rectangle
        if self.rect_id:
            self.canvas.delete(self.rect_id)

        # Create new rounded rectangle
        self.rect_id = self.canvas.create_rectangle(
            0, 0, width, height,
            fill=self.bg_color, outline="", width=0
        )

        # Update content window size
        content_width = width - 2 * self.padding
        content_height = height - 2 * self.padding
        self.content.configure(width=content_width, height=content_height)

        # Move rectangle behind content
        self.canvas.tag_lower(self.rect_id, self.content_id)

class ModernNotification:
    """Modern notification window with rounded corners and animations"""
    def __init__(self, message, is_dark_mode=False):
        self.root = tk.Toplevel()
        self.root.title("")
        self.root.attributes('-topmost', True)
        self.root.overrideredirect(True)
        self.root.attributes('-alpha', 0.0)

        # Colors based on theme
        if is_dark_mode:
            self.bg_color = "#212529"
            self.fg_color = "#f8f9fa"
            self.accent_color = "#4361ee"
        else:
            self.bg_color = "#f8f9fa"
            self.fg_color = "#212529"
            self.accent_color = "#4361ee"

        # Configure window
        self.root.configure(bg=self.bg_color)

        # Main container
        self.frame = tk.Frame(self.root, bg=self.bg_color)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Title bar
        title_bar = tk.Frame(self.frame, bg=self.bg_color, height=30)
        title_bar.pack(fill=tk.X)
        title_bar.pack_propagate(False)

        # Close button
        close_btn = tk.Button(title_bar, text="✕", command=self.close,
                            font=("Segoe UI", 10), bg=self.bg_color, fg=self.fg_color,
                            relief=tk.FLAT, bd=0, padx=10, pady=0, cursor="hand2")
        close_btn.pack(side=tk.RIGHT)

        # Hover effects for close button
        def on_close_enter(e):
            close_btn.configure(bg="#e63946", fg="#ffffff")
        def on_close_leave(e):
            close_btn.configure(bg=self.bg_color, fg=self.fg_color)

        close_btn.bind("<Enter>", on_close_enter)
        close_btn.bind("<Leave>", on_close_leave)

        # Get best font for Arabic text
        available_fonts = font.families()
        arabic_fonts = [
            "Traditional Arabic", "Simplified Arabic", "Amiri",
            "Arabic Typesetting", "Aldhabi", "Microsoft Uighur",
            "Arial Unicode MS", "Segoe UI", "Tahoma"
        ]
        message_font = next((f for f in arabic_fonts if f in available_fonts), "Arial")

        # Content area
        content_frame = tk.Frame(self.frame, bg=self.bg_color)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        # Message
        self.message = message
        self.label = tk.Label(content_frame, text=message,
                           bg=self.bg_color, fg=self.fg_color,
                           font=(message_font, 16, "bold"),
                           justify="center", wraplength=350)
        self.label.pack(fill=tk.BOTH, expand=True, pady=10)

        # Bottom bar with copy button
        bottom_frame = tk.Frame(self.frame, bg=self.bg_color, height=40)
        bottom_frame.pack(fill=tk.X, side=tk.BOTTOM)

        # Copy button
        copy_btn = tk.Button(bottom_frame, text="📋 Copy", command=self.copy_text,
                           bg=self.bg_color, fg=self.fg_color,
                           relief=tk.FLAT, bd=0, font=("Segoe UI", 10),
                           padx=10, cursor="hand2")
        copy_btn.pack(side=tk.RIGHT, padx=10, pady=5)

        # Hover effects for copy button
        def on_copy_enter(e):
            copy_btn.configure(bg="#f1f3f5", fg=self.fg_color)
        def on_copy_leave(e):
            copy_btn.configure(bg=self.bg_color, fg=self.fg_color)

        copy_btn.bind("<Enter>", on_copy_enter)
        copy_btn.bind("<Leave>", on_copy_leave)

        # Calculate window size
        self.root.update_idletasks()
        width = 400
        height = self.label.winfo_reqheight() + 100  # Add space for title and bottom bars
        height = max(150, min(400, height))  # Constrain height

        # Position window
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = screen_width - width - 20
        y = screen_height - height - 40

        # Set window size and position
        self.root.geometry(f"{width}x{height}+{x}+{y}")

        # Make window corners rounded
        self.root.after(10, self.make_rounded)

        # Fade in animation
        self.fade_in()

        # Auto close after 2 minutes
        self.root.after(120000, self.fade_out)

        # Window dragging
        for widget in [title_bar, self.label, content_frame]:
            widget.bind("<Button-1>", self.start_move)
            widget.bind("<ButtonRelease-1>", self.stop_move)
            widget.bind("<B1-Motion>", self.on_motion)

    def make_rounded(self):
        """Make window corners rounded using Windows API"""
        try:
            from win32gui import GetWindowRect, SetWindowRgn, CreateRoundRectRgn
            hwnd = self.root.winfo_id()
            rect = GetWindowRect(hwnd)
            width = rect[2] - rect[0]
            height = rect[3] - rect[1]
            region = CreateRoundRectRgn(0, 0, width, height, 15, 15)  # More rounded corners
            SetWindowRgn(hwnd, region, True)
        except ImportError:
            pass

    def fade_in(self):
        alpha = self.root.attributes('-alpha')
        if alpha < 1.0:
            alpha += 0.1
            self.root.attributes('-alpha', alpha)
            self.root.after(20, self.fade_in)

    def fade_out(self):
        alpha = self.root.attributes('-alpha')
        if alpha > 0.0:
            alpha -= 0.1
            self.root.attributes('-alpha', alpha)
            self.root.after(20, self.fade_out)
        else:
            self.root.destroy()

    def copy_text(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.message)

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None

    def on_motion(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def close(self):
        self.fade_out()

class SimpleAthkarApp:
    """Modern Athkar Reminder application without system tray dependency"""
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Athkar Reminder")
        self.root.geometry("600x600")  # Larger window for modern UI
        self.root.minsize(500, 500)    # Set minimum size

        # Check if icon exists
        self.icon_path = "icon.ico" if os.path.exists("icon.ico") else None
        if self.icon_path:
            self.root.iconbitmap(default=self.icon_path)

        # Theme detection
        self.is_dark_mode_enabled = self.detect_dark_mode()

        # Define color schemes
        self.colors = {
            "light": {
                "bg": "#f8f9fa",
                "fg": "#212529",
                "accent": "#4361ee",
                "accent_hover": "#3a56d4",
                "card_bg": "#ffffff",
                "border": "#e9ecef",
                "input_bg": "#ffffff",
                "input_border": "#ced4da"
            },
            "dark": {
                "bg": "#212529",
                "fg": "#f8f9fa",
                "accent": "#4361ee",
                "accent_hover": "#3a56d4",
                "card_bg": "#343a40",
                "border": "#495057",
                "input_bg": "#2b3035",
                "input_border": "#495057"
            }
        }

        # Set theme
        self.theme = "dark" if self.is_dark_mode_enabled else "light"

        # Store images to prevent garbage collection
        self.images = {}

        # Load or create duaas
        self.load_duaas()

        # Initialize timer variables
        self.reminder_interval = tk.IntVar(value=30)  # Default: 30 minutes
        self.is_running = False
        self.next_reminder_time = None
        self.notification_window = None

        # Create UI
        self.create_ui()

        # Apply theme
        self.apply_theme()

        # Start reminder service
        self.start_reminder_service()

    def load_duaas(self):
        """Load duaas from file or create default list"""
        self.duaas_file = "duaas.json"

        if os.path.exists(self.duaas_file):
            with open(self.duaas_file, "r", encoding="utf-8") as f:
                self.duaas = json.load(f)
        else:
            # Default duaas
            self.duaas = [
                "اللَّهُمَّ إِنِّي أَسْأَلُكَ الْهُدَى، وَالتُّقَى، وَالْعَفَافَ، وَالْغِنَى",
                "رَبِّ اغْفِرْ لِي خَطِيئَتِي وَجَهْلِي، وَإِسْرَافِي فِي أَمْرِي كُلِّهِ، وَمَا أَنْتَ أَعْلَمُ بِهِ مِنِّي",
                "اللَّهُمَّ اغْفِرْ لِي ذَنْبِي كُلَّهُ، دِقَّهُ وَجِلَّهُ، وَأَوَّلَهُ وَآخِرَهُ، وَعَلَانِيَتَهُ وَسِرَّهُ",
                "اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنْ شَرِّ مَا عَمِلْتُ، وَمِنْ شَرِّ مَا لَمْ أَعْمَلْ",
                "اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنَ الْهَمِّ وَالْحَزَنِ، وَالْعَجْزِ وَالْكَسَلِ، وَالْجُبْنِ وَالْبُخْلِ، وَضَلَعِ الدَّيْنِ وَغَلَبَةِ الرِّجَالِ",
                "اللَّهُمَّ إِنِّي أَسْأَلُكَ الْجَنَّةَ وَأَعُوذُ بِكَ مِنَ النَّارِ",
                "اللَّهُمَّ أَصْلِحْ لِي دِينِي الَّذِي هُوَ عِصْمَةُ أَمْرِي، وَأَصْلِحْ لِي دُنْيَايَ الَّتِي فِيهَا مَعَاشِي",
                "اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنْ زَوَالِ نِعْمَتِكَ، وَتَحَوُّلِ عَافِيَتِكَ، وَفُجَاءَةِ نِقْمَتِكَ، وَجَمِيعِ سَخَطِكَ",
                "لَا إِلَهَ إِلَّا اللَّهُ وَحْدَهُ لَا شَرِيكَ لَهُ، لَهُ الْمُلْكُ وَلَهُ الْحَمْدُ وَهُوَ عَلَى كُلِّ شَيْءٍ قَدِيرٌ",
                "سُبْحَانَ اللَّهِ وَبِحَمْدِهِ، سُبْحَانَ اللَّهِ الْعَظِيمِ"
            ]
            self.save_duaas()

    def save_duaas(self):
        """Save duaas to file"""
        with open(self.duaas_file, "w", encoding="utf-8") as f:
            json.dump(self.duaas, f, ensure_ascii=False, indent=4)

    def detect_dark_mode(self):
        """Detect if system is using dark mode"""
        try:
            import winreg
            registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key = winreg.OpenKey(registry, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return value == 0
        except Exception:
            return False

    def apply_theme(self):
        """Apply current theme to the application"""
        colors = self.colors[self.theme]

        # Configure root window
        self.root.configure(bg=colors["bg"])

        # Configure ttk style
        style = ttk.Style()
        style.theme_use("clam")

        # Configure frames
        style.configure("TFrame", background=colors["bg"])
        style.configure("Card.TFrame", background=colors["card_bg"])

        # Configure labels
        style.configure("TLabel", background=colors["bg"], foreground=colors["fg"])
        style.configure("Card.TLabel", background=colors["card_bg"], foreground=colors["fg"])
        style.configure("Title.TLabel", font=("Segoe UI", 20, "bold"), background=colors["bg"], foreground=colors["fg"])
        style.configure("Subtitle.TLabel", font=("Segoe UI", 14), background=colors["bg"], foreground=colors["fg"])

        # Configure buttons
        style.configure("TButton", background=colors["accent"], foreground="white")
        style.map("TButton",
                background=[("active", colors["accent_hover"])],
                foreground=[("active", "white")])

        # Configure notebook and tabs
        style.configure("TNotebook", background=colors["bg"], borderwidth=0)
        style.configure("TNotebook.Tab", background=colors["card_bg"], foreground=colors["fg"],
                      padding=[15, 5], font=("Segoe UI", 11))
        style.map("TNotebook.Tab",
                background=[("selected", colors["accent"])],
                foreground=[("selected", "white")])

        # Configure listbox if it exists
        if hasattr(self, "duaas_listbox"):
            self.duaas_listbox.configure(bg=colors["input_bg"], fg=colors["fg"],
                                      selectbackground=colors["accent"],
                                      selectforeground="white")

    def create_ui(self):
        """Create the main UI"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # App title
        title_label = ttk.Label(main_frame, text="Athkar Reminder", style="Title.TLabel")
        title_label.pack(pady=(0, 20))

        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Create tabs
        self.home_tab = ttk.Frame(self.notebook)
        self.duaas_tab = ttk.Frame(self.notebook)
        self.settings_tab = ttk.Frame(self.notebook)
        self.about_tab = ttk.Frame(self.notebook)

        # Add tabs to notebook
        self.notebook.add(self.home_tab, text="Home")
        self.notebook.add(self.duaas_tab, text="Custom Duaas")
        self.notebook.add(self.settings_tab, text="Settings")
        self.notebook.add(self.about_tab, text="About")

        # Create content for each tab
        self.create_home_tab()
        self.create_duaas_tab()
        self.create_settings_tab()
        self.create_about_tab()

    def create_home_tab(self):
        """Create content for the Home tab"""
        # Container with padding
        container = ttk.Frame(self.home_tab)
        container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Timer card
        timer_card = ModernCard(container, bg_color=self.colors[self.theme]["card_bg"])
        timer_card.pack(fill=tk.X, pady=10)

        # Timer settings
        timer_title = ttk.Label(timer_card.content, text="Reminder Interval",
                              font=("Segoe UI", 14, "bold"),
                              background=self.colors[self.theme]["card_bg"],
                              foreground=self.colors[self.theme]["fg"])
        timer_title.pack(anchor=tk.W, pady=(0, 10))

        # Interval selection
        interval_frame = ttk.Frame(timer_card.content, style="Card.TFrame")
        interval_frame.pack(fill=tk.X)

        interval_label = ttk.Label(interval_frame, text="Minutes:",
                                 style="Card.TLabel")
        interval_label.pack(side=tk.LEFT, padx=(0, 10))

        # Interval dropdown
        interval_values = [1, 5, 10, 15, 30, 60, 120, 180, 240]
        interval_combo = ttk.Combobox(interval_frame, textvariable=self.reminder_interval,
                                    values=interval_values, width=5)
        interval_combo.pack(side=tk.LEFT)
        interval_combo.bind("<<ComboboxSelected>>", self.update_interval)
        interval_combo.bind("<Return>", self.update_interval)
        interval_combo.bind("<FocusOut>", self.update_interval)

        # Status card
        status_card = ModernCard(container, bg_color=self.colors[self.theme]["card_bg"])
        status_card.pack(fill=tk.X, pady=10)

        # Status content
        status_title = ttk.Label(status_card.content, text="Status",
                               font=("Segoe UI", 14, "bold"),
                               background=self.colors[self.theme]["card_bg"],
                               foreground=self.colors[self.theme]["fg"])
        status_title.pack(anchor=tk.W, pady=(0, 10))

        # Status display
        self.status_var = tk.StringVar(value="Active - Next reminder will appear soon")
        status_label = ttk.Label(status_card.content, textvariable=self.status_var,
                               wraplength=500, style="Card.TLabel")
        status_label.pack(fill=tk.X, pady=5)

        # Control buttons
        buttons_frame = ttk.Frame(container, style="TFrame")
        buttons_frame.pack(fill=tk.X, pady=15)

        # Toggle button
        self.toggle_button = ModernButton(buttons_frame, text="Pause Reminders",
                                        command=self.toggle_reminder_service,
                                        width=150, height=40)
        self.toggle_button.pack(side=tk.LEFT, padx=(0, 10))

        # Test button
        test_button = ModernButton(buttons_frame, text="Test Notification",
                                 command=self.show_test_notification,
                                 width=150, height=40)
        test_button.pack(side=tk.LEFT)

    def create_duaas_tab(self):
        """Create content for the Custom Duaas tab"""
        # Container with padding
        container = ttk.Frame(self.duaas_tab)
        container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Duaas list card
        duaas_card = ModernCard(container, bg_color=self.colors[self.theme]["card_bg"])
        duaas_card.pack(fill=tk.BOTH, expand=True, pady=10)

        # Duaas list title
        duaas_title = ttk.Label(duaas_card.content, text="All Duaas",
                              font=("Segoe UI", 14, "bold"),
                              background=self.colors[self.theme]["card_bg"],
                              foreground=self.colors[self.theme]["fg"])
        duaas_title.pack(anchor=tk.W, pady=(0, 10))

        # List frame
        list_frame = ttk.Frame(duaas_card.content, style="Card.TFrame")
        list_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Listbox
        self.duaas_listbox = tk.Listbox(list_frame, height=10,
                                      yscrollcommand=scrollbar.set,
                                      font=("Segoe UI", 11),
                                      bg=self.colors[self.theme]["input_bg"],
                                      fg=self.colors[self.theme]["fg"],
                                      selectbackground=self.colors[self.theme]["accent"],
                                      selectforeground="white",
                                      borderwidth=1,
                                      relief=tk.SOLID)
        self.duaas_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.duaas_listbox.yview)

        # Populate listbox
        for duaa in self.duaas:
            self.duaas_listbox.insert(tk.END, duaa)

        # Add duaa card
        add_card = ModernCard(container, bg_color=self.colors[self.theme]["card_bg"])
        add_card.pack(fill=tk.X, pady=10)

        # Add duaa title
        add_title = ttk.Label(add_card.content, text="Add New Duaa",
                            font=("Segoe UI", 14, "bold"),
                            background=self.colors[self.theme]["card_bg"],
                            foreground=self.colors[self.theme]["fg"])
        add_title.pack(anchor=tk.W, pady=(0, 10))

        # Entry for new duaa
        self.new_duaa_var = tk.StringVar()
        new_duaa_entry = ttk.Entry(add_card.content, textvariable=self.new_duaa_var,
                                 font=("Segoe UI", 11), width=50)
        new_duaa_entry.pack(fill=tk.X, pady=5)

        # Buttons frame
        duaa_buttons_frame = ttk.Frame(add_card.content, style="Card.TFrame")
        duaa_buttons_frame.pack(fill=tk.X, pady=10)

        # Add button
        add_button = ModernButton(duaa_buttons_frame, text="Add Duaa",
                                command=self.add_duaa,
                                width=120, height=36)
        add_button.pack(side=tk.LEFT, padx=(0, 10))

        # Delete button
        delete_button = ModernButton(duaa_buttons_frame, text="Delete Selected",
                                   command=self.delete_duaa,
                                   width=150, height=36,
                                   bg_color="#e63946", hover_color="#d62b39")
        delete_button.pack(side=tk.LEFT)

    def create_settings_tab(self):
        """Create content for the Settings tab"""
        # Container with padding
        container = ttk.Frame(self.settings_tab)
        container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Settings card
        settings_card = ModernCard(container, bg_color=self.colors[self.theme]["card_bg"])
        settings_card.pack(fill=tk.X, pady=10)

        # Settings title
        settings_title = ttk.Label(settings_card.content, text="Application Settings",
                                 font=("Segoe UI", 14, "bold"),
                                 background=self.colors[self.theme]["card_bg"],
                                 foreground=self.colors[self.theme]["fg"])
        settings_title.pack(anchor=tk.W, pady=(0, 15))

        # Theme setting
        theme_frame = ttk.Frame(settings_card.content, style="Card.TFrame")
        theme_frame.pack(fill=tk.X, pady=5)

        theme_label = ttk.Label(theme_frame, text="Use system theme:",
                              style="Card.TLabel")
        theme_label.pack(side=tk.LEFT, padx=(0, 10))

        self.theme_toggle = ModernToggle(theme_frame, initial_state=True,
                                       command=self.toggle_theme)
        self.theme_toggle.pack(side=tk.LEFT)

        # More settings can be added here

    def create_about_tab(self):
        """Create content for the About tab"""
        # Container with padding
        container = ttk.Frame(self.about_tab)
        container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # About card
        about_card = ModernCard(container, bg_color=self.colors[self.theme]["card_bg"])
        about_card.pack(fill=tk.BOTH, expand=True, pady=10)

        # About content
        about_title = ttk.Label(about_card.content, text="About Athkar Reminder",
                              font=("Segoe UI", 16, "bold"),
                              background=self.colors[self.theme]["card_bg"],
                              foreground=self.colors[self.theme]["fg"])
        about_title.pack(pady=(0, 15))

        about_text = ("Athkar Reminder displays duaas of Prophet Mohammed ﷺ\n\n"
                     "The app runs in the background and shows notifications at your chosen interval. "
                     "It adapts to your system theme automatically.\n\n"
                     "You can drag the notification window to any position on your screen, "
                     "and use the copy button to copy the duaa text.")

        about_label = ttk.Label(about_card.content, text=about_text,
                              wraplength=500, justify="center",
                              style="Card.TLabel")
        about_label.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    def toggle_theme(self, is_system_theme=None):
        """Toggle between system theme and manual theme selection"""
        # This is a placeholder for future theme selection functionality
        pass

    def update_interval(self, event=None):
        """Update the reminder interval"""
        # Get validated interval value
        interval_value = self.get_validated_interval()

        # Reset timer with new interval if the reminder service is running
        if self.is_running:
            self.next_reminder_time = time.time() + (interval_value * 60)
            self.update_status()

    def get_validated_interval(self):
        """Get the current interval value, ensuring it's a valid integer"""
        try:
            interval_value = self.reminder_interval.get()

            # If it's a string (custom input), convert it to integer
            if isinstance(interval_value, str) and interval_value.strip():
                interval_value = int(interval_value.strip())
                # Update the variable with the validated integer
                self.reminder_interval.set(interval_value)

            # Ensure the value is positive
            if interval_value <= 0:
                interval_value = 1
                self.reminder_interval.set(interval_value)

            return interval_value
        except (ValueError, tk.TclError):
            # If conversion fails, reset to default value
            self.reminder_interval.set(30)
            return 30

    def update_status(self):
        """Update the status display"""
        if self.is_running and self.next_reminder_time:
            # Calculate time remaining in seconds
            remaining_seconds = max(0, int(self.next_reminder_time - time.time()))

            # Format as hours:minutes:seconds for better readability
            hours, remainder = divmod(remaining_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            if hours > 0:
                remaining_str = f"{hours}h {minutes}m {seconds}s"
            else:
                remaining_str = f"{minutes}m {seconds}s"

            self.status_var.set(f"Active - Next reminder in {remaining_str}")

            # Schedule regular updates to the countdown display
            self.root.after(500, self.update_status)
        else:
            self.status_var.set("Paused - Reminders are currently disabled")

    def toggle_reminder_service(self):
        """Toggle the reminder service on/off"""
        if self.is_running:
            self.stop_reminder_service()
            self.toggle_button.itemconfig(self.toggle_button.text_id, text="Resume Reminders")
        else:
            self.start_reminder_service()
            self.toggle_button.itemconfig(self.toggle_button.text_id, text="Pause Reminders")
        self.update_status()

    def start_reminder_service(self):
        """Start the reminder service"""
        self.is_running = True

        # Get validated interval value
        interval_value = self.get_validated_interval()

        self.next_reminder_time = time.time() + (interval_value * 60)
        self.update_status()  # Start updating the status immediately
        self.check_reminder_time()

    def stop_reminder_service(self):
        """Stop the reminder service"""
        self.is_running = False
        self.next_reminder_time = None
        self.update_status()

    def check_reminder_time(self):
        """Check if it's time to show a reminder"""
        if not self.is_running:
            self.root.after(1000, self.check_reminder_time)
            return

        current_time = time.time()

        # First reminder or time to show next reminder
        if current_time >= self.next_reminder_time:
            self.show_notification()

            # Get validated interval value
            interval_value = self.get_validated_interval()

            self.next_reminder_time = current_time + (interval_value * 60)

        # Schedule next check
        self.root.after(1000, self.check_reminder_time)

    def get_random_duaa(self):
        """Get a random duaa from the list"""
        return random.choice(self.duaas)

    def show_notification(self):
        """Show a notification with a random duaa"""
        duaa = self.get_random_duaa()
        self.create_notification(duaa)

    def create_notification(self, message):
        """Create a custom notification window"""
        # Close previous notification if it exists
        if hasattr(self, 'notification_window') and self.notification_window is not None:
            try:
                self.notification_window.close()
            except:
                pass

        # Create new notification
        self.notification_window = ModernNotification(message, self.is_dark_mode_enabled)

    def show_test_notification(self):
        """Show a test notification"""
        self.show_notification()

    def add_duaa(self):
        """Add a new duaa to the list"""
        new_duaa = self.new_duaa_var.get().strip()
        if new_duaa:
            # Add to the list
            self.duaas.append(new_duaa)
            # Add to the listbox
            self.duaas_listbox.insert(tk.END, new_duaa)
            # Save to file
            self.save_duaas()
            # Clear the entry
            self.new_duaa_var.set("")

    def delete_duaa(self):
        """Delete the selected duaa"""
        selected = self.duaas_listbox.curselection()
        if selected:
            # Get the index
            index = selected[0]
            # Remove from the listbox
            self.duaas_listbox.delete(index)
            # Remove from the list
            self.duaas.pop(index)
            # Save to file
            self.save_duaas()

    def run(self):
        """Run the application"""
        # Start timer display updates
        self.update_status()

        # Check for theme changes every 5 seconds
        def check_theme():
            current_dark_mode = self.detect_dark_mode()
            if current_dark_mode != self.is_dark_mode_enabled:
                self.is_dark_mode_enabled = current_dark_mode
                self.theme = "dark" if self.is_dark_mode_enabled else "light"
                self.apply_theme()
            self.root.after(5000, check_theme)

        check_theme()
        self.root.mainloop()

# Run the application
if __name__ == "__main__":
    app = SimpleAthkarApp()
    app.run()
