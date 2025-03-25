from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse
import uvicorn
import os
from loguru import logger
from logger import file_logger

file_logger()

app = FastAPI()

# Разрешаем доступ с клиента (например, для разработки локально)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://conspectius.ru", "http://www.conspectius.ru"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
    allow_credentials=True,
)

# Путь для статики
app.mount("/static", StaticFiles(directory="static"), name="static")


# Маршрут для отображения HTML-страницы
@app.get("/", response_class=HTMLResponse)
async def get_home():
    """
    Маршрут для отображения HTML-страницы. Отображает страницу static/index.html.
    """
    try:
        logger.info("Запрос главной страницы")
        with open("static/index.html", "r", encoding="utf-8") as file:
            html_content = file.read()
        logger.success("HTML-страница успешно загружена")
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Ошибка загрузки HTML: {str(e)}")
        raise HTTPException(status_code=500, detail="Ошибка загрузки страницы")


@app.post("/upload/")
async def upload_audio(file: UploadFile = File(...)):
    """
    Обработчик POST-запросов на /upload/. Проверяет тип файла, очищает папку uploads
    и сохраняет файл, если он является аудиофайлом. Возвращает JSON-ответ со
    статусом success, если файл успешно загружен, иначе - error.

    :param file: файл, загруженный с клиента
    :return: JSON-ответ с информацией о результате
    """
    logger.info(f"Начало обработки файла: {file.filename}")
    try:
        try:
            # Очищаем папку и сохраняем новый файл
            os.remove(f"/SITE_CONSPECTIUS/shared_audio/{file.filename}")
            logger.debug(f"Удален старый файл: {file.filename}")
        except FileNotFoundError:
            logger.warning(f"Файл для замены не найден: {file.filename}")

        file_path = f"/SITE_CONSPECTIUS/shared_audio/{file.filename}"
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
            logger.success(f"Файл {file.filename} успешно сохранен ({len(content)} байт)")

        return {"status": "success"}
    except HTTPException as e:
        logger.error(f"HTTP ошибка: {str(e)}")
        raise e
    except Exception as e:
        logger.critical(f"Критическая ошибка обработки файла: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "message": "Произошла ошибка при обработке файла",
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
    logger.error(f"Некорректный запрос: {str(exc)}")
    return JSONResponse(
        status_code=422,
        content={"status": "error", "message": "Некорректный запрос"},
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
