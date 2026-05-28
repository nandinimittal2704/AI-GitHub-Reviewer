import os
import logging
import asyncio
import requests
from github import Github, Auth
from src.models.review_schema import AIReviewResult

# Setup Logging
logger = logging.getLogger("mcp_client")

class MCPClient:
    def __init__(self, repo_name: str):
        """
        Initialize the GitHub Client for a specific repository.
        """
        self.repo_name = repo_name
        self.token = os.getenv("GITHUB_TOKEN")
        
        if not self.token:
            logger.error(" GITHUB_TOKEN is missing in .env! Cannot talk to GitHub.")
            raise ValueError("Missing GITHUB_TOKEN")

        # Authenticate with GitHub
        auth = Auth.Token(self.token)
        self.g = Github(auth=auth)
        
        # Get the Repository object immediately to ensure we have access
        try:
            self.repo = self.g.get_repo(self.repo_name)
        except Exception as e:
            logger.error(f" Failed to access repo {self.repo_name}: {e}")
            raise

    async def get_pr_diff(self, pr_number: int) -> str:
        """
        Fetches the raw diff (code changes) of the Pull Request.
        """
        logger.info(f" MCP: Fetching diff for PR #{pr_number} from {self.repo_name}")
        
        try:
            # 1. Get the PR Object
            pr = self.repo.get_pull(pr_number)
            
            # 2. Get the Diff URL (GitHub provides a raw text URL for changes)
            diff_url = pr.url
            
            # 3. Download the Diff Text securely
            # We use requests because PyGithub doesn't provide the raw diff text easily
            headers = {"Authorization": f"token {self.token}",
                       "Accept": "application/vnd.github.v3.diff"}
            # Run blocking request in a separate thread
            response = await asyncio.to_thread(
                requests.get, 
                diff_url, 
                headers=headers, 
                timeout=10
            )
            response.raise_for_status()
            
            return response.text
        
        except requests.exceptions.Timeout:
            # Specific handling for timeouts
            logger.error(f"Timeout while fetching PR #{pr_number}")
            return ""
        
        except requests.exceptions.RequestException as e:
            #Sanitized logging (hide sensitive URL/headers)
            status = e.response.status_code if e.response else "Unknown"
            logger.error(f"HTTP Error fetching diff: Status {status}")
            return ""
        
        except Exception as e:
            logger.error(f" Failed to fetch PR diff: {e}")
            return ""

    async def post_comment(self, pr_number: int, review: AIReviewResult) -> str:
        """
        Posts the AI Review as a formatted comment on the GitHub PR.
        """
        logger.info(f" MCP: Posting comment to PR #{pr_number}...")
        
        try:
            pr = self.repo.get_pull(pr_number)

            # 1. Format the Review (Markdown)
            # This makes the comment look pretty on GitHub
            body = f"##  AI Code Review\n"
            body += f"**Security Score:** {review.security_score}/100 🛡️\n"
            body += f"**Summary:** {review.summary}\n\n"
            body += "---\n###  Key Findings\n"
            
            if not review.findings:
                body += "\nNo major issues found. Nice job!"
            else:
                for finding in review.findings:
                    icon = "🔴" if "CRITICAL" in finding.severity or "HIGH" in finding.severity else "⚠️"
                    body += f"\n{icon} **{finding.severity}** - `{finding.file_path}:{finding.line_start}`\n"
                    body += f"**Issue:** {finding.suggestion}\n"

            body += "\n\n---\n*Automated Response by AI Code Reviewer*"

            # 2. Post the Comment
            comment = pr.create_issue_comment(body)
            
            return comment.html_url

        except Exception as e:
            logger.error(f"Failed to post comment: {e}")
            return "error_posting_comment"