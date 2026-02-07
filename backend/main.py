from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List
import base64
import secrets
import os
from datetime import datetime, timedelta
import bcrypt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from . import models, schemas, database

# 安全配置
# 生产环境中应更改此密钥
SECRET_KEY = "starbase-internal-secret-key-change-this-in-prod"
ALGORITHM = "HS256" # 加密算法
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # Token 过期时间（分钟）

# OAuth2 方案定义
# tokenUrl="token" 指定了获取 token 的 URL 路径
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 创建 FastAPI 应用实例
app = FastAPI(title="StarBase API", version="1.0.0")

# CORS（跨域资源共享）配置
# 允许前端应用访问后端 API
origins = [
    "http://localhost",
    "http://localhost:5173", # Vite 开发服务器
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 允许所有来源（生产环境应限制）
    allow_credentials=True,
    allow_methods=["*"], # 允许所有 HTTP 方法
    allow_headers=["*"], # 允许所有 HTTP 头
)

# 数据库依赖项
# 每个请求都会创建一个新的数据库会话，请求结束后关闭
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 初始化数据库表
# 自动创建所有定义的模型对应的表
models.Base.metadata.create_all(bind=database.engine)

# 辅助函数：验证密码
def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# 辅助函数：生成密码哈希
def get_password_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# 辅助函数：创建访问令牌 (JWT)
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    # 这里使用了 python-jose 库来生成 JWT
    from jose import jwt
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# 路由定义

@app.get("/")
def read_root():
    """根路径测试接口"""
    return {"message": "StarBase API Online"}

@app.post("/api/submit", response_model=schemas.PendingAppResponse)
def submit_app(app_data: schemas.PendingAppCreate, db: Session = Depends(get_db)):
    """
    提交新应用接口
    用户提交应用信息，进入待审核状态
    """
    # 创建提交令牌
    token = f"STAR-{datetime.now().strftime('%Y%m%d')}-{secrets.token_hex(4).upper()}"
    
    # 处理 Base64 缩略图
    thumb_blob = None
    if app_data.thumbnail_base64:
        try:
            # 移除 data URI 头部 (data:image/png;base64,)
            if "," in app_data.thumbnail_base64:
                header, encoded = app_data.thumbnail_base64.split(",", 1)
                thumb_blob = base64.b64decode(encoded)
            else:
                thumb_blob = base64.b64decode(app_data.thumbnail_base64)
        except Exception:
            pass # 忽略图片解码错误

    # 创建待审核应用记录
    db_app = models.PendingApp(
        name=app_data.name,
        url=app_data.url,
        description=app_data.description,
        developer=app_data.developer,
        deploy_env=app_data.deploy_env,
        category=app_data.category,
        scope=app_data.scope,
        admin_contact=app_data.admin_contact,
        thumbnail=thumb_blob,
        submit_token=token
    )
    db.add(db_app)
    db.commit()
    db.refresh(db_app)
    
    # 构建响应
    resp = schemas.PendingAppResponse.from_orm(db_app)
    resp.thumbnail_base64 = app_data.thumbnail_base64 # 将接收到的 Base64 原样返回（可选）
    return resp

@app.get("/api/apps", response_model=List[schemas.AppResponse])
def get_apps(category: str = None, db: Session = Depends(get_db)):
    """
    获取已批准应用列表接口
    支持按分类筛选
    """
    query = db.query(models.ApprovedApp).filter(models.ApprovedApp.status == 1)
    if category:
        query = query.filter(models.ApprovedApp.category == category)
    apps = query.all()
    
    results = []
    for app in apps:
        resp = schemas.AppResponse.from_orm(app)
        # 将二进制图片数据转换回 Base64 字符串供前端显示
        if app.thumbnail:
            b64 = base64.b64encode(app.thumbnail).decode('utf-8')
            resp.thumbnail_base64 = f"data:image/png;base64,{b64}"
        results.append(resp)
    return results

@app.get("/api/config", response_model=schemas.SystemConfigBase)
def get_config(db: Session = Depends(get_db)):
    """
    获取系统配置接口
    如标题、标语
    """
    title = db.query(models.SystemConfig).filter(models.SystemConfig.key == "title").first()
    slogan = db.query(models.SystemConfig).filter(models.SystemConfig.key == "slogan").first()
    
    return schemas.SystemConfigBase(
        title=title.value if title else "办公网网信系统融合应用平台",
        slogan=slogan.value if slogan else "打造网信系统开发、发布、推广应用的开放平台"
    )

# 管理员路由

# 获取当前管理员用户的依赖项
def get_current_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # 解码 Token
    from jose import jwt, JWTError
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user = db.query(models.AdminUser).filter(models.AdminUser.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    管理员登录接口
    验证用户名密码并返回 JWT Token
    """
    user = db.query(models.AdminUser).filter(models.AdminUser.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/admin/pending", response_model=List[schemas.PendingAppResponse])
def get_pending_apps(current_user: models.AdminUser = Depends(get_current_admin), db: Session = Depends(get_db)):
    """
    获取所有待审核应用接口（仅限管理员）
    """
    apps = db.query(models.PendingApp).all()
    results = []
    for app in apps:
        resp = schemas.PendingAppResponse.from_orm(app)
        if app.thumbnail:
            b64 = base64.b64encode(app.thumbnail).decode('utf-8')
            resp.thumbnail_base64 = f"data:image/png;base64,{b64}"
        results.append(resp)
    return results

@app.post("/api/admin/approve/{app_id}")
def approve_app(app_id: int, current_user: models.AdminUser = Depends(get_current_admin), db: Session = Depends(get_db)):
    """
    批准应用接口（仅限管理员）
    将应用从待审核表移动到已批准表
    """
    pending = db.query(models.PendingApp).filter(models.PendingApp.id == app_id).first()
    if not pending:
        raise HTTPException(status_code=404, detail="App not found")
    
    # 创建已批准应用记录
    approved = models.ApprovedApp(
        name=pending.name,
        url=pending.url,
        description=pending.description,
        developer=pending.developer,
        deploy_env=pending.deploy_env,
        category=pending.category,
        scope=pending.scope,
        admin_contact=pending.admin_contact,
        thumbnail=pending.thumbnail,
        status=1 # 上线状态
    )
    db.add(approved)
    
    # 记录审计日志
    log = models.AuditLog(user=current_user.username, action=f"Approved app {pending.name}")
    db.add(log)
    
    # 删除待审核记录
    db.delete(pending)
    db.commit()
    return {"status": "success"}

@app.put("/api/admin/config")
def update_config(config: schemas.SystemConfigBase, current_user: models.AdminUser = Depends(get_current_admin), db: Session = Depends(get_db)):
    """
    更新系统配置接口（仅限管理员）
    更新标题和标语
    """
    # 更新标题
    title = db.query(models.SystemConfig).filter(models.SystemConfig.key == "title").first()
    if not title:
        title = models.SystemConfig(key="title", value=config.title)
        db.add(title)
    else:
        title.value = config.title
        
    # 更新标语
    slogan = db.query(models.SystemConfig).filter(models.SystemConfig.key == "slogan").first()
    if not slogan:
        slogan = models.SystemConfig(key="slogan", value=config.slogan)
        db.add(slogan)
    else:
        slogan.value = config.slogan
        
    db.commit()
    return {"status": "success"}

@app.delete("/api/admin/apps/{app_id}")
def delete_app(app_id: int, current_user: models.AdminUser = Depends(get_current_admin), db: Session = Depends(get_db)):
    """
    删除应用接口（仅限管理员）
    这里执行的是物理删除，也可以改为软删除（设置状态为 offline）
    """
    app = db.query(models.ApprovedApp).filter(models.ApprovedApp.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    
    # 物理删除
    db.delete(app)
    
    # 记录审计日志
    log = models.AuditLog(user=current_user.username, action=f"Deleted app {app.name}")
    db.add(log)
    
    db.commit()
    return {"status": "success"}

# 挂载静态文件（必须放在最后）
# 用于提供前端构建后的静态资源
if os.path.exists("frontend/dist"):
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")
