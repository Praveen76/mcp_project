# src/mcp_project/api.py
import asyncio
from fastapi import FastAPI, HTTPException, Header
from mcp_project.agents.key_officers_agent import ping, get_key_officers


from dotenv import load_dotenv
import os
# loads .env from current working directory
# load_dotenv()
# API_KEY_ENV = os.getenv("ANTHROPIC_API_KEY")

app = FastAPI()

# async def _check(key: str | None):
#     import os
#     if os.getenv(API_KEY_ENV) and key != os.getenv(API_KEY_ENV):
#         raise HTTPException(status_code=401, detail="unauthorized")

@app.get("/healthz")
async def healthz():
    return {"ok": True}

@app.get("/ping")
async def ping_route(x_api_key: str | None = Header(default=None)):
    # await _check(x_api_key)
    return {"message": await ping()}

@app.get("/key-officers")
async def key_officers(company: str, top_n: int = 10, x_api_key: str | None = Header(default=None)):
    # await _check(x_api_key)
    out = await get_key_officers(company_name=company, top_n=top_n)
    return out

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)