import csv
import psycopg2
from psycopg2 import OperationalError, Error

def connect_db():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="postgres",
            user="postgres",
            password="0984"
        )
        return conn, None
    except OperationalError as e:
        return None, str(e)

def close_db(conn):
    try:
        conn.close()
        print("Database connection closed successfully.")
    except Exception as e:
        print(f"An error occurred while closing the database: {e}")

def upload_to_db(conn, csv_file_path):
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS your_table (
                    Id SERIAL PRIMARY KEY, 
                    TimeCreated TIMESTAMP, 
                    Level INT, 
                    Task TEXT, 
                    Opcode TEXT, 
                    ProcessId INT, 
                    ThreadId INT, 
                    MachineName TEXT, 
                    UserId TEXT, 
                    ActivityId TEXT, 
                    LogName TEXT
                );
                """
            )

            with open(csv_file_path, 'r') as f:
                f.readline()
                reader = csv.DictReader(f)
                print(reader.fieldnames)
                for row in reader:
                    event_id = row['Id']
                    timestamp = row['TimeCreated']
                    level = row['Level']
                    task = row['Task']
                    opcode = row['Opcode']
                    process_id = row['ProcessId']
                    thread_id = row['ThreadId']
                    machine_name = row['MachineName']
                    user_id = row['UserId']
                    activity_id = row['ActivityId']
                    log_name = row['LogName']

                cur.execute(
                    """
                    INSERT INTO your_table (
                        Id, TimeCreated, Level, Task, Opcode, 
                        ProcessId, ThreadId, MachineName, UserId, 
                        ActivityId, LogName
                    ) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
                    ON CONFLICT (Id) DO NOTHING;
                    """,
                    (event_id, timestamp, level, task, opcode, process_id, thread_id, machine_name, user_id, activity_id, log_name)
                )
                
            conn.commit()
        return "Upload successful", None
    except Error as e:
        return None, str(e)
    finally:
        if cur:
            cur.close()

if __name__ == '__main__':
    conn, error = connect_db()
    if conn:
        message, error = upload_to_db(conn, f"C:\\Users\\USER\\Desktop\\구름프로젝트3-1\\sysmon_output.csv")
        if message:
            print(message)
        if error:
            print(f"An error occurred: {error}")
        close_db(conn)
    else:
        print(f"Failed to connect to database: {error}")
