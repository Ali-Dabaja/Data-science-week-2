from flask import Flask, jsonify, Response
from pymongo import MongoClient
from collections import Counter
from datetime import datetime, timedelta
import json
import re
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client['almayadeen']
collection = db['articles']

@app.route('/')
def home():
    return 'Welcome to the Articles API!'

# Custom jsonify function to ensure non-ASCII characters are handled properly
def custom_jsonify(data, status_code=200):
    return Response(
        response=json.dumps(data, ensure_ascii=False),
        mimetype='application/json',
        status=status_code
    )

# Endpoint to get the top keywords used in the articles
@app.route('/top_keywords', methods=['GET'])
def top_keywords():
    try:
        articles = collection.find({}, {'keywords': 1})
        all_keywords = []

        for article in articles:
            keywords = article.get('keywords', [])
            if isinstance(keywords, str):
                words = re.findall(r'\b\w+\b', keywords)
                all_keywords.extend(words)
            elif isinstance(keywords, list):
                all_keywords.extend(keywords)

        keyword_counts = Counter(all_keywords)
        top_keywords = keyword_counts.most_common(10)
        top_keywords_dict = {keyword: count for keyword, count in top_keywords}

        return custom_jsonify(top_keywords_dict)
    except Exception as e:
        logging.error(f"Error in /top_keywords: {e}")
        return custom_jsonify({"error": "An unexpected error occurred"}, 500)

# Endpoint to get the most frequent authors
@app.route('/top-authors', methods=['GET'])
def top_authors():
    try:
        articles = collection.find()
        author_list = [article.get('author') for article in articles if article.get('author')]

        top_authors = Counter(author_list).most_common(10)
        return custom_jsonify(top_authors)
    except Exception as e:
        logging.error(f"Error in /top-authors: {e}")
        return custom_jsonify({"error": "An unexpected error occurred"}, 500)

@app.route('/articles_by_date', methods=['GET'])
def articles_by_date():
    try:
        pipeline = [
            {
                "$group": {
                    "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$published_time"}},
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id": 1}}  # Sort by date (ascending)
        ]
        results = list(collection.aggregate(pipeline))
        articles_by_date = {result['_id']: result['count'] for result in results}

        return custom_jsonify(articles_by_date)
    except Exception as e:
        logging.error(f"Error in /articles_by_date: {e}")
        return custom_jsonify({"error": "An unexpected error occurred"}, 500)

@app.route('/articles_by_word_count', methods=['GET'])
def articles_by_word_count():
    try:
        pipeline = [
            {
                "$bucket": {
                    "groupBy": {"$strLenCP": "$content"},  # Calculate the word count
                    "boundaries": [0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000],
                    "default": "1000+",  # For articles with more than 1000 words
                    "output": {"count": {"$sum": 1}}
                }
            }
        ]
        results = list(collection.aggregate(pipeline))
        articles_by_word_count = {str(result['_id']): result['count'] for result in results}

        return custom_jsonify(articles_by_word_count)
    except Exception as e:
        logging.error(f"Error in /articles_by_word_count: {e}")
        return custom_jsonify({"error": "An unexpected error occurred"}, 500)

@app.route('/articles_by_language', methods=['GET'])
def articles_by_language():
    try:
        pipeline = [
            {
                "$project": {
                    "language": 1
                }
            },
            {
                "$group": {
                    "_id": {"$ifNull": ["$language", "Unknown"]},
                    "count": {"$sum": 1}
                }
            }
        ]
        results = list(collection.aggregate(pipeline))
        articles_by_language = {result['_id']: result['count'] for result in results}

        return custom_jsonify(articles_by_language)
    except Exception as e:
        logging.error(f"Error in /articles_by_language: {e}")
        return custom_jsonify({"error": "An unexpected error occurred"}, 500)

@app.route('/articles_by_classes', methods=['GET'])
def articles_by_classes():
    try:
        pipeline = [
            {"$unwind": "$classes"},
            {
                "$group": {
                    "_id": "$classes",
                    "count": {"$sum": 1}
                }
            }
        ]
        results = list(collection.aggregate(pipeline))
        articles_by_classes = {result['_id']: result['count'] for result in results}

        return custom_jsonify(articles_by_classes)
    except Exception as e:
        logging.error(f"Error in /articles_by_classes: {e}")
        return custom_jsonify({"error": "An unexpected error occurred"}, 500)

@app.route('/recent_articles', methods=['GET'])
def recent_articles():
    try:
        recent_articles = list(collection.find().sort('published_time', -1).limit(10))
        articles_list = [{"title": article.get("title"), "published_date": article.get("published_time").strftime('%Y-%m-%d')} for article in recent_articles]

        return custom_jsonify(articles_list)
    except Exception as e:
        logging.error(f"Error in /recent_articles: {e}")
        return custom_jsonify({"error": "An unexpected error occurred"}, 500)

@app.route('/articles_by_keyword/<keyword>', methods=['GET'])
def articles_by_keyword(keyword):
    try:
        articles = list(collection.find({"keywords": {"$regex": keyword, "$options": "i"}}))
        articles_list = [{"title": article.get("title"), "content": article.get("content", "")[:100]} for article in articles]

        return custom_jsonify(articles_list)
    except Exception as e:
        logging.error(f"Error in /articles_by_keyword/{keyword}: {e}")
        return custom_jsonify({"error": "An unexpected error occurred"}, 500)

@app.route('/articles_by_author/<author_name>', methods=['GET'])
def articles_by_author(author_name):
    try:
        articles = list(collection.find({"author": author_name}))
        articles_list = [{"title": article.get("title"), "content": article.get("content", "")[:100]} for article in articles]

        return custom_jsonify(articles_list)
    except Exception as e:
        logging.error(f"Error in /articles_by_author/{author_name}: {e}")
        return custom_jsonify({"error": "An unexpected error occurred"}, 500)

@app.route('/top_classes', methods=['GET'])
def top_classes():
    try:
        pipeline = [
            {"$unwind": "$classes"},
            {"$group": {"_id": "$classes", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        results = list(collection.aggregate(pipeline))
        top_classes = {result['_id']: result['count'] for result in results}

        return custom_jsonify(top_classes)
    except Exception as e:
        logging.error(f"Error in /top_classes: {e}")
        return custom_jsonify({"error": "An unexpected error occurred"}, 500)

@app.route('/article_details/<postid>', methods=['GET'])
def article_details(postid):
    try:
        article = collection.find_one({"postid": postid})
        if not article:
            return custom_jsonify({"error": "Article not found"}), 404

        article_details = {
            "URL": article.get("url"),
            "Title": article.get("title"),
            "Keywords": article.get("keywords", []),
            "Content": article.get("content"),
        }

        return custom_jsonify(article_details)
    except Exception as e:
        logging.error(f"Error in /article_details/{postid}: {e}")
        return custom_jsonify({"error": "An unexpected error occurred"}, 500)

@app.route('/articles_with_video', methods=['GET'])
def articles_with_video():
    try:
        articles = list(collection.find({"video_duration": {"$ne": None}}))
        articles_list = [{"title": article.get("title"), "content": article.get("content", "")[:100]} for article in articles]

        return custom_jsonify(articles_list)
    except Exception as e:
        logging.error(f"Error in /articles_with_video: {e}")
        return custom_jsonify({"error": "An unexpected error occurred"}, 500)

@app.route('/articles_by_year/<int:year>', methods=['GET'])
def articles_by_year(year):
    try:
        start_date = f"{year}-01-01T00:00:00Z"
        end_date = f"{year + 1}-01-01T00:00:00Z"
        count = collection.count_documents({"published_time": {"$gte": start_date, "$lt": end_date}})

        return custom_jsonify({str(year): count})
    except Exception as e:
        logging.error(f"Error in /articles_by_year/{year}: {e}")
        return custom_jsonify({"error": "An unexpected error occurred"}, 500)

if __name__ == '__main__':
    app.run(debug=True)
