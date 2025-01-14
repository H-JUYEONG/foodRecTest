import os
import json
from langchain_openai import ChatOpenAI
from langchain.agents import Tool, initialize_agent
from langchain.agents import AgentType

# 환경변수에서 API 키 가져오기
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("환경변수 'OPENAI_API_KEY'가 설정되지 않았습니다.")


def search_restaurants(query):
    """
    맛집 추천 도구: 문자열 입력을 파싱하여 처리
    """
    # 예시 맛집 데이터
    restaurants = [
        {
            "name": "해운대 고기집",
            "type": "한식",
            "price": "중가",
            "region": "부산 해운대",
            "suitable_for": "가족",
        },
        {
            "name": "광안리 초밥집",
            "type": "일식",
            "price": "고가",
            "region": "부산 광안리",
            "suitable_for": "친구",
        },
        {
            "name": "해운대 디저트 카페",
            "type": "디저트",
            "price": "저가",
            "region": "부산 해운대",
            "suitable_for": "커플",
        },
    ]

    # 입력 문자열에서 위치 정보 추출
    location = "부산 해운대"  # 기본값
    if "부산" in query:
        if "해운대" in query:
            location = "부산 해운대"
        elif "광안리" in query:
            location = "부산 광안리"

    # 지역 필터링
    filtered = [r for r in restaurants if location in r["region"]]
    if not filtered:
        return "추천 가능한 맛집이 없습니다."

    # 추천 결과 생성
    recommendations = [
        f"{r['name']} ({r['type']}, {r['price']}, {r['region']})" for r in filtered
    ]
    return "\n".join(recommendations)


# LangChain Tool 정의
restaurant_tool = Tool(
    name="맛집검색",
    func=search_restaurants,
    description="한국어로 지역명을 입력하면 해당 지역의 맛집을 찾아줍니다. 반드시 한국어로 입력하세요. 예시) '부산 해운대'",
)

# LLM 초기화
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    openai_api_key=OPENAI_API_KEY,
)

# 시스템 메시지 정의
system_message = """당신은 한국어로만 응답하는 여행 가이드 AI입니다.
영어 사용은 절대 금지입니다.
모든 생각(Thought)과 응답을 반드시 한국어로 작성해야 합니다.

다음 규칙을 엄격하게 따르세요:
1. 맛집검색 도구를 사용할 때는 한국어로 입력하세요
2. 검색 과정에서의 모든 생각을 한국어로 표현하세요
3. 최종 답변은 다음 형식으로만 작성하세요:
   추천 맛집:
   - [식당이름], [음식종류], [가격대]

이 규칙들을 어기지 마세요.
영어로 된 답변은 실패로 간주됩니다."""

# 에이전트 초기화
agent = initialize_agent(
    tools=[restaurant_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    agent_kwargs={"system_message": system_message},
)

# 사용자 입력 처리
user_input = {"location": "부산 해운대", "num_people": "4명", "days": "2박 3일"}

# 에이전트 실행
response = agent.invoke(
    {
        "input": f"{user_input['location']} 지역에 {user_input['num_people']}이서 {user_input['days']} 동안 식사하려고 합니다. 맛집을 추천해주세요."
    }
)

# 결과 출력
print("추천된 맛집:")
print(response)
