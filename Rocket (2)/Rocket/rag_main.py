import psycopg2
import os
import openai
from openai import OpenAI
from sentence_transformers import SentenceTransformer
import numpy as np
from signal123 import SQL




model = SentenceTransformer("all-MiniLM-L6-v2")

def get_embedding(text: str):
    emb = model.encode(text, normalize_embeddings = True)
    return emb.tolist()


database_url = os.environ['DATABASE_URL']

conn = psycopg2.connect(database_url)
cur = conn.cursor()


def vectordb():
    # Get the raw data from database
    event = SQL()

    # Convert to a readable string for the AI agent
    if event:
        user_input = f""" mechanism: {event[6]}
        """
    else:
        user_input = "No recent data available"
    
    event_mining_policy = get_embedding(user_input)

    cur.execute("""SELECT mechanism, Ticker, confidence FROM china_mining_policy_scenarios ORDER BY embedding <-> %s LIMIT 8""", (str(event_mining_policy),))


    
    results = cur.fetchall()
    cur.close()
    conn.close()

    for row in results:
        print(row)
        print(user_input)
    

    return results

if __name__ == "__main__":
    vectordb()

    