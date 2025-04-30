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
    if "assistant_id" not in st.session_state:
        st.session_state.assistant_id = None

    # 어시스턴트 생성 (최초 1회)
    if st.session_state.assistant_id is None:
        assistant = openai.beta.assistants.create(
            name="Mini Chat Assistant",
            instructions="You are a helpful assistant.",
            model="gpt-4-1106-preview"
        )
        st.session_state.assistant_id = assistant.id

    # 쓰레드 생성
    if st.session_state.thread_id is None:
        thread = openai.beta.threads.create()
        st.session_state.thread_id = thread.id

    # ✅ Enter와 버튼 둘 다 작동하도록 form 사용
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("Your message:")
        submitted = st.form_submit_button("Send")

    if submitted and user_input:
        # 메시지 추가
        openai.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=user_input
        )

        # Run 실행
        run = openai.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=st.session_state.assistant_id,
        )

        # 응답 대기
        with st.spinner("Assistant is thinking..."):
            while True:
                run_status = openai.beta.threads.runs.retrieve(
                    thread_id=st.session_state.thread_id,
                    run_id=run.id
                )
                if run_status.status == "completed":
                    break
                elif run_status.status == "failed":
                    st.error("Run failed.")
                    break
                time.sleep(1)

        # 응답 출력
        messages = openai.beta.threads.messages.list(thread_id=st.session_state.thread_id)
        for msg in reversed(messages.data):
            if msg.role == "assistant":
                st.write(f"GPT: {msg.content[0].text.value}")
            elif msg.role == "user":
                st.write(f"User: {msg.content[0].text.value}")
else:
    st.info("Please enter your OpenAI API key to start chatting.")
