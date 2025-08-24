import asyncio
import aiofiles
from pathlib import Path
import logging

logger = logging.getLogger("async_file_sorter")


async def copy_file(file_path: Path, output_path: Path):
    """Asynchronously copies a file to the corresponding subdirectory based on its extension."""
    try:
        extension = file_path.suffix[1:]
        if not extension:
            extension = "no_extension"
        target_dir = output_path / extension
        await asyncio.to_thread(target_dir.mkdir, parents=True, exist_ok=True)
        async with aiofiles.open(file_path, "rb") as src_file:
            content = await src_file.read()
            async with aiofiles.open(target_dir / file_path.name, "wb") as dst_file:
                await dst_file.write(content)

        logger.info(f"Successfully copied: {file_path.name} to {target_dir}")

    except Exception as e:
        logger.error(f"Error copying file {file_path}: {e}")


async def read_folder(source_path: Path, output_path: Path):
    """Recursively reads a folder and creates tasks for copying files."""
    if not source_path.exists():
        logger.error(f"Source folder not found: {source_path}")
        return

    tasks = []
    try:
        for entry in source_path.iterdir():
            if entry.is_dir():
                tasks.append(read_folder(entry, output_path))
            else:
                tasks.append(copy_file(entry, output_path))

        await asyncio.gather(*tasks)

    except Exception as e:
        logger.error(f"Error while reading folder {source_path}: {e}")
