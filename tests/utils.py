from pathlib import Path


def get_test_folder_path():
    test_repo_folder: Path = Path(__file__).resolve().parent / "test-repo"
    return test_repo_folder
