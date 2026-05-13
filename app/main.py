from fastapi import FastAPI
import uvicorn

from app.core.config import settings

app = FastAPI(title=settings.APP_TITLE)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)