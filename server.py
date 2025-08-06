from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import requests
import os
import shutil

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

UPLOAD_DIRECTORY = "./static/uploads"
current_url = None

class Message(BaseModel):
    message: str

class Url(BaseModel):
    url: str

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api")
async def api(message: Message):
    try:
        response = requests.post(f"{latest()['url']}/chat", json={'message': message.message})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)
        file_path = os.path.join(UPLOAD_DIRECTORY, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"file_path": f"/static/uploads/{file.filename}"}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/update")
def update(url: Url):
    global current_url
    current_url = url.url
    return {"status": "updated", "new_url": current_url}

@app.get("/go")
def go():
    if current_url:
        return RedirectResponse(url=current_url)
    else:
        return JSONResponse(content={"error": "No URL set yet"}, status_code=404)

@app.get("/latest")
def latest():
    if current_url:
        return {"url": current_url}
    else:
        return JSONResponse(content={"error": "No URL set yet"}, status_code=404)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)