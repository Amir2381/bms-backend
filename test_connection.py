import psycopg

conn = psycopg.connect(
    host="localhost", port=5432, dbname="bms_db", user="postgres", password=1122
)

print("connected successfully!")
conn.close()
