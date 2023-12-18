from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework import viewsets
from accounts.models import *
from accounts.emails import *
from accounts.decorators import *
from .models import *
from .serializers import *


class YogaCoursesViewSet(viewsets.ModelViewSet):
    queryset = YogaCourses.objects.all()
    serializer_class = YogaCoursesSerializer


class YogaSlotViewSet(viewsets.ModelViewSet):
    queryset = YogaSlot.objects.all()
    serializer_class = YogaSlotSerializer


@api_view(['POST'])
@login_required
def enroll(request):
    try:
        if request.method == 'POST':
            data= request.data
            user=request.user
            
            course_id = YogaCourses.objects.filter(id=data["course_id"])
            if course_id:
                course_id=course_id[0]
            else:
                return Response({"msg": "No Course Found With that ID"}, status=status.HTTP_400_BAD_REQUEST)
            
            slot = YogaSlot.objects.filter(id=data["slot_id"])
            if slot:
                slot=slot[0]
            else:
                return Response({"msg": "No Slot Found With that ID"}, status=status.HTTP_400_BAD_REQUEST)
            
            enrollment=Enrollments.objects.create(user=user,course_id=course_id, slot=slot, payment_status="success", validity="valid")
            enrollment.save()
            
            return Response({"msg": "Payment Successful. Course Registered"}, status=status.HTTP_201_CREATED)
                    

    except Exception as e:
        # print(e)
        return Response({"msg": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@login_required
def get_enrolled_courses(request):
    try:
        if request.method == 'GET':
            user=request.user
            
            # Get all enrollments for the user with payment status "success"
            enrollments = Enrollments.objects.filter(user=user, payment_status="success")
            
            # Can optimize this by checking the validity once in a month. 
            
            valid_enrollments = []
            for enrollment in enrollments:
                if enrollment.enrollment_is_valid():
                    valid_enrollments.append(enrollment)
                else:
                    enrollment.validity = 'completed'
                    enrollment.save()
            
            serializer = EnrollmentsSerializer(valid_enrollments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
                    

    except Exception as e:
        # print(e)
        return Response({"msg": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)