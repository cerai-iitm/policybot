import streamlit as st
import openai

def init_session_state():
  if "messages" not in st.session_state:
    st.session_state.messages = []

def display_chat_messages():
  for message in st.session_state.messages:
    with st.chat_input(message["role"]):
      st.markdown(message["content"])

def model_response(query, context):
  return "d"

def main():
  st.title("AI Policy Chatbot")

  init_session_state()

  display_chat_messages()

  context = st.sidebar.text_area("Context", "Enter context here", height=200)

  if query := st.chat_input("Chat with model"):
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
      st.markdown(query)

    with st.chat_message("assistant"):
      response = "d"
      st.markdown(response)
      st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
  main()