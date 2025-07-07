from fastapi import FastAPI
from phase1 import router as phase1_router
from phase2 import router as phase2_router
from phase3 import router as phase3_router
from phase4 import router as phase4_router

app = FastAPI()

app.include_router(phase1_router, prefix="/phase1", tags=["Phase 1"])   
app.include_router(phase2_router, prefix="/phase2", tags=["Phase 2"])
app.include_router(phase3_router, prefix="/phase3", tags=["Phase 3"])
app.include_router(phase4_router, prefix="/phase4", tags=["Phase 4"])

# TODO: AFTER A WHILE (WHEN WE HAVE ENOUGH DATA) WE WILL BUILD AN ALGORITHM TO RECOMMEND PRODUCTS MANUALLY INSTEAD OF USING AI
# TODO: WE WOULD ALSO CLASSIFY PRODUCTS INTO CATEGORIES LIKE "BEST FOR OILY SKIN", "BEST FOR DRY SKIN", ETC.
# TODO: CLASSIFY PRODUCTS INTO CATEGORIES LIKE CHEAP, MID-RANGE, EXPENSIVE
# IMPROVEMENT: WE WOULD THEN HAVE REPEATING FUNCTION: PRODUCT NAME DB -> PRODUCT DB (FROM SERPAPI), WHERE IN WE COULD JUST DIRECTLY SEARCH FOR PRODUCTS

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)