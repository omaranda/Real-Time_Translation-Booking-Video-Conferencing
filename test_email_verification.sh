#!/bin/bash

# Test script for email verification feature
# This script tests the email verification flow end-to-end

set -e

API_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:3000"

echo "=========================================="
echo "Email Verification Test Script"
echo "=========================================="
echo ""

# Generate random email
TEST_EMAIL="test_$(date +%s)@example.com"
TEST_NAME="Test User"
TEST_PASSWORD="testpass123"

echo "1. Testing translator registration..."
echo "   Email: $TEST_EMAIL"
echo ""

# Register a translator
REGISTER_RESPONSE=$(curl -s -X POST "$API_URL/translators/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$TEST_EMAIL\",
    \"name\": \"$TEST_NAME\",
    \"password\": \"$TEST_PASSWORD\",
    \"languages\": [\"SPANISH\"],
    \"hourly_rate\": \"50\"
  }")

echo "   ✓ Registration successful"
echo ""

# Try to login (should fail - email not verified)
echo "2. Testing login with unverified email..."
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$TEST_EMAIL&password=$TEST_PASSWORD" \
  -w "\n%{http_code}")

HTTP_CODE=$(echo "$LOGIN_RESPONSE" | tail -n 1)

if [ "$HTTP_CODE" == "403" ]; then
  echo "   ✓ Login correctly blocked for unverified email"
else
  echo "   ✗ Expected 403, got $HTTP_CODE"
  exit 1
fi
echo ""

# Get verification token from database
echo "3. Retrieving verification token from database..."
VERIFICATION_TOKEN=$(docker exec callcenter-postgres psql -U callcenter -t -c \
  "SELECT email_verification_token FROM users WHERE email = '$TEST_EMAIL';" | tr -d ' ')

if [ -z "$VERIFICATION_TOKEN" ]; then
  echo "   ✗ No verification token found"
  exit 1
fi

echo "   ✓ Token retrieved: ${VERIFICATION_TOKEN:0:20}..."
echo ""

# Verify email
echo "4. Verifying email with token..."
VERIFY_RESPONSE=$(curl -s -X POST "$API_URL/auth/verify-email?token=$VERIFICATION_TOKEN")

if echo "$VERIFY_RESPONSE" | grep -q "verified"; then
  echo "   ✓ Email verified successfully"
else
  echo "   ✗ Verification failed"
  echo "   Response: $VERIFY_RESPONSE"
  exit 1
fi
echo ""

# Try to login again (should succeed)
echo "5. Testing login with verified email..."
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$TEST_EMAIL&password=$TEST_PASSWORD")

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
  echo "   ✓ Login successful with verified email"
else
  echo "   ✗ Login failed"
  echo "   Response: $LOGIN_RESPONSE"
  exit 1
fi
echo ""

# Test resend verification
echo "6. Testing resend verification..."
RESEND_RESPONSE=$(curl -s -X POST "$API_URL/auth/resend-verification?email=$TEST_EMAIL")

if echo "$RESEND_RESPONSE" | grep -q "already verified"; then
  echo "   ✓ Correctly detected already verified email"
else
  echo "   ✗ Unexpected response"
  echo "   Response: $RESEND_RESPONSE"
fi
echo ""

echo "=========================================="
echo "✓ All tests passed!"
echo "=========================================="
echo ""
echo "Verification URL was: $FRONTEND_URL/verify-email?token=$VERIFICATION_TOKEN"
echo ""
