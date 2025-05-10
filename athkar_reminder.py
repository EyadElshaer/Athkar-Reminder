import tkinter as tk
from tkinter import ttk, font, PhotoImage, messagebox
import json
import os
import random
import time
import threading
from datetime import datetime
import winreg
import ctypes
import sys
from PIL import Image, ImageTk, ImageDraw  # For modern UI elements
import io

# Import language support
from languages import get_text, LANGUAGES

# Import version information
from version import get_version

# Try to import pystray for system tray functionality
try:
    import pystray
    from pystray import MenuItem as item
    SYSTEM_TRAY_AVAILABLE = True
except ImportError:
    SYSTEM_TRAY_AVAILABLE = False

class NotificationWindow:
    def __init__(self, message, is_dark_mode):
        self.root = tk.Toplevel()
        self.root.title("")
        self.root.attributes('-topmost', True)
        self.root.overrideredirect(True)
        self.root.attributes('-alpha', 0.0)

        # Windows 11 style colors
        if is_dark_mode:
            bg_color = "#202020"
            fg_color = "#FFFFFF"
            accent_color = "#2D2D2D"
            hover_color = "#404040"
            button_hover = "#404040"
        else:
            bg_color = "#FFFFFF"
            fg_color = "#202020"
            accent_color = "#F5F5F5"
            hover_color = "#E8E8E8"
            button_hover = "#E8E8E8"

        # Set the background color for the window
        self.root.configure(bg=bg_color)

        # Create main container
        self.frame = tk.Frame(self.root, bg=bg_color)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        # Title bar (Windows 11 style - smaller height)
        title_bar = tk.Frame(self.frame, bg=bg_color, height=25)  # Reduced height
        title_bar.pack(fill=tk.X)
        title_bar.pack_propagate(False)

        # Close button container (for hover effect)
        close_container = tk.Frame(title_bar, bg=bg_color)
        close_container.pack(side=tk.RIGHT)

        # Modern close button - smaller
        close_button = tk.Button(close_container, text="✕", command=self.close,
                               font=("Segoe UI", 9), bg=bg_color, fg=fg_color,  # Smaller font
                               relief=tk.FLAT, highlightthickness=0, borderwidth=0,
                               padx=10, pady=4, cursor="hand2")  # Reduced padding
        close_button.pack(side=tk.RIGHT)

        def on_close_enter(e):
            close_container.configure(bg="#C42B1C")
            close_button.configure(bg="#C42B1C", fg="#FFFFFF")
        def on_close_leave(e):
            close_container.configure(bg=bg_color)
            close_button.configure(bg=bg_color, fg=fg_color)

        close_container.bind("<Enter>", on_close_enter)
        close_container.bind("<Leave>", on_close_leave)
        close_button.bind("<Enter>", on_close_enter)
        close_button.bind("<Leave>", on_close_leave)

        # Get available fonts
        available_fonts = font.families()
        best_fonts = [
            "Segoe UI",
            "Calibri",
            "Tahoma",
            "Arial",
            "Verdana",
            "Open Sans",
            "Roboto",
            "Noto Sans",
            "Dubai",
            "Traditional Arabic",
            "Simplified Arabic",
            "Amiri",
            "Arial Unicode MS",
            "Microsoft Uighur"
        ]
        message_font = next((f for f in best_fonts if f in available_fonts), "Arial")

        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        desired_width = min(400, screen_width // 4)  # Reduce the width

        # Content area with message
        content_frame = tk.Frame(self.frame, bg=bg_color)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 5))

        # Message label with adaptive size
        self.message = message
        self.label = tk.Label(content_frame, text=message,
                          bg=bg_color, fg=fg_color,
                          font=(message_font, 18, "bold"),  # Increased font size for better readability
                          justify="center",
                          wraplength=desired_width - 40)  # More text per line
        self.label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)  # Smaller padding

        # Bottom frame (always visible but smaller)
        self.bottom_frame = tk.Frame(self.frame, bg=bg_color, height=30)  # Reduced height
        self.bottom_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.bottom_frame.pack_propagate(False)

        # Modern copy button with background hover effect - smaller
        copy_container = tk.Frame(self.bottom_frame, bg=bg_color)
        copy_container.pack(side=tk.RIGHT, padx=10, pady=2)  # Reduced padding

        copy_button = tk.Button(copy_container, text="📋", command=self.copy_text,
                               bg=bg_color, fg=fg_color,
                               relief=tk.FLAT, borderwidth=0,
                               font=("Segoe UI", 12),  # Smaller font
                               cursor="hand2", padx=6, pady=1)  # Reduced padding
        copy_button.pack()

        def on_copy_enter(e):
            copy_container.configure(bg=button_hover)
            copy_button.configure(bg=button_hover)
        def on_copy_leave(e):
            copy_container.configure(bg=bg_color)
            copy_button.configure(bg=bg_color)

        copy_container.bind("<Enter>", on_copy_enter)
        copy_container.bind("<Leave>", on_copy_leave)
        copy_button.bind("<Enter>", on_copy_enter)
        copy_button.bind("<Leave>", on_copy_leave)

        # Update UI for size calculation
        self.root.update_idletasks()

        # Calculate window size based on actual content
        label_height = self.label.winfo_reqheight()

        # Determine content height based on text length - shorter text gets smaller window
        text_length = len(message)
        if text_length < 30:  # Very short text
            content_height = label_height
            extra_space = 60  # Minimal extra space
        elif text_length < 100:  # Medium text
            content_height = label_height
            extra_space = 65
        else:  # Longer text
            content_height = label_height
            extra_space = 70

        # Set content frame height based on content
        content_frame.configure(height=content_height)
        content_frame.pack_propagate(False)

        # Calculate window size - truly adaptive
        window_width = desired_width
        window_height = content_height + extra_space  # Dynamic spacing
        window_height = max(90, min(400, window_height))  # Even lower minimum

        # Position window
        x_position = screen_width - window_width - 20
        y_position = screen_height - window_height - 40

        # Set window size and position
        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        # Make window corners rounded (Windows 11 style)
        self.root.after(10, lambda: self.make_rounded())

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
            region = CreateRoundRectRgn(0, 0, width, height, 12, 12)  # Windows 11 style corner radius
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
        # Check if self.x and self.y are not None to avoid TypeError
        if self.x is not None and self.y is not None:
            deltax = event.x - self.x
            deltay = event.y - self.y
            x = self.root.winfo_x() + deltax
            y = self.root.winfo_y() + deltay
            self.root.geometry(f"+{x}+{y}")

    def close(self):
        self.fade_out()

class ModernWidget:
    """Base class for creating modern-looking widgets"""
    @staticmethod
    def create_rounded_rectangle(width, height, radius, fill_color):
        """Create a rounded rectangle image for modern buttons/widgets"""
        image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle([(0, 0), (width-1, height-1)], radius, fill=fill_color)
        return ImageTk.PhotoImage(image)

    @staticmethod
    def create_circle(diameter, fill_color):
        """Create a circle image"""
        image = Image.new("RGBA", (diameter, diameter), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.ellipse([(0, 0), (diameter-1, diameter-1)], fill=fill_color)
        return ImageTk.PhotoImage(image)

class ModernButton(tk.Canvas):
    """A modern-looking button with rounded corners and hover effects"""
    def __init__(self, parent, text, command, width=120, height=36, bg_color="#4a6cd4",
                 hover_color="#5a7ce4", text_color="white", radius=18, **kwargs):
        super().__init__(parent, width=width, height=height,
                         highlightthickness=0, bd=0, **kwargs)

        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.command = command

        # Create normal and hover images
        self.normal_img = ModernWidget.create_rounded_rectangle(width, height, radius, bg_color)
        self.hover_img = ModernWidget.create_rounded_rectangle(width, height, radius, hover_color)

        # Create the button
        self.bg_id = self.create_image(width//2, height//2, image=self.normal_img)
        self.text_id = self.create_text(width//2, height//2, text=text, fill=text_color,
                                       font=("Segoe UI", 11, "bold"))  # Increased font size for better readability

        # Bind events
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)

    def _on_enter(self, event):
        self.itemconfig(self.bg_id, image=self.hover_img)

    def _on_leave(self, event):
        self.itemconfig(self.bg_id, image=self.normal_img)

    def _on_click(self, event):
        if self.command:
            self.command()

class ModernToggle(tk.Canvas):
    """A modern toggle switch"""
    def __init__(self, parent, command=None, width=60, height=30, initial_state=False, **kwargs):
        super().__init__(parent, width=width, height=height,
                         highlightthickness=0, bd=0, **kwargs)

        self.width = width
        self.height = height
        self.command = command
        self.is_on = initial_state

        # Colors
        self.on_color = "#4a6cd4"
        self.off_color = "#cccccc"
        self.handle_color = "#ffffff"

        # Create the track
        self.track_radius = height // 2
        self.track_on_img = ModernWidget.create_rounded_rectangle(width, height, self.track_radius, self.on_color)
        self.track_off_img = ModernWidget.create_rounded_rectangle(width, height, self.track_radius, self.off_color)

        # Create the handle
        self.handle_radius = (height - 8) // 2
        self.handle_img = ModernWidget.create_circle(self.handle_radius * 2, self.handle_color)

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
        self.itemconfig(self.track_id, image=self.track_on_img if self.is_on else self.track_off_img)

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

class AthkarReminder:
    def __init__(self):
        self.root = tk.Tk()

        # Load settings or use defaults
        self.load_settings()

        self.root.title(self.get_text("app_title"))
        self.root.geometry("600x650")  # Larger window for modern UI
        self.root.resizable(True, True)  # Allow resizing for better UX
        self.root.minsize(600, 650)    # Set minimum size to prevent UI elements from being hidden

        # Flag to track if app is running in system tray
        self.running_in_tray = False

        # Define colors
        self.colors = {
            "light": {
                "bg": "#f8f9fa",
                "fg": "#212529",
                "accent": "#4a6cd4",
                "accent_hover": "#5a7ce4",
                "card_bg": "#ffffff",
                "border": "#e9ecef"
            },
            "dark": {
                "bg": "#212529",
                "fg": "#f8f9fa",
                "accent": "#4a6cd4",
                "accent_hover": "#5a7ce4",
                "card_bg": "#343a40",
                "border": "#495057"
            }
        }

        # Store images to prevent garbage collection
        self.images = {}

        # Set app icon
        self.icon_path = "icon.ico" if os.path.exists("icon.ico") else None
        if self.icon_path:
            self.root.iconbitmap(default=self.icon_path)

        # Load or create duaas
        self.load_duaas()

        # Initialize timer variables
        self.reminder_interval = tk.IntVar(value=30)  # Set default to 30 minutes
        self.is_running = False
        self.next_reminder_time = None
        self.notification_window = None

        # Theme settings
        self.use_system_theme = True
        self.dark_mode = self.is_dark_mode() if self.use_system_theme else False

        # Setup system tray if available
        if SYSTEM_TRAY_AVAILABLE:
            self.setup_tray_icon()

        # Create UI
        self.create_ui()

        # Apply the current system theme
        self.apply_system_theme()

        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Start the reminder service
        self.start_reminder_service()

    def load_settings(self):
        """Load application settings or use defaults"""
        self.settings_file = "settings.json"

        # Default settings
        self.settings = {
            "language": "English"
        }

        # Try to load settings from file
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    loaded_settings = json.load(f)
                    # Update settings with loaded values
                    self.settings.update(loaded_settings)
            except Exception as e:
                print(f"Error loading settings: {e}")

        # Create language variable
        self.language = tk.StringVar(value=self.settings["language"])

    def save_settings(self):
        """Save application settings to file"""
        # Update settings dictionary with current values
        self.settings["language"] = self.language.get()

        # Save to file
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def get_text(self, key, **kwargs):
        """Get translated text for the current language"""
        return get_text(self.language.get(), key, **kwargs)

    def change_language(self, *args):
        """Change the application language"""
        # Save the new language setting
        self.save_settings()

        # Update the window title
        self.root.title(self.get_text("app_title"))

        # Recreate the UI with the new language
        self.recreate_ui()

    def recreate_ui(self):
        """Recreate the UI with the current language"""
        # Clear the notebook tabs
        for tab in self.notebook.tabs():
            self.notebook.forget(tab)

        # Recreate tabs
        self.create_tabs()

        # Update system tray menu if available
        if SYSTEM_TRAY_AVAILABLE and hasattr(self, 'tray_icon'):
            self.update_tray_menu()

    def setup_tray_icon(self):
        """Setup system tray icon and menu"""
        # Create icon image
        if self.icon_path:
            # Use existing icon if available
            icon_image = Image.open(self.icon_path)
        else:
            # Create a simple icon if no icon file exists
            icon_image = self.create_default_icon()

        # Create system tray menu with translated text
        menu = (
            item(self.get_text('show'), self.show_window),
            item(self.get_text('test_notification'), self.show_test_notification),
            item(self.get_text('exit'), self.exit_app)
        )

        # Create system tray icon
        self.tray_icon = pystray.Icon("AthkarReminder", icon_image, self.get_text("app_title"), menu)

        # Start tray icon in a separate thread
        self.tray_thread = threading.Thread(target=self.tray_icon.run)
        self.tray_thread.daemon = True

    def update_tray_menu(self):
        """Update the system tray menu with the current language"""
        if hasattr(self, 'tray_icon'):
            # Create updated menu with translated text
            menu = (
                item(self.get_text('show'), self.show_window),
                item(self.get_text('test_notification'), self.show_test_notification),
                item(self.get_text('exit'), self.exit_app)
            )

            # Update the tray icon
            self.tray_icon.menu = menu
            self.tray_icon.title = self.get_text("app_title")

    def create_default_icon(self):
        """Create a default icon if no icon file exists"""
        # Create a simple colored square with 'AR' text
        img = Image.new('RGBA', (64, 64), color=(74, 108, 212, 255))  # Using accent color
        d = ImageDraw.Draw(img)

        # Try to use a system font
        try:
            from PIL import ImageFont
            font = ImageFont.truetype("arial.ttf", 32)
            d.text((16, 16), "AR", fill="white", font=font)
        except Exception:
            # Fallback if font loading fails
            d.text((16, 16), "AR", fill="white")

        return img

    def show_window(self):
        """Show the main window"""
        if self.running_in_tray:
            self.running_in_tray = False
            self.root.deiconify()  # Show window
            self.root.lift()       # Bring to front
            self.root.focus_force()  # Focus the window

    def exit_app(self):
        """Exit the application completely"""
        # Stop the tray icon
        if hasattr(self, 'tray_icon'):
            self.tray_icon.stop()

        # Destroy the root window
        self.root.destroy()

        # Exit the application
        os._exit(0)

    def on_close(self):
        """Handle window close event - minimize to tray instead of closing"""
        if SYSTEM_TRAY_AVAILABLE:
            # Show Windows notification the first time
            if not hasattr(self, 'tray_info_shown'):
                self.show_windows_notification(
                    self.get_text("app_title"),
                    self.get_text("tray_info_short")
                )
                self.tray_info_shown = True

            self.root.withdraw()  # Hide the window
            self.running_in_tray = True

            # Start the tray icon if it's not already running
            if hasattr(self, 'tray_thread') and not self.tray_thread.is_alive():
                self.tray_thread.start()
        else:
            # If system tray is not available, just close normally
            self.root.destroy()

    def show_windows_notification(self, title, message):
        """Show a Windows notification"""
        try:
            from win10toast import ToastNotifier
            toaster = ToastNotifier()
            toaster.show_toast(title, message, duration=5, threaded=True)
        except ImportError:
            # Fallback to a simpler notification if win10toast is not available
            try:
                # Use Windows API directly
                ctypes.windll.user32.MessageBoxW(0, message, title, 0x40)
            except:
                # Last resort fallback
                print(f"{title}: {message}")

    def load_duaas(self):
        """Load duaas from file or create default list"""
        self.duaas_file = "duaas.json"

        if os.path.exists(self.duaas_file):
            with open(self.duaas_file, "r", encoding="utf-8") as f:
                self.duaas = json.load(f)
        else:
            # Default duaas from Prophet Mohammed
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

    def create_ui(self):
        style = ttk.Style()
        style.configure("Title.TLabel", font=("Segoe UI", 20, "bold"))
        style.configure("Header.TLabel", font=("Segoe UI", 12))
        style.configure("Content.TLabel", font=("Segoe UI", 11))

        # Add RTL support for Arabic
        style.configure("RTL.TLabel", font=("Dubai", 13), justify="right")
        style.configure("RTL.Title.TLabel", font=("Dubai", 20, "bold"), justify="right")
        style.configure("RTL.Header.TLabel", font=("Dubai", 14), justify="right")
        style.configure("RTL.Content.TLabel", font=("Dubai", 13), justify="right")

        # Configure status label styles
        style.configure("Status.TLabel", font=("Segoe UI", 11), padding=5)
        style.configure("RTL.Status.TLabel", font=("Dubai", 13), justify="right", padding=5)

        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title with modern font - use RTL style for Arabic
        if self.language.get() == "العربية":
            title_label = ttk.Label(main_frame, text=self.get_text("app_title"), style="RTL.Title.TLabel")
        else:
            title_label = ttk.Label(main_frame, text=self.get_text("app_title"), style="Title.TLabel")
        title_label.pack(pady=(0, 15))

        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create tabs with content
        self.create_tabs()

    def create_tabs(self):
        """Create all tabs with their content"""
        # Create tab frames
        self.home_tab = ttk.Frame(self.notebook)
        self.custom_duaas_tab = ttk.Frame(self.notebook)
        self.settings_tab = ttk.Frame(self.notebook)
        self.about_tab = ttk.Frame(self.notebook)

        # Add tabs to notebook with translated text
        self.notebook.add(self.home_tab, text=self.get_text("home_tab"))
        self.notebook.add(self.custom_duaas_tab, text=self.get_text("custom_duaas_tab"))
        self.notebook.add(self.settings_tab, text=self.get_text("settings_tab"))
        self.notebook.add(self.about_tab, text=self.get_text("about_tab"))

        # Create content for each tab
        self.create_home_tab()
        self.create_custom_duaas_tab()
        self.create_settings_tab()
        self.create_about_tab()

    def create_home_tab(self):
        """Create content for the Home tab"""
        # Settings frame
        settings_frame = ttk.LabelFrame(self.home_tab, text=self.get_text("settings_group"), padding="10")
        settings_frame.pack(fill=tk.X, padx=5, pady=5)

        # Interval setting
        interval_frame = ttk.Frame(settings_frame)
        interval_frame.pack(fill=tk.X, padx=5, pady=5)

        interval_label = ttk.Label(interval_frame, text=self.get_text("reminder_interval"), style="Content.TLabel")
        interval_label.pack(side=tk.LEFT, padx=(0, 5))

        interval_values = [1, 5, 10, 15, 30, 60, 120, 180, 240]

        # Create a custom style for the combobox with larger font
        style = ttk.Style()
        style.configure("Custom.TCombobox", font=("Segoe UI", 12))

        interval_combo = ttk.Combobox(interval_frame, textvariable=self.reminder_interval,
                                    values=interval_values, width=5, style="Custom.TCombobox")
        interval_combo.pack(side=tk.LEFT)
        interval_combo.bind("<<ComboboxSelected>>", self.update_interval)
        # Add binding for custom values when user presses Enter
        interval_combo.bind("<Return>", self.update_interval)
        # Add binding for when focus leaves the combobox
        interval_combo.bind("<FocusOut>", self.update_interval)

        # Buttons frame
        buttons_frame = ttk.Frame(self.home_tab)
        buttons_frame.pack(fill=tk.X, padx=5, pady=10)

        self.toggle_button = ttk.Button(buttons_frame, text=self.get_text("pause_reminders"),
                                      command=self.toggle_reminder_service)
        self.toggle_button.pack(side=tk.LEFT, padx=5)

        test_button = ttk.Button(buttons_frame, text=self.get_text("test_notification"),
                                command=self.show_test_notification)
        test_button.pack(side=tk.LEFT, padx=5)

        # Status frame
        status_frame = ttk.LabelFrame(self.home_tab, text=self.get_text("status_group"), padding="10")
        status_frame.pack(fill=tk.X, padx=5, pady=5)

        self.status_var = tk.StringVar(value=self.get_text("status_active", time=""))

        # Use RTL style for Arabic
        if self.language.get() == "العربية":
            status_label = ttk.Label(status_frame, textvariable=self.status_var,
                                  wraplength=350, style="RTL.Status.TLabel", anchor="e")
            # Configure the frame to expand the label to full width for proper RTL alignment
            status_frame.columnconfigure(0, weight=1)
            status_label.grid(row=0, column=0, sticky="e", padx=5, pady=5)
        else:
            status_label = ttk.Label(status_frame, textvariable=self.status_var,
                                  wraplength=350, style="Status.TLabel")
            status_label.pack(fill=tk.X, padx=5, pady=5)

    def create_custom_duaas_tab(self):
        """Create content for the Custom Duaas tab"""
        # Frame for the list of duaas
        duaas_frame = ttk.LabelFrame(self.custom_duaas_tab, text=self.get_text("all_duaas"), padding="10")
        duaas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create a frame for the listbox and scrollbar
        list_frame = ttk.Frame(duaas_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Listbox to display all duaas
        self.duaas_listbox = tk.Listbox(list_frame, height=10, width=50,
                                      yscrollcommand=scrollbar.set,
                                      font=("Segoe UI", 12))  # Increased font size for better readability
        self.duaas_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.duaas_listbox.yview)

        # Populate the listbox with duaas
        for duaa in self.duaas:
            self.duaas_listbox.insert(tk.END, duaa)

        # Frame for adding new duaas
        add_frame = ttk.LabelFrame(self.custom_duaas_tab, text=self.get_text("add_new_duaa"), padding="10")
        add_frame.pack(fill=tk.X, padx=5, pady=5)

        # Text entry for new duaa
        self.new_duaa_var = tk.StringVar()
        style = ttk.Style()
        style.configure("Custom.TEntry", font=("Segoe UI", 12))  # Create custom style with larger font
        new_duaa_entry = ttk.Entry(add_frame, textvariable=self.new_duaa_var, width=50, style="Custom.TEntry")
        new_duaa_entry.pack(fill=tk.X, padx=5, pady=5)

        # Buttons frame for duaa management
        duaa_buttons_frame = ttk.Frame(add_frame)
        duaa_buttons_frame.pack(fill=tk.X, padx=5, pady=5)

        # Add button
        add_button = ttk.Button(duaa_buttons_frame, text=self.get_text("add_duaa"),
                              command=self.add_duaa)
        add_button.pack(side=tk.LEFT, padx=5)

        # Delete button
        delete_button = ttk.Button(duaa_buttons_frame, text=self.get_text("delete_selected"),
                                 command=self.delete_duaa)
        delete_button.pack(side=tk.LEFT, padx=5)

    def create_settings_tab(self):
        """Create content for the Settings tab"""
        # Settings frame
        settings_frame = ttk.LabelFrame(self.settings_tab, text=self.get_text("app_settings"), padding="10")
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Language settings section
        language_frame = ttk.LabelFrame(settings_frame, text=self.get_text("language_settings"), padding="10")
        language_frame.pack(fill=tk.X, padx=5, pady=5)

        # Language selection
        language_label = ttk.Label(language_frame, text=self.get_text("choose_language"),
                                  style="Content.TLabel")
        language_label.pack(side=tk.LEFT, padx=(0, 10), pady=5)

        # Create language dropdown with custom style for better readability
        style = ttk.Style()
        style.configure("Language.TCombobox", font=("Segoe UI", 12))

        language_combo = ttk.Combobox(language_frame, textvariable=self.language,
                                     values=list(LANGUAGES.keys()), width=15,
                                     state="readonly", style="Language.TCombobox")
        language_combo.pack(side=tk.LEFT, padx=5, pady=5)

        # Bind language change event
        language_combo.bind("<<ComboboxSelected>>", self.change_language)

        # Other settings section
        other_frame = ttk.Frame(settings_frame)
        other_frame.pack(fill=tk.X, padx=5, pady=10)

        # Placeholder for future settings
        settings_label = ttk.Label(other_frame,
                                 text=self.get_text("future_settings"),
                                 style="Content.TLabel", wraplength=350)
        settings_label.pack(fill=tk.X, padx=5, pady=10)

        # Auto-start option could be added here
        # Theme selection could be added here
        # Notification position settings could be added here

    def create_about_tab(self):
        """Create content for the About tab"""
        # All colors are now defined in the apply_system_theme method
        # using specific styles for each element

        # Main container with padding
        main_container = ttk.Frame(self.about_tab, padding="15", style="About.TFrame")
        main_container.pack(fill=tk.BOTH, expand=True)

        # Create a canvas for the background
        canvas_frame = ttk.Frame(main_container, style="About.TFrame")
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create a card-like container for content
        content_frame = ttk.Frame(canvas_frame, style="AboutCard.TFrame")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # App title with larger font
        title_frame = ttk.Frame(content_frame, style="AboutCard.TFrame")
        title_frame.pack(fill=tk.X, pady=(20, 5))

        # Use RTL style for Arabic
        if self.language.get() == "العربية":
            title_style = "RTL.AboutTitle.TLabel"
        else:
            title_style = "AboutTitle.TLabel"

        app_title = ttk.Label(title_frame, text=self.get_text("app_title"),
                           style=title_style, font=("Segoe UI", 24, "bold"))  # Increased font size
        app_title.pack(anchor=tk.CENTER)

        # App version - get from version file
        version_text = f"v{get_version()}"
        version_label = ttk.Label(title_frame, text=version_text,
                               style="AboutVersion.TLabel",
                               font=("Segoe UI", 12))  # Increased font size
        version_label.pack(anchor=tk.CENTER, pady=(0, 10))

        # Separator
        separator1 = ttk.Separator(content_frame, orient="horizontal")
        separator1.pack(fill=tk.X, padx=30, pady=10)

        # About content with translated text
        about_text_frame = ttk.Frame(content_frame, style="AboutCard.TFrame")
        about_text_frame.pack(fill=tk.X, padx=20, pady=5)

        # Use RTL style for Arabic
        if self.language.get() == "العربية":
            text_style = "RTL.AboutContent.TLabel"
        else:
            text_style = "AboutContent.TLabel"

        # Adjust wraplength based on language to accommodate Arabic text
        wraplength = 450 if self.language.get() == "العربية" else 400
        justify_style = "right" if self.language.get() == "العربية" else "center"

        about_label = ttk.Label(about_text_frame, text=self.get_text("about_text"),
                              wraplength=wraplength, justify=justify_style, style=text_style)
        about_label.pack(fill=tk.X, padx=10, pady=10)

        # Separator
        separator2 = ttk.Separator(content_frame, orient="horizontal")
        separator2.pack(fill=tk.X, padx=30, pady=10)

        # Developer information
        dev_frame = ttk.Frame(content_frame, style="AboutCard.TFrame")
        dev_frame.pack(fill=tk.X, padx=20, pady=5)

        # Developer title
        # Use appropriate font and style for Arabic
        dev_title_font = ("Dubai", 15, "bold") if self.language.get() == "العربية" else ("Segoe UI", 14, "bold")
        dev_title_style = "RTL.AboutDeveloperTitle.TLabel" if self.language.get() == "العربية" else "AboutDeveloperTitle.TLabel"

        dev_title = ttk.Label(dev_frame, text=self.get_text("developer_title"),
                           style=dev_title_style, font=dev_title_font)
        dev_title.pack(anchor=tk.CENTER, pady=(5, 10))

        # Developer name
        dev_name_font = ("Dubai", 14) if self.language.get() == "العربية" else ("Segoe UI", 13)
        dev_name = ttk.Label(dev_frame, text=self.get_text("developer_name"),
                          style=text_style, font=dev_name_font)
        dev_name.pack(anchor=tk.CENTER)

        # Copyright information
        copyright_frame = ttk.Frame(content_frame, style="AboutCard.TFrame")
        copyright_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=20)  # Increased padding

        current_year = datetime.now().year
        copyright_text = f"© {current_year} {self.get_text('copyright_text')}"

        # Use a larger font for better readability
        font_size = 12 if self.language.get() == "العربية" else 11
        font_family = "Dubai" if self.language.get() == "العربية" else "Segoe UI"

        copyright_label = ttk.Label(copyright_frame, text=copyright_text,
                                 style=text_style, font=(font_family, font_size))
        copyright_label.pack(anchor=tk.CENTER, pady=10)  # Increased padding

    def is_dark_mode(self):
        """Check if Windows is in dark mode"""
        try:
            registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key = winreg.OpenKey(registry, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
            value, regtype = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return value == 0
        except Exception:
            return False

    def apply_system_theme(self):
        """Apply system theme to the application"""
        if self.is_dark_mode():
            # Dark mode
            self.root.configure(bg="#1e1e1e")
            style = ttk.Style()
            style.theme_use("clam")
            style.configure("TFrame", background="#1e1e1e")
            style.configure("TLabel", background="#1e1e1e", foreground="#ffffff")
            style.configure("TLabelframe", background="#1e1e1e", foreground="#ffffff")
            style.configure("TLabelframe.Label", background="#1e1e1e", foreground="#ffffff")
            style.configure("TButton", background="#333333", foreground="#ffffff")

            # Style for card frames in About tab
            style.configure("Card.TFrame", background="#343a40")

            # Special styles for About tab
            style.configure("About.TFrame", background="#1e1e1e")
            style.configure("AboutCard.TFrame", background="#2d3339")
            style.configure("AboutTitle.TLabel", background="#2d3339", foreground="#ffffff", font=("Segoe UI", 24, "bold"))
            style.configure("AboutVersion.TLabel", background="#2d3339", foreground="#6c757d", font=("Segoe UI", 12))
            style.configure("AboutContent.TLabel", background="#2d3339", foreground="#ffffff", font=("Segoe UI", 12))
            style.configure("AboutDeveloperTitle.TLabel", background="#2d3339", foreground="#6c757d", font=("Segoe UI", 14, "bold"))

            # Style for separators
            style.configure("TSeparator", background="#495057")

            # Style for notebook and tabs
            style.configure("TNotebook", background="#1e1e1e", borderwidth=0)
            style.configure("TNotebook.Tab", background="#2d2d2d", foreground="#ffffff",
                          padding=[10, 2], font=("Segoe UI", 11))  # Added font size for better readability
            style.map("TNotebook.Tab",
                    background=[("selected", "#3d3d3d")],
                    foreground=[("selected", "#ffffff")])

            # Style for listbox
            if hasattr(self, 'duaas_listbox'):
                self.duaas_listbox.configure(bg="#2d2d2d", fg="#ffffff")

            # Update RTL styles for Arabic
            style.configure("RTL.TLabel", background="#1e1e1e", foreground="#ffffff")
            style.configure("RTL.Title.TLabel", background="#1e1e1e", foreground="#ffffff")
            style.configure("RTL.Header.TLabel", background="#1e1e1e", foreground="#ffffff")
            style.configure("RTL.Content.TLabel", background="#1e1e1e", foreground="#ffffff")
            style.configure("RTL.Status.TLabel", background="#1e1e1e", foreground="#ffffff")

            # RTL styles for About tab
            style.configure("RTL.AboutTitle.TLabel", background="#2d3339", foreground="#ffffff", font=("Dubai", 24, "bold"), justify="right")
            style.configure("RTL.AboutContent.TLabel", background="#2d3339", foreground="#ffffff", font=("Dubai", 14), justify="right")
            style.configure("RTL.AboutDeveloperTitle.TLabel", background="#2d3339", foreground="#6c757d", font=("Dubai", 16, "bold"), justify="right")
        else:
            # Light mode
            self.root.configure(bg="#f0f0f0")
            style = ttk.Style()
            style.theme_use("clam")
            style.configure("TFrame", background="#f0f0f0")
            style.configure("TLabel", background="#f0f0f0", foreground="#000000")
            style.configure("TLabelframe", background="#f0f0f0", foreground="#000000")
            style.configure("TLabelframe.Label", background="#f0f0f0", foreground="#000000")
            style.configure("TButton", background="#e1e1e1", foreground="#000000")

            # Style for card frames in About tab
            style.configure("Card.TFrame", background="#ffffff")

            # Special styles for About tab
            style.configure("About.TFrame", background="#f0f0f0")
            style.configure("AboutCard.TFrame", background="#ffffff")
            style.configure("AboutTitle.TLabel", background="#ffffff", foreground="#212529", font=("Segoe UI", 24, "bold"))
            style.configure("AboutVersion.TLabel", background="#ffffff", foreground="#6c757d", font=("Segoe UI", 12))
            style.configure("AboutContent.TLabel", background="#ffffff", foreground="#212529", font=("Segoe UI", 12))
            style.configure("AboutDeveloperTitle.TLabel", background="#ffffff", foreground="#6c757d", font=("Segoe UI", 14, "bold"))

            # Style for separators
            style.configure("TSeparator", background="#dee2e6")

            # Style for notebook and tabs
            style.configure("TNotebook", background="#f0f0f0", borderwidth=0)
            style.configure("TNotebook.Tab", background="#e1e1e1", foreground="#000000",
                          padding=[10, 2], font=("Segoe UI", 11))  # Added font size for better readability
            style.map("TNotebook.Tab",
                    background=[("selected", "#ffffff")],
                    foreground=[("selected", "#000000")])

            # Style for listbox
            if hasattr(self, 'duaas_listbox'):
                self.duaas_listbox.configure(bg="#ffffff", fg="#000000")

            # Update RTL styles for Arabic
            style.configure("RTL.TLabel", background="#f0f0f0", foreground="#000000")
            style.configure("RTL.Title.TLabel", background="#f0f0f0", foreground="#000000")
            style.configure("RTL.Header.TLabel", background="#f0f0f0", foreground="#000000")
            style.configure("RTL.Content.TLabel", background="#f0f0f0", foreground="#000000")
            style.configure("RTL.Status.TLabel", background="#f0f0f0", foreground="#000000")

            # RTL styles for About tab
            style.configure("RTL.AboutTitle.TLabel", background="#ffffff", foreground="#212529", font=("Dubai", 24, "bold"), justify="right")
            style.configure("RTL.AboutContent.TLabel", background="#ffffff", foreground="#212529", font=("Dubai", 14), justify="right")
            style.configure("RTL.AboutDeveloperTitle.TLabel", background="#ffffff", foreground="#6c757d", font=("Dubai", 16, "bold"), justify="right")

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

    def update_interval(self, event=None):
        """Update the reminder interval"""
        # Get validated interval value
        interval_value = self.get_validated_interval()

        # Reset timer with new interval if the reminder service is running
        if self.is_running:
            self.next_reminder_time = time.time() + (interval_value * 60)
            self.update_status()

    def update_status(self):
        """Update the status display"""
        if self.is_running and self.next_reminder_time:
            # Calculate time remaining in seconds
            remaining_seconds = max(0, int(self.next_reminder_time - time.time()))

            # Format as hours:minutes:seconds for better readability
            hours, remainder = divmod(remaining_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            # Format time string based on language
            if self.language.get() == "العربية":
                # Arabic format with Arabic numerals
                arabic_numerals = {
                    '0': '٠', '1': '١', '2': '٢', '3': '٣', '4': '٤',
                    '5': '٥', '6': '٦', '7': '٧', '8': '٨', '9': '٩'
                }

                # Convert to Arabic numerals
                hours_str = ''.join(arabic_numerals.get(c, c) for c in str(hours))
                minutes_str = ''.join(arabic_numerals.get(c, c) for c in str(minutes))
                seconds_str = ''.join(arabic_numerals.get(c, c) for c in str(seconds))

                if hours > 0:
                    remaining_str = f"{hours_str} ساعة {minutes_str} دقيقة {seconds_str} ثانية"
                else:
                    remaining_str = f"{minutes_str} دقيقة {seconds_str} ثانية"
            else:
                # English format
                if hours > 0:
                    remaining_str = f"{hours}h {minutes}m {seconds}s"
                else:
                    remaining_str = f"{minutes}m {seconds}s"

            self.status_var.set(self.get_text("status_active", time=remaining_str))

            # Schedule regular updates to the countdown display (more frequent for smoother countdown)
            self.root.after(500, self.update_status)
        else:
            self.status_var.set(self.get_text("status_paused"))

    def toggle_reminder_service(self):
        """Toggle the reminder service on/off"""
        if self.is_running:
            self.stop_reminder_service()
            self.toggle_button.configure(text=self.get_text("resume_reminders"))
        else:
            self.start_reminder_service()
            self.toggle_button.configure(text=self.get_text("pause_reminders"))
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

            # Get the current interval value, ensuring it's an integer
            try:
                interval_value = self.reminder_interval.get()
                if isinstance(interval_value, str) and interval_value.strip():
                    interval_value = int(interval_value.strip())
                    self.reminder_interval.set(interval_value)

                # Ensure the value is positive
                if interval_value <= 0:
                    interval_value = 1
                    self.reminder_interval.set(interval_value)
            except (ValueError, tk.TclError):
                # If conversion fails, reset to default value
                interval_value = 30
                self.reminder_interval.set(interval_value)

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
        dark_mode = self.is_dark_mode()
        self.notification_window = NotificationWindow(message, dark_mode)

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
            self.apply_system_theme()
            self.root.after(5000, check_theme)

        check_theme()
        self.root.mainloop()

if __name__ == "__main__":
    # Check if pystray is required but not installed
    if not SYSTEM_TRAY_AVAILABLE:
        # Show a warning but continue without system tray functionality
        print("Warning: pystray module not found. System tray functionality will be disabled.")
        print("To enable system tray functionality, install pystray with: pip install pystray")

    app = AthkarReminder()
    app.run()