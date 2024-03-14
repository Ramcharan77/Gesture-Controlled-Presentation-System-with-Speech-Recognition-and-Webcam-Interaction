import shutil
import tkinter as tk
from tkinter import filedialog
import os
import re
import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import speech_recognition as sr
width ,height=1920,1080
# Function to ask the user to select a folder using tkinter file dialog
# Initialize the speech recognizer
recognizer = sr.Recognizer()

# Function to recognize speech
def recognize_speech():
    with sr.Microphone() as source:
        print("Listening...")
        cv2.rectangle(img_combined, (0, img_combined.shape[0] - 100), (img_combined.shape[1], img_combined.shape[0]),(0, 0, 0), -1)
        cv2.putText(img_combined, 'Listening...', (50, img_combined.shape[0] - 50), cv2.FONT_HERSHEY_SIMPLEX, 1,(255, 255, 255), 2)
        cv2.imshow("slides", img_combined) 
        cv2.waitKey(1) 
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source)

    try:
        print("Recognizing...")
        cv2.rectangle(img_combined, (0, img_combined.shape[0] - 100), (img_combined.shape[1], img_combined.shape[0]),(0, 0, 0), -1)
        cv2.putText(img_combined, 'Recognizing...', (50, img_combined.shape[0] - 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255),2)
        cv2.imshow("slides", img_combined)  # Display the updated image
        cv2.waitKey(1)  # Needed to update the display
        text = recognizer.recognize_google(audio)
        print("You said:", text)
        return text.lower()
    except sr.UnknownValueError:
        print("Sorry, I could not understand your command.")
        cv2.rectangle(img_combined, (0, img_combined.shape[0] - 100), (img_combined.shape[1], img_combined.shape[0]),(0, 0, 0), -1)
        cv2.putText(img_combined, 'Sorry, I could not understand your command.', (50, img_combined.shape[0] - 50), cv2.FONT_HERSHEY_SIMPLEX, 1,(255, 255, 255), 2)
        cv2.imshow("slides", img_combined)  
        cv2.waitKey(1)  
        return ""
    except sr.RequestError as e:
        print("Error:", e)
        return ""

# Function to ask the user to select a folder using tkinter file dialog
def select_folder():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    folder_path = filedialog.askdirectory(title="Select Folder")
    if folder_path:
        return folder_path
    else:
        print("Folder selection cancelled.")
        return None

# Get the folder path selected by the user
selected_folder = select_folder()

def rename_png_files(folder_path):
   
    png_files = [file for file in os.listdir(folder_path) if file.endswith('.png')]
    
    png_files.sort()
    for index, old_name in enumerate(png_files, start=1):
        new_name = f"{index}.png"
        old_path = os.path.join(folder_path, old_name)
        new_path = os.path.join(folder_path, new_name)
        os.rename(old_path, new_path)
        print(f"Renamed: {old_name} -> {new_name}")

if selected_folder:
    rename_png_files(selected_folder)
#camera
cap=cv2.VideoCapture(0)
cap.set(3,width)
cap.set(4,height)
#img list
pattern = r"(\d+)"  # Regular expression pattern to extract numeric part
pathImages = sorted(os.listdir(selected_folder), key=lambda x: int(re.findall(pattern, x)[0]))
#print(pathImages)
#var
imgno=0
hs , ws =int(120*1) ,int(180*1)
gestureThreshold=300
buttonPressed=False
buttoncounter=0
buttondelay=15
annotations=[[]]
annotationNo=0
annotationstart=False
#hand dectector
det=HandDetector(detectionCon=0.9,maxHands=1)
while True:
    #images
    success , img=cap.read()
    img=cv2.flip(img,1)
    pathFullimage=os.path.join(selected_folder,pathImages[imgno])
    imgcurr=cv2.imread(pathFullimage)
    hands,img=det.findHands(img)
    cv2.line(img,(0,gestureThreshold),(width,gestureThreshold),(0,255,0),10)
    print(annotationNo)
    if hands and buttonPressed is False:
        hand=hands[0]
        fingers=det.fingersUp(hand)
        cx,cy=hand['center']
        lmList=hand['lmList']
        #constrain values for easier drawing
        xVal=int(np.interp(lmList[8][0],[width//2,width],[0,width]))
        yVal =int(np.interp(lmList[8][1], [100,height], [0, height]))
        indexFinger=xVal,yVal
        #print(fingers)

        if cy<=gestureThreshold:#if hand is at the height is at face
            # g-1 left
            if fingers == [1, 0, 0, 0, 0]:
                annotationstart = False
                print("left")
                if imgno > 0:
                    buttonPressed = True
                    annotations = [[]]
                    annotationNo = 0
                    imgno -= 1
            # g-2 right
            if fingers == [0, 0, 0, 0, 0]:
                annotationstart = False
                print("right")
                if imgno < len(pathImages) - 1:
                    buttonPressed = True
                    annotations = [[]]
                    annotationNo = 0
                    imgno += 1
            if fingers ==[1,1,1,1,1]:
                annotationstart = False
                command = recognize_speech()
                if command.startswith("open slide"):
                    try:
                        slide_number = int(command.split()[-1]) - 1  # Convert "go to slide 1" to slide index
                        if 0 <= slide_number < len(pathImages):
                            imgno = slide_number
                            annotations = [[]]
                            print(f"Going to slide {slide_number + 1}")
                        else:
                            print("Slide number out of range.")
                    except ValueError:
                        print("Invalid command format.")
                if command == "next":
                    # Code to move to the next slide
                    annotationstart = False
                    print("right")
                    if imgno < len(pathImages) - 1:
                        buttonPressed = True
                        annotations = [[]]
                        annotationNo = 0
                        imgno += 1
                elif command == "previous":
                    annotationstart = False
                    print("left")
                    if imgno > 0:
                        buttonPressed = True
                        annotations = [[]]
                        annotationNo = 0
                        imgno -= 1
                    # Code to move to the previous slide
                elif command == "delete":
                    if annotations:
                        if annotationNo >= 0:
                            annotations.pop(-1)
                            annotationNo -= 1
                            buttonPressed = True
                elif command == "terminate":
                    shutil.rmtree(selected_folder)
                    print(f"The folder at {selected_folder} has been successfully deleted.")
                    break
                elif command == "delete all":
                    buttonPressed = True
                    annotations = [[]]
                    annotationNo = 0

            if fingers == [1, 1, 0, 0, 1]:
                    shutil.rmtree(selected_folder)
                    print(f"The folder at {selected_folder} has been successfully deleted.")
                    break
        #g-3 -show pointer
        if fingers==[0,1,1,0,0]:
            cv2.circle(imgcurr,indexFinger,8,(0,0,255),cv2.FILLED)
            annotationstart = False
        # g-4 -draw pointer
        if fingers == [0, 1, 0, 0, 0]:
            if annotationstart is False:
                annotationstart=True
                annotationNo+=1
                annotations.append([])
            cv2.circle(imgcurr, indexFinger, 12, (0, 0, 255), cv2.FILLED)
            annotations[annotationNo].append(indexFinger)
        else:
            annotationstart=False
        #g-5 -erase
        if fingers == [0, 1, 1, 1, 0]:
            if annotations:
                if annotationNo>=0:
                    annotations.pop(-1)
                    annotationNo-=1
                    buttonPressed=True
    else:
        annotationstart = False
    #button pressed iterations
    if buttonPressed:
        buttoncounter+=1
        if buttoncounter>buttondelay:
            buttoncounter=0
            buttonPressed=False
    for i in range(len(annotations)):
        for j in range(len(annotations[i])):
            if j!=0:
                cv2.line(imgcurr,annotations[i][j-1],annotations[i][j],(0,0,200),12)
    #adding  webcam in the site
    imgsmall=cv2.resize(img,(ws,hs))
    h,w,_=imgcurr.shape
    imgsmall_resized = cv2.resize(imgsmall, (ws, hs))

    # Create a black canvas to place the resized imgsmall
    canvas = np.zeros((imgcurr.shape[0], ws, 3), dtype=np.uint8)

    # Place the resized imgsmall on the canvas
    canvas[:imgsmall_resized.shape[0], :imgsmall_resized.shape[1]] = imgsmall_resized

    # Concatenate the canvas with imgcurr to create the final combined image
    img_combined = cv2.hconcat([imgcurr, canvas])
    cv2.imshow("slides", img_combined)
    key=cv2.waitKey(1)