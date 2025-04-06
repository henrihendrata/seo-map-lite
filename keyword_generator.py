import random
import os
import json
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
from urllib.parse import quote_plus

# Import OpenAI if available
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    class OpenAI:  # Dummy class to prevent LSP errors
        def __init__(self, api_key=None):
            pass

# Import Google Gemini if available
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Check if Google Search API is available
GOOGLE_SEARCH_AVAILABLE = os.environ.get("GOOGLE_SEARCH_API_KEY") and os.environ.get("GOOGLE_SEARCH_CX")

# Initialize Gemini API if API key is available
def initialize_gemini():
    """Initialize Gemini API with API key if available."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key and GEMINI_AVAILABLE:
        # Using Google's generative AI library
        genai.configure(api_key=api_key)
        return True
    return False

def test_gemini_connection():
    """Test the Gemini API connection."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {"success": False, "message": "No Gemini API key provided"}
    
    if GEMINI_AVAILABLE:
        try:
            # Method 1: Using Google's generative AI library
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.0-flash')
            response = model.generate_content("Test connection to Gemini API")
            return {"success": True, "message": "Successfully connected to Gemini API"}
        except Exception as e:
            # Check if the error is related to rate limiting (quota exceeded)
            error_str = str(e).lower()
            if "429" in error_str or "quota" in error_str or "rate limit" in error_str or "resource exhausted" in error_str:
                return {"success": True, "message": "Connected to Gemini API, but quota limit reached. Your API key is valid but you may need to wait before making more requests."}
                
            try:
                # Method 2: Using direct API URL for Gemini 2.0 Flash as requested
                endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
                headers = {"Content-Type": "application/json"}
                data = {
                    "contents": [{"parts": [{"text": "Test connection to Gemini API"}]}]
                }
                response = requests.post(endpoint, headers=headers, json=data)
                
                if response.status_code == 200:
                    return {"success": True, "message": "Successfully connected to Gemini API (using direct endpoint)"}
                elif response.status_code == 429:
                    return {"success": True, "message": "Connected to Gemini API, but quota limit reached. Your API key is valid but you may need to wait before making more requests."}
                else:
                    return {"success": False, "message": f"Failed to connect to Gemini API endpoint: HTTP {response.status_code} - {response.text[:100]}..."}
            except Exception as e2:
                return {"success": False, "message": f"Failed to connect to Gemini API: {str(e)[:100]}..., Direct endpoint error: {str(e2)[:100]}..."}
    else:
        return {"success": False, "message": "Google Generative AI package not available"}

def test_openai_connection():
    """Test the OpenAI API connection."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return {"success": False, "message": "No OpenAI API key provided"}
    
    if OPENAI_AVAILABLE:
        try:
            client = OpenAI(api_key=api_key)
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a test assistant."},
                    {"role": "user", "content": "This is a test message to check connection."}
                ],
                max_tokens=10
            )
            return {"success": True, "message": "Successfully connected to OpenAI API"}
        except Exception as e:
            error_str = str(e).lower()
            # Check if the error is related to rate limiting or quota
            if "429" in error_str or "quota" in error_str or "rate limit" in error_str or "capacity" in error_str:
                return {"success": True, "message": "Connected to OpenAI API, but rate limit or quota reached. Your API key is valid but you may need to wait before making more requests."}
            # Check if the error is related to authentication
            elif "auth" in error_str or "key" in error_str or "invalid" in error_str:
                return {"success": False, "message": f"Authentication error: {str(e)[:100]}..."}
            else:
                return {"success": False, "message": f"Failed to connect to OpenAI API: {str(e)[:100]}..."}
    else:
        return {"success": False, "message": "OpenAI package not available"}

def generate_title_with_gemini_endpoint(keyword: str, intent: str, custom_prompt: str = "") -> str:
    """Generate an SEO-friendly title using Google's Gemini API with direct endpoint."""
    try:
        # Check if API key is available
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return ""
        
        # Create base instruction
        base_instruction = f"Generate one SEO-friendly article title for the keyword '{keyword}'."
        
        # Include custom prompt if available
        if custom_prompt:
            prompt = f"{base_instruction} {custom_prompt}. Make it compelling and optimized for search. Return just the title with no explanation."
        else:
            # Use standard intent-based prompts
            if intent == "Informational":
                prompt = f"Generate one SEO-friendly, informational/educational article title for the keyword '{keyword}'. Make it compelling and optimized for search. Return just the title with no explanation."
            elif intent == "Commercial":
                prompt = f"Generate one SEO-friendly, commercial/purchase-oriented article title for the keyword '{keyword}'. Make it compelling and optimized for search. Return just the title with no explanation."
            else:  # Navigational
                prompt = f"Generate one SEO-friendly, navigational/resource-oriented article title for the keyword '{keyword}'. Make it compelling and optimized for search. Return just the title with no explanation."
        
        # Make the API call using direct endpoint for Gemini 2.0 Flash
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        
        response = requests.post(endpoint, headers=headers, json=data)
        
        if response.status_code == 200:
            try:
                response_json = response.json()
                if "candidates" in response_json and len(response_json["candidates"]) > 0:
                    candidate = response_json["candidates"][0]
                    if "content" in candidate and "parts" in candidate["content"]:
                        for part in candidate["content"]["parts"]:
                            if "text" in part:
                                title = part["text"].strip()
                                # Remove any quotes that might be in the response
                                title = title.strip('"\'')
                                return title if title else ""
            except Exception as e:
                print(f"Error parsing Gemini API response: {e}")
        else:
            print(f"Gemini API returned status code {response.status_code}: {response.text}")
        
        return ""
            
    except Exception as e:
        print(f"Error generating title with Gemini endpoint: {e}")
        return ""

def generate_title_with_gemini(keyword: str, intent: str, custom_prompt: str = "") -> str:
    """Generate an SEO-friendly title using Google's Gemini API."""
    try:
        # First try the direct endpoint approach
        title = generate_title_with_gemini_endpoint(keyword, intent, custom_prompt)
        if title:
            return title
            
        # If direct endpoint fails, try the standard library approach
        # Check if API key is available and initialize
        if not initialize_gemini():
            return ""
        
        # Create base instruction
        base_instruction = f"Generate one SEO-friendly article title for the keyword '{keyword}'."
        
        # Include custom prompt if available
        if custom_prompt:
            prompt = f"{base_instruction} {custom_prompt}. Make it compelling and optimized for search. Return just the title with no explanation."
        else:
            # Use standard intent-based prompts
            if intent == "Informational":
                prompt = f"Generate one SEO-friendly, informational/educational article title for the keyword '{keyword}'. Make it compelling and optimized for search. Return just the title with no explanation."
            elif intent == "Commercial":
                prompt = f"Generate one SEO-friendly, commercial/purchase-oriented article title for the keyword '{keyword}'. Make it compelling and optimized for search. Return just the title with no explanation."
            else:  # Navigational
                prompt = f"Generate one SEO-friendly, navigational/resource-oriented article title for the keyword '{keyword}'. Make it compelling and optimized for search. Return just the title with no explanation."
        
        # Make the API call using Gemini 2.0 Flash
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        
        # Get the title from the response
        if response and response.text:
            title = response.text.strip()
            # Remove any quotes that might be in the response
            title = title.strip('"\'')
            return title if title else ""
        return ""
            
    except Exception as e:
        print(f"Error generating title with Gemini: {e}")
        return ""

def determine_intent_with_gemini(keyword: str) -> Optional[str]:
    """Determine the intent for a keyword using Google's Gemini API."""
    try:
        # Check if API key is available and initialize
        if not initialize_gemini():
            return None
        
        # Create prompt
        prompt = f"""Analyze the search intent for the keyword: '{keyword}'
        Classify it as one of the following:
        - Commercial: The user wants to buy something or compare products/services
        - Informational: The user wants to learn or find information
        - Navigational: The user wants to find a specific website or resource
        
        Return ONLY the intent category as a single word with no explanation."""
        
        # Make the API call using Gemini-Flash
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        
        # Parse the response
        if response and response.text:
            result = response.text.strip()
            
            # Make sure the result is one of our expected categories
            if "commercial" in result.lower():
                return "Commercial"
            elif "navigational" in result.lower():
                return "Navigational"
            elif "informational" in result.lower():
                return "Informational"
        return None
            
    except Exception as e:
        print(f"Error determining intent with Gemini: {e}")
        return None

def generate_related_keywords_with_gemini(keyword: str, intent: str) -> List[str]:
    """Generate related keywords using Google's Gemini API."""
    try:
        # Check if API key is available and initialize
        if not initialize_gemini():
            return []
        
        # Create appropriate prompt based on intent
        if intent == "Informational":
            prompt = f"Generate 10 informational search keywords related to '{keyword}'. Focus on educational, how-to, and learning-oriented keywords. Format as a comma-separated list."
        elif intent == "Commercial":
            prompt = f"Generate 10 commercial/transactional search keywords related to '{keyword}'. Focus on buying, product reviews, and service-oriented keywords. Format as a comma-separated list."
        else:  # Navigational
            prompt = f"Generate 10 navigational search keywords related to '{keyword}'. Focus on brand-specific, website, app, login, and portal-related keywords. Format as a comma-separated list."
        
        # Make the API call using Gemini-Flash
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        
        # Parse the response
        if response and response.text:
            # Split by commas and clean up the keywords
            keywords = [k.strip() for k in response.text.split(',') if k.strip()]
            return keywords[:10]  # Limit to 10 keywords
        return []
            
    except Exception as e:
        print(f"Error generating keywords with Gemini: {e}")
        return []

def generate_competitors_with_gemini(keyword: str) -> List[Dict[str, str]]:
    """Generate more realistic competitor data using Google's Gemini API."""
    try:
        # Check if API key is available and initialize
        if not initialize_gemini():
            return []
        
        # Create prompt
        prompt = f"""Generate 3 realistic competitor article titles and URLs for the keyword: '{keyword}'.
        Format your response as:
        
        Title 1: [Title]
        URL 1: [URL]
        
        Title 2: [Title]
        URL 2: [URL]
        
        Title 3: [Title]
        URL 3: [URL]
        
        Make URLs look realistic with relevant domains and URL structures."""
        
        # Make the API call using Gemini-Flash
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        
        # Parse the response
        if response and response.text:
            text = response.text
            competitors = []
            lines = text.split("\n")
            
            title = ""
            url = ""
            
            for line in lines:
                line = line.strip()
                if line.startswith("Title") and ":" in line:
                    title = line.split(":", 1)[1].strip()
                elif line.startswith("URL") and ":" in line:
                    url = line.split(":", 1)[1].strip()
                    if title and url:
                        competitors.append({"title": title, "url": url})
                        title = ""
                        url = ""
            
            return competitors[:3]  # Ensure we get max 3 competitors
        return []
            
    except Exception as e:
        print(f"Error generating competitors with Gemini: {e}")
        return []

# Intent categories
INTENTS = ["Commercial", "Informational", "Navigational"]

# Common modifiers to generate keyword variations
INFORMATIONAL_MODIFIERS = [
    "what is", "how to", "guide", "tutorial", "tips for", "best practices", 
    "examples of", "understanding", "learn", "beginner's guide to", "advanced",
    "complete guide", "definition", "explained", "overview", "benefits of",
    "history of", "types of", "comparison", "vs", "difference between"
]

COMMERCIAL_MODIFIERS = [
    "best", "top", "buy", "cheap", "affordable", "premium", "review", "price",
    "cost of", "for sale", "deal", "discount", "professional", "services",
    "near me", "online", "shop", "purchase", "hire", "agency", "software",
    "tools", "platform"
]

NAVIGATIONAL_MODIFIERS = [
    "login", "sign up", "download", "app", "website", "official", "customer service",
    "contact", "support", "dashboard", "account", "register", "free trial", "demo",
    "forum"
]

# Common domains for mock competitor URLs
DOMAINS = [
    "example.com", "seosite.com", "digitalmarketer.com", "wordstream.com", 
    "semrush.com", "ahrefs.com", "moz.com", "searchenginejournal.com", 
    "backlinko.com", "neilpatel.com", "hubspot.com", "seoroundtable.com",
    "searchengineland.com", "contentmarketinginstitute.com", "bloggingwizard.com"
]

def generate_title_with_openai(keyword: str, intent: str, custom_prompt: str = "") -> str:
    """Generate an SEO-friendly title using OpenAI."""
    try:
        # Check if API key is available
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return ""
        
        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)
        
        # Create prompt based on intent and custom prompt if available
        base_instruction = f"Generate one SEO-friendly article title for the keyword '{keyword}'."
        
        if custom_prompt:
            # Include custom prompt in the instruction
            prompt = f"{base_instruction} {custom_prompt}. Make it compelling and optimized for search. Return just the title with no explanation."
        else:
            # Use standard intent-based prompts
            if intent == "Informational":
                prompt = f"Generate one SEO-friendly, informational/educational article title for the keyword '{keyword}'. Make it compelling and optimized for search. Return just the title with no explanation."
            elif intent == "Commercial":
                prompt = f"Generate one SEO-friendly, commercial/purchase-oriented article title for the keyword '{keyword}'. Make it compelling and optimized for search. Return just the title with no explanation."
            else:  # Navigational
                prompt = f"Generate one SEO-friendly, navigational/resource-oriented article title for the keyword '{keyword}'. Make it compelling and optimized for search. Return just the title with no explanation."
        
        # Make the API call
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert SEO copywriter that creates compelling article titles."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100
        )
        
        # Get the title from the response
        title = response.choices[0].message.content.strip()
        # Remove any quotes that might be in the response
        title = title.strip('"\'')
        
        return title if title else ""
            
    except Exception as e:
        print(f"Error generating title with OpenAI: {e}")
        return ""

def generate_title(keyword: str, intent: str, custom_prompt: str = "") -> str:
    """Generate an SEO-friendly title for a keyword based on its intent."""
    generated_title = ""
    
    # Try to use OpenAI if available
    if OPENAI_AVAILABLE and os.environ.get("OPENAI_API_KEY"):
        openai_title = generate_title_with_openai(keyword, intent, custom_prompt)
        if openai_title:
            return openai_title  # Return the AI-generated title
    
    # Try to use Gemini if available
    if GEMINI_AVAILABLE and os.environ.get("GEMINI_API_KEY"):
        # Pass the custom prompt to Gemini title generator
        gemini_title = generate_title_with_gemini(keyword, intent, custom_prompt)
        if gemini_title:
            return gemini_title  # Return the AI-generated title
    
    # If there's a custom prompt but no AI was able to use it, create a smart template-based title
    if custom_prompt:
        # Check for common custom prompt patterns and try to incorporate them
        use_numbers = any(term in custom_prompt.lower() for term in ["number", "numbered", "use number", "add number"])
        formal_tone = any(term in custom_prompt.lower() for term in ["formal", "professional", "formal tone"])
        
        # Create a better fallback title that respects the custom prompt where possible
        if intent == "Informational":
            if use_numbers:
                templates = [
                    f"10 Essential {keyword.title()} Tips You Should Know",
                    f"7 Important Facts About {keyword.title()} for Beginners",
                    f"5 Step-by-Step Methods to Master {keyword.title()}",
                    f"8 Key Concepts of {keyword.title()} Explained"
                ]
            elif formal_tone:
                templates = [
                    f"A Comprehensive Analysis of {keyword.title()} Methodologies",
                    f"The Definitive Guide to {keyword.title()}: Professional Insights",
                    f"{keyword.title()}: A Thorough Examination of Principles and Applications",
                    f"Understanding the Fundamentals of {keyword.title()}: An In-depth Overview"
                ]
            else:
                templates = [
                    f"The Ultimate Guide to {keyword.title()}: Everything You Need to Know",
                    f"How to {keyword.title()}: A Complete Step-by-Step Guide",
                    f"{keyword.title()} 101: Essential Tips and Techniques",
                    f"Understanding {keyword.title()}: A Comprehensive Overview"
                ]
        elif intent == "Commercial":
            if use_numbers:
                templates = [
                    f"Top 10 {keyword.title()} Products to Buy in {datetime.now().year}",
                    f"5 Best {keyword.title()} Options for Every Budget",
                    f"7 {keyword.title()} Products Professional Reviewers Recommend",
                    f"8 Premium {keyword.title()} Solutions Worth Your Investment"
                ]
            elif formal_tone:
                templates = [
                    f"A Comparative Analysis of Premium {keyword.title()} Products",
                    f"Professional Review: Selected {keyword.title()} Solutions for Discerning Buyers",
                    f"Investment Considerations: Superior {keyword.title()} Options Available",
                    f"An Objective Assessment of Leading {keyword.title()} Products"
                ]
            else:
                templates = [
                    f"The Best {keyword.title()} Reviews: Ultimate Buyer's Guide",
                    f"{keyword.title()}: Top Options Compared",
                    f"Best {keyword.title()} Products: Reviews and Comparisons",
                    f"How to Choose the Right {keyword.title()} for Your Needs"
                ]
        else:  # Navigational
            if use_numbers:
                templates = [
                    f"5 Essential {keyword.title()} Resources You Need to Bookmark",
                    f"10 Official {keyword.title()} Platforms to Access Information",
                    f"7 Best Ways to Navigate {keyword.title()} Successfully",
                    f"3 Direct Pathways to Access {keyword.title()} Resources"
                ]
            elif formal_tone:
                templates = [
                    f"Professional Guide to Accessing {keyword.title()} Resources",
                    f"An Index of Authoritative {keyword.title()} Platforms",
                    f"Navigational Framework for {keyword.title()} Information Access",
                    f"A Structured Approach to Finding {keyword.title()} Resources"
                ]
            else:
                templates = [
                    f"Official {keyword.title()} Resources: Where to Find What You Need",
                    f"How to Access {keyword.title()}: A Quick Reference Guide",
                    f"Navigate {keyword.title()} Like a Pro: Essential Links",
                    f"{keyword.title()} Directory: Top Sites and Resources"
                ]
        
        return random.choice(templates)
    
    # No custom prompt or AI, use standard templates
    if intent == "Informational":
        templates = [
            f"The Complete Guide to {keyword.title()}: Everything You Need to Know",
            f"How to Master {keyword.title()}: Step-by-Step Tutorial",
            f"{keyword.title()} Explained: A Comprehensive Guide for Beginners",
            f"10 Essential {keyword.title()} Tips You Should Know",
            f"Understanding {keyword.title()}: A Detailed Overview"
        ]
    elif intent == "Commercial":
        templates = [
            f"Top 10 Best {keyword.title()} Solutions in {random.randint(2023, 2024)}",
            f"The Ultimate Buyer's Guide to {keyword.title()}",
            f"Best {keyword.title()} Products: Reviews and Comparisons",
            f"{keyword.title()}: Pricing, Features, and Alternatives Compared",
            f"How to Choose the Right {keyword.title()} for Your Needs"
        ]
    else:  # Navigational
        templates = [
            f"Official {keyword.title()} Resources: Where to Find What You Need",
            f"How to Access {keyword.title()}: A Quick Reference Guide",
            f"Navigate {keyword.title()} Like a Pro: Essential Links and Resources",
            f"Finding the Best {keyword.title()} Platforms and Tools",
            f"{keyword.title()} Directory: Top Sites and Resources"
        ]
    
    return random.choice(templates)

def recommend_word_count(intent: str) -> int:
    """Recommend word count based on intent."""
    if intent == "Informational":
        return random.randint(1500, 2500)
    elif intent == "Commercial":
        return random.randint(1200, 2000)
    else:  # Navigational
        return random.randint(800, 1500)

def generate_competitors_with_openai(keyword: str) -> List[Dict[str, str]]:
    """Generate more realistic competitor data using OpenAI API."""
    try:
        # Check if API key is available
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return []
        
        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)
        
        # Create prompt
        prompt = f"""Generate 3 realistic competitor article titles and URLs for the keyword: '{keyword}'
        
        Return results as a JSON array with objects having 'title' and 'url' properties.
        Example format:
        [
          {{"title": "10 Best Ways to Learn Programming in 2024", "url": "https://www.realprogramming.com/learn-programming-guide/"}},
          {{"title": "Programming for Beginners: A Complete Guide", "url": "https://www.codingforbeginners.org/programming-complete-guide"}},
          {{"title": "How to Start Programming: Step-by-Step Tutorial", "url": "https://www.programmingtutorials.net/how-to-start"}}
        ]
        
        Make URLs look realistic with relevant domains and URL structures. Don't use placeholder domains."""
        
        # Make the API call
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a SEO competitor researcher that creates realistic competitor listings."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=500
        )
        
        # Parse the response
        result = json.loads(response.choices[0].message.content)
        if isinstance(result, list):
            return result[:3]  # Ensure we get max 3 competitors
        elif isinstance(result, dict) and "competitors" in result:
            return result["competitors"][:3]
        else:
            # Try to find any array in the response
            for key, value in result.items():
                if isinstance(value, list) and len(value) > 0:
                    return value[:3]
            return []
            
    except Exception as e:
        print(f"Error generating competitors with OpenAI: {e}")
        return []

def generate_competitors_with_google_search(keyword: str) -> List[Dict[str, str]]:
    """Generate competitor data using Google Search API."""
    try:
        api_key = os.environ.get("GOOGLE_SEARCH_API_KEY")
        cx = os.environ.get("GOOGLE_SEARCH_CX")
        
        if not api_key or not cx:
            return []
            
        # Format the URL for the Google Custom Search API
        encoded_query = quote_plus(keyword)
        url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={cx}&q={encoded_query}&num=5"
        
        # Make the request
        response = requests.get(url)
        
        if response.status_code != 200:
            print(f"Error with Google Search API: {response.status_code}")
            return []
            
        # Parse the results
        data = response.json()
        competitors = []
        
        if "items" in data:
            for item in data["items"][:3]:  # Get the top 3 results
                competitors.append({
                    "title": item.get("title", ""),
                    "url": item.get("link", "")
                })
                
        return competitors
        
    except Exception as e:
        print(f"Error using Google Search API: {e}")
        return []

def generate_competitors(keyword: str) -> List[Dict[str, str]]:
    """Generate competitor data for a keyword."""
    # Try to use Google Search API if available
    if GOOGLE_SEARCH_AVAILABLE:
        search_competitors = generate_competitors_with_google_search(keyword)
        if search_competitors and len(search_competitors) > 0:
            return search_competitors
    
    # Try to use OpenAI if available
    if OPENAI_AVAILABLE and os.environ.get("OPENAI_API_KEY"):
        openai_competitors = generate_competitors_with_openai(keyword)
        if openai_competitors and len(openai_competitors) > 0:
            return openai_competitors
            
    # Try to use Gemini if available
    if GEMINI_AVAILABLE and os.environ.get("GEMINI_API_KEY"):
        gemini_competitors = generate_competitors_with_gemini(keyword)
        if gemini_competitors and len(gemini_competitors) > 0:
            return gemini_competitors
    
    # Fallback to rule-based generation
    competitors = []
    domains = random.sample(DOMAINS, 3)
    
    for i, domain in enumerate(domains):
        title_templates = [
            f"{keyword.title()} - Complete Guide and Resources",
            f"Everything You Need to Know About {keyword.title()}",
            f"The Ultimate Guide to {keyword.title()} | {domain.split('.')[0].title()}",
            f"{random.randint(5, 15)} Best {keyword.title()} Strategies",
            f"{keyword.title()}: Definition, Examples, and Best Practices",
            f"{keyword.title()} 101: Beginner's Guide to Success"
        ]
        
        title = random.choice(title_templates)
        slug = keyword.lower().replace(' ', '-')
        url = f"https://www.{domain}/{slug}/"
        
        competitors.append({
            "title": title,
            "url": url
        })
    
    return competitors

def determine_intent_with_openai(keyword: str) -> Optional[str]:
    """Determine the intent for a keyword using OpenAI API."""
    try:
        # Check if API key is available
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return None
        
        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)
        
        # Create prompt
        prompt = f"""Analyze the search intent for the keyword: '{keyword}'
        Classify it as one of the following:
        - Commercial: The user wants to buy something or compare products/services
        - Informational: The user wants to learn or find information
        - Navigational: The user wants to find a specific website or resource
        
        Return ONLY the intent category as a single word with no explanation."""
        
        # Make the API call
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a search intent classifier that categorizes keywords based on user intent."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=50
        )
        
        # Parse the response
        result = response.choices[0].message.content.strip()
        
        # Make sure the result is one of our expected categories
        if "commercial" in result.lower():
            return "Commercial"
        elif "navigational" in result.lower():
            return "Navigational"
        elif "informational" in result.lower():
            return "Informational"
        else:
            return None
            
    except Exception as e:
        print(f"Error determining intent with OpenAI: {e}")
        return None

def determine_intent(keyword: str) -> str:
    """Determine the likely intent for a keyword."""
    # Try to use OpenAI if available
    if OPENAI_AVAILABLE and os.environ.get("OPENAI_API_KEY"):
        openai_intent = determine_intent_with_openai(keyword)
        if openai_intent:
            return openai_intent
    
    # Try to use Gemini if available
    if GEMINI_AVAILABLE and os.environ.get("GEMINI_API_KEY"):
        gemini_intent = determine_intent_with_gemini(keyword)
        if gemini_intent:
            return gemini_intent
    
    # Fallback to rule-based determination
    keyword_lower = keyword.lower()
    
    # Check for commercial intent
    commercial_indicators = ["buy", "price", "cost", "shop", "purchase", "review", "best", "top", "vs", "comparison"]
    for indicator in commercial_indicators:
        if indicator in keyword_lower:
            return "Commercial"
    
    # Check for navigational intent
    navigational_indicators = ["login", "sign up", "download", "app", "website", "contact", "support"]
    for indicator in navigational_indicators:
        if indicator in keyword_lower:
            return "Navigational"
    
    # Default to informational intent
    return "Informational"

def generate_related_keywords_with_openai(keyword: str, intent: str) -> List[str]:
    """Generate related keywords using OpenAI API."""
    try:
        # Check if API key is available
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return []
        
        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)
        
        # Create appropriate prompt based on intent
        if intent == "Informational":
            prompt = f"Generate 10 informational search keywords related to '{keyword}'. Focus on educational, how-to, and learning-oriented keywords. Return as a JSON array of strings with no explanation."
        elif intent == "Commercial":
            prompt = f"Generate 10 commercial/transactional search keywords related to '{keyword}'. Focus on buying, product reviews, and service-oriented keywords. Return as a JSON array of strings with no explanation."
        else:  # Navigational
            prompt = f"Generate 10 navigational search keywords related to '{keyword}'. Focus on brand-specific, website, app, login, and portal-related keywords. Return as a JSON array of strings with no explanation."
        
        # Make the API call
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a skilled SEO keyword researcher that generates related keywords based on a main keyword and intent."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=500
        )
        
        # Parse the response
        result = json.loads(response.choices[0].message.content)
        if isinstance(result, dict) and "keywords" in result:
            return result["keywords"]
        elif isinstance(result, list):
            return result
        else:
            # Try to find any array in the response
            for key, value in result.items():
                if isinstance(value, list) and len(value) > 0:
                    return value
            return []
            
    except Exception as e:
        print(f"Error generating keywords with OpenAI: {e}")
        return []

def generate_related_keywords(keyword: str, intent: str = "") -> List[str]:
    """Generate related keywords based on a given keyword and intent."""
    if not intent:
        intent = determine_intent(keyword)
    
    # Try to use OpenAI if available
    if OPENAI_AVAILABLE and os.environ.get("OPENAI_API_KEY"):
        openai_keywords = generate_related_keywords_with_openai(keyword, intent)
        if openai_keywords and len(openai_keywords) > 0:
            return openai_keywords[:min(10, len(openai_keywords))]
    
    # Try to use Gemini if available
    if GEMINI_AVAILABLE and os.environ.get("GEMINI_API_KEY"):
        gemini_keywords = generate_related_keywords_with_gemini(keyword, intent)
        if gemini_keywords and len(gemini_keywords) > 0:
            return gemini_keywords[:min(10, len(gemini_keywords))]
    
    # Fallback to rule-based generation
    related_keywords = []
    
    if intent == "Informational":
        modifiers = INFORMATIONAL_MODIFIERS
    elif intent == "Commercial":
        modifiers = COMMERCIAL_MODIFIERS
    else:  # Navigational
        modifiers = NAVIGATIONAL_MODIFIERS
    
    # Generate keyword variations
    for modifier in random.sample(modifiers, min(5, len(modifiers))):
        if " " in keyword:
            related_keywords.append(f"{modifier} {keyword}")
        else:
            related_keywords.append(f"{modifier} {keyword}")
    
    # Add some keyword combinations
    words = keyword.split()
    if len(words) > 1:
        for i in range(len(words)):
            new_words = words.copy()
            new_words[i] = random.choice(["best", "top", "online", "professional", "free"]) + " " + new_words[i]
            related_keywords.append(" ".join(new_words))
    
    # Add some specific variations
    related_keywords.extend([
        f"{keyword} examples",
        f"{keyword} tools",
        f"{keyword} services",
        f"{keyword} tips",
        f"{keyword} strategies"
    ])
    
    # Remove duplicates and limit to a reasonable number
    related_keywords = list(set(related_keywords))
    return related_keywords[:min(10, len(related_keywords))]

def generate_keyword_node(keyword: str, is_root: bool = False, custom_prompt: str = "") -> Dict[str, Any]:
    """Generate a complete keyword node with all required data."""
    if is_root:
        intent = random.choice(INTENTS)
    else:
        intent = determine_intent(keyword)
    
    return {
        "keyword": keyword,
        "intent": intent,
        "title": generate_title(keyword, intent, custom_prompt),
        "word_count": recommend_word_count(intent),
        "competitors": generate_competitors(keyword),
        "children": []
    }

def generate_keyword_structure(main_keyword: str, depth: int = 2, custom_prompt: str = "") -> Dict[str, Any]:
    """
    Generate a complete keyword structure with a specified depth.
    
    Args:
        main_keyword: The main keyword to build the structure around
        depth: How many levels of nested keywords to generate (1-3)
        custom_prompt: Optional custom prompt for title generation
    
    Returns:
        A complete keyword structure as a nested dictionary
    """
    # Create the root node
    keyword_structure = generate_keyword_node(main_keyword, is_root=True, custom_prompt=custom_prompt)
    
    # Generate first level of children
    first_level_keywords = generate_related_keywords(main_keyword)
    for keyword in first_level_keywords:
        child_node = generate_keyword_node(keyword, custom_prompt=custom_prompt)
        keyword_structure["children"].append(child_node)
        
        # Generate second level (if requested)
        if depth >= 2:
            second_level_keywords = generate_related_keywords(keyword)[:3]  # Limit to 3 for performance
            for sub_keyword in second_level_keywords:
                sub_node = generate_keyword_node(sub_keyword, custom_prompt=custom_prompt)
                child_node["children"].append(sub_node)
                
                # Generate third level (if requested)
                if depth >= 3:
                    third_level_keywords = generate_related_keywords(sub_keyword)[:2]  # Limit to 2 for performance
                    for sub_sub_keyword in third_level_keywords:
                        sub_sub_node = generate_keyword_node(sub_sub_keyword, custom_prompt=custom_prompt)
                        sub_node["children"].append(sub_sub_node)
    
    return keyword_structure
