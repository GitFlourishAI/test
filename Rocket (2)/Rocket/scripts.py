import os
import psycopg2

def get_db():

    conn = None
    cur = None

    try:

        database_url = os.environ['DATABASE_URL']
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()

        cur.execute("SELECT * FROM scenario")
        rows = cur.fetchall()

        return rows

    finally:
        if cur:
            cur.close()

        if conn:
            conn.close()