import telebot
from telebot import types
import os
import threading
from .utils import resolve_link_type
from .database import DatabaseManager
from .downloaders.shopee import ShopeeDownloader
from .downloaders.social import SocialDownloader

# Instancia Singletons (Recriados a cada request no serverless, idealmente cacheado fora do handler)
db = DatabaseManager()
shopee_dl = ShopeeDownloader()
social_dl = SocialDownloader()

class BotHandler:
    def __init__(self, token):
        self.bot = telebot.TeleBot(token, threaded=False)
        self.setup_handlers()

    def process_update(self, json_string):
        if not json_string: return
        update = telebot.types.Update.de_json(json_string)
        self.bot.process_new_updates([update])

    def setup_handlers(self):
        # --- MENUS ---
        def get_main_menu():
            markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
            btn1 = types.KeyboardButton("📚 Como Usar")
            btn2 = types.KeyboardButton("🆘 Suporte")
            btn3 = types.KeyboardButton("📢 Grupo")
            btn4 = types.KeyboardButton("💸 Fazer um Mimo")
            btn5 = types.KeyboardButton("⚙️ Status")
            btn6 = types.KeyboardButton("⚙️ Configurações")
            markup.add(btn1, btn2)
            markup.add(btn3, btn4)
            markup.add(btn5, btn6)
            return markup

        def get_config_menu(user_id):
            prefs = db.get_user_prefs(user_id)
            markup = types.InlineKeyboardMarkup(row_width=2)
            options = [("title", "📦 Título"), ("link", "🔗 Link"), ("desc", "📝 Descrição"), ("video", "🎥 Vídeo")]
            buttons = []
            for key, label in options:
                status = "✅" if prefs.get(key, True) else "❌"
                buttons.append(types.InlineKeyboardButton(f"{status} {label}", callback_data=f"cfg_{key}"))
            markup.add(*buttons)
            markup.add(types.InlineKeyboardButton("🔽 Fechar", callback_data="cfg_close"))
            return markup

        # --- COMMANDS ---
        @self.bot.message_handler(commands=['start', 'help', 'ajuda'])
        def send_welcome(message):
            db.save_telegram_user(message.from_user)
            msg = (
                f"👋 **Olá, {message.from_user.first_name}!**\n\n"
                f"Sou o **AlfaVision Web**! 🌐\n"
                f"Baixo vídeos do TikTok, Instagram, Shopee, YouTube, Kwai e Facebook.\n\n"
                f"👇 **Use o menu abaixo:**"
            )
            self.bot.send_message(message.chat.id, msg, parse_mode="Markdown", reply_markup=get_main_menu())

        # --- TEXT MENU ---
        @self.bot.message_handler(func=lambda m: m.text in ["📚 Como Usar", "🆘 Suporte", "📢 Grupo", "💸 Fazer um Mimo", "⚙️ Status", "⚙️ Configurações"])
        def menu_handler(message):
            txt = message.text
            cid = message.chat.id
            
            if txt == "📚 Como Usar":
                self.bot.reply_to(message, "Envie o link do vídeo e eu te devolvo o arquivo ou o link de download!", parse_mode="Markdown")
            elif txt == "🆘 Suporte":
                self.bot.reply_to(message, "Contato: @gabriellriicardo")
            elif txt == "📢 Grupo":
                mk = types.InlineKeyboardMarkup()
                mk.add(types.InlineKeyboardButton("Entrar", url="https://t.me/alfatyvideosshopee"))
                self.bot.send_message(cid, "Entre no nosso grupo!", reply_markup=mk)
            elif txt == "⚙️ Status":
                self.bot.reply_to(message, "🟢 **Online (Vercel Edition)**\n⚡ Velocidade Máxima")
            elif txt == "⚙️ Configurações":
                self.bot.send_message(cid, "🔧 Configurações:", reply_markup=get_config_menu(cid))
            elif txt == "💸 Fazer um Mimo":
                 self.bot.reply_to(message, "O sistema de doação Pix está sendo migrado. Em breve!")

        # --- CALLBACKS ---
        @self.bot.callback_query_handler(func=lambda call: call.data.startswith("cfg_"))
        def callback_config(call):
            cid = call.message.chat.id
            if call.data == "cfg_close":
                self.bot.delete_message(cid, call.message.message_id)
                return
            
            key = call.data.split("cfg_")[1]
            prefs = db.get_user_prefs(cid)
            new_val = not prefs.get(key, True)
            db.save_user_pref_value(cid, key, new_val)
            
            self.bot.edit_message_reply_markup(cid, call.message.message_id, reply_markup=get_config_menu(cid))

        # --- DOWNLOAD LOGIC ---
        @self.bot.message_handler(func=lambda m: True)
        def handle_message(message):
            url = message.text.strip()
            link_type = resolve_link_type(url)
            
            if link_type == 'UNKNOWN':
                self.bot.reply_to(message, "🤔 Link não reconhecido.")
                return

            cid = message.chat.id
            status_msg = self.bot.send_message(cid, f"🔎 Processando {link_type}...")
            
            video_url = None
            title = ""
            
            try:
                if link_type == 'VIDEO': # Shopee
                    video_url, title = shopee_dl.get_video_url(url)
                    if not video_url: raise Exception(title)
                else:
                    video_url, title = social_dl.get_video_info(url)
                    if not video_url: raise Exception("Falha ao extrair")
                
                # UPDATE: No Vercel não podemos baixar arquivos grandes e enviar via send_video(open(file)).
                # Temos que enviar a URL direta ou usar send_video(url).
                # O Telegram aceita URL direta se for < 20MB, mas social_dl retorna URL instavel as vezes.
                
                caption = f"🎥 **{title}**\n\n🔗 [Link Original]({url})\n🤖 Via AlfaVision Web"
                
                try:
                    self.bot.send_video(cid, video_url, caption=caption, parse_mode="Markdown")
                except Exception as e:
                    # Fallback se a URL falhar (ex: expirada ou bloqueada pelo Telegram)
                    self.bot.send_message(cid, f"🎥 **Não consegui enviar o vídeo direto.**\n\n👇 **Clique para baixar:**\n{video_url}", parse_mode="Markdown")

                self.bot.delete_message(cid, status_msg.message_id)
                db.increment_global_stat(link_type)

            except Exception as e:
                self.bot.edit_message_text(f"❌ Erro: {str(e)}", cid, status_msg.message_id)
