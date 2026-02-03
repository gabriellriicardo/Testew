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
        }
        self.session = requests.Session()

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
            
            # Logic extracted from original shopee.py
            props = json_data.get('props', {}).get('pageProps', {})
            video_url = None
            caption = "Shopee Video"

            if 'mediaInfo' in props:
                media_info = props['mediaInfo']
                video_url = media_info.get('video', {}).get('watermarkVideoUrl')
                caption = media_info.get('title') or caption
            
            if not video_url:
                initial_state = props.get('initialState', {})
                product = initial_state.get('product', {}) if initial_state else props.get('product', {})
                if product and 'video_info_list' in product:
                    video_list = product.get('video_info_list', [])
                    if video_list:
                        video_url = video_list[0].get('video_url')
                        caption = product.get('name') or caption

            if video_url:
                # Returns the direct URL (playable in browser)
                return video_url, caption
                
            return None, "Vídeo não encontrado no JSON"

        except Exception as e:
            logger.log(f"Shopee Exception: {str(e)}", "ERROR")
            return None, str(e)
