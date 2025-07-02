import os
import time
import re
import requests
from collections import Counter
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from deep_translator import GoogleTranslator

def setup_driver():
    # Initializes and returns a Chrome WebDriver instance
    options = Options()
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    return driver

def accept_cookie_banner(driver):
    # accept cookie banner
    try:
        agree_button = driver.find_element(By.ID, "didomi-notice-agree-button")
        agree_button.click()
        print("Cookie banner accepted")
        time.sleep(2)
    except:
        print("No cookie banner found")

def extract_articles(driver, max_articles=5):
    # Scrapes and returns the first 5 valid articles
    articles = driver.find_elements(By.CSS_SELECTOR, 'article.c')
    print(f"Found {len(articles)} article containers")
    return articles[:max_articles]

def download_image(url, filename):
    # Takes image from URL to local filename
    try:
        img_data = requests.get(url).content
        with open(filename, 'wb') as f:
            f.write(img_data)
        return True
    except:
        return False

def process_articles(articles):
    # Returns original and translated titles
    os.makedirs("images", exist_ok=True)
    titles = []
    translated_titles = []

    for i, article in enumerate(articles):
        try:
            title_el = article.find_element(By.CSS_SELECTOR, 'h2.c_t a, h2.c_t-i a, h2.c_t a')
            title = title_el.text.strip()
            url = title_el.get_attribute('href')
            titles.append(title)

            try:
                desc_el = article.find_element(By.CLASS_NAME, 'c_d')
                description = desc_el.text.strip()
            except:
                description = "No description"

            try:
                img_el = article.find_element(By.CSS_SELECTOR, 'img')
                img_url = img_el.get_attribute('src')
                image_path = f"images/article_{i+1}.jpg"
                image_saved = download_image(img_url, image_path)
            except:
                img_url = None
                image_saved = False

            print(f"\n Article {i+1}")
            print(f"Title: {title}")
            print(f"URL: {url}")
            print(f"Description: {description}")
            print(f"Image: {'Saved' if image_saved else 'Not found'}")

        except Exception as e:
            print(f"Error processing article {i+1}: {e}")
            continue

    # Translate Titles
    print("\n Translated Titles:")
    for i, title in enumerate(titles):
        try:
            translated = GoogleTranslator(source='auto', target='en').translate(title)
            translated_titles.append(translated)
            print(f"{i+1}. {translated}")
        except Exception as e:
            print(f"{i+1}. Translation failed for '{title}': {e}")
            translated_titles.append("Translation failed")

    return translated_titles


def analyze_word_frequency(translated_titles):
    # Count frequency analysis on translated titles
    words = []
    for title in translated_titles:
        if title != "Translation failed":
            clean_text = re.sub(r'[^\w\s]', '', title).lower()
            words.extend(clean_text.split())

    word_counts = Counter(words)
    repeated = {word: count for word, count in word_counts.items() if count > 2}

    print("\n Repeated Words (More Than Twice):")
    if repeated:
        for word, count in repeated.items():
            print(f"{word}: {count}")
    else:
        print("No word repeated more than twice")

def main():
    driver = setup_driver()
    driver.get("https://elpais.com/opinion/")
    time.sleep(10)

    accept_cookie_banner(driver)
    articles = extract_articles(driver, max_articles=5)
    translated_titles = process_articles(articles)
    analyze_word_frequency(translated_titles)

    driver.quit()

if __name__ == "__main__":
    main()
