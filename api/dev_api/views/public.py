from django.http import JsonResponse

def public_endpoint(request):
    return JsonResponse({"message": "Public API Response"})
    