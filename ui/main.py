import requests
import streamlit as st


def show_error(message, previous_question):
    st.error(message)
    st.button('Retry')
    # Keep user's previous question
    st.session_state['question'] = previous_question
    st.stop()
    

@st.cache_data
def upload_file(file):
    try:
        response = requests.post('http://localhost:8000/api/upload', files={'file': file})
        response.raise_for_status()
        response = response.json()
    except requests.ConnectionError:
        st.error('Failed to connect to the server. Try again.')
    except requests.HTTPError:
        st.error(str(response.status_code) + ' ' + response.reason)
    else:
        if response['error']:
            show_error(response['error'], question)
        else:
            print('filename:', response['content'])
            st.session_state['filename'] = response['content']


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


def request_to_server(question, filename):
    try:
        response = requests.post('http://localhost:8000/api/ask', json={'question': question, 'filename': filename})
        response.raise_for_status()
        response = response.json()
    except requests.ConnectionError:
        show_error('Failed to connect to the server. Try again.', question)
    except requests.HTTPError:
        show_error(str(response.status_code) + ' ' + response.reason, question)
    else:
        if response['error']:
            show_error(response['error'], question)
        else:
            st.session_state['chat_messages'].append({
                'role': 'assistant',
                'content': response['content']
            })


file = st.file_uploader('the file what model read')
if file is not None:
    upload_file(file)


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
            request_to_server(st.session_state['question'], st.session_state['filename'])
            # change chat status after gotten response
            st.session_state['chat_running'] = False
            # rerun to show the answer
            st.rerun()

# show chat input widget
question = st.chat_input(key='question',
                         on_submit=update_messages_and_status,
                         disabled=st.session_state['chat_running'],
                         )
