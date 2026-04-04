'''
Real-Time Object Detection

Why Real-Time Detection?
In the previous section, we applied YOLO to a single image.
Now we apply it to:
 - Live camera feed
 - Video stream

This is extremely important in:
 - Self-driving cars
 - Surveillance systems
 - Robotics
 - Smart cities
 - Human-machine interaction

Because the system must:
 - Detect objects
 - Process them
 - Make decisions
 
 All in real-time

 ___________________________________________________________________

Why We Cannot Use Google Colab?

Google Colab:
 - Runs in cloud servers
 - Has no direct access to your local webcam
So we must:
Run everything locally on our own machine.


Creating Virtual Environment
Command: python -m venv YOLO-env

What this does:
- Creates isolated Python environment
- Prevents dependency conflicts
- Keeps project clean

Activate Environment
YOLO-env\Scripts\activate.bat

If activated successfully:
Terminal shows:
(YOLO-env)
This means:
All packages now install inside this folder only.

Why We Must Use GPU Instead of CPU
CPU
    - Few cores (4–16)
    - Designed for sequential operations
    - Good for general programs

GPU
- Thousands of cores
- Designed for parallel matrix operations
- Ideal for:
    - Deep learning
    - Image processing
    - Video processing

Neural networks = heavy matrix multiplications.
GPU is MUCH faster.
If you run model on CPU:
    - Camera becomes laggy
    - FPS drops
    - Detection becomes slow

'''


import torch
from transformers import YolosImageProcessor, YolosForObjectDetection
import cv2
from torchvision.ops import nms
from PIL import Image

device = torch.device("cpu")

processor = YolosImageProcessor.from_pretrained("hustvl/yolos-small")
model = YolosForObjectDetection.from_pretrained("hustvl/yolos-small").to(device)

# Define Frame Processing Function
def process_frame(frame, confidence_threshold=0.8, iou_threshold=0.5):
#  This function processes ONE frame.
# Video = many frames per second.
# Parameters:
# confidence_threshold → removes weak detections
# iou_threshold → removes overlapping boxes

# Convert BGR → RGB
    image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
# OpenCV uses BGR format.
# Deep learning models expect RGB.
# If not converted:
# Colors incorrect → lower accuracy.

# Preprocess Frame
    inputs = processor(images=image, return_tensors="pt").to(device)
# This:
# Resizes image
# Normalizes pixels
# Converts to tensor
# Adds batch dimension

# Moves tensor to GPU
    outputs = model(**inputs)
# This Produce:
# Raw class logits
# Bounding box predictions

    target_sizes = torch.tensor([image.size[::-1]])
# image.size returns:
# (width, height)
# Model expects:
# (height, width)
# So we reverse order.

    results = processor.post_process_object_detection(
        outputs, target_sizes=target_sizes
    )[0]
#  This:
# Converts normalized box coordinates to pixel values
# Filters predictions
# Returns readable results

# Extract Scores, Labels, Boxes
    scores = results["scores"]
    labels = results["labels"]
    boxes = results["boxes"]

# Apply Confidence Filtering
    keep = scores > confidence_threshold
    scores = scores[keep]
    labels = labels[keep]
    boxes = boxes[keep]

# Apply NMS (Non-Maximum Suppression)
# Removes duplicate overlapping boxes.
# Keeps highest confidence one.
    keep_indices = nms(boxes, scores, iou_threshold)
    boxes = boxes[keep_indices]
    scores = scores[keep_indices]
    labels = labels[keep_indices]

    for score, label, box in zip(scores, labels, boxes):
        xmin, ymin, xmax, ymax = box.tolist()

# Draw Bounding Boxes Using OpenCV
        cv2.rectangle(frame,
                      (int(xmin), int(ymin)),
                      (int(xmax), int(ymax)),
                      (0, 255, 0),
                      2)
#  Draws green rectangle.
# Coordinates:
# Top-left → (xmin, ymin)
# Bottom-right → (xmax, ymax)

# Add Label Text
        label_text = f"{model.config.id2label[label.item()]}: {score.item():.2f}"

        cv2.putText(frame,
                    label_text,
                    (int(xmin), int(ymin) - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    2)

    return frame

# Camera Setup
cap = cv2.VideoCapture(0) #0 = default camera. , local camera 

if not cap.isOpened():
    print("Cannot open camera")
    exit()

while True:
    ret, frame = cap.read()

    if not ret:
        break

    frame = process_frame(frame)

    cv2.imshow("Real-time Object Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()