import streamlit as st
import pandas as pd
import datetime
import base64
import requests
import json

# ==========================================
# 1. 全局配置：开启全屏宽屏模式
# ==========================================
st.set_page_config(page_title="Smart Finance", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# 2. 现代 SaaS 极简高定 UI 注入
# ==========================================
modern_ui_style = """
<style>
    /* 隐藏系统默认元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 全局高级灰底色 */
    .stApp {background-color: #F4F7FE;}
    
    /* 核心卡片化设计 */
    .css-1r6slb0, .css-18e3th9, .css-1d391kg {
        background-color: #FFFFFF;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0px 4px 20px rgba(0, 0, 0, 0.04);
        border: none;
    }
    
    /* 侧边栏样式优化 */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }
    
    /* 按钮高定质感 (现代紫) */
    .stButton>button {
        background-color: #5B58EB; 
        color: #ffffff; 
        border: none;
        border-radius: 10px; 
        width: 100%; 
        font-size: 16px;
        font-weight: 600;
        padding: 12px 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .stButton>button:hover {
        background-color: #4A47D1; 
        color: #ffffff;
        box-shadow: 0 8px 16px rgba(91, 88, 235, 0.3);
        transform: translateY(-2px);
    }
    
    /* 数据表与输入框纯净去线 */
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        border-radius: 8px !important;
        border: 1px solid #E2E8F0 !important;
        background-color: #F8FAFC !important;
    }
    
    /* 自定义 KPI 卡片 HTML 样式 */
    .kpi-card {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0px 4px 20px rgba(0, 0, 0, 0.04);
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .kpi-title {
        color: #718096;
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .kpi-value {
        color: #1A202C;
        font-size: 32px;
        font-weight: 700;
    }
    .kpi-value.expense { color: #E53E3E; }
    .kpi-value.income { color: #38A169; }
</style>
"""
st.markdown(modern_ui_style, unsafe_allow_html=True)

# ==========================================
# 3. 云端数据引擎
# ==========================================
TOKEN = st.secrets["GITHUB_TOKEN"]
REPO = "1452443771yu-ux/my-finance-app" 
FILE_PATH = "records.csv"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json"
}

@st.cache_data(ttl=5) # 增加短时缓存，提升加载丝滑度
def load_data():
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        file_info = response.json()
        file_content = base64.b64decode(file_info["content"]).decode("utf-8")
        from io import StringIO
        df = pd.read_csv(StringIO(file_content))
        df['日期'] = pd.to_datetime(df['日期']).dt.strftime('%Y-%m-%d')
        return df
    return pd.DataFrame(columns=["日期", "收支", "分类", "金额", "备注"])

def save_data(df):
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    get_resp = requests.get(url, headers=HEADERS)
    sha = get_resp.json().get("sha") if get_resp.status_code == 200 else None
    
    csv_string = df.to_csv(index=False)
    content_encoded = base64.b64encode(csv_string.encode("utf-8")).decode("utf-8")
    
    data = {"message": "Update financial records", "content": content_encoded}
    if sha: data["sha"] = sha
        
    put_resp = requests.put(url, headers=HEADERS, data=json.dumps(data))
    return put_resp.status_code in [200, 201]

df = load_data()

# ==========================================
# 4. 侧边栏：快捷操作中枢
# ==========================================
with st.sidebar:
    st.markdown("## ⚡️ 快捷记账")
    st.markdown("---")
    
    with st.form("quick_record", clear_on_submit=True):
        date = st.date_input("🗓️ 交易日期", datetime.date.today())
        type_ = st.selectbox("🔄 收支类型", ["支出", "收入"])
        amount = st.number_input("💰 金额 (¥)", min_value=0.0, format="%.2f", step=10.0)
        
        # 允许用户直接输入新分类，打破下拉框限制
        existing_categories = df['分类'].unique().tolist() if not df.empty else ["日常餐饮", "交通出行", "商业预付", "尾款收入"]
        category = st.selectbox("📂 分类", existing_categories)
        new_category = st.text_input("✨ 或输入新分类 (选填)")
        final_category = new_category if new_category else category
            
        note = st.text_input("📝 备注说明 (选填)")
        
        submitted = st.form_submit_button("＋ 添 加 记 录")
        if submitted and amount > 0:
            new_record = pd.DataFrame({
                "日期": [date.strftime("%Y-%m-%d")],
                "收支": [type_],
                "分类": [final_category],
                "金额": [amount],
                "备注": [note]
            })
            df = pd.concat([new_record, df], ignore_index=True)
            if save_data(df):
                st.success("🎉 记录已保存至云端")
                st.rerun()

# ==========================================
# 5. 主视图：SaaS 仪表盘
# ==========================================
st.markdown("<h1>✨ 智能财务看板 <span style='font-size:18px;color:#718096;'>Smart Finances, Better Business</span></h1>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

if not df.empty:
    df['金额'] = pd.to_numeric(df['金额'])
    df['日期'] = pd.to_datetime(df['日期'])
    
    # 核心指标计算
    total_expense = df[df["收支"] == "支出"]["金额"].sum()
    total_income = df[df["收支"] == "收入"]["金额"].sum()
    balance = total_income - total_expense
    
    # --- 第一排：KPI 卡片 ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">📉 总支出 (Expense)</div>
            <div class="kpi-value expense">¥ {total_expense:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">📈 总收入 (Income)</div>
            <div class="kpi-value income">¥ {total_income:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">🏦 结余 (Balance)</div>
            <div class="kpi-value">¥ {balance:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- 第二排：可视化图表 & 数据管理 ---
    chart_col, data_col = st.columns([1, 1.2])
    
    with chart_col:
        st.markdown("### 📊 近期收支走势")
        # 聚合每日数据生成走势图
        trend_df = df.groupby(['日期', '收支'])['金额'].sum().unstack().fillna(0)
        st.bar_chart(trend_df, color=["#E53E3E", "#5B58EB"]) # 支出红色，收入紫色

    with data_col:
        st.markdown("### 🗂️ 账单管理 (支持直接编辑/删除)")
        
        # 使用 Streamlit 强大的 data_editor 实现自由删改
        edited_df = st.data_editor(
            df.sort_values(by="日期", ascending=False),
            use_container_width=True,
            num_rows="dynamic", # 允许用户动态删除或添加行
            hide_index=True,
            column_config={
                "日期": st.column_config.DateColumn("日期", format="YYYY-MM-DD"),
                "金额": st.column_config.NumberColumn("金额", format="¥ %.2f"),
                "收支": st.column_config.SelectboxColumn("收支", options=["支出", "收入"])
            }
        )
        
        # 比对数据是否发生修改，提供保存按钮
        if not edited_df.equals(df):
            if st.button("💾 保存数据修改至云端"):
                # 修复时间格式后保存
                edited_df['日期'] = pd.to_datetime(edited_df['日期']).dt.strftime('%Y-%m-%d')
                if save_data(edited_df):
                    st.success("✅ 数据已完美同步！")
                    st.rerun()

else:
    st.info("👋 欢迎来到全新的智能财务台。请在左侧栏录入你的第一笔账单。")
