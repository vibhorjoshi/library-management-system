from django.contrib.auth.models import User
from library.models import Profile

# Create student user
if not User.objects.filter(username='student').exists():
    student = User.objects.create_user(username='student', password='password')
    student.first_name = 'John'
    student.last_name = 'Doe'
    student.save()
    student.profile.role = 'student'
    student.profile.save()
    print("✓ Student user created")
else:
    print("✓ Student user already exists")

# Create teacher user
if not User.objects.filter(username='teacher').exists():
    teacher = User.objects.create_user(username='teacher', password='password')
    teacher.first_name = 'Jane'
    teacher.last_name = 'Smith'
    teacher.save()
    teacher.profile.role = 'teacher'
    teacher.profile.save()
    print("✓ Teacher user created")
else:
    print("✓ Teacher user already exists")

# Create staff user
if not User.objects.filter(username='staff').exists():
    staff = User.objects.create_user(username='staff', password='password')
    staff.first_name = 'Mike'
    staff.last_name = 'Wilson'
    staff.save()
    staff.profile.role = 'staff'
    staff.profile.save()
    print("✓ Staff user created")
else:
    print("✓ Staff user already exists")

print("\nAll demo users created successfully!")
print("Demo Credentials:")
print("  Student: student / password")
print("  Teacher: teacher / password")
print("  Staff:   staff / password")
