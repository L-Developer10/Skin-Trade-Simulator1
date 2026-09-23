from functools import wraps
from flask import Blueprint, request, redirect, session, jsonify
from config import Config
from models.user_model import UserModel
from services.github_service import GitHubOAuthService

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"error": "Sessão não encontrada ou expirada. Faça login com o GitHub ou modo teste.", "code": 401}), 401
        user = UserModel.get_by_id(user_id)
        if not user:
            session.clear()
            return jsonify({"error": "Usuário não encontrado. Faça login novamente.", "code": 401}), 401
        return f(user, *args, **kwargs)
    return decorated_function


@auth_bp.route('/auth/github', methods=['GET'])
def github_login():
    """Redireciona o jogador para a página de autorização oficial do GitHub."""
    if not Config.GITHUB_CLIENT_ID or Config.GITHUB_CLIENT_ID.startswith("seu_") or not Config.GITHUB_CLIENT_SECRET:
        # Se as chaves não foram configuradas, redireciona para o frontend com aviso amigável
        return redirect(f"{Config.FRONTEND_URL}/?auth_error=configure_github_keys")
        
    auth_url = GitHubOAuthService.get_authorization_url()
    return redirect(auth_url)


@auth_bp.route('/auth/github/callback', methods=['GET'])
def github_callback():
    """
    Callback oficial do GitHub após o jogador autorizar o aplicativo.
    Troca o código por token, carrega/cria o usuário no MongoDB e redireciona para o frontend na porta 5500.
    """
    code = request.args.get('code')
    error = request.args.get('error')

    if error:
        return redirect(f"{Config.FRONTEND_URL}/?auth_error={error}")

    if not code:
        return redirect(f"{Config.FRONTEND_URL}/?auth_error=no_code_provided")

    try:
        # Troca code por token exclusivamente no backend
        token = GitHubOAuthService.exchange_code_for_token(code)
        profile = GitHubOAuthService.get_user_profile(token)

        # Cadastra ou carrega no MongoDB
        user = UserModel.get_or_create_user(profile)

        # Salva o ID na sessão
        session['user_id'] = user['id']
        session.permanent = True

        # Redireciona o jogador com sucesso de volta para o frontend :5500
        return redirect(f"{Config.FRONTEND_URL}/?auth=success")
    except Exception as e:
        print(f"[OAuth Erro] {e}")
        return redirect(f"{Config.FRONTEND_URL}/?auth_error=oauth_failed")


@auth_bp.route('/auth/logout', methods=['GET', 'POST'])
def logout():
    """Encerra a sessão do jogador no backend."""
    session.clear()
    if request.is_json or request.headers.get('Accept') == 'application/json':
        return jsonify({"success": True, "message": "Sessão encerrada com sucesso."})
    return redirect(f"{Config.FRONTEND_URL}/")


@auth_bp.route('/api/me', methods=['GET'])
def get_current_user():
    """Retorna os dados do usuário autenticado a partir da sessão."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"authenticated": False}), 200

    try:
        user = UserModel.get_by_id(user_id)
        if not user:
            session.clear()
            return jsonify({"authenticated": False}), 200

        return jsonify({
            "authenticated": True,
            "user": user
        })
    except Exception as e:
        return jsonify({"authenticated": False, "error": str(e)}), 500


@auth_bp.route('/auth/dev-login', methods=['POST'])
@auth_bp.route('/api/login/teste', methods=['POST'])
def dev_login():
    """
    Rota de login de teste local:
    Permite entrar com um usuário de teste sem GitHub e carregar/criar o progresso desse usuário no MongoDB.
    """
    data = request.get_json(silent=True) or {}
    username = data.get("username", "Jogador_CSGO").strip() or "Jogador_CSGO"
    
    mock_profile = {
        "id": 99990000 + abs(hash(username)) % 10000,
        "login": username,
        "name": username.replace("_", " ").title(),
        "avatar_url": f"https://avatars.githubusercontent.com/{username}"
    }
    
    try:
        user = UserModel.get_or_create_user(mock_profile)
        session['user_id'] = user['id']
        session.permanent = True
        return jsonify({
            "success": True,
            "authenticated": True,
            "user": user,
            "message": f"Conectado como {user['nome']} via MongoDB!"
        })
    except Exception as e:
        return jsonify({"error": f"Erro ao conectar ao banco de dados: {e}"}), 500
