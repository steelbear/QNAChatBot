from fastapi import FastAPI

from model import Question, Response

app = FastAPI()


@app.post("/api/ask")
def respond_question(question: Question):
    return Response(content='You said: ' + question.question)