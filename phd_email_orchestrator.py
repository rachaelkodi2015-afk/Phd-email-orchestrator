"""
PhD Email Orchestrator Agent - .env Version
Loads credentials from .env file using python-dotenv
This is the BEST PRACTICE way to handle secrets!
"""

import os
import ssl
import smtplib
from email.message import EmailMessage
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Get configuration from environment variables
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
GMAIL_APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')
YOUR_NAME = os.getenv('YOUR_NAME')
YOUR_BACKGROUND = os.getenv('YOUR_BACKGROUND')
GOOGLE_SCHOLAR_URL = os.getenv('GOOGLE_SCHOLAR_URL')
SMU_PROFILE_URL = os.getenv('SMU_PROFILE_URL')
TARGET_EMAIL = os.getenv('TARGET_EMAIL')
PROFESSOR_NAME = os.getenv('PROFESSOR_NAME')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Initialize OpenAI client
openai_client = None
if OPENAI_API_KEY:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
    print("OpenAI API initialized")

# Validate required variables
if not all([SENDER_EMAIL, GMAIL_APP_PASSWORD, YOUR_NAME, TARGET_EMAIL]):
    print("ERROR: Missing required environment variables in .env file!")
    print("Required: SENDER_EMAIL, GMAIL_APP_PASSWORD, YOUR_NAME, TARGET_EMAIL")
    exit(1)

print("Loaded configuration from .env file")


class PhDEmailOrchestrator:
    """
    Single orchestrator agent that handles:
    1. Research (scraping Google Scholar + SMU website)
    2. Email composition
    3. Human approval (HITL)
    4. Email sending
    """
    
    def __init__(self, professor_name=PROFESSOR_NAME, test_email=TARGET_EMAIL):
        self.professor_name = professor_name
        self.test_email = test_email
        self.research_data = {}
        self.drafted_email = None
        self.driver = None
        
    def setup_browser(self):
        """Initialize Selenium WebDriver with Chrome"""
        print(" Setting up browser...")
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        print(" Browser ready!")
        
    def scrape_google_scholar(self, scholar_url=None):
        """Scrape Google Scholar for professor's research interests and publications"""
        print(f"\n Researching {self.professor_name} on Google Scholar...")
        
        # Use provided URL from .env if available
        if not scholar_url and GOOGLE_SCHOLAR_URL:
            scholar_url = GOOGLE_SCHOLAR_URL
            print(f"  Using URL from .env file")
        
        try:
            if not scholar_url:
                print("  Attempting automatic search...")
                
                search_query = f"{self.professor_name} Saint Mary's University"
                profiles_url = f"https://scholar.google.com/citations?view_op=search_authors&mauthors={search_query.replace(' ', '+')}&hl=en"
                
                self.driver.get(profiles_url)
                time.sleep(3)
                
                found_profile = False
                try:
                    profile_results = self.driver.find_elements(By.CLASS_NAME, "gs_ai_name")
                    
                    if profile_results:
                        print(f"  Found {len(profile_results)} potential profile(s)")
                        
                        if len(profile_results) == 1:
                            profile_link = profile_results[0].find_element(By.TAG_NAME, "a")
                            scholar_url = profile_link.get_attribute('href')
                            profile_name = profile_results[0].text
                            print(f"  Auto-selected: {profile_name}")
                            found_profile = True
                        else:
                            print("\n  Multiple profiles found. Please select:")
                            for i, result in enumerate(profile_results[:5], 1):
                                name = result.text
                                try:
                                    parent = result.find_element(By.XPATH, "..")
                                    affiliation = parent.find_element(By.CLASS_NAME, "gs_ai_aff").text
                                    print(f"  {i}. {name} - {affiliation}")
                                except:
                                    print(f"  {i}. {name}")
                            
                            print(f"  {len(profile_results[:5]) + 1}. None of these / Enter URL manually")
                            
                            choice = input("\n  Enter choice number: ").strip()
                            
                            try:
                                choice_num = int(choice)
                                if 1 <= choice_num <= len(profile_results[:5]):
                                    profile_link = profile_results[choice_num - 1].find_element(By.TAG_NAME, "a")
                                    scholar_url = profile_link.get_attribute('href')
                                    found_profile = True
                                    print(f"  Selected profile {choice_num}")
                            except:
                                pass
                
                except Exception as e:
                    print(f"  Search attempt failed: {str(e)[:100]}")
                
                if not found_profile:
                    print("\n  Could not find profile automatically")
                    scholar_url = input("  Please enter the Google Scholar PROFILE URL (or 'skip' to skip): ")
                    
                    if scholar_url.lower() == 'skip':
                        print("  Skipping Google Scholar")
                        self.research_data['google_scholar'] = {'skipped': True}
                        return
            
            # Visit the scholar profile
            self.driver.get(scholar_url)
            time.sleep(3)
            
            # Extract research interests
            interests = []
            try:
                interest_elements = self.driver.find_elements(By.CLASS_NAME, "gsc_prf_inta")
                interests = [elem.text for elem in interest_elements if elem.text]
            except Exception as e:
                print(f"  Could not extract interests: {e}")
            
            # Extract recent publications
            publications = []
            try:
                pub_elements = self.driver.find_elements(By.CLASS_NAME, "gsc_a_t")[:5]
                publications = [elem.text for elem in pub_elements if elem.text]
            except Exception as e:
                print(f"  Could not extract publications: {e}")
            
            # Extract citation count
            citations = None
            try:
                citation_elem = self.driver.find_element(By.CLASS_NAME, "gsc_rsb_std")
                citations = citation_elem.text
            except Exception as e:
                print(f"  Could not extract citations: {e}")
            
            self.research_data['google_scholar'] = {
                'interests': interests,
                'recent_publications': publications,
                'citations': citations,
                'profile_url': scholar_url
            }
            
            print(f" Found {len(interests)} research interests and {len(publications)} publications")
            
        except Exception as e:
            print(f" Error scraping Google Scholar: {e}")
            self.research_data['google_scholar'] = {'error': str(e)}
    
    def scrape_smu_website(self, smu_url=None):
        """Scrape SMU website for professor's profile and additional info"""
        print(f"\n Researching {self.professor_name} on SMU website...")
        
        # Use provided URL from .env if available
        if not smu_url and SMU_PROFILE_URL:
            smu_url = SMU_PROFILE_URL
            print(f"  Using URL from .env file")
        
        try:
            if not smu_url:
                print("  Attempting automatic search...")
                
                search_query = f"{self.professor_name} Saint Mary's University Halifax faculty profile"
                google_search_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
                self.driver.get(google_search_url)
                time.sleep(3)
                
                found_smu = False
                try:
                    smu_links = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'smu.ca')]")
                    
                    if smu_links:
                        profile_links = []
                        for link in smu_links[:10]:
                            href = link.get_attribute('href')
                            if any(keyword in href.lower() for keyword in ['profile', 'faculty', 'researcher', 'staff']):
                                try:
                                    link_text = link.text
                                    profile_links.append((href, link_text))
                                except:
                                    profile_links.append((href, ""))
                        
                        if profile_links:
                            if len(profile_links) == 1:
                                smu_url = profile_links[0][0]
                                print(f"  Auto-selected: {profile_links[0][1] if profile_links[0][1] else 'SMU profile'}")
                                found_smu = True
                            else:
                                print("\n  Multiple SMU pages found. Please select:")
                                for i, (url, text) in enumerate(profile_links[:5], 1):
                                    display_text = text[:60] if text else url[:60]
                                    print(f"  {i}. {display_text}")
                                print(f"  {len(profile_links[:5]) + 1}. None of these / Enter URL manually")
                                print(f"  {len(profile_links[:5]) + 2}. Skip SMU scraping")
                                
                                choice = input("\n  Enter choice number: ").strip()
                                
                                try:
                                    choice_num = int(choice)
                                    if 1 <= choice_num <= len(profile_links[:5]):
                                        smu_url = profile_links[choice_num - 1][0]
                                        found_smu = True
                                        print(f"  Selected option {choice_num}")
                                    elif choice_num == len(profile_links[:5]) + 2:
                                        print("  Skipping SMU website")
                                        self.research_data['smu'] = {'skipped': True}
                                        return
                                except:
                                    pass
                
                except Exception as e:
                    print(f"  Search attempt failed: {str(e)[:100]}")
                
                if not found_smu:
                    print("\n  Could not find SMU profile automatically")
                    smu_url = input("  Please enter the SMU profile URL (or 'skip' to skip): ")
                    if not smu_url or smu_url.lower() == 'skip':
                        print("  Skipping SMU website")
                        self.research_data['smu'] = {'skipped': True}
                        return
            
            # Visit the SMU profile
            self.driver.get(smu_url)
            time.sleep(3)
            
            # Extract profile information
            profile_text = self.driver.find_element(By.TAG_NAME, "body").text
            
            bio = ""
            try:
                bio_section = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Research') or contains(text(), 'Biography') or contains(text(), 'About')]")
                bio = bio_section.text[:500]
            except:
                pass
            
            self.research_data['smu'] = {
                'profile_url': smu_url,
                'bio_snippet': bio,
                'full_text_length': len(profile_text)
            }
            
            print(f" Retrieved SMU profile information")
            
        except Exception as e:
            print(f" Error scraping SMU website: {e}")
            self.research_data['smu'] = {'error': str(e)}
    
    def compose_email(self, your_name, your_background):
        """Compose a personalized email based on research findings"""
        print("\n  Composing personalized email...")
        
        your_background = your_background.strip()
        
        interests = self.research_data.get('google_scholar', {}).get('interests', [])
        publications = self.research_data.get('google_scholar', {}).get('recent_publications', [])
        
        # Debug: Show what was found
        print(f"  DEBUG: Found {len(interests)} interests: {interests[:2] if interests else 'None'}")
        print(f"  DEBUG: Found {len(publications)} publications: {publications[0][:50] if publications else 'None'}...")
        
        # If OpenAI is available, use GPT to write the email
        if openai_client and (interests or publications):
            print("  Using GPT to generate personalized email...")
            try:
                email_body = self._generate_email_with_gpt(your_name, your_background, interests, publications)
                subject = f"PhD Opportunity - Interest in Your Research"
                
                self.drafted_email = {
                    'subject': subject,
                    'body': email_body
                }
                print(" GPT-generated email drafted!")
                return
            except Exception as e:
                print(f"  GPT generation failed: {e}")
                print("  Falling back to template-based email...")
        
        # Fallback: Template-based email composition
        personalization = []
        
        # Filter out invalid publications (placeholders, too short, etc.)
        valid_publications = [
            pub for pub in publications 
            if pub and len(pub) > 10 and pub.lower() not in ['title', 'publication', 'paper', 'article']
        ]
        
        if interests:
            interest_text = f"I am particularly drawn to your work in {', '.join(interests[:2])}"
            if len(interests) > 2:
                interest_text += f", and {interests[2]}"
            interest_text += "."
            personalization.append(interest_text)
        
        if valid_publications:
            pub_text = f"Your recent publication \"{valid_publications[0]}\" especially resonates with my research interests."
            personalization.append(pub_text)
        
        personalization_paragraph = "\n\n".join(personalization) if personalization else ""
        
        subject = f"PhD Opportunity - Interest in Your Research"
        
        body_parts = [
            f"Dear Professor {self.professor_name},",
            "",
            f"I hope this email finds you well. My name is {your_name}, and I am writing to express my strong interest in pursuing a PhD under your supervision.",
            "",
            your_background
        ]
        
        if personalization_paragraph:
            body_parts.extend(["", personalization_paragraph])
        
        body_parts.extend([
            "",
            "I am excited about the possibility of contributing to your research and would greatly appreciate the opportunity to discuss potential PhD projects with you. I believe my background and research interests align well with your work, and I am eager to learn from your expertise.",
            "",
            "Would you be available for a brief meeting to discuss this opportunity further? I am happy to work around your schedule.",
            "",
            "Thank you for considering my interest. I look forward to hearing from you.",
            "",
            "Best regards,",
            your_name
        ])
        
        body = "\n".join(body_parts)

        self.drafted_email = {
            'subject': subject,
            'body': body
        }
        
        print(" Email drafted!")
    
    def _generate_email_with_gpt(self, your_name, your_background, interests, publications):
        """Use GPT to generate a personalized email"""
        
        # Build context for GPT
        research_context = f"Professor {self.professor_name}'s research interests: {', '.join(interests) if interests else 'Not available'}.\n"
        if publications:
            research_context += f"Recent publications include: {publications[0]}"
        
        prompt = f"""You are helping a PhD applicant write a professional, personalized email to a professor.

Applicant Information:
- Name: {your_name}
- Background: {your_background}

Professor Information:
- Name: Professor {self.professor_name}
- {research_context}

Write a professional PhD inquiry email that:
1. Is warm but formal
2. References specific research interests or publications
3. Explains why the applicant is a good fit
4. Requests a meeting to discuss PhD opportunities
5. Is concise (250-300 words)
6. Shows genuine interest in the professor's work

Do not include a subject line. Start with "Dear Professor {self.professor_name}," and end with "Best regards,\n{your_name}"
"""
        
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert at writing professional academic emails."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content.strip()
        
    def request_approval(self):
        """Display email and request human approval (HITL)"""
        print("\n" + "="*80)
        print(" DRAFTED EMAIL FOR YOUR APPROVAL")
        print("="*80)
        
        print(f"\n RESEARCH SUMMARY:")
        print(json.dumps(self.research_data, indent=2))
        
        print(f"\n" + "-"*80)
        print(f"SUBJECT: {self.drafted_email['subject']}")
        print(f"-"*80)
        print(self.drafted_email['body'])
        print("-"*80)
        
        print(f"\n This email will be sent to: {self.test_email}")
        
        while True:
            approval = input("\n Do you approve sending this email? (yes/no/edit): ").lower().strip()
            
            if approval == 'yes':
                print(" Email approved for sending!")
                return True
            elif approval == 'no':
                print(" Email sending cancelled.")
                return False
            elif approval == 'edit':
                print("\n  Enter your edited email body (type 'END' on a new line when done):")
                lines = []
                while True:
                    line = input()
                    if line == 'END':
                        break
                    lines.append(line)
                self.drafted_email['body'] = '\n'.join(lines)
                
                print("\n" + "-"*80)
                print("UPDATED EMAIL:")
                print(self.drafted_email['body'])
                print("-"*80)
            else:
                print("  Please enter 'yes', 'no', or 'edit'")
    
    def send_email(self, sender_email, app_password):
        """Send the approved email via Gmail SMTP"""
        print("\n Sending email...")
        
        try:
            msg = EmailMessage()
            msg['Subject'] = self.drafted_email['subject']
            msg['From'] = sender_email
            msg['To'] = self.test_email
            msg.set_content(self.drafted_email['body'])
            
            smtp_server = "smtp.gmail.com"
            port = 465
            
            context = ssl._create_unverified_context()
            
            with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
                server.login(sender_email, app_password)
                server.send_message(msg)
            
            print(" Email sent successfully!")
            return True
            
        except smtplib.SMTPException as e:
            print(f" SMTP Error: {e}")
            return False
        except Exception as e:
            print(f" Error sending email: {e}")
            return False
    
    def cleanup(self):
        """Close browser and cleanup resources"""
        if self.driver:
            self.driver.quit()
            print("\n Browser closed")
    
    def run(self, your_name, your_background, sender_email, app_password):
        """Main orchestration method"""
        try:
            print(" Starting PhD Email Orchestrator Agent")
            print("="*80)
            
            # Phase 1: Research
            self.setup_browser()
            self.scrape_google_scholar()
            self.scrape_smu_website()
            
            # Phase 2: Composition
            self.compose_email(your_name, your_background)
            
            # Phase 3: Human Approval (HITL)
            approved = self.request_approval()
            
            # Phase 4: Send Email
            if approved:
                self.send_email(sender_email, app_password)
            
            print("\n" + "="*80)
            print(" Workflow completed!")
            print("="*80)
            
        except Exception as e:
            print(f"\n Workflow error: {e}")
            
        finally:
            self.cleanup()


def main():
    """Run orchestrator with .env file settings"""
    print("""
    
              PhD Email Orchestrator Agent                          
      An agentic workflow for researching and emailing professors   
      
                Using credentials from .env file
    
    """)
    
    print(f"Sender: {SENDER_EMAIL}")
    print(f"Target: {TARGET_EMAIL}")
    print(f"Your Name: {YOUR_NAME}")
    
    if OPENAI_API_KEY:
        print(f"OpenAI API: Enabled (will use GPT-4 for email generation)")
    else:
        print(f"OpenAI API: Not configured (will use template-based email)")
    
    print("\nPress Enter to start, or Ctrl+C to cancel...")
    input()
    
    # Create and run orchestrator
    orchestrator = PhDEmailOrchestrator(
        professor_name=PROFESSOR_NAME,
        test_email=TARGET_EMAIL
    )
    
    orchestrator.run(
        your_name=YOUR_NAME,
        your_background=YOUR_BACKGROUND,
        sender_email=SENDER_EMAIL,
        app_password=GMAIL_APP_PASSWORD
    )


if __name__ == "__main__":
    main()