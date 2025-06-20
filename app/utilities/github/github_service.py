import requests
from typing import List

from app.utilities.github.github_models import Repo
from app.utilities.github.github_exceptions import (
    GitHubAuthError,
    GitHubAPIError,
)


GITHUB_API_BASE = "https://api.github.com"


def validate_token(token: str) -> dict:
    """
    Test GitHub token validity and return authenticated user info.
    """
    headers = {"Authorization": f"token {token}"}
    response = requests.get(f"{GITHUB_API_BASE}/user", headers=headers)

    if response.status_code == 401:
        raise GitHubAuthError("Invalid GitHub token.")

    if not response.ok:
        raise GitHubAPIError(f"GitHub returned {response.status_code}: {response.text}")

    return response.json()


def list_user_repos(token: str) -> List[Repo]:
    """
    Return a list of repos visible to the authenticated user.
    """
    headers = {"Authorization": f"token {token}"}
    response = requests.get(f"{GITHUB_API_BASE}/user/repos", headers=headers, params={"per_page": 100})

    if not response.ok:
        raise GitHubAPIError(f"Failed to list user repos: {response.text}")

    repo_dicts = response.json()

    return [
        Repo(
            name=r["name"],
            full_name=r["full_name"],
            private=r["private"],
            default_branch=r["default_branch"],
            owner=r["owner"]["login"]
        )
        for r in repo_dicts
    ]

from app.utilities.github.github_models import TreeItem

def list_repo_tree(token: str, repo: str, branch: str, path: str = "") -> List[TreeItem]:
    """
    List files and folders at a specific path in a repo's branch.
    Uses the GitHub v3 Contents API (not the full recursive tree).
    """
    headers = {"Authorization": f"token {token}"}
    api_url = f"{GITHUB_API_BASE}/repos/{repo}/contents/{path}"
    params = {"ref": branch}

    response = requests.get(api_url, headers=headers, params=params)
    if response.status_code == 404:
        raise FileNotFoundError(f"Path '{path}' not found in {repo}@{branch}")
    if not response.ok:
        raise GitHubAPIError(f"Failed to fetch repo tree: {response.text}")

    contents = response.json()

    if isinstance(contents, dict):  # single file
        contents = [contents]

    return [
        TreeItem(
            path=item["path"],
            type=item["type"],
            sha=item["sha"],
            size=item.get("size"),
        )
        for item in contents
    ]


def get_file_content(token: str, repo: str, branch: str, path: str) -> str:
    """
    Retrieve the raw content of a file at a given path and branch.
    """
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3.raw"
    }
    api_url = f"{GITHUB_API_BASE}/repos/{repo}/contents/{path}"
    params = {"ref": branch}

    response = requests.get(api_url, headers=headers, params=params)
    if response.status_code == 404:
        raise FileNotFoundError(f"File '{path}' not found in {repo}@{branch}")
    if not response.ok:
        raise GitHubAPIError(f"Failed to fetch file content: {response.text}")

    return response.text

import base64
import json

def create_branch(token: str, repo: str, source_branch: str, new_branch: str) -> str:
    """
    Create a new branch from an existing branch.
    Returns the SHA of the new branch reference.
    """
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Step 1: Get the source branch's latest commit SHA
    ref_url = f"{GITHUB_API_BASE}/repos/{repo}/git/ref/heads/{source_branch}"
    ref_response = requests.get(ref_url, headers=headers)
    if not ref_response.ok:
        raise GitHubAPIError(f"Failed to fetch source branch: {ref_response.text}")
    sha = ref_response.json()["object"]["sha"]

    # Step 2: Create the new branch
    create_url = f"{GITHUB_API_BASE}/repos/{repo}/git/refs"
    payload = {
        "ref": f"refs/heads/{new_branch}",
        "sha": sha
    }
    response = requests.post(create_url, headers=headers, json=payload)
    if not response.ok:
        raise GitHubAPIError(f"Failed to create branch: {response.text}")

    return response.json()["ref"]


def commit_file(token: str, repo: str, branch: str, path: str, content: str, message: str) -> str:
    """
    Create or update a file on the given branch.
    Returns the file's commit SHA.
    """
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Step 1: Check if the file already exists
    get_url = f"{GITHUB_API_BASE}/repos/{repo}/contents/{path}"
    get_params = {"ref": branch}
    get_resp = requests.get(get_url, headers=headers, params=get_params)

    sha = get_resp.json().get("sha") if get_resp.ok else None

    # Step 2: Encode content and prepare payload
    encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")

    payload = {
        "message": message,
        "content": encoded_content,
        "branch": branch,
    }
    if sha:
        payload["sha"] = sha  # required for update

    put_resp = requests.put(get_url, headers=headers, json=payload)
    if not put_resp.ok:
        raise GitHubAPIError(f"Failed to commit file: {put_resp.text}")

    return put_resp.json()["commit"]["sha"]


def create_pull_request(token: str, repo: str, title: str, head: str, base: str, body: str = "") -> str:
    """
    Open a pull request from `head` to `base` with a title/body.
    Returns the PR URL.
    """
    headers = {"Authorization": f"token {token}"}
    payload = {
        "title": title,
        "head": head,
        "base": base,
        "body": body
    }

    response = requests.post(f"{GITHUB_API_BASE}/repos/{repo}/pulls", headers=headers, json=payload)
    if not response.ok:
        raise GitHubAPIError(f"Failed to create PR: {response.text}")

    return response.json()["html_url"]


def get_pull_request_diff(token: str, repo: str, pr_number: int) -> str:
    """
    Returns a unified diff string for the specified pull request.
    """
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3.diff"
    }

    url = f"{GITHUB_API_BASE}/repos/{repo}/pulls/{pr_number}"
    response = requests.get(url, headers=headers)

    if not response.ok:
        raise GitHubAPIError(f"Failed to retrieve PR diff: {response.text}")

    return response.text

from app.utilities.github.github_models import FileVersion


def get_file_history(token: str, repo: str, path: str, branch: str = "main") -> List[FileVersion]:
    """
    Return a list of commits that modified the given file.
    """
    headers = {"Authorization": f"token {token}"}
    url = f"{GITHUB_API_BASE}/repos/{repo}/commits"
    params = {"path": path, "sha": branch, "per_page": 100}

    response = requests.get(url, headers=headers, params=params)
    if not response.ok:
        raise GitHubAPIError(f"Failed to retrieve file history: {response.text}")

    return [
        FileVersion(
            sha=commit["sha"],
            date=commit["commit"]["committer"]["date"],
            author=commit["commit"]["committer"]["name"],
            message=commit["commit"]["message"]
        )
        for commit in response.json()
    ]


def get_file_at_commit(token: str, repo: str, sha: str, path: str) -> str:
    """
    Get the content of a file at a specific commit.
    """
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3.raw"
    }
    url = f"{GITHUB_API_BASE}/repos/{repo}/contents/{path}"
    params = {"ref": sha}

    response = requests.get(url, headers=headers, params=params)
    if not response.ok:
        raise GitHubAPIError(f"Failed to fetch file at commit {sha}: {response.text}")

    return response.text


