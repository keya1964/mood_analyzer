# 🧠 Mood Analyzer  
*A journal‑based web app that lets you track your feelings and see how your mood evolves over time.*

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/) 
[![Flask](https://img.shields.io/badge/Flask-3.1-green?logo=flask)](https://flask.palletsprojects.com/) 
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ✨ Demo

<p align="center">
  <img src="docs/demo.gif" alt="Animated demo of Mood Analyzer" width="700"/>
</p>

*(Don’t have a GIF yet? Grab a quick screen‑capture, save it to `docs/demo.gif`, and it will show up here.)*

---

## 🚀 Features

| | |
|--|--|
| 📝 **Journal Entries** | Write daily thoughts & feelings in a clean, distraction‑free interface. |
| 🧠 **Hybrid Sentiment Analysis** | Combines TextBlob + a Hugging Face Transformer for nuanced classification. |
| 📊 **Mood Dashboard** | Interactive history of all entries; discover trends in positivity/negativity. |
| 🔐 **User Auth** | Register, log in, log out, route protection, hashed passwords—powered by Flask‑Login. |
| 💾 **SQLAlchemy Models** | Each entry stored with user ID, timestamp, raw text, polarity, subjectivity, model score. |
| 🎨 **Tailwind CSS** | Modern, responsive UI you can tweak quickly. |
| ☁️ **Production‑ready** | Works on Gunicorn + PostgreSQL out of the box (SQLite for dev). |

---

## 🛠️ Tech Stack

| Layer | Tech |
|-------|------|
| **Backend** | Flask 3.1 · Flask‑Login · Flask‑SQLAlchemy · Python‑Dotenv |
| **NLP** | HuggingFace 🤗 Transformers · TextBlob · NLTK · Torch |
| **Database** | SQLite (dev) · PostgreSQL (prod) |
| **Frontend** | HTML5 · Jinja2 · Tailwind CSS |
| **Dev Ops** | Gunicorn · Render/Heroku · GitHub Actions (optional CI) |

---

## 📁 Project Structure

mood-analyzer/
├── app/ # Flask application package
│ ├── init.py # create_app() factory
│ ├── models.py # SQLAlchemy models
│ ├── routes.py # Flask blueprints
│ ├── forms.py # WTForms classes
│ ├── nlp.py # sentiment helpers
│ ├── static/
│ │ └── styles.css
│ └── templates/
│ ├── base.html
│ ├── index.html
│ ├── login.html
│ ├── register.html
│ ├── history.html
│ └── result.html
├── requirements.txt
├── .env.example # sample env vars
├── run.py # entry‑point for flask run
├── README.md
└── LICENSE

---

## 🏃‍♂️ Quick Start

# 1. Clone
git clone https://github.com/<your‑username>/mood-analyzer.git
cd mood-analyzer

# 2. Create & activate virtualenv
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 3. Install deps
pip install -r requirements.txt

# 4. Configure env
cp .env.example .env              # then edit .env with your own values

# 5. Initialize DB
flask shell -c "from app import db; db.create_all()"

# 6. Launch!
flask run        

## 📸 Screenshot
<img width="1421" alt="Login_page" src="https://github.com/user-attachments/assets/52b2d72e-52aa-441c-903d-a3876c087a8d" />

<img width="1430" alt="Journal_entry_page" src="https://github.com/user-attachments/assets/e70f1d62-cbde-4c83-8827-86c368713a4d" />

<img width="1423" alt="Detected_mood" src="https://github.com/user-attachments/assets/020864cc-d121-4988-93f8-118940a69644" />

<img width="688" alt="History_page" src="https://github.com/user-attachments/assets/b2d946f5-3741-4022-923d-fdb939caf12e" />

<img width="909" alt="Filter_applied" src="https://github.com/user-attachments/assets/d8abfb90-ebcb-4e67-9c55-915f86200ae3" />








