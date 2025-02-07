from django.urls import path
from dev_api.views import public

urlpatterns = [
    path('', public.public_endpoint, name='public-endpoint'),
]