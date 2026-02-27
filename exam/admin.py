from django.contrib import admin
from .models import (
    Year,
    Branch,
    Section,
    Hall,
    Exam,
    Student,
    Attendance,
    Invigilator
)

@admin.register(Year)
class YearAdmin(admin.ModelAdmin):
    list_display = ['year_name']
    search_fields = ['year_name']

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['branch_name']
    search_fields = ['branch_name']

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['section_name', 'year', 'branch']
    list_filter = ['year', 'branch']
    search_fields = ['section_name']

@admin.register(Hall)
class HallAdmin(admin.ModelAdmin):
    list_display = ['hall_no']
    search_fields = ['hall_no']

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['subject', 'date', 'session']
    list_filter = ['date', 'session']
    search_fields = ['subject']

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = [
        'reg_no',
        'name',
        'year',
        'branch',
        'section',
        'exam',
        'hall'
    ]

    list_filter = [
        'year',
        'branch',
        'section',
        'exam',
        'hall'
    ]

    search_fields = ['reg_no', 'name']

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = [
        'student',
        'status',
        'timestamp'
    ]

    list_filter = [
        'status',
        'student__exam',
        'student__hall'
    ]

    search_fields = ['student__reg_no', 'student__name']

@admin.register(Invigilator)
class InvigilatorAdmin(admin.ModelAdmin):
    list_display = ['user']
    filter_horizontal = ['halls']