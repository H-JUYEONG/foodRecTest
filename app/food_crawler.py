from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
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
options.add_argument('window-size=1920,1080')
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36')

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

try:
    # 네이버 지도 접속
    URL = 'https://map.naver.com/p/search/부산%20해운대%20음식점'
    driver.get(URL)
    time.sleep(3)  # 페이지 로딩 대기

    # iframe 전환
    switch_left()
    time.sleep(2)

    # 스크롤 처리
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # 검색 결과 수집
    places = driver.find_elements(By.CSS_SELECTOR, "li.UEzoS")
    print(f"총 {len(places)}개의 장소를 찾았습니다.")

    for i, place in enumerate(places, 1):
        try:
            # 가게 이름 클릭
            name_element = place.find_element(By.CSS_SELECTOR, "span.TYaxT")
            name = name_element.text
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
            print(f"\n{i}. {name}")
            print(f"카테고리: {category}")
            print(f"평점: {rating}")
            print(f"주소: {address}")
            print("-" * 50)

            # 다음 가게를 위해 검색 결과 프레임으로 전환
            switch_left()
            time.sleep(1)

        except Exception as e:
            print(f"가게 정보 수집 중 오류: {e}")
            switch_left()
            continue

except Exception as e:
    print(f"크롤링 중 오류 발생: {e}")

finally:
    driver.quit()
