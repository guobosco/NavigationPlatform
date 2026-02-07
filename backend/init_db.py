try:
    from .database import SessionLocal, engine
    from . import models
except ImportError:
    from database import SessionLocal, engine
    import models

import bcrypt

def init_db():
    db = SessionLocal()
    
    # 1. Check if Admin exists
    admin = db.query(models.User).filter(models.User.username == "admin").first()
    if not admin:
        print("Creating admin user...")
        pwd_hash = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        admin_user = models.User(
            username="admin", 
            password_hash=pwd_hash, 
            plain_password="admin123", # For demo/admin view
            role=models.UserRole.admin
        )
        db.add(admin_user)
    else:
        # Update existing admin to have plain_password if missing
        if not admin.plain_password:
             print("Updating admin user with plain password...")
             admin.plain_password = "admin123" # Reset/Update for consistency
    
    # 2. Check if Standard User exists
    user = db.query(models.User).filter(models.User.username == "user").first()
    if not user:
        print("Creating standard user...")
        pwd_hash = bcrypt.hashpw("user123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        std_user = models.User(
            username="user", 
            password_hash=pwd_hash, 
            plain_password="user123", # For demo/admin view
            role=models.UserRole.user
        )
        db.add(std_user)
    else:
        # Update existing user to have plain_password if missing
        if not user.plain_password:
            print("Updating standard user with plain password...")
            user.plain_password = "user123"

    # 3. Init Categories
    categories = [
        ("web", "行政办公"),
        ("desktop", "业务系统"),
        ("data", "资源数据"),
        ("service", "开发工具"),
        ("other", "监控运维")
    ]
    for i, (name, label) in enumerate(categories):
        cat = db.query(models.Category).filter(models.Category.name == name).first()
        if not cat:
            print(f"Creating category: {label}")
            db.add(models.Category(name=name, label=label, sort_order=i))

    # 4. Init Scopes
    scopes = [
        ("all", "全公司"),
        ("dept", "部门内部"),
        ("group", "项目组"),
        ("personal", "个人专用")
    ]
    for i, (name, label) in enumerate(scopes):
        scope = db.query(models.AppScope).filter(models.AppScope.name == name).first()
        if not scope:
            print(f"Creating scope: {label}")
            db.add(models.AppScope(name=name, label=label, sort_order=i))

    db.commit()
    db.close()
    print("Database initialized successfully.")

if __name__ == "__main__":
    # Ensure tables are created
    models.Base.metadata.create_all(bind=engine)
    init_db()
