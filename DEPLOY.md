# 部署指南 (Deployment Guide)

StarBase 导航平台支持多种部署方式，请根据您的环境选择合适的指南。

## 部署文档索引

### 1. 🚀 [快速开始 (开发/测试)](README.md#快速开始)
适用于本地开发或快速体验功能。使用 Docker Compose 即可一键启动。

### 2. ☁️ [腾讯云/公网服务器部署](docs/deploy/TENCENT_CLOUD_DEPLOY.md)
适用于在腾讯云 CVM、阿里云 ECS 或其他公网 Linux 服务器上部署。
- 包含环境安装 (Docker)
- 安全组配置
- Nginx 反向代理与 HTTPS 配置

### 3. 🔒 [离线环境/内网部署](docs/deploy/OFFLINE_DEPLOY.md)
适用于无互联网访问权限的内网环境（如保密机房）。
- 离线镜像构建与导出
- 镜像导入与加载
- 数据备份与迁移方案

---

## 通用 Docker 命令速查

| 操作 | 命令 | 说明 |
|------|------|------|
| **启动服务** | `docker-compose up -d` | 后台启动所有服务 |
| **构建并启动** | `docker-compose up -d --build` | 代码更新后重新构建并启动 |
| **停止服务** | `docker-compose stop` | 仅停止容器，保留状态 |
| **停止并删除** | `docker-compose down` | 删除容器和网络 (保留数据卷) |
| **查看日志** | `docker-compose logs -f` | 实时查看服务日志 |
| **查看状态** | `docker-compose ps` | 查看容器运行状态 |

## 数据持久化说明

无论采用何种部署方式，系统核心数据均存储在 Docker Volume `starbase_data` 中。
- **容器内路径**: `/app/data`
- **包含内容**: 
  - `sql_app.db` (SQLite 数据库文件)
  - `uploads/` (上传的应用图标等文件)

请务必定期备份该数据卷，具体备份方法参考 [离线部署指南 - 数据备份](docs/deploy/OFFLINE_DEPLOY.md#3-数据备份与迁移)。
