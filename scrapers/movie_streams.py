from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

def robust_get(driver, url, retries=3, wait=2):
    for attempt in range(1, retries + 1):
        try:
            driver.get(url)
            return True
        except TimeoutException:
            print(f"⏳ Retry {attempt}/{retries} for {url}")
            time.sleep(wait)
    print(f"❌ Failed to load after {retries} attempts: {url}")
    return False

def extract_streams(driver, url):
    if not robust_get(driver, url):
        return None

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
    except:
        print(f"⚠️ Timed out waiting for: {url}")

    soup = BeautifulSoup(driver.page_source, "lxml")

    title = soup.find("h1").text if soup.find("h1") else "Unknown"
    streams = [a["href"] for a in soup.find_all("a") if "Stream #" in a.text]
    genres = [a.text.strip() for a in soup.select('a[href^="/genre/"]')]

    year = None
    year_tag = soup.select_one(".badge.bg-primary")
    if year_tag and year_tag.text.strip().isdigit():
        year = int(year_tag.text.strip())

    rating = None
    rating_tag = soup.find("span", class_="imdb")
    if rating_tag:
        rating = rating_tag.text.strip()

    return {
        "title": title,
        "url": url,
        "genres": genres,
        "streams": streams,
        "year": year,
        "rating": rating
    }
