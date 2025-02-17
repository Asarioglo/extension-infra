from django.urls import path, include

urlpatterns = [
    path('public/', include('dev_api.urls.public-urls')),
    path('private/', include('dev_api.urls.private-urls')),
]