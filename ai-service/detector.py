import cv2
import torch
import time
from ultralytics import YOLO

class Detector:
    def __init__(self, source=0):    # think self like this in (C++/java)
        # source=0         → device webcam
        # source="file.mp4" → video file
        # source="rtsp://..." → real IP camera (future)

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        print(f"[Detector] Loading YOLOv8n on {self.device}...")
        self.model = YOLO("yolov8n.pt")
        self.model.to(self.device)
        self.model.fuse()
        print("[Detector] Model ready.")

        self.source = source
        self.cap = None  #cap will later hold the camera object
    
    def start(self):
        self.cap = cv2.VideoCapture(self.source)
        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot open video source: {self.source}")
        print(f"[Detector] Opened source: {self.source}")

    def stop(self):
        if self.cap:
            self.cap.release()
            print("[Detector] Camera released.")

    def generate_frames(self):
        """
        Generator — yields (jpeg_bytes, detections_list) for each frame.
        
        Why a generator?
        FastAPI's StreamingResponse needs something it can iterate over.
        Each iteration = one MJPEG frame pushed to the client.
        The generator runs forever (like your while True loop) until
        the client disconnects or source ends.
        """

        while True:
            ret, frame = self.cap.read()

            if not ret:
                # Video file ended — loop it back
                # For webcam this means camera disconnected
                if isinstance(self.source, str):
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # rewind
                    continue
                else:
                    print("[Detector] Frame capture failed. Stopping.")
                    break

            # Run YOLO inference on the frame
            results = self.model(frame, verbose=False)
            # verbose=False stops YOLO from printing to console every frame

            # Extract detections
            detections = []
            for box in results[0].boxes:
                confidence = float(box.conf[0])
                
                if confidence < 0.5:  # skip low confidence detections
                    continue

                class_id = int(box.cls[0])
                label = self.model.names[class_id]
                x1, y1, x2, y2 = box.xyxy[0].tolist()


                detections.append({
                    "object": label,
                    "confidence": round(confidence, 4),
                    "bounding_box": {
                        "x1": round(x1, 1),
                        "y1": round(y1, 1),
                        "x2": round(x2, 1),
                        "y2": round(y2, 1),
                    }
                })
            
            # Draw bounding boxes on frame (same as results[0].plot())
            annotated_frame = results[0].plot()

            # Encode frame as JPEG bytes
            # This is what gets pushed to the browser as MJPEG
            success, buffer = cv2.imencode(".jpg", annotated_frame)
            if not success:
                continue

            jpeg_bytes = buffer.tobytes()

            yield jpeg_bytes, detections