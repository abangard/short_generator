from constants import INDEX_NAME


def get_similar_items(client, embeddings, topk):
    search_body = {
        "size": topk,
        "query": {
            "knn": {
                "embeddings": {
                    "vector": embeddings,
                    "k": topk
                }
            }
        }
    }

    return client.search(index=INDEX_NAME, body=search_body)