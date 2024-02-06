from fastapi import FastAPI

from src.api.router import router as api_router
from src.cache.events_router import router as cache_events_router
from src.middlewares import LoggingMiddleware

app = FastAPI(
    title="Library Management System",
    version="1.0",
)

app.add_middleware(LoggingMiddleware)

# startup, shutdown events
app.include_router(cache_events_router)
# routes
app.include_router(api_router)
