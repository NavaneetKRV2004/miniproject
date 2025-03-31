import cv2
import face_recognition
import numpy as np
import threading
import ui

def uimain():
	print("ui")
	ui.main()
    

t1=threading.Thread(target=uimain)

live_feed=True
# Load known faces and their names
known_face_encodings = []
known_face_names = []

lock = threading.Lock()

face_locations = []
face_encodings = []

def detect_faces(rgb_frame):
    """Detect faces and update global face_locations."""
    global face_locations
    locations = face_recognition.face_locations(rgb_frame)
    with lock:
        face_locations[:] = locations  # Update shared variable safely

def encode_faces(rgb_frame):
    """Encode faces and update global face_encodings."""
    global face_encodings
    with lock:
        encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        face_encodings[:] = encodings  # Update shared variable safely
        

# Load an image and encode it
def load_known_face(image_path, name):
    image = face_recognition.load_image_file(image_path)
    encoding = face_recognition.face_encodings(image)[0]
    known_face_encodings.append(encoding)
    known_face_names.append(name)

# Add known faces (Add your own images here)
import os

folder_path = "faces"  

# Loop through all files in the folder
for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)

 
    if os.path.isfile(file_path) and filename.split(".")[-1] in ["jpeg","jpg"]:
        try:
            print(file_path)
            load_known_face(file_path,filename.split(".")[0])
        except Exception as e:
            print(f"Could not read {filename}: {e}")


# Open webcam
cap = cv2.VideoCapture(0)


while True:
	
	
	ret, frame = cap.read()
	if not ret:
		break

	
		# Convert to RGB (OpenCV uses BGR, face_recognition uses RGB)
	rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

		# Detect faces
	face_locations = face_recognition.face_locations(rgb_frame)
	face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
	

	for face_encoding, (top, right, bottom, left) in zip(face_encodings, face_locations):
			# Compare with known faces
		matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
		name = "Unknown"

		# Find the best match
		face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
		best_match_index = np.argmin(face_distances)

		if matches[best_match_index]:
			name = known_face_names[best_match_index]

		if live_feed==True:
			# Draw rectangle and label
			cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
			cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
		else:
			print(name)
  # Show video feed
	if True :#live_feed==True:
		cv2.imshow("Face Recognition", frame)
	

    # Press 'q' to exit
	if cv2.waitKey(1) & 0xFF == ord("q"):
		break

cap.release()
cv2.destroyAllWindows()
