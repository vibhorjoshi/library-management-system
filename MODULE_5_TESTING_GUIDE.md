# MODULE 5: Multi-tenant SaaS - Testing Guide

## Quick Start - API Testing

### 1. Obtain JWT Token
```bash
curl -X POST http://localhost:8000/api-token-auth/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass"}'

# Response:
# {"token": "eyJ0eXAiOiJKV1QiLCJhbGc..."}
```

### 2. Test College Endpoints

#### List All Colleges (Admin Only)
```bash
TOKEN="your_token_here"

curl -X GET http://localhost:8000/api/colleges/ \
  -H "Authorization: Bearer $TOKEN"
```

#### Create College (Admin Only)
```bash
curl -X POST http://localhost:8000/api/colleges/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Harvard University",
    "code": "HARVARD001",
    "location": "Cambridge, MA",
    "admin_email": "admin@harvard.edu",
    "subscription_plan": "enterprise"
  }'
```

#### Get College Details
```bash
curl -X GET http://localhost:8000/api/colleges/1/ \
  -H "Authorization: Bearer $TOKEN"
```

#### Get College Statistics
```bash
curl -X GET http://localhost:8000/api/colleges/1/statistics/ \
  -H "Authorization: Bearer $TOKEN"
```

#### Get College Users
```bash
curl -X GET 'http://localhost:8000/api/colleges/1/users/?role=student' \
  -H "Authorization: Bearer $TOKEN"
```

#### Get/Update Billing Info
```bash
# Get billing
curl -X GET http://localhost:8000/api/colleges/1/billing/ \
  -H "Authorization: Bearer $TOKEN"

# Update billing
curl -X PATCH http://localhost:8000/api/colleges/1/billing/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "subscription_plan": "pro",
    "payment_method": "stripe_tok_xxx"
  }'
```

#### Upgrade College Plan
```bash
curl -X POST http://localhost:8000/api/colleges/1/upgrade_plan/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "new_plan": "enterprise",
    "payment_method": "stripe_tok_xxx"
  }'
```

#### Activate/Deactivate College
```bash
# Activate
curl -X POST http://localhost:8000/api/colleges/1/activate/ \
  -H "Authorization: Bearer $TOKEN"

# Deactivate
curl -X POST http://localhost:8000/api/colleges/1/deactivate/ \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Test Analytics Endpoints

#### College Dashboard
```bash
curl -X GET http://localhost:8000/api/college/dashboard/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-College-Code: TEST001"
```

#### Fine Analytics
```bash
curl -X GET http://localhost:8000/api/college/analytics/fines/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-College-Code: TEST001"
```

#### Book Analytics
```bash
curl -X GET http://localhost:8000/api/college/analytics/books/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-College-Code: TEST001"
```

#### User Analytics
```bash
curl -X GET http://localhost:8000/api/college/analytics/users/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-College-Code: TEST001"
```

#### Billing Report
```bash
curl -X GET http://localhost:8000/api/college/billing/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-College-Code: TEST001"
```

---

## Python Testing

### Test Data Isolation
```python
from django.test import TestCase
from library.models import College, Book, IssuedBook, User, Profile
from django.contrib.auth.models import User as DjangoUser
from django.utils import timezone

class TenantIsolationTests(TestCase):
    def setUp(self):
        # Create two colleges
        self.college1 = College.objects.create(
            name="MIT",
            code="MIT001",
            admin_email="admin@mit.edu"
        )
        self.college2 = College.objects.create(
            name="Stanford",
            code="STAN001",
            admin_email="admin@stanford.edu"
        )
        
        # Create books in each college
        self.book1 = Book.objects.create(
            title="Python 101",
            isbn="111111",
            author="Author 1",
            college=self.college1,
            category="Technology"
        )
        
        self.book2 = Book.objects.create(
            title="Java Basics",
            isbn="222222",
            author="Author 2",
            college=self.college2,
            category="Technology"
        )
    
    def test_book_isolation(self):
        """Verify books from one college don't appear in another"""
        # College1 should only see its books
        college1_books = Book.objects.filter(college=self.college1)
        self.assertIn(self.book1, college1_books)
        self.assertNotIn(self.book2, college1_books)
        
        # College2 should only see its books
        college2_books = Book.objects.filter(college=self.college2)
        self.assertIn(self.book2, college2_books)
        self.assertNotIn(self.book1, college2_books)
    
    def test_unique_isbn_per_college(self):
        """Same ISBN can exist in different colleges"""
        # Create same ISBN in different colleges (should work)
        book1 = Book.objects.create(
            title="Book",
            isbn="SAME123",
            author="Author",
            college=self.college1,
            category="Tech"
        )
        
        book2 = Book.objects.create(
            title="Book",
            isbn="SAME123",
            author="Author",
            college=self.college2,
            category="Tech"
        )
        
        self.assertNotEqual(book1.id, book2.id)
        self.assertEqual(book1.isbn, book2.isbn)
    
    def test_issued_book_isolation(self):
        """Issued books are isolated by college"""
        # Create users
        user1 = DjangoUser.objects.create_user(
            username="user1", password="pass"
        )
        user2 = DjangoUser.objects.create_user(
            username="user2", password="pass"
        )
        
        # Create profiles
        profile1 = Profile.objects.create(
            user=user1,
            college=self.college1,
            role="student"
        )
        profile2 = Profile.objects.create(
            user=user2,
            college=self.college2,
            role="student"
        )
        
        # Issue books
        issue1 = IssuedBook.objects.create(
            book=self.book1,
            user=profile1,
            college=self.college1,
            issued_date=timezone.now(),
            due_date=timezone.now()
        )
        
        issue2 = IssuedBook.objects.create(
            book=self.book2,
            user=profile2,
            college=self.college2,
            issued_date=timezone.now(),
            due_date=timezone.now()
        )
        
        # Verify isolation
        college1_issues = IssuedBook.objects.filter(
            college=self.college1
        )
        self.assertIn(issue1, college1_issues)
        self.assertNotIn(issue2, college1_issues)

# Run tests
from django.test.runner import DiscoverRunner
runner = DiscoverRunner(verbosity=2)
runner.run_tests(["library.tests"])
```

### Test Subscription Limits
```python
def test_subscription_limits(self):
    """Verify subscription user limits are enforced"""
    # Create college with 2-user limit
    college = College.objects.create(
        name="Small College",
        code="SMALL001",
        subscription_plan="basic",
        max_users=2
    )
    
    # Create 2 users
    for i in range(2):
        user = DjangoUser.objects.create_user(
            username=f"user{i}",
            password="pass"
        )
        Profile.objects.create(
            user=user,
            college=college,
            role="student"
        )
    
    # Update current_users count
    college.current_users = 2
    college.save()
    
    # Can't add more
    self.assertFalse(college.can_add_user())
    
    # Upgrade plan
    college.subscription_plan = "pro"
    college.max_users = 1000
    college.save()
    
    # Now can add more
    self.assertTrue(college.can_add_user())
```

---

## Manual Testing Checklist

### College Management
- [ ] Create college (POST /api/colleges/)
- [ ] List colleges (GET /api/colleges/)
- [ ] Get college details (GET /api/colleges/{id}/)
- [ ] Update college (PATCH /api/colleges/{id}/)
- [ ] Delete college (DELETE /api/colleges/{id}/)
- [ ] Get college statistics (GET /api/colleges/{id}/statistics/)
- [ ] Get college users (GET /api/colleges/{id}/users/)
- [ ] Activate college (POST /api/colleges/{id}/activate/)
- [ ] Deactivate college (POST /api/colleges/{id}/deactivate/)

### Billing Management
- [ ] Get billing info (GET /api/colleges/{id}/billing/)
- [ ] Update billing (PATCH /api/colleges/{id}/billing/)
- [ ] Upgrade subscription plan (POST /api/colleges/{id}/upgrade_plan/)
- [ ] Verify user limit enforcement
- [ ] Verify plan-specific features

### Analytics
- [ ] College dashboard (GET /api/college/dashboard/)
- [ ] Fine analytics (GET /api/college/analytics/fines/)
- [ ] Book analytics (GET /api/college/analytics/books/)
- [ ] User analytics (GET /api/college/analytics/users/)
- [ ] Billing report (GET /api/college/billing/)

### Data Isolation
- [ ] Users can only see their college data
- [ ] Admins can see all colleges (if superuser)
- [ ] College-specific searches work correctly
- [ ] Cross-college queries return no results
- [ ] Books are unique per college (same ISBN different colleges)

### Permissions
- [ ] Non-authenticated users get 401
- [ ] Authenticated users see their college
- [ ] College admins have elevated permissions
- [ ] Superusers can access any college
- [ ] Regular users can't access other colleges

### Edge Cases
- [ ] College with 0 users
- [ ] College at user limit
- [ ] College with null fields
- [ ] Deactivated college can't accept new users
- [ ] Creating duplicate college code fails
- [ ] Billing with past/future dates works

---

## Performance Testing

### Load Test Endpoints
```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Test college list endpoint (100 requests, 10 concurrent)
ab -n 100 -c 10 -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/colleges/

# Test analytics endpoint
ab -n 100 -c 10 -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/college/dashboard/
```

### Database Query Analysis
```python
from django.db import connection
from django.db.models import Count

# Enable query logging
connection.queries_log.clear()

# Run query
books = Book.objects.filter(college=college).count()

# Check queries
print(f"Number of queries: {len(connection.queries)}")
for query in connection.queries:
    print(query['sql'])
    print(f"Time: {query['time']}s\n")
```

---

## Troubleshooting

### Common Issues

#### "College has no field named..."
**Cause:** Migration not applied
**Solution:** `python manage.py migrate`

#### "FieldDoesNotExist: Fine has no field named 'college'"
**Cause:** Migration operation order issue
**Solution:** Check migration file, ensure AddField operations come before AddIndex

#### "IntegrityError: UNIQUE constraint failed"
**Cause:** Duplicate college code
**Solution:** Use unique colleges or check existing data

#### "User can't see data"
**Cause:** college field is null in Profile
**Solution:** Set college when creating profile

#### "Cross-college data visible"
**Cause:** Query not filtered by college
**Solution:** Always use `.filter(college=request.college)`

---

## Related Files
- [MODULE_5_MULTITENANT_GUIDE.md](MODULE_5_MULTITENANT_GUIDE.md) - Architecture guide
- [library/models.py](library/models.py) - College model and relationships
- [library/tenant_utils.py](library/tenant_utils.py) - Middleware and decorators
- [library/college_views.py](library/college_views.py) - College API views
- [library/college_analytics.py](library/college_analytics.py) - Analytics endpoints
- [library/college_serializers.py](library/college_serializers.py) - Response serializers
