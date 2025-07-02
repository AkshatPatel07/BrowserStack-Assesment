# El País Scraper using Selenium and BrowserStack

This script uses Selenium via BrowserStack to scrape the opinion section of El País (https://elpais.com/opinion/), translates article titles to English using Deep Translator, and performs word frequency analysis.

## Features
- Cross-browser testing via BrowserStack (Chrome, Edge, Safari, Firefox)
- Multithreaded scraping (5 browsers in parallel)
- Translation to English (via Deep Translator)
- Top word frequency analysis
- Outputs image URLs, descriptions, and titles

## Requirements

- Python 3.8+
- Selenium
- Deep Translator
- dotenv

## Note
The local_test.py file runs the selenium code on your local machine, and the browserstack_test.py file runs the code on Browserstack with 5 Threads.
