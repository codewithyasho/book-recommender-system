# 📚 Book Recommender System Web App

A beautiful, responsive web application for book recommendations using machine learning and collaborative filtering. Built with Flask, featuring a modern purple, black, and white theme.

## ✨ Features

- **Popular Books Page**: Display top 100 books with highest ratings
- **Smart Recommendations**: AI-powered book suggestions based on user input
- **Responsive Design**: Mobile-friendly interface that works on all devices
- **Interactive UI**: Smooth animations, auto-complete search, and modern design
- **Real-time Search**: Autocomplete suggestions and instant results
- **Collaborative Filtering**: Advanced ML algorithm for accurate recommendations


### Installation

1. **Navigate to the project directory**:
   ```bash
   cd Book-recommender-system
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Open your browser** and visit:
   ```
   http://localhost:5000
   ```


## 🎯 Routes

### 1. **Homepage** (`/`)
- **Purpose**: Display popular books
- **Features**: 
  - Shows top 100 rated books
  - Filtering and sorting options
  - Quick recommendation buttons
  - Responsive grid layout

### 2. **Recommendations** (`/recommend`)
- **Purpose**: Get book recommendations
- **Features**:
  - Auto-complete search
  - Real-time suggestions
  - Similarity scoring
  - Detailed book information

### 3. **API Endpoints**
- `POST /get_recommendations`: Get book recommendations
- `GET /search_books`: Search for books (autocomplete)

## 🤖 How It Works

1. **Data Loading**: Loads pre-trained ML models and book data
2. **Similarity Calculation**: Uses cosine similarity for book matching
3. **Filtering**: Considers only knowledgeable users (200+ ratings) and popular books (50+ ratings)
4. **Recommendation**: Returns top 7 most similar books with similarity scores

## 🎨 Customization

### Changing Colors
Edit the CSS variables in `static/css/style.css`:
```css
:root {
    --primary-purple: #6a4c93;
    --secondary-purple: #8e44ad;
    --dark-purple: #4a2c5a;
    /* ... other colors */
}
```

## 🚀 Deployment

### For Production:

1. **Set environment variables**:
   ```bash
   export FLASK_ENV=production
   export FLASK_DEBUG=False
   ```

2. **Use a production server** (e.g., Gunicorn):
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

3. **Add a reverse proxy** (Nginx) for better performance



## 👨‍💻 Author

Created with ❤️ for book lovers everywhere.

---

**Happy Reading! 📚✨**
