import os
import json
import hashlib
import numpy as np
from PIL import Image
from django.conf import settings
import pickle
import cv2

# Prediction cache: maps image MD5 hash -> prediction dict
_prediction_cache = {}


# Disease labels
DISEASE_LABELS = ['Healthy', 'Powdery Mildew', 'Rust', 'Leaf Spot']

# Cache for the model
_model = None
_model_type = None  # 'keras' or 'mock' or 'real'

def extract_features(img_array):
    """
    Extracts color histograms and basic texture features from a single RGB image.
    img_array: numpy array of shape (224, 224, 3) with values in [0, 1]
    """
    # Convert to uint8 for cv2
    img_uint8 = (img_array * 255).astype(np.uint8)
    
    # Convert to HSV color space which is much better for color segmentation
    hsv = cv2.cvtColor(img_uint8, cv2.COLOR_RGB2HSV)
    
    # Calculate 3D histogram
    hist = cv2.calcHist([hsv], [0, 1, 2], None, [8, 8, 8], [0, 180, 0, 256, 0, 256])
    cv2.normalize(hist, hist)
    hist_features = hist.flatten()
    
    # Also calculate basic color means to capture the dominant color quickly
    mean_color = np.mean(img_uint8, axis=(0, 1)) / 255.0
    std_color = np.std(img_uint8, axis=(0, 1)) / 255.0
    
    # Combine features
    return np.concatenate([hist_features, mean_color, std_color])


class RealDiseaseDetectionModel:
    """
    Real ML model using RandomForest on Color Histograms.
    This class wraps the scikit-learn model so it matches the expected interface.
    """
    def __init__(self, rf_model):
        self.name = "RandomForest Plant Disease Model"
        self.rf_model = rf_model
        self.classes = DISEASE_LABELS
        
    def predict(self, images, verbose=0):
        """
        Make predictions for a batch of images.
        images: Array of shape (batch_size, 224, 224, 3) normalized to [0, 1]
        """
        batch_features = []
        for img in images:
            feats = extract_features(img)
            batch_features.append(feats)
            
        X = np.array(batch_features)
        predictions = self.rf_model.predict_proba(X)
        return predictions



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
                
                # Check if it's our new real model or the old mock model
                if hasattr(_model, 'rf_model'):
                    _model_type = 'real'
                else:
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
    Returns a cached result if this exact image file has been seen before,
    ensuring the same image always produces the same result.
    """
    try:
        # Check if the image is actually a leaf
        if not is_leaf(image_path):
            raise ValueError("The uploaded image does not appear to be a plant leaf. Please upload a clear image of a leaf.")

        # Compute MD5 hash of the image file for stable caching
        hasher = hashlib.md5()
        with open(image_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hasher.update(chunk)
        image_hash = hasher.hexdigest()

        # Return cached prediction for this exact image
        if image_hash in _prediction_cache:
            return _prediction_cache[image_hash]

        # Get model
        model = get_model()

        # Preprocess image
        img_array = preprocess_image(image_path)

        # Make prediction
        predictions = model.predict(img_array, verbose=0)
        predicted_index = int(np.argmax(predictions[0]))
        confidence = round(float(predictions[0][predicted_index]) * 100, 2)

        disease = DISEASE_LABELS[predicted_index]

        result = {
            'disease': disease,
            'confidence': confidence,
            'label_index': predicted_index,
            'all_predictions': {DISEASE_LABELS[i]: round(float(p) * 100, 2) for i, p in enumerate(predictions[0])},
            'model_type': _model_type
        }

        # Cache and return
        _prediction_cache[image_hash] = result
        return result

    except Exception as e:
        raise Exception(f"Prediction failed: {str(e)}")


