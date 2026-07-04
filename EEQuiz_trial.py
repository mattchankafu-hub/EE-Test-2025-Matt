import streamlit as st
import csv
import io

# ================= 1. 頁面基本設定 =================
st.set_page_config(
    page_title="電工模擬試題練習系統",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ================= 2. 狀態管理 (Session State) =================
# 在網頁中，必須使用 session_state 來記住使用者的進度與分數
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

# ================= 3. 側邊欄：設定與題庫載入 =================
st.sidebar.title("⚙️ 題庫設定")
uploaded_file = st.sidebar.file_uploader("上傳你的 CSV 題庫檔案", type=["csv"])

if uploaded_file is not None:
    try:
        # 讀取上傳的 CSV 檔案
        content = uploaded_file.getvalue().decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(content))
        st.session_state.all_questions = list(reader)
        st.sidebar.success(f"✅ 成功載入 {len(st.session_state.all_questions)} 條題目！")
    except Exception as e:
        st.sidebar.error(f"讀取失敗：{e}。請確認 CSV 格式。")

# 如果題庫已載入，顯示題組選擇
if st.session_state.all_questions:
    total_q = min(len(st.session_state.all_questions), 400)
    
    # 產生區間列表 (1-50, 51-100...)
    ranges = []
    for i in range(0, total_q, 50):
        start = i + 1
        end = min(i + 50, total_q)
        ranges.append(f"{start}-{end}")
        
    selected_range = st.sidebar.selectbox("選擇要練習的題組：", ranges)
    
    # 重新開始測驗的按鈕
    if st.sidebar.button("🚀 開始 / 重新測驗", use_container_width=True, type="primary"):
        start_idx, end_idx = map(int, selected_range.split("-"))
        st.session_state.current_questions = st.session_state.all_questions[start_idx-1 : end_idx]
        st.session_state.current_index = 0
        st.session_state.score = 0
        st.session_state.user_answers = []
        st.session_state.quiz_active = True

# ================= 4. 答題邏輯 =================
def submit_answer(user_choice):
    """處理使用者的選擇並進入下一題"""
    q_data = st.session_state.current_questions[st.session_state.current_index]
    correct_answer = q_data['答案'].strip().upper()
    
    is_correct = (user_choice == correct_answer)
    if is_correct:
        st.session_state.score += 1
        
    # 記錄這題的結果
    st.session_state.user_answers.append({
        "q_num": q_data['題號'],
        "is_correct": is_correct,
        "user_choice": user_choice,
        "correct_answer": correct_answer
    })
    
    # 題號推進
    st.session_state.current_index += 1

# ================= 5. 主畫面：測驗與成績單 =================
st.title("⚡ 電工模擬試題練習系統")

if not st.session_state.quiz_active:
    if not st.session_state.all_questions:
        st.info("👈 請先從左側邊欄上傳你的 CSV 題庫檔案。")
    else:
        st.info("👈 題庫已載入！請從左側邊欄選擇題組並點擊「開始測驗」。")

elif st.session_state.current_index < len(st.session_state.current_questions):
    # 正在測驗中...
    current_q_count = st.session_state.current_index + 1
    total_q_count = len(st.session_state.current_questions)
    
    # 顯示進度條
    progress_val = st.session_state.current_index / total_q_count
    st.progress(progress_val)
    st.caption(f"進度： {current_q_count} / {total_q_count}")
    
    # 取得目前題目資料
    q_data = st.session_state.current_questions[st.session_state.current_index]
    
    # 顯示題目
    st.markdown(f"### 第 {q_data['題號']} 題")
    st.markdown(f"#### {q_data['題目']}")
    st.write("---")
    
    # 選項按鈕 (為了手機好按，使用全寬按鈕)
    if st.button(f"A. {q_data['選擇A']}", use_container_width=True):
        submit_answer("A")
        st.rerun() # 點擊後重新刷新網頁以顯示下一題
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
    # 該區間測驗結束，顯示成績單
    total_q_count = len(st.session_state.current_questions)
    percentage = (st.session_state.score / total_q_count) * 100
    
    st.progress(1.0) # 進度條全滿
    st.success(f"🎉 **測驗結束！**")
    
    # 顯示大字體分數
    col1, col2 = st.columns(2)
    col1.metric("答對題數", f"{st.session_state.score} / {total_q_count}")
    col2.metric("準確率", f"{percentage:.1f}%")
    
    st.write("---")
    st.subheader("📋 錯題詳細報告")
    
    # 列出所有作答明細
    for item in st.session_state.user_answers:
        if item['is_correct']:
            st.success(f"**第 {item['q_num']} 題：✅ 答對**")
        else:
            # 答錯的題目用紅色的 error 框顯示，並給予對比強烈的提示
            with st.error(f"**第 {item['q_num']} 題：❌ 答錯**"):
                st.write(f"你的選擇： `{item['user_choice']}`")
                st.write(f"**正確答案： `{item['correct_answer']}`**")
                
    st.info("您可以從左側選單選擇其他題組，繼續您的練習！")