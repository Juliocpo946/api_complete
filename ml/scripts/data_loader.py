import pandas as pd
from database_connection import execute_query

def load_features():
    query = open('../data/02_extract_features.sql', 'r').read()
    data = execute_query(query)
    return pd.DataFrame(data)

def load_table(schema, table):
    query = f"SELECT * FROM {schema}.{table}"
    data = execute_query(query)
    return pd.DataFrame(data)