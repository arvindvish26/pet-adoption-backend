from django.db import models

class Contact(models.Model):
    SUBJECT_CHOICES = [
        ('adoption', 'Pet Adoption Inquiry'),
        ('volunteer', 'Volunteer Opportunities'),
        ('donation', 'Donations & Sponsorship'),
        ('lost-pet', 'Lost or Found Pet'),
        ('general', 'General Question'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES)
    message = models.TextField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'
    
    def __str__(self):
        return f"Contact from {self.name} - {self.get_subject_display()}"