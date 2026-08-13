import os


def list_files(repo_path: str) -> list[str]:
    files: list[str] = []

    for dirpath, dirnames, filenames in os.walk(repo_path, followlinks=False):
        if ".git" in dirnames:
            dirnames.remove(".git")

        for name in filenames:
            file_path: str = os.path.join(dirpath, name)

            if os.path.islink(file_path):
                continue

            rel_path: str = os.path.relpath(file_path, repo_path)
            files.append(rel_path)

    files.sort()
    return files
