from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse
import uvicorn
import os

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
    """
    Маршрут для отображения HTML-страницы. Отображает страницу static/index.html.
    """
    with open("static/index.html", "r", encoding="utf-8") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)


@app.post("/upload/")
async def upload_audio(file: UploadFile = File(...)):
    """
    Обработчик POST-запросов на /upload/. Проверяет тип файла, очищает папку uploads
    и сохраняет файл, если он является аудиофайлом. Возвращает JSON-ответ со
    статусом success, если файл успешно загружен, иначе - error.

    :param file: файл, загруженный с клиента
    :return: JSON-ответ с информацией о результате
    """
    try:
        try:
            # Очищаем папку и сохраняем новый файл
            os.remove(f"/SITE_CONSPECTIUS/shared_audio/{file.filename}")
        except FileNotFoundError:
            print("Старый файл не найден")

        file_path = f"/SITE_CONSPECTIUS/shared_audio/{file.filename}"
        with open(file_path, "wb") as f:
            f.write(await file.read())

        return {"status": "success"}
    except HTTPException as e:
        raise e
    except Exception as e:
        return {
            "status": "error",
            "message": "Произошла ошибка при обработке файла.",
            "details": str(e),
        }


# Обработчик ошибок валидации
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):   
    """
    Обработчик ошибок валидации. Возвращает JSON-ответ со статусом 422 и информацией
    об ошибке.

    :param request: запрос, в котором произошла ошибка
    :param exc: экземпляр RequestValidationError
    :return: JSONResponse
    """
    return JSONResponse(
        status_code=422,
        content={"status": "error", "message": "Некорректный запрос.", "details": str(exc)},
    )


if __name__ == "__main__":
    uvicorn.run("main:app")
