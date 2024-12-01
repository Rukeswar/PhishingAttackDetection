import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import tldextract
from difflib import SequenceMatcher
from sklearn.preprocessing import LabelEncoder

# Label Encoder initialization
label_encoder = LabelEncoder()

def extract_features(url):
    try:
        response = requests.get(url, timeout=10, allow_redirects=True)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        redirect_history = response.history  # Extract redirect history if needed
    except requests.exceptions.RequestException as e:
        response = None
        soup = None
        redirect_history = []

    # URL parsing and domain extraction
    parsed_url = urlparse(url)
    extracted = tldextract.extract(url)
    domain = (
        f"{extracted.subdomain}.{extracted.domain}.{extracted.suffix}"
        if extracted.subdomain else f"{extracted.domain}.{extracted.suffix}"
    )

    # Extract features from the URL
    url_length = len(url)
    no_of_letters = sum(c.isalpha() for c in url)
    no_of_digits = sum(c.isdigit() for c in url)
    no_of_special_chars = sum(c in "#$%^*()_+={}[]|:;<>,.?/~" for c in url)
    title = soup.title.string.strip() if soup and soup.title else ""

    features = {
        "URLLength": url_length,
        "Domain": domain,
        "DomainLength": len(domain),
        "IsDomainIP": 1 if extracted.domain.replace(".", "").isdigit() else 0,
        "TLD": extracted.suffix,
        "TLDLength": len(extracted.suffix),
        "URLSimilarityIndex": 0.5,  # Placeholder
        "CharContinuationRate": 0.5,  # Placeholder
        "TLDLegitimateProb": 0.8,  # Placeholder
        "URLCharProb": 0.05,  # Placeholder
        "NoOfSubDomain": len(extracted.subdomain.split(".")) if extracted.subdomain else 0,
        # Obfuscation features
        "HasObfuscation": 1 if '%' in url else 0,
        "NoOfObfuscatedChar": url.count('%'),
        "ObfuscationRatio": url.count('%') / url_length if url_length else 0,
        # URL character composition
        "NoOfLettersInURL": no_of_letters,
        "LetterRatioInURL": no_of_letters / url_length if url_length else 0,
        "NoOfDegitsInURL": no_of_digits,
        "DegitRatioInURL": no_of_digits / url_length if url_length else 0,
        "NoOfEqualsInURL": url.count('='),
        "NoOfQMarkInURL": url.count('?'),
        "NoOfAmpersandInURL": url.count('&'),
        "NoOfOtherSpecialCharsInURL": no_of_special_chars,
        "SpacialCharRatioInURL": no_of_special_chars / url_length if url_length else 0,
        "IsHTTPS": 1 if parsed_url.scheme == "https" else 0,
        # Content-based features
        "LineOfCode": len(html.splitlines()) if html else 0,
        "LargestLineLength": max(len(line) for line in html.splitlines()) if html else 0,
        "HasTitle": 1 if title else 0,
        "DomainTitleMatchScore": SequenceMatcher(None, domain, title).ratio() if title else 0,
        "URLTitleMatchScore": 1 if title.lower() in url.lower() else 0,
        "HasFavicon": 1 if soup and soup.find("link", rel="icon") else 0,
        "Robots": 1 if requests.get(urljoin(url, "/robots.txt"), timeout=5).status_code == 200 else 0,
        "IsResponsive": 1 if soup and (soup.find("meta", attrs={"name": "viewport"}) or any("responsive" in link.get("href", "") for link in soup.find_all("link", href=True))) else 0,
        "NoOfURLRedirect": len(redirect_history),
        "NoOfSelfRedirect": len([r for r in redirect_history if domain in r.url]),
        "HasDescription": 1 if soup and soup.find("meta", {"name": "description"}) else 0,
        "NoOfPopup": html.lower().count("window.open") if html else 0,
        "NoOfiFrame": len(soup.find_all("iframe")) if soup else 0,
        "HasExternalFormSubmit": 1 if soup and any(
            form for form in soup.find_all("form", action=True)
            if domain not in urlparse(form["action"]).netloc and "http" in form["action"]
        ) else 0,
        # HasSocialNet
        "HasSocialNet": 1 if any(social in url.lower() for social in ['facebook', 'twitter', 'instagram']) else 0,

        # Security-related features
        "HasSubmitButton": 1 if soup and soup.find("button", {"type": "submit"}) else 0,
        "HasHiddenFields": 1 if soup and soup.find_all("input", {"type": "hidden"}) else 0,
        "HasPasswordField": 1 if soup and soup.find("input", {"type": "password"}) else 0,
        "Bank": 1 if 'bank' in url.lower() else 0,
        "Pay": 1 if 'pay' in url.lower() else 0,
        "Crypto": 1 if 'crypto' in url.lower() else 0,
        "HasCopyrightInfo": 1 if soup and "copyright" in html.lower() else 0,

        # Miscellaneous features
        "NoOfImage": len(soup.find_all("img")) if soup else 0,
        "NoOfCSS": len(soup.find_all("link", {"rel": "stylesheet"})) if soup else 0,
        "NoOfJS": len(soup.find_all("script")) if soup else 0,
        # External references
        "NoOfSelfRef": html.lower().count(domain.lower()) if html else 0,
        "NoOfEmptyRef": len([a for a in soup.find_all("a", href=True) if a['href'] == "#"]) if soup else 0,
        "NoOfExternalRef": len([a for a in soup.find_all("a", href=True) if "http" in a['href'] and domain not in a['href']]) if soup else 0,
    }

    # Encode Domain and TLD using label encoding
    features["Domain"] = label_encoder.fit_transform([features["Domain"]])[0]
    features["TLD"] = label_encoder.fit_transform([features["TLD"]])[0]

    return features
