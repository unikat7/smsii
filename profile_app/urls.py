from django.urls import path
from .views import *
urlpatterns = [
   path("",ChoiceForRegistration,name="choice"),
   path("tregistration/",TeacherRegistration,name="tregister"),
   path("sregistration/",StudentRegistration,name="sregister"),
   path("signin/",SignIn,name="signin"),
   path("profileupdate/",ProfileUpdate,name="profileupdate"),



   #signout
   path("logout/",Logout,name="logout"),


   #passwordchange
   path("passchange/",ChangePassword,name="passwordchange")


]