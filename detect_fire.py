from ultralytics import YOLO
import cv2
import firebase_admin
from firebase_admin import credentials, db
import time

# ---------------------------
# 1. Load YOLO trained model
# ---------------------------
model = YOLO("runs/detect/train/weights/best.pt")   # update path if different

# ---------------------------
# 2. Initialize Firebase
# ---------------------------
cred = credentials.Certificate("serviceAccountKey.json")  # your Firebase key file
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://fire-detection-alert-system-default-rtdb.firebaseio.com/'   # replace this
})

ref = db.reference("alerts")  # Database node

# ---------------------------
# 3. Read webcam/video
# ---------------------------
cap = cv2.VideoCapture(0)   # 0 = webcam

print("🔥 Fire Detection System Started...")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame)

    fire_detected = False

    for r in results:
        for box in r.boxes:
            class_id = int(box.cls[0])
            conf = float(box.conf[0])

            # class_id = 0 → fire, 1 → smoke
            if class_id in [0, 1] and conf > 0.5:
                fire_detected = True

    # ---------------------------
    # 4. Push alert to Firebase
    # ---------------------------
    if fire_detected:
        alert_data = {
            "status": "FIRE DETECTED!",
            "timestamp": int(time.time())
        }
        ref.push(alert_data)
        print("🔥 ALERT SENT TO FIREBASE!")

    cv2.imshow("Fire Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
