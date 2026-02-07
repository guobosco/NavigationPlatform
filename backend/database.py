from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# 获取当前文件(database.py)的绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 数据目录拼接在 backend 目录下
DATA_DIR = os.path.join(BASE_DIR, "data")

print(f"DEBUG: BASE_DIR={BASE_DIR}")
print(f"DEBUG: DATA_DIR={DATA_DIR}")

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# 使用绝对路径连接数据库
SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.join(DATA_DIR, 'starbase.db')}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
