import os
from pathlib import Path
from git import InvalidGitRepositoryError, Repo


def get_code_files(root_path):
    """
    Recursively traverses a directory and returns all code files,
    using Git to respect .gitignore

    Args:
        root_path: Path to the directory to analyze

    Returns:
        List of code file paths
    """
    root_path = Path(root_path).resolve()

    # Extensions to ignore (images, fonts, binaries, etc.)
    ignored_extensions = {
        # Images
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.ico', '.webp',
        # Fonts
        '.ttf', '.otf', '.woff', '.woff2', '.eot',
        # Videos/Audio
        '.mp4', '.avi', '.mov', '.mp3', '.wav',
        # Binaries/Compiled
        '.pyc', '.pyo', '.so', '.dll', '.exe', '.bin',
        # Archives
        '.zip', '.tar', '.gz', '.rar',
        # Others
        '.pdf', '.doc', '.docx'
    }

    # Open the Git repository
    try:
        repo = Repo(root_path, search_parent_directories=True)
        git_root = Path(repo.working_dir)
    except InvalidGitRepositoryError as e:
        raise ValueError(
            f"The directory {root_path} is not a Git repository.") from e

    # Get all files not ignored by Git
    # git ls-files lists all tracked + non-ignored files
    tracked_files = repo.git.ls_files().split('\n')
    untracked_files = repo.untracked_files

    all_files = set(tracked_files + untracked_files)

    code_files: list[str] = []
    for file_path in all_files:
        full_path = git_root / file_path

        if not full_path.exists() or not full_path.is_file():
            continue

        try:
            full_path.relative_to(root_path)
        except ValueError:
            continue

        if full_path.suffix.lower() in ignored_extensions:
            continue

        code_files.append(str(full_path))

    # TODO Only add main.ts, index.ts, package.json, tsconfig.json for test purposes
    code_files = [f for f in code_files if f.split("/")[-1] in {
        "main.ts", "index.ts", "package.json", "tsconfig.json"
    }] + code_files

    return sorted(code_files)
