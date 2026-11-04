
from app.gemini_service import generate_response
from app.retrieval import retrieve_relevant_chunks


def generate_rag_response(question: str) -> dict:
    """Generate an answer using retrieved document context."""

    chunks = retrieve_relevant_chunks(question)

    if not chunks:
        return {
            "answer": "I could not find relevant information in the available building-rule documents.",
            "sources": []
        }

    context_parts = []
    sources = []

    for chunk in chunks:
        source = chunk["source"]
        page = chunk["page_number"]

        context_parts.append(
            f"""
Source: {source}
Page: {page}

Content:
{chunk["text"]}
"""
        )

        citation = {
            "source": source,
            "page_number": page
        }

        if citation not in sources:
            sources.append(citation)

    context = "\n\n".join(context_parts)

    prompt = f"""
You are PlotPermit, an assistant that answers questions
about Tamil Nadu building rules and regulations.

Answer the user's question using ONLY the provided document context.

IMPORTANT RULES:
1. Do not invent rules, measurements, fees, or legal requirements.
2. If the context does not contain the answer, clearly say so.
3. Distinguish historical regulations from newer amendments.
4. Mention the document name and page number supporting the answer.
5. Use simple and clear English.
6. Do not present historical rules as current requirements
   unless the provided context supports that conclusion.

DOCUMENT CONTEXT:

{context}

USER QUESTION:
{question}

Provide a clear answer with source citations.
"""

    answer = generate_response(prompt)

    return {
        "answer": answer,
        "sources": sources
    }
