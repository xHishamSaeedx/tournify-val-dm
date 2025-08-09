from fastapi import FastAPI
from datetime import datetime
from app.routers import matches

app = FastAPI(
    title="Tournify Valorant DM API",
    description="API for managing Valorant deathmatch tournaments",
    version="1.0.0"
)

# Include routers
app.include_router(matches.router)

@app.get("/")
async def root():
    return {"message": "Tournify Valorant DM API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
