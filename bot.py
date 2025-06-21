import os
import time
import requests
import random
import re
from dotenv import load_dotenv, set_key
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

# Load .env file
load_dotenv()

# Initialize environment variables
USER_TOKEN = os.getenv("DISCORD_USER_TOKEN", "")
CHANNEL_IDS = os.getenv("DISCORD_CHANNEL_IDS", "")
channel_list = [cid.strip() for cid in CHANNEL_IDS.split(',')] if CHANNEL_IDS else []

class DiscordMessageSender:
    def __init__(self, root):
        self.root = root
        self.root.title("Discord Message Sender")
        self.root.geometry("650x550")
        self.root.resizable(True, True)
        self.root.configure(bg="#2C2F33")
        
        # Set dark theme for ttk widgets
        self.style = ttk.Style()
        self.style.theme_use('default')
        
        # Configure dark theme
        self.style.configure('TNotebook', background='#2C2F33', borderwidth=0)
        self.style.configure('TNotebook.Tab', 
                            background='#36393F', 
                            foreground='#FFFFFF',
                            padding=[10, 5],
                            borderwidth=0)
        self.style.map('TNotebook.Tab', 
                      background=[('selected', '#7289DA')],
                      foreground=[('selected', '#FFFFFF')])
        
        # Configure frame styles
        self.style.configure('TFrame', background='#2C2F33')
        self.style.configure('TLabelframe', 
                            background='#2C2F33', 
                            foreground='#FFFFFF',
                            borderwidth=1,
                            relief='solid',
                            bordercolor='#36393F')
        self.style.configure('TLabelframe.Label', 
                            background='#2C2F33', 
                            foreground='#FFFFFF')
        
        self.running = False
        self.message_count = 0
        self.min_interval = 90  # Default min interval in seconds
        self.max_interval = 150  # Default max interval in seconds
        self.interval = random.randint(self.min_interval, self.max_interval)
        self.channel_entries = []  # To store channel ID entry widgets
        
        self.setup_ui()
        
    def setup_ui(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root, style='TNotebook')
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Main tab
        self.main_frame = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(self.main_frame, text="Main")
        
        # Settings tab
        self.settings_frame = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(self.settings_frame, text="Settings")
        
        self.setup_main_tab()
        self.setup_settings_tab()
        
    def setup_main_tab(self):
        # Header
        header_frame = tk.Frame(self.main_frame, bg="#2C2F33")
        header_frame.pack(pady=10, fill="x")
        
        title_label = tk.Label(
            header_frame, 
            text="Discord Message Sender", 
            fg="#7289DA", 
            bg="#2C2F33", 
            font=("Arial", 18, "bold")
        )
        title_label.pack()
        
        warning_label = tk.Label(
            header_frame,
            text="Educational Use Only - Violates Discord's ToS",
            fg="#FF5555",
            bg="#2C2F33",
            font=("Arial", 9)
        )
        warning_label.pack(pady=(5, 0))
        
        # Configuration Frame
        config_frame = tk.LabelFrame(
            self.main_frame, 
            text="Message Configuration", 
            bg="#2C2F33", 
            fg="#FFFFFF",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=10,
            bd=1,
            relief="solid",
            highlightbackground="#36393F"
        )
        config_frame.pack(fill="x", padx=5, pady=10)
        
        # Message Input
        tk.Label(
            config_frame, 
            text="Message:", 
            bg="#2C2F33", 
            fg="#FFFFFF",
            anchor="w"
        ).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.message_var = tk.StringVar(value="Hello from your user account!")
        message_entry = tk.Entry(
            config_frame, 
            textvariable=self.message_var,
            width=50,
            bg="#40444B",
            fg="#FFFFFF",
            insertbackground="#FFFFFF",
            highlightbackground="#36393F",
            highlightthickness=1
        )
        message_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew", columnspan=2)
        
        # Interval Inputs (in seconds)
        tk.Label(
            config_frame, 
            text="Min Interval (sec):", 
            bg="#2C2F33", 
            fg="#FFFFFF",
            anchor="w"
        ).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        
        self.min_interval_var = tk.IntVar(value=90)
        min_interval_spin = tk.Spinbox(
            config_frame, 
            from_=10, 
            to=600, 
            increment=5,
            textvariable=self.min_interval_var,
            width=5,
            bg="#40444B",
            fg="#FFFFFF",
            highlightbackground="#36393F",
            highlightthickness=1
        )
        min_interval_spin.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        tk.Label(
            config_frame, 
            text="Max Interval (sec):", 
            bg="#2C2F33", 
            fg="#FFFFFF",
            anchor="w"
        ).grid(row=2, column=0, padx=5, pady=5, sticky="w")
        
        self.max_interval_var = tk.IntVar(value=150)
        max_interval_spin = tk.Spinbox(
            config_frame, 
            from_=10, 
            to=600, 
            increment=5,
            textvariable=self.max_interval_var,
            width=5,
            bg="#40444B",
            fg="#FFFFFF",
            highlightbackground="#36393F",
            highlightthickness=1
        )
        max_interval_spin.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        # Channel selection
        tk.Label(
            config_frame, 
            text="Target Channels:", 
            bg="#2C2F33", 
            fg="#FFFFFF",
            anchor="w"
        ).grid(row=3, column=0, padx=5, pady=5, sticky="w")
        
        self.channel_vars = []
        self.channel_checks = []
        channel_frame = tk.Frame(config_frame, bg="#2C2F33")
        channel_frame.grid(row=3, column=1, padx=5, pady=5, sticky="w", columnspan=2)
        
        # Create checkboxes for up to 5 channels
        for i in range(5):
            var = tk.BooleanVar(value=True)
            self.channel_vars.append(var)
            chk = tk.Checkbutton(
                channel_frame,
                text=f"Channel {i+1}",
                variable=var,
                bg="#2C2F33",
                fg="#FFFFFF",
                selectcolor="#36393F",
                activebackground="#2C2F33",
                activeforeground="#FFFFFF"
            )
            chk.pack(side="left", padx=5)
            self.channel_checks.append(chk)
        
        # Status Frame
        status_frame = tk.LabelFrame(
            self.main_frame, 
            text="Status", 
            bg="#2C2F33", 
            fg="#FFFFFF",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=10,
            bd=1,
            relief="solid",
            highlightbackground="#36393F"
        )
        status_frame.pack(fill="x", padx=5, pady=(10, 5))
        
        self.status_var = tk.StringVar(value="Ready to start")
        status_label = tk.Label(
            status_frame, 
            textvariable=self.status_var,
            fg="#57F287",
            bg="#2C2F33",
            font=("Arial", 10)
        )
        status_label.pack(anchor="w")
        
        # Counters
        counter_frame = tk.Frame(status_frame, bg="#2C2F33")
        counter_frame.pack(fill="x", pady=(10, 0))
        
        tk.Label(
            counter_frame, 
            text="Messages Sent:", 
            bg="#2C2F33", 
            fg="#FFFFFF"
        ).pack(side="left")
        
        self.count_var = tk.StringVar(value="0")
        count_label = tk.Label(
            counter_frame, 
            textvariable=self.count_var,
            fg="#57F287",
            bg="#2C2F33",
            font=("Arial", 10, "bold")
        )
        count_label.pack(side="left", padx=(5, 15))
        
        # Next Message
        tk.Label(
            counter_frame, 
            text="Next Message In:", 
            bg="#2C2F33", 
            fg="#FFFFFF"
        ).pack(side="left")
        
        self.next_var = tk.StringVar(value="--:--")
        next_label = tk.Label(
            counter_frame, 
            textvariable=self.next_var,
            fg="#57F287",
            bg="#2C2F33",
            font=("Arial", 10, "bold")
        )
        next_label.pack(side="left", padx=5)
        
        # Control Buttons
        button_frame = tk.Frame(self.main_frame, bg="#2C2F33")
        button_frame.pack(pady=20)
        
        self.start_button = tk.Button(
            button_frame,
            text="Start Sending",
            command=self.start_sending,
            bg="#7289DA",
            fg="#FFFFFF",
            padx=15,
            pady=5,
            font=("Arial", 10, "bold"),
            bd=0,
            highlightthickness=0
        )
        self.start_button.pack(side="left", padx=10)
        
        self.stop_button = tk.Button(
            button_frame,
            text="Stop Sending",
            command=self.stop_sending,
            bg="#ED4245",
            fg="#FFFFFF",
            padx=15,
            pady=5,
            font=("Arial", 10, "bold"),
            state="disabled",
            bd=0,
            highlightthickness=0
        )
        self.stop_button.pack(side="left", padx=10)
        
        # Log Frame
        log_frame = tk.LabelFrame(
            self.main_frame, 
            text="Activity Log", 
            bg="#2C2F33", 
            fg="#FFFFFF",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=10,
            bd=1,
            relief="solid",
            highlightbackground="#36393F"
        )
        log_frame.pack(fill="both", expand=True, padx=5, pady=(5, 10))
        
        self.log_text = tk.Text(
            log_frame,
            height=6,
            bg="#40444B",
            fg="#FFFFFF",
            insertbackground="#FFFFFF",
            highlightbackground="#36393F",
            highlightthickness=1
        )
        self.log_text.pack(fill="both", expand=True)
        self.log_text.config(state="disabled")
        
        # Suggested settings frame
        settings_frame = tk.Frame(self.main_frame, bg="#2C2F33")
        settings_frame.pack(fill="x", padx=5, pady=(0, 5))
        
        tk.Label(
            settings_frame,
            text="Suggested Settings:",
            bg="#2C2F33",
            fg="#FFFFFF"
        ).pack(anchor="w")
        
        suggestions = tk.Label(
            settings_frame,
            text="Anti-detection: 90-150s | Quick test: 10-20s | Slow mode: 300-600s",
            bg="#2C2F33",
            fg="#B9BBBE",
            font=("Arial", 8)
        )
        suggestions.pack(anchor="w")
        
    def setup_settings_tab(self):
        # Token settings
        token_frame = tk.LabelFrame(
            self.settings_frame,
            text="Discord User Token",
            bg="#2C2F33",
            fg="#FFFFFF",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=10,
            bd=1,
            relief="solid",
            highlightbackground="#36393F"
        )
        token_frame.pack(fill="x", padx=5, pady=10)
        
        tk.Label(
            token_frame,
            text="Your Discord token gives full access to your account.",
            bg="#2C2F33",
            fg="#FF5555",
            wraplength=550
        ).pack(anchor="w", pady=(0, 10))
        
        self.token_var = tk.StringVar(value=USER_TOKEN)
        token_entry = tk.Entry(
            token_frame,
            textvariable=self.token_var,
            width=70,
            bg="#40444B",
            fg="#FFFFFF",
            show="*",
            insertbackground="#FFFFFF",
            highlightbackground="#36393F",
            highlightthickness=1
        )
        token_entry.pack(fill="x", padx=5, pady=5)
        
        # Token buttons
        token_button_frame = tk.Frame(token_frame, bg="#2C2F33")
        token_button_frame.pack(fill="x", pady=5)
        
        tk.Button(
            token_button_frame,
            text="Show Token",
            command=lambda: token_entry.config(show=""),
            bg="#7289DA",
            fg="#FFFFFF",
            bd=0,
            highlightthickness=0
        ).pack(side="left", padx=5)
        
        tk.Button(
            token_button_frame,
            text="Hide Token",
            command=lambda: token_entry.config(show="*"),
            bg="#7289DA",
            fg="#FFFFFF",
            bd=0,
            highlightthickness=0
        ).pack(side="left", padx=5)
        
        tk.Button(
            token_button_frame,
            text="Test Token",
            command=self.test_token,
            bg="#57F287",
            fg="#FFFFFF",
            bd=0,
            highlightthickness=0
        ).pack(side="left", padx=5)
        
        # Channel settings
        channel_frame = tk.LabelFrame(
            self.settings_frame,
            text="Channel Settings (Up to 5)",
            bg="#2C2F33",
            fg="#FFFFFF",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=10,
            bd=1,
            relief="solid",
            highlightbackground="#36393F"
        )
        channel_frame.pack(fill="x", padx=5, pady=10)
        
        tk.Label(
            channel_frame,
            text="Enter Channel IDs (comma separated or one per line):",
            bg="#2C2F33",
            fg="#FFFFFF",
            anchor="w"
        ).pack(anchor="w", padx=5, pady=5)
        
        # Create 5 entry fields for channels
        self.channel_entries = []
        for i in range(5):
            frame = tk.Frame(channel_frame, bg="#2C2F33")
            frame.pack(fill="x", padx=5, pady=2)
            
            tk.Label(
                frame,
                text=f"Channel {i+1}:",
                bg="#2C2F33",
                fg="#FFFFFF",
                width=10,
                anchor="w"
            ).pack(side="left", padx=(0, 5))
            
            channel_var = tk.StringVar()
            if i < len(channel_list):
                channel_var.set(channel_list[i])
            entry = tk.Entry(
                frame,
                textvariable=channel_var,
                width=30,
                bg="#40444B",
                fg="#FFFFFF",
                insertbackground="#FFFFFF",
                highlightbackground="#36393F",
                highlightthickness=1
            )
            entry.pack(side="left", fill="x", expand=True)
            self.channel_entries.append(channel_var)
        
        # Channel buttons
        channel_button_frame = tk.Frame(channel_frame, bg="#2C2F33")
        channel_button_frame.pack(fill="x", pady=5)
        
        tk.Button(
            channel_button_frame,
            text="Test All Channels",
            command=self.test_all_channels,
            bg="#57F287",
            fg="#FFFFFF",
            bd=0,
            highlightthickness=0
        ).pack(side="left", padx=5)
        
        # Save settings
        save_frame = tk.Frame(self.settings_frame, bg="#2C2F33")
        save_frame.pack(fill="x", padx=5, pady=20)
        
        tk.Button(
            save_frame,
            text="Save Settings to .env",
            command=self.save_settings,
            bg="#57F287",
            fg="#FFFFFF",
            padx=10,
            pady=5,
            font=("Arial", 10, "bold"),
            bd=0,
            highlightthickness=0
        ).pack(pady=10)
        
        # How to get token
        help_frame = tk.LabelFrame(
            self.settings_frame,
            text="How to Get Your Token",
            bg="#2C2F33",
            fg="#FFFFFF",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=10,
            bd=1,
            relief="solid",
            highlightbackground="#36393F"
        )
        help_frame.pack(fill="x", padx=5, pady=10)
        
        instructions = (
            "1. Open Discord in Chrome/Firefox\n"
            "2. Press Ctrl+Shift+I to open Developer Tools\n"
            "3. Go to the Application tab\n"
            "4. In Storage → Local Storage → https://discord.com\n"
            "5. Find the 'token' key and copy its value\n"
            "6. Paste it in the User Token field above"
        )
        
        tk.Label(
            help_frame,
            text=instructions,
            bg="#2C2F33",
            fg="#B9BBBE",
            justify="left",
            anchor="w"
        ).pack(fill="x", padx=5, pady=5)
        
    def log_message(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")
    
    def send_discord_message(self):
        if not USER_TOKEN or not channel_list:
            self.log_message("[✗] Error: Token or Channel IDs not configured")
            self.stop_sending()
            return
            
        # Get active channels from checkboxes
        active_channels = []
        for i, var in enumerate(self.channel_vars):
            if var.get() and i < len(channel_list) and channel_list[i]:
                active_channels.append(channel_list[i])
        
        if not active_channels:
            self.log_message("[✗] Error: No channels selected")
            return
            
        success_count = 0
        for channel_id in active_channels:
            url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
            headers = {
                "Authorization": USER_TOKEN,
                "Content-Type": "application/json"
            }
            payload = {"content": self.message_var.get()}
            
            try:
                response = requests.post(url, headers=headers, json=payload)
                if response.status_code == 200:
                    success_count += 1
                    self.log_message(f"[✓] Message sent to channel {channel_id}")
                else:
                    self.log_message(f"[✗] Failed to send to channel {channel_id}. Status: {response.status_code}")
            except Exception as e:
                self.log_message(f"[✗] Error sending to channel {channel_id}: {str(e)}")
        
        if success_count > 0:
            self.message_count += 1
            self.count_var.set(str(self.message_count))
            self.log_message(f"Successfully sent to {success_count}/{len(active_channels)} channels")
            self.log_message(f"Total messages sent: {self.message_count}")
            
            # Log the exact interval used
            self.log_message(f"Next message in: {self.interval}s ({self.interval//60}m {self.interval%60}s)")
    
    def update_next_message_time(self):
        if self.running:
            minutes, seconds = divmod(self.remaining_time, 60)
            self.next_var.set(f"{int(minutes):02d}:{int(seconds):02d}")
            self.remaining_time -= 1
            
            if self.remaining_time < 0:
                self.send_discord_message()
                
                # Generate new random interval
                min_sec = self.min_interval_var.get()
                max_sec = self.max_interval_var.get()
                self.interval = random.randint(min_sec, max_sec)
                self.remaining_time = self.interval
            
            self.root.after(1000, self.update_next_message_time)
    
    def start_sending(self):
        if self.running:
            return
            
        # Validate token and channel IDs
        if not USER_TOKEN:
            self.log_message("[✗] Error: Discord token not configured")
            self.notebook.select(1)  # Switch to settings tab
            return
            
        if not channel_list:
            self.log_message("[✗] Error: Channel IDs not configured")
            self.notebook.select(1)  # Switch to settings tab
            return
            
        self.running = True
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.status_var.set("Sending messages...")
        
        # Get interval values
        min_sec = self.min_interval_var.get()
        max_sec = self.max_interval_var.get()
        
        # Validate interval
        if min_sec >= max_sec:
            self.log_message("[✗] Error: Min interval must be less than max interval")
            self.stop_sending()
            return
        
        # Validate minimum interval
        if min_sec < 10:
            self.log_message("[⚠] Warning: Very short intervals increase detection risk")
        
        # Generate random interval
        self.interval = random.randint(min_sec, max_sec)
        self.remaining_time = self.interval
        
        # Log settings
        self.log_message("Message sending started")
        self.log_message(f"Interval range: {min_sec}-{max_sec} seconds")
        self.log_message(f"First interval: {self.interval} seconds")
        
        # Log active channels
        active_channels = []
        for i, var in enumerate(self.channel_vars):
            if var.get() and i < len(channel_list) and channel_list[i]:
                active_channels.append(channel_list[i])
        
        if active_channels:
            self.log_message(f"Target channels: {', '.join(active_channels)}")
        else:
            self.log_message("[✗] Error: No channels selected")
            self.stop_sending()
            return
        
        # Start the timer
        self.update_next_message_time()
    
    def stop_sending(self):
        self.running = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.status_var.set("Sending stopped")
        self.next_var.set("--:--")
        self.log_message("Message sending stopped")
    
    def save_settings(self):
        new_token = self.token_var.get().strip()
        
        # Validate token format (basic check)
        if not re.match(r'^[a-zA-Z0-9_-]{24,}\.[a-zA-Z0-9_-]{6}\.[a-zA-Z0-9_-]{27,}$', new_token):
            self.log_message("[⚠] Warning: Token format looks suspicious")
            if not messagebox.askyesno("Confirm Save", "The token format doesn't look valid. Save anyway?"):
                return
        
        # Collect channel IDs from entries
        new_channel_ids = []
        for entry in self.channel_entries:
            channel_id = entry.get().strip()
            if channel_id:
                if not channel_id.isdigit():
                    self.log_message(f"[✗] Error: Invalid Channel ID format: {channel_id}")
                    return
                new_channel_ids.append(channel_id)
        
        if not new_channel_ids:
            self.log_message("[✗] Error: At least one channel ID is required")
            return
            
        # Update .env file
        set_key('.env', 'DISCORD_USER_TOKEN', new_token)
        set_key('.env', 'DISCORD_CHANNEL_IDS', ','.join(new_channel_ids))
        
        # Reload environment variables
        load_dotenv(override=True)
        global USER_TOKEN, CHANNEL_IDS, channel_list
        USER_TOKEN = os.getenv("DISCORD_USER_TOKEN", "")
        CHANNEL_IDS = os.getenv("DISCORD_CHANNEL_IDS", "")
        channel_list = [cid.strip() for cid in CHANNEL_IDS.split(',')] if CHANNEL_IDS else []
        
        self.log_message("[✓] Settings saved to .env file")
        self.log_message(f"Token: {new_token[:10]}...")
        self.log_message(f"Channel IDs: {', '.join(new_channel_ids)}")
        
        # Update channel checkboxes
        for i, var in enumerate(self.channel_vars):
            if i < len(channel_list):
                var.set(True)
                self.channel_checks[i].config(state="normal")
            else:
                var.set(False)
                self.channel_checks[i].config(state="disabled")
    
    def test_token(self):
        token = self.token_var.get().strip()
        if not token:
            self.log_message("[✗] Error: Token is empty")
            return
            
        url = "https://discord.com/api/v9/users/@me"
        headers = {"Authorization": token}
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                user_data = response.json()
                username = f"{user_data['username']}#{user_data['discriminator']}"
                self.log_message(f"[✓] Token valid! Logged in as: {username}")
            else:
                self.log_message(f"[✗] Token test failed. Status: {response.status_code}")
                self.log_message(f"Response: {response.text}")
        except Exception as e:
            self.log_message(f"[✗] Error testing token: {str(e)}")
    
    def test_channel(self, channel_id):
        token = self.token_var.get().strip()
        
        if not token:
            self.log_message("[✗] Error: Token is empty")
            return False
            
        if not channel_id or not channel_id.isdigit():
            self.log_message(f"[✗] Error: Invalid Channel ID: {channel_id}")
            return False
            
        url = f"https://discord.com/api/v9/channels/{channel_id}"
        headers = {"Authorization": token}
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                channel_data = response.json()
                channel_name = channel_data.get('name', 'Direct Message')
                channel_type = "Server" if channel_data.get('guild_id') else "DM"
                self.log_message(f"[✓] Channel {channel_id} valid! Name: {channel_name} ({channel_type})")
                return True
            else:
                self.log_message(f"[✗] Channel {channel_id} test failed. Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_message(f"[✗] Error testing channel {channel_id}: {str(e)}")
            return False
    
    def test_all_channels(self):
        channels_to_test = []
        for entry in self.channel_entries:
            channel_id = entry.get().strip()
            if channel_id:
                channels_to_test.append(channel_id)
        
        if not channels_to_test:
            self.log_message("[✗] Error: No channels to test")
            return
            
        self.log_message(f"Testing {len(channels_to_test)} channels...")
        success_count = 0
        
        for channel_id in channels_to_test:
            if self.test_channel(channel_id):
                success_count += 1
                
        self.log_message(f"Channel test complete: {success_count}/{len(channels_to_test)} successful")

if __name__ == "__main__":
    root = tk.Tk()
    app = DiscordMessageSender(root)
    
    # Add console warning
    print("=" * 70)
    print("WARNING: This script violates Discord's Terms of Service.")
    print("Using it may result in permanent account suspension.")
    print("Use only for educational purposes on accounts you don't mind losing.")
    print("=" * 70)
    
    # Initial token check
    if not USER_TOKEN:
        app.log_message("[⚠] Warning: Discord token not configured")
        app.notebook.select(1)  # Switch to settings tab
    
    # Initial channel check
    if not channel_list:
        app.log_message("[⚠] Warning: No channel IDs configured")
        app.notebook.select(1)  # Switch to settings tab
    
    root.mainloop()