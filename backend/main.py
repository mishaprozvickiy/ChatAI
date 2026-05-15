from router import router
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import create_tables
from repositories.message import MessageRepository
from config import CORS, PORT, MISSING_TOKEN_EXCEPTION
from authx.exceptions import AuthXException
import uvicorn

@asynccontextmanager
async def lifespan(api: FastAPI):
    await create_tables()
    # await MessageRepository.add_first_message()
    yield

app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware,
                   allow_origins=CORS,
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"])
app.include_router(router)

@app.exception_handler(AuthXException)
async def authx_exception_handler(request: Request, exception: AuthXException):
    raise MISSING_TOKEN_EXCEPTION

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, port=PORT)