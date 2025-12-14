from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.db import create_db_and_tables
from app.api import predict_router, customers_router

app = FastAPI(title="Marketing Response API")


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


app.include_router(predict_router, prefix="/api")
app.include_router(customers_router, prefix="/api")

templates = Jinja2Templates(directory="frontend/templates")
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
