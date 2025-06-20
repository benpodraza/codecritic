class GitHubAuthError(Exception):
    """Raised when authentication with GitHub fails."""
    pass


class GitHubAPIError(Exception):
    """Raised when GitHub API returns a non-successful response."""
    pass


class RepoNotFoundError(Exception):
    """Raised when a specified GitHub repository does not exist or is inaccessible."""
    pass


class FileNotFoundError(Exception):
    """Raised when a requested file does not exist in the GitHub repository."""
    pass
