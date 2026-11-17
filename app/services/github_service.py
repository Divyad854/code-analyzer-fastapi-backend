from urllib.parse import urlencode
import httpx
from fastapi import HTTPException
from app.core.config import settings

API = "https://api.github.com"

def github_headers(token: str):
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

def build_authorization_url(state: str) -> str:
    if not settings.GITHUB_CLIENT_ID or not settings.GITHUB_CLIENT_SECRET:
        raise HTTPException(status_code=503, detail="GitHub OAuth is not configured")
    params = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "redirect_uri": settings.GITHUB_REDIRECT_URI,
        # read:user: Allows reading the authenticated user's profile.
        # repo: Requests repository access, including private repositories, 
        # subject to granted permissions.
        "scope": "read:user repo",
        "state": state,
    }
    return "https://github.com/login/oauth/authorize?" + urlencode(params)

def exchange_code(code: str) -> str:
    with httpx.Client(timeout=15) as client:
        response = client.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={"client_id": settings.GITHUB_CLIENT_ID, "client_secret": settings.GITHUB_CLIENT_SECRET, "code": code, "redirect_uri": settings.GITHUB_REDIRECT_URI},
        )
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="GitHub token exchange failed")
    data = response.json()
    token = data.get("access_token")
    if not token:
        raise HTTPException(status_code=400, detail="GitHub authorization was not completed")
    return token

def github_get(path: str, token: str, params=None):
    try:
        with httpx.Client(timeout=20, follow_redirects=False) as client:
            response = client.get(f"{API}{path}", headers=github_headers(token), params=params)
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Could not connect to GitHub")
    if response.status_code == 401:
        raise HTTPException(status_code=401, detail="GitHub authorization expired or was revoked")
    if response.status_code == 403:
        raise HTTPException(status_code=429, detail="GitHub API rate limit or permission limit reached")
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="GitHub resource not found or not accessible")
    if response.status_code >= 400:
        raise HTTPException(status_code=502, detail="GitHub API request failed")
    return response.json()
