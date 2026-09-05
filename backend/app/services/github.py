import httpx
from fastapi import HTTPException, status


class GitHubService:
    """
    A service class for interacting with the GitHub REST API.
    Example repo parsing: https://github.com/ranjeetsingh63/ai-developer-copilot
    """
    BASE_URL = "https://api.github.com"

    def __init__(self, pat_token: str | None = None):
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if pat_token:
            self.headers["Authorization"] = f"Bearer {pat_token}"

        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers=self.headers,
            timeout=10.0
        )

    async def close(self) -> None:
        """Closes the underlying httpx client."""
        await self.client.aclose()

    def _parse_github_url(self, url: str) -> tuple[str, str]:
        """Extracts owner and repo name from a standard GitHub URL."""
        parts = url.rstrip("/").split("/")
        if len(parts) < 2:
            raise ValueError("Invalid GitHub URL")
        return parts[-2], parts[-1]

    async def verify_repository(self, github_url: str) -> dict:
        """
        Hits the GitHub API to confirm the repository exists and is accessible.
        Returns the raw JSON response containing repo metadata.
        """
        try:
            owner, repo = self._parse_github_url(github_url)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not parse GitHub URL."
            )

        response = await self.client.get(f"/repos/{owner}/{repo}")

        if response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Repository not found on GitHub or is private without sufficient token scope."
            )
        elif response.status_code == 403:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="GitHub API rate limit exceeded."
            )

        response.raise_for_status()
        return response.json()