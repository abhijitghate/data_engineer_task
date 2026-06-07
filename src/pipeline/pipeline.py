
from src.pipeline.validator import validate_data
from src.pipeline.transformer import transform_to_db_ready
from src.pipeline.loader import load_db_ready_data
from src.database.database import SessionLocal
from src.pipeline.parser import parse_excel_master


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


if __name__ == "__main__":
    run_ingestion_pipeline("data/corporates_A_1.xlsm", "v1")