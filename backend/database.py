from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# 确保数据目录存在
# 如果不存在 ./data 目录，则创建它，用于存放 SQLite 数据库文件
if not os.path.exists("./data"):
    os.makedirs("./data")

# 数据库连接 URL，使用 SQLite 数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///./data/starbase.db"

# 创建 SQLAlchemy 引擎
# connect_args={"check_same_thread": False} 是 SQLite 特有的配置，
# 允许在多线程环境下使用同一个连接（FastAPI 是多线程的）
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 创建 SessionLocal 类
# autocommit=False: 不自动提交事务，需要手动 commit
# autoflush=False: 不自动刷新 flush，需要手动 flush
# bind=engine: 绑定到上面创建的引擎
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建 Base 类
# 所有的数据模型类都将继承自这个 Base 类
Base = declarative_base()

# 获取数据库会话的依赖函数
# 用于 FastAPI 的依赖注入
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        # 请求结束后关闭数据库会话
        db.close()
