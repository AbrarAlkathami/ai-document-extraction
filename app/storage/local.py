from __future__ import annotations

import re
from pathlib import Path
from uuid import UUID
import anyio
from fastapi import UploadFile


_SAFE = re.compile(r"[^A-Za-z0-9.\-_]+")

def safe_filename(name: str) -> str:
    name = name.strip().replace(" ", "_")
    name = _SAFE.sub("", name)
    return name or "file"

async def save_uploadfile_locally(
    file: UploadFile,
    dest_dir: Path,
    doc_id: UUID,
    chunk_size: int = 1024 * 1024,  # 1MB
) -> tuple[str, int]:
    """
    Saves UploadFile to dest_dir using a unique name.
    Returns: (path_str, size_bytes)
    """
    dest_dir.mkdir(parents=True, exist_ok=True)

    original = safe_filename(file.filename or "file")
    dest_path = dest_dir / f"{doc_id}_{original}"

    def _write_sync() -> int:
        size = 0
        file.file.seek(0)
        with open(dest_path, "wb") as out:
            while True:
                chunk = file.file.read(chunk_size)
                if not chunk:
                    break
                out.write(chunk)
                size += len(chunk)
        return size

    size_bytes = await anyio.to_thread.run_sync(_write_sync)
    return str(dest_path), size_bytes