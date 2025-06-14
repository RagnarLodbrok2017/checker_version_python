import tkinter as tk
from tkinter import ttk, messagebox

class LoginWindow:
    """Login window for the Version Checker application."""
    
    def __init__(self, on_login_success):
        self.root = tk.Tk()
        self.root.title("Login - Version Checker")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Set up window close event handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Store callback function
        self.on_login_success = on_login_success
        
        # Define colors - reversed scheme (dark background, light text)
        self.colors = {
            "primary": "#3498db",      # Bright blue
            "secondary": "#1abc9c",   # Teal
            "accent": "#e74c3c",      # Red accent
            "warning": "#e74c3c",     # Red
            "success": "#2ecc71",     # Green
            "background": "#1e272e",  # Dark background
            "text": "#ecf0f1",        # Light text
            "input_bg": "#2d3436",    # Slightly lighter than background
            "highlight": "#00a8ff"    # Bright highlight blue
        }
        
        # Configure style
        self.setup_styles()
        
        # Create GUI elements
        self.create_widgets()
        
        # Center window
        self.center_window()
    
    def setup_styles(self):
        """Configure ttk styles for a modern dark theme look."""
        style = ttk.Style()
        
        # Configure frame style
        style.configure("Card.TFrame", background=self.colors["background"])
        style.configure("InputFrame.TFrame", background=self.colors["input_bg"])
        
        # Configure button styles
        style.configure("Primary.TButton", 
                      font=('Segoe UI', 11, 'bold'),
                      background=self.colors["primary"],
                      foreground=self.colors["text"])
        style.map("Primary.TButton",
                background=[('active', self.colors["highlight"])],
                foreground=[('active', self.colors["text"])])
        
        # Label styles
        style.configure("Title.TLabel", 
                      font=('Segoe UI', 20, 'bold'),
                      background=self.colors["background"],
                      foreground=self.colors["primary"])
        style.configure("Subtitle.TLabel", 
                      font=('Segoe UI', 12, 'bold'),
                      background=self.colors["background"],
                      foreground=self.colors["secondary"])
        style.configure("Info.TLabel", 
                      font=('Segoe UI', 10),
                      background=self.colors["background"],
                      foreground=self.colors["text"])
                      
        # Entry style - need to use tk directly as ttk.Entry styling is limited
        self.entry_style = {
            'font': ('Segoe UI', 11),
            'background': self.colors["input_bg"],
            'foreground': self.colors["text"],
            'insertbackground': self.colors["text"],  # cursor color
            'highlightcolor': self.colors["highlight"],
            'highlightbackground': self.colors["secondary"],
            'highlightthickness': 1,
            'bd': 0,  # no border
            'relief': tk.FLAT
        }
    
    def create_widgets(self):
        """Create and arrange GUI widgets with modern dark theme styling."""
        # Set background color for root window
        self.root.configure(background=self.colors["background"])
        
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="20", style="Card.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header with title and logo effect
        header_frame = ttk.Frame(main_frame, style="Card.TFrame")
        header_frame.pack(fill=tk.X, pady=(0, 25))
        
        # Title with modern styling
        title_label = ttk.Label(
            header_frame, 
            text="VERSION CHECKER", 
            style="Title.TLabel"
        )
        title_label.pack(anchor=tk.CENTER)
        
        # Subtitle
        subtitle_label = ttk.Label(
            header_frame,
            text="Sign in to continue",
            style="Info.TLabel"
        )
        subtitle_label.pack(anchor=tk.CENTER, pady=(5, 0))
        
        # Login form with elevated card effect
        form_frame = ttk.Frame(main_frame, style="Card.TFrame")
        form_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Username field with modern styling
        username_frame = ttk.Frame(form_frame, style="Card.TFrame")
        username_frame.pack(fill=tk.X, pady=10)
        
        username_label = ttk.Label(
            username_frame,
            text="USERNAME",
            style="Subtitle.TLabel"
        )
        username_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Use tk.Entry instead of ttk.Entry for better styling control
        self.username_var = tk.StringVar(value="Elnakieb")
        self.username_entry = tk.Entry(
            username_frame,
            textvariable=self.username_var,
            **self.entry_style
        )
        self.username_entry.pack(fill=tk.X, ipady=8, pady=(0, 5))
        
        # Password field with modern styling
        password_frame = ttk.Frame(form_frame, style="Card.TFrame")
        password_frame.pack(fill=tk.X, pady=10)
        
        password_label = ttk.Label(
            password_frame,
            text="PASSWORD",
            style="Subtitle.TLabel"
        )
        password_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.password_var = tk.StringVar(value="Elnakieb")
        self.password_entry = tk.Entry(
            password_frame,
            textvariable=self.password_var,
            show="•",  # Modern bullet character for password
            **self.entry_style
        )
        self.password_entry.pack(fill=tk.X, ipady=8, pady=(0, 5))
        
        # Login button with hover effect
        button_frame = ttk.Frame(main_frame, style="Card.TFrame")
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.login_btn = ttk.Button(
            button_frame, 
            text="SIGN IN", 
            command=self.login,
            style="Primary.TButton"
        )
        self.login_btn.pack(fill=tk.X, ipady=8)
        
        # Add copyright text at bottom
        copyright_frame = ttk.Frame(main_frame, style="Card.TFrame")
        copyright_frame.pack(fill=tk.X, pady=(20, 0))
        
        copyright_label = ttk.Label(
            copyright_frame,
            text="© 2023 Elnakieb. All rights reserved.",
            style="Info.TLabel",
            font=('Segoe UI', 8)
        )
        copyright_label.pack(anchor=tk.CENTER)
        
        # Bind Enter key to login
        self.root.bind('<Return>', lambda event: self.login())
        
        # Set focus to username field
        self.username_entry.focus()
    
    def center_window(self):
        """Center the window on screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def login(self):
        """Validate login credentials and proceed if valid."""
        username = self.username_var.get()
        password = self.password_var.get()
        
        # Simple validation - in a real app, this would be more secure
        if username == "Elnakieb" and password == "Elnakieb":
            self.root.destroy()  # Close login window
            self.on_login_success()  # Call the success callback
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")
    
    def on_close(self):
        """Handle window close event."""
        self.root.destroy()
        import sys
        sys.exit(0)  # Exit the application
    
    def run(self):
        """Start the login window."""
        self.root.mainloop()