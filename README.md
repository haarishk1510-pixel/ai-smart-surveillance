# Intelligent Surveillance System with AI, Face Recognition, Cloud Backup and IoT Alerting

![Python](https://img.shields.io/badge/Python-3.11-blue)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Object%20Detection-red)
![Face Recognition](https://img.shields.io/badge/Face%20Recognition-AI-orange)
![Flask](https://img.shields.io/badge/Flask-Web%20Dashboard-black)
![SQLite](https://img.shields.io/badge/SQLite-Database-blue)
![AWS S3](https://img.shields.io/badge/AWS-S3-orange)
![Arduino Nano](https://img.shields.io/badge/Arduino-Nano-cyan)
![IoT](https://img.shields.io/badge/IoT-Smart%20Surveillance-green)

---

## Project Overview

The Intelligent Surveillance System is an AI-powered security monitoring platform that combines Computer Vision, Face Recognition, Cloud Computing, and IoT technologies to provide real-time surveillance, automated threat detection, evidence management, and instant alert generation.

The system continuously monitors live video streams using a camera, detects objects using YOLOv8, authenticates authorized individuals through facial recognition, captures evidence automatically, stores incidents locally, uploads evidence to AWS S3 cloud storage, and triggers hardware alerts through an Arduino Nano-based alert mechanism.

This project aims to reduce manual surveillance efforts while improving security response times and ensuring reliable evidence preservation.

---

# Features

### Real-Time Surveillance

- Live camera monitoring
- Continuous frame processing
- Automated incident detection
- Real-time threat identification

### AI Object Detection

- YOLOv8 object detection
- Person detection
- Confidence-based predictions
- Real-time inference

### Face Authentication

- Authorized user recognition
- Unknown person detection
- Face registration module
- Face encoding and matching

### Evidence Management

- Automatic image capture
- Timestamped evidence storage
- Incident archiving
- Historical evidence tracking

### Cloud Integration

- AWS S3 evidence upload
- Secure cloud backup
- Remote evidence accessibility
- Cloud synchronization

### IoT Alert System

- Arduino Nano integration
- LED alert notification
- Buzzer alarm system
- Serial communication

### Monitoring Dashboard

- Incident monitoring
- Event visualization
- Evidence review
- Alert tracking

### Logging and Database

- Event logging
- Incident history
- SQLite database storage
- Audit records

---

# System Architecture

```text
                    ┌─────────────────────┐
                    │      USB Camera     │
                    └──────────┬──────────┘
                               │
                               ▼

                    ┌─────────────────────┐
                    │ OpenCV Video Stream │
                    └──────────┬──────────┘
                               │
                               ▼

                    ┌─────────────────────┐
                    │ YOLOv8 Detection    │
                    └──────────┬──────────┘
                               │

           ┌───────────────────┴───────────────────┐
           │                                       │

           ▼                                       ▼

 ┌─────────────────────┐              ┌─────────────────────┐
 │ Face Authentication │              │ Object Recognition  │
 └──────────┬──────────┘              └──────────┬──────────┘
            │                                    │
            └─────────────┬──────────────────────┘
                          ▼

                ┌─────────────────────┐
                │   Decision Engine   │
                └──────────┬──────────┘
                           │

      ┌────────────────────┼────────────────────┐
      │                    │                    │

      ▼                    ▼                    ▼

┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│ Evidence      │  │ Event Logging │  │ Alert Module  │
│ Generation    │  │ SQLite DB     │  │ Arduino Nano  │
└───────┬───────┘  └───────────────┘  └───────┬───────┘
        │                                      │
        ▼                                      ▼

┌───────────────┐                    ┌──────────────────┐
│ AWS S3 Cloud  │                    │ LED + Buzzer     │
│ Backup        │                    │ Alert System     │
└───────────────┘                    └──────────────────┘
```

---

# Technology Stack

| Category | Technology |
|-----------|------------|
| Programming Language | Python 3.11 |
| Artificial Intelligence | YOLOv8 |
| Computer Vision | OpenCV |
| Face Recognition | face_recognition |
| Machine Learning | Deep Learning |
| Backend Framework | Flask |
| Frontend | HTML, CSS, JavaScript |
| Database | SQLite |
| Cloud Platform | AWS S3 |
| IoT Controller | Arduino Nano |
| Communication | PySerial |
| Hardware Alert | LED + Buzzer |
| Development Environment | VS Code |
| Version Control | Git & GitHub |

---

# Project Structure

```text
INTELLIGENT-SURVEILLANCE-SYSTEM
│
├── app/
│   ├── alerts.py
│   ├── cloud_upload.py
│   ├── decision_engine.py
│   ├── detection.py
│   ├── evidence.py
│   ├── face_auth.py
│   ├── main.py
│   └── __init__.py
│
├── backup/
│
├── database/
│
├── evidence/
│
├── known_faces/
│
├── logs/
│
├── models/
│   └── yolov8n.pt
│
├── static/
│
├── templates/
│
├── register_face.py
├── find_cam.py
├── nano_test_cam.py
├── aws_test.py
├── main.py
├── requirements.txt
└── README.md
```

---

# System Workflow

1. Webcam captures live video.
2. OpenCV processes incoming frames.
3. YOLOv8 performs object detection.
4. Face Recognition authenticates individuals.
5. Decision Engine evaluates threat level.
6. Evidence is captured automatically.
7. Incident data is stored in SQLite.
8. Evidence is uploaded to AWS S3.
9. Arduino Nano receives alert signals.
10. LED and Buzzer notify security personnel.
11. Dashboard displays incidents and logs.

---

# Database Design

### Events Table

| Field | Description |
|---------|-------------|
| id | Event ID |
| timestamp | Detection Time |
| event_type | Event Category |
| person_name | Identified Person |
| confidence | Detection Confidence |
| image_path | Local Evidence Path |
| cloud_url | Cloud Storage URL |

### Known Faces Table

| Field | Description |
|---------|-------------|
| id | Face ID |
| name | User Name |
| encoding_path | Face Encoding File |

### Alerts Table

| Field | Description |
|---------|-------------|
| id | Alert ID |
| timestamp | Alert Time |
| alert_level | Alert Severity |
| description | Alert Information |

---

# Arduino Connections

## LED Circuit

| Arduino Nano Pin | Component |
|------------------|------------|
| D2 | LED Positive |
| GND | LED Negative |

## Buzzer Circuit

| Arduino Nano Pin | Component |
|------------------|------------|
| D3 | Buzzer Positive |
| GND | Buzzer Negative |

---

# Installation

### Clone Repository

```bash
git clone https://github.com/your-username/intelligent-surveillance-system.git
cd intelligent-surveillance-system
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

#### Windows

```bash
venv\Scripts\activate
```

#### macOS / Linux

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Configuration

Create a `.env` file:

```env
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_BUCKET_NAME=your_bucket
SERIAL_PORT=/dev/ttyUSB0
```

---

# Run the Project

```bash
python main.py
```

---

# Future Enhancements

- Multi-camera support
- Mobile application
- Weapon detection
- Fire and smoke detection
- Email notifications
- SMS alerts
- Cloud dashboard
- Edge AI deployment
- CCTV integration
- Vehicle recognition

---

# Research Areas

- Artificial Intelligence
- Computer Vision
- Face Recognition
- Cloud Computing
- Internet of Things (IoT)
- Embedded Systems
- Smart Surveillance Systems

---

# Screenshots

```text
screenshots/
├── dashboard.png
├── detection.png
├── face_authentication.png
├── alert_system.png
└── architecture.png
```

Add screenshots here after deployment.

---

# License

This project is developed for academic and research purposes.

---

# Author

### Haarish kumar S
B.Tech Computer Science and Engineering



**Intelligent Surveillance System with AI, Face Recognition, Cloud Backup and IoT Alerting**
