import streamlit as st
import pandas as pd
import datetime
import os

# 全局页面配置：强制宽屏和极简布局
st.set_page_config(page_title="极简记账", layout="centered", initial_sidebar_state="collapsed")

# 深度定制的青春极简 CSS 样式
youthful_green_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            
            /* 全局背景设为非常浅的冷灰色，提升高级感与对比度 */
            .stApp {background-color: #F7FBFC; color: #111111;}
            
            /* 标题和文字颜色极度纯粹 */
            h1, h2, h3, p, label {color: #111111 !important;}
            
            /* 青春绿按钮设计：圆角、无边框、鲜亮绿色 */
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
            
            /* 输入框强制白底黑字，浅灰边框，保持视觉明了 */
            .stTextInput>div>div>input, .stNumberInput>div>div>input {
                background-color: #ffffff !important;
                color: #111111 !important;
                border: 1px solid #E0E0E0 !important;
                border-radius: 6px !important;
            }
            
            /* 修复下拉菜单的暗色冲突 */
            div[data-baseweb="select"] > div {
                background-color: #ffffff !important;
                border: 1px solid #E0E0E0 !important;
                border-radius: 6px !important;
            }
            
            /* 日期选择器修正 */
            div[data-baseweb="input"] > div {
                background-color: #ffffff !important;
                border: 1px solid #E0E0E0 !important;
            }
            </style>
            """
st.markdown(youthful_green_style, unsafe_allow_html=True)

st.title("🌱 青春记账台")

DATA_FILE = "records.csv"

# 加载数据
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=["日期", "收支", "分类", "金额", "备注"])

# 保存数据
def save_data(df):
    df.to_csv(DATA_FILE, index=False)

df = load_data()

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
            save_data(df)
            st.success("✨ 记账成功！")
            st.rerun()
        else:
            st.error("⚠️ 请输入有效的金额")

# --- 展示区块 ---
st.markdown("---")
st.markdown("### 📊 财务明细")

if not df.empty:
    df['金额'] = pd.to_numeric(df['金额'])
    total_expense = df[df["收支"] == "支出"]["金额"].sum()
    total_income = df[df["收支"] == "收入"]["金额"].sum()
    
    # 高对比度数据汇总板
    st.info(f"**总支出:** ¥ {total_expense:.2f} ｜ **总收入:** ¥ {total_income:.2f}")
    
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("暂无数据，你的第一笔账单将显示在这里。")
