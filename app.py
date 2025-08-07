from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import joblib
from sklearn.metrics.pairwise import cosine_similarity
import os

app = Flask(__name__)

# Load the pre-trained models and data
try:
    # Load data from current directory (since app.py is now in the same folder as data files)
    popular_df = pd.read_csv('popular_books.csv')
    books = joblib.load('books.pkl')
    final_ratings_table = joblib.load('final_ratings_table.pkl')
    similarity_score = joblib.load('similarity_score.pkl')

    print("All data loaded successfully!")
except Exception as e:
    print(f"Error loading data: {e}")
    # Create dummy data for testing
    popular_df = pd.DataFrame()
    books = pd.DataFrame()
    final_ratings_table = pd.DataFrame()
    similarity_score = np.array([])


def recommend_books(book_name):
    """Recommend books based on similarity"""
    try:
        book_name = book_name.lower().strip()

        # Check if book exists in our dataset
        if book_name not in final_ratings_table.index:
            return []

        # Get the index of the book
        book_index = np.where(final_ratings_table.index == book_name)[0][0]

        # Find similar books
        similar_books = sorted(
            list(enumerate(similarity_score[book_index])),
            key=lambda x: x[1],
            reverse=True
        )[1:8]  # Top 7 similar books (excluding the book itself)

        recommendations = []
        for i in similar_books:
            # Get book details
            book_title = final_ratings_table.index[i[0]]
            temp_df = books[books['Book-Title'].str.lower() == book_title]

            if not temp_df.empty:
                book_data = temp_df.drop_duplicates("Book-Title").iloc[0]
                recommendations.append({
                    'title': book_data['Book-Title'],
                    'author': book_data['Book-Author'],
                    'year': book_data['Year-Of-Publication'],
                    'image': book_data['Image-URL-M'],
                    'similarity': round(i[1] * 100, 2)
                })

        return recommendations
    except Exception as e:
        print(f"Error in recommendation: {e}")
        return []


@app.route('/')
def index():
    """Landing page with popular books"""
    try:
        # Convert popular_df to list of dictionaries for template
        popular_books = []
        for _, row in popular_df.iterrows():
            popular_books.append({
                'title': row['Book-Title'],
                'author': row['Book-Author'],
                'year': row['Year-Of-Publication'],
                'image': row['Image-URL-M'],
                'num_ratings': row['num_ratings'],
                'avg_rating': round(row['avg_rating'], 2)
            })

        return render_template('index.html', books=popular_books)
    except Exception as e:
        print(f"Error in index route: {e}")
        return render_template('index.html', books=[])


@app.route('/recommend')
def recommend():
    """Recommendation page"""
    return render_template('recommend.html')


@app.route('/get_recommendations', methods=['POST'])
def get_recommendations():
    """API endpoint to get book recommendations"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'})

        book_name = data.get('book_name', '').strip()

        if not book_name:
            return jsonify({'error': 'Please enter a book name'})

        recommendations = recommend_books(book_name)

        if not recommendations:
            # Get available books for suggestion
            # First 20 books as suggestions
            available_books = list(final_ratings_table.index[:20])
            return jsonify({
                'error': f'Book "{book_name}" not found in our database.',
                'suggestions': available_books
            })

        return jsonify({'recommendations': recommendations})

    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'})


@app.route('/search_books')
def search_books():
    """API endpoint to search for books (for autocomplete)"""
    try:
        query = request.args.get('q', '').lower().strip()

        if len(query) < 2:
            return jsonify([])

        # Search in available books
        matching_books = []
        for book_title in final_ratings_table.index:
            if query in book_title.lower() and len(matching_books) < 10:
                matching_books.append(book_title.title())

        return jsonify(matching_books)

    except Exception as e:
        return jsonify([])


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
