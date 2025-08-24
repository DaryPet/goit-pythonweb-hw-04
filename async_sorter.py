import asyncio
import aiofiles
from pathlib import Path
import logging

logger = logging.getLogger("async_file_sorter")

CHUNK_SIZE = 1024 * 1024
DEFAULT_CONCURRENCY = 64


def _normalize_ext(path: Path) -> str:
    ext = path.suffix.lstrip(".").lower()
    return ext or "no_extension"


async def _unique_destination(dst_dir: Path, filename: str) -> Path:
    base = Path(filename).stem
    suffix = Path(filename).suffix
    candidate = dst_dir / filename
    if not await asyncio.to_thread(candidate.exists):
        return candidate

    i = 1
    while True:
        cand = dst_dir / f"{base} ({i}) {suffix}"
        if not await asyncio.to_thread(cand.exists):
            return cand
        i += 1


async def copy_file(
    file_path: Path, output_path: Path, sem: asyncio.Semaphore | None = None
) -> None:
    """Asynchronously copies a file to the corresponding subdirectory based on its extension."""
    sem = sem or asyncio.Semaphore(1)
    async with sem:

        try:
            extension = _normalize_ext(file_path)
            target_dir = output_path / extension
            await asyncio.to_thread(target_dir.mkdir, parents=True, exist_ok=True)
            dst_path = await _unique_destination(target_dir, file_path.name)
            async with aiofiles.open(file_path, "rb") as src, aiofiles.open(
                dst_path, "wb"
            ) as dst:
                while True:
                    chunk = await src.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    await dst.write(chunk)
            logger.info("Copied %s -> %s", file_path, dst_path)
        except Exception:
            logger.exception("Error copying %s", file_path)


async def read_folder(
    source_path: Path,
    output_path: Path,
    sem: asyncio.Semaphore | None = None,
) -> None:
    """Recursively reads a folder and creates tasks for copying files."""
    sem = sem or asyncio.Semaphore(DEFAULT_CONCURRENCY)
    if not await asyncio.to_thread(source_path.exists):
        logger.error("Source folder not found: %s", source_path)
        return

    try:
        source_resolved = source_path.resolve()
        output_resolved = output_path.resolve()
    except Exception:
        logger.exception("Failed to resolve paths.")
        return

    tasks: list[asyncio.Future] = []
    try:
        entries = await asyncio.to_thread(lambda: list(source_resolved.iterdir()))
        for entry in entries:
            try:
                entry_resolved = entry.resolve()
                if (
                    entry_resolved == output_resolved
                    or output_resolved in entry_resolved.parents
                ):
                    continue
                if entry.is_dir():
                    tasks.append(read_folder(entry_resolved, output_resolved, sem))
                elif entry.is_file():
                    tasks.append(copy_file(entry_resolved, output_resolved, sem))
                else:
                    logger.info("Skipping non-regular entry: %s", entry_resolved)
            except Exception:
                logger.exception("Error handling entry %s", entry)
        if tasks:
            await asyncio.gather(*tasks)

    except Exception as e:
        logger.error(f"Error while reading folder {source_path}: {e}")
