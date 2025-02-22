import json
from datetime import datetime

class ChatHistory:
    def __init__(self):
        try:
            with open('chat_history.json', 'r') as f:
                self.history = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Initialize with empty dictionary if file doesn't exist or is empty
            self.history = {}
            with open('chat_history.json', 'w') as f:
                json.dump(self.history, f)
    
    def save_history(self):
        with open('chat_history.json', 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def add_message(self, phone_number, message, role):
        if phone_number not in self.history:
            self.history[phone_number] = []
        
        self.history[phone_number].append({
            'role': role,
            'content': message,
            'timestamp': datetime.now().isoformat()
        })
        self.save_history()
    
    def get_history(self, phone_number, limit=10):
        return self.history.get(phone_number, [])[-limit:] 