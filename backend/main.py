# main.py
from fastapi import FastAPI
from database import engine, Base
from routers import supervisor
from routers import user 

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(user.router, prefix="/api", tags=["user"])
app.include_router(supervisor.router)
# The supervisor function is completely decoupled, with a clear structure and high scalability

