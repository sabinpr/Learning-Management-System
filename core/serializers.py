from rest_framework import serializers
from .models import User, Course, Enrollment, Assessment, Submission, Sponsorship, Notification, Payment, Videos


# User serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role']


# Videos serializer
class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Videos
        fields = '__all__'

# Course serializer


class CourseSerializer(serializers.ModelSerializer):
    instructor = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='instructor'), write_only=True)
    instructor_email = serializers.CharField(
        source='instructor.email', read_only=True)
    videos = VideoSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ["id", "title", "description",
                  "instructor", "difficulty", "created_at", "videos", "instructor_email"]


# Enrollment serializer
class EnrollmentSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='student'), write_only=True)
    course = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), write_only=True)

    # Read-only fields to display student email and course title
    student_email = serializers.CharField(
        source='student.email', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = Enrollment
        fields = '__all__'


# Assessment serializer
class AssessmentSerializer(serializers.ModelSerializer):
    course = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), write_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = Assessment
        fields = '__all__'


# Submission serializer
class SubmissionSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='student'), write_only=True)
    assessment = serializers.PrimaryKeyRelatedField(
        queryset=Assessment.objects.all(), write_only=True)

    # Read-only fields to display student email and assesment title
    student_email = serializers.CharField(
        source='student.email', read_only=True)
    assessment_title = serializers.CharField(
        source='assessment.title', read_only=True)

    class Meta:
        model = Submission
        fields = '__all__'


# Sponsorship serializer
class SponsorshipSerializer(serializers.ModelSerializer):
    sponsor = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='sponsor'), write_only=True)
    sponsor_email = serializers.CharField(
        source='sponsor.email', read_only=True)
    student = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='student'), write_only=True)
    student_email = serializers.CharField(
        source='student.email', read_only=True)

    class Meta:
        model = Sponsorship
        fields = '__all__'


# Notification serializer
class NotificationSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True)
    user_email = serializers.CharField(
        source='user.email', read_only=True)

    class Meta:
        model = Notification
        fields = '__all__'


# Payment serializer
class PaymentSerializer(serializers.ModelSerializer):
    sponsor = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='sponsor'), write_only=True)
    sponsor_email = serializers.CharField(
        source='sponsor.email', read_only=True)

    class Meta:
        model = Payment
        fields = '__all__'
