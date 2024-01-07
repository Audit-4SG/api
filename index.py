### Module Imports
import os
import sqlite3
import uuid
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rdflib import Graph

### FastAPI Setup
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

### Read ontology and convert to JSONLD
dirname = os.path.dirname(__file__)
owl_file_path = os.path.join(dirname, 'ontology/RelAIEO_v7.owl')
g = Graph()
g.parse(owl_file_path)
graph_jsonld = g.serialize(format='json-ld')

### Connect with SQLITE 
con = sqlite3.connect("db.sqlite")
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS shares (sessionId, selectedCardIds)")

### Fetch Ontology
@app.get("/ontology")
async def get_ontology():
    session_id = str(uuid.uuid4())
    return { "success": True, "ontologyData": graph_jsonld, "sessionId": session_id}

### Save Cards
class Share(BaseModel):
    sessionId: str
    selectedCardIds: list
@app.post("/cards")
async def save_cards(data: Share):
    res = cur.execute('''SELECT * FROM shares WHERE sessionId = ?''', (data.sessionId,))
    if len(res.fetchall()) > 0:
        cur.execute('''UPDATE shares SET selectedCardIds = ? WHERE sessionId = ?''', (json.dumps(data.selectedCardIds), data.sessionId,))
        con.commit()
    else:
        row = [data.sessionId, json.dumps(data.selectedCardIds)]
        cur.execute('INSERT INTO shares VALUES (?, ?)', row)
        con.commit()
    return {"success": True}

### Fetch Cards
class Read(BaseModel):
    sessionId: str
@app.get("/cards")
async def get_cards(data: Read):
    res = cur.execute('''SELECT * FROM shares WHERE sessionId = ?''', (data.sessionId,))
    return { "success": True, "payload": graph_jsonld, "readingData": res.fetchall()}