from app.scanner.files import list_files


def test_files(tmp_path):
    assert list_files(str(tmp_path)) == []


def test_single_file_in_root(tmp_path):
    (tmp_path / "a.txt").write_text("X")

    assert list_files(str(tmp_path)) == ["a.txt"]


def test_multiple_file_in_root(tmp_path):
    (tmp_path / "a.txt").write_text("X")
    (tmp_path / "b.txt").write_text("X")
    (tmp_path / "c.txt").write_text("X")

    assert list_files(str(tmp_path)) == ["a.txt", "b.txt", "c.txt"]


def test_nested_dir(tmp_path):
    (tmp_path / "app").mkdir()
    (tmp_path / "app" / "models").mkdir()
    (tmp_path / "app" / "models" / "user.py").write_text("X")
    (tmp_path / "app" / "config.py").write_text("X")
    (tmp_path / ".env").write_text("X")

    result: list[str] = list_files(str(tmp_path))

    assert result == sorted(
        [
            ".env",
            "app/models/user.py",
            "app/config.py",
        ]
    )


def test_git_dir_excluded(tmp_path):
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text("X")
    (tmp_path / "file.txt").write_text("X")

    result: list[str] = sorted(list_files(str(tmp_path)))

    assert result == ["file.txt"]


def test_symlink(tmp_path):
    target_dir = tmp_path / "target"
    target_dir.mkdir()
    (target_dir / "inner.txt").write_text("x")

    link_dir = tmp_path / "link_dir"
    link_dir.symlink_to(target_dir, target_is_directory=True)

    result: list[str] = list_files(str(tmp_path))

    assert result == ["target/inner.txt"]


def test_symlink_to_file_outside_repo(tmp_path, tmp_path_factory):
    outside = tmp_path_factory.mktemp("outside") / "secret.txt"
    outside.write_text("X")

    (tmp_path / "link.txt").symlink_to(outside)
    (tmp_path / "real.txt").write_text("X")

    assert list_files(str(tmp_path)) == ["real.txt"]


def test_nonexist_path(tmp_path):
    missing = tmp_path / "does_not_exist"
    assert list_files(str(missing)) == []
