from router import router
from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import create_table
import uvicorn

@asynccontextmanager
async def lifespan(api: FastAPI):
    await create_table()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)