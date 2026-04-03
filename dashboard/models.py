from django.db import models

# Create your models here.

class Semester(models.Model):
    semester=models.IntegerField()

    def __str__(self):
        return str(self.semester)

class Courses(models.Model):
    teacher = models.ForeignKey("profile_app.Teacher", on_delete=models.CASCADE, related_name='courses', null=True,blank=True)
    course_name = models.CharField(max_length=200)
    course_code = models.CharField(max_length=10)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='sem')
    
    def __str__(self):
        return self.course_name










    