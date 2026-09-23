import os
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'skin_trader_local_secret_key_change_in_production')
    
    # URL do Frontend (Live Server padrão: http://127.0.0.1:5500)
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://127.0.0.1:5500').rstrip('/')
    
    # GitHub OAuth
    GITHUB_CLIENT_ID = os.getenv('GITHUB_CLIENT_ID', '').strip()
    GITHUB_CLIENT_SECRET = os.getenv('GITHUB_CLIENT_SECRET', '').strip()
    GITHUB_REDIRECT_URI = os.getenv('GITHUB_REDIRECT_URI', 'http://127.0.0.1:5000/auth/github/callback').strip()
    
    # MongoDB
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://127.0.0.1:27017/skin_trader_db').strip()
    
    # Economia
    INITIAL_BALANCE = float(os.getenv('INITIAL_BALANCE', 150.00))
    
    # Servidor Backend
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 't')
