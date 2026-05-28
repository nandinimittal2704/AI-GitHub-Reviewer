import logging
from typing import Dict, Any
from src.mcp.client import MCPClient
from src.llm_engine import LLMEngine
from src.models.review_schema import AIReviewResult

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("orchestrator")

# Constants for "Budgeting"
MAX_TOKENS_ESTIMATE = 10000

async def process_pr_event(payload: Dict[str, Any]):
    """
    The main coordinator. 
    1. Fetches Context (via MCP)
    2. Decides on a Persona (Security vs Generic)
    3. Calls LLM
    4. Posts Feedback
    """
    # Safe navigation of the dictionary to avoid crashes if keys are missing
    pr_data = payload.get("pull_request", {})
    repo_data = payload.get("repository", {})
    
    repo_full_name = repo_data.get("full_name")
    pr_number = pr_data.get("number")
    
    if not pr_data or not repo_full_name:
        logger.error("Invalid payload: Missing PR or Repo data")
        return

    logger.info(f"Orchestrator: Analyzing PR #{pr_number} in {repo_full_name}")

    # 1. Initialize our Tools
    mcp = MCPClient(repo_name=repo_full_name)
    llm = LLMEngine()

    try:
        # 2. Fetch the PR Diff (Safe Access)
        pr_diff = await mcp.get_pr_diff(pr_number)
        
        if not pr_diff:
            logger.error("Diff is empty or failed to fetch. Aborting review.")
            return
        
        # 3. Budget Check
        if len(pr_diff) > MAX_TOKENS_ESTIMATE:
            logger.warning(f"PR #{pr_number} is too large. Switching to SUMMARY mode.")
            mode = "summary"
        else:
            mode = "detailed"

        # 4. Select Persona
        # Logic: If we see 'secret' or 'key' in diff, activate Security Persona
        if "secret" in pr_diff.lower() or "api_key" in pr_diff.lower():
            persona = "security"
            logger.info("Security Persona Activated")
        else:
            persona = "developer"
            logger.info("General Developer Persona Activated")

        # 5. The "Thinking" Phase(Call LLM)
        review_result: AIReviewResult = await llm.analyze_code(
            diff=pr_diff, 
            persona=persona, 
            mode=mode
        )

        # 6. The "Action" Phase(Post to GitHub)
        comment_url = await mcp.post_comment(
            pr_number=pr_number, 
            review=review_result
        )
        
        logger.info(f"Success! Review posted at: {comment_url}")

    except Exception as e:
        logger.error(f"Orchestration failed: {e}")