import os
import sqlite3
import uuid
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rdflib import Graph

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

dirname = os.path.dirname(__file__)
owl_file_path = os.path.join(dirname, 'ontology/RelAIEO_v6.owl')
g = Graph()
g.parse(owl_file_path)
graph_jsonld = g.serialize(format='json-ld')

con = sqlite3.connect("db.sqlite")
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS shares (sessionId, selectedCardIds)")

@app.get("/test")
async def python_test():
    print(owl_file_path)
    return "Audit4SG app api"

class Share(BaseModel):
    sessionId: str
    selectedCardIds: list
@app.post("/share")
async def save_to_db(data: Share):
    res = cur.execute('''SELECT * FROM shares WHERE sessionId = ?''', (data.sessionId,))
    if len(res.fetchall()) > 0:
        # cur.execute('''UPDATE shares SET selectedCardIds = ? WHERE sessionId = ?''', (str(data.selectedCardIds), data.sessionId,))
        cur.execute('''UPDATE shares SET selectedCardIds = ? WHERE sessionId = ?''', (json.dumps(data.selectedCardIds), data.sessionId,))
        con.commit()
    else:
        # row = [data.sessionId, str(data.selectedCardIds)]
        row = [data.sessionId, json.dumps(data.selectedCardIds)]
        cur.execute('INSERT INTO shares VALUES (?, ?)', row)
        con.commit()
    return {"success": True}

class Read(BaseModel):
    sessionId: str
@app.post("/reading-data")
async def get_reading_data(data: Read):
    res = cur.execute('''SELECT * FROM shares WHERE sessionId = ?''', (data.sessionId,))
    return { "success": True, "payload": graph_jsonld, "readingData": res.fetchall()}

@app.get("/")
async def root():
    session_id = str(uuid.uuid4())
    return { "success": True, "payload": graph_jsonld, "sessionId": session_id}