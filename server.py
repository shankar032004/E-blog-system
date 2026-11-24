from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_bcrypt import Bcrypt
import jwt
import datetime
import re
import heapq
import nltk
from deep_translator import GoogleTranslator
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from textblob import TextBlob
import speech_recognition as sr
import os
import json
import secrets
from werkzeug.utils import secure_filename

# Download NLTK dependencies
try:
    nltk.download('stopwords', quiet=True)
    nltk.download('punkt', quiet=True) 
    nltk.download('wordnet', quiet=True)
except:
    pass

# Initialize Flask App
app = Flask(__name__)
CORS(app)
bcrypt = Bcrypt(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or secrets.token_hex(16)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
db = SQLAlchemy(app)

# ================== MODELS ==================
class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(150), default="Anonymous")
    date = db.Column(db.String(50), default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    image = db.Column(db.String(255), default="https://via.placeholder.com/400x200")
    category = db.Column(db.String(100), default="General")
    views = db.Column(db.Integer, default=0)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.String(50), default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# Create tables and add sample data
def init_db():
    with app.app_context():
        db.create_all()

        # Add sample blogs if none exist
        if Blog.query.count() == 0:
            sample_blogs = [
                {
                    "title": "Getting Started with AI and Machine Learning",
                    "content": "Artificial Intelligence and Machine Learning are revolutionizing the way we interact with technology. This comprehensive guide will take you through the fundamentals of AI, covering everything from basic concepts to advanced applications. Whether you're a beginner looking to understand the basics or an experienced developer wanting to expand your knowledge, this post provides valuable insights into the world of AI. We'll explore different types of machine learning, including supervised learning, unsupervised learning, and reinforcement learning. Additionally, we'll discuss real-world applications and future trends in the field.",
                    "author": "Tech Explorer",
                    "category": "Technology",
                    "image": "https://images.unsplash.com/photo-1555949963-aa79dcee981c?w=400"
                },
                {
                    "title": "The Art of Creative Writing: Tips and Techniques",
                    "content": "Creative writing is a beautiful art form that allows us to express our thoughts, emotions, and imagination through words. In this post, we'll explore various techniques that can help you become a better writer. From developing compelling characters to creating engaging plots, we'll cover all the essential elements of storytelling. We'll also discuss the importance of finding your unique voice as a writer and how to overcome common challenges like writer's block. Whether you're writing fiction, poetry, or creative non-fiction, these tips will help you improve your craft and connect with your readers on a deeper level.",
                    "author": "Writing Enthusiast",
                    "category": "Writing",
                    "image": "https://images.unsplash.com/photo-1455390582262-044cdead277a?w=400"
                },
                {
                    "title": "Sustainable Living: Small Changes, Big Impact",
                    "content": "In today's world, adopting sustainable practices has become more important than ever. This blog post explores practical ways to live more sustainably without making drastic changes to your lifestyle. From reducing waste and conserving energy to making eco-friendly choices in your daily routine, we'll cover actionable steps that can make a significant difference. We'll discuss the environmental impact of our choices and how small changes can contribute to a healthier planet. Topics include sustainable shopping, energy conservation, waste reduction, and creating an eco-friendly home environment.",
                    "author": "Eco Warrior",
                    "category": "Lifestyle",
                    "image": "https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?w=400"
                },
                {
                    "title": "The Future of Web Development: Trends to Watch",
                    "content": "Web development is constantly evolving, with new technologies and frameworks emerging regularly. This comprehensive overview examines the current trends shaping the future of web development. We'll explore topics such as progressive web apps, serverless architecture, artificial intelligence integration, and the rise of low-code/no-code platforms. Additionally, we'll discuss the importance of web accessibility, performance optimization, and mobile-first design. Whether you're a seasoned developer or just starting your journey, understanding these trends will help you stay ahead in the rapidly changing tech landscape.",
                    "author": "Code Master",
                    "category": "Technology",
                    "image": "https://images.unsplash.com/photo-1627398242454-45a1465c2479?w=400"
                },
                {
                    "title": "Mindfulness and Mental Health in the Digital Age",
                    "content": "As our lives become increasingly digital, maintaining mental health and practicing mindfulness has never been more crucial. This post explores the challenges of living in a hyper-connected world and provides practical strategies for maintaining mental well-being. We'll discuss the impact of social media on mental health, the importance of digital detox, and techniques for staying present in our daily lives. From meditation practices to setting healthy boundaries with technology, we'll cover various approaches to achieving better work-life balance and mental clarity in the digital age.",
                    "author": "Wellness Guide",
                    "category": "Health",
                    "image": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400"
                }
            ]

            for blog_data in sample_blogs:
                blog = Blog(**blog_data)
                db.session.add(blog)

            db.session.commit()
            print("✅ Sample blogs added to database")

# ================== ROUTE HANDLERS ==================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/signup')
def signup_page():
    return render_template('signup.html')

@app.route('/create-blog')
def create_blog_page():
    return render_template('create_blog.html')

@app.route('/blogs')
def blogs_page():
    return render_template('blogpost.html')

@app.route('/blog/<int:blog_id>')
def blog_detail_page(blog_id):
    return render_template('blog_detail.html', blog_id=blog_id)

@app.route('/search')
def search_page():
    return render_template('search.html')

@app.route('/translate')
def translate_page():
    return render_template('translate.html')

@app.route('/summarize')
def summarize_page():
    return render_template('summarize_blog.html')

@app.route('/voice-to-text')
def voice_to_text_page():
    return render_template('voice_to_text.html')

@app.route('/contact')
def contact_page():
    return render_template('contact.html')

@app.route('/recommend')
def recommend_page():
    return render_template('recommend.html')

# ================== API ROUTES ==================

# Blog API Routes
@app.route('/api/add_blog', methods=['POST'])
def add_blog():
    try:
        data = request.get_json()
        print("📥 Received blog data:", data)

        title = data.get("title", "").strip()
        content = data.get("content", "").strip()
        author = data.get("author", "Anonymous").strip()
        category = data.get("category", "General").strip()
        image = data.get("image", "https://via.placeholder.com/400x200")

        if not title or not content:
            return jsonify({"error": "Title and content are required"}), 400

        new_blog = Blog(title=title, content=content, author=author, category=category, image=image)
        db.session.add(new_blog)
        db.session.commit()

        print("✅ Blog saved to database.")
        return jsonify({"message": "Blog added successfully!", "id": new_blog.id})

    except Exception as e:
        print(f"❌ Error adding blog: {e}")
        return jsonify({"error": "Failed to add blog"}), 500

@app.route('/api/get_blogs', methods=['GET'])
def get_blogs():
    try:
        blogs = Blog.query.order_by(Blog.id.desc()).all()
        blog_list = []

        for blog in blogs:
            content_preview = blog.content[:200] + "..." if len(blog.content) > 200 else blog.content
            blog_list.append({
                "id": blog.id,
                "title": blog.title,
                "content": content_preview,
                "author": blog.author,
                "date": blog.date,
                "image": blog.image,
                "category": blog.category,
                "views": blog.views
            })

        return jsonify(blog_list)

    except Exception as e:
        print(f"❌ Error fetching blogs: {e}")
        return jsonify({"error": "Failed to fetch blogs"}), 500

@app.route('/api/get_blog/<int:blog_id>', methods=['GET'])
def get_blog(blog_id):
    try:
        blog = Blog.query.get(blog_id)
        if not blog:
            return jsonify({"error": "Blog not found"}), 404

        # Increment view count
        blog.views += 1
        db.session.commit()

        return jsonify({
            "id": blog.id,
            "title": blog.title,
            "content": blog.content,
            "author": blog.author,
            "date": blog.date,
            "image": blog.image,
            "category": blog.category,
            "views": blog.views
        })

    except Exception as e:
        print(f"❌ Error fetching blog: {e}")
        return jsonify({"error": "Failed to fetch blog"}), 500

@app.route('/api/search_blogs', methods=['GET'])
def search_blogs():
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify([])

        blogs = Blog.query.filter(
            (Blog.title.contains(query)) | 
            (Blog.content.contains(query)) |
            (Blog.category.contains(query)) |
            (Blog.author.contains(query))
        ).all()

        blog_list = []
        for blog in blogs:
            content_preview = blog.content[:200] + "..." if len(blog.content) > 200 else blog.content
            blog_list.append({
                "id": blog.id,
                "title": blog.title,
                "content": content_preview,
                "author": blog.author,
                "date": blog.date,
                "image": blog.image,
                "category": blog.category,
                "views": blog.views
            })

        return jsonify(blog_list)

    except Exception as e:
        print(f"❌ Error searching blogs: {e}")
        return jsonify({"error": "Failed to search blogs"}), 500

# User Authentication API Routes
@app.route("/api/signup", methods=["POST"])
def api_signup():
    try:
        data = request.get_json()
        name = data.get("name", "").strip()
        email = data.get("email", "").strip()
        password = data.get("password", "").strip()

        if not name or not email or not password:
            return jsonify({"error": "All fields are required."}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email already registered."}), 400

        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        new_user = User(name=name, email=email, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "Account created successfully!"})

    except Exception as e:
        print(f"❌ Signup error: {e}")
        return jsonify({"error": "Failed to create account"}), 500

@app.route("/api/login", methods=["POST"])
def api_login():
    try:
        data = request.get_json()
        email = data.get("email", "").strip()
        password = data.get("password", "").strip()

        user = User.query.filter_by(email=email).first()

        if not user or not bcrypt.check_password_hash(user.password, password):
            return jsonify({"error": "Invalid credentials"}), 401

        token = jwt.encode({
            "user_id": user.id,
            "user_name": user.name,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, app.config["SECRET_KEY"], algorithm="HS256")

        return jsonify({
            "message": "Login successful",
            "token": token,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email
            }
        })

    except Exception as e:
        print(f"❌ Login error: {e}")
        return jsonify({"error": "Failed to login"}), 500

# NLP Feature API Routes
@app.route('/api/translate', methods=['POST'])
def translate_text():
    try:
        data = request.get_json()
        text = data.get("text", "").strip()
        target_lang = data.get("language", "").strip()

        if not text or not target_lang:
            return jsonify({"error": "Missing text or language"}), 400

        translated_text = GoogleTranslator(source='auto', target=target_lang).translate(text)
        return jsonify({"translated_text": translated_text})

    except Exception as e:
        print(f"❌ Translation error: {e}")
        return jsonify({"error": "Translation failed"}), 500

@app.route('/api/summarize', methods=['POST'])
def summarize():
    try:
        data = request.get_json()
        text = data.get("text", "").strip()

        if not text:
            return jsonify({"summary": "No text provided."})

        summary = extractive_summarization(text)
        return jsonify({"summary": summary})

    except Exception as e:
        print(f"❌ Summarization error: {e}")
        return jsonify({"summary": "Failed to summarize text."})

@app.route('/api/correct_text', methods=['POST'])
def correct_text():
    try:
        data = request.get_json()
        text = data.get("text", "").strip()

        if not text:
            return jsonify({"error": "No text provided."}), 400

        corrected_text, suggestions = auto_correct(text)
        return jsonify({"corrected_text": corrected_text, "suggestions": suggestions})

    except Exception as e:
        print(f"❌ Auto-correct error: {e}")
        return jsonify({"error": "Failed to correct text"}), 500

@app.route('/voice-to-text', methods=['POST'])
def voice_to_text():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio uploaded'}), 400

    f = request.files['audio']
    orig_name = f.filename or 'recording'
    ext = os.path.splitext(orig_name)[1].lower()  # .wav/.webm/.ogg
    tmp_in = f'tmp_in{ext if ext else ".bin"}'
    tmp_wav = 'tmp_conv.wav'
    f.save(tmp_in)

    recognizer = sr.Recognizer()
    text = ''
    try:
        # Convert non-wav to wav using pydub if needed
        if ext not in ['.wav']:
            try:
                from pydub import AudioSegment
                audio_seg = AudioSegment.from_file(tmp_in)
                audio_seg.export(tmp_wav, format='wav')
                path_to_read = tmp_wav
            except Exception as e:
                return jsonify({'error': f'Audio conversion failed: {e}'}), 400
        else:
            path_to_read = tmp_in

        with sr.AudioFile(path_to_read) as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.2)
            audio = recognizer.record(source)

        # Prefer Google (online) for accuracy
        try:
            text = recognizer.recognize_google(audio)
        except Exception:
            # Optional: enable Sphinx only if installed
            try:
                text = recognizer.recognize_sphinx(audio)
            except Exception:
                text = ''

        return jsonify({'text': text})

    finally:
        # Cleanup
        for p in [tmp_in, tmp_wav]:
            try:
                if os.path.exists(p):
                    os.remove(p)
            except:
                pass


# Utility functions
def extractive_summarization(text, num_sentences=3):
    try:
        # Clean and preprocess text
        clean_text = re.sub(r'[^a-zA-Z]', ' ', text)
        clean_text = re.sub(r'\s+', ' ', clean_text)

        sentence_list = sent_tokenize(text)

        if len(sentence_list) <= num_sentences:
            return text

        word_frequencies = {}
        stop_words = set(stopwords.words('english'))

        for word in word_tokenize(clean_text):
            if word.lower() not in stop_words:
                word_frequencies[word.lower()] = word_frequencies.get(word.lower(), 0) + 1

        if not word_frequencies:
            return ' '.join(sentence_list[:num_sentences])

        max_frequency = max(word_frequencies.values())
        for word in word_frequencies:
            word_frequencies[word] = word_frequencies[word] / max_frequency

        sentence_scores = {}
        for sentence in sentence_list:
            words_in_sentence = word_tokenize(sentence.lower())
            score = 0
            word_count = 0

            for word in words_in_sentence:
                if word in word_frequencies:
                    score += word_frequencies[word]
                    word_count += 1

            if word_count > 0 and len(sentence.split(' ')) < 30:
                sentence_scores[sentence] = score / word_count

        summary_sentences = heapq.nlargest(num_sentences, sentence_scores, key=sentence_scores.get)
        summary = ' '.join(summary_sentences)

        return summary if summary else ' '.join(sentence_list[:num_sentences])

    except Exception as e:
        print(f"❌ Summarization error: {e}")
        return text[:500] + "..." if len(text) > 500 else text

def auto_correct(text):
    try:
        blob = TextBlob(text)
        corrected_text = str(blob.correct())

        suggestions = {}
        words = text.split()

        for word in words:
            corrected_word = str(TextBlob(word).correct())
            if corrected_word.lower() != word.lower():
                suggestions[word] = corrected_word

        return corrected_text, suggestions

    except Exception as e:
        print(f"❌ Auto-correct error: {e}")
        return text, {}

# Initialize database
init_db()

if __name__ == "__main__":
    print("🚀 Flask Blog Server Started!")
    print("📝 Access your blog at: http://127.0.0.1:5000/")
    print("✨ Features: Login/Signup, Create Blogs, NLP Tools, and more!")

    with app.app_context():
        users = User.query.all()
        blogs = Blog.query.all()
        print(f"👤 Registered Users: {len(users)}")
        print(f"📰 Available Blogs: {len(blogs)}")

    app.run(debug=True, host='0.0.0.0', port=5000)
