import pandas as pd


def parse_xl_file(file_path: str) -> pd.DataFrame:
    """
    Parses an Excel file and returns a DataFrame.
    
    Args:
        file_path (str): The path to the Excel file.
    Returns:
        pd.DataFrame: The parsed data as a DataFrame.
    """
    try:
        df = pd.read_excel(file_path, sheet_name="MASTER")
        return df
    except Exception as e:
        raise Exception(e)




if __name__ == "__main__":
    print("This is the parser module. It should not be run directly.")
    ## UPLOAD
    df = parse_xl_file("data_engineer_task/data/corporates_A_1.xlsm")
    ## EXTRACT
    ## VALIDATE
    ## LOAD
