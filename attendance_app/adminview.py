import json, datetime
from dateutil.relativedelta import relativedelta
from django.db.models import Avg
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from attendance_app.forms import AddStudentForm, EditStudentForm
from attendance_app.models import CustomUser, Staffs, Courses, Subjects, Students, SessionYearModel, Attendance, \
    AttendanceReport, MessageRecord


@login_required(login_url='')
def admin_home(request):
    course_lectures = {}  # Dictionary to store total lectures taken in each course
    course_attendance_percentages = {}  # Dictionary to store average attendance percentage of each course
    attendance_trend_data = {}

    subjects = Subjects.objects.all()

    for subject in subjects:
        subject_obj = Subjects.objects.get(id=subject.id)
        course_id = subject_obj.course_id_id  # Fetch the course ID directly
        students = Students.objects.filter(course_id=course_id)

        total_lectures_taken = Attendance.objects.filter(subject_id=subject).count()

        if course_id in course_lectures:
            course_lectures[course_id] += total_lectures_taken
        else:
            course_lectures[course_id] = total_lectures_taken

        total_present_students = 0
        total_absent_students = 0

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

            total_present_students += present_days
            total_absent_students += absent_days

        if total_present_students + total_absent_students > 0:
            attendance_percentage = min(
                int((total_present_students / (total_present_students + total_absent_students)) * 100), 100)
        else:
            attendance_percentage = 0
        if course_id in course_attendance_percentages:
            course_attendance_percentages[course_id].append(attendance_percentage)
        else:
            course_attendance_percentages[course_id] = [attendance_percentage]

    course_data = []

    for course_id, total_lectures_taken in course_lectures.items():
        course_name = Courses.objects.get(id=course_id).course_name
        attendance_percentages = course_attendance_percentages[course_id]
        non_zero_attendance_percentages = [percentage for percentage in attendance_percentages if percentage != 0]

        if non_zero_attendance_percentages:
            average_attendance_percentage = round(
                sum(non_zero_attendance_percentages) / len(non_zero_attendance_percentages), 2)
        else:
            average_attendance_percentage = 0

        attendance_data = Attendance.objects.values('attendance_date').annotate(
            average_attendance=Avg('attendancereport__status'))
        dates = [entry['attendance_date'] for entry in attendance_data]
        attendance_percentages = [entry['average_attendance'] * 100 for entry in attendance_data]
        attendance_trend_data = {
            'dates': dates,
            'attendance_percentages': attendance_percentages,
        }

        course_data.append({
            'course_name': course_name,
            'total_lectures_taken': total_lectures_taken,
            'average_attendance_percentage': average_attendance_percentage
        })

    context = {
        'course_data': course_data,
        'attendance_trend_data': attendance_trend_data,
    }

    # Rest of your code...

    return render(request, "hod_templates/home_content.html", context)


@login_required(login_url='')
def add_staff(request):
    return render(request, "hod_templates/add_staff.html")


@login_required(login_url='')
def add_staff_save(request):
    if request.method != "POST":
        return HttpResponse("Method Not Allowed")
    else:
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        address = request.POST.get("address")
        try:
            user = CustomUser.objects.create_user(username=username, password=password, email=email,
                                                  last_name=last_name, first_name=first_name, user_type=2)
            user.staffs.address = address
            user.save()
            messages.success(request, "Successfully Added Staff")
            return HttpResponseRedirect(reverse("add_staff"))
        except:
            messages.error(request, "Failed to Add Staff")
            return HttpResponseRedirect(reverse("add_staff"))


@login_required(login_url='')
def add_course(request):
    return render(request, "hod_templates/add_course.html")


@login_required(login_url='')
def add_course_save(request):
    if request.method != "POST":
        return HttpResponse("Method Not Allowed")
    else:
        course = request.POST.get("course")
        try:
            course_model = Courses(course_name=course)
            course_model.save()
            messages.success(request, "Successfully Added Course")
            return HttpResponseRedirect(reverse("add_course"))
        except Exception as e:
            print(e)
            messages.error(request, "Failed To Add Course")
            return HttpResponseRedirect(reverse("add_course"))


@login_required(login_url='')
def add_student(request):
    form = AddStudentForm()
    return render(request, "hod_templates/add_student.html", {"form": form})


@login_required(login_url='')
def add_student_save(request):
    if request.method != "POST":
        return HttpResponse("Method Not Allowed")
    else:
        form = AddStudentForm(request.POST, request.FILES)
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            address = form.cleaned_data["address"]
            session_year_id = form.cleaned_data["session_year_id"]
            course_id = form.cleaned_data["course"]
            sex = form.cleaned_data["sex"]

            try:
                user = CustomUser.objects.create_user(username=username, password=password, email=email,
                                                      last_name=last_name, first_name=first_name, user_type=3)
                user.students.address = address
                course_obj = Courses.objects.get(id=course_id)
                user.students.course_id = course_obj
                session_year = SessionYearModel.objects.get(id=session_year_id)
                user.students.session_year_id = session_year
                user.students.gender = sex
                user.save()
                messages.success(request, "Successfully Added Student")
                return HttpResponseRedirect(reverse("add_student"))
            except:
                messages.error(request, "Failed to Add Student")
                return HttpResponseRedirect(reverse("add_student"))
        else:
            form = AddStudentForm(request.POST)
            return render(request, "hod_templates/add_student.html", {"form": form})


@login_required(login_url='')
def add_subject(request):
    courses = Courses.objects.all()
    staffs = CustomUser.objects.filter(user_type=2)
    return render(request, "hod_templates/add_subject.html", {"staffs": staffs, "courses": courses})


@login_required(login_url='')
def add_subject_save(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        subject_name = request.POST.get("subject_name")
        course_id = request.POST.get("course")
        course = Courses.objects.get(id=course_id)
        staff_id = request.POST.get("staff")
        staff = CustomUser.objects.get(id=staff_id)

        try:
            subject = Subjects(subject_name=subject_name, course_id=course, staff_id=staff)
            subject.save()
            messages.success(request, "Successfully Added Subject")
            return HttpResponseRedirect(reverse("add_subject"))
        except:
            messages.error(request, "Failed to Add Subject")
            return HttpResponseRedirect(reverse("add_subject"))


@login_required(login_url='')
def manage_staff(request):
    staffs = Staffs.objects.all()
    return render(request, "hod_templates/manage_staff.html", {"staffs": staffs})


@login_required(login_url='')
def manage_student(request):
    students = Students.objects.all()
    return render(request, "hod_templates/manage_student.html", {"students": students})


@login_required(login_url='')
def manage_course(request):
    courses = Courses.objects.all()
    return render(request, "hod_templates/manage_course.html", {"courses": courses})


@login_required(login_url='')
def manage_subject(request):
    subjects = Subjects.objects.all()
    return render(request, "hod_templates/manage_subject.html", {"subjects": subjects})


@login_required(login_url='')
def edit_staff(request, staff_id):
    staff = Staffs.objects.get(admin=staff_id)
    return render(request, "hod_templates/edit_staff.html", {"staff": staff, "id": staff_id})


@login_required(login_url='')
def edit_staff_save(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        staff_id = request.POST.get("staff_id")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        username = request.POST.get("username")
        address = request.POST.get("address")

        try:
            user = CustomUser.objects.get(id=staff_id)
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.username = username
            user.save()

            staff_model = Staffs.objects.get(admin=staff_id)
            staff_model.address = address
            staff_model.save()
            messages.success(request, "Successfully Edited Staff")
            return HttpResponseRedirect(reverse("edit_staff", kwargs={"staff_id": staff_id}))
        except:
            messages.error(request, "Failed to Edit Staff")
            return HttpResponseRedirect(reverse("edit_staff", kwargs={"staff_id": staff_id}))


@login_required(login_url='')
def edit_student(request, student_id):
    request.session['student_id'] = student_id
    student = Students.objects.get(admin=student_id)
    form = EditStudentForm()
    form.fields['email'].initial = student.admin.email
    form.fields['first_name'].initial = student.admin.first_name
    form.fields['last_name'].initial = student.admin.last_name
    form.fields['username'].initial = student.admin.username
    form.fields['address'].initial = student.address
    form.fields['course'].initial = student.course_id.id
    form.fields['sex'].initial = student.gender
    form.fields['session_year_id'].initial = student.session_year_id.id
    return render(request, "hod_templates/edit_student.html",
                  {"form": form, "id": student_id, "username": student.admin.username})


@login_required(login_url='')
def edit_student_save(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        student_id = request.session.get("student_id")
        if student_id == None:
            return HttpResponseRedirect(reverse("manage_student"))

        form = EditStudentForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            address = form.cleaned_data["address"]
            session_year_id = form.cleaned_data["session_year_id"]
            course_id = form.cleaned_data["course"]
            sex = form.cleaned_data["sex"]

            try:
                user = CustomUser.objects.get(id=student_id)
                user.first_name = first_name
                user.last_name = last_name
                user.username = username
                user.email = email
                user.save()

                student = Students.objects.get(admin=student_id)
                student.address = address
                session_year = SessionYearModel.objects.get(id=session_year_id)
                student.session_year_id = session_year
                student.gender = sex
                course = Courses.objects.get(id=course_id)
                student.course_id = course
                student.save()
                del request.session['student_id']
                messages.success(request, "Successfully Edited Student")
                return HttpResponseRedirect(reverse("edit_student", kwargs={"student_id": student_id}))
            except:
                messages.error(request, "Failed to Edit Student")
                return HttpResponseRedirect(reverse("edit_student", kwargs={"student_id": student_id}))
        else:
            form = EditStudentForm(request.POST)
            student = Students.objects.get(admin=student_id)
            return render(request, "hod_templates/edit_student.html",
                          {"form": form, "id": student_id, "username": student.admin.username})


@login_required(login_url='')
def edit_subject(request, subject_id):
    subject = Subjects.objects.get(id=subject_id)
    courses = Courses.objects.all()
    staffs = CustomUser.objects.filter(user_type=2)
    return render(request, "hod_templates/edit_subject.html",
                  {"subject": subject, "staffs": staffs, "courses": courses, "id": subject_id})


@login_required(login_url='')
def edit_subject_save(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        subject_id = request.POST.get("subject_id")
        subject_name = request.POST.get("subject_name")
        staff_id = request.POST.get("staff")
        course_id = request.POST.get("course")

        try:
            subject = Subjects.objects.get(id=subject_id)
            subject.subject_name = subject_name
            staff = CustomUser.objects.get(id=staff_id)
            subject.staff_id = staff
            course = Courses.objects.get(id=course_id)
            subject.course_id = course
            subject.save()

            messages.success(request, "Successfully Edited Subject")
            return HttpResponseRedirect(reverse("edit_subject", kwargs={"subject_id": subject_id}))
        except:
            messages.error(request, "Failed to Edit Subject")
            return HttpResponseRedirect(reverse("edit_subject", kwargs={"subject_id": subject_id}))


@login_required(login_url='')
def edit_course(request, course_id):
    course = Courses.objects.get(id=course_id)
    return render(request, "hod_templates/edit_course.html", {"course": course, "id": course_id})


@login_required(login_url='')
def edit_course_save(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        course_id = request.POST.get("course_id")
        course_name = request.POST.get("course")

        try:
            course = Courses.objects.get(id=course_id)
            print(Courses.course_name)
            course.course_name = course_name
            course.save()
            messages.success(request, "Successfully Edited Course")
            return HttpResponseRedirect(reverse("edit_course", kwargs={"course_id": course_id}))
        except:
            messages.error(request, "Failed to Edit Course")
            return HttpResponseRedirect(reverse("edit_course", kwargs={"course_id": course_id}))


@login_required(login_url='')
def manage_session(request):
    session_years = SessionYearModel.objects.all()
    context = {
        "sessions": session_years
    }
    return render(request, "hod_templates/manage_session.html", context)


@login_required(login_url='')
def add_session_save(request):
    if request.method != "POST":
        return HttpResponseRedirect(reverse("manage_session"))
    else:
        session_start_year = request.POST.get("session_start")
        session_end_year = request.POST.get("session_end")

        try:
            sessionyear = SessionYearModel(session_start_year=session_start_year, session_end_year=session_end_year)
            sessionyear.save()
            messages.success(request, "Successfully Added Session")
            return HttpResponseRedirect(reverse("manage_session"))
        except:
            messages.error(request, "Failed to Add Session")
            return HttpResponseRedirect(reverse("manage_session"))


@login_required(login_url='')
def add_session(request):
    return render(request, 'hod_templates/add_session.html')


@csrf_exempt
def check_email_exist(request):
    email = request.POST.get("email")
    user_obj = CustomUser.objects.filter(email=email).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)


@csrf_exempt
def check_username_exist(request):
    username = request.POST.get("username")
    user_obj = CustomUser.objects.filter(username=username).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)


@login_required(login_url='')
def admin_view_attendance(request):
    courses = Courses.objects.all()
    session_year_id = SessionYearModel.objects.all()
    return render(request, "hod_templates/admin_view_attendance.html",
                  {"session_year_id": session_year_id, "courses": courses})


@csrf_exempt
def admin_get_attendance_dates(request):
    subject = request.POST.get("subject")
    session_year_id = request.POST.get("session_year_id")
    subject_obj = Subjects.objects.get(id=subject)
    session_year_obj = SessionYearModel.objects.get(id=session_year_id)
    attendance = Attendance.objects.filter(subject_id=subject_obj, session_year_id=session_year_obj)
    attendance_obj = []
    for attendance_single in attendance:
        data = {"id": attendance_single.id, "attendance_date": str(attendance_single.attendance_date),
                "session_year_id": attendance_single.session_year_id.id}
        attendance_obj.append(data)

    return JsonResponse(json.dumps(attendance_obj), safe=False)


@csrf_exempt
def admin_get_attendance_student(request):
    attendance_date = request.POST.get("attendance_date")
    attendance = Attendance.objects.get(id=attendance_date)

    attendance_data = AttendanceReport.objects.filter(attendance_id=attendance)
    list_data = []

    for student in attendance_data:
        data_small = {"id": student.student_id.admin.id,
                      "name": student.student_id.admin.first_name + " " + student.student_id.admin.last_name,
                      "status": student.status}
        list_data.append(data_small)
    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)


@login_required(login_url='')
def admin_profile(request):
    user = CustomUser.objects.get(id=request.user.id)
    return render(request, "hod_templates/admin_profile.html", {"user": user})


@login_required(login_url='')
def admin_profile_save(request):
    if request.method != "POST":
        return HttpResponseRedirect(reverse("admin_profile"))
    else:
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        password = request.POST.get("password")
        try:
            customuser = CustomUser.objects.get(id=request.user.id)
            customuser.first_name = first_name
            customuser.last_name = last_name
            # if password!=None and password!="":
            #     customuser.set_password(password)
            customuser.save()
            messages.success(request, "Successfully Updated Profile")
            return HttpResponseRedirect(reverse("admin_profile"))
        except:
            messages.error(request, "Failed to Update Profile")
            return HttpResponseRedirect(reverse("admin_profile"))


@login_required(login_url='')
def mark_attendance(request):
    session_years = SessionYearModel.objects.all()
    courses = Courses.objects.all()
    return render(request, "hod_templates/mark_attendance.html", {"session_years": session_years, "courses": courses})


@csrf_exempt
def get_students(request):
    subject_id = request.POST.get("subject")
    session_year = request.POST.get("session_year")

    subject = Subjects.objects.get(id=subject_id)
    session_model = SessionYearModel.objects.get(id=session_year)
    students = Students.objects.filter(course_id=subject.course_id, session_year_id=session_model)
    list_data = []

    for student in students:
        data_small = {"id": student.admin.id, "name": student.admin.first_name + " " + student.admin.last_name,
                      "number": student.roll_number}
        list_data.append(data_small)
    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)


@csrf_exempt
def get_subjects(request):
    course_id = request.POST.get('course')

    if course_id:
        subjects = Subjects.objects.filter(course_id=course_id).values('id', 'subject_name')
        subjects_data = list(subjects)
        return JsonResponse({'subjects': subjects_data})
    else:
        return JsonResponse({})


@csrf_exempt
def save_attendance_data(request):
    student_ids = request.POST.get("student_ids")
    subject_id = request.POST.get("subject_id")
    attendance_date = request.POST.get("attendance_date")
    session_year_id = request.POST.get("session_year_id")

    subject_model = Subjects.objects.get(id=subject_id)
    session_model = SessionYearModel.objects.get(id=session_year_id)
    json_sstudent = json.loads(student_ids)
    # print(data[0]['id'])

    try:
        attendance = Attendance(subject_id=subject_model, attendance_date=attendance_date,
                                session_year_id=session_model)
        attendance.save()

        for stud in json_sstudent:
            student = Students.objects.get(admin=stud['id'])
            attendance_report = AttendanceReport(student_id=student, attendance_id=attendance, status=stud['status'])
            attendance_report.save()
        return HttpResponse("OK")
    except:
        return HttpResponse("ERR")


@login_required(login_url='')
def update_attendance(request):
    courses = Courses.objects.all()
    session_year_id = SessionYearModel.objects.all()
    return render(request, "hod_templates/update_attendance.html",
                  {"session_year_id": session_year_id, "courses": courses})


@csrf_exempt
def get_attendance_dates(request):
    subject = request.POST.get("subject")
    session_year_id = request.POST.get("session_year_id")
    subject_obj = Subjects.objects.get(id=subject)
    session_year_obj = SessionYearModel.objects.get(id=session_year_id)
    attendance = Attendance.objects.filter(subject_id=subject_obj, session_year_id=session_year_obj)
    attendance_obj = []
    for attendance_single in attendance:
        data = {"id": attendance_single.id, "attendance_date": str(attendance_single.attendance_date),
                "session_year_id": attendance_single.session_year_id.id}
        attendance_obj.append(data)

    return JsonResponse(json.dumps(attendance_obj), safe=False)


@csrf_exempt
def get_attendance_student(request):
    attendance_date = request.POST.get("attendance_date")
    attendance = Attendance.objects.get(id=attendance_date)

    attendance_data = AttendanceReport.objects.filter(attendance_id=attendance)
    list_data = []
    print(attendance_data)
    for student in attendance_data:
        data_small = {"id": student.student_id.admin.id,
                      "name": student.student_id.admin.first_name + " " + student.student_id.admin.last_name,
                      "status": student.status}
        list_data.append(data_small)
    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)


@login_required(login_url='')
def delete_attendance_view(request):
    courses = Courses.objects.all()
    session_year_id = SessionYearModel.objects.all()
    return render(request, "hod_templates/delete_attendance.html",
                  {"session_year_id": session_year_id, "courses": courses})


@csrf_exempt
def delete_attendance(request):
    if request.method == 'POST':
        attendance_id = request.POST.get('attendance_date')
        try:
            Attendance.objects.filter(id=attendance_id).delete()
            success = True
        except:
            success = False

        response_data = {
            'success': success
        }
        print(response_data)
        return JsonResponse(response_data)

    # Return an empty response or handle other HTTP methods
    return JsonResponse({})


@csrf_exempt
def save_updateattendance_data(request):
    student_ids = request.POST.get("student_ids")
    attendance_date = request.POST.get("attendance_date")
    attendance = Attendance.objects.get(id=attendance_date)

    json_sstudent = json.loads(student_ids)

    try:
        for stud in json_sstudent:
            student = Students.objects.get(admin=stud['id'])
            attendance_report = AttendanceReport.objects.get(student_id=student, attendance_id=attendance)
            attendance_report.status = stud['status']
            attendance_report.save()
        return HttpResponse("OK")
    except:
        return HttpResponse("ERR")


@login_required(login_url='')
def generate_report(request):
    subjects = Subjects.objects.all()
    courses = Courses.objects.all()

    context = {
        'subjects': subjects,
        'courses': courses,
    }
    return render(request, 'hod_templates/generate_report.html', context)


@login_required(login_url='')
def view_report(request):
    course_id = request.POST.get("course")
    start_date = request.POST.get("start_date")
    end_date = request.POST.get("end_date")

    start_date_parse = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date_parse = datetime.strptime(end_date, "%Y-%m-%d").date()

    course_obj = Courses.objects.get(id=course_id)
    subjects = Subjects.objects.filter(course_id=course_obj)

    students = Students.objects.filter(
        course_id=course_obj,
        session_year_id__session_start_year__lte=start_date_parse,
        session_year_id__session_end_year__gte=end_date_parse
    )

    student_data = []

    for student in students:
        attendance_data = []
        for subject in subjects:
            total_lectures_taken = Attendance.objects.filter(
                attendance_date__range=(start_date_parse, end_date_parse),
                subject_id=subject
            ).count()

            attendance_reports = AttendanceReport.objects.filter(
                attendance_id__in=Attendance.objects.filter(
                    attendance_date__range=(start_date_parse, end_date_parse),
                    subject_id=subject
                ),
                student_id=student
            )
            absent_days = attendance_reports.filter(status=False).count()
            present_days = attendance_reports.filter(status=True).count()

            if total_lectures_taken > 0:
                attendance_percentage = int((present_days / total_lectures_taken) * 100)
            else:
                attendance_percentage = 0
            lectures_present = present_days
            attendance_data.append({
                'subject': subject.subject_name,
                # 'total_lectures_taken': total_lectures_taken,
                'attendance_percentage': attendance_percentage,
                'lectures_present': lectures_present,
            })

        student_data.append({
            'student_id': student.id,
            'student_name': f"{student.admin.first_name} {student.admin.last_name}",
            'number': student.roll_number,
            'attendance_data': attendance_data
        })

    column_names = ['ID', 'Roll_Number', 'Student Name']
    for subject in subjects:
        # column_names.append(f"{subject.subject_name} #")
        column_names.append(f"{subject.subject_name} %")
        column_names.append(f"{subject.subject_name} #P")
    context = {
        'column_names': column_names,
        'student_data': student_data
    }
    return render(request, 'hod_templates/view_report.html', context)


@login_required(login_url='')
def delete_staff(request, staff_id):
    staff = CustomUser.objects.get(id=staff_id)
    try:
        staff.delete()
        messages.success(request, "Staff Deleted Successfully.")
        return HttpResponseRedirect('/manage_staff')
    except:
        messages.error(request, "Failed to Delete Staff.")
        return HttpResponseRedirect('/manage_staff')


@login_required(login_url='')
def delete_student(request, student_id):
    student = CustomUser.objects.get(id=student_id)
    try:
        student.delete()
        messages.success(request, "Student Deleted Successfully.")
        return HttpResponseRedirect('/manage_student')
    except:
        messages.error(request, "Failed to Delete Student.")
        return HttpResponseRedirect('/manage_student')


@login_required(login_url='')
def delete_subject(request, subject_id):
    subject = Subjects.objects.get(id=subject_id)
    try:
        subject.delete()
        messages.success(request, "Subject Deleted Successfully.")
        return HttpResponseRedirect('/manage_subject')
    except:
        messages.error(request, "Failed to Delete Subject.")
        return HttpResponseRedirect('/manage_subject')


@login_required(login_url='')
def delete_session(request, session_id):
    session = SessionYearModel.objects.get(id=session_id)
    try:
        session.delete()
        messages.success(request, "Session Deleted Successfully.")
        return redirect('manage_session')
    except:
        messages.error(request, "Failed to Delete Session.")
        return redirect('manage_session')


@login_required(login_url='')
def delete_course(request, course_id):
    course = Courses.objects.get(id=course_id)
    try:
        course.delete()
        messages.success(request, "Course Deleted Successfully.")
        return redirect('manage_course')
    except:
        messages.error(request, "Failed to Delete Course.")
        return redirect('manage_course')


@login_required(login_url='')
def sms_view_report(request):
    course_id = request.POST.get("course")
    start_date = request.POST.get("start_date")
    end_date = request.POST.get("end_date")

    start_date_parse = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date_parse = datetime.strptime(end_date, "%Y-%m-%d").date()

    course_obj = Courses.objects.get(id=course_id)
    subjects = Subjects.objects.filter(course_id=course_obj)

    students = Students.objects.filter(
        course_id=course_obj,
        session_year_id__session_start_year__lte=start_date_parse,
        session_year_id__session_end_year__gte=end_date_parse
    )

    student_data = []

    for student in students:
        attendance_data = []
        for subject in subjects:
            total_lectures_taken = Attendance.objects.filter(
                attendance_date__range=(start_date_parse, end_date_parse),
                subject_id=subject
            ).count()

            attendance_reports = AttendanceReport.objects.filter(
                attendance_id__in=Attendance.objects.filter(
                    attendance_date__range=(start_date_parse, end_date_parse),
                    subject_id=subject
                ),
                student_id=student
            )
            absent_days = attendance_reports.filter(status=False).count()
            present_days = attendance_reports.filter(status=True).count()

            if total_lectures_taken > 0:
                attendance_percentage = int((present_days / total_lectures_taken) * 100)
            else:
                attendance_percentage = 0
            lectures_present = present_days
            attendance_data.append({
                'subject': subject.subject_name,
                'total_lectures_taken': total_lectures_taken,
                'attendance_percentage': attendance_percentage,
                'lectures_present': lectures_present,
            })

        student_data.append({
            'student_id': student.id,
            'student_name': f"{student.admin.first_name} {student.admin.last_name}",
            'number': student.roll_number,
            'attendance_data': attendance_data,
            'parent': student.parent_number,
        })

    column_names = ['ID', 'Roll_Number', 'Student Name', 'Parent_number', 'Average Percentage']

    for student in student_data:
        total_subjects = len(subjects)
        total_percentage = sum([subject['attendance_percentage'] for subject in student['attendance_data']])

        if total_subjects > 0:
            cumulative_percentage = total_percentage // total_subjects
        else:
            cumulative_percentage = 0

        student['cumulative_percentage'] = cumulative_percentage

    context = {
        'column_names': column_names,
        'student_data': student_data,
        'course_id': course_id,
        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request, 'hod_templates/sms_view_report.html', context)


@login_required(login_url='')
def sms_generate_report(request):
    subjects = Subjects.objects.all()
    courses = Courses.objects.all()

    context = {
        'subjects': subjects,
        'courses': courses,
    }
    return render(request, 'hod_templates/sms_view.html', context)


@csrf_exempt
def recordsms(request):
    course_id = request.POST.get('course_id')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    course_name = Courses.objects.filter(id=course_id)
    try:
        message = MessageRecord(course_name=course_name, start_date=start_date, end_date=end_date)
        message.save()
        return HttpResponse("OK")
    except:
        return HttpResponse("ERR")
