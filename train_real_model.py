import os
import pickle
import numpy as np
import cv2
from sklearn.ensemble import RandomForestClassifier
from Crop_Detection.model_loader import DISEASE_LABELS, extract_features, RealDiseaseDetectionModel

def generate_synthetic_image(class_name, size=(224, 224)):
    """
    Generates a synthetic plant leaf image based on the disease class.
    Returns RGB image normalized to [0, 1]
    """
    # Start with a base green leaf color (varying slightly)
    base_green = np.array([
        np.random.randint(30, 80),   # R
        np.random.randint(120, 180), # G
        np.random.randint(30, 80)    # B
    ], dtype=np.uint8)
    
    img = np.zeros((size[0], size[1], 3), dtype=np.uint8)
    img[:] = base_green
    
    # Add some noise for realism
    noise = np.random.randint(-20, 20, (size[0], size[1], 3), dtype=np.int16)
    img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    
    num_spots = np.random.randint(5, 20)
    
    if class_name == 'Healthy':
        # Just pure green leaf with noise, maybe some lighter green veins
        pass
        
    elif class_name == 'Rust':
        # Orange/brown spots
        for _ in range(num_spots):
            cx = np.random.randint(0, size[1])
            cy = np.random.randint(0, size[0])
            r = np.random.randint(5, 15)
            color = (
                np.random.randint(180, 230), # R
                np.random.randint(80, 130),  # G
                np.random.randint(20, 50)    # B
            )
            cv2.circle(img, (cx, cy), r, color, -1)
            # Add blur to make spots look more natural
            
    elif class_name == 'Powdery Mildew':
        # White/grey fuzzy patches
        for _ in range(num_spots * 2):
            cx = np.random.randint(0, size[1])
            cy = np.random.randint(0, size[0])
            r = np.random.randint(10, 25)
            color = (
                np.random.randint(200, 255),
                np.random.randint(200, 255),
                np.random.randint(200, 255)
            )
            cv2.circle(img, (cx, cy), r, color, -1)
            
    elif class_name == 'Leaf Spot':
        # Dark brown/black spots with yellow halos sometimes
        for _ in range(num_spots):
            cx = np.random.randint(0, size[1])
            cy = np.random.randint(0, size[0])
            r = np.random.randint(3, 10)
            
            # Optional yellow halo
            if np.random.random() > 0.5:
                cv2.circle(img, (cx, cy), r+3, (180, 180, 50), -1)
                
            color = (
                np.random.randint(0, 40),
                np.random.randint(0, 40),
                np.random.randint(0, 40)
            )
            cv2.circle(img, (cx, cy), r, color, -1)
            
    # Apply a slight blur to make it look less like sharp geometric shapes
    img = cv2.GaussianBlur(img, (5, 5), 0)
    
    return img.astype('float32') / 255.0


def train_model():
    print("Generating synthetic training data for real machine learning model...")
    X_train = []
    y_train = []
    
    samples_per_class = 150
    
    for idx, label in enumerate(DISEASE_LABELS):
        print(f"  Generating {samples_per_class} images for {label}...")
        for _ in range(samples_per_class):
            img = generate_synthetic_image(label)
            features = extract_features(img)
            X_train.append(features)
            y_train.append(idx)
            
    X_train = np.array(X_train)
    y_train = np.array(y_train)
    
    print(f"Training RandomForest on {len(X_train)} samples with {X_train.shape[1]} features...")
    rf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    rf.fit(X_train, y_train)
    
    score = rf.score(X_train, y_train)
    print(f"Training Accuracy: {score * 100:.2f}%")
    
    # Wrap in our standard interface
    wrapped_model = RealDiseaseDetectionModel(rf)
    
    model_dir = os.path.join(os.path.dirname(__file__), 'model')
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, 'plant_model.pkl')
    
    print(f"Saving real ML model to {model_path}...")
    with open(model_path, 'wb') as f:
        pickle.dump(wrapped_model, f)
        
    print("Model trained and saved successfully!")

if __name__ == '__main__':
    train_model()
