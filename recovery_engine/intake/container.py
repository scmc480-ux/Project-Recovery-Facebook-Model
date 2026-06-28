from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import zipfile

from recovery_engine.utils.hashing import sha256_bytes, sha256_file, sha256_text


@dataclass(frozen=True)
class SourceFile:
    path: str
    size: int
    sha256: str


class SourceContainer:
    def __init__(self, source: Path):
        self.source = Path(source)
        self._inventory: list[SourceFile] | None = None
        if self.source.is_dir():
            self._kind = "directory"
        elif self.source.is_file() and self.source.suffix.lower() == ".zip":
            self._kind = "zip"
        else:
            raise ValueError(f"Source must be a directory or .zip file: {self.source}")

    def iter_files(self) -> list[SourceFile]:
        if self._inventory is not None:
            return list(self._inventory)

        if self._kind == "directory":
            inventory = [
                SourceFile(
                    path=path.relative_to(self.source).as_posix(),
                    size=path.stat().st_size,
                    sha256=sha256_file(path),
                )
                for path in sorted(self.source.rglob("*"))
                if path.is_file()
            ]
        else:
            with zipfile.ZipFile(self.source) as archive:
                inventory = [
                    SourceFile(
                        path=info.filename,
                        size=info.file_size,
                        sha256=sha256_bytes(archive.read(info.filename)),
                    )
                    for info in archive.infolist()
                    if not info.is_dir()
                ]

        self._inventory = inventory
        return list(inventory)

    def read_bytes(self, path: str) -> bytes:
        if self._kind == "directory":
            return (self.source / path).read_bytes()

        normalized = path.replace("\\", "/")
        with zipfile.ZipFile(self.source) as archive:
            return archive.read(normalized)

    def read_text(self, path: str) -> str:
        return self.read_bytes(path).decode("utf-8", errors="replace")

    def fingerprint(self) -> str:
        lines = [f"{item.path}|{item.size}|{item.sha256}" for item in self.iter_files()]
        return sha256_text("\n".join(lines))
