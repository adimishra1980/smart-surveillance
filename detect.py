import cv2
import torch
from ultralytics import YOLO

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = YOLO("yolov8n.pt")
model.to(device) 
model.fuse()  # Optimize the model for inference by fusing convolution and batch normalization layers

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()

    if not ret:
        print("Failed to capture frame from webcam. Exiting...")
        break

    # run detection
    results = model(frame)

    #extract detection info
    detections = results[0].boxes


    for box in detections:
        confidence = float(box.conf[0])
        class_id = int(box.cls[0])
        label = model.names[class_id]

        print({
            "object": label,
            "confidence": round(confidence, 2)
        })

    annotated_frame = results[0].plot()

    cv2.imshow("Smart Surveillance", annotated_frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()


# print(model.names)