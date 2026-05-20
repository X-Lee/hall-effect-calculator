# 科研相关性热图工具

前后端分离的科研绘图工具，支持上传数据生成相关性热图，可选 Pearson/Spearman/Kendall 方法，带显著性标注。

## 技术栈

- 后端：Python + FastAPI + matplotlib + seaborn + scipy
- 前端：Vue 3 + Vite + Element Plus
- 部署：Docker + nginx

## 本地启动测试

### 方式一：一键启动（Windows）

双击 `start.bat`，会自动创建虚拟环境、安装依赖、启动前后端。

### 方式二：手动启动

```bash
# 1. 创建虚拟环境并安装后端依赖
cd correlation-heatmap
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac
pip install -r backend/requirements.txt

# 2. 启动后端（端口 8000）
cd backend
python run.py

# 3. 新开终端，安装并启动前端（端口 5173）
cd correlation-heatmap/frontend
npm install
npm run dev
```

启动后访问 http://localhost:5173

## Docker 打包

```bash
cd correlation-heatmap

# 构建镜像
docker-compose up --build

# 构建完成后访问 http://localhost 验证
```

构建会生成两个镜像：
- `correlation-heatmap-backend:latest`
- `correlation-heatmap-frontend:latest`

## 离线部署

### 1. 导出镜像（在有网络的机器上）

```bash
docker save correlation-heatmap-backend:latest correlation-heatmap-frontend:latest -o correlation-heatmap-images.tar
```

### 2. 传输文件到目标机器

需要拷贝的文件：
- `correlation-heatmap-images.tar`（镜像包）
- `docker-compose-run.yml`（部署配置）

### 3. 在目标机器上部署

```bash
# 加载镜像
docker load -i correlation-heatmap-images.tar

# 启动服务
docker-compose -f docker-compose-run.yml up -d
```

启动后访问 http://<目标机器IP> 即可使用。

### 停止服务

```bash
docker-compose -f docker-compose-run.yml down
```

## 功能说明

1. 上传 CSV 或 Excel 文件
2. 选择数值列、相关性方法（Pearson/Spearman/Kendall）
3. 配置配色方案、字体大小、显著性标注等参数
4. 生成热图预览
5. 导出高清 PNG（300 DPI）或 PDF

## 配色方案自定义

### 当前默认配色

系统内置 15 种配色方案：

`RdBu_r` `coolwarm` `viridis` `plasma` `inferno` `magma` `cividis` `RdYlBu_r` `RdYlGn_r` `Spectral_r` `BrBG_r` `PiYG_r` `PRGn_r` `PuOr_r` `seismic`

### 修改/新增配色

编辑 `backend/app/routers/heatmap.py`，找到 `/api/colormaps` 端点中的 `cmaps` 列表，添加或删除配色名称：

```python
@router.get("/api/colormaps")
async def get_colormaps():
    cmaps = [
        "RdBu_r", "coolwarm", "viridis", "plasma", "inferno",
        "magma", "cividis", "RdYlBu_r", "RdYlGn_r", "Spectral_r",
        "BrBG_r", "PiYG_r", "PRGn_r", "PuOr_r", "seismic",
        # 在此添加新的配色方案，例如：
        # "twilight", "hsv", "Pastel1", "Set2",
    ]
    return {"colormaps": cmaps}
```

### 查看所有可用配色名称

在 Python 中运行以下命令可列出 matplotlib 支持的全部配色方案：

```python
import matplotlib.pyplot as plt
print(plt.colormaps())
```

常用科研配色推荐：
- 发散型（适合相关性）：`RdBu_r`, `coolwarm`, `seismic`, `BrBG_r`
- 连续型：`viridis`, `plasma`, `inferno`, `magma`, `cividis`
- 分类型：`Set1`, `Set2`, `Paired`, `tab10`

### 说明

前端下拉菜单从 `/api/colormaps` 接口动态获取配色列表，修改后端列表后重启服务即可生效，无需改动前端代码。
