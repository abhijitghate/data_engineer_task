import argparse
from src.pipeline.validator import validate_data
from src.pipeline.transformer import transform_to_db_ready
from src.pipeline.loader import load_db_ready_data
from src.database.database import SessionLocal
from src.pipeline.parser import parse_excel_master

DEFAULT_INPUT_FILES = [
    "data/corporates_A_1.xlsm",
    "data/corporates_A_2.xlsm",
    "data/corporates_B_1.xlsm",
    "data/corporates_B_2.xlsm",
]


def run_ingestion_pipeline(file_path: str, version: str):
    db = SessionLocal()

    try:
        parsed_data = parse_excel_master(file_path)
        validated_data = validate_data(parsed_data, version, file_path)
        db_ready_data = transform_to_db_ready(validated_data)
        load_result = load_db_ready_data(db, db_ready_data)
        return load_result

    except Exception as e:
        raise e
    finally:
        db.close()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run ingestion pipeline for one or more input files."
    )
    parser.add_argument(
        "--files",
        nargs="+",
        help="One or more input file paths, e.g. data/corporates_A_1.xlsm. If omitted, defaults are used.",
    )
    parser.add_argument(
        "--version",
        default="v1",
        help="Discussion version applied to all provided files (default: v1).",
    )
    return parser


if __name__ == "__main__":
    args = _build_parser().parse_args()
    files_to_load = args.files or DEFAULT_INPUT_FILES
    for file_path in files_to_load:
        result = run_ingestion_pipeline(file_path=file_path, version=args.version)
        print(f"Loaded {file_path}: {result}")
