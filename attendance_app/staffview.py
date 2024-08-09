import subprocess,pytz,json
import datetime
from django.db.models import Count,Q
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render
from django.urls import reverse
from django.http import JsonResponse
from django.db import models
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from attendance_app.models import CustomUser, Staffs, Courses, Subjects, Students, SessionYearModel, Attendance, AttendanceReport

User = get_user_model()

def staff_home(request):   

    subjects = Subjects.objects.filter(staff_id=request.user.id)  
    subject_data = []
    total_lectures_taken_all_subjects = 0
    attendance_percentages = []  # List to store attendance percentages for each subject

    total_lectures_taken_all_subjects = 0
    attendance_percentages = []

    for subject in subjects:
        subject_obj = Subjects.objects.get(id=subject.id)
        students = Students.objects.filter(course_id=subject_obj.course_id)

        total_lectures_taken = Attendance.objects.filter(subject_id=subject).count()
        total_lectures_taken_all_subjects += total_lectures_taken
        total_present_days = 0
        total_absent_days = 0

        for student in students:
            attendance_reports = AttendanceReport.objects.filter(
                attendance_id__in=Attendance.objects.filter(
                    subject_id=subject,
                    session_year_id=student.session_year_id
                ),
                student_id=student
            )
            present_days = attendance_reports.filter(status=True).count()
            absent_days = attendance_reports.filter(status=False).count()
            total_present_days += present_days
            total_absent_days += absent_days

        if total_present_days + total_absent_days > 0:
            attendance_percentage = min(int((total_present_days / (total_present_days + total_absent_days)) * 100), 100)
        else:
            attendance_percentage = 0

        attendance_percentages.append(attendance_percentage)  # Add attendance percentage to the list

    non_zero_attendance_percentages = [percentage for percentage in attendance_percentages if percentage != 0]

    if non_zero_attendance_percentages:
        average_attendance_percentage = round(sum(non_zero_attendance_percentages) / len(non_zero_attendance_percentages), 2)
    else:
        average_attendance_percentage = 0

    print("Attendance Percentages:", attendance_percentages)
    print("Average Attendance Percentage:", average_attendance_percentage)

    subject_list = []
    for subject in subjects:
        subject_list.append(subject.subject_name)
    course_id_list = []
    for subject in subjects:
        course = Courses.objects.get(id=subject.course_id.id)
        course_id_list.append(course.id)
    
    final_course = []
    # Removing Duplicate Course Id
    for course_id in course_id_list:
        if course_id not in final_course:
            final_course.append(course_id)
    
    students_count = Students.objects.filter(course_id__in=final_course).count()
    subject_count = subjects.count()
    context={
        "students_count": students_count,
        "subject_count": subject_count,
        "subject_list": subject_list,
        'average_attendance_percentage': average_attendance_percentage,
        'total_lectures_taken':total_lectures_taken_all_subjects,
        "attendance_percentages": attendance_percentages,
    }
    return render(request,"staff_templates/staff_home.html",context)


def staff_view_attendance(request):
    subjects=Subjects.objects.all()
    session_year_id=SessionYearModel.objects.all()
    return render(request,"staff_templates/staff_view_attendance.html",{"subjects":subjects,"session_year_id":session_year_id})

@csrf_exempt
def staff_get_attendance_dates(request):
    subject=request.POST.get("subject")
    session_year_id=request.POST.get("session_year_id")
    subject_obj=Subjects.objects.get(id=subject)
    session_year_obj=SessionYearModel.objects.get(id=session_year_id)
    attendance=Attendance.objects.filter(subject_id=subject_obj,session_year_id=session_year_obj)
    attendance_obj=[]
    for attendance_single in attendance:
        data={"id":attendance_single.id,"attendance_date":str(attendance_single.attendance_date),"session_year_id":attendance_single.session_year_id.id}
        attendance_obj.append(data)

    return JsonResponse(json.dumps(attendance_obj),safe=False)


@csrf_exempt
def staff_get_attendance_student(request):
    attendance_date=request.POST.get("attendance_date")
    attendance=Attendance.objects.get(id=attendance_date)

    attendance_data=AttendanceReport.objects.filter(attendance_id=attendance)
    list_data=[]

    for student in attendance_data:
        data_small={"id":student.student_id.admin.id,"name":student.student_id.admin.first_name+" "+student.student_id.admin.last_name,"status":student.status}
        list_data.append(data_small)
    return JsonResponse(json.dumps(list_data),content_type="application/json",safe=False)


def staff_update_attendance(request):
    subjects=Subjects.objects.filter(staff_id=request.user.id)
    session_year_id=SessionYearModel.objects.all()
    return render(request,"staff_templates/staff_update_attendance.html",{"subjects":subjects,"session_year_id":session_year_id})

@csrf_exempt
def staff_get_attendance_dates(request):
    subject=request.POST.get("subject")
    session_year_id=request.POST.get("session_year_id")
    subject_obj=Subjects.objects.get(id=subject)
    session_year_obj=SessionYearModel.objects.get(id=session_year_id)
    attendance=Attendance.objects.filter(subject_id=subject_obj,session_year_id=session_year_obj)
    attendance_obj=[]
    for attendance_single in attendance:
        data={"id":attendance_single.id,"attendance_date":str(attendance_single.attendance_date),"session_year_id":attendance_single.session_year_id.id}
        attendance_obj.append(data)

    return JsonResponse(json.dumps(attendance_obj),safe=False)

@csrf_exempt
def staff_get_attendance_student(request):
    attendance_date=request.POST.get("attendance_date")
    attendance=Attendance.objects.get(id=attendance_date)

    attendance_data=AttendanceReport.objects.filter(attendance_id=attendance)
    list_data=[]

    for student in attendance_data:
        data_small={"id":student.student_id.admin.id,"name":student.student_id.admin.first_name+" "+student.student_id.admin.last_name,"status":student.status}
        list_data.append(data_small)
    return JsonResponse(json.dumps(list_data),content_type="application/json",safe=False)

@csrf_exempt
def staff_save_updateattendance_data(request):
    student_ids=request.POST.get("student_ids")
    attendance_date=request.POST.get("attendance_date")
    attendance=Attendance.objects.get(id=attendance_date)

    json_sstudent=json.loads(student_ids)


    try:
        for stud in json_sstudent:
             student=Students.objects.get(admin=stud['id'])
             attendance_report=AttendanceReport.objects.get(student_id=student,attendance_id=attendance)
             attendance_report.status=stud['status']
             attendance_report.save()
        return HttpResponse("OK")
    except:
        return HttpResponse("ERR")

def generate_report(request):
    # course = Courses.objects.get(id=student.course_id.id) # Getting Course Enrolled of LoggedIn Student
    subjects = Subjects.objects.filter(staff_id_id=request.user.id) # Getting the Subjects of Course Enrolled
    context = {
        "subjects": subjects
    }
    return render(request, "staff_templates/generate_report.html", context)

def view_report(request):
    subject_id = request.POST.get("subject")
    start_date = request.POST.get("start_date")
    end_date = request.POST.get("end_date")

    start_data_parse = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end_data_parse = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    subject_obj = Subjects.objects.get(id=subject_id)

    # Get the total lectures taken for the specific subject during the date range
    total_lectures_taken = Attendance.objects.filter(
        attendance_date__range=(start_data_parse, end_data_parse),
        subject_id=subject_obj
    ).count()
    students = Students.objects.filter(
            course_id=subject_obj.course_id,
            session_year_id__session_start_year__lte=start_data_parse,
            session_year_id__session_end_year__gte=end_data_parse
        )
    for student in students:
        attendance_reports = AttendanceReport.objects.filter(
            attendance_id__in=Attendance.objects.filter(
                attendance_date__range=(start_data_parse, end_data_parse),
                subject_id=subject_obj
            ),
            student_id=student
        )
        absent_days = attendance_reports.filter(status=False).count()
        present_days = attendance_reports.filter(status=True).count()

        if total_lectures_taken > 0:
            attendance_percentage = int((present_days / total_lectures_taken) * 100 )
        else:
            attendance_percentage = 0

        student.present_days=present_days
        student.absent_days=absent_days
        student.total_lectures_taken = total_lectures_taken
        student.attendance_percentage = attendance_percentage
        
        context = {
        'students': students,
        'subject_name':subject_obj.subject_name,
        'start_date':start_data_parse,
        'end_date':end_data_parse,
    }
    return render(request, 'staff_templates/report.html', context)