from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Courses,Semester
from profile_app.models import Teacher,Student,Marks
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
import os
import pandas as pd
import joblib
from django.conf import settings
import pickle
from django.http import HttpResponse
from django.db.models import Prefetch
from django.contrib import messages

# Create your views here.


ML_FOLDER = os.path.join(settings.BASE_DIR, 'dashboard', 'templates', 'dashboard', 'ml_model')
model_path = os.path.join(ML_FOLDER, 'tech_path_model.pkl')
columns_path = os.path.join(ML_FOLDER, 'train_columns.pkl')



# Load model
model = joblib.load(model_path)

# Load training columns
with open(columns_path, 'rb') as f:
    train_columns = pickle.load(f)


@login_required(login_url='signin')
def BaseDashBoard(request):
    return render(request,"dashboard/basedashboard.html")
    
@login_required(login_url='signin')
def StudentDashBoard(request):
    return render(request,"dashboard/studentdashboard.html")


def TeacherDashBoard(request):
    return render(request,"dashboard/teacherdashboard.html")



def ViewCourses(request):
    courses=Courses.objects.all()
    if request.method=="POST":
        data=request.POST

        semester=data["semester"]

        if semester:
            seme=Semester.objects.filter(semester=semester).first()
            courses=seme.sem.all()
        
    
    paginator=Paginator(courses,5)
    page_number = request.GET.get('page')
    page_obj=paginator.get_page(page_number)
    return render(request,"features/viewcourses.html",{
      
        "page_obj":page_obj
    })


def ViewTeachers(request):

    teachers = Teacher.objects.select_related('user','user__profile_pic')
    return render(request,"features/viewteachers.html",{
        "teachers":teachers
    })



def ViewStudents(request):
    student_name=request.GET.get("q")
    if student_name:
        students=Student.objects.filter(user__username__icontains=student_name)
    else:
    #   students=Student.objects.select_related('user','user__profile_pic')
      students=Student.objects.all()
  
    return render(request,"features/viewstudents.html",{
        "students":students
    })



@login_required
def AssignMarks(request):
    teacher = Teacher.objects.get(user=request.user)

    # Courses assigned to this teacher
    courses = Courses.objects.filter(teacher=teacher)

    selected_course_id = request.GET.get('course')
    students = None
    selected_course = None

    # ---------- GET: Load students + existing marks ----------
    if selected_course_id:
        selected_course = Courses.objects.get(id=selected_course_id)

        # Prefetch existing marks for this course & teacher
        students = Student.objects.filter(
            semester=selected_course.semester
        ).prefetch_related(
            Prefetch(
                'marks_set',
                queryset=Marks.objects.filter(course=selected_course, teacher=teacher),
                to_attr='course_marks'
            )
        )

    # ---------- POST: Insert or Update marks ----------
    if request.method == "POST":
        course_id = request.POST.get('course')
        student_ids = request.POST.getlist('student_id')
        marks_list = request.POST.getlist('marks')

        course = Courses.objects.get(id=course_id)

        for i, student_id in enumerate(student_ids):
            student = Student.objects.get(id=student_id)

            Marks.objects.update_or_create(
                student=student,
                course=course,
                teacher=teacher,
                defaults={
                    'marks': marks_list[i],
                    'semester': student.semester
                }
            )

        # Add success message
        messages.success(request, "Marks assigned / updated successfully!")

        # Redirect to avoid resubmission on refresh
        return redirect(f"{request.path}?course={course_id}")

    return render(request, 'features/assignmarks.html', {
        'courses': courses,
        'students': students,
        'selected_course': selected_course
    })


def TechForm(request):
    prediction = None

    if request.method == 'POST':
        data = request.POST
        user_input = {
            'prefer_design_or_logic': data['prefer_design_or_logic'],
            'like_coding': data['like_coding'],
            'enjoy_math': data['enjoy_math'],
            'like_puzzles': data['like_puzzles'],
            'build_apps_or_websites': data['build_apps_or_websites']
        }

        # Convert to DataFrame
        user_df = pd.DataFrame([user_input])

        # One-hot encode
        user_df = pd.get_dummies(user_df)

        # Add missing columns
        for col in train_columns:
            if col not in user_df.columns:
                user_df[col] = 0

        # Ensure order
        user_df = user_df[train_columns]

        # Predict
        prediction = model.predict(user_df)[0]

    return render(request, "features/techform.html", {"prediction": prediction})


@login_required
def ViewResults(request):
    student = Student.objects.get(user=request.user)
    marks = Marks.objects.filter(student=student)
    courses = Courses.objects.filter(semester=student.semester)

    course_marks_list = []
    completed = 0

    for c in courses:
        m = marks.filter(course=c).first()
        if m:
            course_marks_list.append({'course_name': c.course_name, 'marks': m.marks, 'assigned': True})
            completed += 1
        else:
            course_marks_list.append({'course_name': c.course_name, 'marks': 0, 'assigned': False})

    total = courses.count()
    pending = total - completed
    progress_percent = int((completed / total) * 100) if total > 0 else 0

    return render(request, 'features/viewmarks.html', {
        'student': student,
        'course_marks_list': course_marks_list,
        'total_courses': total,
        'completed_courses': completed,
        'pending_courses': pending,
        'progress_percent': progress_percent,
    })
