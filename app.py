import streamlit as st
import pandas as pd
import datetime
import base64
import requests
import json

# 1. 全局配置：强制全屏宽屏模式
st.set_page_config(page_title="Finnova 智能财务", layout="wide", initial_sidebar_state="expanded")

# 2. 极简高定 UI 样式 (彻底消除纯黑，引入高对比度蓝灰与现代紫)
saas_css = """
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 整体背景：极浅的蓝灰，拉开空间层次 */
    .stApp {background-color: #F8FAFC !important;}
    
    /* 强制所有默认文本为高级深蓝灰，拒绝死黑 */
    .stMarkdown, p, h1, h2, h3, h4, h5, h6, span, label {color: #1E293B !important;}
    
    /* 侧边栏纯白+深色文字 */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0 !important;
    }
    
    /* 卡片化指标设计 */
    .kpi-card {
        background-color: #FFFFFF;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03), 0 2px 4px -1px rgba(0, 0, 0, 0.02);
        border: 1px solid #F1F5F9;
        display: flex;
        flex-direction: column;
    }
    .kpi-title {
        color: #64748B;
        font-size: 0.9rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
    }
    .kpi-value {
        font-size: 2.2rem;
        font-weight: 700;
    }
    .color-expense { color: #EF4444; } /* 年轻活力的西瓜红 */
    .color-income { color: #10B981; }  /* 清新的薄荷绿 */
    .color-balance { color: #6366F1; } /* 现代 SaaS 紫 */

    /* 统一输入框风格 */
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        background-color: #F1F5F9 !important;
        border: 1px solid #CBD5E1 !important;
        color: #1E293B !important;
        border-radius: 8px !important;
    }
    
    /* 按钮：现代紫高定质感 */
    .stButton>button {
        background-color: #6366F1 !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 10px 0 !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        background-color: #4F46E5 !important;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3) !important;
        transform: translateY(-1px);
    }
</style>
"""
st.markdown(saas_css, unsafe_allow_html=True)

# 3. GitHub 数据引擎
TOKEN = st.secrets["GITHUB_TOKEN"]
REPO = "1452443771yu-ux/my-finance-app" 
FILE_PATH = "records.csv"
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github+json"}

@st.cache_data(ttl=2) 
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

# 4. 侧边栏：操作区
with st.sidebar:
    st.markdown("### ⚡️ 快速记账")
    st.markdown("<br>", unsafe_allow_html=True)
    with st.form("quick_record", clear_on_submit=True):
        date = st.date_input("📅 交易日期", datetime.date.today())
        type_ = st.selectbox("🔄 类型", ["支出", "收入"])
        amount = st.number_input("💵 金额 (¥)", min_value=0.0, format="%.2f", step=100.0)
        
        # 智能分类：自动读取历史分类，支持新增
        existing_cats = df['分类'].unique().tolist() if not df.empty else ["🍔 日常餐饮", "🚗 交通出行", "🎬 美术与道具"]
        category = st.selectbox("📂 选择分类", existing_cats)
        new_category = st.text_input("✨ 或输入新分类名称")
        final_category = new_category if new_category else category
            
        note = st.text_input("📝 备注 (如：打车去影棚)")
        submitted = st.form_submit_button("＋ 保 存 记 录")
        
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
                st.success("🎉 同步成功！")
                st.rerun()

# 5. 主视图：数据看板
st.markdown("<h1>✨ 智能财务大盘 <span style='font-size:16px;color:#64748B;font-weight:normal;'>Smart Finances, Better Control</span></h1>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

if not df.empty:
    df['金额'] = pd.to_numeric(df['金额'])
    df['日期'] = pd.to_datetime(df['日期'])
    
    # 核心指标
    total_expense = df[df["收支"] == "支出"]["金额"].sum()
    total_income = df[df["收支"] == "收入"]["金额"].sum()
    balance = total_income - total_expense
    
    # 指标卡片排版
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-title">📉 总支出 (Overdue)</div><div class="kpi-value color-expense">¥ {total_expense:,.2f}</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-title">📈 总收入 (Paid)</div><div class="kpi-value color-income">¥ {total_income:,.2f}</div></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-title">🏦 净结余 (Available)</div><div class="kpi-value color-balance">¥ {balance:,.2f}</div></div>""", unsafe_allow_html=True)
        
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # 图表与明细数据区
    col_chart, col_data = st.columns([1, 1.2], gap="large")
    
    with col_chart:
        st.markdown("### 📊 财务走势图")
        # 按月/日切换的统计逻辑
        view_mode = st.radio("查看维度", ["按日统计", "按月统计"], horizontal=True, label_visibility="collapsed")
        
        if view_mode == "按月统计":
            chart_df = df.copy()
            chart_df['月份'] = chart_df['日期'].dt.strftime('%Y-%m')
            trend_df = chart_df.groupby(['月份', '收支'])['金额'].sum().unstack().fillna(0)
        else:
            trend_df = df.groupby([df['日期'].dt.strftime('%m-%d'), '收支'])['金额'].sum().unstack().fillna(0)
            
        # 使用 SaaS 质感色彩渲染柱状图
        st.bar_chart(trend_df, color=["#6366F1", "#EF4444"]) # 收入紫，支出红

    with col_data:
        st.markdown("### 🗂️ 账单明细 (支持选中删除/双击修改)")
        # 强大的可视化编辑表格
        edited_df = st.data_editor(
            df.sort_values(by="日期", ascending=False),
            use_container_width=True,
            num_rows="dynamic",
            hide_index=True,
            column_config={
                "日期": st.column_config.DateColumn("📅 日期", format="YYYY-MM-DD"),
                "金额": st.column_config.NumberColumn("💵 金额", format="¥ %.2f"),
                "收支": st.column_config.SelectboxColumn("🔄 收支", options=["支出", "收入"]),
                "分类": st.column_config.TextColumn("📂 分类"),
                "备注": st.column_config.TextColumn("📝 备注")
            }
        )
        
        # 侦测修改并保存
        if not edited_df.equals(df):
            st.info("👆 检测到数据变动，请点击下方保存")
            if st.button("💾 将修改同步至云端"):
                edited_df['日期'] = pd.to_datetime(edited_df['日期']).dt.strftime('%Y-%m-%d')
                if save_data(edited_df):
                    st.success("✅ 数据已完美同步！")
                    st.rerun()
else:
    st.info("👋 欢迎来到全新的智能财务台。请在左侧录入第一笔账单。")
