# Email Verification Feature

This document describes the email verification system implemented for user registration on the Translation Platform.

## Overview

The email verification feature ensures that users can only access the platform after confirming their email address. This improves security and ensures valid contact information.

## Features

- **Automatic Email Sending**: Verification emails are sent automatically upon registration
- **Token-Based Verification**: Secure, time-limited tokens (24-hour expiration)
- **Resend Capability**: Users can request a new verification email if needed
- **Development Mode**: Console logging when SMTP is disabled for easy local testing
- **Email Templates**: Professional HTML and plain-text email templates

## Architecture

### Backend Components

#### 1. Database Schema ([backend/app/models/user.py](../backend/app/models/user.py#L46-L49))

Added three new fields to the `User` model:
- `is_email_verified` (Boolean): Whether the email has been verified
- `email_verification_token` (String): Unique token for verification
- `email_verification_token_expires` (DateTime): Token expiration timestamp

#### 2. Email Service ([backend/app/services/email_service.py](../backend/app/services/email_service.py))

Functions:
- `generate_verification_token()`: Creates secure random tokens
- `get_verification_token_expiry()`: Returns expiration time (24 hours)
- `send_verification_email(email, name, token)`: Sends verification email
- `send_welcome_email(email, name)`: Sends welcome email after verification

#### 3. API Endpoints ([backend/app/api/auth.py](../backend/app/api/auth.py))

**POST /auth/verify-email**
- Verifies email address using token
- Returns success/error message
- Sends welcome email on success

**POST /auth/resend-verification**
- Generates new verification token
- Sends new verification email
- Parameters: `email` (query parameter)

**POST /auth/login** (Modified)
- Now checks if email is verified
- Returns 403 error if email not verified

**POST /auth/register** (Modified)
- Generates verification token
- Sends verification email
- Creates user with `is_email_verified=false`

**POST /translators/register** (Modified)
- Same verification flow as general registration

### Frontend Components

#### 1. Email Verification Page ([frontend/src/app/verify-email/page.tsx](../frontend/src/app/verify-email/page.tsx))

- Handles verification token from URL query parameter
- Shows loading, success, or error states
- Auto-redirects to login after successful verification
- Provides link to resend verification if expired

#### 2. Resend Verification Page ([frontend/src/app/resend-verification/page.tsx](../frontend/src/app/resend-verification/page.tsx))

- Allows users to request new verification email
- Simple form with email input
- Shows success message after sending

#### 3. Registration Page Updates ([frontend/src/app/register/translator/page.tsx](../frontend/src/app/register/translator/page.tsx))

- Shows success screen after registration
- Displays email verification instructions
- Provides links to resend verification or login

#### 4. Login Page Updates ([frontend/src/app/login/page.tsx](../frontend/src/app/login/page.tsx))

- Shows specific error for unverified emails
- Provides link to resend verification page

## Configuration

### Environment Variables

Add to `backend/.env`:

```env
# Email Configuration
SMTP_ENABLED=false  # Set to true when SMTP is configured
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_TLS=true
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@translationplatform.com
FRONTEND_URL=http://localhost:3000
```

### Development Mode

When `SMTP_ENABLED=false`:
- Emails are not actually sent
- Verification URLs are printed to console
- Perfect for local development and testing

### Production Setup

For production, configure a real SMTP server:

**Gmail Example:**
1. Enable 2FA on your Google account
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. Set environment variables:
   ```env
   SMTP_ENABLED=true
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_TLS=true
   SMTP_USER=yourapp@gmail.com
   SMTP_PASSWORD=your-16-char-app-password
   SMTP_FROM_EMAIL=noreply@translationplatform.com
   FRONTEND_URL=https://yourplatform.com
   ```

**Other SMTP Providers:**
- **SendGrid**: smtp.sendgrid.net, port 587
- **Amazon SES**: email-smtp.us-east-1.amazonaws.com, port 587
- **Mailgun**: smtp.mailgun.org, port 587

## User Flow

### Registration Flow

1. User fills out registration form
2. Backend creates user with `is_email_verified=false`
3. Verification token generated and saved
4. Verification email sent to user
5. Success screen shown with instructions
6. User receives email with verification link

### Verification Flow

1. User clicks link in email (e.g., `http://localhost:3000/verify-email?token=abc123`)
2. Frontend sends token to `/auth/verify-email`
3. Backend validates token and expiration
4. User marked as verified
5. Welcome email sent
6. User redirected to login page

### Login Flow

1. User attempts to login
2. Backend checks credentials
3. If email not verified, returns 403 error
4. Frontend shows error with resend link
5. User can click to resend verification email

## Email Templates

### Verification Email

**Subject:** "Verify your Translation Platform account"

**Content:**
- Personalized greeting
- Clear call-to-action button
- Plain text link as fallback
- Expiration warning (24 hours)
- Spam/ignore instructions

### Welcome Email

**Subject:** "Welcome to Translation Platform!"

**Content:**
- Confirmation of verification
- Login link
- Welcome message

## Testing

### Development Testing

1. Start the stack: `./stack.sh start`
2. Register a new translator at http://localhost:3000/register/translator
3. Check backend logs for verification URL:
   ```bash
   ./stack.sh logs backend
   ```
4. Copy the verification URL from logs and open in browser
5. Verify that email is confirmed and you can log in

### Manual Testing Checklist

- [ ] Registration creates unverified user
- [ ] Verification email logged to console (dev mode)
- [ ] Verification link works correctly
- [ ] Token expiration is enforced (24 hours)
- [ ] Invalid tokens show appropriate error
- [ ] Already verified emails handled gracefully
- [ ] Login blocked for unverified users
- [ ] Resend verification works
- [ ] Welcome email sent after verification
- [ ] Frontend flows work end-to-end

## Database Migration

The new fields are added to the User model. When you restart the backend with the new code:

1. FastAPI will automatically create the new columns (via `Base.metadata.create_all()`)
2. Existing users will have `is_email_verified=NULL` by default
3. You may want to run a migration to set existing users to verified:

```sql
UPDATE users SET is_email_verified = true WHERE is_email_verified IS NULL;
```

Or use Alembic for proper migrations:

```bash
cd backend
alembic revision --autogenerate -m "Add email verification fields"
alembic upgrade head
```

## Security Considerations

1. **Token Security**: Tokens are generated using `secrets.token_urlsafe(32)` for cryptographic strength
2. **Expiration**: Tokens expire after 24 hours
3. **One-Time Use**: Tokens are cleared after successful verification
4. **HTTPS**: Use HTTPS in production to protect tokens in transit
5. **Rate Limiting**: Consider adding rate limiting to resend endpoint

## Troubleshooting

### Emails not sending

1. Check `SMTP_ENABLED=true` in `.env`
2. Verify SMTP credentials are correct
3. Check backend logs for error messages
4. Try sending a test email manually

### Token expired errors

1. Tokens are valid for 24 hours
2. Use the resend verification feature
3. Check server time synchronization

### Users can't verify

1. Check verification URL is correct
2. Ensure token parameter is in URL
3. Verify backend is accessible
4. Check database connection

## Future Enhancements

- [ ] Add email rate limiting
- [ ] Implement email change verification
- [ ] Add password reset via email
- [ ] Email notification preferences
- [ ] Multi-language email templates
- [ ] Email open/click tracking
- [ ] Batch email sending for notifications
