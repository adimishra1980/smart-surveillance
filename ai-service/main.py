from requests.packages import target
from fastapi import requests
import io
import time
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
detector = Detector(source=0)

@app.on_event("startup")
def startup():
    # opens camera/video when fastapi starts.
    detector.start()

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
    """
    Generator for StreamingResponse.
    
    MJPEG format is dead simple:
    Each frame is a JPEG wrapped in a multipart HTTP boundary.
    The browser treats the <img> tag as a live video stream.
    
    Format:
    --frame
    Content-Type: image/jpeg
    
    <jpeg bytes>
    --frame
    Content-Type: image/jpeg
    """
    for jpeg_bytes, detections in detector.generate_frames():
        # Push detections to Node in background (non-blocking)
        frame_time = time.strftime("%Y-%m-%dT%H:%M:%S")
        thread = threading.Thread(
            target = push_to_backend,
            args = (detections, frame_time),
            daemon = True
        )
        thread.start()

        # Yield MJPEG frame to whoever is watching the stream
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