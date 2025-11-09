# 🚀 Quick Deployment Guide - PONS AUTO

## ✅ What's Ready

All 4 components are now implemented:
1. ✅ **Stripe Payment Integration** - Checkout, webhooks, subscriptions
2. ✅ **User Authentication** - JWT tokens, signup/login, password hashing
3. ✅ **Billing System** - Plan limits, usage tracking, subscription management
4. ✅ **Deployment Config** - Railway ready, Streamlit Cloud ready

---

## 🚀 Option 1: Deploy to Railway + Streamlit Cloud (RECOMMENDED)

### Part A: Deploy Backend to Railway

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login to Railway
railway login

# 3. Navigate to project
cd /Users/brandonsandoval/Downloads/pons-auto

# 4. Initialize Railway project
railway init
# Name it: pons-auto-backend

# 5. Add PostgreSQL database
railway add postgresql

# 6. Add Redis
railway add redis

# 7. Set environment variables
railway variables set JWT_SECRET_KEY=$(openssl rand -hex 32)
railway variables set STRIPE_SECRET_KEY=sk_live_your_key
railway variables set STRIPE_WEBHOOK_SECRET=whsec_your_secret
railway variables set OPENAI_API_KEY=sk-your_key

# Set Stripe Price IDs (after creating in Stripe Dashboard)
railway variables set STRIPE_STARTER_PRICE_ID=price_xxxxx
railway variables set STRIPE_PROFESSIONAL_PRICE_ID=price_xxxxx
railway variables set STRIPE_BUSINESS_PRICE_ID=price_xxxxx
railway variables set STRIPE_ENTERPRISE_PRICE_ID=price_xxxxx

# 8. Deploy!
railway up

# 9. Get your backend URL
railway status
# Save this URL: https://pons-auto-backend.railway.app
```

**Cost:** ~$20/month (includes PostgreSQL + Redis)

---

### Part B: Deploy Frontend to Streamlit Cloud

```bash
# 1. Create GitHub repository
cd /Users/brandonsandoval/Downloads/pons-auto
git init
git add .
git commit -m "Initial commit - PONS AUTO"

# Create repo on GitHub:
# - Go to github.com
# - Click "New repository"
# - Name: pons-auto
# - Click "Create repository"

# Push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/pons-auto.git
git branch -M main
git push -u origin main

# 2. Deploy to Streamlit Cloud
# - Go to share.streamlit.io
# - Click "New app"
# - Connect GitHub account
# - Select repository: pons-auto
# - Branch: main
# - Main file path: dashboard/app.py
# - Click "Deploy"

# 3. Add secrets in Streamlit Cloud dashboard
# Settings → Secrets → Add:
```

Create `dashboard/.streamlit/secrets.toml`:
```toml
API_BASE_URL = "https://pons-auto-backend.railway.app/api/v1"
OPENAI_API_KEY = "sk-your-key"
```

**Cost:** $20/month (private app) or FREE (public app)

---

## 💳 Step 2: Set Up Stripe

### 1. Create Stripe Account
- Go to https://stripe.com
- Sign up for account
- Complete onboarding

### 2. Create Products & Prices

In Stripe Dashboard → Products:

**Product 1: Starter Plan**
- Name: PONS AUTO Starter
- Price: $49/month
- Recurring: Monthly
- Copy Price ID: `price_xxxxx`

**Product 2: Professional Plan**
- Name: PONS AUTO Professional  
- Price: $149/month
- Recurring: Monthly
- Copy Price ID: `price_xxxxx`

**Product 3: Business Plan**
- Name: PONS AUTO Business
- Price: $299/month
- Recurring: Monthly
- Copy Price ID: `price_xxxxx`

**Product 4: Enterprise Plan**
- Name: PONS AUTO Enterprise
- Price: $499/month
- Recurring: Monthly
- Copy Price ID: `price_xxxxx`

### 3. Set Up Webhook

In Stripe Dashboard → Developers → Webhooks:

- Click "Add endpoint"
- URL: `https://pons-auto-backend.railway.app/api/v1/billing/webhook`
- Events to listen to:
  - `checkout.session.completed`
  - `customer.subscription.updated`
  - `customer.subscription.deleted`
- Copy Webhook Secret: `whsec_xxxxx`

### 4. Update Railway Variables

```bash
railway variables set STRIPE_STARTER_PRICE_ID=price_xxxxx
railway variables set STRIPE_PROFESSIONAL_PRICE_ID=price_xxxxx
railway variables set STRIPE_BUSINESS_PRICE_ID=price_xxxxx
railway variables set STRIPE_ENTERPRISE_PRICE_ID=price_xxxxx
railway variables set STRIPE_WEBHOOK_SECRET=whsec_xxxxx
```

---

## 🔐 Step 3: Test Authentication

```bash
# Test signup
curl -X POST https://pons-auto-backend.railway.app/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "full_name": "Test User",
    "dealership_name": "Test Motors"
  }'

# Response:
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "email": "test@example.com",
    "subscription_plan": "trial",
    "subscription_status": "active"
  }
}

# Test login
curl -X POST https://pons-auto-backend.railway.app/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=password123"
```

---

## 💰 Step 4: Test Payments

```bash
# 1. Create checkout session
curl -X POST https://pons-auto-backend.railway.app/api/v1/billing/checkout \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plan_id": "professional",
    "success_url": "https://ponsauto.com/success",
    "cancel_url": "https://ponsauto.com/pricing"
  }'

# Response:
{
  "checkout_url": "https://checkout.stripe.com/c/pay/cs_test_...",
  "session_id": "cs_test_..."
}

# 2. Open checkout_url in browser
# 3. Use Stripe test card: 4242 4242 4242 4242
# 4. Complete payment
# 5. Webhook will update user subscription automatically
```

---

## 🌐 Step 5: Configure Custom Domain

### Buy Domain (Optional but Recommended)

1. **Buy domain** from Namecheap/GoDaddy: `ponsauto.com` ($10-15/year)

2. **Configure DNS** in your domain registrar:

```
Type    Name    Value                               TTL
A       @       Railway app IP (get from Railway)   3600
CNAME   www     pons-auto-backend.railway.app       3600
CNAME   api     pons-auto-backend.railway.app       3600
CNAME   app     your-app.streamlit.app              3600
```

3. **Add custom domain in Railway:**
- Railway Dashboard → Settings → Domains
- Click "Add Domain"
- Enter: api.ponsauto.com
- Follow DNS instructions

4. **Add custom domain in Streamlit:**
- Streamlit Dashboard → Settings → Custom subdomain
- Enter: app.ponsauto.com (requires paid plan)

---

## 📊 Step 6: Monitoring & Analytics

### Add Google Analytics (Optional)

```python
# Add to dashboard/app.py
import streamlit.components.v1 as components

components.html("""
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
""", height=0)
```

### Monitor Usage

Check Railway logs:
```bash
railway logs
```

Check Stripe Dashboard:
- Revenue
- Active subscriptions
- Failed payments

---

## 🔧 API Endpoints Summary

### Authentication
- `POST /api/v1/auth/signup` - Create account
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Get current user
- `GET /api/v1/auth/verify` - Verify token

### Billing
- `GET /api/v1/billing/plans` - List all plans
- `GET /api/v1/billing/plans/{plan_id}` - Get plan details
- `POST /api/v1/billing/checkout` - Create checkout session
- `GET /api/v1/billing/subscription` - Get user subscription
- `POST /api/v1/billing/portal` - Customer portal
- `POST /api/v1/billing/check-limit` - Check usage limits
- `GET /api/v1/billing/usage` - Get usage stats
- `POST /api/v1/billing/webhook` - Stripe webhook (Stripe calls this)

### AI Features
- `POST /api/v1/ai/description` - Generate AI description
- `POST /api/v1/ai/image/background` - AI background (single)
- `POST /api/v1/ai/image/background/batch` - AI background (batch)

---

## 💡 Next Steps

### Week 1: Test Everything
- [ ] Deploy backend to Railway
- [ ] Deploy frontend to Streamlit Cloud  
- [ ] Test signup/login flow
- [ ] Test Stripe checkout (test mode)
- [ ] Test webhook delivery
- [ ] Verify usage limits work

### Week 2: Go Live
- [ ] Switch Stripe to live mode
- [ ] Update Stripe webhook to live endpoint
- [ ] Configure custom domain
- [ ] Add Google Analytics
- [ ] Create landing page
- [ ] Add Terms of Service
- [ ] Add Privacy Policy

### Week 3: Marketing
- [ ] Create demo video
- [ ] Write blog post
- [ ] Post on Reddit r/entrepreneur
- [ ] Facebook Ads to dealers
- [ ] Google Ads for "car listing software"
- [ ] Email 50 local dealers

### Week 4: Support & Iterate
- [ ] Set up support email
- [ ] Monitor user feedback
- [ ] Fix bugs
- [ ] Add requested features
- [ ] Celebrate first paying customer! 🎉

---

## 📞 Support

**Questions about deployment?**
- Railway Docs: https://docs.railway.app
- Streamlit Docs: https://docs.streamlit.io
- Stripe Docs: https://stripe.com/docs

**Need help?**
- Check DEPLOYMENT_MONETIZATION_GUIDE.md for detailed info
- Railway Discord: https://discord.gg/railway
- Stripe Support: support@stripe.com

---

## 💰 Cost Summary

**Monthly Costs:**
- Railway (Backend + DB + Redis): $20
- Streamlit Cloud: $20 (or free for public)
- Domain: $1 (annual / 12)
- Stripe: 2.9% + $0.30 per transaction
- OpenAI API: ~$200 (varies by usage)

**Total: $40-50/month + OpenAI usage**

**Revenue Potential:**
- 10 customers x $149 = $1,490/month
- Break-even: ~3 customers
- Profit margin: 80-90%

---

## 🎊 You're Ready!

Everything is built and ready to deploy:
- ✅ Authentication system
- ✅ Payment processing
- ✅ Subscription management
- ✅ Usage tracking & limits
- ✅ AI features
- ✅ Mobile dashboard
- ✅ API backend

**Time to launch:** ~4 hours
**Time to first customer:** Could be today! 🚀

Good luck with PONS AUTO! 🚗✨
