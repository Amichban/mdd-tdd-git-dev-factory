"""
GitHub Bridge Service

Manages all GitHub operations for automated workflow:
- Issue creation and management
- Branch creation
- PR creation and merging
- Worktree management
"""

import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Optional
from dataclasses import dataclass


@dataclass
class Issue:
    """Represents a GitHub issue."""
    number: int
    title: str
    body: str
    labels: list[str]
    url: str


@dataclass
class PullRequest:
    """Represents a GitHub pull request."""
    number: int
    title: str
    body: str
    head_branch: str
    base_branch: str
    url: str
    checks_passing: bool = False


@dataclass
class Worktree:
    """Represents a git worktree."""
    path: Path
    branch: str
    issue_number: Optional[int] = None


class GitHubBridge:
    """Manages all GitHub operations for the orchestrator."""

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.worktrees_dir = repo_path / ".worktrees"
        self.worktrees_dir.mkdir(exist_ok=True)

    def run_gh(self, args: list[str]) -> str:
        """Run GitHub CLI command."""
        result = subprocess.run(
            ["gh"] + args,
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            raise Exception(f"GitHub CLI error: {result.stderr}")
        return result.stdout.strip()

    def run_git(self, args: list[str], cwd: Optional[Path] = None) -> str:
        """Run git command."""
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd or self.repo_path,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            raise Exception(f"Git error: {result.stderr}")
        return result.stdout.strip()

    # Issue Operations

    def create_issue(
        self,
        title: str,
        body: str,
        labels: list[str] = None
    ) -> Issue:
        """Create a GitHub issue."""
        args = ["issue", "create", "--title", title, "--body", body]

        if labels:
            for label in labels:
                args.extend(["--label", label])

        output = self.run_gh(args)

        # Parse issue URL to get number
        # Output format: https://github.com/owner/repo/issues/123
        url = output.strip()
        number = int(url.split("/")[-1])

        return Issue(
            number=number,
            title=title,
            body=body,
            labels=labels or [],
            url=url
        )

    def get_issue(self, number: int) -> Issue:
        """Get issue details."""
        output = self.run_gh([
            "issue", "view", str(number), "--json",
            "number,title,body,labels,url"
        ])
        data = json.loads(output)
        return Issue(
            number=data["number"],
            title=data["title"],
            body=data["body"],
            labels=[l["name"] for l in data.get("labels", [])],
            url=data["url"]
        )

    def list_open_issues(self, labels: list[str] = None) -> list[Issue]:
        """List open issues, optionally filtered by labels."""
        args = ["issue", "list", "--state", "open", "--json",
                "number,title,body,labels,url"]

        if labels:
            for label in labels:
                args.extend(["--label", label])

        output = self.run_gh(args)
        issues = json.loads(output)

        return [
            Issue(
                number=i["number"],
                title=i["title"],
                body=i["body"],
                labels=[l["name"] for l in i.get("labels", [])],
                url=i["url"]
            )
            for i in issues
        ]

    # Branch Operations

    def create_branch(self, branch_name: str, from_branch: str = "main") -> str:
        """Create a new branch."""
        self.run_git(["checkout", from_branch])
        self.run_git(["pull", "origin", from_branch])
        self.run_git(["checkout", "-b", branch_name])
        return branch_name

    def branch_exists(self, branch_name: str) -> bool:
        """Check if branch exists."""
        try:
            self.run_git(["rev-parse", "--verify", branch_name])
            return True
        except Exception:
            return False

    # Worktree Operations

    def create_worktree(self, issue_number: int, branch_name: str) -> Worktree:
        """Create a git worktree for parallel development."""
        worktree_path = self.worktrees_dir / f"issue-{issue_number}"

        if worktree_path.exists():
            # Worktree already exists
            return Worktree(
                path=worktree_path,
                branch=branch_name,
                issue_number=issue_number
            )

        # Create branch if it doesn't exist
        if not self.branch_exists(branch_name):
            self.run_git(["branch", branch_name, "main"])

        # Create worktree
        self.run_git(["worktree", "add", str(worktree_path), branch_name])

        return Worktree(
            path=worktree_path,
            branch=branch_name,
            issue_number=issue_number
        )

    def remove_worktree(self, worktree: Worktree):
        """Remove a git worktree."""
        self.run_git(["worktree", "remove", str(worktree.path), "--force"])

    def list_worktrees(self) -> list[Worktree]:
        """List all worktrees."""
        output = self.run_git(["worktree", "list", "--porcelain"])
        worktrees = []

        current_path = None
        current_branch = None

        for line in output.split("\n"):
            if line.startswith("worktree "):
                current_path = Path(line.split(" ", 1)[1])
            elif line.startswith("branch "):
                current_branch = line.split("/")[-1]
                if current_path and current_path != self.repo_path:
                    # Extract issue number from path if present
                    issue_number = None
                    if current_path.name.startswith("issue-"):
                        try:
                            issue_number = int(current_path.name.split("-")[1])
                        except (IndexError, ValueError):
                            pass

                    worktrees.append(Worktree(
                        path=current_path,
                        branch=current_branch,
                        issue_number=issue_number
                    ))
                current_path = None
                current_branch = None

        return worktrees

    # Pull Request Operations

    def create_pr(
        self,
        title: str,
        body: str,
        head_branch: str,
        base_branch: str = "main",
        labels: list[str] = None
    ) -> PullRequest:
        """Create a pull request."""
        # Push branch first
        self.run_git(["push", "-u", "origin", head_branch])

        args = [
            "pr", "create",
            "--title", title,
            "--body", body,
            "--head", head_branch,
            "--base", base_branch
        ]

        if labels:
            for label in labels:
                args.extend(["--label", label])

        output = self.run_gh(args)
        url = output.strip()
        number = int(url.split("/")[-1])

        return PullRequest(
            number=number,
            title=title,
            body=body,
            head_branch=head_branch,
            base_branch=base_branch,
            url=url
        )

    def get_pr_status(self, pr_number: int) -> dict:
        """Get PR status including checks."""
        output = self.run_gh([
            "pr", "view", str(pr_number), "--json",
            "number,title,state,mergeable,statusCheckRollup"
        ])
        return json.loads(output)

    def merge_pr(self, pr_number: int, method: str = "squash") -> bool:
        """Merge a pull request."""
        try:
            self.run_gh([
                "pr", "merge", str(pr_number),
                f"--{method}",
                "--delete-branch"
            ])
            return True
        except Exception:
            return False

    def list_open_prs(self) -> list[PullRequest]:
        """List open pull requests."""
        output = self.run_gh([
            "pr", "list", "--state", "open", "--json",
            "number,title,body,headRefName,baseRefName,url"
        ])
        prs = json.loads(output)

        return [
            PullRequest(
                number=pr["number"],
                title=pr["title"],
                body=pr["body"],
                head_branch=pr["headRefName"],
                base_branch=pr["baseRefName"],
                url=pr["url"]
            )
            for pr in prs
        ]

    # Commit Operations

    def commit_and_push(
        self,
        message: str,
        files: list[str] = None,
        worktree: Optional[Worktree] = None
    ):
        """Commit changes and push."""
        cwd = worktree.path if worktree else self.repo_path

        if files:
            for f in files:
                self.run_git(["add", f], cwd=cwd)
        else:
            self.run_git(["add", "-A"], cwd=cwd)

        self.run_git(["commit", "-m", message], cwd=cwd)
        self.run_git(["push"], cwd=cwd)

    # Utility Methods

    def get_current_branch(self) -> str:
        """Get current branch name."""
        return self.run_git(["rev-parse", "--abbrev-ref", "HEAD"])

    def has_uncommitted_changes(self) -> bool:
        """Check if there are uncommitted changes."""
        output = self.run_git(["status", "--porcelain"])
        return bool(output.strip())

    def get_files_changed_in_pr(self, pr_number: int) -> list[str]:
        """Get list of files changed in a PR."""
        output = self.run_gh([
            "pr", "view", str(pr_number), "--json", "files"
        ])
        data = json.loads(output)
        return [f["path"] for f in data.get("files", [])]
