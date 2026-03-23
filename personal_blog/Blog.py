import streamlit as st
from pathlib import Path
import yaml

st.set_page_config(page_title="个人知识博客", layout="wide")

# -----------------------
# 路径
# -----------------------
BASE_DIR = Path(__file__).parent
NOTES_DIR = BASE_DIR / "notes"
NOTES_DIR.mkdir(exist_ok=True)

# -----------------------
# 获取文件（按时间排序）
# -----------------------
def get_files():
    files = list(NOTES_DIR.glob("*.md"))
    files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return files

md_files = get_files()

# -----------------------
# Sidebar：笔记列表
# -----------------------
st.sidebar.title("📄 笔记")

selected_file = st.session_state.get("selected_file")

# 默认选第一个
if not selected_file and md_files:
    selected_file = md_files[0].name
    st.session_state["selected_file"] = selected_file

for f in md_files:
    label = f"👉 {f.name}" if f.name == selected_file else f.name
    if st.sidebar.button(label, key=f"file_{f.name}"):
        st.session_state["selected_file"] = f.name
        st.rerun()

# -----------------------
# 上传
# -----------------------
st.sidebar.markdown("---")
st.sidebar.title("📤 上传")

uploaded_file = st.sidebar.file_uploader("上传 Markdown", type=["md"])

if uploaded_file:
    filename = uploaded_file.name
    filepath = NOTES_DIR / filename

    with open(filepath, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.sidebar.success(f"✅ 已保存: {filename}")
    st.rerun()

# -----------------------
# 删除
# -----------------------
selected_file = st.session_state.get("selected_file")

if selected_file:
    st.sidebar.markdown("---")
    if st.sidebar.button("🗑 删除当前笔记"):
        file_path = NOTES_DIR / selected_file
        if file_path.exists():
            file_path.unlink()
            st.session_state.pop("selected_file", None)
            st.sidebar.success("已删除")
            st.rerun()

# -----------------------
# 主区域展示
# -----------------------
selected_file = st.session_state.get("selected_file")

if selected_file:
    file_path = NOTES_DIR / selected_file

    if file_path.exists():
        content = file_path.read_text(encoding="utf-8")

        # YAML 解析
        metadata = {}
        if content.startswith("---"):
            try:
                parts = content.split("---", 2)
                metadata = yaml.safe_load(parts[1])
                content = parts[2]
            except:
                pass

        # ⭐ 统一显示标题
        display_title = "User Notes"
        st.markdown(f"# {display_title}")

        # 显示标签
        if metadata.get("tags"):
            tags = " | ".join([f"`{t}`" for t in metadata["tags"]])
            st.markdown(tags)

        st.markdown("---")
        st.markdown(content)