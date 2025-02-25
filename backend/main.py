from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

import os
import tempfile
import uuid
import re


# initialize FastAPI app
backend_app = FastAPI()

# Enable CORS (Optional, for frontend)
backend_app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)


def clean_filename(filename):
    """cleans filename to meet ChromaDB's name requirements"""
    filename = filename.lower()  # convert to lowercase
    filename = filename.rsplit(".", 1)[0]  # remove file extension
    filename = re.sub(r'[^a-zA-Z0-9_-]', '_', filename)  # replace invalid characters with "_"
    filename = re.sub(r'_+', '_', filename)  # remove consecutive underscores
    filename = filename.strip("_-")  # make sure it starts/ends with an alphanumeric character

    # make sure name length is within limits
    return filename[:63]  # trim to 63 characters max


def save_uploaded_pdf(uploaded_file: UploadFile) -> str:
    """save uploaded PDF to a temporary file"""
    try:
        temp_file = tempfile.NamedTemporaryFile(delete = False, suffix = ".pdf")
        temp_file.write(uploaded_file.file.read())
        temp_file.close()
        return temp_file.name
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"File saving error: {str(e)}")


def split_document_text(documents, chunk_size = 1000, chunk_overlap = 200):
    """split text into chunks"""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = chunk_size,
                                                   chunk_overlap = chunk_overlap,
                                                   length_function = len,
                                                   separators = ["\n\n", "\n", " "])
    return text_splitter.split_documents(documents)


def get_embedding_function(api_key: str):
    """initialize OpenAI embeddings to use in Chroma vector store"""
    return OpenAIEmbeddings(model = "text-embedding-ada-002", openai_api_key = api_key)


def create_vectorstore(text_chunks, embedding_function, file_name, vector_store_path = "db"):
    """create Chroma vector store from text chunks"""
    ids = [str(uuid.uuid5(uuid.NAMESPACE_DNS, doc.page_content)) for doc in text_chunks]
    unique_text_chunks = []
    unique_ids = set()

    # pair each chunk with its unique id
    for text_chunk, id in zip(text_chunks, ids):
        if id not in unique_ids:
            unique_ids.add(id)
            unique_text_chunks.append(text_chunk)

    # create vector database
    vectorstore = Chroma.from_documents(documents = unique_text_chunks, # list of text_chunks to store
                                        collection_name = clean_filename(file_name),
                                        embedding = embedding_function,
                                        ids = list(unique_ids),
                                        persist_directory = vector_store_path)

    vectorstore.persist()
    return vectorstore


def load_vectorstore(file_name, api_key, vectorstore_path = "db"):
    """load previously saved Chroma vector store"""
    embedding_function = get_embedding_function(api_key)
    return Chroma(persist_directory = vectorstore_path,
                  embedding_function = embedding_function,
                  collection_name = clean_filename(file_name))


# fastapi **data models**
class QueryRequest(BaseModel):
    query: str
    file_name: str
    api_key: str


class QueryResponse(BaseModel):
    answer: str


# fastapi endpoints

@backend_app.post("/upload/")
async def upload_pdf(file: UploadFile = File(...), api_key: str = Form(...)):
    """
    Uploads a PDF and creates a vector store.
    """
    try:
        temp_file_path = save_uploaded_pdf(file)
        loader = PyPDFLoader(temp_file_path)
        documents = loader.load()

        # step 1: split documents
        text_chunks = split_document_text(documents)

        # step 2: generate embeddings
        embedding_function = get_embedding_function(api_key)

        # step 3: create vector store
        vectorstore = create_vectorstore(text_chunks, embedding_function, file.filename)

        # delete temporary file after processing
        os.unlink(temp_file_path)

        return JSONResponse(content = {"message": "PDF uploaded & vector store created",
                                       "file_name": file.filename})

    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))


@backend_app.post("/query/")
async def query_pdf(request: QueryRequest):
    """
    queries the vector store and returns an ai response.
    """
    try:
        vectorstore = load_vectorstore(request.file_name, request.api_key)

        # initialize gpt 4o mini model
        llm = ChatOpenAI(model = "gpt-4o-mini", api_key = request.api_key)
        retriever = vectorstore.as_retriever(search_type = "similarity")

        # prompt
        PROMPT_TEMPLATE = """
        You are an assistant for question-answering tasks.
        Answer as naturally as possible.
        The users are not very knowledgeable on the topic so keep it simple.
        Use the following retrieved context to answer the question.
        If you don't know the answer, say "I don't know."

        {context}

        ---

        Answer: {question}
        """

        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)

        # rag pipeline
        rag_chain = (
                {"context": retriever | (
                    lambda docs: "\n\n".join(doc.page_content for doc in docs)),
                 "question": RunnablePassthrough()}
                | prompt_template
                | llm.with_structured_output(QueryResponse, strict = True)
        )

        structured_response = rag_chain.invoke(request.query)
        return JSONResponse(content = structured_response.dict())

    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))


if __name__ == "__main__":
    import uvicorn


    uvicorn.run(backend_app, host = "127.0.0.1", port = 8000, reload = True)
