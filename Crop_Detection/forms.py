from django import forms
from django.core.exceptions import ValidationError


class ImageUploadForm(forms.Form):
    """Form for uploading plant leaf images"""
    
    image = forms.ImageField(
        label='Upload Plant Leaf Image',
        required=True,
        widget=forms.FileInput(attrs={
            'id': 'imageInput',
            'accept': 'image/jpeg,image/png,image/gif',
            'style': 'display: none;',
        })
    )
    
    def clean_image(self):
        """Validate image file"""
        image = self.cleaned_data.get('image')
        
        if not image:
            raise ValidationError('Please select an image to upload.')
        
        # Check file size (max 5MB)
        if image.size > 5 * 1024 * 1024:
            raise ValidationError('Image size must be less than 5MB.')
        
        # Check file format
        valid_formats = ['image/jpeg', 'image/png', 'image/gif']
        if image.content_type not in valid_formats:
            raise ValidationError('Please upload a valid image format (JPEG, PNG, or GIF).')
        
        return image
