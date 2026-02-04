# 部署指南 (Deployment Guide)

本平台支持单容器离线部署，适合航天内网环境。

## 环境要求
- Docker 20.10+
- Docker Compose v2.0+

## 目录说明
- `docker/`: 包含 Dockerfile 和启动脚本
- `docker-compose.yml`: 编排文件
- `backend/`: 后端源码
- `frontend/`: 前端源码

## 在线构建与启动 (开发环境)
1. 确保已安装 Docker 和 Docker Compose。
2. 在项目根目录下运行：
   ```bash
   docker-compose up -d --build
   ```
3. 访问 `http://localhost:80` (或服务器IP)。

## 离线部署流程 (生产环境)

### 1. 构建镜像 (在外网机器)
```bash
# 构建镜像
docker build -t starbase:v1 -f docker/Dockerfile .

# 导出镜像
docker save -o starbase_v1.tar starbase:v1
```

### 2. 导入镜像 (在内网服务器)
将 `starbase_v1.tar` 和 `docker-compose.yml` 传输到内网服务器。

```bash
# 导入镜像
docker load -i starbase_v1.tar
```

### 3. 启动服务
修改 `docker-compose.yml` (如有必要，如端口映射)，然后运行：

```bash
# 启动
docker-compose up -d
```

### 4. 数据持久化
系统数据存储在 Docker 卷 `starbase_data` 中 (映射到容器内 `/app/data`)。
如需备份，请备份该 Docker 卷或挂载主机目录。

## 默认账号
- 管理员后台: `/admin/login`
- 用户名: `admin`
- 初始密码: `admin123` (请登录后尽快修改配置或数据库)
