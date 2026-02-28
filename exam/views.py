from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

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

import openpyxl
from datetime import datetime

from .forms import LoginForm

def invigilator_login(request):

    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)

            if user and Invigilator.objects.filter(user=user).exists():
                login(request, user)
                return redirect('invigilator_dashboard')

            return render(request, 'exam/invigilator_login.html', {
                'form': form,
                'error': "Invalid credentials"
            })

    else:
        form = LoginForm()

    return render(request, 'exam/invigilator_login.html', {'form': form})

def admin_login(request):

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user and user.is_staff:
            login(request, user)
            return redirect('admin_dashboard')

        return render(request, 'exam/admin_login.html', {
            'error': "Invalid Admin Credentials"
        })

    return render(request, 'exam/admin_login.html')

@login_required
def invigilator_dashboard(request):
    invigilator = get_object_or_404(Invigilator, user=request.user)
    halls = invigilator.halls.all()

    return render(request, 'exam/dashboard.html', {
        'halls': halls
    })

@login_required
def takeAttendance(request, hall_id):

    hall = get_object_or_404(Hall, id=hall_id)

    # Restrict invigilator to assigned halls
    if not request.user.is_staff:
        invigilator = get_object_or_404(Invigilator, user=request.user)
        if hall not in invigilator.halls.all():
            return redirect('invigilator_dashboard')

    students_qs = Student.objects.filter(hall=hall)

    existing = Attendance.objects.filter(student__in=students_qs)

    attendance_map = {
        record.student_id: record.status
        for record in existing
    }

    students = []
    for s in students_qs:
        students.append({
            "id": s.id,
            "reg_no": s.reg_no,
            "name": s.name,
            "exam": s.exam.subject,
            "status": attendance_map.get(s.id, "Present")
        })

    if request.method == "POST":
        for s in students_qs:
            status = request.POST.get(s.reg_no, "Present")

            Attendance.objects.update_or_create(
                student=s,
                defaults={'status': status}
            )

        return redirect('success')

    return render(request, 'exam/takeAttendance.html', {
        'students': students,
        'hall': hall
    })

def success(request):
    return render(request, 'exam/success.html')


@staff_member_required
def admin_dashboard(request):

    exams = Exam.objects.all()
    selected_exam_id = request.GET.get("exam")

    records = Attendance.objects.select_related(
        'student',
        'student__exam',
        'student__hall'
    )

    if selected_exam_id:
        records = records.filter(student__exam_id=selected_exam_id)

    return render(request, 'exam/admin_dashboard.html', {
        'records': records,
        'exams': exams,
        'selected_exam_id': selected_exam_id
    })


@staff_member_required
def section_wise_absentees(request, exam_id):

    exam = get_object_or_404(Exam, id=exam_id)

    sections = Section.objects.all()
    section_data = {}

    for section in sections:

        absentees = Attendance.objects.filter(
            student__section=section,
            student__exam=exam,
            status="Absent"
        ).select_related('student', 'student__hall')

        if absentees.exists():
            section_data[section] = [
                record.student for record in absentees
            ]

    return render(request, 'exam/section_absentees.html', {
        'section_data': section_data,
        'exam': exam
    })


@staff_member_required
def export_attendance_excel(request, exam_id):

    records = Attendance.objects.filter(
        student__exam_id=exam_id
    ).select_related('student').order_by('student__reg_no')

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Attendance"

    ws.append([
        "Register No",
        "Student Name",
        "Status"
    ])

    for record in records:
        ws.append([
            record.student.reg_no,
            record.student.name,
            record.status
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = (
        f'attachment; filename=attendance_{exam_id}.xlsx'
    )

    wb.save(response)
    return response

@staff_member_required
def upload_students(request):

    if request.method == "POST":

        file = request.FILES['file']
        wb = openpyxl.load_workbook(file)
        ws = wb.active

        for row in ws.iter_rows(min_row=2, values_only=True):

            if not row or not row[0]:
                continue

            reg_no, name, year_name, branch_name, section_name, hall_name, subject, date, session = row

            if isinstance(date, datetime):
                date = date.date()

            year = Year.objects.get(year_name__iexact=str(year_name).strip())
            branch = Branch.objects.get(branch_name__iexact=str(branch_name).strip())
            section = Section.objects.get(
                section_name__iexact=str(section_name).strip(),
                year=year,
                branch=branch
            )
            hall = Hall.objects.get(hall_no__iexact=str(hall_name).strip())
            exam = Exam.objects.get(
                subject__iexact=str(subject).strip(),
                date=date,
                session__iexact=str(session).strip()
            )

            Student.objects.update_or_create(
                reg_no=str(reg_no).strip(),
                defaults={
                    'name': name,
                    'year': year,
                    'branch': branch,
                    'section': section,
                    'hall': hall,
                    'exam': exam
                }
            )

        return redirect('admin_dashboard')

    return render(request, 'exam/upload.html')

from django.contrib.auth import get_user_model

def create_admin(request):
    User = get_user_model()

    if not User.objects.filter(username="Keerthana").exists():
        User.objects.create_superuser(
            username="Keerthana",
            email="127003181@sastra.ac.in",
            password="keerthana@256"
        )
        return HttpResponse("Admin Created Successfully")

    return HttpResponse("Admin Already Exists")