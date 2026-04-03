from django.urls import path
from .views import *

urlpatterns = [
    path('basedashboard/',BaseDashBoard,name="basedashboard"),
    path('studentdashboard/',StudentDashBoard,name="studentdashboard"),
    path('teacherdashboard/',TeacherDashBoard,name="teacherdashboard"),

    #features url
    path('viewcourses/',ViewCourses,name='viewcourses'),
    path('viewteachers/',ViewTeachers,name="viewteachers"),
    path('viewstudents/',ViewStudents,name="viewstudents"),
    path('assignmarks/',AssignMarks,name='assignmarks'),
    path('viewmarks/',ViewResults,name='viewmarks'),

    #model
    path('techform/',TechForm,name='techform')
]
