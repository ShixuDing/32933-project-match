from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import supervisor, user

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI()

# 打印确认是否启动的是你写的 main.py
print("✅ 正在运行我自己修改过的 main.py ✅")

# 跨域配置（开发阶段允许所有源）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载路由
app.include_router(user.router, prefix="/api", tags=["user"])
app.include_router(supervisor.router)





