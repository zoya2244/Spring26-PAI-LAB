from flask import Flask, render_template, request
import cv2
import os
from profile_logic import analyze_face

app = Flask(__name__)
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Load face detector
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    image_path = None

    if request.method == "POST":
        file = request.files["image"]
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)

        img = cv2.imread(filepath)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            personality = analyze_face(w, h)
            cv2.rectangle(img, (x,y), (x+w, y+h), (0,255,0), 2)
            cv2.putText(img, personality, (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

        cv2.imwrite(filepath, img)

        result = personality
        image_path = filepath

    return render_template("index.html", result=result, image=image_path)


if __name__ == "__main__":
    app.run(debug=True)