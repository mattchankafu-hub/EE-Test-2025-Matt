import streamlit as st
import csv
import os

# ================= 1. 頁面基本設定 =================
st.set_page_config(
    page_title="電工模擬試題練習系統",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ================= 2. 狀態管理 (Session State) =================
if 'all_questions' not in st.session_state:
    st.session_state.all_questions = []
if 'current_questions' not in st.session_state:
    st.session_state.current_questions = []
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = []
if 'quiz_active' not in st.session_state:
    st.session_state.quiz_active = False

# ================= 3. 自動讀取 GitHub 上的 CSV =================
# 這裡填寫你在 GitHub 上的 CSV 確切檔名 (注意大小寫和副檔名 .csv)
CSV_FILE_NAME = "EE Quiz CSV-8.csv"

# 如果還沒有載入題庫，程式開啟時自動讀取
if not st.session_state.all_questions:
    if os.path.exists(CSV_FILE_NAME):
        try:
            with open(CSV_FILE_NAME, mode='r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                st.session_state.all_questions = list(reader)
        except Exception as e:
            st.sidebar.error(f"讀取失敗：{e}")
    else:
        st.sidebar.error(f"找不到檔案：{CSV_FILE_NAME}。請確定 CSV 已經上傳到 GitHub，且檔名完全一致。")

# ================= 4. 側邊欄：題組設定 =================
st.sidebar.title("⚙️ 題庫設定")

# 如果題庫已成功載入，顯示題組選擇
if st.session_state.all_questions:
    st.sidebar.success(f"✅ 題庫已自動載入！共 {len(st.session_state.all_questions)} 題。")
    
    total_q = min(len(st.session_state.all_questions), 400)
    
    # 產生區間列表 (1-50, 51-100...)
    ranges = []
    for i in range(0, total_q, 50):
        start = i + 1
        end = min(i + 50, total_q)
        ranges.append(f"{start}-{end}")
        
    selected_range = st.sidebar.selectbox("選擇要練習的題組：", ranges)
    
    # 開始測驗的按鈕
    if st.sidebar.button("🚀 開始 / 重新測驗", use_container_width=True, type="primary"):
        start_idx, end_idx = map(int, selected_range.split("-"))
        st.session_state.current_questions = st.session_state.all_questions[start_idx-1 : end_idx]
        st.session_state.current_index = 0
        st.session_state.score = 0
        st.session_state.user_answers = []
        st.session_state.quiz_active = True

# ================= 5. 答題邏輯 =================
def submit_answer(user_choice):
    q_data = st.session_state.current_questions[st.session_state.current_index]
    correct_answer = q_data['答案'].strip().upper()
    
    is_correct = (user_choice == correct_answer)
    if is_correct:
        st.session_state.score += 1
        
    st.session_state.user_answers.append({
        "q_num": q_data['題號'],
        "is_correct": is_correct,
        "user_choice": user_choice,
        "correct_answer": correct_answer
    })
    
    st.session_state.current_index += 1

# ================= 6. 主畫面：測驗與成績單 =================
st.title("⚡ 電工模擬試題練習系統")

if not st.session_state.quiz_active:
    st.info("👈 題庫已就緒！請從左側邊欄選擇題組並點擊「開始測驗」。")

elif st.session_state.current_index < len(st.session_state.current_questions):
    # 正在測驗中
    current_q_count = st.session_state.current_index + 1
    total_q_count = len(st.session_state.current_questions)
    
    progress_val = st.session_state.current_index / total_q_count
    st.progress(progress_val)
    st.caption(f"進度： {current_q_count} / {total_q_count}")
    
    q_data = st.session_state.current_questions[st.session_state.current_index]
    
    st.markdown(f"### 第 {q_data['題號']} 題")
    st.markdown(f"#### {q_data['題目']}")
    st.write("---")
    
    if st.button(f"A. {q_data['選擇A']}", use_container_width=True):
        submit_answer("A")
        st.rerun()
    if st.button(f"B. {q_data['選擇B']}", use_container_width=True):
        submit_answer("B")
        st.rerun()
    if st.button(f"C. {q_data['選擇C']}", use_container_width=True):
        submit_answer("C")
        st.rerun()
    if st.button(f"D. {q_data['選擇D']}", use_container_width=True):
        submit_answer("D")
        st.rerun()

else:
    # 測驗結束，顯示成績單
    total_q_count = len(st.session_state.current_questions)
    percentage = (st.session_state.score / total_q_count) * 100
    
    st.progress(1.0)
    st.success(f"🎉 **測驗結束！**")
    
    col1, col2 = st.columns(2)
    col1.metric("答對題數", f"{st.session_state.score} / {total_q_count}")
    col2.metric("準確率", f"{percentage:.1f}%")
    
    st.write("---")
    st.subheader("📋 錯題詳細報告")
    
    for item in st.session_state.user_answers:
        if item['is_correct']:
            st.success(f"**第 {item['q_num']} 題：✅ 答對**")
        else:
            with st.error(f"**第 {item['q_num']} 題：❌ 答錯**"):
                st.write(f"你的選擇： `{item['user_choice']}`")
                st.write(f"**正確答案： `{item['correct_answer']}`**")
                
    st.info("您可以從左側選單選擇其他題組，繼續您的練習！")
