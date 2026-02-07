from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from . import models
from .main import get_password_hash
import base64

def init_db():
    """初始化数据库，创建默认用户和示例数据"""
    db = SessionLocal()
    
    # 检查是否已存在管理员用户
    admin = db.query(models.AdminUser).filter(models.AdminUser.username == "admin").first()
    if not admin:
        print("Creating default admin user...")
        # 创建默认管理员: admin / admin123
        admin = models.AdminUser(
            username="admin",
            password_hash=get_password_hash("admin123")
        )
        db.add(admin)
    
    # 检查并初始化系统配置
    if not db.query(models.SystemConfig).first():
        print("Seeding config...")
        db.add(models.SystemConfig(key="title", value="办公网网信系统融合应用平台"))
        db.add(models.SystemConfig(key="slogan", value="打造网信系统开发、发布、推广应用的开放平台"))
    
    # 如果没有应用，则填充示例数据
    if not db.query(models.ApprovedApp).first():
        print("Seeding example apps...")
        examples = [
            {
                "name": "协同办公系统",
                "category": models.CategoryEnum.web,
                "description": "提供日常办公协同、文档管理、流程审批等核心功能",
                "scope": "全公司",
                "developer": "信息中心",
                "deploy_env": "生产环境",
                "admin_contact": "张三"
            },
            {
                "name": "项目管理平台",
                "category": models.CategoryEnum.web,
                "description": "航天项目全生命周期管理，支持任务分配、进度跟踪、资源调度",
                "scope": "研发部",
                "developer": "研发部",
                "deploy_env": "生产环境",
                "admin_contact": "李四"
            },
            {
                "name": "数据资源中心",
                "category": models.CategoryEnum.data,
                "description": "统一数据资源管理，提供数据查询、分析和可视化服务",
                "scope": "数据部",
                "developer": "数据部",
                "deploy_env": "生产环境",
                "admin_contact": "王五"
            },
            {
                "name": "代码仓库平台",
                "category": models.CategoryEnum.service,
                "description": "Git代码托管、版本管理、代码审查和CI/CD集成",
                "scope": "技术部",
                "developer": "技术部",
                "deploy_env": "生产环境",
                "admin_contact": "赵六"
            },
             {
                "name": "系统监控中心",
                "category": models.CategoryEnum.service,
                "description": "实时监控系统运行状态、性能指标和告警信息",
                "scope": "运维部",
                "developer": "运维部",
                "deploy_env": "生产环境",
                "admin_contact": "孙七"
            },
             {
                "name": "知识库系统",
                "category": models.CategoryEnum.other,
                "description": "技术文档、规范标准、最佳实践的集中管理和分享",
                "scope": "技术委员会",
                "developer": "技术委员会",
                "deploy_env": "测试环境",
                "admin_contact": "周八"
            }
        ]
        
        for ex in examples:
            app = models.ApprovedApp(
                name=ex["name"],
                url="http://example.com", # 示例链接
                description=ex["description"],
                developer=ex["developer"],
                deploy_env=ex["deploy_env"],
                category=ex["category"],
                scope=ex["scope"],
                admin_contact=ex["admin_contact"],
                status=1 # 默认上线
            )
            db.add(app)
            
    db.commit()
    db.close()
    print("Database initialized.")

if __name__ == "__main__":
    # 确保所有表都已创建
    models.Base.metadata.create_all(bind=engine)
    init_db()
