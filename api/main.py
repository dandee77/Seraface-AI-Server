from fastapi import FastAPI
from phase1 import router as phase1_router

app = FastAPI()

app.include_router(phase1_router, prefix="/phase1", tags=["Phase 1"])   

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)