from django.db import models
from accounts.models import *

class YogaCourses(models.Model):
    course_name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    cost = models.IntegerField()
    course_content = models.TextField(null=True, blank=True)
    instructions = models.TextField(null=True, blank=True)
    instructors = models.TextField(null=True, blank=True)
    languages = models.CharField(max_length=255)
    # reviews, health issues
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.course_name

class YogaSlot(models.Model):
    course = models.ForeignKey(YogaCourses, related_name='slots', on_delete=models.CASCADE)
    time_slot = models.CharField(max_length=50)
    day = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.course.course_name} - {self.time_slot}"
    
class Enrollments(models.Model):
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    )
    
    VALIDITY_CHOICES = (
        ('comlpeted', 'Completed'),
        ('valid', 'Valid'),
        ('invalid', 'Invalid'),
    )
    
    user = models.ForeignKey(MyUser, related_name='enrolled_user', on_delete=models.CASCADE)
    course_id = models.ForeignKey(YogaCourses, related_name='enrolled_course', on_delete=models.CASCADE)
    slot = models.ForeignKey(YogaSlot, related_name='enrolled_slot', on_delete=models.CASCADE)
    payment_status = models.TextField(choices=PAYMENT_STATUS_CHOICES, default='pending')
    validity = models.TextField(choices=VALIDITY_CHOICES, default='invalid')
    enrollment_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user} - {self.course_id} - {self.slot}"
    
    def enrollment_is_valid(self):
        """
        Check if the enrollment is still valid.
        Returns True if the enrollment date and the current date are in the same month, False otherwise.
        """
        current_date = timezone.now()
        return self.enrollment_date.year == current_date.year and self.enrollment_date.month == current_date.month
