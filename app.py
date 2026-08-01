import streamlit as st
import pandas as pd
import datetime
import base64
import requests
import json

# 全局页面配置：自适应与极简布局
st.set_page_config(page_title="极简记账", page_icon="💸", layout="centered", initial_sidebar_state="collapsed")

# 深度定制的紫罗兰极简 SaaS 风格 CSS
modern_saas_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            
            /* 全局背景设为极浅的冷紫色，突出白色卡片 */
            .stApp {background-color: #F4F2FF; color: #111111;}
            h1, h2, h3, p, label {color: #111111 !important;}
            
            /* 极简纯白卡片风格 */
            .css-1r6slb0, .css-18e3th9 {
                background-color: #ffffff;
                border-radius: 16px;
                padding: 20px;
                box-shadow: 0 8px 24px rgba(108, 93, 211, 0.05);
                border: none;
            }
            
            /* 现代紫罗兰主按钮 */
            .stButton>button {
                background-color: #6C5DD3; 
                color: #ffffff; 
                border: none;
                border-radius: 10px; 
                width: 100%; 
                font-size: 16px;
                font-weight: bold;
                padding: 12px 0;
                transition: all 0.3s ease;
                box-shadow: 0 4px 12px rgba(108, 93, 211, 0.2);
            }
            .stButton>button:hover {
                background-color: #594AC3; 
                color: #ffffff;
                transform: translateY(-2px);
                box-shadow: 0 6px 16px rgba(108, 93, 211, 0.3);
            }
            
            /* 输入框纯白背景、无多余边框、底部极细线条 */
            .stTextInput>div>div>input, .stNumberInput>div>div>input {
                background-color: #ffffff !important;
                color: #111111 !important;
                border: 1px solid #EBE9F1 !important;
                border-radius: 8px !important;
            }
            
            /* 修正下拉菜单与日期选择器 */
            div[data-baseweb="select"] > div, div[data-baseweb="input"] > div {
                background-color: #ffffff !important;
                border: 1px solid #EBE9F1 !important;
                border-radius: 8px !important;
            }
            
            /* 数据看板的大数字高对比度设计 */
            .metric-card {
                background-color: #ffffff;
                border-radius: 12px;
                padding: 15px;
                text-align: center;
                box-shadow: 0 4px 12px rgba(0,0,0,0.03);
                border: 1px solid #F0F0F0;
            }
            </style>
            """
st.markdown(modern_saas_style, unsafe_allow_html=True)

st.markdown("## 💸 极简财务看板")

# --- GitHub 云端数据持久化配置 ---
TOKEN = st.secrets["GITHUB_TOKEN"]
REPO = "1452443771yu-ux/my-finance-app"  # 你的仓库名
FILE_PATH = "records.csv"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json"
}

@st.cache_data(ttl=5) # 短暂缓存，加快刷新速度
def load_data_from_github():
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        file_info = response.json()
        file_content = base64.b64decode(file_info["content"]).decode("utf-8")
        from io import StringIO
        df = pd.read_csv(StringIO(file_content))
        # 确保金额列是数字类型
        df['金额'] = pd.to_numeric(df['金额'], errors='coerce').fillna(0.0)
        return df
    else:
        return pd.DataFrame(columns=["日期", "收支", "分类", "金额", "备注"])

def save_data_to_github(df):
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    get_resp = requests.get(url, headers=HEADERS)
    sha = get_resp.json().get("sha") if get_resp.status_code == 200 else None
    
    csv_string = df.to_csv(index=False)
    content_encoded = base64.b64encode(csv_string.encode("utf-8")).decode("utf-8")
    
    data = {
        "message": "Update financial records via UI",
        "content": content_encoded,
    }
    if sha:
        data["sha"] = sha
        
    put_resp = requests.put(url, headers=HEADERS, data=json.dumps(data))
    if put_resp.status_code in [200, 201]:
        load_data_from_github.clear() # 清除缓存，强制拉取最新数据
        return True
    return False

df = load_data_from_github()

# --- 顶层数据看板 (高对比度视觉) ---
if not df.empty:
    total_expense = df[df["收支"] == "🔴 支出"]["金额"].sum()
    total_income = df[df["收支"] == "🟢 收入"]["金额"].sum()
    balance = total_income - total_expense
else:
    total_expense, total_income, balance = 0.0, 0.0, 0.0

col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
    st.markdown(f"<div class='metric-card'><p style='color:#888; font-size:14px; margin:0;'>🔴 总支出</p><h3 style='margin:0; color:#FF4B4B;'>¥ {total_expense:.2f}</h3></div>", unsafe_allow_html=True)
with col_m2:
    st.markdown(f"<div class='metric-card'><p style='color:#888; font-size:14px; margin:0;'>🟢 总收入</p><h3 style='margin:0; color:#00C853;'>¥ {total_income:.2f}</h3></div>", unsafe_allow_html=True)
with col_m3:
    st.markdown(f"<div class='metric-card'><p style='color:#888; font-size:14px; margin:0;'>💳 净结余</p><h3 style='margin:0; color:#6C5DD3;'>¥ {balance:.2f}</h3></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- 录入区块 ---
st.markdown("### ✍️ 新增记录")
with st.container():
    with st.form("record_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("📅 日期", datetime.date.today())
            type_ = st.radio("🔄 收支类型", ["🔴 支出", "🟢 收入"], horizontal=True)
        with col2:
            amount = st.number_input("💰 金额 (¥)", min_value=0.0, format="%.2f", step=10.0)
            
            # 年轻化的 Emoji 分类
            categories = ["🍔 日常餐饮", "🚗 交通出行", "💻 软件订阅", "🎨 美术与道具", "🛍️ 购物消费", "💼 商业预付", "💸 尾款收入", "✨ 其他"]
            category = st.selectbox("🏷️ 分类", categories)
            
        note = st.text_input("📝 备注说明 (选填)")
        
        submitted = st.form_submit_button("✨ 添 加 记 录")
        if submitted:
            if amount > 0:
                new_record = pd.DataFrame({
                    "日期": [date.strftime("%Y-%m-%d")],
                    "收支": [type_],
                    "分类": [category],
                    "金额": [amount],
                    "备注": [note]
                })
                # 新记录插在最前面
                df = pd.concat([new_record, df], ignore_index=True)
                if save_data_to_github(df):
                    st.success("✅ 记录已安全同步至云端！")
                    st.rerun()
                else:
                    st.error("❌ 同步失败，请检查设置。")
            else:
                st.error("⚠️ 请输入大于 0 的有效金额")

st.markdown("---")

# --- 交互式数据明细（支持修改与删除） ---
st.markdown("### 🗂️ 财务明细 (可直接修改/删除)")
if not df.empty:
    st.info("💡 **操作指南：** 勾选最左侧的选框可以**删除整行**；双击任何一个单元格可以**修改数据**。修改完成后，请务必点击下方的「保存更改」按钮。")
    
    # 核心升级：使用 data_editor 替代 dataframe，开启增删改功能
    edited_df = st.data_editor(
        df,
        num_rows="dynamic", # 允许动态增删行
        use_container_width=True,
        hide_index=False # 保留索引，方便勾选删除
    )
    
    # 仅当数据发生改变时，提供手动同步按钮
    if not edited_df.equals(df):
        if st.button("💾 将上面的修改/删除同步至云端"):
            if save_data_to_github(edited_df):
                st.success("✅ 修改已永久保存！")
                st.rerun()
            else:
                st.error("❌ 保存失败。")
else:
    st.info("📭 暂无数据，你的第一笔账单将显示在这里。")
