# -*- coding: utf-8 -*-
# @Author : User Lee
# @File : app.py.py
import streamlit as st

# --- 页面配置 ---
st.set_page_config(page_title="我的个人主页", page_icon="🚀", layout="centered")

# --- 自定义 CSS (用于美化界面) ---
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stProgress > div > div > div > div {
        background-color: #007bff;
    }
    </style>
    """, unsafe_allow_html=True)


# 1. 注入一点自定义 CSS，增加交互感
st.markdown("""
    <style>
    .school-text {
        color: #31333F;
        font-weight: bold;
        text-decoration: underline dotted #007bff; /* 加个蓝色虚线下划线，提示可以点击/悬停 */
        cursor: help;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 侧边栏：个人信息 ---
with st.sidebar:
    st.image(
        "https://img0.baidu.com/it/u=2612741288,182099192&fm=253&fmt=auto&app=120&f=JPEG?w=513&h=500",
        caption="LEE",
        width=50  # 在这里设置你想要的宽度
    )
    st.title("联系我")
    st.write("📧 Email: lixiaochun521@163.com")
    st.write("🔗 [GitHub](https://github.com/X-Lee)")
    # st.write("📝 [知乎/掘金](https://juejin.cn)")
    # st.info("欢迎来到我的个人角落！这里记录了我的技术成长与项目沉淀。")
    with st.sidebar:
        st.subheader("🏆 荣誉")

        # 定义一套精简的 CSS 样式
        st.markdown("""
        <style>
        .award-item {
            margin-bottom: 10px;
            line-height: 1.4;
        }
        .award-title {
            font-size: 12px;
            font-weight: bold;
            color: #31333F;
            display: block;
        }
        .award-meta {
            font-size: 12px;
            color: #666;
        }
        </style>
        """, unsafe_allow_html=True)

        # 1. 奖项一
        st.markdown("""
        <div class="award-item">
            <span class="award-title">🥉 第四届河北省研究生网络与信息安全技术大赛</span>
            <span class="award-meta">三等奖 · 研究生 (2023)</span>
        </div>
        """, unsafe_allow_html=True)

        # 2. 奖项二
        st.markdown("""
        <div class="award-item">
            <span class="award-title">🎓 连续三年研究生学业奖学金</span>
            <span class="award-meta">校级三等 · 研究生</span>
        </div>
        """, unsafe_allow_html=True)

        # 3. 奖项三
        st.markdown("""
        <div class="award-item">
            <span class="award-title">🥉 第12届中国大学生计算机设计大赛河北省级赛</span>
            <span class="award-meta">三等奖 · 本科 (2020)</span>
        </div>
        """, unsafe_allow_html=True)

        # 4. 奖项四
        st.markdown("""
        <div class="award-item">
            <span class="award-title">🎓 18-19学年优秀奖学金</span>
            <span class="award-meta">校级二等 · 本科</span>
        </div>
        """, unsafe_allow_html=True)


    with st.sidebar:
        # st.divider()
        st.subheader("🏆 证书")
        # 使用自定义 HTML 样式
        st.markdown("""
        <div style="background-color: #f0f2f6; padding: 10px; border-radius: 5px; border-left: 5px solid #ffaa00;">
            <div style="font-size: 13px; margin-bottom: 5px;">计算机三级数据库</div>
            <div style="font-size: 13px; margin-bottom: 5px;">计算机二级C语言</div>
            <div style="font-size: 13px; margin-bottom: 5px;">计算机二级Office</div>
        </div>
        """, unsafe_allow_html=True)


# --- 主界面：个人介绍 ---
st.title("👋 你好，我是 User LEE")
st.subheader("一名热爱技术的 [预测算法工程师]")
st.write(
    """
    我专注于构建高效、可扩展的系统，并热衷于探索前沿技术。
    具备较强的学习能力和扎实的专业知识，做事认真且性格开朗，拥有积极的工作态度，能够高效完成任务。
    在多个重要项目的实践中，业务知识到技术水平都在快速成长，
    同时积累了丰富的模型研究思路、算法优化方法以及报告编写技巧，这些技术能力将在未来的工作中得以充分展现。
    """
)

st.divider()

# --- 技术栈 (技能条) ---
st.header("🛠️ 技术栈")
col1, col2 = st.columns(2)

with col1:
    st.write("**编程语言**")
    st.progress(95, text="Python")
    st.progress(90, text="LLM / Machine Learning / Deep Learning")
    st.progress(85, text="Dify")
    st.progress(80, text="RAG")
    st.progress(70, text="LLAMA Factory / Lora")


with col2:
    st.write("**框架 & 工具**")
    st.progress(85, text="Streamlit / Flask")
    st.progress(80, text="Docker / Git")
    st.progress(80, text="PyTorch / TensorFlow")

st.divider()

# --- 职业与教育背景 ---
st.header("💼 个人历程")

# 1. 最近的工作经历 (重点展示)
with st.container(border=True):
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("##### 📍 北京数洋科技有限公司&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;算法工程师")
        # st.caption("🚀 **算法工程师**")
    with col2:
        st.write("")  # 占位
        st.write("`2023.07 - 至今`")

    # 第一层：最外层的大折叠框
    with st.expander("📂 **点击展开：重点项目经历合集**", expanded=False):
        st.write("以下是我在 2023-2026 年间主导的核心算法与平台开发项目：")
        st.write("")  # 留点间距

        # 创建分栏
        xm1, xm2 = st.columns([3, 1])
        with xm1:
            # 左侧：大标题
            st.markdown("##### NL2SQL 及其它相关项目")
        with xm2:
            # 右侧：时间对齐
            st.write("")  # 稍微下移一点对齐标题
            st.write("`2025.10 - 2026.01`")
        # 在下方放置详情折叠框，它会自动对齐宽度
        with st.expander("**工作职责**", expanded=True):
            st.markdown("""
                - 数据集构建，大模型微调（Llama Factory框架）
                - 知识库构建，RAG增强检索（智能体编排）
                - 现场产品对接与需求对接
                - 材料编写等其它事宜
            """)

            # 既然是 NL2SQL 相关，建议加一两句核心技术点
            st.caption("核心技术：Llama-Factory RAG Dify")

        # 创建分栏
        xm1, xm2 = st.columns([3, 1])
        with xm1:
            # 左侧：大标题
            st.markdown("##### 智能体编排")
        with xm2:
            # 右侧：时间对齐
            st.write("")  # 稍微下移一点对齐标题
            st.write("`2025.07 - 2025.10`")
        # 在下方放置详情折叠框，它会自动对齐宽度
        with st.expander("**工作职责**", expanded=True):
            st.markdown("""
                - 数据需求梳理，智能体编排
                - 大小模型协调设计
                - 会议评审，材料编写等其它事宜
            """)

        # 创建分栏
        xm1, xm2 = st.columns([3, 1])
        with xm1:
            # 左侧：大标题
            st.markdown("##### 山东济南典型经验")
        with xm2:
            # 右侧：时间对齐
            st.write("")  # 稍微下移一点对齐标题
            st.write("`2025.09 - 2025.10`")
        # 在下方放置详情折叠框，它会自动对齐宽度
        with st.expander("**工作职责**", expanded=True):
            st.markdown("""
                - 聚类算法开发，实现典型用户曲线选取
                - 智能体搭建，实现用户标签智能标注
                - 会议评审，材料编写等其它事宜
            """)

        # 创建分栏
        xm1, xm2 = st.columns([3, 1])
        with xm1:
            # 左侧：大标题
            st.markdown("##### 国网大数据中心服务类项目")
        with xm2:
            # 右侧：时间对齐
            st.write("")  # 稍微下移一点对齐标题
            st.write("`2025.02 - 2025.10`")
        # 在下方放置详情折叠框，它会自动对齐宽度
        with st.expander("**工作职责**", expanded=True):
            st.markdown("""
                - 用电分析预测平台算法设计，实现，优化负责人
                - 大模型相关知识调研，环境搭建（dify）
                - 会议评审，材料编写等其它事宜
            """)

        # 创建分栏
        xm1, xm2 = st.columns([3, 1])
        with xm1:
            # 左侧：大标题
            st.markdown("##### 浙江全时域用电态势分析")
        with xm2:
            # 右侧：时间对齐
            st.write("")  # 稍微下移一点对齐标题
            st.write("`2024.07 - 2025.11`")
        # 在下方放置详情折叠框，它会自动对齐宽度
        with st.expander("**工作职责**", expanded=True):
            st.markdown("""
                - 现场算法负责人，需求对接，产品对接，人员管理
                - 负责光伏出力新能源算法数据收集，算法设计，算法实现，算法优化
                - 负责负荷预测数据清洗算法，负荷预测算法，光伏出力预测算法的优化
                - 验收材料，PPT，原型等文档以及其他相关事宜
            """)
            st.caption("2025年02月以后变为远程支撑人员")

        # 创建分栏
        xm1, xm2 = st.columns([3, 1])
        with xm1:
            # 左侧：大标题
            st.markdown("##### 面向新型电力系统的智能配电网运行特征挖掘与负荷辨识感知智能算法研究项目")
        with xm2:
            # 右侧：时间对齐
            st.write("")  # 稍微下移一点对齐标题
            st.write("`2023.07 - 2024.02`")
        # 在下方放置详情折叠框，它会自动对齐宽度
        with st.expander("**工作职责**", expanded=True):
            st.markdown("""
                - 负责智能配电网中负荷分解算法的数据收集，算法设计，算法实现，算法优化
                - 负责智能配电网中源荷匹配算法的数据收集，算法设计，算法实现，算法优化
                - 负责数据清洗算法，负荷预测算法，光伏出力预测算法的优化
                - 负责编写《面向新型电力系统的智能配电网运行特征挖掘与负荷辨识感知智能算法技术研究报告》
                - 验收材料，PPT，原型等文档以及其他相关事宜
            """)

        # 创建分栏
        xm1, xm2 = st.columns([3, 1])
        with xm1:
            # 左侧：大标题
            st.markdown("##### 国电南瑞2023年用电信息采集系统组管理模块实施服务项目")
        with xm2:
            # 右侧：时间对齐
            st.write("")  # 稍微下移一点对齐标题
            st.write("`2023.07 - 2024.05`")
        # 在下方放置详情折叠框，它会自动对齐宽度
        with st.expander("**工作职责**", expanded=True):
            st.markdown("""
                - 负责数据清洗算法，分类聚类算法，预测算法的维护
                - 负责负荷预测算法的升级，包括多特征，自动参数优化，数据异常处理等
                - 负责现场算法上架优化，合肥现场用户级别负荷预测平均准确度优化至80%以上
                - 负责与甲方专责对接及沟通需求相关事宜
                - 负责编写算法说明文档等其他相关事宜
            """)

        # 创建分栏
        xm1, xm2 = st.columns([3, 1])
        with xm1:
            # 左侧：大标题
            st.markdown("##### 国网大数据中心典型公共建筑碳排放测算项目")
        with xm2:
            # 右侧：时间对齐
            st.write("")  # 稍微下移一点对齐标题
            st.write("`2023.07 - 2024.10`")
        # 在下方放置详情折叠框，它会自动对齐宽度
        with st.expander("**工作职责**", expanded=True):
            st.markdown("""
                - 负责典型公共建筑基本数据处理，数据分析，特征构建等
                - 负责典型公共建筑碳排放测算模型的设计，开发与优化，包括不限于超参数优化，特征筛选，模型筛选等
                - 负责专利交底书初稿的编写
                - 负责3个子报告与1个优化报告的编写
                - 负责原型设计阶段的沟通以及其他相关事宜
            """)

        # 创建分栏
        xm1, xm2 = st.columns([3, 1])
        with xm1:
            # 左侧：大标题
            st.markdown("##### 国网大数据中心代理购电预测项目")
        with xm2:
            # 右侧：时间对齐
            st.write("")  # 稍微下移一点对齐标题
            st.write("`2023.09 - 2023.12`")
        # 在下方放置详情折叠框，它会自动对齐宽度
        with st.expander("**工作职责**", expanded=True):
            st.markdown("""
                - 负责预测模型的设计，开发，优化工作
                - 负责与客户沟通需求，需求确认等
                - 负责项目各个阶段的文档编写与汇报
                - 其他相关事宜
            """)

        # 创建分栏
        xm1, xm2 = st.columns([3, 1])
        with xm1:
            # 左侧：大标题
            st.markdown("##### 信通院模型验证平台项目")
        with xm2:
            # 右侧：时间对齐
            st.write("")  # 稍微下移一点对齐标题
            st.write("`2023.09 - 2024.01`")
        # 在下方放置详情折叠框，它会自动对齐宽度
        with st.expander("**工作职责**", expanded=True):
            st.markdown("""
                - 负责分类，聚类，预测，回归算法的验证流程设计与开发
                - 负责与相关人员沟通相关接口、算法逻辑、研发进度、上线、测试等事宜，确保项目高质量按期完成
            """)


st.write("")  # 间距

# 2. 教育背景 (采用更紧凑的并排布局)
st.subheader("🎓 教育背景")

# 联合培养
col_l1, col_l2 = st.columns([3, 1])
with col_l1:
    # st.markdown("**应急管理大学（防灾科技学院）** | 硕士研究生", help="研究方向：机器学习, 灾害信息处理")
    st.markdown(
        '<span class="school-hover" title="湖北省地震局">**中国地震局地震研究所**</span> | 硕士研究生(联合培养)',
        unsafe_allow_html=True, help="研究生培养模式为校外导师联合培养"
    )
    st.caption("**专业**：资源与环境")
with col_l2:
    st.markdown("`2021.07 - 2023.06`")
st.info("📍 **主要研究方向**：机器学习，地球物理，连续重力，信号处理")
with st.expander("**毕业设计**"):
    # 标题部分：居中并加粗
    st.markdown("""
            <div style="text-align: left;">
                <p style="color: #1E1E1E;">基于时间序列与深度学习的连续重力数据清洗</p>
            </div>
        """, unsafe_allow_html=True)

    # 正文部分：首行缩进 2em (2个中文字符宽度)，设置行高 1.6 倍方便阅读
    st.markdown("""
            <p style="text-indent: 2em; line-height: 1.6; text-align: justify;">
                使用时间序列分析分析连续重力的平稳性与随机性，利用离散小波变换进行连续重力处理，
                对处理结果分析并进行基于LSTM的连续重力预测建模，最后使用建模模型进行数据异常识别与处理，即数据清洗。
            </p>
            <p style="text-indent: 2em; line-height: 1.6; text-align: justify;">
                李啸春.(2023).基于时间序列与深度学习的连续重力数据清洗(硕士学位论文,防灾科技学院).
                硕士https://doi.org/10.27899/d.cnki.gfzkj.2023.000066.
            </p>
            
        """, unsafe_allow_html=True)
with st.expander("**科研项目**"):
    st.write("""
      - 基于机器学习对重力数据模型的应用研究&nbsp;|&nbsp;局所项目
      - 关于重力背景噪声与云图的数据自动化处理的应用研究&nbsp;|&nbsp;局所项目
      - 一带一路地震监测台网项目重力台分项
    """)
with st.expander("**软著 | 论文**"):
    st.write("""
      - 基于LSTM的连续重力异常数据自动处理软件 V1.0
      - 周浩,彭益坤,苟家宁,李啸春 & 魏工哲.(2022).高精度地图难度系数量化方法及系统研究.海洋测绘,42(03),72-76.
    """)

st.divider()

# 硕士
col_m1, col_m2 = st.columns([3, 1])
with col_m1:
    # st.markdown("**应急管理大学（防灾科技学院）** | 硕士研究生", help="研究方向：机器学习, 灾害信息处理")
    st.markdown(
        '<span class="school-hover" title="防灾科技学院">**应急管理大学**</span> | 硕士研究生',
        unsafe_allow_html=True, help="2025年防灾科技学院更名为应急管理大学"
    )
    st.caption("**专业**：资源与环境")
with col_m2:
    st.markdown("`2020.09 - 2021.06`")
st.info("💡 **主要研究方向**：机器学习，灾害信息处理")
st.info("💡 **主修课程**：人工神经网络，时间序列分析，软件体系结构，大数据技术，目标检测与行为识别，高等工程数学，英语等")

st.divider()

# 本科
col_b1, col_b2 = st.columns([3, 1])
with col_b1:
    st.markdown("**华北理工大学轻工学院** | 本科",)
    st.caption("**专业**：计算机科学与技术")
with col_b2:
    st.markdown("`2016.09 - 2020.06`")


st.info("  - **毕业设计**：《基于PHP的体育赛事管理系统的设计与开发》")
st.info("  - **主修课程**：Web 网站设计与开发，JavaScript 脚本，C 语言，数据结构，操作系统，数据库原理，C#程序设计，Java 网络编程，平面设计")
st.divider()

# --- 项目展示 ---
# st.header("🚀 精选项目")
# p_col1, p_col2 = st.columns(2)
#
# with p_col1:
#     st.subheader("智能数据看板")
#     #
#     st.write("基于 Streamlit 和 Pandas 开发的自动化报表系统。")
#     st.button("查看 Demo", key="demo1")
#
# with p_col2:
#     st.subheader("分布式爬虫")
#     st.write("使用 Scrapy-Redis 构建的高并发抓取框架。")
#     st.button("查看源码", key="code1")

# --- 页脚 ---
st.caption("Made with &nbsp; ❤ &nbsp; using Streamlit | © 2026 User LEE")