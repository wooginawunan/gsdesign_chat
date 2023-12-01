# **app.py**

import time
import streamlit as st
from src.utils import load_chain

def add_message(role, content, avatar):
    # Add message to chat history
    st.session_state.messages.append({"role": role, "content": content})
    # Display message in chat message container
    with st.chat_message(role, avatar=avatar):
        st.markdown(content)

# Custom image for the app icon and the assistant's avatar
# company_logo = 'https://www.app.nl/wp-content/uploads/2019/01/Blendle.png'
company_logo = 'images/aipal.jpg'
expert_logo = 'images/keavan.png'
user_logo = 'images/user.jpg'


# Configure Streamlit page
st.set_page_config(
    page_title="Chat with The gsDesign Expert",
    page_icon=company_logo
)

# Initialize LLM chain
chain = load_chain()

# Initialize chat history
if 'messages' not in st.session_state:
    # Start with first message from assistant
    st.session_state['messages'] = [{"role": "assistant", 
                                  "content": "Dear Friend! I am the gsDesign expert. How can I help you today?"}]
# print(st.session_state)
# Display chat messages from history on app rerun
# Custom avatar for the assistant, default avatar for user
for message in st.session_state.messages:
    if message["role"] == 'assistant':
        with st.chat_message(message["role"], avatar=expert_logo):
            st.markdown(message["content"])
    else:
        with st.chat_message(message["role"], avatar=user_logo):
            st.markdown(message["content"])


    
# Chat logic
try:
    if query := st.chat_input("Ask me anything"):
        add_message("user", query, user_logo)

        with st.chat_message("assistant", avatar=expert_logo):
            message_placeholder = st.empty()
            # Send user's question to our chain
            result = chain({"question": query}, return_only_outputs=True)
            
            response = result['answer']
            docs = [(doc.metadata, doc.page_content) for doc in result['source_documents']]
            
            st.markdown(response)
            
        with st.sidebar:
            
            st.title('📖 References:')
            for i, (meta, doc) in enumerate(docs):
                print(meta)
                #st.markdown("[{}] On page {} of {} -- {}".format(i+1, meta['page'], meta['source'], doc))
                if 'page' in meta:
                    st.markdown("[{}] {}. Page {}.".format(i+1, meta['source'].split("/")[-1], meta['i']))
                else:
                    st.markdown("[{}] {}.".format(i+1, meta['source'].split("/")[-1])) 
                    st.markdown(f"<p style='font-size:12px'>{doc}</p>", unsafe_allow_html=True)  
        st.session_state.messages.append({"role": "assistant", "content": response})
    
        
except Exception as e:
    st.error(f"An error occurred: {e}")


