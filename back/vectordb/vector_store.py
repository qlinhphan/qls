import faiss
from pprint import pprint
import numpy as np

def vector_stores(mycol):
    if hasattr(mycol, "find"):
        data_db = list(mycol.find())
    else:
        data_db = list(mycol)

    get_vector = np.array([d['vector'] for d in data_db], dtype=np.float32)

    print("GET: ", get_vector.shape)
    if get_vector.ndim != 2:
        raise ValueError(f"Vector data is invalid, shape={get_vector.shape}")

    faiss.normalize_L2(get_vector)


    ind = faiss.IndexFlatIP(len(data_db[0]['vector']))
    ind.add(get_vector)

    faiss.write_index(ind, "faiss.index")
    # print(ind)
