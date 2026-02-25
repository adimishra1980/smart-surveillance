# 🛡️ Smart Surveillance

Real-time object detection system using **YOLOv8** with a **Node.js/Express** backend.

---

## 📋 Prerequisites

- [Python 3.10+](https://www.python.org/downloads/)
- [Node.js 18+](https://nodejs.org/)
- A webcam (for live detection)
- [Git](https://git-scm.com/)

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/smart-surveillance.git
cd smart-surveillance
```

### 2. Python Setup (Detection Module)

#### Create & activate a virtual environment

```bash
# Create
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate
```

#### Install Python dependencies

```bash
pip install -r requirements.txt
```

#### Download YOLOv8 model weights

The model weights file (`yolov8n.pt`) is not included in the repo due to its size. It will be **automatically downloaded** the first time you run `detect.py`, or you can manually download it:

```bash
# Auto-downloads on first run
python detect.py
```

Or download manually from [Ultralytics YOLOv8](https://github.com/ultralytics/assets/releases) and place `yolov8n.pt` in the project root.

---

### 3. Backend Setup (Node.js Server)

```bash
cd backend
```

#### Install Node.js dependencies

```bash
npm install
```

#### Configure environment variables

Create a `.env` file inside the `backend/` folder:

```bash
# backend/.env
PORT=3000
DATABASE_URL=your_database_connection_string
```

#### Run the backend server

```bash
npx ts-node-dev server.ts
```

The server will start on `http://localhost:3000`.

---

### 4. Run the Detection Script

Make sure your webcam is connected, then from the **project root**:

```bash
python detect.py
```

- A window titled **"Smart Surveillance"** will open with live detections.
- Press **Esc** to stop the detection.

---

## 📁 Project Structure

```
smart-surveillance/
├── backend/                # Node.js/Express API server
│   ├── routes/             # API route handlers
│   │   └── detection.routes.ts
│   ├── db.ts               # Database connection
│   ├── server.ts           # Express server entry point
│   ├── package.json        # Node.js dependencies
│   └── .env                # Environment variables (not in git)
├── detect.py               # YOLOv8 real-time detection script
├── requirements.txt        # Python dependencies
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

---

## 🛠️ Tech Stack

| Layer     | Technology                      |
| --------- | ------------------------------- |
| Detection | Python, OpenCV, YOLOv8, PyTorch |
| Backend   | Node.js, Express, TypeScript    |
| Database  | PostgreSQL                      |

---

## ⚠️ Troubleshooting

| Issue                                 | Solution                                                              |
| ------------------------------------- | --------------------------------------------------------------------- |
| `No module named 'ultralytics'`       | Make sure venv is activated and run `pip install -r requirements.txt` |
| `Failed to capture frame from webcam` | Check if your webcam is connected and not in use by another app       |
| CUDA not detected                     | PyTorch will fall back to CPU automatically — no action needed        |
| `Cannot find module 'express'`        | Run `npm install` inside the `backend/` folder                        |
