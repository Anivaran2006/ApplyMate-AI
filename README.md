# ApplyMate AI

ApplyMate AI is an AI-powered NTA notification monitoring system that automatically tracks new notices, generates summaries, detects categories, and sends personalized email alerts.

## Features

* Monitor NTA notifications automatically
* Download and process PDF notices
* Generate AI summaries using Gemini
* Detect categories (NEET, JEE, CUET, GENERAL)
* Send personalized email notifications
* User subscription dashboard
* User registration and deletion

## Tech Stack

* Python
* FastAPI
* HTML
* CSS
* JavaScript
* Gemini API
* Resend API
* APScheduler

## Project Structure

```text
app/
├── notifier/
├── routes/
├── scraper/
├── services/
├── database/

static/
templates/
data/
```

## Installation

```bash
pip install -r requirements.txt
```

## Run the Project

```bash
python -m uvicorn app.main:app --reload
```

Open:

```text
https://applymate-ai-gz7k.onrender.com/dashboard
```

## Author

Anivaran Dubey
B.Tech AIML Student
