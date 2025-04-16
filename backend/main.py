# main.py
from fastapi import FastAPI
from database import engine, Base
from routers import user  # 导入你的路由

# 创建表（仅第一次用）
Base.metadata.create_all(bind=engine)

app = FastAPI()

# 挂载路由
app.include_router(user.router, prefix="/api", tags=["user"])
