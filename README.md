# Phd-email-orchestrator
Autonomous agent that researches professors and drafts personalized PhD inquiry emails. It scrapes academic profiles, uses GPT‑4 to craft messages based on research interests, and requires human approval before sending. Includes secure credential handling, fallbacks, and professional Gmail delivery.
# COMPLETE SETUP GUIDE - Final Version

## All Requirements Met 

1. **UV Package Manager** - Uses `uv pip install` as required
2. **.env File** - Secure credential storage
3. **OpenAI API** - GPT-4 powered email generation
4. **Auto-Search Fixed** - URLs loaded from .env automatically
5. **No Manual Input** - Everything runs automatically

---
## Files You Need

### Essential Files:
1. **phd_email_orchestrator_env.py** - Main script (with OpenAI integration)
2. **.env** - My credentials and API keys
3. **install_with_uv.sh** - Installation script
4. **requirements.txt** - Dependencies
5. **.gitignore** - Prevents committing secrets

### Optional Files (for reference):
- Simple test version (no web scraping)
- Professor Zhang reference
- Documentation files

---

## Setup Instructions

### Step 1: Edit .env File

Open `.env` and add your credentials:

```bash
# Gmail Configuration
SENDER_EMAIL=xxxxxxxxx@gmail.com
GMAIL_APP_PASSWORD=xxxxxxxxxxx

# OpenAI API
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx  # ADD YOUR OPENAI KEY HERE

# Your Information
YOUR_NAME=xxxx
YOUR_BACKGROUND=I am a graduate student currently pursuing business analytics at SMU. I am interested in a PhD program in AI Ethics, Health Data Analytics and Machine Learning.

# Professor Information
PROFESSOR_NAME=Michael
TARGET_EMAIL=Michael.Zhang@smu.ca

# Professor URLs (these bypass auto-search - guaranteed to work!)
GOOGLE_SCHOLAR_URL=https://scholar.google.com/citations?user=RHcPtfkAAAAJ&hl=en
SMU_PROFILE_URL=https://www.smu.ca/researchers/sobey/profiles/michael-zhang.html
```

### Step 2: Install Dependencies with UV

```bash
# Make the script executable
chmod +x install_with_uv.sh

# Run the installer (uses uv as professor requires)
./install_with_uv.sh
```

This installs:
- selenium (web scraping)
- webdriver-manager (Chrome automation)
- python-dotenv (loads .env file)
- openai (GPT-4 integration)

### Step 3: Run the Agent

```bash
python phd_email_orchestrator.py
```

---

## What Happens When You Run It

```
PhD Email Orchestrator Agent
An agentic workflow for researching and emailing professors

Using credentials from .env file

Sender: xxxxxx@gmail.com
Target: Michael.Zhang@smu.ca
Your Name: xxxxxxx
OpenAI API: Enabled (will use GPT-4 for email generation)

Press Enter to start, or Ctrl+C to cancel...

[You press Enter]

Starting PhD Email Orchestrator Agent
================================================================================
Setting up browser...
Browser ready!

Researching Michael on Google Scholar...
  Using URL from .env file
Found 3 research interests and 5 publications

Researching Michael on SMU website...
  Using URL from .env file
Retrieved SMU profile information

Composing personalized email...
  Using GPT to generate personalized email...
GPT-generated email drafted!

================================================================================
DRAFTED EMAIL FOR YOUR APPROVAL
================================================================================

RESEARCH SUMMARY:
{
  "google_scholar": {
    "interests": ["AI for Business and Healthcare", "Machine Learning", "Healthcare Analytics"],
    "recent_publications": ["Supporting Youth with Mental Health Conditions..."],
    ...
  }
}

--------------------------------------------------------------------------------
SUBJECT: PhD Opportunity - Interest in Your Research
--------------------------------------------------------------------------------
Dear Professor Michael,

[GPT-4 generated personalized email based on research findings]

Best regards,
xxxxxxxx
--------------------------------------------------------------------------------

This email will be sent to: Michael.Zhang@smu.ca

Do you approve sending this email? (yes/no/edit): yes

Sending email...
Email sent successfully!

================================================================================
Workflow completed!
================================================================================

Browser closed
```

## Key Features

### 1. Automatic Everything
- Loads all credentials from .env
- Uses professor URLs from .env (no manual searching!)
- No typing required during execution

### 2. GPT-4 Email Generation
- Uses OpenAI API to write sophisticated emails
- Analyzes research interests and publications
- Creates personalized, professional content
- Falls back to template if API fails

### 3. Human-in-the-Loop (HITL)
- Shows you the email before sending
- Options: yes (send), no (cancel), edit (modify)
- You maintain full control

### 4. Four-Phase Workflow
1. **Research** - Scrapes Google Scholar + SMU
2. **Compose** - GPT-4 writes personalized email
3. **Approve** - You review and approve (HITL)
4. **Send** - Sends via Gmail SMTP

---

## Troubleshooting

### "ERROR: Missing required environment variables"
**Fix:** Make sure these are in your .env file:
- SENDER_EMAIL
- GMAIL_APP_PASSWORD
- YOUR_NAME
- TARGET_EMAIL

### "OpenAI API: Not configured"
**Fix:** Add your OpenAI API key to .env:
```
OPENAI_API_KEY=sk-proj-your-key-here
```

### "ModuleNotFoundError: No module named 'openai'"
**Fix:** Run the installer:
```bash
./install_with_uv.sh
```

### GPT generation fails
**No problem!** The agent automatically falls back to template-based email generation. You'll still get a good email.

### Auto-search not finding profiles
**Already fixed!** The URLs in your .env file are used automatically, so auto-search is bypassed entirely. 100% reliable!

---

## Security Notes

### IMPORTANT: Never Share These Files

1. **.env** - Contains your passwords and API keys
2. **config.py** - If you created it (use .env instead)

### The .gitignore File

Already configured to prevent committing:
- .env
- config.py
- __pycache__/
- Other sensitive files

---

## Comparison: With vs Without OpenAI

### Without OpenAI (Template-Based):
```
Dear Professor Michael,

I hope this email finds you well. My name is Rachael Kodi...

I am particularly drawn to your work in AI for Business and Healthcare, machine learning.

I am excited about the possibility of contributing to your research...
```

### With OpenAI (GPT-4):
```
Dear Professor Michael,

I am writing to express my sincere interest in pursuing doctoral studies under your supervision at Saint Mary's University. Your pioneering work in applying machine learning to healthcare challenges, particularly your recent NFRFE-funded project on supporting youth mental health, aligns remarkably well with my research aspirations.

As a graduate student in business analytics at SMU, I have developed a strong foundation in data analytics and machine learning. My particular interest in AI Ethics and Health Data Analytics makes your research on ethical AI deployment in healthcare settings especially compelling...

[More sophisticated, context-aware content]
```

**GPT-4 writes better emails!**

---

**Key innovations:**
- Uses UV for package management (as required)
- Stores credentials securely in .env file
- Integrates OpenAI API for intelligent email generation
- Fallback to template if API fails (graceful degradation)
- Auto-loads professor URLs to bypass unreliable web search

---

## Final Notes

This is production-ready code that:
- Follows best practices (secure credential storage)
- Uses required tools (UV package manager)
- Integrates AI capabilities (OpenAI API)
- Is reliable for live demos (URLs in .env)
- Is professional quality (proper error handling)

