# Web Scraper for News Summarization
This project is a web scraper system designed to receive URLs of news articles and generate concise summaries. Through a REST endpoint, the system allows users to send URLs, after which it crawls the articles, extracts the main content, and generates a summary.

_The system is initially configured to work only with [BBC](https://www.bbc.com/news) articles._

## Installation

Install all project dependencies:
```
pip install -r requirements.txt
```

This project stores data in a MongoDB Atlas cluster in JSON format. Make sure you have access to your Atlas cluster and configure the connection URI in the .env configuration file.


## Usage

Run the server with the following command:
```
uvicorn NewsWebScraper:app --reload
```

Make a POST request to http://localhost:8000 with a JSON body containing the productUrl field, as shown:
```
{
  "productUrl": "https://www.bbc.com/news/article-url" 
}
```

## Technologies Used
+ Python: Main programming language.
+ Transformers ([Hugging Face](https://huggingface.co/)): Specifically, the [BART](https://huggingface.co/facebook/bart-large-cnn) model by Meta AI, to automatically summarize long texts.
+ [MongoDB Atlas](https://www.mongodb.com/en/atlas): Cloud-based NoSQL database to store data in JSON format.
+ [FastAPI](https://fastapi.tiangolo.com/): High-performance web framework for creating the REST endpoint.
+ Requests: To make HTTP requests and retrieve page content.
+ BeautifulSoup: Tool for extracting and parsing HTML content from web pages.

## Project Structure
+ NewsWebScraper.py: Main file for server execution and request handling.
+ tokens.txt: Contains credentials for both the MongoDB database and the Hugging Face API token.
