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
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI

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
    # while True:

    #     # if i == 2: break
        
    #     q = input("Ban: ")
    #     if q == "bye":
    #         break;
    #     q_vector = get_embedding(q)
    #     response = rechieval_data(
    #         question_vector=q_vector,
    #         index_file=file_index,
    #         top_k=10,
    #         mycol=all_data_in_db,
    #         min_score=float(os.getenv("MIN_SCORE_RECHIEVAL")),
    #     )

    #     # print("CHECK KNOW: ", response)
    #     res = llama_clients(llama_clients_prompt, response, context, q)
    #     context.append([q, res])
    #     print("res: ", res)
    #     print("===================================================================================================================================")
    #     # print(type(res))

    while True:
        q = input("Ban: ")
        if q == "bye":
            break;
        q_vector = get_embedding(q)
        response = rechieval_data(
            question_vector=q_vector,
            index_file=file_index,
            top_k=3,
            mycol=all_data_in_db,
            min_score=float(os.getenv("MIN_SCORE_RECHIEVAL")),
        )

        llm = ChatOpenAI(model = "gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("BASE_URL"))
        prompt = ChatPromptTemplate.from_messages([
        ("system",
            """Bạn là trợ lý AI y tế của Bệnh viện Đa khoa Quốc tế Bắc Hà. Nhiệm vụ duy nhất của bạn là đọc các "Kiến thức được cung cấp" dưới đây để đề xuất chuyên khoa khám phù hợp cho người bệnh.

        Kiến thức được cung cấp (Chỉ dùng dữ liệu này để trả lời):
        {knowledge}

        Lịch sử hội thoại:
        {context}

        [QUY TẮC PHẢN HỒI NẰM LÒNG]:
        - Đi thẳng vào câu trả lời! TUYỆT ĐỐI KHÔNG in ra các câu như "Để trả lời câu hỏi này...", "Dựa vào tài liệu...", "Tôi hiểu rồi".
        - CHỈ SỬ DỤNG TIẾNG VIỆT CÓ DẤU.
        - TUYỆT ĐỐI KHÔNG THÊM CÁC TỪ KHÔNG LIÊN QUAN
        - ⚠️ LUẬT ĐỊNH DẠNG ĐƠN VỊ: Tuyệt đối KHÔNG ĐƯỢC viết dính liền dấu độ thành "390C" hay "400C". Bạn phải viết rõ ràng có dấu độ hoặc chữ độ (Ví dụ: "39°C - 40°C" hoặc "39-40 độ C").
        - Nếu được hỏi danh tính hoặc nguồn gốc: Trả lời ngay "Tôi là trợ lý AI y tế được tạo ra bởi Phòng CNTT thuộc Bệnh viện Đa khoa Quốc tế Bắc Hà."
        - Nếu được hỏi tóm tắt hội thoại thì PHẢI TÓM TẮT NGẮN GỌN DỰA VÀO {context}
        - Nếu triệu chứng chưa rõ ràng HOẶC "Kiến thức được cung cấp" trống rỗng/không chứa triệu chứng tương thích: Hãy lịch sự báo chưa tìm thấy hướng phù hợp dựa trên kiến thức hiện có và chủ động hỏi thêm triệu chứng chi tiết.

        [QUY TẮC ĐẶT TÊN CHUYÊN KHOA]:
        Hãy nhìn vào phần tên file ở cuối kiến thức để đọc vị ra tên khoa. Chỉ được điền tên khoa theo đúng quy định sau:
        - Tên file có "KHÁM CẤP CỨU" -> Ghi đúng chữ: Khám Cấp Cứu
        - Tên file có "K. NGOẠI" -> Ghi đúng chữ: Chuyên Khoa Ngoại
        - Tên file có "K. NHI" -> Ghi đúng chữ: Chuyên Khoa Nhi
        - Tên file có "K. NỘI" -> Ghi đúng chữ: Chuyên Khoa Nội
        - Tên file có "K. SẢN" -> Ghi đúng chữ: Khám Chuyên Khoa Sản
        - Tên file có "KHÁM TMH,RHM,MẮT" -> liên quan đến tai, mũi họng thì đề xuất Khám chuyên khoa Tai Mũi Họng, liện quan đến chuyên khoa Răng, Hàm, Mặt thì đề xuất khám Chuyên khoa Răng Hàm Mặt, liên quan đến mắt thì đề xuất khám Chuyên khoa Mắt
        (Tuyệt đối không tự ý dùng các tên khoa khác).

        [CẤU TRÚC ĐẦU RA BẮT BUỘC]:
        Chuyên khoa đề xuất:

        (Dựa vào {knowledge}, có bao nhiêu chuyên khoa phù hợp thì bạn PHẢI liệt kê ra bấy nhiêu chuyên khoa theo đúng cấu trúc bên dưới. Nếu chỉ có 1 khoa thì chỉ in ra 1 lần, nếu có nhiều khoa thì lặp lại khối này tương ứng, đặc biệt cùng một khoa/khám thì không được lặp lại):

        🩺 Kiến nghị: [Điền tên khoa theo quy định trên]
        📝 Lý do: [Diễn đạt phần DẤU HIỆU LÂM SÀNG GỢI Ý hoặc tên bệnh lý tương ứng có trong kiến thức, không tự bịa thêm]
        """),
            ("user", "{input}")
            # ("placeholder", "{agent_scratchpad}")
        ])

        messages = prompt.invoke({
            "knowledge": response,
            "context": "",
            "input": q
        })

        response = llm.invoke(messages)

        print(response.content)








        # if isinstance(res, dict):
        #     guardrail_res = llama_guardrail(guardrail_prompt, res, response)
        #     guardrail_res = extract_json(guardrail_res)
        #     if guardrail_res['check'] == "pass":
        #         print("AI: ",res)
        #     else:
        #         print("AI: ", "Xin lỗi, tôi không tìm thấy hướng điều trị phù hợp dựa trên kiến thức hiện có.")

        # if isinstance(res, str):
        #     print("AI: ",res)





    # summarize = llama_summary_conversation(llama_summary_conversation_prompt, context)

    # save_data_into_postgre(cursor = cursor, sessionId = "session-123", userId='user-123', content = summarize)

    # with open("ingestion/record.txt", 'r', encoding='utf-8') as fo:
    #     data = fo.readlines()
    #     data = [d.rstrip() for d in data]
        
    #     rs = llama_check_record(check_medical_record_logic_prompt, data)
    #     print(rs)





if __name__ == "__main__":
    main()
