from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()
import os
# tao ra 1 con agent kiem tra tu vung
from langchain_classic.tools import tool
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from pydantic import Field, BaseModel
from langchain_core.prompts import ChatPromptTemplate


class Baseinp(BaseModel):
    exp: str = Field("Câu tiếng anh đầu vào của người dung")
@tool(args_schema=Baseinp)
def toolCheckVocab(exp: str):
    """Tool nhận xét trình độ sử dụng từ vựng tiếng anh của người dùng"""
    if "good" in exp:
        return {
            "result": "Khả năng sử dụng từ vựng tiếng anh của bạn rất tốt"
        }
    elif "bad" in exp:
        return {
            "result": "Trình độ sử dụng tiếng anh của bạn rất tệ"
        }
    else: 
        return {
            "result": "Trình độ sử dụng tiếng anh của bạn bình thường"
        }
    
llm = ChatOpenAI(model = os.getenv("MODEL_CHAT"), api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("BASE_URL"))

prompt = ChatPromptTemplate.from_messages([
    ("system", """
    Bạn là trợ lý AI chuyện đánh giá khả năng sử dụng từ vựng của user
     - Quy tắc:
     Phải sử dụng tool để phản hồi user
     Khi người dùng nói câu ngoài chủ đề tiếng anh thì bảo "bạn dã lạc đề, hãy nói 1 câu tiếng anh để tôi nhận xét"
     PHẢI SỬ DỤNG TOOL
"""),
    ("user", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

base = create_tool_calling_agent(llm, [toolCheckVocab], prompt)

agent = AgentExecutor(agent=base, tools=[toolCheckVocab])

rs = agent.invoke({"input": "Tôi mệt!"})

print(rs['output'])