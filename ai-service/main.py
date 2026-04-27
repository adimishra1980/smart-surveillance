import io
import time
import queue
import uuid
import threading
import requests
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from detector import Detector

app = FastAPI(title = "Smart Surveillance AI Service")

# Config — Node backend URL
# When Node backend isn't running yet, detections just get skipped gracefully
NODE_BACKEND_URL = "http://localhost:3000/api/detections"

# Single detector instance shared across requests
# We don't want to open the camera twice
detector = Detector(source=0)   # or "footage.mp4"

# Queue holds detection payloads waiting to be sent to Node
# maxsize=5 means if Node is slow, we drop old detections 
# rather than building up a backlog that eats memory
detection_queue = queue.Queue(maxsize=5)

SESSION_ID = str(uuid.uuid4())

def backend_worker():
    """
    Single persistent thread that reads from the queue and POSTs to Node.
    Runs forever in the background.
    Much cheaper than spawning a thread per frame.
    """
    while True:
        try:
            payload = detection_queue.get(timeout=1)
            try:
                requests.post(NODE_BACKEND_URL, json=payload, timeout=2)
            except Exception:
                pass # Node not running yet - slip silently
            continue # No detections ready, keep waiting
        except queue.Empty:
            continue


@app.on_event("startup")
def startup():
    # opens camera/video when fastapi starts.
    detector.start()
    # Start the single background worker thread once
    worker = threading.Thread(target = backend_worker, daemon = True)
    worker.start()

@app.on_event("shutdown")
def shutdown():
    # Releases camera when FastAPI stops.
    detector.stop()

def push_to_backend(detections: list, frame_time: str):
    """
    Sends detection results to Node backend in a background thread.
    
    Why a thread?
    HTTP POST to Node takes ~5-20ms. If we block the main loop,
    it pauses the video stream. A fire-and-forget thread keeps
    the stream smooth.
    """

    if not detections:
        return  # nothing detected this frame, no point saving

    try:
        requests.post(
            NODE_BACKEND_URL,
            json={
                "timestamps": frame_time,
                "detections": detections,
                "source": str(detector.source)
            },
            timeout=5,  # Don't wait more than 5 seconds for Node
        )
    except requests.exceptions.ConnectionError:
        pass  # Node backend not running yet — silently skip
    except Exception as e:
        print(f"[Push] Failed to send detections: {e}")

def mjpeg_stream():
    for jpeg_bytes, detections in detector.generate_frames():
        # Only enqueue if there are detections AND queue isn't full
        # put_nowait raises if full — we just skip that frame's data
        if detections:
            try:
                detection_queue.put_nowait({
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "detections": detections,
                    "source": str(detector.source),
                    "sessionId": SESSION_ID
                })
            except queue.Full:
                pass  # backend is slow, drop this frame's data, keep streaming

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + jpeg_bytes +
            b"\r\n"
        )


@app.get("/stream")
def stream():
    """
    Open this URL in any browser or VLC to watch the live annotated feed.
    http://localhost:8000/stream
    """
    return StreamingResponse(
        mjpeg_stream(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )

@app.get("/health")
def health():
    return {"status": "ok", "source": str(detector.source)}