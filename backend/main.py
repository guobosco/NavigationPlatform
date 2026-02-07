from fastapi import FastAPI, Depends, HTTPException, status, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional
import base64
import secrets
import os
from datetime import datetime, timedelta
import bcrypt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

try:
    from . import models, schemas, database
except ImportError:
    import models, schemas, database

# 安全配置
SECRET_KEY = "starbase-internal-secret-key-change-this-in-prod"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 24 hours

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI(title="StarBase API", version="2.0.0")

# CORS
origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库依赖项
def get_db():
    """
    获取数据库会话，请求结束后自动关闭
    """
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

models.Base.metadata.create_all(bind=database.engine)

# 认证辅助函数
def verify_password(plain_password, hashed_password):
    """验证密码是否匹配"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password):
    """生成密码哈希值"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    创建 JWT 访问令牌
    :param data: 包含在 payload 中的数据
    :param expires_delta: 过期时间增量
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    from jose import jwt
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    获取当前登录用户
    :param token: JWT 令牌
    :param db: 数据库会话
    """
    from jose import jwt, JWTError
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def get_current_admin(current_user: models.User = Depends(get_current_user)):
    """
    获取当前管理员用户 (依赖 get_current_user)
    """
    if current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=403, detail="Not enough privileges")
    return current_user

# --- Routes ---

@app.get("/")
def read_root():
    """API 根路径，用于健康检查"""
    return {"message": "StarBase API v2 Online"}

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    用户登录接口，获取访问令牌
    """
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token, 
        "token_type": "bearer", 
        "role": user.role,
        "username": user.username
    }

@app.post("/api/register", response_model=schemas.Token)
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    用户注册接口
    """
    # Check if user exists
    if db.query(models.User).filter(models.User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Create user
    db_user = models.User(
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
        plain_password=user_data.password, # Store plain text for admin view
        role=models.UserRole.user
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Auto login
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.username, "role": db_user.role}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token, 
        "token_type": "bearer", 
        "role": db_user.role,
        "username": db_user.username
    }

# --- Config APIs ---

@app.get("/api/config", response_model=schemas.SystemConfigBase)
def get_config(db: Session = Depends(get_db)):
    """获取系统配置信息"""
    config_dict = {}
    items = db.query(models.SystemConfig).all()
    for item in items:
        config_dict[item.key] = item.value
        
    return schemas.SystemConfigBase(
        title=config_dict.get("title", "办公网网信系统融合应用平台"),
        slogan=config_dict.get("slogan", "打造网信系统开发、发布、推广应用的开放平台"),
        home_nav_title=config_dict.get("home_nav_title", "系统导航"),
        footer_copyright=config_dict.get("footer_copyright", "© 2024 StarBase. All rights reserved."),
        nav_publish_text=config_dict.get("nav_publish_text", "发布"),
        submit_page_title=config_dict.get("submit_page_title", "发布新系统"),
        submit_page_desc=config_dict.get("submit_page_desc", "填写下方信息提交您的系统，管理员审核通过后将展示在首页"),
        
        # Placeholders
        placeholder_name=config_dict.get("placeholder_name", "例如：协同办公系统"),
        placeholder_url=config_dict.get("placeholder_url", "http://example.com"),
        placeholder_desc=config_dict.get("placeholder_desc", "简要描述系统的主要功能和用途..."),
        placeholder_developer=config_dict.get("placeholder_developer", "开发团队或个人姓名"),

        placeholder_admin_name=config_dict.get("placeholder_admin_name", "系统管理员姓名"),
        placeholder_contact_info=config_dict.get("placeholder_contact_info", "手机号或邮箱地址"),
        placeholder_server_location=config_dict.get("placeholder_server_location", "例如：总部机房 / 阿里云")
    )

@app.get("/api/admin/users", response_model=List[schemas.User])
def get_users(current_user: models.User = Depends(get_current_admin), db: Session = Depends(get_db)):
    """管理员接口：获取所有用户（含密码）"""
    return db.query(models.User).order_by(models.User.id.desc()).all()

@app.put("/api/admin/config")
def update_config(config: schemas.SystemConfigBase, current_user: models.User = Depends(get_current_admin), db: Session = Depends(get_db)):
    """管理员接口：更新系统配置"""
    # Helper to update or create config
    def set_config(key, value):
        item = db.query(models.SystemConfig).filter(models.SystemConfig.key == key).first()
        if not item:
            db.add(models.SystemConfig(key=key, value=value))
        else:
            item.value = value

    set_config("title", config.title)
    set_config("slogan", config.slogan)
    set_config("home_nav_title", config.home_nav_title)
    set_config("footer_copyright", config.footer_copyright)
    
    set_config("nav_publish_text", config.nav_publish_text)
    set_config("submit_page_title", config.submit_page_title)
    set_config("submit_page_desc", config.submit_page_desc)
    
    # Placeholders
    set_config("placeholder_name", config.placeholder_name)
    set_config("placeholder_url", config.placeholder_url)
    set_config("placeholder_desc", config.placeholder_desc)
    set_config("placeholder_developer", config.placeholder_developer)
    set_config("placeholder_admin_name", config.placeholder_admin_name)
    set_config("placeholder_contact_info", config.placeholder_contact_info)
    set_config("placeholder_server_location", config.placeholder_server_location)
        
    db.commit()
    return {"status": "success"}

# --- Category & Scope APIs ---

@app.get("/api/categories", response_model=List[schemas.Category])
def get_categories(db: Session = Depends(get_db)):
    """获取所有应用分类"""
    return db.query(models.Category).order_by(models.Category.sort_order).all()

@app.post("/api/admin/categories", response_model=schemas.Category)
def create_category(category: schemas.CategoryCreate, current_user: models.User = Depends(get_current_admin), db: Session = Depends(get_db)):
    """管理员接口：创建新分类"""
    db_cat = models.Category(**category.dict())
    db.add(db_cat)
    db.commit()
    db.refresh(db_cat)
    return db_cat

@app.delete("/api/admin/categories/{cat_id}")
def delete_category(cat_id: int, current_user: models.User = Depends(get_current_admin), db: Session = Depends(get_db)):
    """管理员接口：删除分类"""
    db_cat = db.query(models.Category).filter(models.Category.id == cat_id).first()
    if not db_cat:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(db_cat)
    db.commit()
    return {"status": "success"}

@app.get("/api/scopes", response_model=List[schemas.AppScope])
def get_scopes(db: Session = Depends(get_db)):
    """获取所有应用范围"""
    return db.query(models.AppScope).order_by(models.AppScope.sort_order).all()

@app.post("/api/admin/scopes", response_model=schemas.AppScope)
def create_scope(scope: schemas.AppScopeCreate, current_user: models.User = Depends(get_current_admin), db: Session = Depends(get_db)):
    """管理员接口：创建新应用范围"""
    db_scope = models.AppScope(**scope.dict())
    db.add(db_scope)
    db.commit()
    db.refresh(db_scope)
    return db_scope

@app.delete("/api/admin/scopes/{scope_id}")
def delete_scope(scope_id: int, current_user: models.User = Depends(get_current_admin), db: Session = Depends(get_db)):
    """管理员接口：删除应用范围"""
    db_scope = db.query(models.AppScope).filter(models.AppScope.id == scope_id).first()
    if not db_scope:
        raise HTTPException(status_code=404, detail="Scope not found")
    db.delete(db_scope)
    db.commit()
    return {"status": "success"}

# --- App APIs ---


# Let's redefine the route to properly accept the header
from fastapi import Header

@app.post("/api/submit", response_model=schemas.AppResponse)
def submit_app(
    app_data: schemas.AppCreate, 
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None) # Get Authorization header
):
    """
    提交新应用
    支持匿名提交和登录用户提交
    """
    owner_id = None
    if authorization:
        try:
            scheme, token = authorization.split()
            if scheme.lower() == 'bearer':
                from jose import jwt
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                username = payload.get("sub")
                user = db.query(models.User).filter(models.User.username == username).first()
                if user:
                    owner_id = user.id
        except:
            pass # Ignore invalid token

    # Handle Thumbnail
    thumb_blob = None
    if app_data.thumbnail_base64:
        try:
            # Handle data:image/jpeg;base64, prefix
            if "," in app_data.thumbnail_base64:
                header, encoded = app_data.thumbnail_base64.split(",", 1)
                thumb_blob = base64.b64decode(encoded)
            else:
                thumb_blob = base64.b64decode(app_data.thumbnail_base64)
        except Exception as e:
            print(f"Error decoding thumbnail: {e}")
            pass

    db_app = models.App(
        name=app_data.name,
        url=app_data.url,
        description=app_data.description,
        developer=app_data.developer,
        server_location=app_data.server_location,
        category_id=app_data.category_id,
        scope_id=app_data.scope_id,
        admin_contact=app_data.admin_contact,
        contact_info=app_data.contact_info,
        thumbnail=thumb_blob,
        status=models.AppStatus.pending.value,
        owner_id=owner_id
    )
    db.add(db_app)
    db.commit()
    db.refresh(db_app)
    
    # Re-fetch with relationships loaded
    db.refresh(db_app)
    
    return _format_app_response(db_app, db)

def _format_app_response(app, db):
    """格式化应用响应数据，处理缩略图 Base64 转换"""
    try:
        # Use model_validate for Pydantic v2
        resp = schemas.AppResponse.model_validate(app)
        # Fill Labels
        if app.category:
            resp.category_label = app.category.label
        if app.scope:
            resp.scope_label = app.scope.label
        # Fill Thumbnail Base64
        if app.thumbnail:
            b64 = base64.b64encode(app.thumbnail).decode('utf-8')
            resp.thumbnail_base64 = f"data:image/png;base64,{b64}"
        
        # 强制重新校验
        return schemas.AppResponse.model_validate(resp)
    except Exception as e:
        print(f"Error formatting response: {e}")
        raise e

@app.get("/api/apps", response_model=List[schemas.AppResponse])
def get_apps(category_id: int = None, db: Session = Depends(get_db)):
    """Public API: Get Online Apps"""
    query = db.query(models.App).filter(models.App.status == models.AppStatus.online.value)
    if category_id:
        query = query.filter(models.App.category_id == category_id)
    
    # Sort by Pinned (desc), Sort Order (desc), ID (desc)
    apps = query.order_by(
        models.App.is_pinned.desc(), 
        models.App.sort_order.desc(), 
        models.App.id.desc()
    ).all()
    
    return [_format_app_response(app, db) for app in apps]

@app.get("/api/my-apps", response_model=List[schemas.AppResponse])
def get_my_apps(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """用户接口：获取我提交的应用（所有状态）"""
    apps = db.query(models.App).filter(models.App.owner_id == current_user.id).order_by(models.App.id.desc()).all()
    return [_format_app_response(app, db) for app in apps]

@app.post("/api/apps/{app_id}/visit")
def record_visit(app_id: int, db: Session = Depends(get_db)):
    """Record a visit for an app"""
    app = db.query(models.App).filter(models.App.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    
    app.visits = (app.visits or 0) + 1
    db.commit()
    return {"status": "success", "visits": app.visits}

@app.get("/api/apps/{app_id}", response_model=schemas.AppResponse)
def get_app_details(app_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取应用详情（需要权限）"""
    app = db.query(models.App).filter(models.App.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    
    # Permission check: Owner or Admin
    if app.owner_id != current_user.id and current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=403, detail="Permission denied")
        
    return _format_app_response(app, db)

@app.put("/api/apps/{app_id}", response_model=schemas.AppResponse)
def update_app(
    app_id: int, 
    app_data: schemas.AppCreate, 
    current_user: models.User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    更新应用信息
    更新后状态会重置为待审核
    """
    app = db.query(models.App).filter(models.App.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
        
    # Permission check: Owner only (Admin usually uses status update API, but could be added here if needed)
    if app.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Permission denied")

    # Update fields
    app.name = app_data.name
    app.url = app_data.url
    app.description = app_data.description
    app.developer = app_data.developer
    app.server_location = app_data.server_location
    app.category_id = app_data.category_id
    app.scope_id = app_data.scope_id
    app.admin_contact = app_data.admin_contact
    app.contact_info = app_data.contact_info
    
    # Handle Thumbnail
    if app_data.thumbnail_base64:
        try:
            if "," in app_data.thumbnail_base64:
                header, encoded = app_data.thumbnail_base64.split(",", 1)
                app.thumbnail = base64.b64decode(encoded)
            else:
                app.thumbnail = base64.b64decode(app_data.thumbnail_base64)
        except Exception as e:
            print(f"Error decoding thumbnail: {e}")
            pass
            
    # Reset Status to Pending for re-audit
    app.status = models.AppStatus.pending.value
    app.reject_reason = None
    app.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(app)
    
    # Audit Log
    log = models.AuditLog(user=current_user.username, action=f"Updated and Resubmitted app {app.name}")
    db.add(log)
    db.commit()

    return _format_app_response(app, db)

@app.post("/api/apps/{app_id}/toggle-status")
def toggle_app_status(
    app_id: int, 
    current_user: models.User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """User/Admin API: Toggle App Status (Online <-> Offline)"""
    app = db.query(models.App).filter(models.App.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
        
    # Permission Check
    if app.owner_id != current_user.id and current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    # Only allow toggling between Online (1) and Offline (3)
    # Status 0 (Pending) and 2 (Rejected) cannot be toggled this way
    if app.status == models.AppStatus.online.value:
        app.status = models.AppStatus.offline.value
        action = "Offline"
    elif app.status == models.AppStatus.offline.value:
        app.status = models.AppStatus.online.value
        action = "Online"
    else:
        raise HTTPException(status_code=400, detail="Cannot toggle status for pending or rejected apps")
        
    db.commit()
    
    # Audit Log
    log = models.AuditLog(user=current_user.username, action=f"User toggled app {app.name} to {action}")
    db.add(log)
    db.commit()
    
    return {"status": "success", "new_status": app.status}

@app.get("/api/admin/apps", response_model=List[schemas.AppResponse])
def get_admin_apps(status: int = None, current_user: models.User = Depends(get_current_admin), db: Session = Depends(get_db)):
    """管理员接口：获取所有应用（支持状态筛选）"""
    query = db.query(models.App)
    if status is not None:
        query = query.filter(models.App.status == status)
    apps = query.order_by(models.App.id.desc()).all()
    return [_format_app_response(app, db) for app in apps]

@app.put("/api/admin/apps/{app_id}/attributes")
def update_app_attributes(
    app_id: int, 
    attr_data: schemas.AppAttributeUpdate, 
    current_user: models.User = Depends(get_current_admin), 
    db: Session = Depends(get_db)
):
    """Admin API: Update App Attributes (Sort, Pin, Star)"""
    app = db.query(models.App).filter(models.App.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    
    if attr_data.sort_order is not None:
        app.sort_order = attr_data.sort_order
    if attr_data.is_pinned is not None:
        app.is_pinned = attr_data.is_pinned
    if attr_data.is_starred is not None:
        app.is_starred = attr_data.is_starred
        
    db.commit()
    return {"status": "success"}

@app.put("/api/admin/apps/{app_id}/update")
def update_app_details_admin(
    app_id: int, 
    app_data: schemas.AppAdminDetailUpdate, 
    current_user: models.User = Depends(get_current_admin), 
    db: Session = Depends(get_db)
):
    """Admin API: Update App Details without status reset"""
    app = db.query(models.App).filter(models.App.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    
    # Update fields if provided
    if app_data.name is not None:
        app.name = app_data.name
    if app_data.url is not None:
        app.url = app_data.url
    if app_data.description is not None:
        app.description = app_data.description
    if app_data.developer is not None:
        app.developer = app_data.developer
    if app_data.server_location is not None:
        app.server_location = app_data.server_location
    if app_data.admin_contact is not None:
        app.admin_contact = app_data.admin_contact
    if app_data.contact_info is not None:
        app.contact_info = app_data.contact_info
    if app_data.category_id is not None:
        app.category_id = app_data.category_id
    if app_data.scope_id is not None:
        app.scope_id = app_data.scope_id
        
    db.commit()
    return {"status": "success"}

@app.post("/api/admin/apps/{app_id}/status")
def update_app_status(
    app_id: int, 
    status_data: schemas.AppUpdate, 
    current_user: models.User = Depends(get_current_admin), 
    db: Session = Depends(get_db)
):
    """管理员接口：审批应用（批准/拒绝/下线）"""
    app = db.query(models.App).filter(models.App.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    
    if status_data.status is not None:
        app.status = status_data.status
    if status_data.reject_reason is not None:
        app.reject_reason = status_data.reject_reason
        
    db.commit()
    
    # Audit Log
    action_map = {0: "Pending", 1: "Approved", 2: "Rejected", 3: "Offline"}
    action = action_map.get(status_data.status, "Updated")
    log = models.AuditLog(user=current_user.username, action=f"{action} app {app.name}")
    db.add(log)
    db.commit()
    
    return {"status": "success"}

@app.delete("/api/admin/apps/{app_id}")
def delete_app(app_id: int, current_user: models.User = Depends(get_current_admin), db: Session = Depends(get_db)):
    """管理员接口：删除应用"""
    app = db.query(models.App).filter(models.App.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    db.delete(app)
    db.commit()
    return {"status": "success"}

# --- Credential APIs ---

@app.get("/api/credentials/{app_id}", response_model=Optional[schemas.CredentialResponse])
def get_credential(app_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取指定应用的凭据"""
    cred = db.query(models.AppCredential).filter(
        models.AppCredential.user_id == current_user.id,
        models.AppCredential.app_id == app_id
    ).first()
    return cred

@app.post("/api/credentials", response_model=schemas.CredentialResponse)
def save_credential(cred_data: schemas.CredentialCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """保存或更新应用凭据"""
    cred = db.query(models.AppCredential).filter(
        models.AppCredential.user_id == current_user.id,
        models.AppCredential.app_id == cred_data.app_id
    ).first()
    
    if cred:
        cred.username_text = cred_data.username_text
        cred.password_text = cred_data.password_text
        cred.note = cred_data.note
    else:
        cred = models.AppCredential(
            user_id=current_user.id,
            **cred_data.dict()
        )
        db.add(cred)
    
    db.commit()
    db.refresh(cred)
    return cred

# Static Files
if os.path.exists("frontend/dist"):
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")
