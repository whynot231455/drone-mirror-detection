import cv2

# Test indices 0 through 4 (0 is usually built-in, external is often 1, 2, or 3)
for i in range(5):
    cap = cv2.VideoCapture(i, cv2.CAP_DSHOW) # Use CAP_DSHOW for better Windows compatibility
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            print(f"Camera index {i} is working. Checking its resolution...")
            width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            print(f"Resolution: {width}x{height}")
            
            # Show the video feed for visual confirmation
            cv2.imshow(f"Camera Index {i}", frame)
            cv2.waitKey(1000) # Show for 1 second
            cv2.destroyAllWindows()
            
        else:
            print(f"Camera index {i} opened, but failed to read a frame.")
        
        cap.release()
    else:
        print(f"Camera index {i} failed to open.")

print("Testing complete. Note the index of your external webcam.")