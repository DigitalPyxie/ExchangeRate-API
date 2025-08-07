from fastapi import FastAPI, HTTPException
import sqlite3
from pydantic import BaseModel #validates the data users send to the API
from datetime import date

app = FastAPI()

class ExchangeRate(BaseModel):
    currency_pair: str
    rate: float
    date_recorded: date

def init_db():
    conn = sqlite3.connect("database,db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS exchange_rates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        currency_pair TEXT,
        rate REAL,
        date_recorded TEXT)
        """)
    conn.commit()
    conn.close()

init_db() #gets called at startup

#Get all the exchange rates
@app.get("/rates")
def get_rates():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM exchange_rates")
    rates = cursor.fetchall()
    conn.close()
    return rates

#Get the latest rate for a specific currency pair
@app.get("/rate/{currency_pair}")
def get_latest_rate(currency_pair: str):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""SELECT rate, date_recorded FROM exchange_rates
        WHERE currency_pair = ?
        ORDER BY date_recorded DESC LIMIT 1""", (currency_pair,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return {"currency_pair": currency_pair, "rate": result[0], "date_recorded": result[1]}
    else:
        raise HTTPException(status_code=404, detail="Requested currency pair not found")

#Add a new rate
@app.post("/rate")
def add_rate(rate: ExchangeRate):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO exchange_rates (currency_pair, rate, date_recorded)
        VALUES (?, ?, ?)
    """, (rate.currency_pair, rate.rate, rate.date_recorded.isoformat()))
    conn.commit()
    conn.close()
    return {"message": "Rate added"}

#Update an existing rate with ID
@app.put("/rate/{rate_id}")
def update_rate(rate_id: int, rate:ExchangeRate):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM exchange_rates WHERE id = ?", (rate_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Rate ID not found")

    cursor.execute("""
         UPDATE exchange_rates
          SET currency_pair = ?, rate = ?, date_recorded = ?
          WHERE id = ?""", (rate.currency_pair, rate.rate, rate.date_recorded.isoformat(), rate_id))
    conn.commit()
    conn.close()
    return {"message": "Rate updated"}

#Delete an exchange rate by ID
@app.delete("/rate/{rate_id}")
def delete_rate(rate_id: int):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM exchange_rates WHERE id = ?", (rate_id,))
    conn.commit()
    conn.close()

    return {"message": "Rate deleted"}
