# osintai.py (Çok Dilli Raporlama için Güncellenmiş - Tam Versiyon)

import os
import json
import time
import subprocess
from datetime import datetime
from bs4 import BeautifulSoup
from googlesearch import search
from utils import initialize_gemini, check_tool_installed

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException, NoSuchElementException


def get_webdriver():

    try:
        from selenium.webdriver.chrome.options import Options
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        driver = webdriver.Chrome(options=chrome_options)
        print("Chrome driver launched successfully.")
        return driver
    except WebDriverException:
        print("Chrome not found or failed, trying Firefox...")

    try:
        from selenium.webdriver.firefox.options import Options
        firefox_options = Options()
        firefox_options.add_argument("-headless")
        driver = webdriver.Firefox(options=firefox_options)
        print("Firefox driver launched successfully.")
        return driver
    except WebDriverException:
        print("Firefox not found or failed.")
    
    return None

def extract_entities_with_ai(user_input, model):
    print("AI extracting key entities from request...")
    prompt = f"""
        [TASK]
        You are an information extraction system. From the user's request, extract the following entities: a probable username, the person's full name, and any other descriptive keywords (like profession, city, hobbies).

        [OUTPUT FORMAT]
        Your response MUST be a single, valid JSON object with the keys "username", "full_name", and "keywords" (which should be a list of strings).

        [USER REQUEST]
        "{user_input}"

        [YOUR JSON RESPONSE]
    """
    try:
        response = model.generate_content(prompt)
        clean_text = response.text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        entities = json.loads(clean_text)
        print(f"Entities extracted: {entities}")
        return entities
    except Exception as e:
        print(f"Could not extract entities: {e}")
        return None

def verify_profile_existence_with_selenium(url, model):
    print(f"  Verifying URL with Selenium: {url}")
    driver = get_webdriver()
    if not driver:
        print("    -> No compatible browser (Chrome, Firefox) found. Skipping verification.")
        return "NO_BROWSER_FOUND"

    try:
        driver.get(url)
        time.sleep(5) 

        common_accept_texts = ["Accept", "Allow all", "Agree", "Kabul Et", "Onayla"]
        for text in common_accept_texts:
            try:
                button_xpath = f"//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text.lower()}')]"
                accept_button = driver.find_element(By.XPATH, button_xpath)
                if accept_button.is_displayed() and accept_button.is_enabled():
                    print(f"    -> Found and clicked a consent button with text containing '{text}'")
                    accept_button.click()
                    time.sleep(2)
                    break
            except NoSuchElementException:
                pass
        
        page_source = driver.page_source
        
    except Exception as e:
        print(f"    -> Selenium error navigating or interacting with page: {e}. Discarding.")
        return "SELENIUM_ERROR"
    finally:
        if driver:
            driver.quit()

    try:
        soup = BeautifulSoup(page_source, 'html.parser')
        page_text = soup.get_text(separator=' ', strip=True)
        if not page_text:
            return "NO_TEXT_FOUND"
        
        try:
            safe_filename_part = url.split('//')[-1].replace('/', '_').replace('?', '_').replace('=', '')
            debug_filename = f"osints/debug/debug_{safe_filename_part[:50]}.txt"
            with open(debug_filename, "w", encoding="utf-8") as f:
                f.write(f"URL: {url}\n\n")
                f.write(page_text)
            print(f"    -> Page content saved to '{debug_filename}' for debugging.")
        except Exception as e:
            print(f"    -> Could not write debug file: {e}")

        truncated_text = page_text[:4000]

        verification_prompt = f"""
            [TASK]
            You are a highly precise web content classifier. Your task is to analyze the provided text from a webpage and distinguish between a specific user's public profile page and a generic portal, login, or error page.

            [CONTEXT & RULES]
            - A `VALID_PROFILE` contains specific, personal details like the user's name repeated in the content, a biography ('About Me'), a list of projects or posts, follower counts, or a join date.
            - A `NOT_FOUND` page contains explicit error messages like 'page not found', 'profile is private', 'user does not exist', 'This account doesn’t exist'.
            - A `GENERIC_ERROR` is a valid page but NOT a user profile. This includes login screens, cookie consent walls, main homepages, or 'search for other users' pages. Look for general phrases like 'Log In', 'Sign Up', 'Find Talent', 'This site uses cookies', 'Join now to see'.

            [PAGE TEXT TO ANALYZE]
            "{truncated_text}"

            [YOUR RESPONSE]
            Respond with ONLY one of the following keywords: VALID_PROFILE, NOT_FOUND, GENERIC_ERROR
        """
        ai_response = model.generate_content(verification_prompt)
        status = ai_response.text.strip().upper()
        print(f"    -> AI Verification Status: {status}")
        return status
    except Exception as e:
        print(f"    -> An unknown error occurred during AI analysis: {e}")
        return "UNKNOWN_ERROR"

def run_social_analyzer(username):
    if not username: return None
    print(f"Running social-analyzer for username: '{username}'...")
    try:
        command = ["social-analyzer", "--username", username, "--output", "json"]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        stdout_data, stderr_data = process.communicate()
        if process.returncode != 0: raise subprocess.CalledProcessError(process.returncode, command, output=stdout_data, stderr=stderr_data)
        return json.loads(stdout_data)
    except Exception as e:
        print(f"Failed to run social-analyzer: {e}")
        return None

def run_google_dorks(full_name, keywords, num_results=10):
    if not full_name: return None
    print(f"Running Google Dorks for query: '{full_name}' with keywords: {keywords}...")
    queries = [f'"{full_name}"']
    if keywords:
        queries.append(f'"{full_name}" {" ".join(keywords)}')
        queries.append(f'"{full_name}" filetype:pdf OR filetype:doc OR filetype:docx')
    all_urls = []
    try:
        for query in queries:
            print(f"  Searching for: {query}")
            results = search(query, num_results=num_results, lang='en')
            all_urls.extend(list(results))
        return list(set(all_urls))
    except Exception as e:
        print(f"Google Dorking failed: {e}")
        return None

def analyze_fused_data_with_ai(user_input, verified_data, keywords, model, language_code: str):
    print(f"AI analyzing verified data and generating final intelligence profile in language: {language_code}...")

    LANG_MAP = {
        "en": "English",
        "tr": "Turkish (Türkçe)",
        "ru": "Russian (Русский)"
    }
    language_name = LANG_MAP.get(language_code, "English") 

    prompt = f"""
        [REPORT LANGUAGE]
        You MUST produce the entire report in the following language: **{language_name}**. 
        All headers, analyses, and summaries must be written strictly in {language_name}.

        [PERSONA]
        You are a senior intelligence analyst and a meticulous investigative journalist. Your guiding principle is "Evidence First." You don't just state facts; you back up every single claim with a verifiable source link. Your goal is maximum detail and transparency, not brevity.

        [PRIMARY TASK]
        Your mission is to produce an exhaustive intelligence profile based on all the data provided below.
        1.  **Synthesize ALL data points.** Do not omit details. Your report must be comprehensive.
        2.  **Correlate information.** Explicitly state connections between different accounts (e.g., "The GitHub profile bio directly matches the Freelancer profile description, indicating high confidence.").
        3.  **Provide Direct Evidence.** For every profile, document, or piece of information you mention, you MUST include the source link directly in the report.
        4.  **Incorporate initial keywords** into your analysis to ensure the report is relevant to the user's original query.

        [INITIAL CONTEXT]
        - Original User Request: "{user_input}"
        - Extracted Keywords for focus: {keywords}

        [VERIFIED OSINT DATA]
        This is a list of URLs that have been confirmed to be valid and existing profiles or documents related to the target.
        {json.dumps(verified_data, indent=2, ensure_ascii=False)}

        [MANDATORY REPORT STRUCTURE & INSTRUCTIONS]
        Produce your report using the following Markdown structure. Be as detailed as possible in each section.

        # Intelligence Profile: [Target's Inferred Full Name]

        ## 1. Executive Summary
        A brief, one-paragraph overview of the target's digital identity, primary activities, and key characteristics based on the verified evidence.

        ## 2. Detailed Findings & Evidence
        This is the core of the report. Go through every verified link. **Do not summarize links; cite them and analyze their content.**

        ### 2.1. Verified Professional & Technical Profiles
        Analyze profiles from professional sites like GitHub, Freelancer, Habr, LinkedIn, etc. Detail their stated skills, bio, projects, and services.
        - **GitHub Profile:** [URL]
          - **Analysis:** [Detailed analysis of bio, pinned repos, languages, contributions...]
        - **Freelancer Profile:** [URL]
          - **Analysis:** [Detailed analysis of offered services, reviews, work history...]

        ### 2.2. Verified Social Media Presence
        Analyze confirmed accounts from platforms like Facebook, Instagram, Twitter, VK, Reddit, etc.
        - **Platform:** Instagram
          - **URL:** [URL]
          - **Analysis:** [Description of the profile, type of content posted, follower/following count, any links in bio...]
        - **Platform:** Twitter
          - **URL:** [URL]
          - **Analysis:** [Similar detailed analysis...]

        ### 2.3. Verified Public Documents & Footprints
        List and analyze all relevant documents, articles, and public posts found via Google Dorking.
        - **Document/Link:** [URL]
          - **Type:** [e.g., CV, Research Paper, Forum Post]
          - **Analysis:** [Summary of the document's content and its relevance to the target's profile.]

        ## 3. Analyst's Assessment & Conclusion
        This is your final professional opinion.
        - **Synthesize:** Weave the findings together into a coherent narrative about the target's digital persona and expertise.
        - **Identify Inconsistencies:** Note any contradictions in the data.
        - **Actionable Intelligence:** What are the key takeaways? What does this footprint mean?
        - **Next Steps:** Suggest specific, actionable steps for a deeper investigation.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Final analysis by AI failed: {e}"

def osint(user_input: str, language_code: str = "en") -> str:
    try:
        model = initialize_gemini()
        if not check_tool_installed("social-analyzer"):
            return "Error: 'social-analyzer' is not installed. Please run 'pip3 install social-analyzer'."
    except Exception as e:
        return str(e)

    entities = extract_entities_with_ai(user_input, model)
    if not entities: return "Error: Could not understand the initial request."

    target_username = entities.get("username")
    target_name = entities.get("full_name")
    target_keywords = entities.get("keywords")

    social_results = run_social_analyzer(target_username)
    google_results = run_google_dorks(target_name, target_keywords)

    candidate_urls = []
    if social_results and social_results.get("detected"):
        for item in social_results["detected"]:
            if item.get("link"):
                candidate_urls.append(item.get("link"))
    if google_results:
        candidate_urls.extend(google_results)
    
    unique_urls = list(set(filter(None, candidate_urls)))
    
    if not unique_urls:
        return "Info: No potential profiles or links found for the target."

    print(f"\nStarting verification for {len(unique_urls)} unique URLs using Selenium...")
    verified_data = []
    for url in unique_urls:
        status = verify_profile_existence_with_selenium(url, model)
        if status == 'VALID_PROFILE':
            verified_data.append({"url": url, "verification_status": "Confirmed_Profile"})
    
    if not verified_data:
        return "Info: All potential links were checked, but no confirmed profiles were found."

    final_report = analyze_fused_data_with_ai(user_input, verified_data, target_keywords, model, language_code)

    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_username = "".join(c for c in (target_username or 'report') if c.isalnum() or c in ('_', '-')).rstrip()
        filename = f"osints/OSINT_Report_{safe_username}_{timestamp}.md" # Dosya uzantısı .md olarak değiştirildi
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(final_report)
        
        success_message = f"Success! A detailed, VERIFIED analysis report has been generated and saved to '{filename}'."
        print(success_message)
        return final_report
        
    except Exception as e:
        return f"Error: Could not write the final report to a file: {e}"