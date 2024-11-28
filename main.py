from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from etc.delete_files import delete_files_in_folder


app = FastAPI()


# Разрешаем доступ с клиента (например, для разработки локально)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Путь для статики
app.mount("/static", StaticFiles(directory="static"), name="static")


# Маршрут для отображения HTML-страницы
@app.get("/", response_class=HTMLResponse)
async def get_home():
    with open("static/index.html", "r", encoding="utf-8") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)


# Маршрут для обработки загружаемых файлов
@app.post("/upload/")
async def upload_audio(file: UploadFile = File(...)):
    try:
        delete_files_in_folder("uploads")
        with open(f"uploads/{file.filename}", "wb") as f:
            f.write(await file.read())
        return {"status": "success", "filename": file.filename}
    except Exception as e:
        return {"status": "error", "message": str(e)}
