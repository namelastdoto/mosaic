from django.urls import path, include

urlpatterns = [
    path('examples/', include('api.examples.urls')),
]