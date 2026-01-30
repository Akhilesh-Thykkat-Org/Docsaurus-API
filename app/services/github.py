import time
import jwt
import base64
import requests

from app.core.config import settings


class GitHubService:
    API = "https://api.github.com"
    TIMEOUT = 10

    # -------------------------
    # Core headers
    # -------------------------
    @staticmethod
    def _headers(token: str | None = None) -> dict:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if token:
            headers["Authorization"] = f"token {token}"
        return headers

    # -------------------------
    # Installation token
    # -------------------------
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
            timeout=GitHubService.TIMEOUT,
        )
        res.raise_for_status()
        return res.json()["token"]

    # -------------------------
    # Branch management
    # -------------------------
    @staticmethod
    def ensure_branch(token: str, branch: str, base: str = "main") -> None:
        headers = GitHubService._headers(token)

        # Check branch exists
        r = requests.get(
            f"{GitHubService.API}/repos/{settings.GITHUB_REPO}/git/ref/heads/{branch}",
            headers=headers,
            timeout=GitHubService.TIMEOUT,
        )
        if r.status_code == 200:
            return

        # Get base SHA
        base_ref = requests.get(
            f"{GitHubService.API}/repos/{settings.GITHUB_REPO}/git/ref/heads/{base}",
            headers=headers,
            timeout=GitHubService.TIMEOUT,
        )
        base_ref.raise_for_status()

        sha = base_ref.json()["object"]["sha"]

        # Create branch
        create = requests.post(
            f"{GitHubService.API}/repos/{settings.GITHUB_REPO}/git/refs",
            headers=headers,
            json={"ref": f"refs/heads/{branch}", "sha": sha},
            timeout=GitHubService.TIMEOUT,
        )

        # Branch already exists = OK
        if create.status_code not in (201, 422):
            create.raise_for_status()

    # -------------------------
    # File upsert (create OR update)
    # -------------------------
    @staticmethod
    def upsert_file(token: str, branch: str, path: str, content: str):
        headers = GitHubService._headers(token)
        url = f"{GitHubService.API}/repos/{settings.GITHUB_REPO}/contents/{path}"

        encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")

        payload = {
            "message": f"docs: update {path}",
            "content": encoded,
            "branch": branch,
        }

        # Check if file already exists (needed for update)
        existing = requests.get(
            url,
            headers=headers,
            params={"ref": branch},
            timeout=GitHubService.TIMEOUT,
        )

        if existing.status_code == 200:
            payload["sha"] = existing.json()["sha"]

        res = requests.put(
            url,
            headers=headers,
            json=payload,
            timeout=GitHubService.TIMEOUT,
        )
        res.raise_for_status()
        return res.json()

    # -------------------------
    # PR creation (deduplicated)
    # -------------------------
    @staticmethod
    def open_pull_request(token: str, branch: str, title: str, body: str):
        headers = GitHubService._headers(token)

        # Check if PR already exists
        prs = requests.get(
            f"{GitHubService.API}/repos/{settings.GITHUB_REPO}/pulls",
            headers=headers,
            params={"state": "open", "head": f"{settings.GITHUB_REPO.split('/')[0]}:{branch}"},
            timeout=GitHubService.TIMEOUT,
        ).json()

        if prs:
            return prs[0]["html_url"]

        # Create PR
        res = requests.post(
            f"{GitHubService.API}/repos/{settings.GITHUB_REPO}/pulls",
            headers=headers,
            json={
                "title": title,
                "head": branch,
                "base": "main",
                "body": body,
            },
            timeout=GitHubService.TIMEOUT,
        )
        res.raise_for_status()
        return res.json()["html_url"]
