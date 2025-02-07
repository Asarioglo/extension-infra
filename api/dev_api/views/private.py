from django.http import JsonResponse

def private_endpoint(request):
    return JsonResponse({"message": "Private API Response"})
 