from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from import_export import resources,widgets
from import_export.fields import Field
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.hashers import make_password
from .models import (
    SessionYearModel,
    CustomUser,
    AdminHOD,
    Staffs,
    Courses,
    Subjects,
    Students,
    Attendance,
    AttendanceReport,
    MessageRecord
)

class CustomUserResource(resources.ModelResource):
    password = Field(column_name='password', attribute='password', widget=widgets.CharWidget())
    groups = Field(column_name='groups', attribute='groups', widget=widgets.ManyToManyWidget(Group, field='name'))
    user_permissions = Field(column_name='user_permissions', attribute='user_permissions', widget=widgets.ManyToManyWidget(Permission, field='name'))
    class Meta:
        model = CustomUser
        fields = ('id', 'password', 'last_login', 'is_superuser', 'groups', 'user_permissions',
                  'username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active',
                  'date_joined', 'user_type')

    def save_instance(self, instance, *args, **kwargs):
        password = instance.password
        print(password)
        if password and not password.startswith('pbkdf2_sha256$'):  # Check if the password is new
            instance.password = make_password(password)
        super().save_instance(instance, *args, **kwargs)


@admin.register(SessionYearModel)
class SessionYearModelAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    list_display = ('id', 'session_start_year', 'session_end_year')

@admin.register(CustomUser)
class CustomUserAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    resource_class = CustomUserResource
    list_display = ('id', 'username', 'email', 'user_type')

@admin.register(AdminHOD)
class AdminHODAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    list_display = ('id', 'admin', 'created_at', 'updated_at')

@admin.register(Staffs)
class StaffsAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    list_display = ('id', 'admin', 'address', 'created_at', 'updated_at')

@admin.register(Courses)
class CoursesAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    list_display = ('id', 'course_name', 'created_at', 'updated_at')

@admin.register(Subjects)
class SubjectsAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    list_display = ('id', 'subject_name', 'course_id', 'staff_id', 'created_at', 'updated_at')

@admin.register(Students)
class StudentsAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    list_display = ('id', 'admin', 'gender', 'address', 'course_id', 'session_year_id', 'created_at', 'updated_at')

@admin.register(Attendance)
class AttendanceAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    list_display = ('id', 'subject_id', 'attendance_date', 'created_at', 'session_year_id', 'updated_at')

@admin.register(AttendanceReport)
class AttendanceReportAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    list_display = ('id', 'student_id', 'attendance_id', 'status', 'created_at', 'updated_at')

@admin.register(MessageRecord)
class MessageRecordAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    list_display = ('id', 'course_name', 'created_at', 'updated_at')

