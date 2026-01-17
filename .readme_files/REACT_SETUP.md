# React Frontend Setup Guide

## Overview
This guide provides step-by-step instructions to set up the React frontend for the Library Management System.

## Prerequisites
- Node.js (v16 or higher)
- npm or yarn
- Create React App CLI

## Installation & Setup

### Step 1: Create React App
```bash
cd /workspaces/library-management-system
npx create-react-app frontend
cd frontend
```

### Step 2: Install Dependencies
```bash
npm install axios react-router-dom
npm install bootstrap
npm install react-redux @reduxjs/toolkit  # Optional for state management
```

### Step 3: Project Structure
```
frontend/
├── src/
│   ├── components/
│   │   ├── Login.js
│   │   ├── Register.js
│   │   ├── Dashboard/
│   │   │   ├── StudentDashboard.js
│   │   │   ├── TeacherDashboard.js
│   │   │   └── StaffDashboard.js
│   │   ├── Books/
│   │   │   ├── BookList.js
│   │   │   ├── BookDetail.js
│   │   │   └── BookForm.js
│   │   └── Common/
│   │       ├── Navbar.js
│   │       ├── Footer.js
│   │       └── ProtectedRoute.js
│   ├── services/
│   │   ├── api.js
│   │   └── auth.js
│   ├── styles/
│   │   └── App.css
│   ├── App.js
│   └── index.js
├── public/
├── package.json
└── .env
```

### Step 4: Environment Variables
Create a `.env` file in the frontend directory:
```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_TIMEOUT=5000
```

## Key Component Files

### 1. API Service (src/services/api.js)
Handles all HTTP requests to the backend.

### 2. Login Component (src/components/Login.js)
- Form for user authentication
- JWT token storage
- Redirect to appropriate dashboard

### 3. Dashboard Components
- StudentDashboard: Display issued books and reservations
- TeacherDashboard: View library statistics
- StaffDashboard: Administrative functions

### 4. Protected Route Component
Ensures only authenticated users can access certain pages.

## Running the Frontend

### Development Server
```bash
cd frontend
npm start
```
The app will open at http://localhost:3000

### Production Build
```bash
npm run build
```

## API Integration

All API calls should use the base URL from environment variables:
```javascript
const API_URL = process.env.REACT_APP_API_URL;
```

### Authentication Flow
1. User logs in via Login component
2. Backend returns JWT token
3. Token stored in localStorage
4. All subsequent requests include token in Authorization header
5. Token refreshed automatically on expiry

## Common Issues & Solutions

### CORS Errors
- Ensure CORS_ALLOWED_ORIGINS includes frontend URL in Django settings
- Add 'http://localhost:3000' to CORS configuration

### Token Expiration
- Implement token refresh logic
- Redirect to login on 401 response

### State Management
- Use React Context API or Redux for global state
- Store user info and token securely

## Deployment

### Frontend Deployment Options
1. **Vercel** - Recommended for React apps
2. **Netlify** - Easy setup with GitHub integration
3. **AWS S3 + CloudFront** - For scalable deployments
4. **Docker** - For containerized deployments

### Build & Deploy
```bash
# Build the app
npm run build

# Test production build locally
npm install -g serve
serve -s build

# Deploy to your hosting platform
```

## Testing

```bash
# Run tests
npm test

# Run tests with coverage
npm test -- --coverage
```

## Performance Optimization

1. **Code Splitting** - Use React.lazy() for route-based splitting
2. **Image Optimization** - Use optimized image formats
3. **Caching** - Implement service workers
4. **Lazy Loading** - Load components on demand
5. **Minification** - Production build handles this automatically

## Security Best Practices

1. Never expose API keys in frontend code
2. Store JWT tokens securely (consider HttpOnly cookies)
3. Implement HTTPS for all communications
4. Validate user input on client side
5. Use environment variables for sensitive data

## Troubleshooting

### Hot Reload Not Working
- Check if port 3000 is available
- Clear node_modules and reinstall

### Build Failures
- Clear npm cache: `npm cache clean --force`
- Delete node_modules and package-lock.json, then reinstall

### API Connection Issues
- Verify Django server is running on port 8000
- Check CORS configuration in Django settings
- Verify API_URL in .env file

## Next Steps

1. Create Login component and test authentication
2. Implement dashboard components for each role
3. Create book management components
4. Add notification system integration
5. Implement state management (Redux/Context)
6. Add comprehensive error handling
7. Set up unit and integration tests
8. Configure CI/CD pipeline

## Support

For more information:
- React Documentation: https://react.dev
- Axios Documentation: https://axios-http.com
- React Router Documentation: https://reactrouter.com
