import cv2
import numpy as np
import pyautogui
import track_hand as htm
import time
import threading
from tkinter import Tk, Button

# Global variable to control the start/stop of the gesture application
running = False

# Webcam settings
wCam, hCam = 1280, 720
frameR = 100  # Frame reduction for smoother mouse control

# Initialize previous and current locations
plocX, plocY = 0, 0
clocX, clocY = 0, 0
smoothening = 4  # Factor to smoothen mouse movement

# Function to run gesture control
def gesture_control():
    global running, plocX, plocY, clocX, clocY

    # Initialize webcam
    cap = cv2.VideoCapture(0)
    cap.set(3, wCam)
    cap.set(4, hCam)

    # Initialize hand detector
    detector = htm.handDetector(maxHands=1)

    while running:
        success, img = cap.read()
        img = detector.findHands(img)
        lmList, bbox = detector.findPosition(img)

        if len(lmList) != 0:
            # Get the tip of the index and middle fingers
            x1, y1 = lmList[8][1:]  # Index finger
            x2, y2 = lmList[12][1:]  # Middle finger

            # Get the fingers state
            fingers = detector.fingersUp()

            # Control mouse movement with index finger
            if fingers[1] == 1 and fingers[2] == 0:
                x3 = np.interp(x1, (frameR, wCam - frameR), (0, pyautogui.size().width))
                y3 = np.interp(y1, (frameR, hCam - frameR), (0, pyautogui.size().height))
                clocX = plocX + (x3 - plocX) / smoothening
                clocY = plocY + (y3 - plocY) / smoothening
                pyautogui.moveTo(pyautogui.size().width - clocX, clocY)
                plocX, plocY = clocX, clocY

            # Left click
            if fingers[1] == 0 and fingers[2] == 0:
                length, img, lineInfo = detector.findDistance(8, 12, img)
                if length < 40:
                    cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                    pyautogui.click()
                    time.sleep(1)       

            # Right click
            if fingers[1] == 1 and fingers[2] == 1 and len(lmList) > 0:
                length, img, lineInfo = detector.findDistance(8, 12, img)
                if length < 40:
                    pyautogui.rightClick()
                    time.sleep(0.5)

            # PPT slide control gestures
            if fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 1:
                pyautogui.press("left")  # Move back in slides.
                time.sleep(1)

            # Forward gesture (Three fingers)
            if fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 0:
                pyautogui.hotkey('alt', 'right')
                time.sleep(0.5)

            # Backward gesture (Four fingers)
            if fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 1:
                pyautogui.hotkey('alt', 'left')
                time.sleep(0.5)

            # Minimize/Restore all tabs with palm open/close
            if fingers == [1, 1, 1, 1, 1]:  # Palm open
                pyautogui.hotkey('win', 'd')
                time.sleep(1)

        # Display the image
        cv2.imshow("Gesture Control", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Function to start the gesture recognition in a separate thread
def start_gesture_control():
    global running
    if not running:
        running = True
        threading.Thread(target=gesture_control).start()

# Function to stop the gesture recognition
def stop_gesture_control():
    global running
    running = False

# Tkinter GUI for Start/Stop
root = Tk()
root.title("Gesture Control App")
root.geometry("500x400")
start_button = Button(root, text="Run", command=start_gesture_control)
start_button.pack(pady=20)

stop_button = Button(root, text="Stop", command=stop_gesture_control)
stop_button.pack(pady=20)

root.mainloop()
