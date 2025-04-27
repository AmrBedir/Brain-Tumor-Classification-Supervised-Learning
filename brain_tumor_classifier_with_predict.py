import os
import numpy as np
import cv2
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
from tkinter import Tk, filedialog
from PIL import Image, ImageTk
import tkinter as tk

# ====================== 1. Data Preparation ======================
def load_data(data_dir="brain_tumor_dataset", img_size=128):
    """Load images from subfolders and prepare dataset."""
    images = []
    labels = []
    class_mapping = {
        'normal': 0,  # Map class names to numeric labels
        'glioma_tumor': 1,
        'meningioma_tumor': 2,
        'pituitary_tumor': 3
    }
    
    # Iterate through each class and load images
    for class_name, class_label in class_mapping.items():
        class_dir = os.path.join(data_dir, class_name)
        for img_file in os.listdir(class_dir):
            img_path = os.path.join(class_dir, img_file)
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                img = cv2.resize(img, (img_size, img_size))
                images.append(img.flatten())
                labels.append(class_label)
    
    return np.array(images), np.array(labels)

# ====================== 2. Model Building and Training ======================
def train_model(X_train, y_train):
    """Train a Random Forest model."""
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    return model

# ====================== 3. Evaluation ======================
def evaluate_model(model, X_test, y_test, class_names):
    """Evaluate the model and display results."""
    y_pred = model.predict(X_test)
    
    # Classification Report
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=class_names))
    
    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=class_names, yticklabels=class_names)
    plt.title("Confusion Matrix")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.show()

# ====================== 4. Enhanced Prediction GUI ======================
def predict_external_image(model, img_size=128):
    """Enhanced GUI for image selection and prediction results."""
    # Initialize Tkinter and hide the main window
    root = Tk()
    root.withdraw()
    
    # Open file dialog to select an image
    file_path = filedialog.askopenfilename(
        title="Select Brain MRI Scan",
        filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tif")]
    )
    
    if not file_path:
        print("No file selected.")
        return
    
    # Read and preprocess the selected image
    img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print("Error: Could not read the image.")
        return
    
    # Resize and flatten the image
    img_resized = cv2.resize(img, (img_size, img_size))
    img_flat = img_resized.flatten().reshape(1, -1)
    
    # Predict the class
    class_names = ['Normal', 'Glioma Tumor', 'Meningioma Tumor', 'Pituitary Tumor']
    prediction = model.predict(img_flat)
    proba = model.predict_proba(img_flat)[0]
    
    # Create the results window
    result_window = tk.Toplevel()
    result_window.title("Brain Tumor Classification Result")
    result_window.geometry("800x600")
    result_window.configure(bg='#f0f0f0')
    
    # Header
    header_frame = tk.Frame(result_window, bg='#2c3e50')
    header_frame.pack(fill='x', padx=10, pady=10)
    
    header_label = tk.Label(
        header_frame,
        text="Brain Tumor Classification Result",
        font=('Helvetica', 16, 'bold'),
        fg='white',
        bg='#2c3e50'
    )
    header_label.pack(pady=10)
    
    # Image display
    img_frame = tk.Frame(result_window, bg='#f0f0f0')
    img_frame.pack(pady=10)
    
    img_display = Image.fromarray(img_resized)
    img_display = ImageTk.PhotoImage(img_display)
    
    img_label = tk.Label(img_frame, image=img_display, borderwidth=2, relief='solid')
    img_label.image = img_display
    img_label.pack()
    
    # Prediction result
    result_frame = tk.Frame(result_window, bg='#f0f0f0')
    result_frame.pack(pady=10)
    
    pred_text = f"Prediction: {class_names[prediction[0]]}"
    pred_label = tk.Label(
        result_frame,
        text=pred_text,
        font=('Helvetica', 14, 'bold'),
        fg='#27ae60' if prediction[0] == 0 else '#e74c3c',
        bg='#f0f0f0'
    )
    pred_label.pack(pady=5)
    
    # Confidence meter
    confidence_frame = tk.Frame(result_window, bg='#f0f0f0')
    confidence_frame.pack(pady=10)
    
    confidence_label = tk.Label(
        confidence_frame,
        text="Classification Confidence:",
        font=('Helvetica', 12),
        bg='#f0f0f0'
    )
    confidence_label.pack()
    
    confidence = int(proba[prediction[0]] * 100)
    confidence_color = '#2ecc71' if confidence > 70 else '#f39c12' if confidence > 50 else '#e74c3c'
    
    canvas = tk.Canvas(confidence_frame, width=300, height=20, bg='#ecf0f1', highlightthickness=0)
    canvas.pack(pady=5)
    canvas.create_rectangle(0, 0, confidence * 3, 20, fill=confidence_color, outline='')
    canvas.create_text(150, 10, text=f"{confidence}%", font=('Helvetica', 10, 'bold'))
    
    # Detailed probabilities
    proba_frame = tk.Frame(result_window, bg='#f0f0f0')
    proba_frame.pack(pady=10)
    
    proba_label = tk.Label(
        proba_frame,
        text="Detailed Probabilities:",
        font=('Helvetica', 12),
        bg='#f0f0f0'
    )
    proba_label.pack()
    
    for i, (class_name, prob) in enumerate(zip(class_names, proba)):
        row_frame = tk.Frame(proba_frame, bg='#f0f0f0')
        row_frame.pack(fill='x', padx=50, pady=2)
        
        class_label = tk.Label(
            row_frame,
            text=class_name,
            width=20,
            anchor='w',
            font=('Helvetica', 10),
            bg='#f0f0f0'
        )
        class_label.pack(side='left')
        
        prob_bar = tk.Canvas(row_frame, width=200, height=15, bg='#ecf0f1', highlightthickness=0)
        prob_bar.pack(side='left', padx=5)
        prob_bar.create_rectangle(0, 0, prob * 200, 15, fill='#3498db', outline='')
        
        prob_text = tk.Label(
            row_frame,
            text=f"{prob:.2%}",
            width=10,
            anchor='w',
            font=('Helvetica', 10),
            bg='#f0f0f0'
        )
        prob_text.pack(side='left')
    
    # Close button
    button_frame = tk.Frame(result_window, bg='#f0f0f0')
    button_frame.pack(pady=20)
    
    close_button = tk.Button(
        button_frame,
        text="Close",
        command=result_window.destroy,
        font=('Helvetica', 10),
        bg='#e74c3c',
        fg='white',
        activebackground='#c0392b',
        padx=20,
        pady=5,
        borderwidth=0
    )
    close_button.pack()

# ====================== 5. Main Execution ======================
if __name__ == "__main__":
    # Dataset directory
    data_dir = "brain_tumor_dataset"
    img_size = 128
    
    # Load dataset
    print("Loading data...")
    X, y = load_data(data_dir, img_size)
    print(f"Dataset loaded. Shape of X: {X.shape}, Shape of y: {y.shape}")
    
    # Split dataset
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print("Data split into training and testing sets.")
    
    # Train the model
    print("Training the model...")
    class_names = ['normal', 'glioma_tumor', 'meningioma_tumor', 'pituitary_tumor']
    model = train_model(X_train, y_train)
    print("Model training completed.")
    
    # Evaluate the model
    print("Evaluating the model...")
    evaluate_model(model, X_test, y_test, class_names)
    
    # Prediction loop
    while True:
        print("\nOptions:")
        print("1. Predict an external image")
        print("2. Exit")
        choice = input("Enter your choice (1 or 2): ")
        
        if choice == '1':
            predict_external_image(model, img_size)
        elif choice == '2':
            break
        else:
            print("Invalid choice. Please try again.")