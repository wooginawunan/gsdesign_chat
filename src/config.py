config = {
    'project': "llmapps",
    'entity': None,
    'job_type': "production",
    'model_name':"gpt-4",
    'chat_temperature': 0.3,
    'max_fallback_retries': 1,
    'faiss_index_path': "./vector_store/faiss_index",
    'docs_dir': {'github_url': 'https://github.com/keaven/gsDesign',
                 'pdf': "docs/gsdesign_pdf", 
                 'scripts': "docs/gsDesign-master/R"}
}