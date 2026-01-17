#!/bin/bash
# API Testing Script for Library Management System

BASE_URL="http://localhost:8000"

echo "================================================"
echo "   Library Management System - API Testing"
echo "================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Register a new user
echo -e "${YELLOW}[TEST 1] User Registration${NC}"
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/api/register/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "role": "student"
  }')

echo "Response: $REGISTER_RESPONSE"
echo ""

# Test 2: Get JWT Token
echo -e "${YELLOW}[TEST 2] Get JWT Token${NC}"
TOKEN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/token/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }')

echo "Response: $TOKEN_RESPONSE"

# Extract token
ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"access":"[^"]*' | cut -d'"' -f4)
echo "Access Token: ${ACCESS_TOKEN:0:30}..."
echo ""

# Test 3: Access protected dashboard API
if [ -n "$ACCESS_TOKEN" ]; then
  echo -e "${YELLOW}[TEST 3] Access Protected Dashboard API${NC}"
  DASHBOARD=$(curl -s -X GET "$BASE_URL/api/dashboard/" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json")
  
  echo "Response: $DASHBOARD"
  echo ""
else
  echo -e "${RED}[TEST 3] SKIPPED - Could not obtain access token${NC}"
  echo ""
fi

# Test 4: Test login page
echo -e "${YELLOW}[TEST 4] Check Login Page${NC}"
LOGIN_CHECK=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/login/")
if [ "$LOGIN_CHECK" == "200" ]; then
  echo -e "${GREEN}✓ Login page is accessible (HTTP 200)${NC}"
else
  echo -e "${RED}✗ Login page returned HTTP $LOGIN_CHECK${NC}"
fi
echo ""

# Test 5: Test registration page
echo -e "${YELLOW}[TEST 5] Check Registration Page${NC}"
REGISTER_CHECK=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/register/")
if [ "$REGISTER_CHECK" == "200" ]; then
  echo -e "${GREEN}✓ Registration page is accessible (HTTP 200)${NC}"
else
  echo -e "${RED}✗ Registration page returned HTTP $REGISTER_CHECK${NC}"
fi
echo ""

# Test 6: Test JWT token refresh
if [ -n "$ACCESS_TOKEN" ]; then
  echo -e "${YELLOW}[TEST 6] Test JWT Token Refresh${NC}"
  
  # Get refresh token first
  TOKEN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/token/" \
    -H "Content-Type: application/json" \
    -d '{
      "username": "testuser",
      "password": "testpass123"
    }')
  
  REFRESH_TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"refresh":"[^"]*' | cut -d'"' -f4)
  
  if [ -n "$REFRESH_TOKEN" ]; then
    REFRESH_RESPONSE=$(curl -s -X POST "$BASE_URL/api/token/refresh/" \
      -H "Content-Type: application/json" \
      -d "{
        \"refresh\": \"$REFRESH_TOKEN\"
      }")
    
    echo "Refresh Response: $REFRESH_RESPONSE"
  else
    echo -e "${RED}✗ Could not extract refresh token${NC}"
  fi
else
  echo -e "${YELLOW}[TEST 6] SKIPPED - No access token available${NC}"
fi
echo ""

echo "================================================"
echo "Testing Complete!"
echo "================================================"
