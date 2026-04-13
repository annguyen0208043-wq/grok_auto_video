import streamlit as st
import json
import os
import time

QUEUE_FILE = "D:/TOOLS/queue.json"

if not os.path.exists(QUEUE_FILE):
    with open(QUEUE_FILE, "w") as f: json.dump([], f)

st.title("🎬 Grok Video Control")

# Nhập Prompt
with st.form("input_form", clear_on_submit=True):
    prompt_text = st.text_area("Nhập nội dung video:")
    submitted = st.form_submit_button("➕ Gửi vào hàng đợi")
    
    if submitted and prompt_text:
        with open(QUEUE_FILE, "r", encoding="utf-8") as f:
            queue = json.load(f)
        
        new_id = int(time.time())
        queue.append({"id": new_id, "text": prompt_text})
        
        with open(QUEUE_FILE, "w", encoding="utf-8") as f:
            json.dump(queue, f, indent=4, ensure_ascii=False)
        st.success(f"Đã thêm ID {new_id}")

# Hiển thị hàng đợi
st.subheader("📋 Danh sách đang chờ")
with open(QUEUE_FILE, "r", encoding="utf-8") as f:
    current_queue = json.load(f)

if current_queue:
    for item in current_queue:
        st.info(f"🔹 {item['text']}")
else:
    st.write("Hàng đợi trống.")

time.sleep(5)
st.rerun()