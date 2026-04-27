"""GitHub repository manager for policyengine-us."""

import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

import git
import requests


class GitHubManager:
    """Manages policyengine-us repository from GitHub."""

    def __init__(self, base_path: Path, repo_url: str, branch: str = "master"):
        """
        Initialize GitHub manager.

        Args:
            base_path: Base directory for storing repositories
            repo_url: GitHub repository URL
            branch: Branch to track (default: master)
        """
        self.base_path = base_path
        self.repo_url = repo_url
        self.branch = branch
        self.repo_path = base_path / "policyengine-us"
        self.repo: Optional[git.Repo] = None

        # Ensure base path exists
        self.base_path.mkdir(parents=True, exist_ok=True)

    def ensure_cloned(self) -> Path:
        """
        Ensure repository is cloned. Clone if not present.

        Returns:
            Path to the cloned repository
        """
        if not self.repo_path.exists():
            print(f"Cloning {self.repo_url} (branch: {self.branch})...")
            try:
                # Shallow clone for speed
                git.Repo.clone_from(
                    self.repo_url, self.repo_path, branch=self.branch, depth=1
                )
                print(f"✓ Cloned to {self.repo_path}")
            except Exception as e:
                raise Exception(f"Failed to clone repository: {e}")

        # Initialize repo object
        self.repo = git.Repo(self.repo_path)
        return self.repo_path

    def sync(self) -> dict:
        """
        Pull latest changes from GitHub.

        Returns:
            Dictionary with sync information (commit SHA, message, etc.)
        """
        self.ensure_cloned()

        print(f"Syncing {self.branch} from GitHub...")
        try:
            origin = self.repo.remotes.origin
            origin.pull()
            print("✓ Synced successfully")
        except Exception as e:
            raise Exception(f"Failed to sync repository: {e}")

        # Get commit info
        commit = self.repo.head.commit

        return {
            "sha": commit.hexsha[:7],
            "full_sha": commit.hexsha,
            "message": commit.message.strip(),
            "author": str(commit.author),
            "date": commit.committed_datetime.isoformat(),
            "synced_at": datetime.now().isoformat(),
            "branch": self.branch,
        }

    def get_current_commit(self) -> dict:
        """
        Get current commit information.

        Returns:
            Dictionary with commit details
        """
        self.ensure_cloned()

        commit = self.repo.head.commit

        return {
            "sha": commit.hexsha[:7],
            "full_sha": commit.hexsha,
            "message": commit.message.strip(),
            "author": str(commit.author),
            "date": commit.committed_datetime.isoformat(),
        }

    def get_file_url(self, relative_path: str) -> str:
        """
        Get GitHub URL for a file.

        Args:
            relative_path: Path relative to repository root

        Returns:
            GitHub URL for the file
        """
        repo_base = self.repo_url.replace(".git", "")
        return f"{repo_base}/blob/{self.branch}/{relative_path}"

    def get_file_url_with_lines(
        self, relative_path: str, start_line: int, end_line: Optional[int] = None
    ) -> str:
        """
        Get GitHub URL for specific lines in a file.

        Args:
            relative_path: Path relative to repository root
            start_line: Starting line number
            end_line: Ending line number (optional)

        Returns:
            GitHub URL for the file with line anchors
        """
        base_url = self.get_file_url(relative_path)

        if end_line:
            return f"{base_url}#L{start_line}-L{end_line}"
        else:
            return f"{base_url}#L{start_line}"

    def get_file_content(self, relative_path: str) -> str:
        """
        Get content of a specific file.

        Args:
            relative_path: Path relative to repository root

        Returns:
            File content as string

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        self.ensure_cloned()

        full_path = self.repo_path / relative_path

        if not full_path.exists():
            raise FileNotFoundError(f"{relative_path} not found in repository")

        return full_path.read_text()

    def list_files(self, pattern: str) -> list[Path]:
        """
        List files matching a glob pattern.

        Args:
            pattern: Glob pattern (e.g., "**/*.py")

        Returns:
            List of Path objects matching the pattern
        """
        self.ensure_cloned()
        return list(self.repo_path.glob(pattern))

    def get_repo_path(self) -> Path:
        """Get path to the repository root."""
        self.ensure_cloned()
        return self.repo_path
