
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
from prompts.prompt_review_medical_record import prompt_check_identity, prompt_check_medical_logic, prompt_check_pharmacy
from llm.llama_review_medical_record import llama_check_identity, llama_check_medical_logic, llama_check_phamarcy
import time


def fun():
    file = "aperson/test_a_1.json"
    with open(file, 'r', encoding='utf8') as fo:
        data = json.load(fo)
    print(data)
    # paath_file = [os.path.join(folder, o) for o in os.listdir(folder)]
    # print(paath_file)


    # data_final = []
    # for pf in paath_file:
    #     with open(pf, 'r', encoding="utf-8") as fo:
    #         data = json.load(fo)
    #         data_final.append(data)
    #     # break

    # pprint(data_final)
    # print("len: ",len(data_final))
    start = time.time()

    response = {
        "check_identity": True,
        "check_logic": True,
        "check_pharmacy": True
    }

    res_iden = llama_check_identity(prompt_check_identity, data)

    res_logic = llama_check_medical_logic(prompt_check_medical_logic, data)

    res_pharmacy = llama_check_phamarcy(prompt_check_pharmacy, data)

    if "❌" in res_iden: response["check_identity"] = False
    if "❌" in res_logic: response["check_logic"] = False
    if "❌" in res_pharmacy: response["check_pharmacy"] = False

    end = time.time()

    print(response)
    print("during: ", (end-start))

    

if __name__ == "__main__":
    fun()