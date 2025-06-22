import os
import uvicorn
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware
app = FastAPI()
class DynamicCORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        origin = request.headers.get("origin")
        if origin:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Authorization,Content-Type"
        return response

app.add_middleware(DynamicCORSMiddleware)
app.add_middleware(SessionMiddleware, secret_key=os.environ["SESSION_SECRET_KEY"])

if __name__ == '__main__':
    uvicorn.run('main:app', port=8000, reload=True)