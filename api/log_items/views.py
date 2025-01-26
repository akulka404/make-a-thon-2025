from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser 
from rest_framework import status
from rest_framework.decorators import api_view
from log_items.models import FOOD_DATA as Tutorial
from log_items.serializers import USERD_Serializer as TutorialSerializer

from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser 
from rest_framework import status
from rest_framework.decorators import api_view

from log_items.models import FOOD_DATA as Tutorial
from log_items.serializers import USERD_Serializer as TutorialSerializer

import datetime
from dateutil.relativedelta import relativedelta  # pip install python-dateutil


@api_view(['GET', 'POST', 'DELETE'])
def user_data(request):
    if request.method == 'GET':
        # your existing GET logic...
        tutorials = Tutorial.objects.all()
        tutorials_serializer = TutorialSerializer(tutorials, many=True)
        return JsonResponse(tutorials_serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)

        # Extract the offset the client wants
        offset_days = data.get("expiry_offset_days", 0)
        offset_hours = data.get("expiry_offset_hours", 0)
        offset_months = data.get("expiry_offset_months", 0)

        # We'll auto-set stored_date and stored_time via the model, so we do NOT
        # set them in 'data'. Django will fill them in upon creation.

        # We'll compute expiry based on "now" + offsets
        # (Alternatively, you could base it on the *exact* stored_date/time after creation,
        #  but that would require a 2-step creation or a custom model.save().)
        now = datetime.datetime.now()

        expired_datetime = now + relativedelta(
            months=offset_months,
            days=offset_days,
            hours=offset_hours
        )

        data["expired_date"] = expired_datetime.date().isoformat()
        data["expired_time"] = expired_datetime.time().replace(microsecond=0).isoformat()

        serializer = TutorialSerializer(data=data)
        if serializer.is_valid():
            serializer.save()  # stored_date/time get auto-added here
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED) 

        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        count = Tutorial.objects.all().delete()
        return JsonResponse(
            {'message': '{} food items were deleted successfully!'.format(count[0])}, 
            status=status.HTTP_204_NO_CONTENT
        )

@api_view(['GET', 'DELETE'])
def user_name(request, name):
    # find user by name
    try:
        tutorial = Tutorial.objects.get(user_name=name)
    except Tutorial.DoesNotExist:
        return JsonResponse({'message': 'The user does not exist'}, status=status.HTTP_404_NOT_FOUND) 

    if request.method == 'GET': 
        tutorial_serializer = TutorialSerializer(tutorial) 
        return JsonResponse(tutorial_serializer.data) 
    elif request.method == 'DELETE': 
        tutorial.delete() 
        return JsonResponse({'message': 'User was deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['PUT'])
def update_user_name(request, name):
    # update user by name
    try:
        tutorial = Tutorial.objects.get(user_name=name)
    except Tutorial.DoesNotExist:
        return JsonResponse({'message': 'The user does not exist'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        tutorial_data = JSONParser().parse(request)
        tutorial_serializer = TutorialSerializer(tutorial, data=tutorial_data)
        if tutorial_serializer.is_valid():
            tutorial_serializer.save()
            return JsonResponse(tutorial_serializer.data)
        return JsonResponse(tutorial_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET', 'PUT'])
def food_data_detail_by_id(request, food_id):
    """
    Fetch or update a FOOD_DATA record by its 'food_id'.
    """
    try:
        # Fetch the food item by ID
        food_obj = Tutorial.objects.get(food_id=food_id)  # 'Tutorial' alias is actually FOOD_DATA
    except Tutorial.DoesNotExist:
        return JsonResponse({'message': 'Food item does not exist'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        # Return the food item details
        serializer = TutorialSerializer(food_obj)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'PUT':
        # Parse the incoming JSON data
        food_data = JSONParser().parse(request)
        # Update the food item
        serializer = TutorialSerializer(food_obj, data=food_data, partial=True)  # partial=True allows partial updates
        if serializer.is_valid():
            serializer.save()  # Save the updates
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def food_data_detail_by_name(request, food_name):
    """Fetch one or more FOOD_DATA records by 'food_name'."""
    food_qs = Tutorial.objects.filter(food_name=food_name)
    
    if not food_qs.exists():
        return JsonResponse(
            {'message': 'No food items found with that name'},
            status=status.HTTP_404_NOT_FOUND
        )

    # If multiple items match, we'll return them all in a list
    serializer = TutorialSerializer(food_qs, many=True)
    return JsonResponse(serializer.data, safe=False)

