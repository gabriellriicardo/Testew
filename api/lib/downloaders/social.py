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

    def get_video_info(self, url, cookies_path=None):
        """
        Retorna (video_url, title) usando yt-dlp.
        Em Serverless, não podemos baixar arquivos grandes.
        Vamos tentar obter a URL direta (format URL) para que o frontend baixe ou exiba.
        """
        ydl_opts = {
            'quiet': False, # Precisamos ver os logs
            'logger': MyYtdlLogger(),
            'no_warnings': False,
            'format': 'best', # Tenta pegar a melhor disponível
            'noplaylist': True,
            'extract_flat': True, # Tenta não baixar, apenas extrair
            'socket_timeout': 10,
        }
        
        # Se tiver cookies, adiciona (seria passado via arquivo temp no serverless)
        if cookies_path:
            ydl_opts['cookiefile'] = cookies_path

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # yt-dlp retorna dict. 'url' geralmente é o link direto do arquivo de vídeo.
                video_url = info.get('url')
                title = info.get('title', 'Social Video')
                
                if not video_url:
                    # As vezes 'url' não está no root, precisa checar formats
                    if 'formats' in info:
                        # Pega o último (melhor qualidade +- geralmente)
                        video_url = info['formats'][-1].get('url')

                return video_url, title
        except Exception as e:
            print(f"Erro yt-dlp: {e}")
            return None, str(e)
