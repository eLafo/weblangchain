import os
from .google_search_retriever import GoogleSearchRetriever
from langchain.retrievers import (ContextualCompressionRetriever,
                                  TavilySearchAPIRetriever)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.retrievers.document_compressors import (
    DocumentCompressorPipeline, EmbeddingsFilter)

def get_base_retriever():
    if (os.environ.get("USE_BACKUP", False)):
        return GoogleSearchRetriever()
    return TavilySearchAPIRetriever(k=6, include_raw_content=True, include_images=True)

embeddings = OpenAIEmbeddings()
splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=20)
relevance_filter = EmbeddingsFilter(embeddings=embeddings, similarity_threshold=0.8)
pipeline_compressor = DocumentCompressorPipeline(
    transformers=[splitter, relevance_filter]
)
base_retriever = get_base_retriever()

contextual_compression_retriever = ContextualCompressionRetriever(
                            base_compressor=pipeline_compressor, base_retriever=base_retriever
                        ).with_config(run_name="FinalSourceRetriever")
