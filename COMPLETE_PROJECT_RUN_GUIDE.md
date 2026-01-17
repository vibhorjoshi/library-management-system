# Complete Project Setup & Run Guide
## Mobile App + Backend Integration

### 🎯 System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                 REACT NATIVE MOBILE APP                     │
│  (Expo - iOS/Android - Module 4)                           │
│  ├─ Login Screen                                            │
│  ├─ Register Screen                                         │
│  ├─ Student/Teacher/Librarian Dashboard                    │
│  ├─ Books List (with search)                               │
│  ├─ Fines Management                                        │
│  └─ Profile Management                                      │
└─────────────────────────────────────────────────────────────┘
                           ↓ API Calls (Axios)
┌─────────────────────────────────────────────────────────────┐
│             DJANGO REST API BACKEND                         │
│  (Module 1-5 - Django 4.2 + DRF)                           │
│  ├─ Authentication (JWT)                                    │
│  ├─ User Management                                         │
│  ├─ Book Management                                         │
│  ├─ Issue/Return Books                                      │
│  ├─ Fine Management                                         │
│  ├─ Analytics Dashboard                                     │
│  └─ Multi-tenant Support (Colleges)                         │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│              DATABASE (SQLite/MySQL)                        │
│  ├─ Users                                                   │
│  ├─ Books                                                   │
│  ├─ Issued Books                                            │
│  ├─ Fines                                                   │
│  ├─ Colleges (Multi-tenant)                                 │
│  └─ Analytics Data                                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Prerequisites Check

Run this first to verify everything is ready:

```bash
# Check Python version
python3 --version
# Expected: Python 3.9+

# Check Node.js
node --version
# Expected: Node.js 18+

# Check npm
npm --version
# Expected: npm 9+

# Check expo
npx expo --version
# Expected: Expo CLI
```

---

## 🚀 Step 1: Start the Django Backend

### 1.1 Open Terminal 1 - Backend Server

```bash
cd /workspaces/library-management-system
```

### 1.2 Verify Database & Migrations

```bash
# Check if database exists and apply any pending migrations
python manage.py migrate
```

**Expected Output:**
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, library, sessions
Running migrations:
  ...
  Applying library.0004_college_alter_book_isbn_alter_book_title_and_more... OK
```

### 1.3 Create Test User Account

```bash
python manage.py shell
```

Then in the Python shell:

```python
from django.contrib.auth.models import User
from library.models import College, Profile

# Create test user
user, created = User.objects.get_or_create(
    username='testuser',
    defaults={
        'email': 'testuser@example.com',
        'first_name': 'Test',
        'last_name': 'User'
    }
)

if created:
    user.set_password('Test@1234')
    user.save()

# Get or create college
college, _ = College.objects.get_or_create(
    code='TEST001',
    defaults={
        'name': 'Test College',
        'location': 'Test Location',
        'admin_email': 'admin@test.edu',
        'subscription_plan': 'pro'
    }
)

# Create profile
profile, created = Profile.objects.get_or_create(
    user=user,
    defaults={
        'college': college,
        'role': 'student'
    }
)

print(f"✅ User created/updated: {user.username}")
print(f"✅ College: {college.name}")
print(f"✅ Role: {profile.role}")
print(f"✅ Password: Test@1234")

exit()
```

### 1.4 Start Django Development Server

```bash
python manage.py runserver 0.0.0.0:8000
```

**Expected Output:**
```
Starting development server at http://0.0.0.0:8000/
Quit the server with CONTROL-C.
```

**✅ Backend is running on:** `http://localhost:8000`

---

## 📱 Step 2: Configure Mobile App API Connection

### 2.1 Open Terminal 2 - Mobile Setup

```bash
cd /workspaces/library-management-system/mobile
```

### 2.2 Check/Update API Configuration

```bash
# View current API configuration
cat src/services/api.js 2>/dev/null || cat components/api.js 2>/dev/null || echo "Finding API config..."
```

### 2.3 Update API URL (if needed)

Look for the API configuration file and ensure it points to your backend:

```javascript
// In mobile app API config file
const API_URL = 'http://10.0.2.2:8000/api'; // Android emulator
// OR
const API_URL = 'http://localhost:8000/api'; // Physical device on same network
// OR
const API_URL = 'http://<YOUR_IP>:8000/api'; // Use your machine's IP
```

**Get your machine's IP:**
```bash
# On Linux/Mac:
ifconfig | grep "inet " | grep -v 127.0.0.1

# On Windows:
ipconfig
```

### 2.4 Install Mobile Dependencies

```bash
npm install
# or
yarn install
```

**Expected Output:**
```
added XXX packages in X.XXs
```

---

## 🎯 Step 3: Start Expo Development Server

### 3.1 Start Expo in Terminal 2

```bash
npx expo start
```

**Expected Output:**
```
┌──────────────────────────────────────────────────────────────┐
│    Expo Go                                                   │
│                                                              │
│ ➜  Tunnel:   Not connected                                 │
│ ➜  LAN:      exp://192.168.x.x:19000                       │
│ ➜  Local:    localhost:19000                                │
│                                                              │
│ Press 'a' for Android, 'i' for iOS, 'w' for web            │
│ Press 'e' to clear bookmarks, 'q' to quit                  │
└──────────────────────────────────────────────────────────────┘
```

---

## 📱 Step 4: Run Mobile App

### Option A: iOS Simulator (macOS only)

```bash
# In Terminal 2 (where expo is running), press: i
```

**Expected:**
- iOS Simulator opens automatically
- App loads
- You see login screen

### Option B: Android Emulator

```bash
# Make sure Android emulator is running first, then:
# In Terminal 2, press: a
```

**Expected:**
- Android emulator loads the app
- You see login screen

### Option C: Physical Device

#### For iPhone:
1. Download "Expo Go" from App Store
2. Open Expo Go
3. Scan QR code from Terminal 2
4. App loads on your device

#### For Android Phone:
1. Download "Expo Go" from Google Play Store
2. Open Expo Go
3. Scan QR code from Terminal 2
4. App loads on your device

---

## 🧪 Step 5: Test the Full Flow

### 5.1 Login Test

**Mobile App Login Screen:**

```
Username: testuser
Password: Test@1234
```

**Expected:**
- ✅ Successful login
- ✅ Redirects to Dashboard
- ✅ Shows student/teacher/librarian role

### 5.2 Test Authentication Flow

**What happens:**

```
Mobile App → POST /api-token-auth/
  {
    "username": "testuser",
    "password": "Test@1234"
  }
         ↓
Backend → Returns JWT token
  {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
         ↓
Mobile App → Stores token (SecureStore)
         ↓
All future requests include:
  Header: "Authorization: Bearer <token>"
```

**Verify in Backend (Terminal 1):**
```
[17/Jan/2026 12:00:00] "POST /api-token-auth/ HTTP/1.1" 200 52
```

### 5.3 Test Dashboard Screen

**Expected data from backend:**
```
GET /api/dashboard/
  ↓
Returns:
  {
    "total_books": 2500,
    "issued_books": 120,
    "pending_fines": 5,
    "fine_amount": 500.00,
    "overdue_books": 3
  }
```

**Mobile App displays:**
- Total books in library
- Your issued books
- Pending fines
- Overdue items

### 5.4 Test Books List

**Expected:**
```
GET /api/books/?college_id=1
  ↓
Returns list of books with:
  - Title
  - Author
  - ISBN
  - Availability
  - Category
```

**Mobile App shows:**
- Searchable list of books
- Filter by category
- Issue book button (if available)

### 5.5 Test Fines Management

**Expected:**
```
GET /api/fines/?status=unpaid
  ↓
Returns:
  {
    "id": 1,
    "amount": 500.00,
    "issued_date": "2026-01-10",
    "status": "unpaid"
  }
```

**Mobile App shows:**
- List of pending fines
- Amount owed
- Due date
- Pay button (Stripe integration)

---

## 🔌 Step 6: Verify API Connection

### 6.1 Check Backend Logs (Terminal 1)

Look for requests from mobile app:

```bash
# You should see logs like:
[17/Jan/2026 12:00:00] "POST /api-token-auth/ HTTP/1.1" 200 52
[17/Jan/2026 12:00:01] "GET /api/dashboard/ HTTP/1.1" 200 245
[17/Jan/2026 12:00:02] "GET /api/books/ HTTP/1.1" 200 1024
[17/Jan/2026 12:00:03] "GET /api/fines/ HTTP/1.1" 200 512
```

### 6.2 Check Mobile Logs (Terminal 2)

In Expo server output, you should see network requests being processed.

### 6.3 Test API Directly (Optional)

From Terminal 3:

```bash
# Get auth token
TOKEN=$(curl -s -X POST http://localhost:8000/api-token-auth/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"Test@1234"}' | jq -r '.token')

echo "Token: $TOKEN"

# Test dashboard endpoint
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/dashboard/

# Test books endpoint
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/books/
```

---

## 📊 Step 7: Test Complete User Journey

### Journey 1: Student Workflow
1. ✅ **Login** → Enter credentials
2. ✅ **View Dashboard** → See summary
3. ✅ **Browse Books** → Search and filter
4. ✅ **Issue Book** → Request to borrow
5. ✅ **View Issued Books** → See borrowed books
6. ✅ **View Fines** → Check pending fines
7. ✅ **Pay Fines** → Use Stripe payment

### Journey 2: Librarian Workflow
1. ✅ **Login** → Librarian account
2. ✅ **View Dashboard** → Library statistics
3. ✅ **Manage Books** → Add/edit books
4. ✅ **Issue Books** → Manually issue to students
5. ✅ **Accept Returns** → Process returns
6. ✅ **Manage Fines** → Create/update fines
7. ✅ **View Analytics** → See library stats

### Journey 3: Teacher Workflow
1. ✅ **Login** → Teacher account
2. ✅ **View Dashboard** → Personal stats
3. ✅ **Browse Books** → Search library
4. ✅ **Issue Book** → Request books
5. ✅ **View Issues** → See my books

---

## 🔧 Troubleshooting

### Mobile can't connect to backend

**Problem:** Blank screen, "Network error", or timeout

**Solutions:**

1. **Check backend is running:**
   ```bash
   curl http://localhost:8000/api/
   # Should not give connection error
   ```

2. **Verify IP address:**
   ```bash
   # Get your machine IP
   hostname -I  # Linux
   ipconfig     # Windows
   ifconfig     # Mac
   
   # Update API_URL in mobile app to use this IP
   ```

3. **Check firewall:**
   ```bash
   # Allow port 8000
   sudo ufw allow 8000  # Linux
   ```

4. **For Android emulator, use:**
   ```javascript
   const API_URL = 'http://10.0.2.2:8000/api';
   ```

### Login fails

**Problem:** "Invalid credentials" or "Network error"

**Check:**
1. User exists in database
2. Password is correct
3. Backend is running
4. Database migrations applied

```bash
# Verify user in Django shell
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.filter(username='testuser').first()
```

### App crashes after login

**Problem:** App closes after successful login

**Check:**
1. Dashboard endpoint exists
2. Database has required data
3. JWT token is valid
4. Serializers are correctly set up

```bash
# Test dashboard endpoint
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/dashboard/
```

### API returns 401 Unauthorized

**Problem:** "Token is invalid" or "Not authenticated"

**Solutions:**
1. Token may have expired (get new token)
2. Token not being sent in header
3. Token format incorrect (should be "Bearer <token>")

---

## 📈 Step 8: Monitor Performance

### Backend Monitoring

**Terminal 1 (Django):**
```bash
# Check response times in logs
# Watch for slow requests (> 100ms)

[17/Jan/2026 12:00:00] "GET /api/books/ HTTP/1.1" 200 1024 (45ms)
[17/Jan/2026 12:00:01] "POST /api/issues/ HTTP/1.1" 201 256 (78ms)
```

### Mobile Performance

**Terminal 2 (Expo):**
- Check for network errors
- Monitor bundle size
- Watch for memory leaks
- Check frame rate (should be 60fps)

### Database Monitoring

```bash
# Check database queries
sqlite3 db.sqlite3
sqlite> SELECT COUNT(*) FROM library_book;
sqlite> SELECT COUNT(*) FROM library_issuedbook;
sqlite> .quit
```

---

## ✅ Full Testing Checklist

- [ ] Backend running on port 8000
- [ ] Database migrated successfully
- [ ] Test user created (testuser / Test@1234)
- [ ] Expo development server started
- [ ] Mobile app loads
- [ ] Login successful
- [ ] Dashboard displays correctly
- [ ] Books list loads
- [ ] Can search books
- [ ] Can view fines
- [ ] Backend logs show requests
- [ ] No network errors in app
- [ ] No crashes on screens

---

## 🎉 You're Ready!

Once all checks pass:

✅ **Full Stack Working:**
- React Native mobile app
- Django REST API backend
- Database (SQLite/MySQL)
- JWT authentication
- Multi-tenant support
- All 5 modules integrated

---

## 💾 Quick Commands Reference

```bash
# Terminal 1 - Backend
cd /workspaces/library-management-system
python manage.py migrate
python manage.py runserver 0.0.0.0:8000

# Terminal 2 - Mobile
cd /workspaces/library-management-system/mobile
npx expo start
# Then press: a (Android), i (iOS), or w (Web)

# Terminal 3 - Testing
# Get token
TOKEN=$(curl -s -X POST http://localhost:8000/api-token-auth/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"Test@1234"}' | jq -r '.token')

# Test endpoints
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/dashboard/
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/books/
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/fines/
```

---

## 📚 Documentation References

- **Backend Setup:** [README.md](README.md)
- **Mobile App:** [mobile/README.md](mobile/README.md)
- **MODULE 4 (Mobile):** [MODULE_4_COMPLETION_SUMMARY.md](MODULE_4_COMPLETION_SUMMARY.md)
- **MODULE 5 (Multi-tenant):** [MODULE_5_README.md](MODULE_5_README.md)

---

**Next Step:** Start Terminal 1 with the backend server! 🚀
