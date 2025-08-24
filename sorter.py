import sys
import asyncio
import argparse
from pathlib import Path

from async_sorter import read_folder
from logging_setup import setup_logging


def main() -> None:
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

    source_folder: Path = args.source
    output_folder: Path = args.output

    if not source_folder.exists() or not source_folder.is_dir():
        logger.error(
            "Source folder does not exist or is not a directory: %s", source_folder
        )
        sys.exit(1)

    try:
        source_res = source_folder.resolve()
        output_res = output_folder.resolve()
        if output_res == source_res or output_res in source_res.parents:
            logger.error(
                "Output folder must not be the source folder nor placed inside it.\n"
                "source=%s\noutput=%s",
                source_res,
                output_res,
            )
            sys.exit(2)
    except Exception as e:
        logger.exception(f"An unhandled error occurred: {e}")
        sys.exit(1)

    try:
        asyncio.run(read_folder(source_res, output_res))
    except KeyboardInterrupt:
        logger.warning("Interrupted by user.")
        sys.exit(130)
    except Exception:
        logger.critical("An unhandled error occurred.", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
