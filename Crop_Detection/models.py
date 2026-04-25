from django.db import models

class Feedback(models.Model):
    CATEGORY_USER_EXPERIENCE = "user_experience"
    CATEGORY_DISEASE_INFO_QUALITY = "disease_info_quality"
    CATEGORY_TREATMENT_SUGGESTION = "treatment_suggestion"
    CATEGORY_EASE_OF_USE = "ease_of_use"
    CATEGORY_DESIGN_INTERFACE = "design_interface"
    CATEGORY_SUPPORTED_CROP_VARIETY = "supported_crop_variety"
    CATEGORY_LANGUAGE_SUPPORT = "language_support"
    CATEGORY_RECOMMENDATION_IMPROVEMENT = "recommendation_improvement"

    CATEGORY_CHOICES = [
        (CATEGORY_USER_EXPERIENCE, "User experience"),
        (CATEGORY_DISEASE_INFO_QUALITY, "Disease information quality"),
        (CATEGORY_TREATMENT_SUGGESTION, "Treatment suggestion"),
        (CATEGORY_EASE_OF_USE, "Easy of use"),
        (CATEGORY_DESIGN_INTERFACE, "Design and interface"),
        (CATEGORY_SUPPORTED_CROP_VARIETY, "Supported crop variety"),
        (CATEGORY_LANGUAGE_SUPPORT, "Language support"),
        (CATEGORY_RECOMMENDATION_IMPROVEMENT, "Recommendation & improvement"),
    ]

    name = models.CharField(max_length=120)
    email = models.EmailField(max_length=254)
    rating = models.PositiveSmallIntegerField()
    category = models.CharField(
        max_length=40,
        choices=CATEGORY_CHOICES,
        default=CATEGORY_USER_EXPERIENCE,
    )
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} ({self.rating}/5) - {self.category}"


class ScanHistory(models.Model):
    """Stores every scan result so the history page can display them."""
    original_name = models.CharField(max_length=255)
    image_path = models.CharField(max_length=512)  # relative to MEDIA_ROOT
    disease = models.CharField(max_length=100)
    confidence = models.FloatField()
    # JSON-encoded dict, e.g. {"Healthy": 10.5, "Rust": 77.2, ...}
    all_predictions = models.JSONField(default=dict)
    scanned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-scanned_at"]

    def __str__(self) -> str:
        return f"{self.original_name} → {self.disease} ({self.confidence:.1f}%)"


class ContactMessage(models.Model):
    """Stores every contact form submission."""
    name = models.CharField(max_length=120)
    email = models.EmailField(max_length=254)
    subject = models.CharField(max_length=255)
    message = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-submitted_at"]

    def __str__(self) -> str:
        return f"{self.name} — {self.subject} ({self.submitted_at.strftime('%d %b %Y')})"


