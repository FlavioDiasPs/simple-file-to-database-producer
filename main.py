from typing import List
import time
import duckdb
import glob
import os
import pandas as pd
from sqlalchemy import create_engine, text

path_csv = "data/csv/crypto"


def create_duckdb_connection():
    conn = duckdb.connect(database=":memory:", read_only=False)
    return conn


def create_postgres_engine():
    engine = create_engine("postgresql://postgres:postgres@host.docker.internal:5432/postgres")
    return engine


def discover_csv_files(folder_path: str) -> List[str]:
    csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
    return csv_files


def convert_schema_to_postgres(schema: duckdb.DuckDBPyRelation) -> str:
    columns = []
    for col_name, col_type in zip(schema.columns, schema.types):
        if col_type == "BOOLEAN":
            pg_type = "BOOLEAN"
        elif col_type == "INTEGER":
            pg_type = "INTEGER"
        elif col_type == "VARCHAR":
            pg_type = "TEXT"
        elif col_type == "DOUBLE":
            pg_type = "DOUBLE PRECISION"
        else:
            pg_type = "TEXT"  # Default to TEXT for simplicity
        columns.append(f"{col_name} {pg_type}")
    return ", ".join(columns)


def build_table_schema(path, table_name):
    relation = duckdb.from_csv_auto(path_or_buffer=path)
    schema = relation.describe()
    postgres_schema = convert_schema_to_postgres(schema)
    return f"CREATE TABLE IF NOT EXISTS crypto.{table_name} ({postgres_schema});"


def setup_postgres_and_workload(csv_files: List[str]):
    engine = create_postgres_engine()
    workload = []

    with engine.connect() as conn:
        for path in csv_files:
            # Create table in postgres
            table_name = os.path.splitext(os.path.basename(path))[0]
            create_table_query = build_table_schema(path, table_name)
            conn.execute(text('create schema if not exists "crypto";'))
            conn.execute(text(create_table_query))

            # Create workload
            df = pd.read_csv(path).sort_values(by="event_timestamp", ascending=True)
            count = len(df)
            workload.append(
                {
                    "table_name": table_name,
                    "df": df,
                    "count": count,
                    "current_row": 0,
                }
            )
    return workload


def stream_all_data_workloads(workloads: List[dict]):
    engine = create_postgres_engine()
    speed = 1

    while any(workload["current_row"] < workload["count"] for workload in workloads):
        for workload in workloads:
            if workload["current_row"] < workload["count"]:
                current_row = workload["current_row"]
                selected_rows = workload["df"][current_row : current_row + speed]
                workload["current_row"] += speed

                table_name = workload["table_name"]
                print(f"Inserting on {table_name}")
                selected_rows.to_sql(table_name, engine, if_exists="append", index=False, method="multi")

        time.sleep(1)


def main():
    print("Starting!")
    print("Discovering the files")
    csv_files = discover_csv_files(path_csv)
    print(f"Found {len(csv_files)} files")

    print("Setting up postgres tables")
    workloads = setup_postgres_and_workload(csv_files)

    print("Streaming data to postgres")
    stream_all_data_workloads(workloads)

    print("Finished")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)


# select count(1) from deposit_sample_data

# select * from deposit_sample_data order by event_timestamp desc limit 1000;
# select * from event_sample_data order by event_timestamp desc limit 1000;
# select * from user_level_sample_data order by event_timestamp desc limit 1000;
# select * from withdrawals_sample_data order by event_timestamp desc limit 1000;
