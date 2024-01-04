import time

import requests
import streamlit as st


def update_messages_and_status():
    question = st.session_state['question']

    if question is None:
        print('question should not be None.')
        st.stop()
    st.session_state['chat_messages'].append({
        'role': 'user',
        'content': question,
    })

    st.session_state['chat_running'] = True


def request_to_server():
    response = requests.post('http://localhost:8000/api/ask',
                             json={'question': st.session_state['question']},
                             ).json()

    print(response)
    
    st.session_state['chat_messages'].append({
        'role': 'assistant',
        'content': response['content']
    })


# chat messages initialization
if st.session_state.get('chat_messages') is None:
    st.session_state['chat_messages'] = [
        {
            'role': 'assistant',
            'content': 'Hello! Ask anything about your document.',
        }
    ]

# chat status initialization
if st.session_state.get('chat_running') is None:
    st.session_state['chat_running'] = False

# show chat messages 
for message in st.session_state['chat_messages']:
    with st.chat_message(message['role']):
        st.write(message['content'])

# show chat input widget
question = st.chat_input(key='question',
                         on_submit=update_messages_and_status,
                         disabled=st.session_state['chat_running'],
                         )

# request the answer to the model server
if st.session_state['chat_running']:
    with st.chat_message('assistant'):
        with st.spinner('Thinking...'):  # show the status requesting the answer
            request_to_server()
            # change chat status after gotten response
            st.session_state['chat_running'] = False
            # rerun to show the answer
            st.rerun()
