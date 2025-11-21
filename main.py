from fastapi import FastAPI
from routers.user_router import router as user_router  # agregado por CRUDfull

app = FastAPI()
app.include_router(user_router)  # agregado por CRUDfull

@app.get("/")
def root():
    return {"message": "🚀 CRUDfull FastAPI ready!"}
