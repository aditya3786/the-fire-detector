import firebase_admin
from firebase_admin import credentials, db

# Load your Firebase Admin SDK key
cred = credentials.Certificate("serviceAccountKey.json")

# Initialize Firebase app
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://fire-detection-alert-system-default-rtdb.firebaseio.com/"
})

def send_alert(message):
    ref = db.reference("/alerts")
    ref.push({
        "alert": message
    })
    print("🔥 Alert sent to Firebase:", message)


# Test
if __name__ == "__main__":
    send_alert("Fire detected in the area.")
