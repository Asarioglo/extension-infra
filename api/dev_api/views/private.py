from django.http import JsonResponse
import json

def private_endpoint(request):
    userinfo = request.headers.get("x-userinfo")
    access_tkn = request.headers.get("x-access-token")
    return JsonResponse({"message": "Private API Response", "userinfo": userinfo, "access_token": access_tkn})
 