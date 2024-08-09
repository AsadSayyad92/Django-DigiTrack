"""ams URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from attendance_app import views
from attendance_app import adminview,staffview,studentview
from django.conf.urls.static import static
from attendance import settings

urlpatterns = [
    path('',views.showLoginPage),
    path('admin/', admin.site.urls),
    path('doLogin',views.doLogin),
    path('get_user_details',views.GetUserDetails),
    path('logout_user/',views.logout_user),
    
    path('admin_home',adminview.admin_home,name="admin_home"),
    path('add_staff',adminview.add_staff,name="add_staff"),
    path('add_staff_save',adminview.add_staff_save,name="add_staff_save"),
    path('add_course/', adminview.add_course,name="add_course"),
    path('add_course_save', adminview.add_course_save,name="add_course_save"),
    path('add_student', adminview.add_student,name="add_student"),
    path('add_student_save', adminview.add_student_save,name="add_student_save"),
    path('add_subject', adminview.add_subject,name="add_subject"),
    path('add_subject_save', adminview.add_subject_save,name="add_subject_save"),
    path('manage_staff', adminview.manage_staff,name="manage_staff"),
    path('manage_student', adminview.manage_student,name="manage_student"),
    path('manage_course', adminview.manage_course,name="manage_course"),
    path('manage_subject', adminview.manage_subject,name="manage_subject"),
    path('edit_staff/<str:staff_id>', adminview.edit_staff,name="edit_staff"),
    path('edit_staff_save', adminview.edit_staff_save,name="edit_staff_save"),
    path('edit_student/<str:student_id>', adminview.edit_student,name="edit_student"),
    path('edit_student_save', adminview.edit_student_save,name="edit_student_save"),
    path('edit_subject/<str:subject_id>', adminview.edit_subject,name="edit_subject"),
    path('edit_subject_save', adminview.edit_subject_save,name="edit_subject_save"),
    path('edit_course/<str:course_id>', adminview.edit_course,name="edit_course"),
    path('edit_course_save', adminview.edit_course_save,name="edit_course_save"),
    path('add_session',adminview.add_session,name="add_session"),
    path('manage_session', adminview.manage_session,name="manage_session"),
    path('add_session_save', adminview.add_session_save,name="add_session_save"),
    path('check_email_exist', adminview.check_email_exist,name="check_email_exist"),
    path('check_username_exist', adminview.check_username_exist,name="check_username_exist"),
    path('admin_view_attendance', adminview.admin_view_attendance,name="admin_view_attendance"),
    path('admin_get_attendance_dates', adminview.admin_get_attendance_dates,name="admin_get_attendance_dates"),
    path('admin_get_attendance_student', adminview.admin_get_attendance_student,name="admin_get_attendance_student"),
    path('admin_profile', adminview.admin_profile,name="admin_profile"),
    path('admin_profile_save', adminview.admin_profile_save,name="admin_profile_save"),
    path('mark_attendance', adminview.mark_attendance, name="mark_attendance"),
    path('update_attendance', adminview.update_attendance, name="update_attendance"),
    path('get_subjects',adminview.get_subjects,name="get_subjects"),
    path('get_students', adminview.get_students, name="get_students"),
    path('get_attendance_dates', adminview.get_attendance_dates, name="get_attendance_dates"),
    path('get_attendance_student', adminview.get_attendance_student, name="get_attendance_student"),
    path('delete_attendance',adminview.delete_attendance,name="delete_attendance"),
    path('delete_attendance_view',adminview.delete_attendance_view,name="delete_attendance_view"),
    path('save_attendance_data', adminview.save_attendance_data, name="save_attendance_data"),
    path('save_updateattendance_data', adminview.save_updateattendance_data, name="save_updateattendance_data"),
    path('admin_generate_report',adminview.generate_report,name="admin_generate_report"),
    path('admin_view_report',adminview.view_report,name="admin_view_report"),
    path('delete_staff/<staff_id>/', adminview.delete_staff, name="delete_staff"),
    path('delete_student/<student_id>/', adminview.delete_student, name="delete_student"),
    path('delete_subject/<subject_id>/', adminview.delete_subject, name="delete_subject"),
    path('delete_course/<course_id>/', adminview.delete_course, name="delete_course"),
    path('delete_session/<session_id>/', adminview.delete_session, name="delete_session"),
    path('sms_generate_report',adminview.sms_generate_report,name="sms_generate_report"),
    path('sms_view_report',adminview.sms_view_report,name="sms_view_report"),
    path('record_sms',adminview.recordsms,name="record_sms"),
    

    path('staff_home', staffview.staff_home, name="staff_home"),
    path('staff_view_attendance', staffview.staff_view_attendance,name="staff_view_attendance"),
    path('staff_get_attendance_dates', staffview.staff_get_attendance_dates,name="staff_get_attendance_dates"),
    path('staff_get_attendance_student', staffview.staff_get_attendance_student,name="staff_get_attendance_student"),
    path('staff_update_attendance', staffview.staff_update_attendance, name="staff_update_attendance"),
    path('staff_get_attendance_dates', staffview.staff_get_attendance_dates, name="staff_get_attendance_dates"),
    path('staff_get_attendance_student', staffview.staff_get_attendance_student, name="staff_get_attendance_student"),
    path('staff_save_updateattendance_data', staffview.staff_save_updateattendance_data, name="staff_save_updateattendance_data"),
    path('staff_generate_report',staffview.generate_report,name="staff_generate_report"),
    path('staff_view_report',staffview.view_report,name="staff_view_report"),

    path('student_home/', studentview.student_home, name="student_home"),
    path('student_view_attendance/', studentview.student_view_attendance, name="student_view_attendance"),
    path('student_view_attendance_post/', studentview.student_view_attendance_post, name="student_view_attendance_post"),

]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)+static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)

