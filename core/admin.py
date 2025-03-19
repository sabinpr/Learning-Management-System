from django.contrib import admin
from .models import User, Course, Enrollment, Assessment, Payment, Sponsorship, Submission, Notification, Videos

# Register your models here.
admin.site.register(User)
admin.site.register(Course)
admin.site.register(Enrollment)
admin.site.register(Assessment)
admin.site.register(Payment)
admin.site.register(Sponsorship)
admin.site.register(Submission)
admin.site.register(Notification)
admin.site.register(Videos)
