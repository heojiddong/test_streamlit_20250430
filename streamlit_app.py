import streamlit as st
prompt = st.chat_input("Say something")
if prompt:
    st.write(f"User: {prompt}")
