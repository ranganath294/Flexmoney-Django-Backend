from rest_framework import serializers
from .models import *

class YogaCoursesSerializer(serializers.ModelSerializer):
    class Meta:
        model = YogaCourses
        fields = '__all__'

class YogaSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = YogaSlot
        fields = '__all__'

class EnrollmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollments
        fields = '__all__'
