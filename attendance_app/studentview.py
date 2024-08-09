import subprocess,pytz,json
import datetime
from django.db.models import Count
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render
from django.urls import reverse
from django.http import JsonResponse
from django.db import models
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
User=get_user_model()
from attendance_app.models import CustomUser, Staffs, Courses, Subjects, Students, SessionYearModel, Attendance, AttendanceReport

def student_home(request):
    student_obj=Students.objects.get(admin=request.user.id)
    attendance_total=AttendanceReport.objects.filter(student_id=student_obj).count()
    attendance_present=AttendanceReport.objects.filter(student_id=student_obj,status=True).count()
    attendance_absent=AttendanceReport.objects.filter(student_id=student_obj,status=False).count()
    course=Courses.objects.get(id=1)
    subjects=Subjects.objects.filter(course_id=course).count()
    subjects_data=Subjects.objects.filter(course_id=1)
    
    subjects_all=Subjects.objects.all()
    subject_list=[]
    for subject in subjects_all:
        subject_list.append(subject.subject_name)
    for subject in subjects_all:
        subject_list.append(subject.subject_name)
        students_all=student_obj
        attendance_present_list_student=[]
        attendance_absent_list_student=[]
        student_name_list=[]
        attendance=AttendanceReport.objects.filter(student_id=student_obj.id,status="True").count()
        absent=AttendanceReport.objects.filter(student_id=student_obj.id,status="False").count()
        attendance_present_list_student.append(attendance)
        attendance_absent_list_student.append(absent)
        student_name_list.append(student_obj.admin.username)
    return render(request,"student_templates/student_home.html",{"total_attendance":attendance_total,"attendance_absent":attendance_absent,"attendance_present":attendance_present,"subjects":subjects,"student_name_list":student_name_list,"attendance_present_list_student":attendance_present_list_student[0],"attendance_absent_list_student":attendance_absent_list_student[0],"subject_list":subject_list})


def student_view_attendance_post(request):
    subject_id = request.POST.get("subject")
    start_date = request.POST.get("start_date")
    end_date = request.POST.get("end_date")

    start_data_parse = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end_data_parse = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    subject_obj = Subjects.objects.get(id=subject_id)
    user_object = CustomUser.objects.get(id=request.user.id)
    stud_obj = Students.objects.get(admin=user_object)

    attendance = Attendance.objects.filter(attendance_date__range=(start_data_parse, end_data_parse), subject_id=subject_obj)
    attendance_reports = AttendanceReport.objects.filter(attendance_id__in=attendance, student_id=stud_obj)

    total_days=attendance_reports.count()
    present_days = attendance_reports.filter(status=True).count()
    print(attendance_reports)
    print(present_days)
    if (total_days) > 0:
        attendance_percentage = (present_days / total_days) * 100
    else:
        attendance_percentage = 0

    return render(request, "student_templates/student_attendance_data.html", {
        "attendance_reports": attendance_reports,
        "attendance_percentage": attendance_percentage,
        'subject_name':subject_obj.subject_name,
        'start_date':start_data_parse,
        'end_date':end_data_parse,
    })

def student_view_attendance(request):
    student = Students.objects.get(admin=request.user.id) 
    course = student.course_id 
    subjects = Subjects.objects.filter(course_id=course) 
    context = {
        "subjects": subjects
        
    }
    return render(request, "student_templates/student_view_attendance.html", context)