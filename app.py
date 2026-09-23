import os

from flask import Flask, send_from_directory, request
from flask_cors import CORS

from config import Config
from controllers.auth_controller import auth_bp
from controllers.api_controller import api_bp
from models.user_model import Database


def create_app():
    # Inicializa o Flask usando a pasta atual como diretório dos arquivos
    # estáticos (HTML, CSS, JS, imagens etc.)
    app = Flask(
        __name__,
        static_folder=".",
        static_url_path=""
    )

    # Carrega configurações
    app.config.from_object(Config)

    # Chave secreta
    app.secret_key = Config.SECRET_KEY

    # ---------------------------------------------------------
    # CONFIGURAÇÃO DE SESSÃO
    # ---------------------------------------------------------

    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    # Em produção (Vercel) usamos HTTPS.
    # Localmente usamos HTTP.
    app.config["SESSION_COOKIE_SECURE"] = os.getenv(
        "VERCEL"
    ) == "1"

    # ---------------------------------------------------------
    # CORS
    # ---------------------------------------------------------

    allowed_origins = [
        Config.FRONTEND_URL,

        # Desenvolvimento com Live Server
        "http://127.0.0.1:5500",
        "http://localhost:5500",

        # Desenvolvimento Flask
        "http://127.0.0.1:5000",
        "http://localhost:5000",
    ]

    # Remove valores vazios e duplicados
    allowed_origins = list(
        dict.fromkeys(
            origin for origin in allowed_origins if origin
        )
    )

    CORS(
        app,
        supports_credentials=True,
        origins=allowed_origins
    )

    # ---------------------------------------------------------
    # CABEÇALHOS CORS
    # ---------------------------------------------------------

    @app.after_request
    def add_cors_headers(response):
        origin = request.headers.get("Origin")

        if origin in allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Headers"] = (
                "Content-Type, Authorization, X-Requested-With, Accept"
            )
            response.headers["Access-Control-Allow-Methods"] = (
                "GET, POST, PUT, DELETE, OPTIONS"
            )

        return response

    # ---------------------------------------------------------
    # BLUEPRINTS
    # ---------------------------------------------------------

    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)

    # ---------------------------------------------------------
    # ROTA PRINCIPAL
    # ---------------------------------------------------------

    @app.route("/")
    def index():
        return send_from_directory(".", "index.html")

    # ---------------------------------------------------------
    # TESTE DO SERVIDOR
    # ---------------------------------------------------------

    @app.route("/api/status")
    def status():
        return {
            "status": "online",
            "message": "Skin Trade Simulator API funcionando!"
        }

    # ---------------------------------------------------------
    # MONGODB
    # ---------------------------------------------------------

    try:
        Database.get_db()
        print("MongoDB conectado com sucesso.")
    except Exception as e:
        print("Aviso: não foi possível conectar ao MongoDB.")
        print(f"Erro: {e}")

    return app


# =============================================================
# IMPORTANTE PARA A VERCEL
# =============================================================
# A Vercel procura uma variável chamada "app" no nível principal.
# Por isso NÃO deixamos app = create_app() apenas dentro do
# if __name__ == "__main__".

app = create_app()


# =============================================================
# EXECUÇÃO LOCAL
# =============================================================

if __name__ == "__main__":

    print("\n" + "=" * 70)
    print("SKIN TRADE SIMULATOR - SERVIDOR BACKEND FLASK ATIVO")
    print("=" * 70)

    print(
        f"Backend API: http://127.0.0.1:{Config.PORT}"
    )

    print(
        f"Frontend App: {Config.FRONTEND_URL}"
    )

    print(
        f"MongoDB URI: "
        f"{'Configurada' if Config.MONGODB_URI else 'NÃO CONFIGURADA'}"
    )

    print(
        "GitHub OAuth: "
        f"{'Configurado' if Config.GITHUB_CLIENT_ID else 'NÃO CONFIGURADO'}"
    )

    print("=" * 70)

    print("Como executar localmente:")
    print("1. Backend: python app.py")
    print("2. Frontend: Live Server")
    print("=" * 70 + "\n")

    app.run(
        host="127.0.0.1",
        port=Config.PORT,
        debug=Config.DEBUG
    )