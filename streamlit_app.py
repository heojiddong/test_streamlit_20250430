import streamlit as st
import openai
import time

st.title("Chat with GPT-4.1-mini via Assistant API")

# 🔐 OpenAI API Key 입력
api_key = st.text_input("Enter your OpenAI API Key", type="password")

if api_key:
    openai.api_key = api_key

    # 세션 상태 초기화
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = None

    # 쓰레드 생성 (최초 1회)
    if st.session_state.thread_id is None:
        # 새로운 채팅 스레드 생성
        st.session_state.thread_id = openai.ChatCompletion.create(
            model="gpt-4-1106-preview",  # GPT 모델 선택
            messages=[{"role": "system", "content": "You are a helpful assistant."}]
        ).id

    # ✅ Enter와 버튼 둘 다 작동하도록 form 사용
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("Your message:")
        submitted = st.form_submit_button("Send")

    if submitted and user_input:
        # 메시지 추가
        openai.ChatCompletion.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "user", "content": user_input}
            ],
            thread_id=st.session_state.thread_id  # 기존 스레드로 메시지 추가
        )

        # 응답 대기
        with st.spinner("Assistant is thinking..."):
            response = None
            while True:
                # 채팅 응답 요청
                response = openai.ChatCompletion.retrieve(
                    thread_id=st.session_state.thread_id
                )

                # 응답이 완료되면 break
                if response['status'] == "completed":
                    break
                elif response['status'] == "failed":
                    st.error("Run failed.")
                    break
                time.sleep(1)

        # 응답 출력
        if response:
            messages = response['messages']
            for msg in reversed(messages):
                if msg['role'] == 'assistant':
                    st.write(f"GPT: {msg['content']}")
                elif msg['role'] == 'user':
                    st.write(f"User: {msg['content']}")
else:
    st.info("Please enter your OpenAI API key to start chatting.")
