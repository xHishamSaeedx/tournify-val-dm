from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import matches

# Create FastAPI app instance
app = FastAPI(
    title="Riot Dummy Server",
    description="A dummy server that provides fake match data for testing purposes",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(matches.router)


@app.get("/")
async def root():
    """Root endpoint with basic information."""
    return {
        "message": "Riot Dummy Server is running",
        "version": "1.0.0",
        "endpoints": {
            "POST /matches/": "Get dummy match data with player stats"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
