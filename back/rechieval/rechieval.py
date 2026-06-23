import faiss
import numpy as np


def rechieval_data(question_vector, index_file, top_k, mycol, min_score=0.6):
    question = np.array([question_vector], dtype=np.float32)
    faiss.normalize_L2(question)

    distances, indices = index_file.search(question, top_k)
    scores = distances[0].tolist()
    matched_indices = indices[0].tolist()

    # print("Scores:", scores)
    final_scores = []
    final_indices = []
    for score, idx in zip(scores, matched_indices):
        if score >= min_score:
            final_scores.append(score)
            final_indices.append(idx)

    # print("CHECK INDICE: ", final_indices)        

    if hasattr(mycol, "find"):
        list_data_db = list(mycol.find())
    else:
        list_data_db = list(mycol)

    response = []
    name_docs = []
    for fi in final_indices:
        data = list_data_db[fi]
        response.append(data['content'])
        name_docs.append(data['name_doc'])
        # print("rechieval: ", response)

    finals = []
    for r, n in zip(response, name_docs):
        finals.append([r, n])

    # print("FINALS: ", finals)
    return {
        "response": finals
    }


def rechieval_data_for_test(question_vector, index_file, top_k, mycol, min_score=0.6):
    question = np.array([question_vector], dtype=np.float32)
    faiss.normalize_L2(question)

    distances, indices = index_file.search(question, top_k)
    scores = distances[0].tolist()
    matched_indices = indices[0].tolist()

    # print("Scores:", scores)
    final_scores = []
    final_indices = []
    for score, idx in zip(scores, matched_indices):
        if score >= min_score:
            final_scores.append(score)
            final_indices.append(idx)

    if hasattr(mycol, "find"):
        list_data_db = list(mycol.find())
    else:
        list_data_db = list(mycol)

    response = []
    name_docs = []
    for fi in final_indices:
        data = list_data_db[fi]
        response.append(data['content'])
        name_docs.append(data['name_doc'])
    return {
        "chunk_predict": final_indices
    }
