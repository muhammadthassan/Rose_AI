import streamlit as st
from langchain_ollama import ChatOllama

st.set_page_config(page_title="Rose AI", page_icon="🌹")

# Initialize session state for user name and chat history
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Page 1: User Name Entry
if st.session_state.user_name is None:
    st.header(":rainbow[Welcome to Rose] AI 🌹")
    st.subheader("Please enter your name to get started")
    
    with st.form("name_form"):
        name_input = st.text_input("Your Name", placeholder="Enter your name...")
        submitted = st.form_submit_button("Start Chatting")
        
        if submitted and name_input.strip():
            st.session_state.user_name = name_input.strip()
            st.rerun()
        elif submitted:
            st.error("Please enter a valid name!")

# Page 2: Chat Interface
else:
    user_name = st.session_state.user_name
    
    st.header(":rainbow[Rose] AI")
    st.caption(f"Welcome, **{user_name}**! 👋")
    
    # Option to change name and clear chat in sidebar
    with st.sidebar:
        st.write(f"Logged in as: **{user_name}**")
        if st.button("Change Name"):
            st.session_state.user_name = None
            st.session_state.chat_history = []
            st.rerun()
        if st.button("Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()
    
    llm = ChatOllama(model="hf.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF:Q4_K_M")
    
    # Helper function to display a chat message
    def display_chat_message(question, response, user_name):
        with st.chat_message("ai"):
            # Check if question exceeds 3 lines (approximately 150 chars or contains 3+ newlines)
            lines = question.count('\n') + 1
            is_long_question = lines > 3 or len(question) > 150
            
            # Show the question with user's name (collapsible if long)
            if is_long_question:
                with st.expander(f"📝 **{user_name}** (click to expand)", expanded=False):
                    st.write(question)
            else:
                st.markdown(f"📝 **{user_name}:**\n\n{question}")
            
            st.divider()
            
            # Display the response
            st.markdown(f"💬 **Rose:**\n\n{response}")
    
    # Display all previous chat messages
    for chat in st.session_state.chat_history:
        display_chat_message(chat["question"], chat["response"], user_name)
    
    # Chat input
    prompt = st.chat_input("Add your Question...")
    
    # Process new question
    if prompt:
        # Display the current question and stream the response
        with st.chat_message("ai"):
            # Check if question exceeds 3 lines
            lines = prompt.count('\n') + 1
            is_long_question = lines > 3 or len(prompt) > 150
            
            # Show the question with user's name (collapsible if long)
            if is_long_question:
                with st.expander(f"📝 **{user_name}** (click to expand)", expanded=False):
                    st.write(prompt)
            else:
                st.markdown(f"📝 **{user_name}:**\n\n{prompt}")
            
            st.divider()
            
            # Stream the response
            st.markdown("💬 **Rose:**")
            
            # Create a generator for streaming
            def stream_response():
                for chunk in llm.stream(prompt):
                    yield chunk.content
            
            # Use write_stream to display streaming response
            response_content = st.write_stream(stream_response())
        
        # Save to chat history
        st.session_state.chat_history.append({
            "question": prompt,
            "response": response_content
        })