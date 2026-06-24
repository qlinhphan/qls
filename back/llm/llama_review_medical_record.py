import requests
import os


def llama_check_identity(prompt_check_identity, knowledge):
    prompt = prompt_check_identity(knowledge)
    response = requests.post(
        os.getenv("CHAT_API_SERVER"),
        json={
            'model': os.getenv("MODEL_CHAT"),
            'prompt': prompt,
            'stream': False,
            'options': {
                'num_predict': 4096,
                'temperature': 0   
            }  
        }
    )

    if response.status_code == 200:
        res_json = response.json()
        return res_json.get("response", "Không tìm thấy nội dung phản hồi từ LLM.")
    else:
        return f"Lỗi gọi API: Mã lỗi {response.status_code} - {response.text}"
    

def llama_check_medical_logic(prompt_check_medical_logic, knowledge):
    prompt = prompt_check_medical_logic(knowledge)
    response = requests.post(
        os.getenv("CHAT_API_SERVER"),
        json={
            'model': os.getenv("MODEL_CHAT"),
            'prompt': prompt,
            'stream': False,
            'options': {
                'num_predict': 4096,
                'temperature': 0   
            }  
        }
    )

    if response.status_code == 200:
        res_json = response.json()
        return res_json.get("response", "Không tìm thấy nội dung phản hồi từ LLM.")
    else:
        return f"Lỗi gọi API: Mã lỗi {response.status_code} - {response.text}"
    
def llama_check_phamarcy(prompt_check_pharmacy, knowledge):
    prompt = prompt_check_pharmacy(knowledge)
    response = requests.post(
        os.getenv("CHAT_API_SERVER"),
        json={
            'model': os.getenv("MODEL_CHAT"),
            'prompt': prompt,
            'stream': False,
            'options': {
                'num_predict': 4096,
                'temperature': 0   
            }  
        }
    )

    if response.status_code == 200:
        res_json = response.json()
        return res_json.get("response", "Không tìm thấy nội dung phản hồi từ LLM.")
    else:
        return f"Lỗi gọi API: Mã lỗi {response.status_code} - {response.text}"
    