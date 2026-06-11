import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.title("LLM 기반 Streamlit 챗봇입니다.")

# 대화 이력 초기화
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# 지금까지 대화 내용 출력
for role, content in st.session_state["messages"]:
    with st.chat_message(role):
        st.write(content)

user_input = st.chat_input("메시지를 입력하세요.")

if user_input:
    # 1) 사용자 메시지 저장 및 출력
    st.session_state["messages"].append(("user", user_input))
    with st.chat_message("user"):
        st.write(user_input)


    now = datetime.now().strftime("%Y년 %m월 %d일 %H시 %M분 %S초")
    
    messages = [
        {
            "role": "system",
            "content": f"""
너는 친절한 LLM 튜터입니다.
현재 시간은 {now} 입니다.
사용자가 현재 날짜나 시간을 물어보면 이 정보를 기준으로 답변하세요.
"""
        }
    ]

    for role, content in st.session_state["messages"]:
        messages.append({"role": role, "content": content})

    # 2) OpenAI 호출용 messages 구성
    messages = [{"role": "system", "content": "친절한 LLM 튜터입니다."}]
    for item in st.session_state["messages"]:
        role    = item[0]
        content = item[1]
        messages.append({"role": role, "content": content})

    response = client.chat.completions.create(
        model="gpt-4.5-mini",
        messages=messages,
    )

    
    assistant_reply = response.choices[0].message.content

    # 3) 응답 저장 및 출력
    st.session_state["messages"].append(("assistant", assistant_reply))
    with st.chat_message("assistant"):
        st.write(assistant_reply)

        
