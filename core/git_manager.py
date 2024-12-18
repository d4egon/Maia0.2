from subprocess import run, CalledProcessError
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def create_git_commit(sync_log):
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
        run(["git", "add", "."], check=True)
        run(["git", "commit", "-m", commit_message], check=True)
        logger.info(f"[GIT COMMIT] {commit_message}")
        return commit_message
    except CalledProcessError as e:
        logger.error(f"Git commit failed: {e.stderr}", exc_info=True)
        return str(e)

def push_to_git():
    try:
        push_result = run(["git", "push"], check=True, capture_output=True, text=True)
        logger.info("[GIT PUSH] Push successful.")
        return push_result.stdout
    except CalledProcessError as e:
        logger.error(f"Git push failed: {e.stderr}", exc_info=True)
        return str(e)
