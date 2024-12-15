# Filename: /core/git_manager.py

import subprocess
import logging

# Initialize logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def create_git_commit(sync_log):
    """
    Automatically create a Git commit with a meaningful message.
    """
    try:
        commit_message = "Auto-sync: "
        changes = []

        if sync_log["updated"]:
            changes.append(f"Updated {len(sync_log['updated'])} files")
        if sync_log["added"]:
            changes.append(f"Added {len(sync_log['added'])} files")
        if sync_log["skipped"]:
            changes.append(f"Skipped {len(sync_log['skipped'])} unchanged files")

        commit_message += ", ".join(changes) if changes else "No changes detected"

        # Stage changes and create a commit
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", commit_message], check=True)

        logger.info(f"[GIT COMMIT] {commit_message}")
        return commit_message

    except subprocess.CalledProcessError as e:
        error_message = f"Git commit failed: {e.stderr}"
        logger.error(error_message, exc_info=True)
        return error_message


def push_to_git():
    """
    Push committed changes to the remote Git repository.
    """
    try:
        push_result = subprocess.run(
            ["git", "push"],
            check=True,
            capture_output=True,
            text=True
        )
        logger.info("[GIT PUSH] Push successful.")
        return push_result.stdout
    except subprocess.CalledProcessError as e:
        error_message = f"Git push failed: {e.stderr}"
        logger.error(error_message, exc_info=True)
        return error_message