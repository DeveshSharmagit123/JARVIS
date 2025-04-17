import cv2
import os

# Initialize camera
cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Try changing 0 to 1 if needed
cam.set(3, 640)  # Set video FrameWidth
cam.set(4, 480)  # Set video FrameHeight

# Load Haar Cascade
xml_path = r"BACKEND/auth/haarcascade_frontalface_default.xml"
if not os.path.exists(xml_path):
    print("Error: Haarcascade XML file not found.")
    exit()

detector = cv2.CascadeClassifier(xml_path)

# Input User ID
face_id = input("Enter a Numeric user ID here: ")
print("Taking samples, look at the camera...")

count = 0  # Initialize sample count

while True:
    ret, img = cam.read()
    
    if not ret:
        print("Error: Failed to capture image.")
        break

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = detector.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
        count += 1

        # Save captured face
        sample_path = f"D:/JARVIS UPGRADED PART/BACKEND/auth/samples/face.{face_id}.{count}.jpg"
        cv2.imwrite(sample_path, gray[y:y+h, x:x+w])

        cv2.imshow('Camera Feed', img)

    # Exit conditions
    k = cv2.waitKey(1) & 0xFF  
    if k == 27:  # Press ESC to exit
        break
    elif count >= 100:  # Stop after 100 samples
        break

print("Samples taken. Closing program...")
cam.release()
cv2.destroyAllWindows()
