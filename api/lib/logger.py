from datetime import datetime

class Logger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance.logs = []
            cls._instance.max_logs = 50
        return cls._instance

    def log(self, message, type="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = {
            "time": timestamp,
            "type": type,
            "msg": message
        }
        self.logs.insert(0, entry) # Prepend
        if len(self.logs) > self.max_logs:
            self.logs.pop() # Keep list small
        print(f"[{type}] {message}") # Also print to Vercel console

    def get_logs(self):
        return self.logs
