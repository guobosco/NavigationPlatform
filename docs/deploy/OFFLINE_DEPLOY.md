# 离线环境部署指南 (Offline Deployment Guide)

本指南适用于无法访问互联网的内部网络环境（如保密机房、内部局域网等）。

## 1. 准备工作（在外网环境）

在部署到离线环境之前，你需要在一台**可以访问互联网**的机器上准备好部署包。

### 1.1 获取项目代码
```bash
git clone <repository-url>
cd NavigationPlatform
```

### 1.2 构建 Docker 镜像
使用 Docker 构建完整的应用镜像（包含前端和后端）。

```bash
# 构建镜像并标记为 starbase:v1.0.0
docker build -t starbase:v1.0.0 -f docker/Dockerfile .
```

### 1.3 导出镜像文件
将构建好的镜像保存为 `.tar` 文件，以便传输。

```bash
# 导出镜像
docker save -o starbase_v1.0.0.tar starbase:v1.0.0
```

### 1.4 准备部署文件
创建一个部署文件夹 `deployment/`，并将以下文件复制进去：
1. `starbase_v1.0.0.tar` (刚才导出的镜像)
2. `docker-compose.yml` (项目根目录下的编排文件)
3. `init_db.sql` (如果需要手动初始化数据库，通常容器会自动处理)

**建议打包：**
```bash
mkdir deployment_pack
cp starbase_v1.0.0.tar deployment_pack/
cp docker-compose.yml deployment_pack/
# 压缩以便传输
zip -r deployment_pack.zip deployment_pack/
```

---

## 2. 离线服务器部署

将 `deployment_pack.zip` 通过安全介质（如光盘、安全U盘）传输到离线服务器。

### 2.1 环境检查
确保离线服务器已安装 Docker 和 Docker Compose。
```bash
docker --version
docker-compose --version
```
> 如果未安装，请参考《离线安装 Docker 指南》先安装 Docker 环境。

### 2.2 导入镜像
解压部署包并导入镜像。

```bash
unzip deployment_pack.zip
cd deployment_pack

# 导入镜像
docker load -i starbase_v1.0.0.tar
```
验证镜像是否导入成功：
```bash
docker images | grep starbase
```

### 2.3 启动服务
直接使用 Docker Compose 启动。

```bash
# 后台启动
docker-compose up -d
```

### 2.4 验证部署
查看容器状态：
```bash
docker-compose ps
```
查看日志确保无报错：
```bash
docker-compose logs -f
```

访问应用：
- 打开浏览器访问服务器 IP 地址（例如 `http://192.168.1.100`）。
- 默认端口为 `80`。

---

## 3. 数据备份与迁移

系统数据存储在 Docker Volume `starbase_data` 中。

### 3.1 备份数据
```bash
# 停止服务
docker-compose stop

# 创建备份容器将数据卷打包
docker run --rm --volumes-from starbase_app -v $(pwd):/backup ubuntu tar cvf /backup/backup.tar /app/data
```

### 3.2 恢复数据
```bash
# 确保容器已创建但未启动，或者数据卷已存在
docker run --rm --volumes-from starbase_app -v $(pwd):/backup ubuntu bash -c "cd /app/data && tar xvf /backup/backup.tar --strip 1"
```

## 4. 常见问题

**Q: 启动时提示端口冲突？**
A: 修改 `docker-compose.yml` 中的端口映射，例如将 `80:8000` 改为 `8080:8000`。

**Q: 数据库文件在哪里？**
A: 默认在容器内的 `/app/data/sql_app.db`，映射到宿主机的 Docker Volume。

**Q: 如何更新版本？**
A: 在外网重复步骤 1.2-1.3 导出新镜像，在内网执行 `docker load` 导入新镜像，然后修改 `docker-compose.yml` 中的镜像标签（如果没变则不需要），最后执行 `docker-compose up -d` 重建容器。
