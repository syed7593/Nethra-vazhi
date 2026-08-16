from ultralytics import YOLO
import cv2
# namude models pothole detectioninu vendi train cheythathum, coco datasetil train cheythathum aanu
pothole_model = YOLO("runs/detect/pothole_yolo26/weights/best.pt")
coco_model = YOLO("yolo26n.pt")
class_for_coco=['person', 'bicycle', 'motorcycle', 'car', 'bus', 'truck', 'traffic light', 'stop sign']
cap=cv2.VideoCapture(0) #by default camera 0 aanu open cheyyunnathu athayath web cam aanu open cheyyunnathu
while True:
    ret,frame=cap.read() #frame read cheyyunnathu
    if not ret:
        break
    #farme il detect cheyyunnathu,conf mean cheyyunnathu confidence level,verbose=False mean cheyyunnathu verbose output display cheyyathirikkanam ennath
    coco_results=coco_model(frame,conf=0.5,verbose=False)[0] #coco modelil detect cheyyunnathu
    pothole_result=pothole_model(frame,conf=0.7,verbose=False)[0] #pothhole modelil detect cheyyunnathu 
    ano_frame=frame.copy() #ano_frame mean cheyyunnathu original frame copy cheyyunnathu
    #coco modelil detect cheytha results ano_frame il draw cheyyunnathu
    for box in coco_results.boxes:
        cls_id=int(box.cls[0]) #class id mean cheyyunnathu boxil ninn class id edukkunnathu
        class_name=coco_model.names[cls_id] #class name mean cheyyunnathu class id ninn class name edukkunnathu
        if class_name in class_for_coco:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])

            cv2.rectangle(ano_frame, (x1, y1), (x2, y2), (0, 255, 0), 2) #rectangle draw cheyyunnathu  
            label = f"{class_name} {conf:.2f}" #label mean cheyyunnathu class name and confidence level
            cv2.putText(ano_frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2) #l3
    for box in pothole_result.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0]) #boxil ninn coordinates edukkunnathu
        conf = float(box.conf[0])#confidence level edukkunnathu
        cv2.rectangle(ano_frame,(x1,y1),(x2,y2),(0,0,255),2) #rectangle draw cheyyunnathu
        label=f"pothole {conf:.2f}" #label mean cheyyunnathu pothole and confidence level
        cv2.putText(ano_frame, label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    cv2.imshow("Frame", ano_frame) #display cheyyunnathu
    if cv2.waitKey(1) & 0xFF == ord('q'): #q press cheythal exit cheyyunnathu
        break
cap.release()
cv2.destroyAllWindows()