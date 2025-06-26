from fastapi import FastAPI
from backend.routes import gestures, training

app = FastAPI(title="Sign Glove API")

app.include_router(gestures.router, prefix="/gestures", tags=["Gestures"])
app.include_router(training.router, prefix="/training", tags=["Training"])

@app.get("/")
def root():
    return {"message": "Backend is running 🚀"}
