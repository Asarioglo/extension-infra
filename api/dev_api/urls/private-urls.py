from django.urls import path
from dev_api.views import private

urlpatterns = [
    path('', private.private_endpoint, name='private-endpoint'),
]