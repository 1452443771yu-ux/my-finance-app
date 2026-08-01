import streamlit as st
import pandas as pd
import datetime
import os

# 全局页面配置：极简布局
st.set_page_config(page_title="极简记账", layout="centered", initial_sidebar_state="collapsed")

# 彻底移除顶部导航、底部水印等多余环境元素，维持高对比度纯净背景
hide_st_style = '''
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            /* 使用简单的黑白对比 */
            .stApp {background-color: #ffffff; color: #111111;}
            .stButton>button {border: 1px solid #111111; border-radius: 0px; background-color: #111111; color: #ffffff; width: 100%; font-weight: bold;}
            .stButton>button:hover {background-color: #ffffff; color: #111111;}
            .stTextInput>div>div>input {border-radius: 0px; border: 1px solid #cccccc;}
            </style>
            '''
st.markdown(hide_st_style, unsafe_allow_html=True)

st.title("■ 记账台")

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
st.markdown("### 录入")
with st.form("record_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("日期", datetime.date.today())
        type_ = st.radio("收支", ["支出", "收入"], horizontal=True)
    with col2:
        amount = st.number_input("金额 (¥)", min_value=0.0, format="%.2f", step=10.0)
        category = st.selectbox("分类", ["交通出行", "软件订阅", "美术与道具", "日常餐饮", "商业预付款", "尾款收入", "其他"])
        
    note = st.text_input("备注 (选填)")
    
    submitted = st.form_submit_button("保 存")
    if submitted:
        if amount > 0:
            new_record = pd.DataFrame({
                "日期": [date.strftime("%Y-%m-%d")],
                "收支": [type_],
                "分类": [category],
                "金额": [amount],
                "备注": [note]
            })
            df = pd.concat([new_record, df], ignore_index=True) # 新记录放在最前
            save_data(df)
            st.success("已记录")
            st.rerun()
        else:
            st.error("请输入有效的金额")

# --- 展示区块 ---
st.markdown("---")
st.markdown("### 明细")

if not df.empty:
    # 统计核心数据
    df['金额'] = pd.to_numeric(df['金额'])
    total_expense = df[df["收支"] == "支出"]["金额"].sum()
    total_income = df[df["收支"] == "收入"]["金额"].sum()
    
    # 简洁的数据汇总板
    st.markdown(f"**总支出:** ¥ {total_expense:.2f} &nbsp;&nbsp;&nbsp; **总收入:** ¥ {total_income:.2f}")
    
    # 无边框极简表格展示
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("暂无数据，你的第一笔账单将显示在这里。")
