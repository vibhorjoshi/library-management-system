# React Frontend Starter Files

This directory contains starter component files for the React frontend of the Library Management System.

## Files Included

### 1. `src_services_api.js`
API service layer with axios integration
- Authentication endpoints
- Dashboard endpoints
- Book management endpoints
- User profile endpoints
- Automatic token refresh

**Usage:**
```javascript
import { authAPI, dashboardAPI, bookAPI } from '../services/api';
```

### 2. `src_components_Login.js`
Login component with:
- Username/password form
- JWT token handling
- Error handling
- Loading states

**Usage:**
```javascript
import Login from '../components/Login';
```

### 3. `src_components_StudentDashboard.js`
Student dashboard showing:
- Issued books count
- Reservations count
- Pending fines
- Dashboard data

**Usage:**
```javascript
import StudentDashboard from '../components/StudentDashboard';
```

### 4. `src_components_ProtectedRoute.js`
Protected route wrapper ensuring:
- Only authenticated users can access
- Automatic redirection to login if needed

**Usage:**
```javascript
<ProtectedRoute
  component={YourComponent}
  isAuthenticated={isAuthenticated}
/>
```

### 5. `src_App.js`
Main App component with:
- React Router setup
- Route definitions
- Authentication state management
- Protected routes

### 6. `src_App.css`
CSS styling with:
- Bootstrap enhancement
- Custom color variables
- Responsive design
- Component-specific styles

## How to Use These Files

### Step 1: Create React App
```bash
npx create-react-app frontend
cd frontend
```

### Step 2: Install Dependencies
```bash
npm install axios react-router-dom bootstrap
```

### Step 3: Copy Files
1. Copy `src_services_api.js` → `src/services/api.js`
2. Copy `src_components_Login.js` → `src/components/Login.js`
3. Copy `src_components_StudentDashboard.js` → `src/components/StudentDashboard.js`
4. Copy `src_components_ProtectedRoute.js` → `src/components/ProtectedRoute.js`
5. Copy `src_App.js` → `src/App.js`
6. Copy `src_App.css` → `src/App.css`

### Step 4: Update index.js
```javascript
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import 'bootstrap/dist/css/bootstrap.min.css';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

### Step 5: Create .env file
```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_TIMEOUT=5000
```

### Step 6: Run Development Server
```bash
npm start
```

## Component Architecture

```
App
├── Login (public route)
├── Dashboard (protected route)
│   ├── StudentDashboard
│   ├── TeacherDashboard
│   └── StaffDashboard
└── ProtectedRoute (wrapper)
```

## API Integration

All components use the `api.js` service for backend communication:

```javascript
// Login
const response = await authAPI.login(username, password);

// Get Dashboard
const data = await dashboardAPI.getDashboard();

// Book Operations
const issued = await bookAPI.issueBook(bookId);
const returned = await bookAPI.returnBook(issuedBookId);
```

## State Management

The starter uses React hooks with localStorage for:
- User authentication state
- JWT token storage
- User profile data

For larger applications, consider using Redux or Context API.

## Next Steps

1. **Create more components**
   - Register component
   - Teacher/Staff dashboards
   - Book list and details
   - User profile management

2. **Add features**
   - Book reservation system
   - Fine payment
   - Notification system
   - Search and filtering

3. **Improve styling**
   - Add custom theme
   - Implement dark mode
   - Responsive design enhancements

4. **Testing**
   - Unit tests with Jest
   - Integration tests
   - E2E tests with Cypress

5. **Optimization**
   - Code splitting
   - Lazy loading
   - Performance monitoring

6. **Deployment**
   - Build optimization
   - Environment configuration
   - CI/CD setup

## Troubleshooting

### CORS Error
- Ensure Django CORS settings include http://localhost:3000
- Check API_URL in .env

### Token Issues
- Clear localStorage and login again
- Check token expiration time in backend settings

### API Connection
- Verify Django server is running
- Check network tab in browser DevTools
- Verify API_URL points to correct backend

## Resources

- [React Documentation](https://react.dev)
- [Axios Documentation](https://axios-http.com)
- [React Router](https://reactrouter.com)
- [Bootstrap Documentation](https://getbootstrap.com)

## Support

For more help, refer to:
- Main README.md
- REACT_SETUP.md
- Backend API documentation
