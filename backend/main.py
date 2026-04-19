from router import router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import create_table
from repository import MessageRepository
from config import CORS, PORT
import uvicorn

@asynccontextmanager
async def lifespan(api: FastAPI):
    await create_table()
    await MessageRepository.add_first_message()
    yield

app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware,
                   allow_origins=CORS,
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"])
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, port=PORT)