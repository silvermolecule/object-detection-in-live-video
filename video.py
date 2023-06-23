from datetime import datetime
from tabnanny import check
import cv2
from cv2 import threshold
import pandas 

first_frame = None
status_list = [None, None]
times = []
video = cv2.VideoCapture(0)
df = pandas.DataFrame(columns= ["Start","End"])

while True:
    check, frame = video.read()

    status = 0
    gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray,(21,21),0) #blurring the current frame for better processing

    if first_frame is None:
        first_frame = gray #assigning the base frame
        continue
    
    delta_frame = cv2.absdiff(first_frame,gray) #figuring out the difference between current frame and base frame
    thresh_frame = cv2.threshold(delta_frame,30,255,cv2.THRESH_BINARY)[1] #setting the threshold frame above which the frame is converted to white image
    thresh_frame = cv2.dilate(thresh_frame,None, iterations= 5) #dilating the video for smooth processing

    (cnts,_) = cv2.findContours(thresh_frame.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)#finding the contours

    for contour in cnts: #iterating through all the contours to check for moving objects and identify them
        if cv2.contourArea(contour) < 2000: #change the pixel size based on the size of theo bject you want to detect
            continue  
        status = 1                                          
        (x,y,w,h) = cv2.boundingRect(contour)
        cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),4)
    status_list.append(status)
    if status_list[-1] == 1 and status_list [-2] == 0:
        times.append(datetime.now())
    if status_list[-1] == 0 and status_list [-2] == 1:
        times.append(datetime.now())
    
    cv2.imshow("Frame",frame) #showing the moving objects in the frame
    
    key = cv2.waitKey(1)
    if key == ord('w'):
        if status==1: #to store the value of change at the last frame even if no object is moving
            times.append(datetime.now())
        break

print(status_list)
print(times)

for i in range(0,len(times),2):
    df = df.append({"Start": times[i],"End": times [i+1]},ignore_index= True)

df.to_excel("Times.xlsx")
video.release()
cv2.destroyAllWindows()