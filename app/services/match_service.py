from app.retrieval.retriever import RetrievalService


class MatchService:
    def __init__(self):
        self.retriever = RetrievalService()

    def run_match(self, query: str) -> dict:
        resume_docs = self.retriever.retrieve("resume_chunks", query)
        job_docs = self.retriever.retrieve("job_chunks", query)

        resume_results = [
            {
                "content": doc.page_content,
                "metadata": doc.metadata
            }
            for doc in resume_docs
        ]

        job_results = [
            {
                "content": doc.page_content,
                "metadata": doc.metadata
            }
            for doc in job_docs
        ]

        return {
            "status": "success",
            "query": query,
            "resume_results": resume_results,
            "job_results": job_results
        }