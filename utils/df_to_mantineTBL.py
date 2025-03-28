import pandas as pd
from dash import html

def genTBLContent(df: pd.DataFrame) -> dict:
    return {"head": list(df.columns), "body": df.values.tolist()}