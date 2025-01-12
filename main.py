import os
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.agents import Tool, AgentExecutor, initialize_agent
from langchain.prompts import PromptTemplate
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

# 맛집 추천 도구 정의
def search_restaurants(location, num_people, days):
    """
    맛집 추천 도구: 간단한 데이터를 반환. 실제로는 API 또는 DB 연결 가능.
    """
    # 예시 맛집 데이터 (실제 데이터는 API 또는 DB에서 가져올 것)
    restaurants = [
        {"name": "해운대 고기집", "type": "한식", "price": "중가", "region": "부산 해운대", "suitable_for": "가족"},
        {"name": "광안리 초밥집", "type": "일식", "price": "고가", "region": "부산 광안리", "suitable_for": "친구"},
        {"name": "해운대 디저트 카페", "type": "디저트", "price": "저가", "region": "부산 해운대", "suitable_for": "커플"},
    ]

    # 지역 필터링
    filtered = [r for r in restaurants if location in r["region"]]
    if not filtered:
        return "추천 가능한 맛집이 없습니다."

    # 추천 결과 생성
    recommendations = []
    for r in filtered:
        recommendations.append(f"{r['name']} ({r['type']}, {r['price']}, {r['region']})")
    return "\n".join(recommendations)

# LangChain Tool 정의
restaurant_tool = Tool(
    name="RestaurantSearch",
    func=lambda input_text: search_restaurants(
        location=input_text["location"],
        num_people=input_text["num_people"],
        days=input_text["days"],
    ),
    description="여행 장소와 인원을 기반으로 맛집을 추천합니다."
)

# LLM 초기화
llm = ChatOpenAI(
    model="gpt-4",
    openai_api_key=OPENAI_API_KEY,
)

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

# 에이전트 초기화
agent = initialize_agent(
    tools=[restaurant_tool],
    llm=llm,
    agent="zero-shot-react-description",
    verbose=True,
)

# 사용자 입력 처리
user_input = {
    "location": "부산 해운대",
    "num_people": "4명",
    "days": "2박 3일"
}

# 에이전트 실행
response = agent.run(user_input)

# 결과 출력
print("추천된 맛집:")
print(response)
