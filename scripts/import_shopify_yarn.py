import argparse
import json
import re
import sys
from pathlib import Path
import requests

# Import validation function from validate_data.py
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir / "scripts"))
from validate_data import validate_yarn_data, load_json

def parse_weight_category(tags, body_html):
    """Attempt to parse CYC weight category (0-7) from Shopify tags or body HTML."""
    # Check tags first for pattern like "Weight_3-Light" or "Weight_4"
    for tag in tags:
        match = re.search(r"weight[_\s\-]*(\d)", tag, re.IGNORECASE)
        if match:
            return int(match.group(1))

    # Search in HTML description
    text = re.sub(r'<[^>]+>', ' ', body_html)
    match = re.search(r"(?:CYC|weight|category)\s*[:#-]?\s*(\d)", text, re.IGNORECASE)
    if match:
        return int(match.group(1))

    # Default fallback weight category if not found
    return 4

def parse_put_up(body_html):
    """Extract yardage, meters, weight_grams, weight_ounces from body HTML text."""
    text = re.sub(r'<[^>]+>', ' ', body_html)

    # Defaults
    grams = 100.0
    ounces = 3.5
    yardage = 200.0
    meters = 183.0

    # Look for grams
    g_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:g|grams|oz)', text, re.IGNORECASE)
    if g_match:
        grams = float(g_match.group(1))
        ounces = round(grams / 28.3495, 2)

    # Look for yardage
    yd_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:yd|yds|yards)', text, re.IGNORECASE)
    if yd_match:
        yardage = float(yd_match.group(1))
        meters = round(yardage * 0.9144, 2)

    return {
        "weight_grams": grams,
        "weight_ounces": ounces,
        "yardage": yardage,
        "meters": meters
    }

def parse_fiber_content(body_html):
    """Extract fiber content list from body HTML text."""
    text = re.sub(r'<[^>]+>', ' ', body_html)
    # Match patterns like "100% Acrylic" or "80% Acrylic, 20% Wool"
    matches = re.findall(r'(\d+(?:\.\d+)?)\s*%\s*([A-Za-z\s]+?)(?=[.,;\d]|$)', text)

    fiber_content = []
    if matches:
        for pct, ftype in matches:
            ftype_clean = ftype.strip()
            if ftype_clean:
                fiber_content.append({
                    "fiber_type": ftype_clean,
                    "percentage": float(pct)
                })

    if not fiber_content:
        fiber_content = [{"fiber_type": "Acrylic", "percentage": 100.0}]

    return fiber_content

def parse_recommended_gauge(body_html):
    """Extract or default recommended gauge information."""
    return {
        "knit_gauge_4in": 18.0,
        "crochet_gauge_4in": 14.0,
        "recommended_needle_mm": 5.0,
        "recommended_hook_mm": 5.5
    }

def fetch_shopify_product(url):
    clean_url = url.split('?')[0].rstrip('/')
    if not clean_url.endswith('.json'):
        json_url = clean_url + '.json'
    else:
        json_url = clean_url

    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(json_url, headers=headers)
    response.raise_for_status()
    payload = response.json()

    if 'product' not in payload:
        raise ValueError("Invalid Shopify product JSON response")

    return payload['product'], clean_url

def main():
    parser = argparse.ArgumentParser(description="Import yarn product data from a Shopify store URL.")
    parser.add_argument("url", nargs="?", help="Shopify product URL (e.g. https://www.lionbrand.com/products/mandala-yarn)")
    args = parser.parse_args()

    url = args.url
    if not url:
        url = input("Enter Shopify product URL: ").strip()

    if not url:
        print("Error: No URL provided.")
        sys.exit(1)

    print(f"Fetching data from {url}...")
    try:
        product, clean_url = fetch_shopify_product(url)
    except Exception as e:
        print(f"Failed to fetch product data: {e}")
        sys.exit(1)

    handle = product.get('handle') or clean_url.split('/')[-1]
    title = product.get('title', 'Unknown Yarn')
    vendor = product.get('vendor', 'Unknown Brand')
    tags = product.get('tags', [])
    body_html = product.get('body_html', '')

    yarn_data = {
        "brand": vendor,
        "line_name": title,
        "weight_category": parse_weight_category(tags, body_html),
        "put_up": parse_put_up(body_html),
        "recommended_gauge": parse_recommended_gauge(body_html),
        "fiber_content": parse_fiber_content(body_html)
    }

    # Validate generated data
    errors = validate_yarn_data(yarn_data, f"data/{handle}.json")
    if errors:
        print("Generated yarn data is invalid:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)

    # Save to data directory
    output_path = root_dir / "data" / f"{handle}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(yarn_data, f, indent=2)

    print(f"Successfully saved validated yarn data to {output_path}")

if __name__ == "__main__":
    main()
