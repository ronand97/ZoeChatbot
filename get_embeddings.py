from langchain_community.embeddings.ollama import OllamaEmbeddings


def get_embedding_function() -> OllamaEmbeddings:
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    return embeddings


if __name__ == "__main__":
    embeddings = get_embedding_function()
    print(embeddings.embed_query("hello world"))
