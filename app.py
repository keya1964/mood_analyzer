import os
import io
import base64
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
import pandas as pd

from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import csv




app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Required for flash messages

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./mood_entries.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

from flask_migrate import Migrate
migrate = Migrate(app, db)

# flask-login setup 
login_manager = LoginManager()
login_manager.login_view = "login" # the name of your login route function
login_manager.init_app(app)

# Define MoodEntry table
class MoodEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    entry = db.Column(db.Text, nullable=False)
    mood = db.Column(db.String(20), nullable=False)
    confidence = db.Column(db.Float, nullable=False)

    # ✅ Foreign Key to link entry to user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # ✅ Optional: define relationship from entry to user
    user = db.relationship('User', backref='entries')

# User Model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Load sentiment model
model_name = "cardiffnlp/twitter-roberta-base-sentiment"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name, use_safetensors=True)
classifier = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer, return_all_scores=True)

# Mood label mapping
mood_map = {
    "LABEL_0": "😞 Negative",
    "LABEL_1": "😐 Neutral",
    "LABEL_2": "😊 Positive"
}

# Home route
@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        entry_text = request.form['entry'].strip()
        if not entry_text:
            flash("Please write something before submitting.", "error")
            return redirect(url_for('index'))

        result_scores = classifier(entry_text)[0]
        result_scores.sort(key=lambda x: x['score'], reverse=True)
        top_result = result_scores[0]
        top_label = top_result['label']
        confidence = top_result['score'] * 100

        # If Neutral is very close in score to the top, prefer Neutral
        label_conf_map = {r['label']: r['score'] for r in result_scores}
        if abs(label_conf_map.get('LABEL_1', 0) - top_result['score']) < 0.05:
            top_label = 'LABEL_1'

        mood = mood_map.get(top_label, "😐 Neutral")

        new_entry = MoodEntry(entry=entry_text, mood=mood, confidence=confidence, user_id=current_user.id)

        db.session.add(new_entry)
        db.session.commit()

        flash("Entry saved successfully!", "success")
        return render_template('result.html', mood=mood, entry=entry_text, confidence=confidence)

    return render_template('index.html')


# Mood history route
@app.route('/history')
@login_required
def history():
    mood_filter = request.args.get('mood', "")
    start_str = request.args.get('start_date', "")
    end_str = request.args.get('end_date', "")

    q = MoodEntry.query.filter_by(user_id=current_user.id)


    if mood_filter:
        q = q.filter(MoodEntry.mood == mood_filter)

    if start_str:
        start_dt = datetime.fromisoformat(start_str)
        q = q.filter(MoodEntry.timestamp >= start_dt)
    if end_str:
        end_dt = datetime.fromisoformat(end_str)
        q = q.filter(MoodEntry.timestamp <= end_dt)

    entries = q.order_by(MoodEntry.timestamp).all()

    chart_url = None
    if entries:
        df = pd.DataFrame([{
            'Timestamp': e.timestamp,
            'Mood': e.mood
        } for e in entries])
        df['Label'] = df['Mood'].apply(lambda x: x.split()[-1])
        df['Score'] = df['Label'].map({'Negative': 0, 'Neutral': 1, 'Positive': 2})
        df = df.sort_values('Timestamp')

        plt.figure(figsize=(10, 4))
        plt.plot(df['Timestamp'], df['Score'], marker='o', linestyle='-')
        plt.yticks([0, 1, 2], ['Negative', 'Neutral', 'Positive'])
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        chart_url = base64.b64encode(buf.read()).decode()
        buf.close()
        plt.close()

    return render_template('history.html',
                           entries=entries,
                           chart_url=chart_url,
                           mood_filter=mood_filter,
                           start_date=start_str,
                           end_date=end_str)


# CSV export route
@app.route('/download')
@login_required
def download_csv():
    entries = MoodEntry.query.filter_by(user_id=current_user.id).order_by(MoodEntry.timestamp).all()

    csv_path = "mood_entries_export.csv"

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Timestamp', 'Entry', 'Mood', 'Confidence'])
        for e in entries:
            writer.writerow([e.timestamp.strftime("%Y-%m-%d %H:%M:%S"), e.entry, e.mood, f"{e.confidence:.2f}%"])

    return send_file(csv_path, as_attachment=True)



@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered.")
            return redirect(url_for("register"))

        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. Please login.")
        return redirect(url_for("login"))

    return render_template("register.html")

from flask_login import login_user, logout_user, login_required, current_user

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("index"))
        else:
            flash("Invalid credentials")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/delete/<int:entry_id>', methods=['POST'])
@login_required
def delete_entry(entry_id):
    entry = MoodEntry.query.get_or_404(entry_id)
    if entry.user_id != current_user.id:
        flash("You are not authorized to delete this entry.", "error")
        return redirect(url_for('history'))

    db.session.delete(entry)
    db.session.commit()
    flash("Entry deleted successfully!", "success")
    return redirect(url_for('history'))

# Run server
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5050)
