import base64
import io
from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from minio import Minio
from typing import List
from fastapi import Query

Base = declarative_base()

app = FastAPI()

client = Minio(
    "localhost:9000",  # Используйте именно 'localhost', так как Docker контейнер будет обращаться к самому себе
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)
if not client.bucket_exists("images"):
    client.make_bucket("images")

class Meme(Base):
    __tablename__ = 'memes'

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    image_url = Column(String)

class MemeBase(BaseModel):
    text: str
    image_url: str

class MemeCreate(BaseModel):
    text: str
    image_url: str

class MemeUpdate(BaseModel):
    text: str = Query(..., min_length=1)

class MemeResponse(BaseModel):
    id: int
    text: str
    image_url: str

engine = create_engine("sqlite:///memes.db")
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Добавление эндпоинтов для работы с мемами
@app.post("/memes", response_model=MemeResponse)
def create_meme(meme: MemeCreate):
    db = SessionLocal()
    new_meme = Meme(text=meme.text, image_url=meme.image_url)
    db.add(new_meme)
    db.commit()
    db.refresh(new_meme)
    return new_meme

@app.get("/memes/{id}", response_model=MemeResponse)
def get_meme(id: int):
    db = SessionLocal()
    meme = db.query(Meme).filter(Meme.id == id).first()
    if meme is None:
        raise HTTPException(status_code=404, detail="Meme not found")
    return meme

@app.put("/memes/{id}", response_model=MemeResponse)
def update_meme(id: int, meme: MemeUpdate):
    db = SessionLocal()
    db.query(Meme).filter(Meme.id == id).update({"text": meme.text})
    db.commit()
    updated_meme = db.query(Meme).filter(Meme.id == id).first()
    return updated_meme

@app.delete("/memes/{id}", status_code=204)
def delete_meme(id: int):
    db = SessionLocal()
    db.query(Meme).filter(Meme.id == id).delete()
    db.commit()

@app.get("/memes", response_model=List[MemeResponse])
def get_memes(skip: int = 0, limit: int = 10):
    db = SessionLocal()
    memes = db.query(Meme).offset(skip).limit(limit).all()
    return memes

# Добавление эндпоинтов для работы с изображениями
@app.post("/images/upload")
async def create_image(file: UploadFile = File(...)):
    if not client.bucket_exists("images"):
        client.make_bucket("images")

    filename = file.filename
    content = await file.read()
    client.put_object("images", filename, io.BytesIO(content), len(content))
    return {"filename": filename}

@app.get("/images/{image_id}")
async def get_image(image_id: str):
    try:
        object_data = client.get_object("images", image_id)
        content = object_data.read()
        image_data = base64.b64encode(content).decode("utf-8")
        return JSONResponse(content={"image_data": image_data})
    except Exception as e:
        raise HTTPException(status_code=404, detail="Image not found")

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Meme API",
        version="1.0.0",
        description="This is a meme API using FastAPI with image upload and retrieval capabilities",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    uvicorn.run(app, host="127.0.0.1", port=8001)