import re

def resolve_link_type(url):
    """
    Identifica o tipo de link (Shopee, TikTok, etc)
    """
    url = url.lower()
    
    if 'shopee' in url or 'shp.ee' in url:
        return 'VIDEO' # Assumindo Shopee Video por padrão para simplificar
    elif 'tiktok' in url:
        return 'TIKTOK'
    elif 'kwai' in url:
        return 'KWAI'
    elif 'facebook' in url or 'fb.watch' in url:
        return 'FACEBOOK'
    elif 'instagram' in url:
        return 'INSTAGRAM'
    elif 'youtube' in url or 'youtu.be' in url:
        return 'YOUTUBE'
    elif 'threads' in url:
        return 'THREADS'
        
    return 'UNKNOWN'
