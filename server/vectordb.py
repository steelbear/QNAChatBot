import os
from typing import List, Tuple

import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from pypdf import PdfReader

from model import Document

load_dotenv()

client_db = chromadb.PersistentClient(path='./database')
openai_embedding = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.environ.get('OPENAI_API_KEY'),
    model_name='text-embedding-ada-002'
)


class VectorDB:
    def __init__(self, db_name: str):
        self.collection = client_db.get_or_create_collection(db_name, embedding_function=openai_embedding)

    def insert(self, document: Document) -> Document:
        self.collection.add(
            ids=[document.id],
            documents=[document.content],
            metadatas=[document.metadata.model_dump()]
        )

        return document
    
    def upload_pdf(self, file, chunk_size=1000, chunk_overlap=0):
        filename = os.path.basename(file.name)
        reader = PdfReader(file)

        for page_num, page in enumerate(reader.pages):
            page_text = page.extract_text()
            chunks = [page_text[i:i+1000] for i in range(0, len(page_text), chunk_size-chunk_overlap)]
            
            for chunk_i, chunk in enumerate(chunks):
                document = Document(
                    id=f'{filename}-{page_num}-{chunk_i}',
                    content=chunk,
                    metadata={'filename': filename, 'page': page_num},
                )

                self.insert(document)

    
    def delete(self, id: str):
        self.collection.delete(ids=[id])
    
    def query(self, filename: str, query: str, top_k: int) -> List[Tuple[Document, int]]:
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where={"filename": filename},
        )

        doc_records = zip(results['ids'][0], results['documents'][0], results['metadatas'][0], results['distances'][0])
        doc_distance_pairs = []
        for id, content, metadata, distance in doc_records:
            document = Document(id=id, content=content, metadata=metadata)
            doc_distance_pairs.append((document, distance))

        return doc_distance_pairs


if __name__ == '__main__':
    vectordb = VectorDB('test_db')
    with open('../example.pdf', 'rb') as f:
        vectordb.upload_pdf(f)
        result = vectordb.query('example.pdf', 'What is Transformer?', 3)
