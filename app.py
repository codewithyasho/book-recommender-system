from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import joblib
from sklearn.metrics.pairwise import cosine_similarity
import os

app = Flask(__name__)

# Load the pre-trained models and data
import os
import sys

print("Current working directory:", os.getcwd())
print("Files in current directory:", os.listdir('.'))

try:
    # Check if files exist
    required_files = ['popular_books.csv', 'books.pkl', 'final_ratings_table.pkl', 'similarity_score.pkl']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"Missing files: {missing_files}")
        raise FileNotFoundError(f"Required data files not found: {missing_files}")
    
    # Load data from current directory (since app.py is now in the same folder as data files)
    print("Loading popular_books.csv...")
    popular_df = pd.read_csv('popular_books.csv')
    print(f"Popular books loaded: {len(popular_df)} rows")
    
    print("Loading books.pkl...")
    try:
        books = joblib.load('books.pkl')
        print(f"Books loaded: {len(books) if hasattr(books, '__len__') else 'unknown'}")
    except Exception as pkl_error:
        print(f"Error loading books.pkl: {pkl_error}")
        print("Attempting to recreate from CSV...")
        try:
            # Try to load from CSV and recreate the books dataframe
            books_csv = pd.read_csv('Books.csv')
            print(f"Loaded Books.csv with {len(books_csv)} rows")
            books = books_csv[['ISBN', 'Book-Title', 'Book-Author', 'Year-Of-Publication', 'Publisher', 'Image-URL-S', 'Image-URL-M', 'Image-URL-L']].copy()
            books.columns = ['ISBN', 'Book-Title', 'Book-Author', 'Year-Of-Publication', 'Publisher', 'Image-URL-S', 'Image-URL-M', 'Image-URL-L']
            print(f"Recreated books dataframe: {len(books)} rows")
        except Exception as csv_error:
            print(f"Error loading from CSV: {csv_error}")
            books = pd.DataFrame()
    
    print("Loading final_ratings_table.pkl...")
    try:
        final_ratings_table = joblib.load('final_ratings_table.pkl')
        print(f"Ratings table loaded: {final_ratings_table.shape if hasattr(final_ratings_table, 'shape') else 'unknown'}")
    except Exception as pkl_error:
        print(f"Error loading final_ratings_table.pkl: {pkl_error}")
        print("Attempting to recreate from CSV...")
        try:
            # Load the CSV file that should contain the ratings table
            ratings_csv = pd.read_csv('final_ratings_table.csv')
            final_ratings_table = ratings_csv
            print(f"Recreated ratings table: {final_ratings_table.shape}")
        except Exception as csv_error:
            print(f"Error loading ratings CSV: {csv_error}")
            final_ratings_table = pd.DataFrame()
    
    print("Loading similarity_score.pkl...")
    try:
        similarity_score = joblib.load('similarity_score.pkl')
        print(f"Similarity scores loaded: {similarity_score.shape if hasattr(similarity_score, 'shape') else 'unknown'}")
    except Exception as pkl_error:
        print(f"Error loading similarity_score.pkl: {pkl_error}")
        print("Creating empty similarity matrix...")
        similarity_score = np.array([])

    print("All data loaded successfully!")
    
except Exception as e:
    print(f"Error loading data: {e}")
    print("Creating empty data structures...")
    # Create dummy data for testing
    popular_df = pd.DataFrame()
    books = pd.DataFrame()
    final_ratings_table = pd.DataFrame()
    similarity_score = np.array([])


def recommend_books(book_name):
    """Recommend books based on similarity"""
    try:
        # Check if we have the necessary data
        if final_ratings_table.empty or similarity_score.size == 0:
            print("Warning: Required data not available for recommendations")
            return []
        
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
        # Check if popular_df has data
        if popular_df.empty:
            print("Warning: popular_df is empty!")
            return render_template('index.html', books=[], error_message="Data not loaded properly")
        
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

        print(f"Sending {len(popular_books)} books to template")
        return render_template('index.html', books=popular_books)
    except Exception as e:
        print(f"Error in index route: {e}")
        return render_template('index.html', books=[], error_message=str(e))


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


@app.route('/debug')
def debug():
    """Debug route to check data loading status"""
    debug_info = {
        'cwd': os.getcwd(),
        'files': os.listdir('.'),
        'popular_df_shape': popular_df.shape if not popular_df.empty else "Empty",
        'books_shape': books.shape if hasattr(books, 'shape') and not books.empty else "Empty", 
        'ratings_shape': final_ratings_table.shape if hasattr(final_ratings_table, 'shape') and not final_ratings_table.empty else "Empty",
        'similarity_shape': similarity_score.shape if hasattr(similarity_score, 'shape') and similarity_score.size > 0 else "Empty"
    }
    return jsonify(debug_info)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
