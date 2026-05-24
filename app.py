# app.py
import os

import streamlit as st
from dotenv import load_dotenv
from google import genai

from rag_engine import RAGEngine

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL = "gemini-2.5-flash"


@st.cache_resource
def load_rag():
    return RAGEngine("knowledge/noodle_kb.txt")


rag = load_rag()

st.title("Noodle🍜 ผู้ช่วย AI ของร้าน ก๋วยเตี๋ยวกลางดึก")

# Sample reviews data
SAMPLE_REVIEWS = [
    {
        "name": "ธัญญ์",
        "rating": 5,
        "comment": "ก๋วยเตี๋ยวอร่อยมาก! เส้นนุ่มและน้ำซุปกลมกล่อม ราคาก็ถูกด้วย ยิ่งเปิดกลางดึกสะดวกมากสำหรับคนทำงานค่ำ",
        "date": "2024-05-20"
    },
    {
        "name": "สมศรี",
        "rating": 5,
        "comment": "เมนูบะหมี่เหลืองหมูนุ่มน้ำตกเด็ดมาก! ต้นแบบที่ร้านแนะนำสมควรจริง ๆ อร่อยสุด",
        "date": "2024-05-18"
    },
    {
        "name": "กัญญา",
        "rating": 4,
        "comment": "ที่ตั้งร้านสะดวกมาก อยากให้มี wifi ด้วยจะสุดยอด อยากไปอีก",
        "date": "2024-05-15"
    },
    {
        "name": "สาธร",
        "rating": 5,
        "comment": "เด็ก ๆ ชอบเมนูเส้นหมี่ขาวรวมมิตร น้ำซุปไม่อาบ ทานง่าย แนะนำให้เพื่อน ๆ เยอะ",
        "date": "2024-05-10"
    },
    {
        "name": "นภาลัย",
        "rating": 5,
        "comment": "ต้มยำรสแซ่บจัดจ้าน! ถูกใจสายแซ่บ มากจริง ๆ ได้ตับลวกอร่อย",
        "date": "2024-05-08"
    }
]


# Create tabs
tab1, tab2 = st.tabs(["💬 หน้าแรก (แชทบอท)", "⭐ รีวิว"])

# Tab 1: Chatbot
with tab1:
    st.caption("ถามเรื่องเมนู เวลาเปิด หรือข้อมูลร้านได้เลย")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if prompt := st.chat_input("ถามอะไรเกี่ยวกับร้านได้เลย..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # RAG: Search
        context_chunks = rag.search(prompt, top_k=3)
        context = "\n---\n".join(context_chunks)

        # Generate
        full_prompt = f"""คุณคือ Noodle ผู้ช่วย AI ของร้าน ก๋วยเตี๋ยวกลางดึก ตอบเฉพาะจากข้อมูลด้านล่าง
ถ้าไม่พบข้อมูล ให้บอกว่าไม่ทราบ อย่าแต่งข้อมูลเอง

ข้อมูลร้าน:
{context}

คำถาม: {prompt}
"""
        response = client.models.generate_content(model=MODEL, contents=full_prompt)
        answer = response.text

        st.session_state.messages.append({"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.write(answer)

# Tab 2: Reviews
with tab2:
    st.subheader("รีวิวจากลูกค้า ⭐")
    
    # Calculate average rating
    avg_rating = sum(review["rating"] for review in SAMPLE_REVIEWS) / len(SAMPLE_REVIEWS)
    col1, col2 = st.columns(2)
    with col1:
        st.metric("คะแนนเฉลี่ย", f"{avg_rating:.1f}/5.0")
    with col2:
        st.metric("จำนวนรีวิว", len(SAMPLE_REVIEWS))
    
    st.divider()
    
    # Display reviews
    for review in SAMPLE_REVIEWS:
        with st.container(border=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"**{review['name']}**")
            with col2:
                stars = "⭐" * review['rating']
                st.write(f"{stars}")
            st.caption(review['date'])
            st.write(review['comment'])