import re
import spacy

# Load the English NLP model
nlp = spacy.load("en_core_web_sm")  # Use a small model for basic NER tasks

def find_matches(pattern, string, flags=0):
    # Compile RegEx pattern
    p = re.compile(pattern, flags=flags)
    # Match pattern against input text
    matches = list(p.finditer(string))
    # Handle matches
    if len(matches) == 0:
        return None
    else:
        return([m.group() for m in matches])
    
# Define regex patterns
# phone_pattern = r'\b[689]\d{7}\b'  # Pattern for Singapore phone numbers
phone_pattern = r"\s(\+65)?[\s-]?\d{4}[\s-]?\d{4}\b"
nric_pattern = r'\b[SFTG]\d{7}[A-Z]\b'  # Pattern for Singapore NRIC/FIN
# Placeholder pattern for bank account numbers; adjust as necessary
bank_account_pattern = r'\b\d{10,12}\b'
email_pattern = r"\b[\w.-]+?@\w+?\.\w+?\b"  # Email address pattern
pincode_pattern = r"\b\d{5,6}\b"
# Simple pattern for credit card numbers and CVVs; adjust as necessary
credit_card_pattern = r"\b(?:\d{4}[\s-]?){3}\d{4,7}\b"
cvv_pattern = r"\b\d{3}\b"

def detect_sensitive_info(text):
    # Initial regex detections
    phone_numbers = find_matches(phone_pattern, text, flags=re.IGNORECASE)
    nric_numbers = re.findall(nric_pattern, text)
    bank_account_numbers = re.findall(bank_account_pattern, text)
    email_addresses = re.findall(email_pattern, text)
    pincodes = re.findall(pincode_pattern, text)
    credit_card_numbers = re.findall(credit_card_pattern, text)
    cvvs = re.findall(cvv_pattern, text)

    regex_findings = set(phone_numbers + nric_numbers + bank_account_numbers + email_addresses +
                         pincodes + credit_card_numbers + cvvs)
    
    # Use spaCy for NER
    doc = nlp(text)
    possible_addresses = []
    named_entities = []
    
    for ent in doc.ents:
        if any(regex_finding == ent.text for regex_finding in regex_findings):
            continue  # Skip entities detected by regex
        
        if ent.label_ in ["LOC", "GPE", "ORG", "FAC"]:
            possible_addresses.append(ent.text)
        else:
            named_entities.append((ent.text, ent.label_))

    # Compile results, including regex findings
    results = {
        "named_entities": named_entities,
        "possible_addresses": possible_addresses,
        "phone_numbers": phone_numbers,
        "nric_numbers": nric_numbers,
        "bank_account_numbers": bank_account_numbers,
        "email_addresses": email_addresses,
        "pincodes": pincodes,
        "credit_card_numbers": credit_card_numbers,
        "cvvs": cvvs,
    }

    return results


def print_formatted_info(info):
    print("Detected Sensitive Information:\n")
    
    # Iterate over the results dictionary
    for category, items in info.items():
        # Print the category name
        print(f"{category.replace('_', ' ').title()}:")
        
        if not items:  # Check if the list is empty
            print("  None found.\n")
            continue
        
        # Iterate over items in each category and print
        for item in items:
            # For named entities, 'item' is a tuple (text, label)
            if isinstance(item, tuple):
                print(f"  - {item[0]} ({item[1]})")
            else:  # For regex matches, 'item' is just the matched string
                print(f"  - {item}")
        
        print()  # Add an empty line for spacing