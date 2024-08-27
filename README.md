Week 2 Report: Storing Data in MongoDB and Building a Flask API

Project Overview:

Objective: This week, I focused on storing the data collected from Al Mayadeen into a MongoDB database and developing a Flask API to provide various endpoints for querying and analyzing the data.
Accomplishments:

MongoDB Setup:

Installed MongoDB and configured it to run locally.
Connected to MongoDB using the pymongo library in Python.
Data Storage:

Created a script (data_storage.py) to load the JSON files generated in Week 1.
Inserted the data into a MongoDB collection named articles within a database called almayadeen.
Verified that the data was correctly stored and accessible within MongoDB.
Flask API Development:

Developed a Flask application (app.py) to provide API endpoints for querying the stored data.
Implemented a range of endpoints, including:
/top_keywords: Returns the top 10 most frequently used keywords.
/top_authors: Lists the top 10 authors by article count.
/articles_by_date: Returns the number of articles published on each date.
/articles_by_word_count: Groups articles by word count.
/recent_articles: Fetches the 10 most recently published articles.
/articles_by_language: Shows the number of articles available in each language.
Tested all endpoints to ensure they returned the correct data.
Error Handling:

Implemented error handling in both the data storage script and the Flask application to manage issues like empty databases or network failures.
Testing:

Used Postman and browser-based testing to verify the accuracy of the API responses.
Ensured that each endpoint returned the expected results and handled edge cases appropriately.
Current Progress:

Successfully stored all collected data in MongoDB and developed a fully functional Flask API.
The API provides comprehensive access to the stored data through various endpoints, allowing for detailed analysis.
Next Steps:

Optimize the API for better performance with larger datasets.
Explore additional analytical endpoints to provide more insights from the data
