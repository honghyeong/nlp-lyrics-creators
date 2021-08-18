from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait
import pandas as pd
import time

def crawler():

    naver_id = input("네이버 아이디를 입력하세요: ")
    naver_pwd = input("네이버 비밀번호를 입력하세요: ")

    search_artists = input("검색할 가수를 쉼표와 띄어쓰기로 구분해서 입력하세요: ")
    search_artists = search_artists.split(', ')
    print('다음 가수들의 가사를 가져옵니다: ',search_artists)

    #로그인을 안하면 19금 걸린 노래를 못들어가서 로그인 필요!
    options = ChromeOptions()
    options.add_argument('--headless')

    driver = webdriver.Chrome(
        executable_path='/Users/jonghyunlee/opt/anaconda3/pkgs/python-chromedriver-binary-92.0.4515.43.0-py38h50d1736_0/lib/python3.8/site-packages/chromedriver_binary/chromedriver')
    #이부분은 각자의 크롬드라이버 절대경로 설정해야해!
    driver.maximize_window()
    vibe = "https://vibe.naver.com/"
    driver.get(vibe)
    popup = driver.find_element_by_xpath('//*[@id="app"]/div[2]/div/div/a[2]')
    popup.click()
    #지금 무슨 이벤트하는거같아서 팝업이 뜨는거같은데 만약 나중에 이벤트 끝나면 위 두라인은 주석처리하면 돼!

    loginbutton = driver.find_element_by_xpath('/html/body/div/div/header/div[2]/div[1]/a/span')
    loginbutton.click()
    id_input = driver.find_element_by_xpath('/html/body/div[2]/div[3]/div/form/fieldset/div[1]/div[1]/span/input')
    pwd_input = driver.find_element_by_xpath('/html/body/div[2]/div[3]/div/form/fieldset/div[2]/div[1]/span/input')
    final_login = driver.find_element_by_xpath('/html/body/div[2]/div[3]/div/form/fieldset/input')
    id_input.send_keys(naver_id)
    pwd_input.send_keys(naver_pwd)
    final_login.click()
    #여기가 로그인하는부분

    for artist in search_artists:
        driver.get(vibe)
        time.sleep(1)
        searchbutton = driver.find_element_by_xpath('//*[@id="header"]/a[1]')
        searchbar = driver.find_element_by_xpath('//*[@id="search_keyword"]')
        searchbutton.click()
        searchbar.click()

        searchbar.send_keys(artist)
        searchbar.send_keys(Keys.ENTER)
        searchbar.send_keys(Keys.ESCAPE)
        #여기가 검색 입력하는 부분

        wait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div[1]/div/a/div[2]/div[1]/div'))).click()
        time.sleep(1)
        #여기가 검색한 아티스트 입력하는 부분(인기 검색 결과)

        driver.find_element_by_xpath('//*[@id="content"]/div[2]/h3/a').click()
        time.sleep(0.5)

        try:
            driver.find_element_by_css_selector('#content > div:nth-child(1) > div.summary_section > div.summary_thumb > img')
            time.sleep(1)
            driver.back()
            driver.find_element_by_xpath('//*[@id="content"]/div[3]/h3/a').click()

        except NoSuchElementException:
            pass
        #가수의 노래 목록 들어가는 부분

        time.sleep(1)
        while True:
            try:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                showmore = driver.find_element_by_xpath('/html/body/div/div/div[3]/div/div/div[3]/div[2]/a/span')
                showmore.click()
                time.sleep(1)
            except NoSuchElementException:
                break
        #곡이 많은 가수들은 곡 더보기를 눌러줘야 전체 목록이 뜨더라고! 아닌 가수는 그냥 패스

        nums = list(range(1, 500))
        links = []

        time.sleep(1)

        for num in nums:
            try:
                links.append(driver.find_element_by_xpath(f'//*[@id="content"]/div/div[3]/div[1]/div/\
                    table/tbody/tr[{num}]/td[3]/div[1]/span/a').get_attribute('href'))

            except NoSuchElementException:
                break
        #여기가 모든 노래의 링크 긁어오는 부분

        linknumbers = [link[29:] for link in links]
        #링크의 중요한 키만 남기고 지우는 부분

        lyrics = []
        titles = []

        for linknumber in linknumbers:
            try:
                driver.get("https://vibe.naver.com/track/" + str(linknumber))
                time.sleep(0.5)
                title = driver.find_element_by_class_name("title")
                lyric = driver.find_element_by_class_name("lyrics")
                titles.append(title.text)
                lyrics.append(lyric.text)
                time.sleep(0.5)

            except NoSuchElementException:
                continue
        #여기서 실제로 모든 링크 하나씩 들어가면서 제목이랑 가사 긁어와줘!

        titles = [_[3:] for _ in titles]
        #제목 "곡명\n" 지우는 전처리

        lyrics_new = []
        for i in lyrics:
            lyrics_new.append(i.replace("\n", " "))
        lyrics_new
        #가사마다 행변환 부분 삭제

        crawled = pd.DataFrame({"제목": titles, "가사": lyrics_new})
        crawled.to_excel(f'{artist} 가사 crawling.xlsx', encoding='utf-8')
        #저장!!

if __name__ == '__main__':
    crawler()


