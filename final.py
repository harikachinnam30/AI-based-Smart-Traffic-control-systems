import csv
from ultralytics import YOLO
import cv2
from sklearn.metrics import precision_score, recall_score, f1_score
import numpy as np
import matplotlib.pyplot as plt

# Load YOLOv8 model
model = YOLO("yolov8n.pt")

# Vehicle classes in COCO dataset
VEHICLE_CLASSES = {"car", "motorcycle", "bus", "truck", "bicycle"}

# Define green light duration categories
def categorize_duration(duration):
    if 10 <= duration <= 30:
        return "short"
    elif 31 <= duration <= 60: 
        return "medium"
    else:
        return "long"

# Traffic category classification
def classify_traffic_density(vehicle_count):
    if vehicle_count <= 10:
        return "low"
    elif 10 < vehicle_count <= 25:
        return "medium"
    else:
        return "high"

# Fuzzification for vehicle count (low, medium, high)
def fuzzify_vehicle_count(vehicle_count):
    low = max(min((25 - vehicle_count) / 25, 1), 0)
    medium = max(min((vehicle_count - 10) / 15, (35 - vehicle_count) / 15), 0)
    high = max(min((vehicle_count - 25) / 25, 1), 0)
    return low, medium, high

# Fuzzification for green light duration (short, medium, long)
def fuzzify_duration(duration):
    short = max(min((30 - duration) / 30, 1), 0)
    medium = max(min((duration - 10) / 50, (60 - duration) / 30), 0)
    long = max(min((duration - 60) / 60, 1), 0)
    return short, medium, long

# Defuzzification for vehicle count
def defuzzify_vehicle_count(low, medium, high):
    return (low * 10 + medium * 20 + high * 30) / (low + medium + high) if (low + medium + high) > 0 else 0

# Defuzzification for green light duration
def defuzzify_duration(short, medium, long):
    return (short * 20 + medium * 45 + long * 75) / (short + medium + long) if (short + medium + long) > 0 else 0

# Detect vehicles using YOLOv8
def detect_vehicles(frame):
    results = model(frame)  
    detected_vehicles = 0

    for result in results[0].boxes.data.tolist():
        x1, y1, x2, y2, conf, cls = result
        label = model.names[int(cls)]
        if label in VEHICLE_CLASSES:
            detected_vehicles += 1

    return detected_vehicles, results  
 
# Load dataset
dataset = {}
with open("traffic_density_dataset.csv", mode="r") as file:
    reader = csv.DictReader(file)
    for row in reader:
        vehicle_count = int(row["vehicle_count"])
        category_expected = row["category_expected"]
        duration_expected = row["duration_expected"]
        dataset[vehicle_count] = (category_expected, duration_expected)

# List of video files to process
video_files = ["V.mp4", "Vid.mp4", "Video.mp4","Video11.mp4","Video12.mp4"]  # Add your video files here

# Metrics for all videos
overall_accuracy = []
overall_precision = []
overall_recall = []
overall_f1 = []

# Process each video
for video_file in video_files:
    print(f"Processing video: {video_file}")
    cap = cv2.VideoCapture(video_file)
    correct_predictions = 0
    total_sides = 0
    traffic_data = {}
    y_true_categories = []
    y_pred_categories = []
    sides = ["Side A", "Side B", "Side C", "Side D"]
    
    for side in sides:
        ret, frame = cap.read()
        if not ret:
            print(f"Failed to read frame for {side} in {video_file}")
            break

        # Detect vehicles
        vehicle_count, results = detect_vehicles(frame)
        traffic_category = classify_traffic_density(vehicle_count)

        # Fuzzify vehicle count and green light duration
        low, medium, high = fuzzify_vehicle_count(vehicle_count)
        short, medium_duration, long = fuzzify_duration((vehicle_count / 120) * 120)  # Green light duration scaled to 120s

        # Defuzzify the results to get crisp values
        crisp_vehicle_count = defuzzify_vehicle_count(low, medium, high)
        crisp_duration = defuzzify_duration(short, medium_duration, long)

        # Use defuzzified values for green light duration
        green_duration = crisp_duration 
        total_vehicles = sum([detect_vehicles(frame)[0] for _ in sides]) or 1
        duration_category = categorize_duration(green_duration)

        # Compare with dataset (only category)
        expected_category, expected_duration = dataset.get(vehicle_count, ("unknown", "unknown"))
        category_match = (traffic_category == expected_category)

        # Append true and predicted categories for metric calculation
        y_true_categories.append(expected_category)
        y_pred_categories.append(traffic_category)

        if category_match:
            correct_predictions += 1

        total_sides += 1

        # Store data for each side
        traffic_data[side] = {
            "vehicle_count": vehicle_count,
            "traffic_category": traffic_category,
            "green_duration": green_duration,
            "duration_category": duration_category,
            "expected_category": expected_category,
            "expected_duration": expected_duration,
        }

    # Calculate accuracy based only on category match
    accuracy = (correct_predictions / total_sides) * 100 if total_sides > 0 else 0

    # Performance metrics: Precision, Recall, F1 Score
    precision = precision_score(y_true_categories, y_pred_categories, average='weighted', labels=np.unique(y_pred_categories), zero_division=1)
    recall = recall_score(y_true_categories, y_pred_categories, average='weighted', labels=np.unique(y_pred_categories), zero_division=1)
    f1 = f1_score(y_true_categories, y_pred_categories, average='weighted', labels=np.unique(y_pred_categories), zero_division=1)
    
    # Store metrics for averaging
    overall_accuracy.append(accuracy)
    overall_precision.append(precision)
    overall_recall.append(recall)
    overall_f1.append(f1)

    # Print metrics for the current video
    print("*************** TRAFFIC LIGHT TIMINGS ****************")
    for side, data in traffic_data.items():
        print(f"{side}:")
        print(f"  Vehicle count: {data['vehicle_count']}")
        print(f"  Traffic category: {data['traffic_category']}")
        print(f"  Expected category: {data['expected_category']}")
        print(f"  Expected duration: {data['expected_duration']}")
        print(f"  Recommended green light duration: {data['green_duration']:.2f} seconds - {data['duration_category']}")
        print()

    print(f"Accuracy : {accuracy:.2f}%")
    print(f"Precision : {precision:.2f}")
    print(f"Recall : {recall:.2f}")
    print(f"F1 Score : {f1:.2f}")
    print(f"****************************************************")
    cap.release()

# Calculate average metrics
avg_accuracy = np.mean(overall_accuracy)
avg_precision = np.mean(overall_precision)
avg_recall = np.mean(overall_recall)
avg_f1 = np.mean(overall_f1)

# Plot the overall metrics
metrics = ['Average Accuracy', 'Average Precision', 'Average Recall', 'Average F1 Score']
values = [avg_accuracy / 100, avg_precision, avg_recall, avg_f1]  # Normalize accuracy to a 0-1 scale

plt.figure(figsize=(10, 6))
plt.bar(metrics, values, color=['blue', 'green', 'orange', 'red'])
plt.title('Traffic Detection Model Performance Metrics',fontsize=14, pad=20)
plt.ylabel('Scores',fontsize=12)
plt.ylim(0, 1)  # Limiting the y-axis to 0-1 for better comparison
for i, v in enumerate(values):
    plt.text(i, v + 0.02, f"{v * 100:.2f}%" if i == 0 else f"{v:.2f}", ha='center', fontsize=12)

plt.show()
