#!/usr/bin/env python3
"""
DreamFrame Content Safety & Moderation System
Comprehensive filtering for harmful, toxic, and copyrighted content including celebrity restrictions
"""

import re
import json
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class ContentRiskLevel(Enum):
    SAFE = "safe"
    LOW_RISK = "low_risk"
    MEDIUM_RISK = "medium_risk"
    HIGH_RISK = "high_risk"
    BLOCKED = "blocked"

@dataclass
class ContentSafetyResult:
    is_safe: bool
    risk_level: ContentRiskLevel
    violations: List[str]
    filtered_prompt: str
    reason: str

class DreamFrameContentSafety:
    """Comprehensive content safety system for DreamFrame LLC"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Celebrity and public figure detection
        self.celebrity_patterns = [
            # A-list celebrities (partial list for demonstration)
            r'\b(?:brad pitt|angelina jolie|dicaprio|jennifer lawrence|tom cruise|will smith|dwayne johnson|robert downey|scarlett johansson|emma stone|ryan reynolds|jennifer aniston|george clooney|meryl streep|denzel washington|morgan freeman|samuel jackson|johnny depp|sandra bullock|julia roberts)\b',
            
            # Political figures
            r'\b(?:donald trump|joe biden|barack obama|hillary clinton|nancy pelosi|mitch mcconnell|alexandria ocasio-cortez|bernie sanders|ron desantis|kamala harris|mike pence|ted cruz|elizabeth warren)\b',
            
            # Historical figures (recent/controversial)
            r'\b(?:adolf hitler|joseph stalin|mao zedong|pol pot|idi amin|saddam hussein|osama bin laden|jeffrey epstein)\b',
            
            # Tech/Business leaders
            r'\b(?:elon musk|jeff bezos|bill gates|mark zuckerberg|tim cook|sundar pichai|satya nadella|jack dorsey|reed hastings)\b',
            
            # Generic celebrity terms
            r'\b(?:celebrity|famous person|movie star|pop star|singer|actor|actress|politician|president|prime minister|ceo|billionaire)\b',
            
            # Style/likeness patterns
            r'\b(?:looks like|similar to|in the style of|resembling|face of|appearance of)\s+[A-Z][a-z]+\s+[A-Z][a-z]+\b'
        ]
        
        # Harmful content patterns
        self.harmful_patterns = [
            # Violence and weapons
            r'\b(?:violence|violent|kill|murder|assassination|terrorist|bomb|explosion|gun|weapon|knife|sword|blood|gore|torture|abuse|assault|attack|fight|war|battle|destroy|death|dead|corpse)\b',
            
            # Adult/sexual content
            r'\b(?:nude|naked|sex|sexual|porn|erotic|adult|intimate|provocative|sensual|seductive|lingerie|underwear|bikini|swimsuit|revealing|exposed|topless|bottomless)\b',
            
            # Hate speech and discrimination
            r'\b(?:racist|racism|nazi|supremacist|hate|hatred|discrimination|prejudice|bigot|slur|offensive|derogatory|inflammatory|extremist|radical)\b',
            
            # Drugs and illegal activities
            r'\b(?:drug|cocaine|heroin|marijuana|cannabis|meth|alcohol|drunk|intoxicated|illegal|criminal|theft|robbery|fraud|scam|money laundering)\b',
            
            # Self-harm and mental health
            r'\b(?:suicide|self-harm|cutting|depression|anxiety|mental illness|overdose|addiction|substance abuse)\b',
            
            # Disturbing content
            r'\b(?:horror|scary|frightening|disturbing|creepy|nightmare|ghost|demon|evil|dark|sinister|macabre|grotesque|disgusting)\b'
        ]
        
        # Copyrighted content patterns
        self.copyright_patterns = [
            # Disney characters and properties
            r'\b(?:mickey mouse|disney|marvel|star wars|pixar|frozen|lion king|beauty and the beast|cinderella|snow white|little mermaid|aladdin|mulan|pocahontas|tangled|moana|encanto|toy story|finding nemo|incredibles|cars|monsters inc|up|wall-e|ratatouille|brave|inside out|coco|soul|luca|turning red)\b',
            
            # Warner Bros/DC
            r'\b(?:batman|superman|wonder woman|flash|aquaman|green lantern|justice league|harry potter|lord of the rings|hobbit|matrix|warner bros|dc comics)\b',
            
            # Universal/Comcast
            r'\b(?:jurassic park|fast and furious|despicable me|minions|shrek|madagascar|how to train your dragon|kung fu panda|trolls|boss baby)\b',
            
            # Sony Pictures
            r'\b(?:spider-man|spiderman|venom|ghostbusters|men in black|bad boys|resident evil|underworld|smurfs|cloudy with a chance)\b',
            
            # Paramount
            r'\b(?:transformers|mission impossible|star trek|teenage mutant ninja turtles|indiana jones|top gun)\b',
            
            # Gaming franchises
            r'\b(?:mario|luigi|zelda|pokemon|sonic|minecraft|fortnite|call of duty|grand theft auto|world of warcraft|league of legends|overwatch|apex legends)\b',
            
            # TV shows and streaming
            r'\b(?:game of thrones|breaking bad|stranger things|the office|friends|netflix|amazon prime|hulu|disney plus|hbo max|paramount plus)\b',
            
            # Music and artists
            r'\b(?:taylor swift|beyonce|drake|kanye west|ariana grande|justin bieber|rihanna|lady gaga|ed sheeran|adele|billie eilish|the weeknd|bruno mars|eminem|jay-z|kendrick lamar)\b',
            
            # Sports leagues and teams
            r'\b(?:nfl|nba|mlb|nhl|fifa|olympics|lakers|warriors|patriots|cowboys|yankees|dodgers|real madrid|barcelona|manchester united)\b'
        ]
        
        # Safe alternative suggestions
        self.safe_alternatives = {
            "celebrity": "professional model",
            "famous person": "stylish individual",
            "movie star": "elegant person",
            "looks like": "inspired by",
            "violence": "action scene",
            "fight": "dynamic movement",
            "weapon": "prop",
            "scary": "mysterious",
            "horror": "dramatic",
            "nude": "artistic portrait",
            "revealing": "fashionable"
        }
    
    def check_celebrity_content(self, prompt: str) -> Tuple[bool, List[str]]:
        """Check for celebrity or public figure references"""
        violations = []
        prompt_lower = prompt.lower()
        
        for pattern in self.celebrity_patterns:
            matches = re.findall(pattern, prompt_lower, re.IGNORECASE)
            if matches:
                violations.extend([f"Celebrity/public figure reference: {match}" for match in matches])
        
        return len(violations) > 0, violations
    
    def check_harmful_content(self, prompt: str) -> Tuple[bool, List[str]]:
        """Check for harmful, toxic, or inappropriate content"""
        violations = []
        prompt_lower = prompt.lower()
        
        for pattern in self.harmful_patterns:
            matches = re.findall(pattern, prompt_lower, re.IGNORECASE)
            if matches:
                violations.extend([f"Harmful content: {match}" for match in matches])
        
        return len(violations) > 0, violations
    
    def check_copyright_content(self, prompt: str) -> Tuple[bool, List[str]]:
        """Check for copyrighted material references"""
        violations = []
        prompt_lower = prompt.lower()
        
        for pattern in self.copyright_patterns:
            matches = re.findall(pattern, prompt_lower, re.IGNORECASE)
            if matches:
                violations.extend([f"Copyrighted content: {match}" for match in matches])
        
        return len(violations) > 0, violations
    
    def filter_and_suggest_alternatives(self, prompt: str) -> str:
        """Filter problematic content and suggest safe alternatives"""
        filtered_prompt = prompt
        
        for problematic, alternative in self.safe_alternatives.items():
            filtered_prompt = re.sub(
                r'\b' + re.escape(problematic) + r'\b',
                alternative,
                filtered_prompt,
                flags=re.IGNORECASE
            )
        
        # Remove celebrity references entirely
        for pattern in self.celebrity_patterns:
            filtered_prompt = re.sub(pattern, "[REDACTED]", filtered_prompt, flags=re.IGNORECASE)
        
        # Clean up extra spaces and formatting
        filtered_prompt = re.sub(r'\s+', ' ', filtered_prompt).strip()
        filtered_prompt = filtered_prompt.replace("[REDACTED]", "person")
        
        return filtered_prompt
    
    def assess_content_safety(self, prompt: str, user_email: str = None) -> ContentSafetyResult:
        """Comprehensive content safety assessment"""
        
        # Check all violation types
        has_celebrity, celebrity_violations = self.check_celebrity_content(prompt)
        has_harmful, harmful_violations = self.check_harmful_content(prompt)
        has_copyright, copyright_violations = self.check_copyright_content(prompt)
        
        all_violations = celebrity_violations + harmful_violations + copyright_violations
        
        # Determine risk level and safety
        if has_harmful and any("violence" in v.lower() or "weapon" in v.lower() or "hate" in v.lower() for v in harmful_violations):
            risk_level = ContentRiskLevel.BLOCKED
            is_safe = False
            reason = "Content contains harmful material that violates our safety policies"
            
        elif has_celebrity or (has_harmful and len(harmful_violations) > 2) or (has_copyright and len(copyright_violations) > 1):
            risk_level = ContentRiskLevel.HIGH_RISK
            is_safe = False
            reason = "Content contains multiple policy violations"
            
        elif has_copyright or (has_harmful and len(harmful_violations) > 0):
            risk_level = ContentRiskLevel.MEDIUM_RISK
            is_safe = False
            reason = "Content may violate copyright or safety policies"
            
        elif len(all_violations) > 0:
            risk_level = ContentRiskLevel.LOW_RISK
            is_safe = True  # Allow with filtering
            reason = "Content has minor concerns but can be filtered"
            
        else:
            risk_level = ContentRiskLevel.SAFE
            is_safe = True
            reason = "Content passes all safety checks"
        
        # Generate filtered version
        filtered_prompt = self.filter_and_suggest_alternatives(prompt) if not is_safe else prompt
        
        # Log the assessment
        self.logger.info(f"Content safety check - Risk: {risk_level.value}, Safe: {is_safe}, User: {user_email or 'anonymous'}")
        if all_violations:
            self.logger.warning(f"Content violations detected: {all_violations}")
        
        return ContentSafetyResult(
            is_safe=is_safe,
            risk_level=risk_level,
            violations=all_violations,
            filtered_prompt=filtered_prompt,
            reason=reason
        )
    
    def get_content_policy_message(self, violations: List[str]) -> str:
        """Generate user-friendly policy violation message"""
        
        if any("Celebrity" in v for v in violations):
            return "We don't create videos featuring real people or celebrities to protect privacy and prevent misuse. Try describing a general scene or character instead."
        
        if any("Harmful content" in v for v in violations):
            return "We maintain family-friendly content standards. Please revise your request to focus on positive, safe themes."
        
        if any("Copyrighted" in v for v in violations):
            return "We respect intellectual property rights. Please create original content rather than using copyrighted characters or brands."
        
        return "Your request doesn't meet our content guidelines. Please try a different creative concept."

# Initialize global content safety system
content_safety = DreamFrameContentSafety()

def validate_video_prompt(prompt: str, user_email: str = None) -> ContentSafetyResult:
    """Main function to validate video generation prompts"""
    return content_safety.assess_content_safety(prompt, user_email)

def is_content_safe_for_generation(prompt: str, user_email: str = None) -> bool:
    """Quick safety check - returns True if content can be generated"""
    result = validate_video_prompt(prompt, user_email)
    return result.is_safe and result.risk_level != ContentRiskLevel.BLOCKED

if __name__ == "__main__":
    # Test the content safety system
    test_prompts = [
        "A beautiful sunset over calm waters",  # Safe
        "Taylor Swift singing on stage",  # Celebrity violation
        "A person dancing in a park",  # Safe
        "Mickey Mouse at Disneyland",  # Copyright violation
        "A violent fight scene with weapons",  # Harmful content
        "Professional model in elegant dress",  # Safe
        "Someone who looks like Brad Pitt",  # Celebrity likeness
    ]
    
    print("🛡️ DREAMFRAME CONTENT SAFETY TESTING")
    print("=" * 50)
    
    for i, prompt in enumerate(test_prompts, 1):
        result = validate_video_prompt(prompt, "test@dreamframe.com")
        
        print(f"\nTest {i}: {prompt}")
        print(f"Safe: {result.is_safe}")
        print(f"Risk Level: {result.risk_level.value}")
        print(f"Violations: {result.violations}")
        print(f"Filtered: {result.filtered_prompt}")
        print(f"Reason: {result.reason}")
        print("-" * 30)