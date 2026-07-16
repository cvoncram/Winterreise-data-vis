from config import SCORES_PREFIX, PERFORMANCES_PREFIX


def is_safe_repo_path(path: str) -> bool:
    """
    Only allow paths that stay within the scores/ or performances/
    folders of the repo, with no traversal or absolute paths.
    """
    if not path or path.startswith("/"):
        return False

    if any(part == ".." for part in path.split("/")):
        return False

    return path.startswith(SCORES_PREFIX) or path.startswith(PERFORMANCES_PREFIX)


def is_safe_folder_name(name: str) -> bool:
    """
    A performance folder name must be a bare name, not a path.
    """
    if not name or "/" in name or name in (".", ".."):
        return False
    return True
