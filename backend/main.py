from router import router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import create_table
import uvicorn

@asynccontextmanager
async def lifespan(api: FastAPI):
    await create_table()
    yield

app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware,
                   allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"])
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, port=8001)