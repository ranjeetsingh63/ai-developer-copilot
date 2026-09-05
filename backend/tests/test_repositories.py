import pytest
from backend.app.services.github import GitHubService

# Automatically mock GitHub verification for all tests in this file so they don't hit the real internet
@pytest.fixture(autouse=True)
def mock_github_verification(monkeypatch):
    async def mock_verify(self, github_url: str):
        # Return a fake successful response from GitHub
        return {
            "name": github_url.split("/")[-1],
            "default_branch": "main"
        }
    monkeypatch.setattr(GitHubService, "verify_repository", mock_verify)