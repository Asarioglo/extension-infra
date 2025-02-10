from django.http import JsonResponse
from django.shortcuts import render

def public_endpoint(request):
    return JsonResponse({"message": "Public API Response"})

def bye(request):
    return render(request, "public/bye.html", {
        "login_url": "/dev_api/api/v1/private/"
    })