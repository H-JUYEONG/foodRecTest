from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, NoSuchElementException
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


# 각 페이지의 데이터 수집 함수
def collect_page_data(page_num):
    # 검색 결과 수집
    places = driver.find_elements(By.CSS_SELECTOR, "li.UEzoS")
    print(f"페이지 {page_num}에서 {len(places)}개의 장소를 찾았습니다.")

    for i, place in enumerate(places, 1):
        try:
            # 가게 이름 클릭
            name_element = place.find_element(By.CSS_SELECTOR, "span.TYaxT")
            name = name_element.text
            print(f"\n처리 중: 페이지 {page_num} - {i}/{len(places)} - {name}")

            # 이름 요소가 보이도록 스크롤
            driver.execute_script("arguments[0].scrollIntoView();", name_element)
            time.sleep(1)

            # 클릭 시도
            try:
                WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            f"//span[contains(@class, 'TYaxT') and text()='{name}']",
                        )
                    )
                )
                name_element.click()
            except:
                # 클릭이 안되면 JavaScript로 클릭 시도
                driver.execute_script("arguments[0].click();", name_element)

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
            time.sleep(3)

        except Exception as e:
            print(f"가게 정보 수집 중 오류: {e}")
            try:
                switch_left()
            except:
                pass
            continue


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

    # 페이지네이션 처리
    total_pages = 5  # 수집할 최대 페이지 수

    for current_page in range(1, total_pages + 1):
        print(f"\n=== 페이지 {current_page} 처리 시작 ===\n")

        # 현재 페이지 데이터 수집
        collect_page_data(current_page)

        # 다음 페이지로 이동 (마지막 페이지가 아니면)
        if current_page < total_pages:
            try:
                # 페이지 번호 찾기 (mBN2s 클래스를 가진 버튼들)
                page_buttons = driver.find_elements(By.CSS_SELECTOR, "a.mBN2s")

                # 다음 페이지 번호 찾기
                next_page_button = None
                for button in page_buttons:
                    if button.text == str(current_page + 1):
                        next_page_button = button
                        break

                if next_page_button:
                    print(f"페이지 {current_page + 1}로 이동합니다.")
                    # 버튼이 보이도록 스크롤
                    driver.execute_script(
                        "arguments[0].scrollIntoView();", next_page_button
                    )
                    time.sleep(1)
                    # JavaScript로 클릭 시도 (더 안정적)
                    driver.execute_script("arguments[0].click();", next_page_button)
                    time.sleep(1)  # 페이지 로드 대기
                else:
                    print(f"페이지 {current_page + 1} 버튼을 찾을 수 없습니다.")
                    break
            except Exception as e:
                print(f"다음 페이지로 이동 중 오류 발생: {e}")
                break

    print("\n=== 크롤링 완료 ===\n")

except Exception as e:
    print(f"크롤링 중 오류 발생: {e}")

finally:
    driver.quit()
