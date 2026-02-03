from flask import Flask, request, jsonify
import sys
import os

# Path Fix
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lib.utils import resolve_link_type
from lib.downloaders.shopee import ShopeeDownloader
from lib.downloaders.social import SocialDownloader
from lib.database import DatabaseManager
from lib.bot_handler import BotHandler

app = Flask(__name__)

# Singletons
db = DatabaseManager()
shopee_dl = ShopeeDownloader()
social_dl = SocialDownloader()

# Bot Token deve ser setado via ENV VAR na Vercel ou via Config no Frontend (Mock)
# Para fins de teste/demo, o usuário configurará no Frontend.
# O webhook receberá o token na query string ou header seria o ideal, 
# mas vamos simplificar assumindo um token fixo ou passado na URL do webhook.

@app.route("/api/download", methods=['POST'])
def download_route():
    try:
        data = request.json
        url = data.get('url')
        if not url: return jsonify({"error": "URL missing"}), 400
        
        link_type = resolve_link_type(url)
        if link_type == 'UNKNOWN': return jsonify({"error": "Invalid Link"}), 400

        video_url, title = None, "Video"
        if link_type == 'VIDEO':
            video_url, title = shopee_dl.get_video_url(url)
        else:
            video_url, title = social_dl.get_video_info(url)

        if not video_url: return jsonify({"error": "Download failed"}), 500

        db.increment_global_stat(link_type)
        return jsonify({"status": "success", "title": title, "download_url": video_url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/bot/webhook", methods=['POST'])
def webhook():
    # A URL do webhook no Telegram deve ser: https://site.vercel.app/api/bot/webhook?token=SEU_TOKEN
    token = request.args.get('token') 
    if not token:
        # Fallback para teste local ou hardcoded se o user preferir
        return jsonify({"error": "Token required in query param"}), 403

    try:
        handler = BotHandler(token)
        handler.process_update(request.data.decode('utf-8'))
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        print(f"Webhook Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5328)
