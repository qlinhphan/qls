
from chunking.chunks import load_data
from dotenv import load_dotenv
load_dotenv()
import os
import faiss
from embedding.embedder import get_embedding
from vectordb.vector_store import vector_stores
from rechieval.rechieval import rechieval_data
from llm.llama_client import llama_clients
from vectordb.postgre import (
    create_table_postgre,
    init_postgre,
    load_knowledge_postgre,
    save_data_into_postgre,
    save_knowledge_postgre,
)
from pprint import pprint
from llm.llama_client import llama_summary_conversation, llama_guardrail, llama_check_record, extract_json
from prompts.prompt_temp import llama_clients_prompt, llama_summary_conversation_prompt, guardrail_prompt, check_medical_record_logic_prompt
import json
from prompts.prompt_review_medical_record import prompt_review_medical_records
from llm.llama_review_medical_record import llama_review_medical_record
import time


def fun():
    folder = "aperson"
    paath_file = [os.path.join(folder, o) for o in os.listdir(folder)]
    print(paath_file)


    data_final = []
    for pf in paath_file:
        with open(pf, 'r', encoding="utf-8") as fo:
            data = json.load(fo)
            data_final.append(data)
        # break

    pprint(data_final)
    print("len: ",len(data_final))

    st = time.time()
    res = llama_review_medical_record(prompt_review_medical_records, data_final, len(data_final))
    end = time.time()

    print("res: ", res )
    print("during: ", (end-st))

    

if __name__ == "__main__":
    fun()