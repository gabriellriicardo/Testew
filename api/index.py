from flask import Flask, request, jsonify
import sys
import os

# Adiciona o diretório atual ao path para importações
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lib.utils import resolve_link_type
from lib.downloaders.shopee import ShopeeDownloader
from lib.downloaders.social import SocialDownloader
from lib.database import DatabaseManager

app = Flask(__name__)

# Instancia Singletons
db = DatabaseManager()
shopee_dl = ShopeeDownloader()
social_dl = SocialDownloader()

@app.route("/api/download", methods=['POST'])
def download_route():
    try:
        data = request.json
        url = data.get('url')
        if not url:
            return jsonify({"error": "URL não fornecida"}), 400
            
        link_type = resolve_link_type(url)
        
        video_url = None
        title = "Video Baixado"
        error = None

        if link_type == 'VIDEO': # Shopee
            video_url, title = shopee_dl.get_video_url(url)
            if not video_url: error = title # Logic returns error msg in 2nd arg if fail
        
        elif link_type in ['TIKTOK', 'KWAI', 'FGACEBOOK', 'INSTAGRAM', 'YOUTUBE', 'THREADS']:
            # Pega cookies se passados (future)
            video_url, title = social_dl.get_video_info(url)
            if not video_url: error = "Falha ao extrair link."
            
        else:
             return jsonify({"error": "Link não suportado."}), 400

        if error or not video_url:
             return jsonify({"error": error or "Erro desconhecido"}), 500

        # Incrementa stats
        db.increment_global_stat(link_type)

        return jsonify({
            "status": "success",
            "title": title,
            "download_url": video_url,
            "platform": link_type
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/stats", methods=['GET'])
def stats_route():
    return jsonify(db.get_global_stats())

@app.route("/api/bot/webhook", methods=['POST'])
def bot_webhook():
    # Placeholder para Webhook Real
    return jsonify({"status": "received"}), 200

if __name__ == "__main__":
    app.run(port=5328)
