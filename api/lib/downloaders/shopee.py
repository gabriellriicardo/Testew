import re
import json
import requests
from urllib.parse import unquote
from bs4 import BeautifulSoup
from ..logger import Logger

logger = Logger()

class ShopeeDownloader:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://shopee.com.br/',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7'
        }
        self.session = requests.Session()
        
        # --- CONFIGURAÇÃO DE RETENTATIVAS (PORTADO DO DESKTOP) ---
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        retry_strategy = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def get_video_url(self, share_url):
        logger.log(f"Shopee: Processando {share_url}", "INFO")
        try:
            # Follow redirects manually to get final URL
            response = self.session.get(share_url, headers=self.headers, allow_redirects=True, timeout=10)
            final_url = response.url
            
            if "universal-link" in final_url:
                match = re.search(r'redir=([^&]+)', final_url)
                if match:
                    final_url = unquote(match.group(1))
                    response = self.session.get(final_url, headers=self.headers, timeout=10)

            # Parse HTML for NEXT_DATA
            soup = BeautifulSoup(response.text, 'html.parser')
            script_tag = soup.find('script', {'id': '__NEXT_DATA__', 'type': 'application/json'})

            if not script_tag:
                logger.log("Shopee: __NEXT_DATA__ não encontrado no HTML", "ERROR")
                # Loga pedaço do HTML para debug (cuidado com tamanho)
                logger.log(f"Shopee HTML Snippet: {response.text[:200]}...", "WARN")
                return None, "Dados não encontrados"

            json_data = json.loads(script_tag.string)
            
            # Logic extracted from original shopee.py (Desktop Version)
            props = json_data.get('props', {}).get('pageProps', {})
            video_url = None
            caption = "Shopee Video"

            # 1. Tenta mediaInfo (Versão desktop prioriza isso)
            if 'mediaInfo' in props:
                media_info = props['mediaInfo']
                video_url = media_info.get('video', {}).get('watermarkVideoUrl')
                # Tenta achar caption no mediaInfo
                caption = media_info.get('title') or media_info.get('content') or media_info.get('desc') or caption
            
            # 2. Se não achou, tenta initialState > Product (Fallback)
            if not video_url:
                initial_state = props.get('initialState', {})
                product = initial_state.get('product', {}) if initial_state else props.get('product', {})
                if product and 'video_info_list' in product:
                    video_list = product.get('video_info_list', [])
                    caption = product.get('name') or product.get('description') or caption
                    if video_list and len(video_list) > 0:
                        video_url = video_list[0].get('video_url')

            if video_url:
                # Returns the direct URL (playable in browser)
                return video_url, caption
                
            return None, "Vídeo não encontrado no JSON"

        except Exception as e:
            logger.log(f"Shopee Exception: {str(e)}", "ERROR")
            return None, str(e)
