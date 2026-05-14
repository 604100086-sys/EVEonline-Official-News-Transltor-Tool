import nltk
import torch
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import random
import re
import csv
import os
from nltk.corpus import stopwords
from nltk import word_tokenize, pos_tag, RegexpParser
from playwright.sync_api import sync_playwright
from collections import Counter


url = 'https://www.eveonline.com/news/archive'
base = 'https://www.eveonline.com'
HEADERS =  {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

def fetch_html(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(5000)  # 等JS加载
        html = page.content()
        browser.close()
        return html

def remove_special_characters(text):
    # 使用正则表达式去除特殊字符
    cleaned_text = re.sub(r'[^\x00-\x7F]+', '', text)
    return cleaned_text

list_html = fetch_html(url)
if not list_html:
    raise SystemExit("列表页抓取失败，程序终止。")
list_soup = BeautifulSoup(list_html, 'html.parser')
links = []
results = []
articles = list_soup.select('article div h3 a')


for a in articles:
    title = a.get_text(strip=True)
    link = a.get("href")
    full_link = urljoin(base, link)
    links.append(full_link)
    results.append({"title": title})

for i, link in enumerate(links):
    detail_html = fetch_html(link)
    if not detail_html:
        results[i]['text'] = ""
        continue
    detail_soup = BeautifulSoup(detail_html, 'html.parser')
    content = detail_soup.select('p')
    if content:
        text = ' '.join(c.get_text(' ', strip=True) for c in content)
    else:
        text = ' '
    results[i]['text'] = remove_special_characters(text.lower())
    time.sleep(random.uniform(1, 2))
print(results)

all_terms = []

for item in results:
    text = item["text"]
    tokens = word_tokenize(text)
    tags = pos_tag(tokens)
    grammar = 'NP: {<NN.*|JJ>*<NN.*>}'
    cp = RegexpParser(grammar)
    tree = cp.parse(tags)

    stop_words = set(stopwords.words('english'))

    for subtree in tree:
        if isinstance(subtree, nltk.Tree) and subtree.label() == "NP":
            words = [w.lower() for w, t in subtree.leaves() if w.lower() not in stop_words]
            terms = " ".join(words)
            all_terms.append(terms)
all_terms = Counter(all_terms)
print(all_terms)
save_dir = "terms"
os.makedirs(save_dir, exist_ok=True)
file_path = os.path.join(save_dir, "terms.csv")
with open(file_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["term", "frequency"])
    for term, freq in all_terms.most_common():
        writer.writerow([term, freq])
