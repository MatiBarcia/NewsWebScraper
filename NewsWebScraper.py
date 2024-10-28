from bs4 import BeautifulSoup
import requests
import nltk
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from collections import defaultdict
from fastapi import FastAPI, HTTPException
from pymongo import MongoClient

nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')

app = FastAPI()

with open("mongo.txt", "r") as f:
    lines = f.read().splitlines()
    client_uri = lines[0]
    db_name = lines[1]
    collection_name = lines[2]

# Configuración de MongoDB Atlas
client = MongoClient(client_uri)
db = client[db_name]
collection = db[collection_name]

def summarize_text(text, language, num_sentences=2):
    # Tokenizar el texto en oraciones
    sentences = sent_tokenize(text)
    
    # Validar que el texto tenga suficientes oraciones para el resumen
    if len(sentences) < 2:
        return "Text is too short to summarize."
    
    # Tokenizar palabras y calcular frecuencias excluyendo stopwords
    
    dict_lang = {
        "en-GB": "english",
        "en-US": "english",
        "es": "spanish",
        "fr": "french"
    }
    
    stop_words = set(stopwords.words(dict_lang.get(language)))
    words = word_tokenize(re.sub(r'\W', ' ', text.lower()))
    frequencies = defaultdict(int)

    for word in words:
        if word not in stop_words:
            frequencies[word] += 1

    # Calcular la puntuación de cada oración según las frecuencias de palabras
    sentence_score = defaultdict(int)
    for sentence in sentences:
        for word in word_tokenize(sentence.lower()):
            if word in frequencies:
                sentence_score[sentence] += frequencies[word]

    # Seleccionar las oraciones con puntuaciones más altas para el resumen
    important_sentences = sorted(sentence_score, key=sentence_score.get, reverse=True)
    summary = ' '.join(important_sentences[:num_sentences])

    return summary

def fetch_article_content(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    
    title = soup.find("h1")
    title_text = title.get_text() if title else "Title not available."
    
    language = soup.html.get("lang")
    
    if "bbc.com" in url:
        if "/sport/" in url:
            article = soup.find_all("div", class_="ssrcss-7uxr49-RichTextContainer e5tfeyi1")
            article_text = ''
            for p in article:
                article_text = article_text + p.get_text()
        elif "/mundo/" in url or "/afrique/" in url:
            article = soup.find_all("div", class_="bbc-19j92fr ebmt73l0")
            article_text = ''
            for p in article:
                article_text = article_text + p.get_text()
        elif "/news/" in url or "/travel/" in url or "/culture/" in url:
            article = soup.find("article")
            article_text = article.get_text() if article else "Content not available."
        elif "/live/" in url:
            article = soup.find("div", class_="ssrcss-1o5f7ft-BulletListContainer e5tfeyi0")
            article_text = article.get_text() if article else "Content not available."
            
        return title_text, article_text, language
    else:
        print("I don't know that URL")

@app.post("/")
async def summarize_article(productUrl: str):
    existing_article = collection.find_one({"url": productUrl})
    if existing_article:
        return {
            "title": existing_article["title"],
            "summary": existing_article["summary"]
        }
    
    title, article_text, language = fetch_article_content(productUrl)
        
    if article_text == "Content not available.":
        raise HTTPException(status_code=404, detail="No se encontró el contenido del artículo")

    if "/live/" not in productUrl:
        summary = summarize_text(article_text, language)
    else: 
        summary = article_text

    new_article = {
        "url": productUrl,
        "title": title,
        "summary": summary
    }
    collection.insert_one(new_article)

    return {
        "title": title,
        "summary": summary
    }