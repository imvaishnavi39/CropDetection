# 🌾 CropCare AI - Crop Disease Detection Web Application

A full-stack AI-powered web application for detecting crop diseases using Django, HTML, and Tailwind CSS.

The repo includes a lightweight **placeholder model** (pickle-based) so the app can run **without TensorFlow**. If you have a trained Keras model, you can also plug it in.

## 📋 Features

- **AI-Powered Disease Detection**: Identifies diseases like Powdery Mildew, Rust, Leaf Spot, or reports healthy plants
- **Modern UI**: Built with Tailwind CSS for a responsive, clean interface
- **Image Upload**: Easy drag-and-drop image upload with validation
- **Confidence Scoring**: Shows prediction confidence and all disease probabilities
- **Real-time Predictions**: Instant disease detection using deep learning
- **Error Handling**: Comprehensive validation for uploaded images
- **Session Management**: Track uploaded images during your session

## 🛠️ Tech Stack

- **Backend**: Django 6.0.4 (Python)
- **AI/ML**: NumPy (placeholder model), optional TensorFlow/Keras (real `.h5` model)
- **Frontend**: HTML5, Tailwind CSS (CDN)
- **Database**: SQLite (default)
- **Image Processing**: Pillow, OpenCV

## 📁 Project Structure

```
CropCare AI/
├── manage.py                           # Django management script
├── requirements.txt                    # Python dependencies
├── create_model.py                     # Script to generate placeholder model
├── db.sqlite3                          # SQLite database
├── Crop/                               # Main Django project
│   ├── __init__.py
│   ├── settings.py                     # Project configuration
│   ├── urls.py                         # URL routing
│   ├── asgi.py
│   └── wsgi.py
├── Crop_Detection/                     # Django app for disease detection
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── views.py                        # View functions (home, result)
│   ├── forms.py                        # Image upload form
│   ├── urls.py                         # App URL routing
│   ├── model_loader.py                 # ML model handling
│   ├── tests.py
│   ├── migrations/
│   └── templates/
│       ├── base.html                   # Base template with Tailwind
│       ├── index.html                  # Upload form page
│       └── result.html                 # Prediction results page
├── model/
│   └── plant_model.pkl                 # Placeholder model (no TensorFlow required)
│   └── plant_model.h5                  # Optional: your trained Keras model
├── media/                              # User uploaded images
│   └── uploads/
├── static/                             # Static files (CSS, JS)
└── venv/                               # Virtual environment (created later)
```

## 🚀 Installation & Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Step 1: Create and Activate Virtual Environment

**On Windows (PowerShell or CMD):**
```bash
python -m venv venv
venv\Scripts\Activate.ps1  # For PowerShell
# OR
venv\Scripts\activate     # For CMD
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- Django 6.0.4
- Pillow (image processing)
- NumPy (numerical computing)
- OpenCV (optional, for advanced image processing)

### Step 3: Generate Placeholder Model

Before running the server, create the model file:

```bash
python create_model.py
```

This script will:
- Create a lightweight placeholder model
- Save to `model/plant_model.pkl`

**Note**: This is a placeholder model. Replace it with your actual trained model for production use.

### Step 4: Run Django Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Create Superuser (Optional, for Admin Access)

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account. You can then access Django admin at `/admin/`.

### Step 6: Run Development Server

```bash
python manage.py runserver
```

The application will be available at: **http://127.0.0.1:8000/**

## 📖 Usage

### Upload an Image

1. Go to the home page (http://127.0.0.1:8000/)
2. Click the upload area or drag and drop an image
3. Click "Analyze Image" button
4. Wait for the AI prediction

### View Results

- See your uploaded image
- View the predicted disease name
- Check confidence percentage (0-100%)
- See all disease probabilities
- Get recommendations based on the disease

### Try Another Image

Click "Try Another Image" to return to the upload page and test another image.

## 🔧 Configuration

### settings.py Key Settings

```python
# Media files (uploaded images)
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Templates location
TEMPLATES['DIRS'] = [BASE_DIR / 'Crop_Detection' / 'templates']

# Installed apps
INSTALLED_APPS = [..., 'Crop_Detection']
```

### Model Configuration

Edit `Crop_Detection/model_loader.py` to:
- Change input image size (default: 224x224)
- Modify disease labels
- Adjust confidence threshold

```python
DISEASE_LABELS = ['Healthy', 'Powdery Mildew', 'Rust', 'Leaf Spot']
target_size = (224, 224)
```

## 🤖 AI Model Details

### Model Architecture

The placeholder model uses a CNN (Convolutional Neural Network) with:
- 4 convolutional blocks (32→64→128→256 filters)
- MaxPooling and Dropout layers
- Flatten + Dense layers (512→256→4)
- Softmax activation for 4-class classification

### Input Requirements

- **Image Size**: 224×224 pixels
- **Channels**: RGB (3 channels)
- **Format**: JPG, PNG, GIF
- **Max Size**: 5MB

### Output

The model predicts:
1. **Disease Class**: Healthy, Powdery Mildew, Rust, or Leaf Spot
2. **Confidence**: 0-100% probability
3. **All Predictions**: Probability for each class

## 🔄 Using Your Own Model

To use your trained Keras model:

1. Save your model as `model/plant_model.h5`
2. Update `DISEASE_LABELS` in `model_loader.py` with your class names
3. Ensure input size matches your model (default 224x224)
4. Restart the server

```python
# In Crop_Detection/model_loader.py
DISEASE_LABELS = ['Your', 'Class', 'Labels', 'Here']
```

## ✨ Features Explained

### Image Upload Form (index.html)
- Drag-and-drop support
- File validation (format & size)
- Error messages
- Modern card layout with Tailwind CSS
- Loading feedback

### Result Page (result.html)
- Image preview
- Disease prediction with confidence
- All disease probabilities with progress bars
- AI-powered recommendations
- Disease-specific treatment advice
- "Try Another Image" button

### Backend Logic
- Secure file upload handling
- Image preprocessing (resize, normalize)
- Model prediction pipeline
- Session-based image tracking
- Error handling and logging

## 🛡️ Security Features

- CSRF protection (enabled by default)
- File type validation
- File size limits (5MB max)
- Secure file storage in media folder
- Input validation on all forms

## 🐛 Troubleshooting

### Model File Not Found
```
Error: Model file not found at model/plant_model.h5
```
**Solution**: Run `python create_model.py` to generate the model file.

### Port Already in Use
```
Error: Address already in use
```
**Solution**: Run on a different port:
```bash
python manage.py runserver 8001
```

### TensorFlow Not Found
```
Error: No module named 'tensorflow'
```
**Solution**: Install TensorFlow:
```bash
pip install tensorflow
```

### Image Not Uploading
**Solution**: Check that:
- Image format is JPG, PNG, or GIF
- Image size is less than 5MB
- Image has valid RGB channels

### Predictions Seem Inaccurate
**Note**: The current model is a placeholder. Accuracy will improve with:
- Real training data
- More epochs of training
- Data augmentation
- Hyperparameter tuning

## 📊 Performance Tips

1. **Image Optimization**: Resize images before upload for faster processing
2. **Caching**: Model is cached in memory after first load
3. **Batch Processing**: Can be extended for bulk image analysis
4. **GPU Support**: TensorFlow will use GPU if available (NVIDIA)

## 📚 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Home page with upload form |
| `/` | POST | Upload image and get prediction |
| `/result/<id>/` | GET | View prediction result |

## 🔮 Future Enhancements

- [ ] Database storage for predictions
- [ ] User authentication and accounts
- [ ] Prediction history
- [ ] Batch image upload
- [ ] API endpoint for programmatic access
- [ ] Mobile app
- [ ] Real-time video detection
- [ ] Download report as PDF
- [ ] Email notifications

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

## 📞 Support

For issues and questions:
1. Check the Troubleshooting section
2. Review Django documentation: https://docs.djangoproject.com/
3. Check TensorFlow docs: https://www.tensorflow.org/

## 👨‍💻 Author

Created as a demonstration of AI integration with Django web applications.

---

**Happy Disease Detection! 🌱**
