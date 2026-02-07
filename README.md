# 内部网信系统导航平台 (StarBase)

## 项目简介

StarBase 是一个为内网环境设计的应用系统聚合平台，旨在实现应用的发布、审核、导航和管理的全链路闭环。通过统一的入口，用户可以便捷地访问和管理内网中的各类应用系统。

### 核心价值
- **统一入口**：为内网应用提供统一的访问入口
- **规范化管理**：实现应用的审核、发布和管理流程
- **零外联依赖**：完全在内网环境运行，不依赖外部服务
- **高可用性**：支持容器化部署，确保服务稳定运行

## 技术栈

### 前端
- **框架**：Vue 3 + TypeScript
- **构建工具**：Vite
- **样式方案**：UnoCSS
- **状态管理**：Pinia
- **路由**：Vue Router

### 后端
- **框架**：Python FastAPI
- **数据库**：SQLite
- **认证**：JWT (JSON Web Token)
- **密码加密**：bcrypt
- **CORS**：FastAPI CORSMiddleware

### 部署
- **容器化**：Docker + Docker Compose
- **静态文件**：FastAPI StaticFiles

## 系统架构

### 整体架构
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  前端应用        │◄────┤   API 服务      │◄────┤   数据库        │
│  Vue 3 + TS     │     │   FastAPI       │     │   SQLite        │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### 模块划分
1. **前端模块**
   - 用户界面 (Views)
   - 组件库 (Components)
   - 状态管理 (Stores)
   - 路由配置 (Router)

2. **后端模块**
   - API 路由
   - 数据模型
   - 认证授权
   - 应用管理
   - 系统配置

3. **数据模型**
   - 待审核应用 (PendingApp)
   - 已批准应用 (ApprovedApp)
   - 管理员用户 (AdminUser)
   - 系统配置 (SystemConfig)
   - 审计日志 (AuditLog)

## 主要功能

### 1. 应用提交与审核
- 用户可以提交新应用的信息和缩略图
- 系统生成唯一的提交令牌
- 管理员可以查看、审核待提交的应用
- 审核通过后，应用会被移至已批准列表

### 2. 应用管理
- 查看所有已批准的应用
- 按分类筛选应用
- 管理员可以删除已发布的应用
- 支持应用缩略图的管理

### 3. 系统管理
- 管理员登录认证（JWT 令牌）
- 系统配置管理（标题、标语等）
- 审计日志记录

### 4. 用户界面
- 响应式设计，支持不同设备
- 暗黑模式支持
- 应用卡片展示
- 分类导航

## 目录结构

```
NavigationPlatform/
├── backend/             # 后端代码
│   ├── database.py      # 数据库连接配置
│   ├── init_db.py       # 数据库初始化
│   ├── main.py          # 主应用入口
│   ├── models.py        # 数据模型定义
│   ├── requirements.txt # 依赖包列表
│   └── schemas.py       # 数据验证模式
├── frontend/            # 前端代码
│   ├── src/             # 源代码
│   │   ├── components/  # Vue 组件
│   │   ├── router/      # 路由配置
│   │   ├── stores/      # Pinia 状态管理
│   │   ├── views/       # 页面视图
│   │   ├── App.vue      # 根组件
│   │   ├── main.ts      # 入口文件
│   │   └── style.css    # 全局样式
│   ├── index.html       # HTML 模板
│   ├── package.json     # 前端依赖
│   ├── uno.config.ts    # UnoCSS 配置
│   └── vite.config.ts   # Vite 配置
├── docker/              # Docker 相关文件
│   ├── Dockerfile       # Docker 构建文件
│   └── start.sh         # 启动脚本
├── .gitignore           # Git 忽略文件
├── API_SPEC.yaml        # API 规范文档
├── DEPLOY.md            # 部署文档
├── PROJECT_DOCS.md      # 项目文档
├── README.md            # 项目说明
├── SECURITY.md          # 安全说明
├── docker-compose.yml   # Docker Compose 配置
└── init_db.sql          # 数据库初始化脚本
```

## 快速开始

### 开发环境

#### 前端开发
1. 进入前端目录
   ```bash
   cd frontend
   ```

2. 安装依赖
   ```bash
   npm install
   ```

3. 启动开发服务器
   ```bash
   npm run dev
   ```

4. 访问前端应用
   - 默认地址: http://localhost:5173

#### 后端开发
1. 进入后端目录
   ```bash
   cd backend
   ```

2. 创建虚拟环境并激活
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```

4. 初始化数据库
   ```bash
   python init_db.py
   ```

5. 启动后端服务器
   ```bash
   uvicorn main:app --reload
   ```

6. 访问后端 API
   - API 文档: http://localhost:8000/docs
   - 健康检查: http://localhost:8000/

### 生产部署

#### 使用 Docker Compose
1. 确保 Docker 和 Docker Compose 已安装

2. 在项目根目录执行
   ```bash
   docker-compose up -d
   ```

3. 访问应用
   - 应用地址: http://localhost
   - API 文档: http://localhost/docs

#### 详细部署指南
请参考 [DEPLOY.md](DEPLOY.md) 获取完整的部署文档索引。

- ☁️ **[腾讯云/公网服务器部署](docs/deploy/TENCENT_CLOUD_DEPLOY.md)**
- 🔒 **[离线环境/内网部署](docs/deploy/OFFLINE_DEPLOY.md)**

## API 文档

### API 端点

#### 公共接口
- `GET /` - 健康检查
- `POST /api/submit` - 提交新应用
- `GET /api/apps` - 获取已批准应用列表
- `GET /api/config` - 获取系统配置

#### 管理员接口
- `POST /token` - 获取管理员访问令牌
- `GET /api/admin/pending` - 获取待审核应用
- `POST /api/admin/approve/{app_id}` - 批准应用
- `PUT /api/admin/config` - 更新系统配置
- `DELETE /api/admin/apps/{app_id}` - 删除应用

### 详细 API 规范
请查看 `API_SPEC.yaml` 文件获取完整的 API 规范。

## 项目状态

### 功能状态
- ✅ 应用提交与审核流程
- ✅ 应用管理功能
- ✅ 系统配置管理
- ✅ 管理员认证
- ✅ 前端用户界面
- ✅ 容器化部署
- ✅ 中文代码注释 (前后端)

### 计划功能
- ⏳ 应用分类管理
- ⏳ 用户个性化设置
- ⏳ 应用使用统计
- ⏳ 更完善的权限管理

## 安全说明

### 注意事项
- 生产环境中请修改 `SECRET_KEY`
- 建议限制 CORS 来源，不要使用 `*`
- 定期备份数据库
- 遵循最小权限原则配置服务器

### 安全文档
请参考 `SECURITY.md` 文件获取详细的安全指南。

## 贡献指南

1. 克隆项目
   ```bash
   git clone <repository-url>
   cd NavigationPlatform
   ```

2. 创建功能分支
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. 提交更改
   ```bash
   git commit -m "Add your feature"
   ```

4. 推送分支
   ```bash
   git push origin feature/your-feature-name
   ```

5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证。详情请参阅 LICENSE 文件。

## 联系方式

- 项目维护者: 内网技术团队
- 问题反馈: 请通过内部工单系统提交

---

*StarBase - 让内网应用管理更简单*
