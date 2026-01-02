import os
import requests
import json
import time
import threading
from datetime import datetime
from dotenv import load_dotenv
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Load environment variables
load_dotenv()

REDIS_URL = os.getenv("UPSTASH_REDIS_REST_URL")
REDIS_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN")

if not REDIS_URL or not REDIS_TOKEN:
    print(Fore.RED + "Error: Missing UPSTASH credentials in .env file")
    exit(1)

CHAT_KEY = "chat:messages"
LAST_SEEN_KEY = "chat:last_seen"

class RedisChat:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {REDIS_TOKEN}",
            "Content-Type": "application/json"
        }
        self.username = None
        self.running = True
        self.message_counter = 0
        
    def redis_request(self, command, args=None):
        """Make HTTP request to Upstash Redis REST API"""
        try:
            # Format: ["COMMAND", "arg1", "arg2", ...]
            cmd_list = [command]
            if args:
                cmd_list.extend(args)
            
            response = requests.post(
                f"{REDIS_URL}",
                json=cmd_list,
                headers=self.headers,
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(Fore.RED + f"Redis error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(Fore.RED + f"Connection error: {e}")
            return None
    
    def send_message(self, message):
        """Send a message to the chat"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg_data = {
            "username": self.username,
            "message": message,
            "timestamp": timestamp
        }
        
        msg_json = json.dumps(msg_data)
        result = self.redis_request("LPUSH", [CHAT_KEY, msg_json])
        
        if result:
            print(Fore.GREEN + f"✓ Message sent")
        else:
            print(Fore.RED + "✗ Failed to send message")
    
    def get_message_history(self, count=10):
        """Get chat history from Redis"""
        result = self.redis_request("LRANGE", [CHAT_KEY, 0, count - 1])
        
        if result and result.get("result"):
            messages = []
            for msg_str in result["result"]:
                try:
                    msg = json.loads(msg_str)
                    messages.append(msg)
                except:
                    pass
            return messages
        return []
    
    def display_message(self, msg):
        """Display a single message with formatting"""
        username = msg.get("username", "Unknown")
        message = msg.get("message", "")
        timestamp = msg.get("timestamp", "")
        
        print(f"{Fore.CYAN}[{timestamp}] {Fore.YELLOW}{username}{Style.RESET_ALL}: {message}")
    
    def show_history(self):
        """Display chat history"""
        print(Fore.MAGENTA + "\n" + "="*60)
        print(Fore.MAGENTA + "Chat History (Latest 20 messages)")
        print(Fore.MAGENTA + "="*60)
        
        messages = self.get_message_history(20)
        
        if not messages:
            print(Fore.YELLOW + "No messages yet. Be the first to chat!")
        else:
            # Reverse to show oldest first
            for msg in reversed(messages):
                self.display_message(msg)
        
        print(Fore.MAGENTA + "="*60 + "\n")
    
    def stream_updates(self):
        """Background thread to check for new messages"""
        last_count = 0
        
        while self.running:
            try:
                result = self.redis_request("LLEN", [CHAT_KEY])
                
                if result and result.get("result") is not None:
                    current_count = result["result"]
                    
                    # If new messages arrived, show them
                    if current_count > last_count:
                        new_messages_count = current_count - last_count
                        messages = self.get_message_history(new_messages_count)
                        
                        if messages:
                            print(Fore.CYAN + f"\n--- New message(s) received ---")
                            for msg in messages:
                                self.display_message(msg)
                            print(Fore.GREEN + ">>> ", end="", flush=True)
                        
                        last_count = current_count
                
                time.sleep(1)  # Check for new messages every second
            except Exception as e:
                print(Fore.RED + f"Stream error: {e}")
                time.sleep(2)
    
    def start_stream_thread(self):
        """Start background streaming thread"""
        stream_thread = threading.Thread(target=self.stream_updates, daemon=True)
        stream_thread.start()
    
    def get_username(self):
        """Get username from user"""
        while True:
            username = input(Fore.CYAN + "Enter your username: ").strip()
            if username and len(username) <= 20:
                self.username = username
                print(Fore.GREEN + f"Welcome, {Fore.YELLOW}{username}{Fore.GREEN}!")
                break
            else:
                print(Fore.RED + "Username must be 1-20 characters")
    
    def show_help(self):
        """Display help menu"""
        print(Fore.MAGENTA + "\n" + "="*60)
        print(Fore.MAGENTA + "Commands:")
        print(Fore.MAGENTA + "="*60)
        print(f"{Fore.YELLOW}/history{Style.RESET_ALL}  - Show chat history")
        print(f"{Fore.YELLOW}/help{Style.RESET_ALL}     - Show this help menu")
        print(f"{Fore.YELLOW}/quit{Style.RESET_ALL}     - Exit the chat")
        print(f"{Fore.YELLOW}Any text{Style.RESET_ALL}   - Send a message")
        print(Fore.MAGENTA + "="*60 + "\n")
    
    def run(self):
        """Main chat loop"""
        print(Fore.CYAN + "="*60)
        print(Fore.CYAN + "Welcome to Redis Chat CLI!")
        print(Fore.CYAN + "="*60 + "\n")
        
        self.get_username()
        self.start_stream_thread()
        self.show_history()
        self.show_help()
        
        print(Fore.GREEN + "Connected! Type your message or /help for commands\n")
        
        try:
            while self.running:
                try:
                    message = input(Fore.GREEN + ">>> ").strip()
                    
                    if not message:
                        continue
                    
                    if message.lower() == "/quit":
                        self.running = False
                        print(Fore.YELLOW + "Goodbye!")
                        break
                    elif message.lower() == "/help":
                        self.show_help()
                    elif message.lower() == "/history":
                        self.show_history()
                    else:
                        self.send_message(message)
                
                except KeyboardInterrupt:
                    self.running = False
                    print(Fore.YELLOW + "\nGoodbye!")
                    break
        
        except Exception as e:
            print(Fore.RED + f"Error: {e}")
        
        self.running = False

if __name__ == "__main__":
    chat = RedisChat()
    chat.run()
