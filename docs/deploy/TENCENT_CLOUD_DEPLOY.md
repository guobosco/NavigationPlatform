# 腾讯云服务器部署指南 (Tencent Cloud Deployment Guide)

本指南适用于在腾讯云 CVM (Cloud Virtual Machine) 上部署 StarBase 导航平台。

## 1. 准备工作

### 1.1 购买与配置 CVM
1. **操作系统**: 推荐使用 Ubuntu 20.04/22.04 LTS 或 CentOS 7.9/8。
2. **配置**: 
   - CPU: 2核及以上
   - 内存: 4GB及以上 (构建过程可能需要较大内存，仅运行2GB即可)
   - 带宽: 根据访问量选择，建议 3Mbps 以上。

### 1.2 配置安全组
在腾讯云控制台 -> 安全组 -> 修改规则，开放以下端口：
- **Inbound (入站)**:
  - `TCP:22` (SSH远程连接)
  - `TCP:80` (HTTP服务)
  - `TCP:443` (HTTPS服务，如果配置SSL)

## 2. 环境安装

登录到服务器（使用 SSH）：
```bash
ssh ubuntu@<your-server-ip>
```

### 2.1 安装 Docker
以 Ubuntu 为例：
```bash
# 更新源
sudo apt-get update

# 安装依赖
sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common

# 添加 Docker 官方 GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 添加 Docker 仓库
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装 Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

### 2.2 获取代码
```bash
git clone <repository-url>
cd NavigationPlatform
```
*注：如果是私有仓库，需要配置 SSH Key 或使用 HTTPS Token。*

## 3. 部署服务

### 3.1 构建并启动
直接在服务器上构建镜像并启动（推荐）：

```bash
# 使用 Docker Compose 一键启动
sudo docker compose up -d --build
```

### 3.2 验证运行
```bash
sudo docker compose ps
```
确保状态为 `Up`。

此时访问 `http://<your-server-ip>` 应该可以看到登录页面。

## 4. 进阶配置（推荐）

### 4.1 使用 Nginx 反向代理
为了安全和灵活性，建议在宿主机安装 Nginx 代理请求，而不是让 Docker 直接占用 80 端口。

1. **修改 docker-compose.yml**:
   将端口映射改为本地环回地址：
   ```yaml
   ports:
     - "127.0.0.1:8000:8000"
   ```

2. **安装 Nginx**:
   ```bash
   sudo apt-get install nginx
   ```

3. **配置 Nginx**:
   编辑 `/etc/nginx/sites-available/starbase`:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;  # 你的域名或 IP

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       }
   }
   ```

4. **启用配置并重启**:
   ```bash
   sudo ln -s /etc/nginx/sites-available/starbase /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

### 4.2 配置 HTTPS (SSL)
如果拥有域名，建议配置 HTTPS。可以使用 `certbot` 免费申请证书。

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 5. 维护与更新

### 5.1 更新代码
```bash
git pull origin main
```

### 5.2 重启服务
```bash
sudo docker compose up -d --build
```
Docker Compose 会自动检测变更并重新构建镜像。

### 5.3 查看日志
```bash
sudo docker compose logs -f --tail=100
```
