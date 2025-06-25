from fastapi import FastAPI
from routes.gestures import router as gestures_router

app = FastAPI()
app.include_router(gestures_router)
