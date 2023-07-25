import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
owl_file_path = os.path.join(dirname, 'ontology/RelAiO_v3.owl')
g = Graph()
g.parse(owl_file_path)

graph_jsonld = g.serialize(format='json-ld')

@app.get("/test")
async def python_test():
    print(owl_file_path)
    return "Audit4SG app api"

@app.get("/")
async def root():
    return { "success": True, "payload": graph_jsonld}