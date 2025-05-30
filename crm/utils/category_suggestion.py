"""
Module for automatic category suggestion based on ticket content
"""
import re
from difflib import SequenceMatcher

# Keywords for each category (in Polish)
CATEGORY_KEYWORDS = {
    'hardware': [
        # urządzenia fizyczne i komponenty
        "komputer", "laptop", "monitor", "drukarka", "klawiatura", "myszka", "sprzęt",
        "urządzenie", "dysk", "pamięć", "ram", "procesor", "cpu", "bateria", "zasilacz",
        "ładowarka", "kabel", "słuchawki", "mikrofon", "kamera", "webcam", "scanner",
        "skaner", "hardware", "fizyczny", "płyta główna", "grafika", "karta graficzna", "gpu",
        "dysk ssd", "nvme", "hdd", "obudowa", "wentylator", "cooler", "radiator",
        "złącze", "port usb", "hdmi", "displayport", "adapter", "hub", "slot", "gniazdo",
        "sata", "taśma", "układ scalony", "mikroprocesor", "karta sieciowa", "słuchawek","usb", "port", "myszy", "klawiatury",
        # awarie i uszkodzenia (wszystkie formy)
        "uszkodzony", "uszkodzona", "uszkodzeni", "uszkodzone",
        "popsuty", "popsuta", "popsute", "popsutym", "popsutych",
        "zepsuty", "zepsuta", "zepsute", "zepsutym", "zepsutych",
        "awaria", "awarie", "złamany", "złamana", "złamane", "popsuty",
        "nie działa sprzęt", "sprzęt nie działa"
    ],
    'software': [
        # aplikacje, systemy, biblioteki
        "program", "aplikacja", "system", "windows", "linux", "mac", "office", "excel",
        "word", "powerpoint", "software", "oprogramowanie",
        # instalacja i aktualizacje
        "instalacja", "instaluje się", "zainstalowany", "deinstalacja",
        "aktualizacja", "update", "wersja", "kompilacja", "runtime",
        # błędy i logi
        "błąd", "błędy", "error", "errors", "crash", "crashe", "zawiesza się", "zawiesił się",
        "nie działa program", "exception", "stack trace", "log", "crash dump",
        # licencje i klucze
        "licencja", "klucz", "aktywacja", "klucz produktu",
        # sterowniki, wirusy, skrypty
        "sterownik", "driver", "antywirus", "wirus", "złośliwe",
        "skrypt", "batch", "shell", "framework", "biblioteka", "dll",
        # inne
        "pakiet", "rpm", "deb", "apk", "iso", "konfiguracja", "cfg", "ini",
        "cache", "profil użytkownika", "wirtualizacja", "docker", "vm",
        # języki
        "java", "python", "c#", "javascript"
    ],
    'network': [
        # połączenia sieciowe i protokoły
        "internet", "sieć", "wifi", "ethernet", "połączenie", "brak internetu",
        "wolny internet", "router", "modem", "lan", "wan", "switch", "router",
        "ip", "dns", "dhcp", "nat", "firewall", "zapora", "proxy", "vpn",
        # diagnostyka
        "ping", "traceroute", "trasowanie", "packet loss", "straty pakietów",
        "latencja", "MTU", "QoS",
        # sprzęt sieciowy
        "kabel sieciowy", "port lan", "port wan", "gniazdo sieciowe",
        # inne
        "isp", "operator", "serwer proxy", "hotspot", "ssid", "bridging",
        "routing", "adresacja", "maskowanie",
        # nowe słowa kluczowe - problemy z internetem
        "net", "strony się nie ładują", "strony wolno się ładują", "wolno chodzi", 
        "wywala", "sieć nie działa", "sieć działa wolno", "problem z internetem",
        "problem z siecią", "nie mogę się połączyć", "zrywa połączenie", "słaby sygnał",
        "strony internetowe", "nie działa internet", "internet wolno działa", 
        "strony nie otwierają się", "nie ładuje", "wolno ładuje", "internet zrywa",
        "wifi słabe", "nie mogę wejść na stronę", "stracone pakiety"
    ],
    'account': [
        # logowanie, uprawnienia
        "konto", "użytkownik", "login", "logowanie", "wylogowanie", "hasło",
        "zmiana hasła", "reset hasła", "przypomnienie hasła", "nie pamiętam hasła",
        "nie mogę się zalogować", "blokada konta", "odblokowanie",
        "uprawnienia", "dostęp", "rola", "role", "grupa", "grupy",
        # uwierzytelnianie
        "2fa", "dwuskładnikowe", "token", "sesja", "timeout",
        "ldap", "active directory", "azure ad", "sso", "oauth", "saml",
        # administrator
        "admin", "administrator", "elevacja", "zatwierdzenie"
    ],
    'other': [
        # ogólne
        "inny", "różne", "ogólne", "pytanie", "prośba", "informacja",
        "pomoc", "wsparcie", "sugestia", "propozycja", "uwaga", "opinia",
        "feedback", "zgłoszenie", "problem",
        # procesy i zadania
        "zadanie", "status", "priorytet", "eskalacja", "handover",
        "koordynacja", "spotkanie", "planowanie", "raport", "analiza"
    ]
}

# Lista wyjątków - słowa, które nie powinny być brane pod uwagę przy dopasowywaniu podobieństwa 
# do słów kluczowych z powodu zbyt wielu fałszywych pozytywnych dopasowań
EXCEPTION_WORDS = [
    # Przyimki i spójniki
    "sie", "się", "nie", "jak", "czy", "ale", "lub", "oraz", "tylko", "tez", "też",
    
    # Zaimki i formy czasownikowe
    "jest", "był", "być", "są", "ma", "mam", "mamy", "mi", "to", "tu", "tam",
    "ten", "ta", "te", "ich", "im", "go", "jej", "ona", "one", "on", "ja", "ty",
    
    # Krótkie słowa, które mogą być podobne do słów kluczowych
    "nic", "coś", "cos", "nas", "was", "dla", "dom", "już", "juz", "gdy", "tak", "pod",
    "przy", "bez", "nad", "mac", "ram", "lan", "dwa", "trzy", "raz", "din", "ups", "ssd",
    
    # Krótkie słowa, które mogą być podobne do "sieć"
    "się", "sięgnać", "siedzi", "siebie", "siedzieć", "siekiera", "sieć",
    
    # Inne typowe słowa w języku polskim
    "bardzo", "może", "moze", "nasz", "wasz", "jego", "moje", "twoje", "swoje",
    "dziś", "jutro", "wczoraj", "dzisiaj", "teraz", "potem", "kiedy", "gdzie"
]

# Polish characters mapping for normalization
POLISH_CHARS_MAP = {
    'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n', 
    'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z',
    'Ą': 'A', 'Ć': 'C', 'Ę': 'E', 'Ł': 'L', 'Ń': 'N',
    'Ó': 'O', 'Ś': 'S', 'Ź': 'Z', 'Ż': 'Z'
}

def normalize_polish_chars(text):
    """
    Replace Polish diacritical marks with their non-diacritical counterparts
    """
    for polish_char, latin_char in POLISH_CHARS_MAP.items():
        text = text.replace(polish_char, latin_char)
    return text

def similar(a, b, threshold=0.8):
    """
    Check if two strings are similar enough based on a threshold
    """
    # Calculate similarity ratio for original strings
    orig_similarity = SequenceMatcher(None, a, b).ratio()
    
    # Calculate similarity with normalized Polish characters
    a_norm = normalize_polish_chars(a)
    b_norm = normalize_polish_chars(b)
    norm_similarity = SequenceMatcher(None, a_norm, b_norm).ratio()
    
    # Use the higher similarity score
    similarity = max(orig_similarity, norm_similarity)
    
    return similarity >= threshold

def preprocess_text(text):
    """
    Preprocess text by converting to lowercase and tokenizing into words
    Also creates normalized versions of words without Polish diacritical marks
    """
    # Convert to lowercase and replace punctuation with spaces
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    # Split into words
    words = text.split()
    
    return words

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
    
    # Also create normalized versions of words without Polish diacritical marks
    normalized_words = [normalize_polish_chars(word) for word in words]
    
    # Count matches for each category
    category_scores = {category: 0 for category in CATEGORY_KEYWORDS}
    match_details = {category: [] for category in CATEGORY_KEYWORDS}
    
    # Check both original words and their normalized versions
    for word, norm_word in zip(words, normalized_words):
        if len(word) < 3:  # Skip very short words
            continue
            
        # Skip exception words - to prevent false positives
        if word.lower() in EXCEPTION_WORDS:
            continue
            
        for category, keywords in CATEGORY_KEYWORDS.items():
            # Normalize keywords for comparison
            norm_keywords = [normalize_polish_chars(kw) for kw in keywords]
            
            # Check for exact matches (both original and normalized)
            if word in keywords or norm_word in norm_keywords:
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
