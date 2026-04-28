import cohere
import re
import json
from src.core.config import API_KEY
from src.core.prompts import SYSTEM_PROMPT


class CareerAnalyzer:
    def __init__(self):
        self.co = cohere.Client(API_KEY)

    def _call_cohere(self, message, preamble):
        try:
            response = self.co.chat(
                message=message,
                preamble=preamble,
                model="command-r-plus-08-2024"
            )
            return response.text.strip()
        except Exception as e:
            return f"Cohere Error: {str(e)}"

    def analyze_resume(self, resume_text, target_role):
         prompt = f"""
                     You are a brutally honest AI career coach.
                     
                     Compare the resume against the target role and identify REAL gaps.
                     
                     Target Role:
                     {target_role}
                     
                     Resume:
                     {resume_text[:4000]}

                     Rules:
                    - ALWAYS list at least 3 gaps
                    - Even small weaknesses count as gaps
                    - Be specific (tools, skills, experience)
                    - No generic statements
                     
                     Instructions:
                     - DO NOT be polite or generic
                     - ALWAYS list at least 3 specific gaps
                     - Gaps must be skills, tools, or experience missing compared to the role
                     - If a skill is weak, still count it as a gap
                     - Be specific (e.g., "Lacks AWS deployment experience", not "Needs improvement")
                     
                     Output format EXACTLY:
                     
                     **Strengths:**
                     - ...
                     
                     **Gaps:**
                     - ...
                     - ...
                     - ...
                     
                     **X-Factor Project:**
                    - Suggest ONE specific, practical project aligned with missing skills
                    """
         return self._call_cohere(prompt, SYSTEM_PROMPT)
    def rewrite_resume(self, resume_text):
        prompt = f"""Rewrite KEY experience bullets using STAR method 
(Situation-Task-Action-Result). Keep same length:

{resume_text[:2000]}"""
        preamble = "Expert resume writer. Use strong action verbs and measurable impact."
        return self._call_cohere(prompt, preamble)

    def get_skill_scores(self, resume_text, target_role):
        prompt = f"""Resume: {resume_text[:2000]}
Target Role: {target_role}

Give scores from 0 to 100 for:
Technical, Communication, Leadership, Problem Solving, Creativity.

Return ONLY JSON like:
{{"Technical": 85, "Communication": 70, "Leadership": 60, "Problem Solving": 75, "Creativity": 65}}
"""

        raw = self._call_cohere(
            prompt,
            "You are a JSON generator. Return ONLY valid JSON."
        )

        # --- PRIMARY: JSON PARSE ---
        try:
            scores = json.loads(raw)

            return {
                "Technical": int(scores.get("Technical", 50)),
                "Communication": int(scores.get("Communication", 50)),
                "Leadership": int(scores.get("Leadership", 50)),
                "Problem Solving": int(scores.get("Problem Solving", scores.get("Problem-Solving", 50))),
                "Creativity": int(scores.get("Creativity", 50)),
            }

        except:
            # --- FALLBACK: REGEX ---
            scores = {
                "Technical": 50,
                "Communication": 50,
                "Leadership": 50,
                "Problem Solving": 50,
                "Creativity": 50
            }

            for line in raw.split("\n"):
                match = re.search(r"([\w\s]+):\s*(\d+)", line)
                if match:
                    key = match.group(1).strip()
                    val = int(match.group(2))

                    if key in scores:
                        scores[key] = max(0, min(100, val))

            return scores