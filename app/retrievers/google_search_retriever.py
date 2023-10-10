from typing import List
from langchain.callbacks.manager import CallbackManagerForRetrieverRun
from langchain.document_loaders import AsyncHtmlLoader
from langchain.document_transformers import Html2TextTransformer
from langchain.utilities import GoogleSearchAPIWrapper
from langchain.schema.retriever import BaseRetriever

class GoogleSearchRetriever(BaseRetriever):
    search: GoogleSearchAPIWrapper = GoogleSearchAPIWrapper()
    num_search_results = 6

    def clean_search_query(self, query: str) -> str:
        # Some search tools (e.g., Google) will
        # fail to return results if query has a
        # leading digit: 1. "LangCh..."
        # Check if the first character is a digit
        if query[0].isdigit():
            # Find the position of the first quote
            first_quote_pos = query.find('"')
            if first_quote_pos != -1:
                # Extract the part of the string after the quote
                query = query[first_quote_pos + 1 :]
                # Remove the trailing quote if present
                if query.endswith('"'):
                    query = query[:-1]
        return query.strip()

    def search_tool(self, query: str, num_search_results: int = 1) -> List[dict]:
        """Returns num_search_results pages per Google search."""
        query_clean = self.clean_search_query(query)
        result = self.search.results(query_clean, num_search_results)
        return result

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ):
        # Get search questions
        print("Generating questions for Google Search ...")

        # Get urls
        print("Searching for relevant urls...")
        urls_to_look = []
        search_results = self.search_tool(query, self.num_search_results)
        print("Searching for relevant urls...")
        print(f"Search results: {search_results}")
        for res in search_results:
            if res.get("link", None):
                urls_to_look.append(res["link"])

        print(search_results)
        loader = AsyncHtmlLoader(urls_to_look)
        html2text = Html2TextTransformer()
        print("Indexing new urls...")
        docs = loader.load()
        docs = list(html2text.transform_documents(docs))
        for i in range(len(docs)):
            if search_results[i].get("title", None):
                docs[i].metadata["title"] = search_results[i]["title"]
        return docs
