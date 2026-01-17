# 📱 MODULE 4: MOBILE APP - IMPLEMENTATION GUIDE

## Quick Start

```bash
cd mobile
npm install
npm run android  # or npm run ios, or npm run web
```

---

## Project Structure

```
mobile/
├── App.js                      # Root app component with AuthProvider
├── app.config.js              # Expo configuration
├── src/
│   ├── api/
│   │   └── client.js          # API client with interceptors
│   ├── screens/
│   │   ├── LoginScreen.js     # Authentication login
│   │   ├── RegisterScreen.js  # User registration
│   │   ├── DashboardScreen.js # Home dashboard with analytics
│   │   ├── BooksScreen.js     # Browse books
│   │   └── FinesScreen.js     # View and pay fines
│   ├── contexts/
│   │   └── AuthContext.js     # Auth state management
│   ├── navigation/
│   │   └── RootNavigator.js   # Navigation stack setup
│   └── utils/
│       └── (storage helpers)
└── package.json
```

---

## Features

### 🔐 Authentication
- **Login Screen**: Email and password authentication
- **Register Screen**: User registration with role selection
- **JWT Tokens**: Secure token storage using Expo SecureStore
- **Auto-refresh**: Automatic token refresh on expiration
- **Persistent Login**: Auto-login on app restart

### 📊 Dashboard
- **Analytics Cards**: Total fines, paid amount, pending amount, overdue books
- **Pending Fines**: List of unpaid fines with quick pay option
- **Quick Actions**: Direct links to books and fines
- **Pull-to-Refresh**: Reload data manually

### 📚 Books Screen
- **Search**: Real-time book search
- **Browse**: Paginated list of books
- **Availability**: Shows number of available copies
- **Details**: Book information with author details

### 💰 Fines Screen
- **Summary**: Total and paid fine amounts
- **Fine List**: All user fines with status
- **Pay Now**: Quick payment button
- **Due Date**: Shows due date for each fine

### 🔄 State Management
- React Context API for global state
- Local AsyncStorage for user data
- Secure token storage

---

## API Integration

### Authentication Endpoints
```javascript
POST /api/auth/login/
{
  "email": "user@example.com",
  "password": "password"
}

POST /api/auth/register/
{
  "email": "user@example.com",
  "password": "password",
  "first_name": "John",
  "last_name": "Doe",
  "user_type": "student"
}
```

### Books Endpoints
```javascript
GET /api/books/?search=query&page=1
GET /api/books/{id}/
POST /api/books/{id}/issue/
```

### Fines Endpoints
```javascript
GET /api/fines/
GET /api/fines/{id}/
POST /api/fines/{id}/pay/
```

### Analytics Endpoints
```javascript
GET /api/analytics/user/
GET /api/analytics/fines/
GET /api/analytics/overdue/
```

---

## Screen Components

### LoginScreen
**Props**: `navigation`
**State**: 
- `email`, `password` (form inputs)
- `loading`, `error` (UI state)

**Features**:
- Email and password validation
- Demo credentials display
- Link to registration
- Loading indicator during request

### RegisterScreen
**Props**: `navigation`
**State**:
- `email`, `password`, `confirmPassword` (form inputs)
- `firstName`, `lastName`, `userType` (user info)
- `loading`, `error` (UI state)

**Features**:
- Form validation
- Password confirmation
- User type selection (Student/Teacher/Staff)
- Link to login

### DashboardScreen
**Props**: `navigation`
**Hooks**: `useEffect`, `useContext`
**Features**:
- Fetch analytics data
- Display summary cards
- Show pending fines
- Refresh functionality
- Logout button

### BooksScreen
**Props**: `navigation`
**State**:
- `books`, `searchQuery`
- `loading`, `refreshing`, `page`, `hasMore`

**Features**:
- Search functionality
- Pagination
- Pull-to-refresh
- Availability badges
- Navigate to book details

### FinesScreen
**Props**: `navigation`
**State**:
- `fines`, `totalAmount`, `paidAmount`
- `loading`, `refreshing`

**Features**:
- Summary cards
- Fine list with status
- Pay button
- Refresh functionality

---

## API Client Features

### Request Interceptor
- Automatically adds JWT token to headers
- Retrieves token from secure storage

### Response Interceptor
- Handles 401 errors
- Attempts token refresh
- Clears auth on refresh failure

### Methods

**Auth API**
```javascript
authAPI.login(email, password)
authAPI.register(email, password, firstName, lastName, userType)
authAPI.logout()
authAPI.getProfile()
```

**Books API**
```javascript
booksAPI.searchBooks(query, page)
booksAPI.getBookDetail(bookId)
booksAPI.issueBook(bookId)
booksAPI.returnBook(issueId)
booksAPI.getUserBooks()
```

**Fines API**
```javascript
fineAPI.getFines()
fineAPI.getFineDetail(fineId)
fineAPI.payFine(fineId)
```

**Payment API**
```javascript
paymentAPI.createPaymentIntent(fineId, amount)
paymentAPI.confirmPayment(paymentId, paymentMethodId)
paymentAPI.getPaymentStatus(paymentId)
paymentAPI.listPayments(page)
```

**Analytics API**
```javascript
analyticsAPI.getUserAnalytics()
analyticsAPI.getFineStatistics()
analyticsAPI.getOverdueBooks()
```

---

## Authentication Context

### State
```javascript
{
  isLoading: boolean,
  isSignout: boolean,
  userToken: string | null,
  user: object | null,
  error: string | null
}
```

### Actions
```javascript
signIn(email, password)           // Login user
signUp(email, password, ...)      // Register user
signOut()                         // Logout user
clearError()                      // Clear error message
updateUser(userData)              // Update user info
```

### Usage
```javascript
const { signIn, signOut, user } = useContext(AuthContext);
```

---

## Styling

### Color Scheme
- Primary: `#3498db` (Blue)
- Dark: `#2c3e50` (Dark Blue)
- Success: `#2ecc71` (Green)
- Error: `#e74c3c` (Red)
- Warning: `#f39c12` (Orange)
- Background: `#f5f5f5` (Light Gray)

### Component Styles
- Cards with rounded corners (borderRadius: 8-12)
- Consistent padding/margin
- Touch highlight on buttons
- Status badges with colors

---

## Dependencies

```json
{
  "expo": "^50.0.0",
  "react": "^18.2.0",
  "react-native": "^0.73.0",
  "axios": "^1.6.0",
  "jwt-decode": "^4.0.0",
  "@react-navigation/native": "^6.1.0",
  "@react-navigation/stack": "^6.3.0",
  "@react-navigation/bottom-tabs": "^6.5.0",
  "@react-native-async-storage/async-storage": "^1.21.0",
  "expo-secure-store": "^13.0.0",
  "react-native-screens": "^3.27.0",
  "react-native-safe-area-context": "^4.8.0",
  "react-native-gesture-handler": "^2.14.0",
  "react-native-reanimated": "^3.6.0"
}
```

---

## Environment Configuration

### app.config.js
```javascript
extra: {
  API_URL: process.env.API_URL || "http://localhost:8000"
}
```

Change `API_URL` based on environment:
- Development: `http://localhost:8000`
- Production: `https://api.yourdomain.com`

---

## Running the App

### Development
```bash
# Expo Go (quickest)
cd mobile
npm start
# Scan QR code with Expo Go app

# Android Emulator
npm run android

# iOS Simulator (Mac only)
npm run ios

# Web Browser
npm run web
```

### Testing API Integration
```bash
# Ensure backend is running
cd ..
python manage.py runserver 0.0.0.0:8000

# In another terminal
cd mobile
npm start
```

### Demo Credentials
```
Email: student@example.com
Password: password123
```

---

## Error Handling

All screens include:
- Try-catch blocks for API calls
- Error alerts to user
- Loading indicators
- Retry capabilities

### Common Errors
- **Network Error**: Check API_URL in app.config.js
- **401 Unauthorized**: Token expired, app will auto-refresh
- **404 Not Found**: Resource doesn't exist
- **500 Server Error**: Backend issue

---

## Future Enhancements

✅ **Phase 1 (Current)**
- Login/Register
- Dashboard with analytics
- Book browsing
- Fine management

📋 **Phase 2 (Planned)**
- Book details screen
- Payment integration (Stripe)
- Book return/issue actions
- Notifications

📋 **Phase 3 (Planned)**
- Offline mode with local data
- Push notifications
- Receipt generation
- Book reviews/ratings

---

## Testing

### Manual Testing Checklist
- [ ] Login with valid credentials
- [ ] Login with invalid credentials
- [ ] Register new user
- [ ] View dashboard
- [ ] Refresh dashboard data
- [ ] Search books
- [ ] Load more books (pagination)
- [ ] View fines
- [ ] Pull-to-refresh fines
- [ ] Logout
- [ ] Auto-login on restart

### API Testing
Use Postman or similar tool to test:
1. Authentication endpoints
2. Books endpoints
3. Fines endpoints
4. Analytics endpoints

---

## Deployment

### Android (APK)
```bash
cd mobile
npm install -g eas-cli
eas build --platform android
```

### iOS (App Store)
```bash
eas build --platform ios
```

### Web
```bash
npm run web
# Builds static site in web-build/
```

---

## Support & Troubleshooting

### Common Issues

**"Cannot connect to API"**
- Check API_URL in app.config.js
- Ensure backend server is running
- Check network connectivity

**"Token invalid"**
- Clear app data and re-login
- Check token expiration
- Verify JWT secret in backend

**"Navigation stack error"**
- Ensure all screens are properly exported
- Check navigation prop passing
- Verify stack/tab navigator setup

---

## Module Status

✅ **MODULE 4: Mobile App - 100% COMPLETE**

**Completed Components:**
- ✅ Expo project setup
- ✅ API client with JWT handling
- ✅ Authentication context
- ✅ Login screen with validation
- ✅ Registration screen
- ✅ Dashboard screen with analytics
- ✅ Books search screen
- ✅ Fines management screen
- ✅ Navigation structure (stack + tabs)
- ✅ Error handling
- ✅ Loading states
- ✅ Pull-to-refresh
- ✅ Token persistence
- ✅ Auto-login on app start

**Ready for:**
- iOS deployment
- Android deployment
- Web deployment
- Payment integration
- Notification system

---

## Next Steps

1. **Test on physical device or emulator**
2. **Configure API_URL for production**
3. **Integrate Stripe payments**
4. **Add push notifications**
5. **Deploy to app stores**

---

**Built with ❤️ using Expo and React Native**

See `.readme_files/MODULE_3_ANALYTICS.md` for backend documentation.
