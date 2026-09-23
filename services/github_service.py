import requests
from config import Config

class GitHubOAuthService:
    AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
    TOKEN_URL = "https://github.com/login/oauth/access_token"
    USER_API_URL = "https://api.github.com/user"

    @classmethod
    def get_authorization_url(cls):
        """Retorna a URL oficial para redirecionar o usuário para o login do GitHub."""
        client_id = Config.GITHUB_CLIENT_ID
        redirect_uri = Config.GITHUB_REDIRECT_URI
        scope = "read:user user:email"
        
        return f"{cls.AUTHORIZE_URL}?client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}"

    @classmethod
    def exchange_code_for_token(cls, code):
        """Troca o authorization code pelo access token com o Client Secret (exclusivo do backend)."""
        payload = {
            "client_id": Config.GITHUB_CLIENT_ID,
            "client_secret": Config.GITHUB_CLIENT_SECRET,
            "code": code,
            "redirect_uri": Config.GITHUB_REDIRECT_URI
        }
        headers = {"Accept": "application/json"}
        
        response = requests.post(cls.TOKEN_URL, json=payload, headers=headers, timeout=10)
        if response.status_code != 200:
            raise ValueError(f"Falha ao trocar código do GitHub: {response.text}")
            
        data = response.json()
        if "error" in data:
            raise ValueError(f"Erro OAuth do GitHub: {data.get('error_description', data.get('error'))}")
            
        return data.get("access_token")

    @classmethod
    def get_user_profile(cls, access_token):
        """Busca o perfil público do usuário autenticado no GitHub."""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }
        
        response = requests.get(cls.USER_API_URL, headers=headers, timeout=10)
        if response.status_code != 200:
            raise ValueError(f"Falha ao buscar perfil no GitHub: {response.text}")
            
        return response.json()
