from django.urls import path
from .views import Landing

urlpatterns = [
    path("",Landing,name="Landing")
]
