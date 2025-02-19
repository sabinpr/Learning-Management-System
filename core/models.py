from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.contrib.auth.models import Group
from django.dispatch import receiver


# Create your models here.
# User model
class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('instructor', 'Instructor'),
        ('student', 'Student'),
        ('sponsor', 'Sponsor'),
    ]

    username = models.CharField(max_length=200, blank=True, default="")
    password = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    # Make email default username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


# Auto asign group based on the role
@receiver(post_save, sender=User)
def assign_user_group(sender, instance, created, **kwargs):
    if created:
        group, _ = Group.objects.get_or_create(name=instance.role)
        instance.groups.add(group)


# Course model for all the available cources
class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    instructor = models.ForeignKey(
        User, on_delete=models.CASCADE, limit_choices_to={'role': 'instructor'})
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# Enrollment of Students in new course
class Enrollment(models.Model):
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    progress = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.student.email} - {self.course.title}"


# Add assessment for students
class Assessment(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateField()

    def __str__(self):
        return self.title


# Submitting of the assigned assesment
class Submission(models.Model):
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    assessment = models.ForeignKey(
        Assessment, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    score = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.email} - {self.assessment.title}"


# Sponsorship for student
class Sponsorship(models.Model):
    sponsor = models.ForeignKey(
        User, on_delete=models.CASCADE, limit_choices_to={'role': 'sponsor'})
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sponsored_student", limit_choices_to={'role': 'student'})
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    funded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sponsor.email} sponsored {self.student.email}"


# Sends Notification to the user
class Notification(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username} - {self.user.email}"


# Payment model for requesting Payment from the sponsor
class Payment(models.Model):
    sponsor = models.ForeignKey(
        User, on_delete=models.CASCADE, limit_choices_to={'role': 'sponsor'})
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=255, unique=True)
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.transaction_id} - {self.status}"
