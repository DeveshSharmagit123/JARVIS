import cv2
import os

def AuthenticateFace():
    flag = 0  # Initialize flag
    import os
    import platform
    
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Ensure OpenCV face recognizer is available
    try:
        recognizer = cv2.face.LBPHFaceRecognizer_create()
    except AttributeError:
        print("Error: OpenCV `face` module is missing. Install `opencv-contrib-python`.")
        return flag

    # Load trained model - use relative paths
    trainer_path = os.path.join(current_dir, "trainer", "trainer.yml")
    if not os.path.exists(trainer_path):
        print(f"Error: Trainer file not found at {trainer_path}")
        return flag
    recognizer.read(trainer_path)

    # Load Haar Cascade
    cascadePath = os.path.join(current_dir, "haarcascade_frontalface_default.xml")
    if not os.path.exists(cascadePath):
        print(f"Error: Haar cascade XML file not found at {cascadePath}")
        return flag
    faceCascade = cv2.CascadeClassifier(cascadePath)

    # Set up font and names
    font = cv2.FONT_HERSHEY_SIMPLEX
    names = ['', '', 'DEVESH']  # Ensure the index matches trained IDs

    # Open the camera
    if platform.system() == "Darwin":  # macOS
        cam = cv2.VideoCapture(0)  # On Mac, use simpler initialization
    else:
        cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Windows-specific
        
    if not cam.isOpened():
        print("Error: Could not access camera.")
        return flag

    cam.set(3, 640)  # Width
    cam.set(4, 480)  # Height

    minW = 0.1 * cam.get(3)
    minH = 0.1 * cam.get(4)

    print("Authenticating... Look at the camera.")


    while True:
        ret, img = cam.read()
        if not ret:
            print("Error: Failed to capture image.")
            break

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(int(minW), int(minH)))

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
            id, accuracy = recognizer.predict(gray[y:y+h, x:x+w])

            if accuracy < 100 and id < len(names):  # Avoid index error
                name = names[id]
                flag = 1
            else:
                name = "unknown"
                flag = 0

            accuracy_text = f"  {round(100 - accuracy)}%"
            cv2.putText(img, name, (x+5, y-5), font, 1, (255, 255, 255), 2)
            cv2.putText(img, accuracy_text, (x+5, y+h-5), font, 1, (255, 255, 0), 1)

        cv2.imshow('Camera', img)

        k = cv2.waitKey(10) & 0xff  # Press 'ESC' to exit
        if k == 27 or flag == 1:
            break

    # Cleanup
    cam.release()
    cv2.destroyAllWindows()
    return flag
