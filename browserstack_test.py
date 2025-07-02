import os
import time
import threading
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from deep_translator import GoogleTranslator
from collections import Counter
from dotenv import load_dotenv

load_dotenv()
BROWSERSTACK_USERNAME = os.getenv("BROWSERSTACK_USERNAME")
BROWSERSTACK_ACCESS_KEY = os.getenv("BROWSERSTACK_ACCESS_KEY")
BROWSERSTACK_URL = f"http://{BROWSERSTACK_USERNAME}:{BROWSERSTACK_ACCESS_KEY}@hub-cloud.browserstack.com/wd/hub"

# configurations
CONFIGS = [
    {"os": "Windows", "osVersion": "10", "browserName": "Chrome", "browserVersion": "latest", "sessionName": "Chrome_Windows_Test"},
    {"os": "Windows", "osVersion": "11", "browserName": "Edge", "browserVersion": "latest", "sessionName": "Edge_Windows_Test"},
    {"os": "OS X", "osVersion": "Monterey", "browserName": "Safari", "browserVersion": "latest", "sessionName": "Safari_Mac_Test"},
    {"os": "OS X", "osVersion": "Ventura", "browserName": "Firefox", "browserVersion": "latest", "sessionName": "Firefox_Mac_Test"},
    {"os": "Windows", "osVersion": "10", "browserName": "Firefox", "browserVersion": "latest", "sessionName": "Firefox_Windows_Test"},
]

translated_titles = []
title_lock = threading.Lock()

def build_browserstack_options(capabilities):
    options = Options()
    options.set_capability("browserName", capabilities["browserName"])
    options.set_capability("browserVersion", capabilities["browserVersion"])
    options.set_capability("bstack:options", capabilities["bstack:options"])
    return options

def accept_cookies(driver):
    try:
        cookie_button = driver.find_element(By.ID, "didomi-notice-agree-button")
        cookie_button.click()
        time.sleep(2)
    except:
        pass

def translate_title(text):
    try:
        return GoogleTranslator(source='auto', target='en').translate(text)
    except Exception as e:
        print(f"[Translation Error] {text} → {e}")
        return "untranslated " + text

def extract_articles(driver, name):
    articles = driver.find_elements(By.CSS_SELECTOR, 'article.c')[:5]
    print(f"\n[{name}] Found {len(articles)} articles")

    for i, article in enumerate(articles):
        try:
            title_el = article.find_element(By.CSS_SELECTOR, 'h2.c_t a, h2.c_t-i a')
            title = title_el.text.strip()
            translated = translate_title(title)

            with title_lock:
                translated_titles.append(translated)

            try:
                desc_el = article.find_element(By.CLASS_NAME, 'c_d')
                description = desc_el.text.strip()
            except:
                description = "No description"

            try:
                img_el = article.find_element(By.CSS_SELECTOR, 'img')
                img_url = img_el.get_attribute('src')
            except:
                img_url = "No image"

            print(f"[{name}] Article {i+1}:")
            print(f"  Title (ES): {title}")
            print(f"  Title (EN): {translated}")
            print(f"  Description: {description}")
            print(f"  Image: {img_url}")

        except Exception as e:
            print(f"[{name}] Error parsing article {i+1}: {e}")

def run_browserstack_test(name, capabilities):
    driver = None
    try:
        options = build_browserstack_options(capabilities)
        driver = webdriver.Remote(command_executor=BROWSERSTACK_URL, options=options)

        driver.get("https://elpais.com/opinion/")
        time.sleep(3)

        accept_cookies(driver)
        extract_articles(driver, name)

        driver.execute_script('browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"passed", "reason": "Scraped successfully"}}')

    except Exception as e:
        print(f"[{name}] Error in session: {e}")
    finally:
        if driver:
            driver.quit()

def start_parallel_tests():
    threads = []
    for conf in CONFIGS:
        name = conf["sessionName"]
        capabilities = {
            "browserName": conf["browserName"],
            "browserVersion": conf["browserVersion"],
            "bstack:options": {
                "os": conf["os"],
                "osVersion": conf["osVersion"],
                "sessionName": name,
                "seleniumVersion": "4.20.0"
            }
        }

        thread = threading.Thread(target=run_browserstack_test, args=(name, capabilities))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

def analyze_word_frequency():
    print("\n Translated Titles Collected:")
    for i, t in enumerate(translated_titles, 1):
        print(f"{i}. {t}")

    all_words = []
    for title in translated_titles:
        clean = re.sub(r"[^\w\s]", "", title)  # remove punctuation
        all_words.extend(clean.lower().split())

    if not all_words:
        print("\n No words found in translated titles!")
        return

    counter = Counter(all_words)
    print("\n Word Frequency in Translated Titles:")
    for word, count in counter.most_common(10):
        print(f"{word}: {count}")

if __name__ == "__main__":
    start_parallel_tests()
    analyze_word_frequency()
