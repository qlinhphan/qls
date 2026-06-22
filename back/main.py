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
from llm.llama_client import llama_summary_conversation, llama_guardrail, llama_check_record, extract_json
from prompts.prompt_temp import llama_clients_prompt, llama_summary_conversation_prompt, guardrail_prompt, check_medical_record_logic_prompt
import json
# from llm.llama_client import 

def main():
    cursor = init_postgre()
    create_table_postgre(cursor)
    print("created postgre sucessfully")

    # read_file and split chunks
    file_in_docs = os.listdir('ingestion/docs')
    list_path_file = [os.path.join('ingestion/docs', fid) for fid in file_in_docs]

    all_data_in_db = load_knowledge_postgre(cursor)
    if len(all_data_in_db) == 0:
        save_knowledge_postgre(
            list_path_file=list_path_file,
            load_data=load_data,
            cursor=cursor,
            get_embedding=get_embedding,
        )
        all_data_in_db = load_knowledge_postgre(cursor)
    else:
        print("didn't save knowledge into db")
    

    # build vector store file: name_file.index
    if not os.path.exists("faiss.index"):
        vector_stores(all_data_in_db)
        print("created vector_stores")
    else:
        print("didn't create vector_store")

    # search
    file_index = faiss.read_index("faiss.index")   

    context = []
    # i = 0
    while True:

        # if i == 2: break
        
        q = input("Ban: ")
        if q == "bye":
            break;
        q_vector = get_embedding(q)
        response = rechieval_data(
            question_vector=q_vector,
            index_file=file_index,
            top_k=10,
            mycol=all_data_in_db,
            min_score=float(os.getenv("MIN_SCORE_RECHIEVAL")),
        )

        # print("CHECK KNOW: ", response)
        res = llama_clients(llama_clients_prompt, response, context, q)
        context.append([q, res])

        if isinstance(res, dict):
            guardrail_res = llama_guardrail(guardrail_prompt, res, response)
            guardrail_res = extract_json(guardrail_res)
            if guardrail_res['check'] == "pass":
                print("AI: ",res)
            else:
                print("AI: ", "Xin lỗi, tôi không tìm thấy hướng điều trị phù hợp dựa trên kiến thức hiện có.")

        if isinstance(res, str):
            print("AI: ",res)

    # summarize = llama_summary_conversation(llama_summary_conversation_prompt, context)

    # save_data_into_postgre(cursor = cursor, sessionId = "session-123", userId='user-123', content = summarize)

    # with open("ingestion/record.txt", 'r', encoding='utf-8') as fo:
    #     data = fo.readlines()
    #     data = [d.rstrip() for d in data]
        
    #     rs = llama_check_record(check_medical_record_logic_prompt, data)
    #     print(rs)





if __name__ == "__main__":
    main()
