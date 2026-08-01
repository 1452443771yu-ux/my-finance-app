import streamlit as st
import pandas as pd
import datetime
import base64
import requests
import json

# 全局页面配置：自适应与极简布局
st.set_page_config(page_title="青春记账台", layout="centered", initial_sidebar_state="collapsed")

# 青春绿色、高对比度、清晰明了的专属 UI 样式
youthful_green_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            
            .stApp {background-color: #F7FBFC; color: #111111;}
            h1, h2, h3, p, label {color: #111111 !important;}
            
            /* 青春绿沉浸式按钮 */
            .stButton>button {
                background-color: #00C853; 
                color: #ffffff; 
                border: none;
                border-radius: 8px; 
                width: 100%; 
                font-size: 16px;
                font-weight: 600;
                padding: 10px 0;
                transition: all 0.3s ease;
            }
            .stButton>button:hover {
                background-color: #00E676; 
                color: #ffffff;
                box-shadow: 0 4px 12px rgba(0, 200, 83, 0.3);
            }
            
            /* 输入框纯白背景、精致灰色边框 */
            .stTextInput>div>div>input, .stNumberInput>div>div>input {
                background-color: #ffffff !important;
                color: #111111 !important;
                border: 1px solid #E0E0E0 !important;
                border-radius: 6px !important;
            }
            
            /* 下拉菜单与日期选择器适配 */
            div[data-baseweb="select"] > div, div[data-baseweb="input"] > div {
                background-color: #ffffff !important;
                border: 1px solid #E0E0E0 !important;
                border-radius: 6px !important;
            }
            </style>
            """
st.markdown(youthful_green_style, unsafe_allow_html=True)

st.title("🌱 青春记账台")

# GitHub 云端数据持久化配置（直接读写你的私有文件）
TOKEN = st.secrets["GITHUB_TOKEN"]
REPO = "1452443771yu-ux/my-finance-app"  # 你的仓库名
FILE_PATH = "records.csv"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json"
}

# 从 GitHub 实时加载数据
def load_data_from_github():
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        file_info = response.json()
        file_content = base64.b64decode(file_info["content"]).decode("utf-8")
        from io import StringIO
        return pd.read_csv(StringIO(file_content))
    else:
        # 如果文件暂不存在，初始化一个空账本
        return pd.DataFrame(columns=["日期", "收支", "分类", "金额", "备注"])

# 将新账单实时加密写回 GitHub 仓库
def save_data_to_github(df):
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    get_resp = requests.get(url, headers=HEADERS)
    sha = get_resp.json().get("sha") if get_resp.status_code == 200 else None
    
    csv_string = df.to_csv(index=False)
    content_encoded = base64.b64encode(csv_string.encode("utf-8")).decode("utf-8")
    
    data = {
        "message": "Auto-save financial records",
        "content": content_encoded,
    }
    if sha:
        data["sha"] = sha
        
    put_resp = requests.put(url, headers=HEADERS, data=json.dumps(data))
    return put_resp.status_code in [200, 201]

df = load_data_from_github()

# --- 录入区块 ---
st.markdown("### 📝 快速录入")
with st.form("record_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("日期", datetime.date.today())
        type_ = st.radio("收支", ["支出", "收入"], horizontal=True)
    with col2:
        amount = st.number_input("金额 (¥)", min_value=0.0, format="%.2f", step=10.0)
        category = st.selectbox("分类", ["日常餐饮", "交通出行", "软件订阅", "美术与道具", "商业项目预付", "尾款收入", "其他"])
        
    note = st.text_input("备注说明 (选填)")
    
    submitted = st.form_submit_button("保 存 记 录")
    if submitted:
        if amount > 0:
            new_record = pd.DataFrame({
                "日期": [date.strftime("%Y-%m-%d")],
                "收支": [type_],
                "分类": [category],
                "金额": [amount],
                "备注": [note]
            })
            df = pd.concat([new_record, df], ignore_index=True)
            
            # 自动保存到云端
            if save_data_to_github(df):
                st.success("✨ 记账成功，已安全同步至云端！")
                st.rerun()
            else:
                st.error("⚠️ 同步至云端失败，请检查 Token 权限配置。")
        else:
            st.error("⚠️ 请输入有效的金额")

# --- 展示区块 ---
st.markdown("---")
st.markdown("### 📊 财务明细")

if not df.empty:
    df['金额'] = pd.to_numeric(df['金额'])
    total_expense = df[df["收支"] == "支出"]["金额"].sum()
    total_income = df[df["收支"] == "收入"]["金额"].sum()
    
    # 财务数据看板
    st.info(f"**总支出:** ¥ {total_expense:.2f} ｜ **总收入:** ¥ {total_income:.2f}")
    
    # 高清表格展示
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("暂无数据，你的第一笔账单将显示在这里。")
