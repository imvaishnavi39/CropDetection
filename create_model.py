"""
Script to generate a placeholder model for crop disease detection.
Works without TensorFlow - uses pickle-based mock model.

Usage:
    python create_model.py
"""

import os
import sys
import pickle
import numpy as np


class SimpleDiseaseDetectionModel:
    """
    Simple disease detection model using random predictions.
    This is a placeholder that works without TensorFlow.
    Replace with your actual trained model by replacing plant_model.pkl.
    """
    
    def __init__(self):
        self.name = "Simple Plant Disease Detection Model"
        self.classes = ['Healthy', 'Powdery Mildew', 'Rust', 'Leaf Spot']
        self.input_size = (224, 224)
    
    def predict(self, images, verbose=0):
        """
        Make predictions for batch of images.
        
        Args:
            images: Array of shape (batch_size, 224, 224, 3)
            verbose: Verbosity level (for compatibility)
        
        Returns:
            Array of shape (batch_size, num_classes) with probabilities
        """
        batch_size = len(images)
        # Generate random predictions that sum to 1
        # In production, replace this with actual model inference
        predictions = np.random.dirichlet(np.ones(len(self.classes)), batch_size)
        return predictions


def create_placeholder_model():
    """
    Creates and saves a simple placeholder model.
    This model works with Python 3.14+ without TensorFlow.
    """
    
    print("Creating placeholder disease detection model...")
    
    # Create the model
    model = SimpleDiseaseDetectionModel()
    
    print("\nModel Details:")
    print(f"  Name: {model.name}")
    print(f"  Classes: {model.classes}")
    print(f"  Input Size: {model.input_size}")
    print(f"  Num Classes: {len(model.classes)}")
    
    # Save the model
    model_dir = os.path.join(os.path.dirname(__file__), 'model')
    os.makedirs(model_dir, exist_ok=True)
    
    model_path = os.path.join(model_dir, 'plant_model.pkl')
    
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    
    print(f"\n✓ Model saved successfully to: {model_path}")
    print("\nNote: This is a placeholder model using random predictions.")
    print("For production use, train a real model with your crop disease images.")
    print("\nThe model expects input images of size 224x224 with RGB channels.")
    print(f"Output classes: {model.classes}")
    
    # Test the model
    print("\n--- Testing Model ---")
    test_image = np.random.rand(1, 224, 224, 3).astype('float32')
    predictions = model.predict(test_image)
    
    print(f"Test prediction shape: {predictions.shape}")
    print(f"Test predictions: {predictions[0]}")
    predicted_class = np.argmax(predictions[0])
    confidence = predictions[0][predicted_class] * 100
    print(f"Predicted class: {model.classes[predicted_class]} ({confidence:.2f}%)")
    print("\n✓ Model is working correctly!")


if __name__ == '__main__':
    try:
        create_placeholder_model()
    except Exception as e:
        print(f"Error creating model: {str(e)}")
        sys.exit(1)

