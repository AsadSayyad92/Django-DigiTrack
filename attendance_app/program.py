import cv2
from pyzbar.pyzbar import decode
from datetime import datetime,date
import re,uuid,calendar

def BarcodeReader():

    cap = cv2.VideoCapture(0)

    # Flag to indicate whether a barcode has been detected
    barcode_detected = False

    while not barcode_detected:
        # Capture frame-by-frame
        ret, frame = cap.read()
        
        # Convert frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply histogram equalization to enhance contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        equalized = clahe.apply(gray)
        
        # Decode the barcode image
        detectedBarcodes = decode(equalized)
        
        # If not detected then continue
        if not detectedBarcodes:
            continue

    # If not detected then print the message
        if not detectedBarcodes:
            print("Barcode Not Detected or your barcode is blank/corrupted!")
        else:
        # Traverse through all the detected barcodes in image
            for barcode in detectedBarcodes:
                (x, y, w, h) = barcode.rect
                
                # Put the rectangle in image using
                # cv2 to highlight the barcode
                cv2.rectangle(frame, (x-10, y-10),
                            (x + w+10, y + h+10),
                            (255, 0, 0), 2)
                
                if barcode.data!="":
                    # Print the barcode data
                    print(str(barcode.data)[2:-1])
                    now=datetime.now()
                    currentDay=date.today()
                    
                    barcode_detected = True
                    # Break out of the for loop
                    print(now)
                    x = calendar.day_name[currentDay.weekday()]
                    print(x)
                    break
                        
                # Display the resulting frame
                cv2.imshow('frame', frame)
        
        # Exit if 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Release the camera
    cap.release()
    cv2.destroyAllWindows()
 
if __name__ == "__main__":
    BarcodeReader()
	
