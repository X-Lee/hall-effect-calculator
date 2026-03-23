# Docker 安装与使用完整流程

> 本文档整理了从 Docker 安装、镜像管理、容器操作、数据卷、网络、Compose 到清理的完整流程，适合新手到中级用户参考。

---

## 🟢 安装 Docker

| 步骤 | 命令 | 说明 |
|------|------|------|
| 安装 Docker | `apt install docker.io` / 官网下载安装包 | Linux / Mac / Windows |
| 启动服务 | `systemctl start docker` | Linux 必需 |
| 开机自启 | `systemctl enable docker` | 可选 |
| 验证安装 | `docker -v` | 查看版本 |
| 查看帮助 | `docker --help` | 命令说明 |

---

## 🟡 镜像管理

| 步骤 | 命令 | 说明 |
|------|------|------|
| 搜索镜像 | `docker search nginx` | 查看官方仓库可用镜像 |
| 拉取镜像 | `docker pull nginx:latest` | 从 Docker Hub 下载镜像 |
| 查看本地镜像 | `docker images` | 列出本地镜像 |
| 保存镜像 | `docker save -o nginx.tar nginx:latest` | 导出镜像为 tar 文件 |
| 加载镜像 | `docker load -i nginx.tar` | 将本地 tar 镜像加载到 Docker |
| 删除镜像 | `docker rmi <image_id>` | 删除本地镜像 |

---

## 🔵 容器操作

| 步骤 | 命令 | 说明 |
|------|------|------|
| 运行容器 | `docker run -d -p 8080:80 --name my_nginx nginx:latest` | 核心命令 |
| 查看运行中容器 | `docker ps` | 只显示运行中容器 |
| 查看全部容器 | `docker ps -a` | 包含停止容器 |
| 停止容器 | `docker stop <container_id>` | 停止容器 |
| 启动容器 | `docker start <container_id>` | 启动已停止容器 |
| 删除容器 | `docker rm <container_id>` | 删除容器 |
| 进入容器 | `docker exec -it <container_id> /bin/bash` | 调试或查看内部文件 |
| 查看日志 | `docker logs -f <container_id>` | 实时查看日志 |
| 查看资源 | `docker stats` | CPU/内存使用情况 |

---

## 🟠 数据管理

| 步骤 | 命令 | 说明 |
|------|------|------|
| 挂载本地目录 | `docker run -v /host/path:/container/path nginx` | 数据持久化 |
| 创建卷 | `docker volume create my_volume` | 数据卷 |
| 查看卷 | `docker volume ls` | 列出卷 |
| 删除卷 | `docker volume rm my_volume` | 删除卷 |

---

## 🔴 网络管理

| 步骤 | 命令 | 说明 |
|------|------|------|
| 查看网络 | `docker network ls` | 列出网络 |
| 创建网络 | `docker network create mynet` | 多容器互通 |
| 指定网络运行 | `docker run --network mynet nginx` | 指定网络运行容器 |

---

## ⚫ Docker Compose（项目化）

| 步骤 | 命令 | 说明 |
|------|------|------|
| 编写配置 | `docker-compose.yml` | 多服务项目 |
| 启动 | `docker-compose up -d` | 后台运行 |
| 停止 | `docker-compose down` | 停止所有服务 |
| 重建 | `docker-compose up -d --build` | 镜像修改后重新构建 |

---

## 🧹 清理 Docker 资源

| 步骤 | 命令 | 说明 |
|------|------|------|
| 清理系统 | `docker system prune -a` | 删除未使用镜像、容器、网络、缓存 |
| 删除所有容器 | `docker rm $(docker ps -aq)` | 全部删除 |
| 删除所有镜像 | `docker rmi $(docker images -q)` | 全部删除 |

---

## 🔥 核心一条流水线示例

```bash
# 拉镜像
docker pull nginx:latest

# 运行容器
docker run -d -p 8080:80 --name my_nginx nginx:latest

# 查看容器
docker ps

# 查看日志
docker logs -f my_nginx

# 停止容器
docker stop my_nginx

# 删除容器
docker rm my_nginx

# 删除镜像
docker rmi nginx:latest
```

---

## 💡 Docker 核心概念

- **镜像（Image）** = 模板  
- **容器（Container）** = 运行实例  
- **数据卷（Volume）** = 持久化数据  
- **网络（Network）** = 容器间通信  

---

## 🧠 使用顺序总结

1. 安装 Docker → 启动服务 → 验证  
2. 拉取/加载镜像 → 查看镜像  
3. 运行容器 → 查看运行状态 → 查看日志  
4. 持久化数据（挂载/卷） → 网络配置  
5. 项目化管理（Docker Compose）  
6. 停止容器 → 删除容器 → 清理镜像与资源  

