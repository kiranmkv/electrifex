from fastapi import FastAPI
import os
import asyncpg
from prometheus_fastapi_instrumentator import Instrumentator
import uvicorn
app = FastAPI()
pool = None
@app.on_event("startup")
async def startup():
    global pool
    try:
        pool = await asyncpg.create_pool(
            host=os.getenv("PG_HOST", "postgres"),       # PostgreSQL service name in the cluster
            user=os.getenv("PG_USER", "your_user"),
            password=os.getenv("PG_PASSWORD", "your_password"),
            database=os.getenv("PG_DATABASE", "your_database"),
            port=int(os.getenv("PG_PORT", 5432)),
            min_size=1,
            max_size=10
        )
        # Test the connection
        async with pool.acquire() as conn:
            result = await conn.fetch("SELECT NOW()")
            print("Connected to PostgreSQL at:", result[0]['now'])
    except Exception as e:
        print("Error connecting to PostgreSQL:", e)
@app.on_event("shutdown")
async def shutdown():
    global pool
    if pool:
        await pool.close()
@app.get("/healthz")
async def healthz():
    return {"status": "OK"}
    
Instrumentator().instrument(app).expose(app)
if __name__ == "__main__":
    # Run the application on host 0.0.0.0 and port 8000
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
