import os
import json
import numpy as np
from PIL import Image
from django.conf import settings
import pickle
import cv2


# Disease labels
DISEASE_LABELS = ['Healthy', 'Powdery Mildew', 'Rust', 'Leaf Spot']

# Cache for the model
_model = None
_model_type = None  # 'keras' or 'mock'


def get_model():
    """
    Load and cache the model (Keras or mock).
    Returns the loaded model or mock model object.
    """
    global _model, _model_type
    
    if _model is None:
        model_path = os.path.join(settings.BASE_DIR, 'model', 'plant_model.pkl')
        keras_model_path = os.path.join(settings.BASE_DIR, 'model', 'plant_model.h5')
        
        # Try to load pickle model first (works without TensorFlow)
        if os.path.exists(model_path):
            try:
                with open(model_path, 'rb') as f:
                    _model = pickle.load(f)
                _model_type = 'mock'
                return _model
            except Exception as e:
                print(f"Failed to load pickle model: {e}")
        
        # Fall back to Keras model if available
        if os.path.exists(keras_model_path):
            try:
                from tensorflow.keras.models import load_model
                _model = load_model(keras_model_path)
                _model_type = 'keras'
                return _model
            except Exception as e:
                print(f"TensorFlow not available or model load failed: {e}")
        
        # If no model exists, create a mock model
        if _model is None:
            _model = create_mock_model()
            _model_type = 'mock'
    
    return _model


def create_mock_model():
    """
    Create a simple mock model that returns random predictions.
    Used when TensorFlow is not available.
    """
    class MockModel:
        def __init__(self):
            self.name = "Mock Plant Disease Detection Model"
        
        def predict(self, images, verbose=0):
            """
            Return mock predictions.
            Returns array of shape (batch_size, num_classes)
            """
            batch_size = len(images)
            # Generate random predictions that sum to 1
            predictions = np.random.dirichlet(np.ones(len(DISEASE_LABELS)), batch_size)
            return predictions
    
    return MockModel()


def preprocess_image(image_path, target_size=(224, 224)):
    """
    Preprocess image for model prediction.
    
    Args:
        image_path: Path to the image file
        target_size: Target size for the image (default 224x224)
    
    Returns:
        Preprocessed image array ready for prediction
    """
    try:
        # Open image
        img = Image.open(image_path).convert('RGB')
        
        # Resize to target size
        img = img.resize(target_size)
        
        # Convert to array
        img_array = np.array(img)
        
        # Normalize pixel values to [0, 1]
        img_array = img_array.astype('float32') / 255.0
        
        # Add batch dimension
        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array
    
    except Exception as e:
        raise Exception(f"Failed to preprocess image: {str(e)}")


def is_leaf(image_path, threshold=0.05):
    """
    Check if the image is likely a leaf using color heuristics.
    
    Args:
        image_path: Path to the image file
        threshold: Minimum percentage (0.0 to 1.0) of leaf-like colors required
    
    Returns:
        Boolean indicating if the image passes the leaf check
    """
    try:
        # Read image using OpenCV
        img = cv2.imread(image_path)
        if img is None:
            return False
            
        # Convert to HSV color space
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Define color ranges for leaves (green, yellow, brown)
        # These are approximate HSV ranges
        # Green
        lower_green = np.array([25, 40, 40])
        upper_green = np.array([90, 255, 255])
        
        # Yellow/Brown (diseased/dry leaves)
        lower_yellow_brown = np.array([10, 40, 40])
        upper_yellow_brown = np.array([24, 255, 255])
        
        # Create masks
        mask_green = cv2.inRange(hsv, lower_green, upper_green)
        mask_yellow_brown = cv2.inRange(hsv, lower_yellow_brown, upper_yellow_brown)
        
        # Combine masks
        combined_mask = cv2.bitwise_or(mask_green, mask_yellow_brown)
        
        # Calculate percentage of leaf-colored pixels
        total_pixels = img.shape[0] * img.shape[1]
        leaf_pixels = cv2.countNonZero(combined_mask)
        
        ratio = leaf_pixels / total_pixels
        
        return ratio >= threshold
        
    except Exception as e:
        print(f"Error in is_leaf check: {e}")
        # If the check fails (e.g. invalid image format), assume it's not a valid leaf
        return False


def predict_disease(image_path):
    """
    Predict disease from an image.
    
    Args:
        image_path: Path to the image file
    
    Returns:
        Dictionary with:
            - disease: Predicted disease name
            - confidence: Confidence percentage (0-100)
            - label_index: Index of the predicted label
            - all_predictions: Dict of all disease probabilities
    """
    try:
        # Check if the image is actually a leaf
        if not is_leaf(image_path):
            raise ValueError("The uploaded image does not appear to be a plant leaf. Please upload a clear image of a leaf.")
            
        # Get model
        model = get_model()
        
        # Preprocess image
        img_array = preprocess_image(image_path)
        
        # Make prediction
        predictions = model.predict(img_array, verbose=0)
        predicted_index = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_index]) * 100
        
        # Round confidence to 2 decimal places
        confidence = round(confidence, 2)
        
        # Get disease label
        disease = DISEASE_LABELS[predicted_index]
        
        return {
            'disease': disease,
            'confidence': confidence,
            'label_index': int(predicted_index),
            'all_predictions': {DISEASE_LABELS[i]: round(float(p) * 100, 2) for i, p in enumerate(predictions[0])},
            'model_type': _model_type
        }
    
    except Exception as e:
        raise Exception(f"Prediction failed: {str(e)}")

