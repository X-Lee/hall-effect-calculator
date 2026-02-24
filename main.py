import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# 页面配置
st.set_page_config(page_title="霍尔效应双参数计算器", layout="wide")

st.title("🧪 霍尔效应参数计算与可视化")
st.markdown("""
本工具支持输入两个霍尔系数分量 $R_{H1}$ 和 $R_{H2}$，自动计算其均值 ${R}_H$，并完成后续物理量推导。
""")

# --- 侧边栏：输入参数 ---
st.sidebar.header("1. 实验参数输入")

# 几何尺寸
st.sidebar.subheader("样本尺寸 (单位: mm)")
d_mm = st.sidebar.number_input("厚度 d", value=0.500, format="%.3f")
b_mm = st.sidebar.number_input("宽度 b", value=2.000, format="%.3f")
L_mm = st.sidebar.number_input("长度 L", value=5.000, format="%.3f")

# 测量参数
st.sidebar.subheader("电磁参数")
alpha = st.sidebar.number_input("比例系数 α (T/A)", value=0.1250)
I_M = st.sidebar.number_input("励磁电流 I_M (A)", value=0.600)
I_S = st.sidebar.number_input("工作电流 I_S (A)", value=0.010)
U_sigma = st.sidebar.number_input("电导电压 U_σ (V)", value=0.150)

# 转换常数 k1 和 k2
st.sidebar.subheader("转换常数 (由测量电压计算)")
k1 = st.sidebar.number_input("常数 k1", value=0.0050, format="%.6f")
k2 = st.sidebar.number_input("常数 k2", value=0.0052, format="%.6f")

# --- 单位换算 (SI 标准单位) ---
d = d_mm * 1e-3
b = b_mm * 1e-3
L = L_mm * 1e-3
q = 1.602e-19 # 元电荷

# --- 核心计算逻辑 ---

# 1. 计算 RH1 和 RH2
rh1 = (k1 * d) / (I_M * alpha)
rh2 = (k2 * d) / (I_M * alpha)

# 2. 计算均值 RH
rh_avg = (rh1 + rh2) / 2

# 3. 计算载流子浓度 n
n = 1 / (abs(rh_avg) * q)

# 4. 计算电导率 sigma
sigma = (I_S * L) / (U_sigma * b * d)

# 5. 计算迁移率 mu
mu = abs(rh_avg) * sigma

# --- 页面显示 ---

st.header("2. 公式推导与计算路径")

# 第一排：RH1, RH2 和 均值
col1, col2, col3 = st.columns(3)
with col1:
    st.info("**分量 $R_{H1}$**")
    st.latex(r"R_{H1} = \frac{k_1 d}{I_M \alpha}")
    st.metric("R_{H1}", f"{rh1:.4e} m³/C")

with col2:
    st.info("**分量 $R_{H2}$**")
    st.latex(r"R_{H2} = \frac{k_2 d}{I_S \alpha}") # 依据图片2
    st.metric("R_{H2}", f"{rh2:.4e} m³/C")

with col3:
    st.success("**均值 ${R}_H$**")
    st.latex(r"\bar{R}_H = \frac{R_{H1} + R_{H2}}{2}")
    st.metric("Average R_H", f"{rh_avg:.4e} m³/C")

st.divider()

# 第二排：n, sigma, mu
col4, col5, col6 = st.columns(3)
with col4:
    st.markdown("### 载流子浓度 $n$")
    st.latex(r"n = \frac{1}{|\bar{R}_H|q}")
    st.metric("n", f"{n:.4e} m⁻³")

with col5:
    st.markdown("### 电导率 $\sigma$")
    st.latex(r"\sigma = \frac{I_S L}{U_\sigma b d}")
    st.metric("σ", f"{sigma:.4e} S/m")

with col6:
    st.markdown("### 迁移率 $\mu$")
    st.latex(r"\mu = |\bar{R}_H|\sigma")
    st.metric("μ", f"{mu:.4e} m²/(V·s)")

# --- 可视化 ---
st.header("3. 计算结果可视化")

# 构建汇总数据表
summary_data = {
    "参数": ["霍尔系数1", "霍尔系数2", "平均霍尔系数", "载流子浓度", "电导率", "迁移率"],
    "数值": [rh1, rh2, rh_avg, n, sigma, mu],
    "单位": ["m³/C", "m³/C", "m³/C", "m⁻³", "S/m", "m²/(V·s)"]
}
df_res = pd.DataFrame(summary_data)
st.table(df_res)

# 模拟分析图表：RH1 与 RH2 的偏差对最终迁移率的影响
# st.subheader("参数偏差分析")
# offset_range = np.linspace(0.8, 1.2, 50) # 偏差系数
# mu_sim = [abs(((rh1 * factor + rh2) / 2)) * sigma for factor in offset_range]
#
# fig = px.line(
#     x=offset_range * rh1,
#     y=mu_sim,
#     labels={'x': '变动的 R_{H1} 数值', 'y': '最终计算的迁移率 μ'},
#     title="当 R_{H1} 波动时对迁移率结果的影响曲线"
# )
# st.plotly_chart(fig, use_container_width=True)