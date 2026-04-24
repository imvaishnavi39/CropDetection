# 🚀 Quick Start Guide - CropCare AI

Get up and running in 5 minutes!

## Quick Setup

### 1️⃣ Activate Virtual Environment

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

**⏱️ Usually fast — TensorFlow is optional**

### 3️⃣ Create AI Model

```bash
python create_model.py
```

**Output:**
```
Creating placeholder disease detection model...
✓ Model saved successfully to: model/plant_model.pkl
```

### 4️⃣ Run Server

```bash
python manage.py runserver
```

**Output:**
```
Watching for file changes with StatReloader
Quit the server with CTRL-BREAK.
Django version 6.0.4
Starting development server at http://127.0.0.1:8000/
```

### 5️⃣ Open in Browser

Navigate to: **http://127.0.0.1:8000/**

## 🎯 Test the App

1. **Upload an image** of a plant leaf (JPG, PNG, or GIF)
2. **Click "Analyze Image"**
3. **View predictions** with confidence scores
4. **Click "Try Another Image"** to test again

## 📸 Test Image Tips

For best results with the placeholder model:
- Use clear, well-lit images of plant leaves
- Center the leaf in the frame
- Use JPG, PNG, or GIF format
- Keep file size under 5MB

## ⚙️ Common Commands

| Command | Purpose |
|---------|---------|
| `python manage.py runserver` | Start development server |
| `python manage.py runserver 8001` | Run on different port |
| `python manage.py createsuperuser` | Create admin account |
| `python manage.py shell` | Django interactive shell |
| `python create_model.py` | Generate AI model |

## 📋 Checklist

- [ ] Virtual environment activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Model created (`python create_model.py`)
- [ ] Server running (`python manage.py runserver`)
- [ ] Browser open to http://127.0.0.1:8000/
- [ ] Test image uploaded and analyzed

## 🆘 Having Issues?

### Issue: "ModuleNotFoundError: No module named 'tensorflow'"
**Fix:**
```bash
pip install tensorflow
```

Note: TensorFlow is only needed if you want to use a real Keras `.h5` model. The default placeholder model (`model/plant_model.pkl`) works without TensorFlow.

### Issue: "Model file not found"
**Fix:**
```bash
python create_model.py
```

### Issue: "Address already in use"
**Fix:**
```bash
python manage.py runserver 8001
```

### Issue: "No changes detected in app..."
**Fix:**
```bash
python manage.py makemigrations
python manage.py migrate
```

## 🔐 Admin Panel (Optional)

To access Django admin at http://127.0.0.1:8000/admin/:

```bash
python manage.py createsuperuser
```

Then login with the credentials you create.

## 📂 File Locations

After setup, your folders should contain:

```
✓ media/uploads/        → Uploaded images
✓ model/plant_model.pkl → AI model (placeholder)
✓ db.sqlite3            → Database
```

## 🎓 Next Steps

1. **Learn Django**: https://docs.djangoproject.com/
2. **Train Custom Model**: Replace `plant_model.h5` with your trained model
3. **Deploy to Production**: Use Heroku, AWS, or other platforms
4. **Add Database Models**: Store predictions in database
5. **Build API**: Create REST endpoints for mobile apps

## 📞 Need Help?

1. Check README.md for detailed documentation
2. Review Django error messages carefully
3. Check TensorFlow installation
4. Ensure all directories exist

---

**You're all set! Enjoy detecting crop diseases! 🌾✨**
