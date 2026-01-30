import time
import jwt
import base64
import requests

from app.core.config import settings


class GitHubService:
    API = "https://api.github.com"

    @staticmethod
    def installation_token() -> str:
        payload = {
            "iat": int(time.time()) - 60,
            "exp": int(time.time()) + 600,
            "iss": settings.GITHUB_APP_ID,
        }

        app_jwt = jwt.encode(
            payload,
            settings.GITHUB_PRIVATE_KEY,
            algorithm="RS256",
        )

        res = requests.post(
            f"{GitHubService.API}/app/installations/{settings.GITHUB_INSTALLATION_ID}/access_tokens",
            headers={
                "Authorization": f"Bearer {app_jwt}",
                "Accept": "application/vnd.github+json",
            },
        )
        res.raise_for_status()
        return res.json()["token"]

    @staticmethod
    def ensure_branch(token: str, branch: str):
        headers = {"Authorization": f"token {token}"}

        # Branch exists?
        r = requests.get(
            f"{GitHubService.API}/repos/{settings.GITHUB_REPO}/git/ref/heads/{branch}",
            headers=headers,
        )
        if r.status_code == 200:
            return

        # Create branch from main
        main_ref = requests.get(
            f"{GitHubService.API}/repos/{settings.GITHUB_REPO}/git/ref/heads/main",
            headers=headers,
        ).json()

        sha = main_ref["object"]["sha"]

        requests.post(
            f"{GitHubService.API}/repos/{settings.GITHUB_REPO}/git/refs",
            headers=headers,
            json={
                "ref": f"refs/heads/{branch}",
                "sha": sha,
            },
        ).raise_for_status()

    @staticmethod
    def upsert_file(token: str, branch: str, path: str, content: str):
        headers = {"Authorization": f"token {token}"}
        url = f"{GitHubService.API}/repos/{settings.GITHUB_REPO}/contents/{path}"

        encoded = base64.b64encode(content.encode()).decode()

        payload = {
            "message": f"docs: update {path}",
            "content": encoded,
            "branch": branch,
        }

        res = requests.put(url, headers=headers, json=payload)
        res.raise_for_status()
        return res.json()

    @staticmethod
    def open_pull_request(token: str, branch: str, title: str, body: str):
        headers = {"Authorization": f"token {token}"}

        res = requests.post(
            f"{GitHubService.API}/repos/{settings.GITHUB_REPO}/pulls",
            headers=headers,
            json={
                "title": title,
                "head": branch,
                "base": "main",
                "body": body,
            },
        )
        res.raise_for_status()
        return res.json()["html_url"]
