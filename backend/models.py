from sqlalchemy import Column, Integer, String, Text, LargeBinary, DateTime, Enum, SmallInteger
from sqlalchemy.sql import func
import enum
from .database import Base

# 应用分类枚举
# 定义了应用可能的分类，如 Web、桌面、移动端等
class CategoryEnum(str, enum.Enum):
    web = "web"         # Web应用
    desktop = "desktop" # 桌面应用
    mobile = "mobile"   # 移动应用
    service = "service" # 服务/API
    data = "data"       # 数据服务
    other = "other"     # 其他

# 应用状态枚举
# 定义了应用的生命周期状态
class AppStatus(int, enum.Enum):
    pending = 0  # 待审核
    online = 1   # 已上线
    offline = 2  # 已下线

# 已批准的应用模型
# 存储已经通过审核并上线的应用信息
class ApprovedApp(Base):
    __tablename__ = "approved_apps"

    id = Column(Integer, primary_key=True, index=True) # 主键 ID
    name = Column(String, index=True)       # 应用名称
    url = Column(String)                    # 应用链接地址
    description = Column(Text)              # 应用描述
    developer = Column(String)              # 开发者/开发部门
    deploy_env = Column(String)             # 部署环境
    category = Column(Enum(CategoryEnum))   # 应用分类
    scope = Column(String)                  # 适用范围
    admin_contact = Column(String)          # 管理员联系方式
    thumbnail = Column(LargeBinary, nullable=True) # 缩略图数据（二进制），前端会检查大小限制
    status = Column(SmallInteger, default=AppStatus.online.value) # 应用状态，默认为上线
    created_at = Column(DateTime(timezone=True), server_default=func.now()) # 创建时间

# 待审核应用模型
# 存储用户提交但尚未通过审核的应用信息
class PendingApp(Base):
    __tablename__ = "pending_apps"

    id = Column(Integer, primary_key=True, index=True) # 主键 ID
    name = Column(String)                   # 应用名称
    url = Column(String)                    # 应用链接地址
    description = Column(Text)              # 应用描述
    developer = Column(String)              # 开发者/开发部门
    deploy_env = Column(String)             # 部署环境
    category = Column(Enum(CategoryEnum))   # 应用分类
    scope = Column(String)                  # 适用范围
    admin_contact = Column(String)          # 管理员联系方式
    thumbnail = Column(LargeBinary, nullable=True) # 缩略图数据
    submit_token = Column(String, unique=True, index=True) # 提交令牌，用于追踪或查询
    created_at = Column(DateTime(timezone=True), server_default=func.now()) # 提交时间

# 系统配置模型
# 存储系统的全局配置，如标题、标语等
class SystemConfig(Base):
    __tablename__ = "system_config"

    key = Column(String, primary_key=True, index=True) # 配置键名
    value = Column(String)                             # 配置键值

# 审计日志模型
# 记录管理员的关键操作日志
class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True) # 主键 ID
    user = Column(String)                              # 操作用户
    action = Column(String)                            # 操作内容描述
    timestamp = Column(DateTime(timezone=True), server_default=func.now()) # 操作时间

# 管理员用户模型
# 存储后台管理员的账号信息
class AdminUser(Base):
    __tablename__ = "admin_users"
    
    id = Column(Integer, primary_key=True, index=True) # 主键 ID
    username = Column(String, unique=True, index=True) # 用户名，唯一
    password_hash = Column(String)                     # 密码哈希值
