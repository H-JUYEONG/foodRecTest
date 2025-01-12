import os
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import LLMChain
from langchain.schema import BaseOutputParser

# 환경변수에서 API 키 가져오기
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("환경변수 'OPENAI_API_KEY'가 설정되지 않았습니다.")

# CommaSeparatedListOutputParser 정의
class CommaSeparatedListOutputParser(BaseOutputParser):
    """LLM 출력에서 ','로 분리된 결과를 반환하는 파서."""
    def parse(self, text: str):
        return text.strip().split(", ")

# 시스템 메시지 프롬프트 템플릿
system_template = """
너는 여행 가이드를 도와주는 AI야.
사용자가 특정 장소에 대해 추천을 요청하면, 해당 장소에서 유명한 항목(맛집, 관광지 등)을 3개 추천해줘.
단어는 반드시 comma(,)로 분리해서 답변하고, 다른 내용은 포함하지 마.
"""

system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
human_template = "{text}"
human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

# 프롬프트 통합
chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

# LLMChain 구성
chat_chain = LLMChain(
    llm=ChatOpenAI(openai_api_key=OPENAI_API_KEY, model="gpt-3.5-turbo"),
    prompt=chat_prompt,
    output_parser=CommaSeparatedListOutputParser()
)

# 질문 실행
response = chat_chain.run("부산 해운대에서 유명한 맛집 3가지를 추천해줘.")

# 결과 출력
print(response)  # ['맛집1', '맛집2', '맛집3']와 같은 리스트 형태로 출력됨
