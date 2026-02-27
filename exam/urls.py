from django.urls import path
from . import views

urlpatterns = [

    path('', views.invigilator_login, name='invigilator_login'),
    path('admin-login/', views.admin_login, name='admin_login'),

    path('invigilator/', views.invigilator_dashboard, name='invigilator_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    path('take-attendance/<int:hall_id>/',
         views.takeAttendance,
         name='takeAttendance'),

    path('success/', views.success, name='success'),

    path('section-absentees/<int:exam_id>/',
         views.section_wise_absentees,
         name='section_absentees'),

    path('export/<int:exam_id>/',
         views.export_attendance_excel,
         name='export_attendance_excel'),

    path('upload/', views.upload_students, name='upload_students'),
]