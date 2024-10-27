from bs4 import BeautifulSoup
import requests
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from collections import defaultdict
import re
from fastapi import FastAPI, HTTPException
from pymongo import MongoClient

nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')

app = FastAPI()

# Configuración de MongoDB Atlas
client = MongoClient("mongodb+srv://Cluster87795:challenge123@cluster-articles.xsywn.mongodb.net/?retryWrites=true&w=majority&appName=Cluster-Articles")
db = client["news_summary"]
collection = db["articles"]

def summarize_text(text, num_sentences=1):
    # Tokenizar el texto en oraciones
    sentences = sent_tokenize(text)
    
    # Validar que el texto tenga suficientes oraciones para el resumen
    if len(sentences) < 2:
        return "Text is too short to summarize."
    
    # Tokenizar palabras y calcular frecuencias excluyendo stopwords
    stop_words = set(stopwords.words("english"))
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
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.find("h1")
        title_text = title.get_text() if title else "Título no disponible"
        
        article = soup.find("article")
        article_text = article.get_text() if article else "Contenido no disponible"

        return title_text, article_text

    except requests.RequestException:
        raise HTTPException(status_code=400, detail="Error al hacer la solicitud al artículo")

@app.post("/")
async def summarize_article(productUrl: str):
    existing_article = collection.find_one({"url": productUrl})
    if existing_article:
        return {
            "title": existing_article["title"],
            "summary": existing_article["summary"]
        }
    
    title, article_text = fetch_article_content(productUrl)
    if article_text == "Contenido no disponible":
        raise HTTPException(status_code=404, detail="No se encontró el contenido del artículo")

    summary = summarize_text(article_text)

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