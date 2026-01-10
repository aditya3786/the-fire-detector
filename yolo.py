import cv2
import time
import datetime
import supervision as sv
from ultralytics import YOLO

# -------------------- FIREBASE SETUP --------------------
import firebase_admin
from firebase_admin import credentials, db

# Load your service account key (replace with your JSON file)
cred = credentials.Certificate("serviceAccountKey.json")

firebase_admin.initialize_app(cred, {
    "databaseURL": "https://fire-detection-alert-system-default-rtdb.firebaseio.com/"
})

# Firebase reference
alert_ref = db.reference('/alerts')

# -------------------- ALERT FUNCTION --------------------
last_alert_time = 0
ALERT_COOLDOWN = 10  # seconds

def send_alert(message):
    global last_alert_time
    current_time = time.time()

    if current_time - last_alert_time >= ALERT_COOLDOWN:
        alert_ref.push({
            "message": message,
            "time": str(datetime.datetime.now())
        })
        print("🔥 Alert sent to Firebase:", message)
        last_alert_time = current_time

# -------------------- YOLO SETUP --------------------
model = YOLO("best.pt")  # Replace with your trained model

bounding_box_annotator = sv.BoundingBoxAnnotator()
label_annotator = sv.LabelAnnotator()

# -------------------- CAMERA SETUP --------------------
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Cannot open camera")
    exit()

# Fix Windows display issue
cv2.namedWindow("Webcam Fire Detection", cv2.WINDOW_NORMAL)
print("📸 Webcam started... Press ESC to exit.")

# -------------------- MAIN LOOP --------------------
while True:
    ret, frame = cap.read()
    if not ret:
        print("⚠️ Can't receive frame. Exiting...")
        break

    results = model(frame)[0]
    detections = sv.Detections.from_ultralytics(results)

    # -------------------- FIRE DETECTION --------------------
    fire_detected = False
    if detections.class_id is not None and len(detections.class_id) > 0:
        for i in range(len(detections.class_id)):
            class_id = int(detections.class_id[i])
            label = model.names[class_id].lower()
            if "fire" in label:
                fire_detected = True
                break

    # -------------------- SEND FIRE ALERT --------------------
    if fire_detected:
        send_alert("🔥 Fire detected by webcam!")

    # -------------------- ANNOTATION --------------------
    annotated_image = bounding_box_annotator.annotate(
        scene=frame, detections=detections)

    custom_labels = []
    for i in range(len(detections.xyxy)):
        class_id = int(detections.class_id[i])
        confidence = detections.confidence[i]
        name = model.names[class_id] if class_id < len(model.names) else "Unknown"
        custom_labels.append(f"{name} {confidence:.2f}")

    annotated_image = label_annotator.annotate(
        scene=annotated_image, detections=detections, labels=custom_labels)

    # -------------------- DISPLAY --------------------
    cv2.imshow("Webcam Fire Detection", annotated_image)

    # -------------------- EXIT ON ESC --------------------
    if cv2.waitKey(1) & 0xFF == 27:  # ESC key
        print("👋 ESC pressed, exiting...")
        break

# -------------------- CLEANUP --------------------
cap.release()
cv2.destroyAllWindows()
print("🛑 Webcam closed.")
