# 🎓 AI-Based Exam Proctoring System

> An intelligent online examination monitoring system that uses Artificial Intelligence, Computer Vision, and Machine Learning to detect suspicious activities and maintain the integrity of remote examinations.

---

## 📖 Overview

The **AI-Based Exam Proctoring System** is designed to provide secure, scalable, and automated online exam monitoring. The system continuously analyzes students' behavior during examinations using AI-powered techniques such as facial recognition, eye tracking, object detection, and audio analysis.

Instead of relying solely on human invigilators, the system automatically detects suspicious activities and generates an integrity score, helping institutions conduct fair and trustworthy online assessments.

---

## 🚀 Problem Statement

With the rapid adoption of online education, ensuring academic honesty has become increasingly challenging. Traditional online proctoring methods are:

- Time-consuming
- Expensive
- Difficult to scale
- Prone to human error

Common malpractice includes:

- Identity impersonation
- Looking away from the screen
- Using unauthorized devices
- Receiving external assistance
- Multiple people appearing during an exam

This project addresses these challenges through AI-powered automated monitoring.

---

# ✨ Key Features

### 👤 Identity Verification
- Face detection
- Facial recognition
- Student authentication before the exam

### 👀 Eye & Head Movement Tracking
- Detects frequent looking away from the screen
- Monitors abnormal head movements
- Flags suspicious gaze patterns

### 📱 Object Detection
- Detects prohibited devices such as:
  - Mobile phones
  - Books
  - Additional screens
  - Other unauthorized objects

### 🎤 Audio Monitoring
- Detects:
  - Conversations
  - Multiple voices
  - Background disturbances
  - Unusual sounds

### 🧠 AI-Based Behaviour Analysis
- Continuously analyzes user behavior
- Detects suspicious exam activities
- Reduces false positives using Machine Learning

### 📊 Integrity Score
- Generates an overall exam integrity score
- Highlights suspicious events
- Helps invigilators review flagged sessions

### 📋 Activity Logging
- Stores:
  - Exam logs
  - Detection history
  - Violations
  - Timestamps

---

# 🏗️ System Workflow

```
Student Login
      │
      ▼
Identity Verification
      │
      ▼
Live Camera & Audio Monitoring
      │
      ▼
AI Behaviour Analysis
      │
      ▼
Violation Detection
      │
      ▼
Integrity Score Generation
      │
      ▼
Exam Report
```

---

# 🛠️ Technology Stack

| Category | Technologies |
|----------|--------------|
| Programming Language | Python |
| Artificial Intelligence | AI |
| Machine Learning | ML |
| Computer Vision | OpenCV |
| Face Recognition | Face Recognition Models |
| Audio Analysis | Speech Detection |
| Frontend | HTML, CSS, JavaScript |
| Backend | Flask / Django |
| Database | MySQL / MongoDB |

---

# 📂 Project Structure

```
AI-Exam-Proctoring/
│
├── app.py
├── requirements.txt
├── README.md
├── static/
├── templates/
├── models/
├── database/
├── logs/
├── screenshots/
└── assets/
```

---

# ⚙️ Installation

## Clone the Repository

```bash
git clone https://github.com/your-username/AI-Exam-Proctoring-System.git

cd AI-Exam-Proctoring-System
```

---

## Create Virtual Environment

Windows

```bash
python -m venv venv

venv\Scripts\activate
```

Linux / macOS

```bash
python3 -m venv venv

source venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Run the Project

```bash
python app.py
```

or

```bash
flask run
```

---

# 🎯 End Users

### Primary Users

- 👨‍🎓 Students
- 👩‍🏫 Teachers
- 📝 Examination Invigilators

### Secondary Users

- Universities
- Educational Institutions
- Online Learning Platforms
- Certification Providers
- Government Examination Authorities
- Corporate Recruitment Teams

---

# 📈 Benefits

- Secure online examinations
- Automated cheating detection
- Reduced manual invigilation
- Real-time monitoring
- Scalable for large examinations
- Cost-effective solution
- Fair and unbiased evaluation

---

# 🔮 Future Enhancements

- Multi-camera support
- Emotion detection
- Browser lockdown integration
- Mobile application
- Cloud deployment
- AI-generated exam reports
- Live admin dashboard
- Real-time alerts via email/SMS

---

# 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a new branch

```bash
git checkout -b feature-name
```

3. Commit your changes

```bash
git commit -m "Add new feature"
```

4. Push the branch

```bash
git push origin feature-name
```

5. Open a Pull Request

---

# 📜 License

This project is developed for educational and research purposes.

---

# 👩‍💻 Author

**Ponnam Sriharshini**

Computer Science Student | AI & Machine Learning Enthusiast

---

## ⭐ If you found this project helpful, please consider giving it a Star!
