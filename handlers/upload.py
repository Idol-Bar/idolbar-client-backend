import shutil
from typing import List
from fastapi import FastAPI, File, UploadFile, APIRouter
import os
import uuid
import aiofiles
import aiofiles.os as aios
from os import getcwd
from fastapi.responses import FileResponse
from pdf2image import convert_from_path
from thumbnail import generate_thumbnail
upload_router = APIRouter()
read_router = APIRouter()

@upload_router.post("/uploads")
async def upload_file(uploaded_file: UploadFile = File(...)):
    filename, file_extension = os.path.splitext(uploaded_file.filename)
    uuid_file = uuid.uuid1()
    file_location = f"uploads/{uuid_file}{file_extension}"
    thumbnail_location = f"uploads/{uuid_file}_thumbnail.jpg"

    async with aiofiles.open(file_location, "wb") as out_file:
        content = await uploaded_file.read()  # async read
        await out_file.write(content)  # async write
    response_str = dict(status="success",thumbnail=thumbnail_location,file_name=file_location,original_name=uploaded_file.filename,web_url=file_location,type=file_extension )
    if file_extension == ".pdf":
        convert_from_path(file_location,output_folder=os.getcwd()+"/uploads",output_file=f"{uuid_file}_thumbnail",single_file=True,fmt='jpeg')
    elif file_extension == ".mp4":
        options = {'trim': False,'height': 300,'width': 300,'quality': 85,'type': 'thumbnail'}
        generate_thumbnail(file_location, thumbnail_location, options)
    return response_str

@read_router.get("/uploads/{name_file}")
def download_file(name_file: str):
    try:
        return FileResponse(path=getcwd() + "/uploads/" + name_file, media_type='application/octet-stream', filename=name_file)
    except:
        return "https://alodawpyei.com/images/main/logo280-280.png"
