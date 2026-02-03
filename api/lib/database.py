import json
import os
import time

class DatabaseManager:
    def __init__(self):
        # Em ambiente Serverless (Vercel), não temos persistência de arquivos.
        # Os dados resetam a cada nova execução/deploy.
        # Para produção real, seria necessário conectar a um banco (Supabase, MongoDB, etc).
        # Aqui usaremos uma versão "MOCK" que funciona em memória para demonstração.
        self.users = {}
        self.stats = {"platforms": {}}
        
        # Tenta carregar dados iniciais se existirem no repo (read-only)
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.mock_init()

    def mock_init(self):
        # Se houver arquivos JSON no deploy, carrega como estado inicial
        pass

    def get_user_prefs(self, user_id):
        return self.users.get(str(user_id), {}).get("prefs", {
            "title": True, "link": True, "desc": False, "video": True
        })

    def save_user_pref_value(self, user_id, key, value):
        user_id = str(user_id)
        if user_id not in self.users:
            self.users[user_id] = {"prefs": {}}
        self.users[user_id]["prefs"][key] = value

    def update_user_stats(self, user_id, type_action):
        pass # Stateless

    def save_telegram_user(self, user):
        pass # Stateless

    def increment_global_stat(self, platform):
        key = platform.lower()
        self.stats["platforms"][key] = self.stats["platforms"].get(key, 0) + 1

    def get_global_stats(self):
        return self.stats
