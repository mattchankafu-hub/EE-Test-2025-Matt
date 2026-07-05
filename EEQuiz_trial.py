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
if 'answers_dict' not in st.session_state:
    st.session_state.answers_dict = {} 
if 'quiz_active' not in st.session_state:
    st.session_state.quiz_active = False

# ================= 3. 自動讀取 GitHub 上的 CSV =================
CSV_FILE_NAME = "EE Quiz CSV-8.csv"

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

if st.session_state.all_questions:
    st.sidebar.success(f"✅ 題庫已自動載入！共 {len(st.session_state.all_questions)} 題。")
    
    total_q = min(len(st.session_state.all_questions), 400)
    
    ranges = []
    for i in range(0, total_q, 50):
        start = i + 1
        end = min(i + 50, total_q)
        ranges.append(f"{start}-{end}")
        
    selected_range = st.sidebar.selectbox("選擇要練習的題組：", ranges)
    
    if st.sidebar.button("🚀 開始 / 重新測驗", use_container_width=True, type="primary"):
        start_idx, end_idx = map(int, selected_range.split("-"))
        st.session_state.current_questions = st.session_state.all_questions[start_idx-1 : end_idx]
        st.session_state.current_index = 0
        st.session_state.answers_dict = {} 
        st.session_state.quiz_active = True

# ================= 5. 主畫面：測驗與成績單 =================
st.markdown("<h2 style='font-size: 26px; font-weight: bold; margin-bottom: 20px;'>⚡ 電工模擬試題練習系統</h2>", unsafe_allow_html=True)

if not st.session_state.quiz_active:
    st.info("👈 題庫已就緒！請從左側邊欄選擇題組並點擊「開始測驗」。")

elif st.session_state.current_index < len(st.session_state.current_questions):
    # --- 正在測驗中 ---
    current_q_count = st.session_state.current_index + 1
    total_q_count = len(st.session_state.current_questions)
    
    progress_val = st.session_state.current_index / total_q_count
    st.progress(progress_val)
    st.caption(f"進度： {current_q_count} / {total_q_count}")
    
    q_data = st.session_state.current_questions[st.session_state.current_index]
    correct_answer = q_data['答案'].strip().upper()
    options = {
        "A": q_data['選擇A'],
        "B": q_data['選擇B'],
        "C": q_data['選擇C'],
        "D": q_data['選擇D']
    }
    
    st.markdown(f"### 第 {q_data['題號']} 題")
    st.markdown(f"#### {q_data['題目']}")
    st.write("---")
    
    is_answered = st.session_state.current_index in st.session_state.answers_dict
    
    if is_answered:
        # 【已作答狀態】：顯示深色即時顏色回饋
        user_ans = st.session_state.answers_dict[st.session_state.current_index]
        
        for opt_letter, opt_text in options.items():
            if opt_letter == correct_answer:
                # 答對：深綠色背景，白色文字
                bg_color, border_color, text_color, icon = "#2e7d32", "#1b5e20", "#ffffff", "✅"
            elif opt_letter == user_ans and user_ans != correct_answer:
                # 答錯：深紅色背景，白色文字
                bg_color, border_color, text_color, icon = "#d32f2f", "#b71c1c", "#ffffff", "❌"
            else:
                # 未選擇的其他選項：淺灰色背景，深灰色文字 (與原本按鈕相似)
                bg_color, border_color, text_color, icon = "#f0f2f6", "#f0f2f6", "#31333F", "⬜"
                
            # 調整 padding (8px 12px) 和 font-size (15px) 讓大小與預設按鈕一致
            st.markdown(f"""
            <div style="background-color: {bg_color}; border: 1px solid {border_color}; color: {text_color}; 
                        padding: 8px 12px; border-radius: 8px; margin-bottom: 15px; font-size: 15px; font-weight: 500;
                        text-align: center;">
                {icon} {opt_letter}. {opt_text}
            </div>
            """, unsafe_allow_html=True)
            
    else:
        # 【未作答狀態】：顯示可點擊的按鈕
        for opt_letter, opt_text in options.items():
            if st.button(f"{opt_letter}. {opt_text}", use_container_width=True, key=f"btn_{opt_letter}_{st.session_state.current_index}"):
                st.session_state.answers_dict[st.session_state.current_index] = opt_letter
                st.rerun()

    st.write("---")
    
    # --- 導航按鈕區 ---
    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.current_index > 0:
            if st.button("⬅️ 上一題", use_container_width=True):
                st.session_state.current_index -= 1
                st.rerun()
                
    with col2:
        if is_answered:
            if st.session_state.current_index < total_q_count - 1:
                if st.button("下一題 ➡️", use_container_width=True, type="primary"):
                    st.session_state.current_index += 1
                    st.rerun()
            else:
                if st.button("完成測驗查看成績 🏆", use_container_width=True, type="primary"):
                    st.session_state.current_index += 1
                    st.rerun()

else:
    # --- 測驗結束，計算與顯示成績單 ---
    total_q_count = len(st.session_state.current_questions)
    
    score = 0
    for idx, q_data in enumerate(st.session_state.current_questions):
        if idx in st.session_state.answers_dict:
            if st.session_state.answers_dict[idx] == q_data['答案'].strip().upper():
                score += 1
                
    percentage = (score / total_q_count) * 100
    
    st.progress(1.0)
    st.success(f"🎉 **測驗結束！**")
    
    col1, col2 = st.columns(2)
    col1.metric("答對題數", f"{score} / {total_q_count}")
    col2.metric("準確率", f"{percentage:.1f}%")
    
    st.write("---")
    st.subheader("📋 詳細對錯報告")
    
    for idx, q_data in enumerate(st.session_state.current_questions):
        user_choice = st.session_state.answers_dict.get(idx, "未作答")
        correct_answer = q_data['答案'].strip().upper()
        
        if user_choice == correct_answer:
            st.success(f"**第 {q_data['題號']} 題：✅ 答對**")
        else:
            with st.error(f"**第 {q_data['題號']} 題：❌ 答錯**"):
                st.write(f"你的選擇： `{user_choice}`")
                st.write(f"**正確答案： `{correct_answer}`**")
                
    if st.button("⬅️ 返回檢查最後一題", use_container_width=True):
        st.session_state.current_index -= 1
        st.rerun()
        
    st.info("您可以從左側選單選擇其他題組，繼續您的練習！")
