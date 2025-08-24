import asyncio
import argparse
from pathlib import Path

from async_sorter import read_folder
from logging_setup import setup_logging


def main():
    """Main point to run script"""

    logger = setup_logging()

    parser = argparse.ArgumentParser(
        description="Async file sorter based on file extension."
    )
    parser.add_argument(
        "-s", "--source", type=Path, required=True, help="Path to the source directory."
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("./dist"),
        help="Path to the output directory.",
    )

    args = parser.parse_args()

    source_folder = args.source
    output_folder = args.output

    if not source_folder.exists():
        logger.error(f"Source folder does not exist: {source_folder}")
        return

    try:
        asyncio.run(read_folder(source_folder, output_folder))
    except Exception as e:
        logger.critical(f"An unhandled error occurred: {e}")


if __name__ == "__main__":
    main()
