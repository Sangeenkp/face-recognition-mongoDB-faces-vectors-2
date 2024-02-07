from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import os

from fastapi.middleware.cors import CORSMiddleware

from add_identity import add_identity
from verify_identity import verify_identity

class Item(BaseModel):
    name: str
    image: str

class Image(BaseModel):
    checkImage: list

app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/items/")
async def root(item: List[Item]):
    response = add_identity(item)
    return str(response)
    
@app.post("/image/")
async def root(image: Image):
    dir = 'tests/predictions'
    response = verify_identity(image.checkImage[0])
    for f in os.listdir(dir):
        os.remove(os.path.join(dir, f))
    return str(response)
