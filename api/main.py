from fastapi import FastAPI
from phase1 import router as phase1_router
from phase2 import router as phase2_router
from phase3 import router as phase3_router

app = FastAPI()

app.include_router(phase1_router, prefix="/phase1", tags=["Phase 1"])   
app.include_router(phase2_router, prefix="/phase2", tags=["Phase 2"])
app.include_router(phase3_router, prefix="/phase3", tags=["Phase 3"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)