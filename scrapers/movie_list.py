from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_movie_links(driver):
    base_url = "https://uflix.cc/movies"
    page = 1
    all_links = set()

    while True:
        url = f"{base_url}?page={page}"
        print(f"📄 Visiting page {page}: {url}")
        driver.get(url)

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a[href^="/movie/"]'))
            )
        except:
            print(f"⚠️ No movie links found or page took too long to load: {url}")
            break

        soup = BeautifulSoup(driver.page_source, "lxml")
        anchors = soup.select('a[href^="/movie/"]')

        if not anchors:
            print("❌ No anchors found—ending pagination.")
            break

        for a in anchors:
            href = a.get("href")
            if href and href.startswith("/movie/"):
                all_links.add("https://uflix.cc" + href)

        page += 1

    return list(all_links)
