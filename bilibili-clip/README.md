# B站精彩切片自动化工具

自动分析B站视频，通过弹幕密度、音频能量、AI语义三重信号融合，智能识别高光片段并生成2-3分钟精彩切片。

## 功能特性

- 粘贴B站链接即可自动下载视频和弹幕
- 三信号融合检测精彩片段（弹幕密度 + 音频能量 + AI语义打分）
- 可视化时间轴展示分数热力图
- 支持手动调整片段选择（增删、拖拽）
- 一键导出切片视频（支持转场效果）
- Web界面操作，配置页管理API Key和参数

## 技术架构

```
┌─────────────────────────────────────────────────┐
│  Frontend (Vue3 + Element Plus)  端口: 5174     │
├─────────────────────────────────────────────────┤
│  Backend (FastAPI + SSE)         端口: 8001     │
├─────────────────────────────────────────────────┤
│  核心服务                                        │
│  ├── yt-dlp        视频下载                      │
│  ├── Bilibili API  弹幕获取                      │
│  ├── librosa       音频能量分析                   │
│  ├── Whisper       语音转文字                     │
│  ├── Claude API    AI语义打分                    │
│  └── ffmpeg        视频剪辑拼接                   │
└─────────────────────────────────────────────────┘
```

## 环境要求

- Python >= 3.10
- Node.js >= 18
- ffmpeg（必须在系统 PATH 中）
- yt-dlp（pip 安装或独立安装）
- GPU + CUDA（可选，加速 Whisper 语音识别）

## 快速启动

### 1. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 安装前端依赖

```bash
cd frontend
npm install
```

### 3. 配置

编辑项目根目录的 `config.yaml`：

```yaml
# 填入你的 Anthropic API Key（用于AI语义打分，不填则跳过AI打分）
anthropic_api_key: "sk-ant-xxxxx"

# Whisper 模型选择（tiny/base/small/medium/large）
whisper:
  model: "medium"    # medium 对中文效果最好
  device: "auto"     # auto 自动检测GPU，无GPU则用CPU
```

也可以启动后在 Web 界面的「系统设置」页面中配置。

### 4. 启动

**方式一：一键启动（Windows）**

双击 `start.bat`

**方式二：手动启动**

```bash
# 终端1 - 后端
cd backend
python run.py

# 终端2 - 前端
cd frontend
npm run dev
```

### 5. 访问

浏览器打开 http://localhost:5174

## 使用流程

1. 粘贴B站视频链接，点击「分析」
2. 等待视频下载完成
3. 点击「开始分析」，等待弹幕/音频/AI多步分析
4. 查看推荐的精彩片段，在时间轴上调整
5. 选择转场效果和质量，点击「生成切片」
6. 下载最终视频

## 配置说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `anthropic_api_key` | 空 | Claude API密钥，不填则仅用弹幕+音频双信号 |
| `whisper.model` | medium | 语音模型大小，越大越准但越慢 |
| `whisper.device` | auto | 运行设备，auto/cpu/cuda |
| `analysis.weights.danmaku` | 0.4 | 弹幕密度权重 |
| `analysis.weights.audio` | 0.3 | 音频能量权重 |
| `analysis.weights.ai` | 0.3 | AI语义权重 |
| `clip.target_duration` | 150 | 目标切片总时长（秒） |
| `clip.min_segment` | 15 | 最短片段（秒） |
| `clip.max_segment` | 60 | 最长片段（秒） |

## 处理耗时参考

| 视频时长 | 下载 | 音频分析 | Whisper(CPU) | Whisper(GPU) | 总计(CPU) | 总计(GPU) |
|----------|------|----------|--------------|--------------|-----------|-----------|
| 10分钟 | 30s | 10s | 5min | 1min | ~6min | ~2min |
| 30分钟 | 90s | 25s | 15min | 3min | ~18min | ~5min |

## 项目结构

```
bilibili-clip/
├── config.yaml                  # 统一配置文件
├── start.bat                    # Windows一键启动
├── backend/
│   ├── run.py                   # 后端入口
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py              # FastAPI应用
│   │   ├── config.py            # 配置读写
│   │   ├── models/schemas.py    # 数据模型
│   │   ├── routers/
│   │   │   ├── video.py         # 视频下载接口
│   │   │   ├── analysis.py      # 分析管线接口
│   │   │   ├── export.py        # 导出接口
│   │   │   └── settings.py      # 配置管理接口
│   │   └── services/
│   │       ├── bilibili.py      # B站下载+弹幕
│   │       ├── audio_analysis.py
│   │       ├── transcription.py # Whisper
│   │       ├── llm_scoring.py   # Claude打分
│   │       ├── score_fusion.py  # 信号融合
│   │       ├── segment_selector.py
│   │       └── video_editor.py  # ffmpeg剪辑
│   ├── uploads/                 # 下载的视频(临时)
│   ├── outputs/                 # 生成的切片
│   └── cache/                   # 中间结果缓存
└── frontend/
    ├── index.html
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── main.js
        ├── App.vue
        ├── api/index.js
        ├── router/index.js
        ├── views/
        │   ├── ClipView.vue     # 主页面
        │   └── SettingsView.vue # 设置页
        └── components/
            ├── UrlInput.vue
            ├── ProgressTracker.vue
            ├── TimelineEditor.vue
            ├── SegmentCard.vue
            ├── VideoPreview.vue
            └── ExportPanel.vue
```

## 与热力图项目的关联

本项目与 `correlation-heatmap` 为同级独立项目。热力图项目的侧边栏已添加「B站切片」菜单项，点击后会在新窗口打开本工具（localhost:5174）。两个项目独立运行，互不影响。
