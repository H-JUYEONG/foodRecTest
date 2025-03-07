from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
import time


def switch_left():
    try:
        driver.switch_to.default_content()
        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#searchIframe"))
        )
        driver.switch_to.frame(iframe)
    except Exception as e:
        print(f"iframe 전환 중 오류: {e}")


def switch_right():
    try:
        driver.switch_to.default_content()
        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#entryIframe"))
        )
        driver.switch_to.frame(iframe)
    except Exception as e:
        print(f"iframe 전환 중 오류: {e}")


# 웹드라이버 설정
options = webdriver.ChromeOptions()
options.add_argument("window-size=1920,1080")
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
)

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

try:
    # 네이버 지도 접속
    URL = "https://map.naver.com/p/search/부산%20해운대%20음식점"
    driver.get(URL)
    time.sleep(3)  # 페이지 로딩 대기

    # iframe 전환
    switch_left()
    time.sleep(2)

    # 개선된 스크롤 처리 - 더 명시적인 타겟팅과 여러 번 시도
    scroll_attempts = 15  # 스크롤 시도 횟수
    previous_count = 0

    for i in range(scroll_attempts):
        # 현재 목록 요소 수 확인
        current_places = driver.find_elements(By.CSS_SELECTOR, "li.UEzoS")
        current_count = len(current_places)

        print(
            f"스크롤 시도 {i+1}/{scroll_attempts}: 현재 {current_count}개 항목 로드됨"
        )

        # 결과 리스트 영역 찾기 시도
        try:
            # 검색 결과 컨테이너 요소 찾기
            container = driver.find_element(By.CSS_SELECTOR, "div.q8b2n")

            # 컨테이너 끝으로 스크롤
            driver.execute_script(
                "arguments[0].scrollTop = arguments[0].scrollHeight", container
            )
        except:
            # 컨테이너를 못 찾으면 일반 스크롤 시도
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # 페이지가 로드될 시간 주기
        time.sleep(3)

        # 새 항목이 로드되지 않으면 (두 번 연속) 종료
        if current_count == previous_count:
            print("더 이상 새로운 항목이 로드되지 않습니다. 스크롤 종료.")
            break

        previous_count = current_count

    # 최종 검색 결과 수집
    places = driver.find_elements(By.CSS_SELECTOR, "li.UEzoS")
    print(f"총 {len(places)}개의 장소를 찾았습니다.")

    for i, place in enumerate(places, 1):
        try:
            # 가게 이름 클릭
            name_element = place.find_element(By.CSS_SELECTOR, "span.TYaxT")
            name = name_element.text
            print(f"\n처리 중: {i}/{len(places)} - {name}")

            # 이름 요소가 보이지 않을 수 있으므로 스크롤하여 보이게 함
            driver.execute_script("arguments[0].scrollIntoView();", name_element)
            time.sleep(1)

            name_element.click()
            time.sleep(2)

            # 상세 정보 수집을 위해 iframe 전환
            switch_right()
            time.sleep(2)

            # 상세 정보 수집
            try:
                category = driver.find_element(By.CSS_SELECTOR, "span.lnJFt").text
            except:
                category = "정보 없음"

            try:
                rating = driver.find_element(By.CSS_SELECTOR, "span.PXMot").text
            except:
                rating = "평점 없음"

            try:
                address = driver.find_element(By.CSS_SELECTOR, "span.LDgIH").text
            except:
                address = "주소 정보 없음"

            # 정보 출력
            print(f"{i}. {name}")
            print(f"카테고리: {category}")
            print(f"평점: {rating}")
            print(f"주소: {address}")
            print("-" * 50)

            # 다음 가게를 위해 검색 결과 프레임으로 전환
            switch_left()
            time.sleep(1)

        except Exception as e:
            print(f"가게 정보 수집 중 오류: {e}")
            # 오류가 발생하면 다시 왼쪽 프레임으로 전환 시도
            try:
                switch_left()
            except:
                pass
            continue

except Exception as e:
    print(f"크롤링 중 오류 발생: {e}")

finally:
    driver.quit()
