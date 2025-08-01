import sqlite3
from datetime import datetime
from db import parking

from langchain.prompts import PromptTemplate
from langchain_ollama import OllamaLLM
from langchain_core.runnables import RunnableSequence

llm = OllamaLLM(model="gemma3")  # e.g., "llama3", "mistral"
prompt = PromptTemplate.from_template(
    """
You are an expert SQL Generator.

Below is the schema of the table `parking`:

Table: parking  
Columns:
- parking_id (STRING, PRIMARY KEY)
- username (STRING, FOREIGN KEY -> users.username, NOT NULL)
- location_link (STRING, NOT NULL)
- price_per_hour (FLOAT, NOT NULL)
- available_from (DATETIME, NOT NULL)
- available_till (DATETIME, NOT NULL)
- image_url (STRING, NOT NULL)

Given the user request below, write a valid raw SQL query for the schema above.

User request: "{user_input}"
Return ONLY the SQL as plain text.
"""
)

chain: RunnableSequence = prompt | llm
DB_PATH = "./instance/take-my-park.sqlite3"


def get_filtered_parkings(user_inp: str) -> list[parking.Parking]:
    query: str = chain.invoke({"user_input": user_inp})
    query = query.replace("`", "")
    query = query.replace("sql", "")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(query)
        rows = cursor.fetchall()

        filtered_parkings = []
        for row in rows:
            p = parking.Parking(
                parking_id=row[0],
                username=row[1],
                location_link=row[2],
                price_per_hour=float(row[3]),
                available_from=datetime.strptime(row[4], "%Y-%m-%d %H:%M:%S.%f"),
                available_till=datetime.strptime(row[5], "%Y-%m-%d %H:%M:%S.%f"),
                image_url=row[6],
            )
            filtered_parkings.append(p)
    except Exception as err:
        print(f"Exception in Query: {query}\nError: {err}")
        return []
    finally:
        conn.close()
    return filtered_parkings


if __name__ == "__main__":
    msg = "Find a parking spot near b'twin 1PM to 2PM on 26 July 2025"
    res = get_filtered_parkings(msg)
    print(f"Res: \n{res}")
