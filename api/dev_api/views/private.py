from django.http import JsonResponse
import jwt
import json
from django.shortcuts import render
import base64
import os

def private_endpoint(request):
    userinfo = request.headers.get("x-userinfo")
    access_tkn = request.headers.get("x-access-token")
    user_data = parse_b64(userinfo)
    return render(request, "private/private_page.html", {
        "user_token": userinfo, 
        "access_token": access_tkn, 
        "username": user_data.get("username"),
        "email": user_data.get("email"),
        "full_name": f"{user_data.get('given_name')} {user_data.get('family_name')}",
        "access_token_parsed": json.dumps(parse_jwt(access_tkn), indent=4),
        "user_token_parsed": json.dumps(user_data, indent=4),
        "logout_url": os.getenv("DEV_API_KONG_LOGOUT_PATH")
    })

def parse_b64(b64_str):
    try:
        data = base64.urlsafe_b64decode(b64_str)
        return json.loads(data)
    except Exception as e:
        return {"error": str(e)}

def parse_jwt(jwt_str):
    try:
        jwt_data = jwt.decode(jwt_str, options={"verify_signature": False})
        return jwt_data
    except jwt.ExpiredSignatureError:
        return {"error": "Token is expired"}
    except jwt.InvalidTokenError:
        return {"error": "Token is invalid"} 