import yt_dlp
import requests
from bs4 import BeautifulSoup
from ..logger import Logger

logger = Logger()

class MyYtdlLogger:
    def debug(self, msg):
        if not msg.startswith('[debug] '):
            logger.log(f"[yt-dlp] {msg}", "INFO")
    def info(self, msg):
        logger.log(f"[yt-dlp] {msg}", "INFO")
    def warning(self, msg):
        logger.log(f"[yt-dlp] {msg}", "WARN")
    def error(self, msg):
        logger.log(f"[yt-dlp ERROR] {msg}", "ERROR")

class SocialDownloader:
    def __init__(self):
        pass

    # --- MÉTODOS NATIVOS E OTIMIZAÇÕES (PORTADO DO DESKTOP) ---
    
    def get_tiktok_api(self, url):
        """Tenta pegar via API TikWM (Mais rápido e sem marca d'água)"""
        try:
            logger.log("🎵 Tentando método rápido (TikWM)...", "INFO")
            api_url = "https://www.tikwm.com/api/"
            params = {'url': url, 'count': 12, 'cursor': 0, 'web': 1, 'hd': 1}
            
            # Timeout curto para não travar se a API estiver lenta
            res = requests.post(api_url, data=params, timeout=4) 
            data = res.json()
            
            if data.get('code') == 0:
                video_url = data.get('data', {}).get('hdplay') or data.get('data', {}).get('play')
                title = data.get('data', {}).get('title', 'TikTok Video')
                
                if video_url:
                    if not video_url.startswith('http'): video_url = "https://www.tikwm.com" + video_url
                    logger.log("✅ TikWM sucesso!", "SUCCESS")
                    return video_url, title
        except Exception as e:
             logger.log(f"⚠️ TikWM falhou: {e}", "WARN")
        return None, None

    def get_threads_native(self, url):
        """Scraping nativo para Threads (Funciona no Vercel/Serverless)"""
        try:
            logger.log("🧵 Tentando scrape nativo Threads...", "INFO")
            headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            }
            res = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            
            video_meta = soup.find('meta', property='og:video')
            if video_meta and video_meta.get('content'):
                title_meta = soup.find('meta', property='og:description')
                title = title_meta['content'] if title_meta else "Threads Video"
                logger.log("✅ Threads Nativo sucesso!", "SUCCESS")
                return video_meta['content'], title
        except Exception as e:
            logger.log(f"⚠️ Threads Nativo falhou: {e}", "WARN")
        return None, None

    def get_video_info(self, url, cookies_path=None):
        logger.log(f"Processando URL: {url}", "INFO")

        # 1. Tenta Otimizações Específicas
        if "tiktok.com" in url:
            v_url, v_title = self.get_tiktok_api(url)
            if v_url: return v_url, v_title
            
        if "threads.net" in url:
            v_url, v_title = self.get_threads_native(url)
            if v_url: return v_url, v_title

        # 2. Fallback Robusto (yt-dlp com Estratégias de Cliente)
        # O desktop tenta vários 'clients' (Android, iOS, TV, Web). Vamos replicar.
        
        strategies = [
            ("Default", {}),
            ("Client Android", {'extractor_args': {'youtube': {'player_client': ['android']}}}),
            ("Client iOS", {'extractor_args': {'youtube': {'player_client': ['ios']}}}),
            ("Client TV", {'extractor_args': {'youtube': {'player_client': ['tv']}}}),
        ]

        last_error = ""

        for name, extra_opts in strategies:
            logger.log(f"🔄 Tentando yt-dlp estratégia: {name}", "INFO")
            
            ydl_opts = {
                'quiet': False,
                'logger': MyYtdlLogger(),
                'no_warnings': False,
                'format': 'best[ext=mp4]/best',
                'noplaylist': True,
                'socket_timeout': 15,
                **extra_opts # Mescla opções da estratégia
            }
            
            if cookies_path: ydl_opts['cookiefile'] = cookies_path

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    video_url = info.get('url')
                    title = info.get('title', 'Social Video')
                    
                    if not video_url and 'formats' in info:
                        video_url = info['formats'][-1].get('url')

                    if video_url:
                        logger.log(f"✅ Sucesso com {name}!", "SUCCESS")
                        return video_url, title
            except Exception as e:
                last_error = str(e)
                # logger.log(f"⚠️ Falha em {name}", "WARN") # Opcional: não poluir muito
                continue

        # 3. Fallback com Playwright (para casos mais complexos ou anti-bot)
        logger.log("🔄 Todas as estratégias yt-dlp falharam. Tentando Playwright...", "INFO")
        try:
            from playwright.sync_api import sync_playwright # Importação tardia/segura
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True) # Lança navegador headless
                page = browser.new_page()
                page.goto(url, wait_until='networkidle') # Espera a rede ficar ociosa
                
                # Tenta encontrar o vídeo diretamente no HTML ou via yt-dlp com a página carregada
                # Isso é um exemplo, a lógica exata pode variar muito dependendo do site
                
                # Exemplo: Tentar extrair com yt-dlp usando o HTML da página
                # Ou procurar por tags <video> ou meta tags de vídeo
                
                # Para simplificar, vamos tentar re-executar yt-dlp com o contexto da página se necessário
                # Ou, mais diretamente, tentar encontrar um URL de vídeo
                
                # Esta parte é altamente dependente do site.
                # Por exemplo, para Instagram/Facebook, pode-se procurar por og:video
                video_meta = page.query_selector('meta[property="og:video"]')
                if video_meta:
                    video_url = video_meta.get_attribute('content')
                    title_meta = page.query_selector('meta[property="og:title"]')
                    title = title_meta.get_attribute('content') if title_meta else "Video Playwright"
                    if video_url:
                        logger.log("✅ Playwright sucesso (via meta tag)!", "SUCCESS")
                        browser.close()
                        return video_url, title

                # Outra abordagem: tentar extrair com yt-dlp usando a URL final após redirecionamentos
                # ou o HTML da página se yt-dlp tiver um extrator para isso (raro)
                
                # Se nada for encontrado, podemos tentar uma última vez com yt-dlp na URL final
                # (embora isso já tenha sido feito nas estratégias acima)
                
                browser.close()
                last_error = "Playwright não conseguiu encontrar o vídeo diretamente."

        except ImportError:
            last_error = "Playwright não está instalado. Instale com 'pip install playwright' e 'playwright install'."
            logger.log(f"⚠️ Playwright falhou: {last_error}", "WARN")
        except Exception as e:
            last_error = f"Playwright falhou: {e}"
            logger.log(f"⚠️ Playwright falhou: {e}", "WARN")

        logger.log("❌ Todas as estratégias falharam.", "ERROR")
        return None, last_error
