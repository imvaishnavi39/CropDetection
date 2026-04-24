from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.files.storage import default_storage
from .forms import ImageUploadForm
from .model_loader import predict_disease
import os
import json
from django.conf import settings


def index(request):
    """
    Home page view - handles image upload.
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


def result(request, image_id):
    """
    Result page view - displays disease prediction.
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
            # In a real application, you would:
            # 1. Send an email to your support team
            # 2. Save the message to database
            # For now, we just show a success message
            
            # Log the message (in production, save to database or send email)
            print(f"\n=== New Contact Message ===")
            print(f"Name: {name}")
            print(f"Email: {email}")
            print(f"Subject: {subject}")
            if message:
                print(f"Message: {message}")
            else:
                print("Message: (empty)")
            print(f"===========================\n")
            
            # Show success message
            messages.success(request, f'Thank you {name}! Your message has been sent successfully. We will get back to you soon.')
            
            # Redirect to avoid form resubmission
            return redirect('detection:contact')
        
        except Exception as e:
            messages.error(request, f'Error sending message: {str(e)}')
    
    context = {
        'page_title': 'Contact Us',
        'page_description': 'Get in touch with the CropCare AI team.',
    }
    
    return render(request, 'contact.html', context)
