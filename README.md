# AI Smart Surveillance System

Real-time face authentication with automatic evidence capture, cloud alerts and a hardware alarm.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green)
![DeepFace](https://img.shields.io/badge/DeepFace-FaceNet-orange)
![Flask](https://img.shields.io/badge/Flask-Dashboard-black)
![MySQL](https://img.shields.io/badge/MySQL-Event%20Log-blue)
![AWS](https://img.shields.io/badge/AWS-S3%20%2B%20SNS-orange)
![Arduino](https://img.shields.io/badge/Arduino-Nano-teal)

**Live demo:** <https://ai-smart-surveillance.vercel.app> (one click, no sign-up)

> The live demo runs only the admin dashboard, on sample data. The detection pipeline needs a webcam, an Arduino and a local database, so it runs on an edge device rather than in the cloud. No real people or camera images are in the demo or in this repository.

## What it does

Traditional CCTV records footage for someone to review later. This system watches a camera feed, decides whether the person in view is authorized, and reacts on its own:

- Verifies faces from a live camera against enrolled images using DeepFace (FaceNet).
- Requires consistent results across checks before changing state, which reduces false alarms from a single bad frame.
- Saves a timestamped evidence image for each unauthorized detection.
- Uploads evidence to AWS S3 and sends an email alert through AWS SNS.
- Logs each event to MySQL.
- Signals an Arduino Nano over serial to drive an LED and buzzer.
- Provides a Flask admin dashboard with login, statistics, a searchable event log, evidence previews and CSV export.

## Architecture

```text
Camera -> OpenCV capture -> DeepFace (FaceNet) verification -> Stability logic
                                                                     |
                     +-------------------+-----------------+---------+
                     |                   |                 |
              Evidence image       AWS SNS email     Arduino Nano
              saved locally,          alert          LED + buzzer
              uploaded to S3
                     |
               MySQL event log -> Flask admin dashboard
```

Recognition runs at the edge to keep latency low. The cloud handles evidence backup and notifications.

## How detection works

| Setting | Value |
|---|---|
| Face model | FaceNet through DeepFace |
| Recognition frequency | Every 10th frame |
| Match threshold | Distance below 0.55 |
| Becomes `AUTHORIZED` after | 2 consecutive matching checks |
| Becomes `UNAUTHORIZED` after | 3 consecutive non-matching checks |
| Evidence cooldown | 5 seconds between captures |
| Arduino serial signal | `A` for authorized, `U` for unauthorized |

Evidence upload, alerting and logging run in a background thread so the video loop is not blocked.

## Tech stack

Python, OpenCV, DeepFace, TensorFlow, Flask, Flask-SocketIO, MySQL, AWS S3, AWS SNS, boto3, PySerial, Arduino Nano, HTML, CSS, JavaScript, Chart.js.

## Try the dashboard locally

No camera, MySQL or AWS account needed:

```bash
git clone https://github.com/haarishk1510-pixel/ai-smart-surveillance.git
cd ai-smart-surveillance
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
DEMO_MODE=1 python app.py
```

Open http://127.0.0.1:5000 and choose **Open the live dashboard**. If port 5000 is taken, set `PORT` to another number.

## Run the full system

Requirements: a webcam, MySQL, an AWS account with an S3 bucket and SNS topic, and optionally an Arduino Nano.

```bash
pip install -r requirements-edge.txt
cp .env.example .env              # then fill in your values
mysql -u root -p < schema.sql
aws configure
python register_face.py           # enroll authorized faces into known_faces/
python main.py                    # start detection (press q to quit)
python app.py                     # start the dashboard in a second terminal
```

Set `ADMIN_USERNAME` and `ADMIN_PASSWORD` in `.env` before using the dashboard for anything real.

## Arduino wiring

| Arduino Nano pin | Component |
|---|---|
| D2 | LED positive |
| D3 | Buzzer positive |
| GND | LED and buzzer negative |

## Project structure

```text
main.py              Edge detection, evidence, alerts and serial output
app.py               Flask dashboard, with demo mode
register_face.py     Enrolls authorized faces
schema.sql           MySQL table definition
templates/           Project landing page, dashboard and login
app/                 Earlier modular prototype, including YOLOv8 person detection
find_cam.py, test_cam.py, aws_test.py   Hardware and AWS checks
requirements.txt     Dashboard demo only
requirements-edge.txt  Full system
```

## Privacy

Face images, camera captures and credentials are excluded from version control. Face recognition processes biometric data, so get consent from anyone you enroll or monitor and follow the laws that apply where you deploy it.

## Known limitations

- Accuracy drops in low light and when faces are obscured.
- Recognition speed depends on the edge device's processing power.
- Each check compares against up to 3 enrolled images.
- The system has been tested indoors with a single laptop webcam.

## Research paper

*AI-Powered Intelligent Surveillance and Threat Analytics System with Cloud-Native Security Architecture*
Dr. J. Jegan, Haarish Kumar S, Swathi K S, SRM Institute of Science and Technology, Tiruchirappalli.

A link will be added here once the paper is available.

## Author

**Haarish Kumar S**, B.Tech Computer Science and Engineering, SRM Institute of Science and Technology, Tiruchirappalli.
