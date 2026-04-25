from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.files.storage import default_storage
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import ImageUploadForm, FeedbackForm, SignUpForm
from .model_loader import predict_disease
from .models import ScanHistory, ContactMessage
from .service import get_chat_response_view, initialize_chat_view, clear_chat_memory_view
import os
import json
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt


@login_required(login_url='detection:login')
def index(request):
    """
    Home page view - handles image upload. Requires user to be logged in.
    """
    form = ImageUploadForm()
    
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                # Save the uploaded image
                image_file = request.FILES.get('image')
                
                if not image_file:
                    messages.error(request, 'No image file provided')
                    return render(request, 'index.html', {'form': form})
                
                image_path = default_storage.save(
                    f'uploads/{image_file.name}',
                    image_file
                )
                
                # Store upload info in session (simple approach without database)
                if 'uploads' not in request.session:
                    request.session['uploads'] = []
                
                upload_info = {
                    'id': len(request.session['uploads']) + 1,
                    'image_path': image_path,
                    'original_name': image_file.name,
                }
                
                request.session['uploads'].append(upload_info)
                request.session.modified = True
                
                # Redirect to result page
                return redirect('detection:result', image_id=upload_info['id'])
            
            except Exception as e:
                messages.error(request, f'Error uploading image: {str(e)}')
        else:
            # Display form validation errors
            if form.errors:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, str(error))
    
    context = {
        'form': form,
    }
    
    return render(request, 'index.html', context)


@login_required(login_url='detection:login')
def result(request, image_id):
    """
    Result page view - displays disease prediction. Requires user to be logged in.
    """
    # Get upload info from session
    uploads = request.session.get('uploads', [])
    upload_info = None
    
    for upload in uploads:
        if upload['id'] == image_id:
            upload_info = upload
            break
    
    if not upload_info:
        messages.error(request, 'Image not found. Please upload again.')
        return redirect('detection:index')
    
    try:
        # Get full image path
        media_path = os.path.join(settings.MEDIA_ROOT, upload_info['image_path'])
        
        # Verify file exists
        if not os.path.exists(media_path):
            messages.error(request, 'Image file not found.')
            return redirect('detection:index')
        
        # Make prediction
        prediction = predict_disease(media_path)

        # --- Persist to DB (upsert by image_path so re-scans don't duplicate) ---
        ScanHistory.objects.update_or_create(
            image_path=upload_info['image_path'],
            defaults={
                'original_name': upload_info['original_name'],
                'disease': prediction['disease'],
                'confidence': prediction['confidence'],
                'all_predictions': prediction['all_predictions'],
            }
        )
        
        context = {
            'image_url': f"/media/{upload_info['image_path']}",
            'disease': prediction['disease'],
            'confidence': prediction['confidence'],
            'all_predictions': prediction['all_predictions'],
            'original_name': upload_info['original_name'],
        }
        
        return render(request, 'result.html', context)
    
    except ValueError as ve:
        messages.warning(request, str(ve))
        return redirect('detection:index')
    except Exception as e:
        messages.error(request, f'Error making prediction: {str(e)}')
        return redirect('detection:index')


def about(request):
    """
    About page view - displays information about CropCare AI.
    """
    context = {
        'page_title': 'About Us',
        'page_description': 'Learn about CropCare AI and how we\'re revolutionizing crop disease detection with AI.',
    }
    
    return render(request, 'about.html', context)


def contact(request):
    """
    Contact page view - handles contact form submissions.
    """
    if request.method == 'POST':
        # Get form data
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        
        # Validate fields
        if not all([name, email, subject]):
            messages.error(request, 'Please fill in name, email, and subject.')
            return render(request, 'contact.html')
        
        # Validate email format
        if '@' not in email or '.' not in email:
            messages.error(request, 'Please enter a valid email address.')
            return render(request, 'contact.html')
        
        try:
            # Save message to the database
            ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message,
            )
            messages.success(request, f'Thank you {name}! Your message has been sent successfully. We will get back to you soon.')
            return redirect('detection:contact')
        
        except Exception as e:
            messages.error(request, f'Error sending message: {str(e)}')
    
    context = {
        'page_title': 'Contact Us',
        'page_description': 'Get in touch with the CropCare AI team.',
    }
    
    return render(request, 'contact.html', context)


def feedback(request):
    """
    Feedback page view - stores user feedback in the database.
    """
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback_obj = form.save()
            messages.success(
                request,
                f"Thanks {feedback_obj.name}! Your feedback has been submitted.",
            )
            return redirect("detection:feedback")
        messages.error(request, "Please correct the errors below and resubmit.")
    else:
        form = FeedbackForm()

    return render(
        request,
        "feedback.html",
        {
            "form": form,
            "page_title": "Feedback",
            "page_description": "Help us improve CropCare AI.",
        },
    )


def login_view(request):
    if request.user.is_authenticated:
        return redirect('detection:index')

    form = AuthenticationForm(request=request, data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('detection:index')
        messages.error(request, 'Login failed. Check your username and password.')

    return render(request, 'login.html', {'form': form})


def signup(request):
    if request.user.is_authenticated:
        return redirect('detection:index')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Your account has been created successfully.')
            return redirect('detection:index')
        messages.error(request, 'Please fix the errors below.')
    else:
        form = SignUpForm()

    return render(request, 'signup.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('detection:index')


@require_POST
@csrf_exempt  # For AJAX requests, but keep CSRF protection in frontend
def chatbot_message(request):
    """
    Advanced chatbot endpoint using Gemini API with memory.
    """
    return get_chat_response_view(request)


def chatbot_initialize(request):
    """
    Initialize chatbot session.
    """
    return initialize_chat_view(request)


def chatbot_clear_memory(request):
    """
    Clear chatbot memory.
    """
    return clear_chat_memory_view(request)


@login_required(login_url='detection:login')
def history(request):
    """
    History page – lists all past scans stored in the database.
    Supports clearing all history via a POST request. Requires user to be logged in.
    """
    if request.method == 'POST' and request.POST.get('action') == 'clear':
        ScanHistory.objects.all().delete()
        messages.success(request, 'Scan history cleared successfully.')
        return redirect('detection:history')

    scans = ScanHistory.objects.all()   # already ordered by -scanned_at via Meta
    return render(request, 'history.html', {
        'scans': scans,
        'page_title': 'Scan History',
        'page_description': 'All past plant disease scan results.',
    })

