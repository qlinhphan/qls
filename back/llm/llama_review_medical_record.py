import requests
import os


def llama_review_medical_record(prompt_review_medical, knowledge, len_data):
    prompt = prompt_review_medical(knowledge, len_data)
    response = requests.post(
        os.getenv("CHAT_API_SERVER"),
        json={
            'model': os.getenv("MODEL_CHAT"),
            'prompt': prompt,
            'stream': False,
            'options': {
                'num_predict': 2048,
                'temperature': 0   
            }  
        }
    )

    if response.status_code == 200:
        res_json = response.json()
        return res_json.get("response", "Không tìm thấy nội dung phản hồi từ LLM.")
    else:
        return f"Lỗi gọi API: Mã lỗi {response.status_code} - {response.text}"
    