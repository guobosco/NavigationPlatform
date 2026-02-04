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

# Security
SECRET_KEY = "starbase-internal-secret-key-change-this-in-prod"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI(title="StarBase API", version="1.0.0")

# CORS
origins = [
    "http://localhost",
    "http://localhost:5173", # Vite dev
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For internal network, maybe restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Init DB
models.Base.metadata.create_all(bind=database.engine)

# Helper Functions
def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    # In a real app we would sign this with JWT. 
    # For simplicity and "no external deps" (though jose is pure python), 
    # I will just return a simple stateful token or implement JWT.
    # The requirements didn't forbid JWT. I'll use a simple approach for now.
    # actually let's use a simple random string mapped to user for this demo to avoid complex JWT setup if not strictly needed,
    # but JWT is standard. I'll use a mock implementation or basic JWT if I have the lib.
    # I added python-jose to requirements, so I can use it.
    from jose import jwt
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Routes

@app.get("/")
def read_root():
    return {"message": "StarBase API Online"}

@app.post("/api/submit", response_model=schemas.PendingAppResponse)
def submit_app(app_data: schemas.PendingAppCreate, db: Session = Depends(get_db)):
    # Create submit token
    token = f"STAR-{datetime.now().strftime('%Y%m%d')}-{secrets.token_hex(4).upper()}"
    
    # Handle Base64 thumbnail
    thumb_blob = None
    if app_data.thumbnail_base64:
        try:
            # Remove header if present (data:image/png;base64,...)
            if "," in app_data.thumbnail_base64:
                header, encoded = app_data.thumbnail_base64.split(",", 1)
                thumb_blob = base64.b64decode(encoded)
            else:
                thumb_blob = base64.b64decode(app_data.thumbnail_base64)
        except Exception:
            pass # Fail silently or raise error

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
    
    # Return response with base64 back (or handle it in schema)
    # The schema expects string, but model has bytes. 
    # We need to convert bytes back to base64 string for response? 
    # The submit response only needs token usually, but schema has all fields.
    
    resp = schemas.PendingAppResponse.from_orm(db_app)
    resp.thumbnail_base64 = app_data.thumbnail_base64 # Echo back or leave null
    return resp

@app.get("/api/apps", response_model=List[schemas.AppResponse])
def get_apps(category: str = None, db: Session = Depends(get_db)):
    query = db.query(models.ApprovedApp).filter(models.ApprovedApp.status == 1)
    if category:
        query = query.filter(models.ApprovedApp.category == category)
    apps = query.all()
    
    results = []
    for app in apps:
        resp = schemas.AppResponse.from_orm(app)
        if app.thumbnail:
            b64 = base64.b64encode(app.thumbnail).decode('utf-8')
            resp.thumbnail_base64 = f"data:image/png;base64,{b64}"
        results.append(resp)
    return results

@app.get("/api/config", response_model=schemas.SystemConfigBase)
def get_config(db: Session = Depends(get_db)):
    title = db.query(models.SystemConfig).filter(models.SystemConfig.key == "title").first()
    slogan = db.query(models.SystemConfig).filter(models.SystemConfig.key == "slogan").first()
    
    return schemas.SystemConfigBase(
        title=title.value if title else "办公网网信系统融合应用平台",
        slogan=slogan.value if slogan else "打造网信系统开发、发布、推广应用的开放平台"
    )

# Admin Routes
# Simple auth dependency
def get_current_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # Decode token
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
    pending = db.query(models.PendingApp).filter(models.PendingApp.id == app_id).first()
    if not pending:
        raise HTTPException(status_code=404, detail="App not found")
    
    # Move to approved
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
        status=1 # Online
    )
    db.add(approved)
    
    # Log
    log = models.AuditLog(user=current_user.username, action=f"Approved app {pending.name}")
    db.add(log)
    
    # Delete pending
    db.delete(pending)
    db.commit()
    return {"status": "success"}

@app.put("/api/admin/config")
def update_config(config: schemas.SystemConfigBase, current_user: models.AdminUser = Depends(get_current_admin), db: Session = Depends(get_db)):
    # Upsert title
    title = db.query(models.SystemConfig).filter(models.SystemConfig.key == "title").first()
    if not title:
        title = models.SystemConfig(key="title", value=config.title)
        db.add(title)
    else:
        title.value = config.title
        
    # Upsert slogan
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
    app = db.query(models.ApprovedApp).filter(models.ApprovedApp.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    
    app.status = 2 # Offline instead of delete? Or hard delete.
    # Requirement: "0-pending 1-online 2-offline".
    # But usually admin might want to delete. Let's set to offline for now or hard delete.
    # The UI shows "Delete" button usually.
    # Let's hard delete for simplicity or set status.
    # "Manage online cards" -> "Delete" usually means remove.
    db.delete(app)
    
    log = models.AuditLog(user=current_user.username, action=f"Deleted app {app.name}")
    db.add(log)
    
    db.commit()
    return {"status": "success"}

# Mount Static Files (Must be last)
if os.path.exists("frontend/dist"):
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")
