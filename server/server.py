import os

import openai
from dotenv import load_dotenv
from fastapi import FastAPI

from model import Question, Response

load_dotenv()
client = openai.Client(api_key=os.environ.get('OPENAI_API_KEY'))
app = FastAPI()


@app.post("/api/ask")
def respond_question(question: Question):
    messages = [
        {
            'role': 'user',
            'content': question.question,
        },
    ]
    
    try:
        result_chat = client.chat.completions.create(
            messages=messages,
            model='gpt-3.5-turbo',
            temperature=0,
        )
        content = result_chat.choices[0].message.content
        error = None
    except openai.APIStatusError as e:
        content = ''
        error = f"Got error from OpenAI API:\n  {e.status_code} {e.response}"
    except openai.APIConnectionError as e:
        content = ''
        error = f"Got error from OpenAI API:\n  {e.__cause__}"
    return Response(content=content, error=error)