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


def request_to_server(question: str):
    try:
        response = requests.post('http://localhost:8000/api/ask',
                                json={'question': question},
                                )
        response.raise_for_status()
        response = response.json()
    except requests.ConnectionError:
        st.error('Failed to connect to the server. Try again.')
        st.button('Retry')
        st.session_state['question'] = question
        st.stop()
    except requests.HTTPError:
        st.error(str(response.status_code) + ' ' + response.reason)
        st.button('Retry')
        st.session_state['question'] = question
        st.stop()
    else:
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

# request the answer to the model server
if st.session_state['chat_running']:
    with st.chat_message('assistant'):
        with st.spinner('Thinking...'):  # show the status requesting the answer
            request_to_server(st.session_state['question'])
            # change chat status after gotten response
            st.session_state['chat_running'] = False
            # rerun to show the answer
            st.rerun()

# show chat input widget
question = st.chat_input(key='question',
                         on_submit=update_messages_and_status,
                         disabled=st.session_state['chat_running'],
                         )
