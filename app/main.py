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

from app.rmq.rmq_rpc import RpcClient, get_amqp_url
import os

import os

@app.on_event("startup")
async def startup_event():
    create_db_and_tables()

    # включаем RMQ только если USE_RMQ=1
    if os.getenv("USE_RMQ", "0") == "1":
        app.state.rpc = RpcClient(get_amqp_url())
        await app.state.rpc.connect()
    else:
        app.state.rpc = None


@app.on_event("shutdown")
async def shutdown_event():
    rpc = getattr(app.state, "rpc", None)
    if rpc:
        await rpc.close()
