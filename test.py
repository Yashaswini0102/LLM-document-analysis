import psycopg2
from psycopg2 import sql
from tabulate import tabulate

# PostgreSQL database configuration
DB_CONFIG = {
    'dbname': 'metadata_db',
    'user': 'yashaswini',
    'password': 'Yashu@2003',
    'host': 'localhost',
    'port': '5432'
}

# Function to check if a table exists in the database
def check_table_exists(table_name):
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # Query to check if table exists
        cursor.execute(
            """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = %s
            );
            """, (table_name,)
        )
        exists = cursor.fetchone()[0]

        if exists:
            print(f"Table '{table_name}' exists.")
        else:
            print(f"Table '{table_name}' does NOT exist.")

        cursor.close()
        connection.close()

    except Exception as e:
        print(f"Error checking table: {e}")

# Function to fetch and display all rows from the table in a tabular format
def fetch_table_data(table_name):
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # Fetch column names
        cursor.execute(
            sql.SQL("SELECT column_name FROM information_schema.columns WHERE table_name = %s"), 
            (table_name,)
        )
        column_names = [row[0] for row in cursor.fetchall()]

        # Fetch all data from the specified table
        cursor.execute(sql.SQL("SELECT * FROM {}").format(sql.Identifier(table_name)))
        rows = cursor.fetchall()

        if rows:
            print(f"Data from '{table_name}' table:")
            # Display data in a tabular format
            print(tabulate(rows, headers=column_names, tablefmt='psql'))
        else:
            print(f"No data found in the '{table_name}' table.")

        cursor.close()
        connection.close()

    except Exception as e:
        print(f"Error fetching data: {e}")

# Example usage
table_name = 'document_metadata'  # Replace with your actual table name

# Check if the table exists
check_table_exists(table_name)

# Fetch and display data from the table in a tabular format
fetch_table_data(table_name)