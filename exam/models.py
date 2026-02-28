from django.db import models
from django.contrib.auth.models import User


class Year(models.Model):
    year_name = models.CharField(max_length=20)

    def __str__(self):
        return self.year_name

class Branch(models.Model):
    branch_name = models.CharField(max_length=50)

    def __str__(self):
        return self.branch_name

class Section(models.Model):
    section_name = models.CharField(max_length=10)
    year = models.ForeignKey(Year, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.year} - {self.branch} - {self.section_name}"

class Exam(models.Model):

    SESSION_CHOICES = [
        ('Session 1', 'Session 1'),
        ('Session 2', 'Session 2'),
	('Session 3', 'Session 3'),
	('Session 4', 'Session 4')
    ]

    subject = models.CharField(max_length=100)
    date = models.DateField()
    session = models.CharField(
        max_length=20,
        choices=SESSION_CHOICES,
        default='Session 1'
    )

    start_time = models.TimeField(null=True, blank=True)
    def __str__(self):
        return f"{self.subject} - {self.date} - {self.session}"



class Hall(models.Model):
    hall_no = models.CharField(max_length=20)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)

    def __str__(self):
        return self.hall_no


class Student(models.Model):
    reg_no = models.CharField(max_length=20)
    name = models.CharField(max_length=100)

    year = models.ForeignKey(Year, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE)

    class Meta:
        ordering = ['reg_no']

    def __str__(self):
        return f"{self.reg_no} - {self.name}"


class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=10,
        choices=[('Present', 'Present'), ('Absent', 'Absent')]
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['student__reg_no']

    def __str__(self):
        return f"{self.student.reg_no} - {self.status}"

class Invigilator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    halls = models.ManyToManyField(Hall)

    def __str__(self):
        return self.user.username
