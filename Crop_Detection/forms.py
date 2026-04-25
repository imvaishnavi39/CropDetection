from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Feedback


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


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ["name", "email", "rating", "category", "message"]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": "Your name",
                    "class": "w-full px-5 py-3.5 rounded-xl border border-white/10 bg-[#06090F]/50 backdrop-blur-sm focus:bg-[#0A0E17] focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all font-medium text-white shadow-inner placeholder-slate-500",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "placeholder": "you@example.com",
                    "class": "w-full px-5 py-3.5 rounded-xl border border-white/10 bg-[#06090F]/50 backdrop-blur-sm focus:bg-[#0A0E17] focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all font-medium text-white shadow-inner placeholder-slate-500",
                }
            ),
            "rating": forms.NumberInput(
                attrs={
                    "min": 1,
                    "max": 5,
                    "placeholder": "1-5",
                    "class": "w-full px-5 py-3.5 rounded-xl border border-white/10 bg-[#06090F]/50 backdrop-blur-sm focus:bg-[#0A0E17] focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all font-medium text-white shadow-inner placeholder-slate-500",
                }
            ),
            "category": forms.Select(
                attrs={
                    "class": "w-full px-5 py-3.5 rounded-xl border border-white/10 bg-[#06090F]/50 backdrop-blur-sm focus:bg-[#0A0E17] focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all font-medium text-white shadow-inner",
                }
            ),
            "message": forms.Textarea(
                attrs={
                    "rows": 5,
                    "placeholder": "Tell us what worked, what didn’t, or what you want next...",
                    "class": "w-full px-5 py-3.5 rounded-xl border border-white/10 bg-[#06090F]/50 backdrop-blur-sm focus:bg-[#0A0E17] focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all font-medium text-white shadow-inner placeholder-slate-500 resize-none",
                }
            ),
        }

    def clean_rating(self):
        rating = self.cleaned_data.get("rating")
        if rating is None:
            raise ValidationError("Please provide a rating from 1 to 5.")
        if rating < 1 or rating > 5:
            raise ValidationError("Rating must be between 1 and 5.")
        return rating


class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "placeholder": "you@example.com",
                "class": "w-full px-5 py-3.5 rounded-xl border border-white/10 bg-[#06090F]/50 backdrop-blur-sm focus:bg-[#0A0E17] focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all font-medium text-white shadow-inner placeholder-slate-500",
            }
        ),
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        widgets = {
            "username": forms.TextInput(
                attrs={
                    "placeholder": "Choose a username",
                    "class": "w-full px-5 py-3.5 rounded-xl border border-white/10 bg-[#06090F]/50 backdrop-blur-sm focus:bg-[#0A0E17] focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all font-medium text-white shadow-inner placeholder-slate-500",
                }
            ),
            "password1": forms.PasswordInput(
                attrs={
                    "placeholder": "Create a strong password",
                    "class": "w-full px-5 py-3.5 rounded-xl border border-white/10 bg-[#06090F]/50 backdrop-blur-sm focus:bg-[#0A0E17] focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all font-medium text-white shadow-inner placeholder-slate-500",
                }
            ),
            "password2": forms.PasswordInput(
                attrs={
                    "placeholder": "Confirm your password",
                    "class": "w-full px-5 py-3.5 rounded-xl border border-white/10 bg-[#06090F]/50 backdrop-blur-sm focus:bg-[#0A0E17] focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all font-medium text-white shadow-inner placeholder-slate-500",
                }
            ),
        }
        help_texts = {
            "username": None,
            "password1": "Your password must be at least 8 characters long, cannot be entirely numeric, and should not be too common.",
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email__iexact=email).exists():
            raise ValidationError("A user with that email address already exists.")
        return email
