"""
Module for automatic category suggestion based on ticket content
"""
import re
from difflib import SequenceMatcher

# Keywords for each category (in Polish)
CATEGORY_KEYWORDS = {
    'hardware': [
        "komputer", "laptop", "monitor", "drukarka", "klawiatura", "myszka", "sprzęt", 
        "urządzenie", "dysk", "pamięć", "ram", "procesor", "cpu", "bateria", "zasilacz", 
        "ładowarka", "kabel", "słuchawki", "mikrofon", "kamera", "webcam", "scanner", 
        "skaner", "hardware", "fizyczny", "wymiana", "naprawa", "uszkodzony", "zepsuty",
        "awaria", "złamany", "złamana", "popsuta", "nie działa sprzęt", "zakup sprzętu"
    ],
    'software': [
        "program", "aplikacja", "system", "windows", "linux", "mac", "office", "excel", 
        "word", "powerpoint", "software", "oprogramowanie", "instalacja", "aktualizacja", 
        "update", "wersja", "licencja", "klucz", "aktywacja", "błąd", "error", "crash", 
        "zawiesza", "nie działa program", "reinstalacja", "deinstalacja", "sterownik", 
        "driver", "antywirus", "wirus", "złośliwe", "zakup programu", "zakup licencji"
    ],
    'network': [
        "internet", "sieć", "wifi", "połączenie", "router", "modem", "lan", "ethernet", 
        "ip", "dns", "vpn", "firewall", "zapora", "transfer", "pobieranie", "upload", 
        "download", "ping", "prędkość", "szybkość", "łącze", "bezprzewodowy", "przewodowy", 
        "kabel sieciowy", "serwer", "brak internetu", "wolny internet", "zdalne", "zdalna"
    ],
    'account': [
        "konto", "użytkownik", "login", "hasło", "logowanie", "wylogowanie", "rejestracja", 
        "profil", "e-mail", "email", "mail", "uprawnienia", "dostęp", "blokada", 
        "odblokowanie", "zmiana hasła", "przypomnienie hasła", "autoryzacja", 
        "uwierzytelnianie", "2fa", "dwuskładnikowe", "administrator", "admin", "id", 
        "resetowanie", "reset hasła", "nie pamiętam hasła", "nie mogę się zalogować"
    ],
    'other': [
        "inny", "różne", "ogólne", "pytanie", "prośba", "informacja", "pomoc", "wsparcie", 
        "sugestia", "propozycja", "uwaga", "opinia", "feedback", "zgłoszenie", "problem"
    ]
}

def similar(a, b, threshold=0.8):
    """
    Check if two strings are similar enough based on a threshold
    """
    # Calculate similarity ratio
    similarity = SequenceMatcher(None, a, b).ratio()
    return similarity >= threshold

def preprocess_text(text):
    """
    Preprocess text by converting to lowercase and tokenizing into words
    """
    # Convert to lowercase and replace punctuation with spaces
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    # Split into words
    return text.split()

def detect_category(title, description):
    """
    Analyzes the ticket title and description to suggest the most appropriate category
    based on keyword matches.
    
    Returns:
        tuple: (suggested_category, confidence_score, match_details)
    """
    # Combine title and description for analysis
    combined_text = f"{title} {description}"
    words = preprocess_text(combined_text)
    
    # Count matches for each category
    category_scores = {category: 0 for category in CATEGORY_KEYWORDS}
    match_details = {category: [] for category in CATEGORY_KEYWORDS}
    
    for word in words:
        if len(word) < 3:  # Skip very short words
            continue
            
        for category, keywords in CATEGORY_KEYWORDS.items():
            # Check for exact matches
            if word in keywords:
                category_scores[category] += 1
                match_details[category].append((word, 1.0))
            else:
                # Check for similar words (fuzzy matching)
                for keyword in keywords:
                    if similar(word, keyword, threshold=0.8):
                        category_scores[category] += 0.5  # Lower score for fuzzy matches
                        match_details[category].append((word, 0.5))
                        break
    
    # Find category with highest score
    best_category = max(category_scores, key=category_scores.get)
    best_score = category_scores[best_category]
    
    # Calculate confidence (normalize by dividing by total matches)
    total_matches = sum(category_scores.values())
    confidence = best_score / total_matches if total_matches > 0 else 0
    
    return best_category, confidence, match_details

def should_suggest_category(selected_category, title, description, confidence_threshold=0.5):
    """
    Determines if a different category should be suggested based on the text analysis
    
    Args:
        selected_category: The category selected by the user
        title: Ticket title
        description: Ticket description
        confidence_threshold: Minimum confidence required to make a suggestion
        
    Returns:
        tuple: (should_suggest, suggested_category, confidence, match_details)
    """
    suggested_category, confidence, match_details = detect_category(title, description)
    
    # Only suggest if confidence is high enough and different from selected
    should_suggest = (confidence >= confidence_threshold and 
                     suggested_category != selected_category and
                     len(match_details[suggested_category]) > 0)
    
    return should_suggest, suggested_category, confidence, match_details
