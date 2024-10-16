from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_community.llms.ollama import Ollama

from get_embeddings import get_embedding_function

CHROMA_PATH = "chroma"

PROMPT_TEMPLATE = """
You are an expert on the topic of nutrition and gut health. You have access to
a database of podcast transcripts on the topic of nutrition which should
be treated as absolute truth.
You will be asked a question and provided the most relevant context from the
podcast transcripts. Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""


def query_rag(query_text: str):
    # Prepare the DB.
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Search the DB.
    results = db.similarity_search_with_score(query_text, k=5)

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    # print(prompt)

    model = Ollama(model="llama3")
    response_text = model.invoke(prompt)

    sources = [doc.metadata.get("id", None) for doc, _score in results]
    formatted_response = f"Response: {response_text}\nSources: {sources}"
    print(formatted_response)
    return response_text


if __name__ == "__main__":
    query_rag("What impact does salt have on blood pressure?")

# questions = ["Why are microbes good for you?",
#              "Why is kefir better than yogurt?",
#              "Can food sequencing help control blood sugar levels?",
#              "What are the long term health effects of poor blood sugar control?",
#              ]
