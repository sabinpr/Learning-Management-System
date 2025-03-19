from django.http import HttpResponse
from rest_framework import viewsets
from .models import User, Course, Enrollment, Assessment, Submission, Sponsorship, Notification, Payment, Videos
from .serializers import UserSerializer, CourseSerializer, EnrollmentSerializer, AssessmentSerializer, SubmissionSerializer, SponsorshipSerializer, NotificationSerializer, PaymentSerializer, VideoSerializer
from rest_framework import status, permissions
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from .permissions import IsAdmin, IsSponsor, IsInstructorOfCourse, CustomModelPermissions
from django.db import models
from .utils import create_notification
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from dotenv import load_dotenv
import os

load_dotenv()


def index(request):
    return HttpResponse("""<h1>Learning Management System, API</h1><br><h2>Welcome to My API</h2><br><h2>API Urls</h2><br><h3>Admin Pannel - /admin/<br>Documentation - /docs/<br>APIs - /api/<br>LogIn - /login/<br>Register - /register/<br>Admin Dashboard - /admin_dashboard/<br>Sponsor Dashboard - /sponsor_dashboard/</h3><br><br><br><br><br><br><br><h6>Note:Token Authorization is required (a9f152e09a3d58e742f135f90979ea1cedfffa19
)""")


# Course viewset
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    search_fields = ['title', 'difficulty', 'instructor__username']


class VideoViewset(viewsets.ModelViewSet):
    queryset = Videos.objects.all()
    serializer_class = VideoSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsInstructorOfCourse()]
        return [CustomModelPermissions()]

    def perform_create(self, serializer):
        course_id = self.request.data.get("course")
        course = get_object_or_404(Course, id=course_id)

        # Ensure only instructorcan add videos
        if course.instructor != self.request.user:
            return Response({"error": "You are not the instructor of this course"}, status=status.HTTP_403_FORBIDDEN)
        serializer.save(course=course)


# Enrollment viewset


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    filterset_fields = ['progress']


# Assessment viewset
class AssessmentViewSet(viewsets.ModelViewSet):
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer

    def create(self, request):
        # Step 1: Serialize the incoming data and save the Assessment
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Save the assessment and get the object
            assessment_obj = serializer.save()

            # Step 2: Get the students enrolled in the course related to the assessment
            enrollments = Enrollment.objects.filter(
                course=assessment_obj.course)

            # Step 3: Get a list of students by their IDs
            students = User.objects.filter(
                id__in=enrollments.values_list('student_id', flat=True))

            for student in students:
                # Create a notification for each student
                create_notification(
                    student, f'New Assessment: {assessment_obj.title} - {assessment_obj.description}')

            # Step 4: Create a list of student email addresses
            student_email = [
                student.email for student in students if student.email]

            # Step 5: Prepare the email content
            # Email address from your environment settings
            from_email = os.getenv('EMAIL_HOST_USER')
            subject = f'New Assessment: {assessment_obj.title}'
            message = f'''Please submit the assessment before {assessment_obj.due_date}. 
                          More details: {assessment_obj.description}'''

            # Step 6: Send the email to all enrolled students
            try:
                if student_email:  # Ensure there are email addresses before sending
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=from_email,
                        recipient_list=student_email,
                        fail_silently=False
                    )
                    return Response({'result': 'Email sent successfully'}, status=status.HTTP_201_CREATED)
                else:
                    return Response({'result': 'No students have email addresses'}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'result': f'Error sending email: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Submission viewset
class SubmissionViewSet(viewsets.ModelViewSet):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer


# Sponsorship viewset
class SponsorshipViewSet(viewsets.ModelViewSet):
    queryset = Sponsorship.objects.all()
    serializer_class = SponsorshipSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Save the assessment and get the object
            sponsorship_obj = serializer.save()

            sponsor_email = [sponsorship_obj.sponsor.email]

            sponsor = [sponsorship_obj.sponsor.id]

            # Step 5: Prepare the email content
            # Email address from your environment settings
            from_email = os.getenv('EMAIL_HOST_USER')
            subject = f'Sponsorship for : {sponsorship_obj.student.email}'
            message = f'''Thank you for sponsoring {sponsorship_obj.amount}. Funded at {sponsorship_obj.funded_at}'''

            create_notification(
                sponsor, f'New Sponsorship: {sponsorship_obj.amount} - {sponsorship_obj.student.email}')

            # Step 6: Send the email to all enrolled students
            try:
                if sponsor_email:  # Ensure there are email addresses before sending
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=from_email,
                        recipient_list=sponsor_email,
                        fail_silently=False
                    )
                    return Response({'result': 'Email sent successfully'}, status=status.HTTP_201_CREATED)
                else:
                    return Response({'result': 'No email addresses'}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'result': f'Error sending email: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Notification viewset
class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer


    def update(self, request, *args, **kwargs):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'Notification marked as read'}, status=204)


# Payment viewset
class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filterset_fields = ['status']


# Api View for Registering new User


@api_view(['POST'])
@permission_classes([IsAdmin])
def register_api_view(request):
    # Hashing Of Password for Better Security
    # Get PassWord from request - UnHashed
    password = request.data.get('password')
    hash_password = make_password(password)  # Hash pashword Using sHa
    # Make copy of Requested data for Changing Password to Hash Password
    data = request.data.copy()
    data['password'] = hash_password  # Change Password to  hash password
    serializer = UserSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Api View for login User
@api_view(['POST'])
@permission_classes([AllowAny])
def login_api_view(request):

    # get Email And Password From request data and stoore it in variables email and password
    email = request.data.get('email')
    password = request.data.get('password')

    # Check if Request data Matches The Values in Stored Data
    user = authenticate(username=email, password=password)

    # if User is not authenticated then either email or password are invalid
    if user == None:
        return Response({'detail': 'Invalid Credentials!'}, status=status.HTTP_400_BAD_REQUEST)

    # Get Token If The Token of Logged in user is avaiilable Else Create New Token For The User
    token, _ = Token.objects.get_or_create(user=user)

    return Response(token.key)


@api_view(['GET'])
@permission_classes([IsAdmin])
def admin_dashboard_api_view(request):
    total_users = User.objects.count()
    total_cources = Course.objects.count()
    total_enrollments = Enrollment.objects.count()

    return Response({
        "total_Users": total_users,
        "total_cources": total_cources,
        "total_enrollment": total_enrollments
    })


@api_view(['GET'])
@permission_classes([IsSponsor])
def sponsor_dashboard_api_view(request):
    sponsor = request.user
    sponsorships = Sponsorship.objects.filter(sponsor=sponsor)
    total_students_funded = sponsorships.count()

    total_funds = sponsorships.aggregate(
        total_funded=models.Sum('amount'))['total_funded'] or 0
    avg_progress = Enrollment.objects.all().aggregate(
        avg_progress=models.Avg('progress'))['avg_progress'] or 0
    return Response({
        "total_student_funded": total_students_funded,
        "total_funds": total_funds,
        "avg_progress": avg_progress

    })
