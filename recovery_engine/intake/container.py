from __future__ import annotations

import zipfile
from dataclasses import dataclass
from pathlib import Path

from recovery_engine.utils.hashing import sha256_bytes, sha256_file


@dataclass(frozen=True)
class SourceFile:
    path: str
    size: int
    sha256: str


class SourceContainer:
    """Read a source folder or zip without changing the caller's export."""

    def __init__(self, source: Path):
        self.source = Path(source)
        if not self.source.exists():
            raise FileNotFoundError(f"Source not found: {self.source}")
        self.is_zip = self.source.is_file() and self.source.suffix.lower() == ".zip"

    def iter_files(self) -> list[SourceFile]:
        if self.is_zip:
            return self._iter_zip_files()
        return self._iter_directory_files()

    def read_bytes(self, relative_path: str) -> bytes:
        if self.is_zip:
            with zipfile.ZipFile(self.source) as archive:
                return archive.read(relative_path)
        return (self.source / relative_path).read_bytes()

    def read_text(self, relative_path: str) -> str:
        data = self.read_bytes(relative_path)
        for encoding in ("utf-8", "utf-8-sig", "latin-1"):
            try:
                return data.decode(encoding)
            except UnicodeDecodeError:
                continue
        return data.decode("utf-8", errors="replace")

    def fingerprint(self) -> str:
        rows = [f"{item.path}|{item.size}|{item.sha256}" for item in self.iter_files()]
        return sha256_bytes("\n".join(sorted(rows)).encode("utf-8"))

    def _iter_directory_files(self) -> list[SourceFile]:
        root = self.source.resolve()
        files: list[SourceFile] = []
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(root).as_posix()
            files.append(SourceFile(path=rel, size=path.stat().st_size, sha256=sha256_file(path)))
        return files

    def _iter_zip_files(self) -> list[SourceFile]:
        files: list[SourceFile] = []
        with zipfile.ZipFile(self.source) as archive:
            for info in sorted(archive.infolist(), key=lambda item: item.filename):
                if info.is_dir():
                    continue
                data = archive.read(info.filename)
                files.append(SourceFile(path=info.filename, size=len(data), sha256=sha256_bytes(data)))
        return files
