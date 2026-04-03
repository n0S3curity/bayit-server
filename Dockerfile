FROM python:3.11-slim

# התקנת git וכלים נחוצים (שימוש ב-slim חוסך מקום ב-Raspberry Pi)
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# הגדרת תיקיית העבודה
WORKDIR /app

# העתקת דרישות והתקנה לתוך ה-Virtual Env
COPY requirements.txt ./
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# העתקת שאר הקוד
COPY . .

# הגדרת משתני סביבה ל-Path של ה-Venv
ENV PATH="/opt/venv/bin:$PATH"

# חשיפת הפורט
EXPOSE 5000

# הגדרת תיקיית העבודה לתיקיית השרת
WORKDIR /app/server

# הרצת האפליקציה (ה-Command ב-Compose ידרוס את זה, אבל טוב שיהיה כברירת מחדל)
CMD ["python", "app.py"]