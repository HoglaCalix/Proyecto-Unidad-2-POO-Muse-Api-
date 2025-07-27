import uvicorn
import logging
from fastapi import FastAPI , Request
from controllers.usercontroller import create_user,login 
from models.user import User
from models.loggin import Login
from utils.security import validateuser , validateadmin
from routes.art_type_routes import router as art_type_router
from routes.art_routes import router as art_router


app = FastAPI()
app.include_router(art_type_router)
app.include_router(art_router)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/")
def read_root():
    return {"version": "3.4", "message": "Welcome to the Muse API"}

@app.post("/users")
async def create_user_endpoint(user: User) -> User:
    return await create_user(user)

@app.post("/login")
async def login_access(l:Login):
    return await login(l)



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

