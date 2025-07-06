import json
from datetime import datetime
from utils import initialize_gemini 

def passgen(user_input: str) -> str:

    print("🤖 Hyper-Realistic PassGen Agent (AI Mode) running...")

    try:
        model = initialize_gemini()
    except Exception as e:
        return str(e)

    prompt = f"""
        [PERSONA]
        You are a world-class expert in social engineering and password profiling. You have deep knowledge of how an average, non-technical person creates passwords.

        [CORE PHILOSOPHY: REALISTIC PATTERNS, NOT RANDOM COMPLEXITY]
        Your primary goal is realism. Most people are not security experts. They create passwords that are easy for *them* to remember by reusing a few key pieces of information.
        **KEY RULE: People use special characters sparingly.** A password like `Ayse1995!` or `berk.kucuk` is far more common and likely than `Ays*e!19.95_`. Your goal is to explore all combinations of *these simple, human-like patterns*.

        [PRIMARY TASK]
        Your main goal is to analyze the user-provided information and **exhaustively generate the maximum possible number of unique password combinations** based on the realistic, human-like tiers below. Finally, you will **filter the complete list** based on the user's specified length constraints.

        [CRITICAL INSTRUCTION: NO LEETSPEAK]
        You are strictly forbidden from using 'leetspeak' substitutions (e.g., 'a' -> '@', 'e' -> '3'). All passwords must use standard alphabetical characters and numbers.

        [GENERATION METHODOLOGY: REALISTIC HUMAN-LIKE TIERS]
        First, extract all personal details and infer related data (e.g., for 'trabzonspor', infer 'trabzon', '61', '1967'). Then, generate all possible passwords based on the following tiers, from most common to less common.

        - **Tier 1: The Foundation - Most Common Patterns (No Special Characters):**
          This is the most important tier. Generate all possible combinations here.
          - Simple concatenations of keywords, names, and significant numbers (birth year, plate code, etc.).
          - A single capital letter at the start of names is very common.
          - Examples: `berk2001`, `Berk2001`, `trabzon61`, `berkkucuk61`, `berkkucuk`, `Berkkucuk`, `kucukberk`.

        - **Tier 2: The "One Special Thing" Rule:**
          Take patterns from Tier 1 and apply only ONE of the following realistic complexities.
          - **A) Add a Single Suffix:** Add ONE common special character (`!`, `?`, `*`) or a simple number (`1`, `123`) to the end. Examples: `Berk2001!`, `trabzon61?`, `berkkucuk123`.
          - **B) Use a Single Separator:** Join two keywords with a SINGLE common separator (`.` or `_`). Examples: `berkkucuk.61`, `trabzon_1967`, `berk.2001`.
          - **Crucially, do not combine these in this tier.** A password like `berk.kucuk!` is less common and belongs in the next tier.

        - **Tier 3: Limited Combined Complexity (Less Common Patterns):**
          Generate variations by combining the simple complexities from the tiers above.
          - A capitalized name, a number, and a separator. (e.g., `Berk.2001`, `Kucuk_61`)
          - A capitalized name, a number, and a final special character. (e.g., `Trabzon1967`)
          - Two names with a separator and a final special character. (e.g., `berk.kucuk61`)

        [CRITICAL INSTRUCTION: LENGTH FILTERING]
        After generating the exhaustive list, you MUST strictly filter it. Only include passwords in the final JSON output that meet the min/max length criteria from the user's request.

        [OUTPUT FORMAT]
        Your final output MUST be a single, valid JSON object with one key, "passwords", containing the **filtered** array of strings. Do not include any explanations or markdown.

        [CURRENT TASK]
        Apply this entire process to the following user request:
        "{user_input}"
    """

    try:
        print("Requesting hyper-realistic password combinations from AI...")
        response = model.generate_content(prompt)
        
        response_text = response.text.strip()
        clean_text = response_text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        
        data = json.loads(clean_text)
        password_list = data.get("passwords", [])

        if not password_list:
            return "AI could not generate a wordlist with the provided info and constraints. Please change the details or length range."

    except json.JSONDecodeError:
        return f"Error: Response from AI is not valid JSON. Response: {response.text}"
    except Exception as e:
        return f"Error: An issue occurred while communicating with the AI: {e}"

    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"wordlists/wordlist_{timestamp}.txt"
        
        with open(filename, "w", encoding="utf-8") as f:
            for password in password_list:
                f.write(f"{password}\n")
        
        success_message = f"Success! {len(password_list)} potential passwords generated and saved to '{filename}'."
        print(success_message)
        return success_message
        
    except Exception as e:
        return f"Error: An issue occurred while writing to the file: {e}"