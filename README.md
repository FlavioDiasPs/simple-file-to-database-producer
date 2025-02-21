# Simple File to Database Producer
--Readme: AI Generated --
This project reads CSV files from a specified directory, creates corresponding tables in a PostgreSQL database, and streams the data into these tables.

## Project Structure

```
/c:/Code/simple-file-to-database-producer
│
├── data
│   └── csv
│       └── crypto
│           ├── file1.csv
│           ├── file2.csv
│           └── ...
├── main.py
└── README.md
```

## Setup

### Prerequisites

- Python 3.8+
- PostgreSQL
- Docker (for running PostgreSQL)

### Install Dependencies

```sh
pip install -r requirements.txt
```

### Running PostgreSQL with Docker

```sh
docker run --name postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres
```

## Configuration

Ensure the CSV files are placed in the `data/csv/crypto` directory.

## Running the Script

```sh
python main.py
```

## How It Works

1. **Discover CSV Files**: The script scans the `data/csv/crypto` directory for CSV files.
2. **Setup PostgreSQL Tables**: For each CSV file, a corresponding table is created in the PostgreSQL database.
3. **Stream Data**: The data from the CSV files is streamed into the PostgreSQL tables.

## Example Queries

```sql
-- Count rows in a table
SELECT COUNT(1) FROM deposit_sample_data;

-- Fetch latest 1000 rows from a table
SELECT * FROM deposit_sample_data ORDER BY event_timestamp DESC LIMIT 1000;
```

## Error Handling

If an error occurs during execution, it will be printed to the console.

## License

This project is licensed under the MIT License.