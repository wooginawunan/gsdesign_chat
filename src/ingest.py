# %%
import os
import requests
import fnmatch
import base64
import openai
from langchain.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.document_loaders import TextLoader
from langchain.document_loaders import DirectoryLoader
from langchain.document_loaders import PythonLoader

from config import config
from code_parse import RSegmenter
 
def inject_from_pdf(dir):
    # Load the pdfs in the pdf folder
    loader = PyPDFDirectoryLoader(dir)
    documents = loader.load()

    # Split the pdf content into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ".", "!", "?"],
        chunk_size=1500, 
        chunk_overlap=200)
    docs = text_splitter.split_documents(documents)
    return docs

def directory_loader(path):
    loader = DirectoryLoader(path, glob="*.R", loader_cls=PythonLoader, silent_errors=True)
    docs = loader.load()
    functions = []
    for doc in docs:
        funcs = RSegmenter(doc).extract_functions_classes()
        functions.extend(funcs)
    
    return functions
    

if __name__ == '__main__':
        
    api_key = os.environ.get("OPENAI_API_KEY", None)
    assert api_key.startswith("sk-"), "This doesn't look like a valid OpenAI API key"
    openai.api_key = api_key

    embeddings = OpenAIEmbeddings()

    docs_pdf = inject_from_pdf(config['docs_dir']['pdf'])
    docs_r_code = directory_loader(config['docs_dir']['scripts'])

    docs = docs_pdf + docs_r_code

    # Convert all chunks into vectors embeddings using OpenAI embedding model
    # Store all vectors in FAISS index and save to local folder 'faiss_index'
    db = FAISS.from_documents(docs, embeddings)
    db.save_local("faiss_index")

    print('Local FAISS index has been successfully saved.')

# %%
