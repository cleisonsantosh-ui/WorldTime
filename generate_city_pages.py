#!/usr/bin/env python3
"""
generate_city_pages.py
Gera uma página HTML estática para cada cidade do CITIES_DB
Baseado no template city/_template.html

Uso: python generate_city_pages.py
"""

import os
import json
import re

# ── Banco de cidades (espelho do JS) ──────────────────────────────────────────
CITIES = [
    {"city": "New York",       "country": "United States", "cc": "US", "flag": "🇺🇸", "lat": 40.7128,  "lon": -74.0060,  "tz": "America/New_York",                  "slug": "new-york"},
    {"city": "Los Angeles",    "country": "United States", "cc": "US", "flag": "🇺🇸", "lat": 34.0522,  "lon": -118.2437, "tz": "America/Los_Angeles",               "slug": "los-angeles"},
    {"city": "Chicago",        "country": "United States", "cc": "US", "flag": "🇺🇸", "lat": 41.8781,  "lon": -87.6298,  "tz": "America/Chicago",                   "slug": "chicago"},
    {"city": "Houston",        "country": "United States", "cc": "US", "flag": "🇺🇸", "lat": 29.7604,  "lon": -95.3698,  "tz": "America/Chicago",                   "slug": "houston"},
    {"city": "Miami",          "country": "United States", "cc": "US", "flag": "🇺🇸", "lat": 25.7617,  "lon": -80.1918,  "tz": "America/New_York",                  "slug": "miami"},
    {"city": "Toronto",        "country": "Canada",        "cc": "CA", "flag": "🇨🇦", "lat": 43.6532,  "lon": -79.3832,  "tz": "America/Toronto",                   "slug": "toronto"},
    {"city": "Vancouver",      "country": "Canada",        "cc": "CA", "flag": "🇨🇦", "lat": 49.2827,  "lon": -123.1207, "tz": "America/Vancouver",                 "slug": "vancouver"},
    {"city": "Mexico City",    "country": "Mexico",        "cc": "MX", "flag": "🇲🇽", "lat": 19.4326,  "lon": -99.1332,  "tz": "America/Mexico_City",               "slug": "mexico-city"},
    {"city": "São Paulo",      "country": "Brazil",        "cc": "BR", "flag": "🇧🇷", "lat": -23.5505, "lon": -46.6333,  "tz": "America/Sao_Paulo",                 "slug": "sao-paulo"},
    {"city": "Rio de Janeiro", "country": "Brazil",        "cc": "BR", "flag": "🇧🇷", "lat": -22.9068, "lon": -43.1729,  "tz": "America/Sao_Paulo",                 "slug": "rio-de-janeiro"},
    {"city": "Buenos Aires",   "country": "Argentina",     "cc": "AR", "flag": "🇦🇷", "lat": -34.6037, "lon": -58.3816,  "tz": "America/Argentina/Buenos_Aires",    "slug": "buenos-aires"},
    {"city": "Bogotá",         "country": "Colombia",      "cc": "CO", "flag": "🇨🇴", "lat": 4.7110,   "lon": -74.0721,  "tz": "America/Bogota",                    "slug": "bogota"},
    {"city": "Lima",           "country": "Peru",          "cc": "PE", "flag": "🇵🇪", "lat": -12.0464, "lon": -77.0428,  "tz": "America/Lima",                      "slug": "lima"},
    {"city": "Santiago",       "country": "Chile",         "cc": "CL", "flag": "🇨🇱", "lat": -33.4489, "lon": -70.6693,  "tz": "America/Santiago",                  "slug": "santiago"},
    {"city": "London",         "country": "United Kingdom","cc": "GB", "flag": "🇬🇧", "lat": 51.5074,  "lon": -0.1278,   "tz": "Europe/London",                     "slug": "london"},
    {"city": "Paris",          "country": "France",        "cc": "FR", "flag": "🇫🇷", "lat": 48.8566,  "lon": 2.3522,    "tz": "Europe/Paris",                      "slug": "paris"},
    {"city": "Berlin",         "country": "Germany",       "cc": "DE", "flag": "🇩🇪", "lat": 52.5200,  "lon": 13.4050,   "tz": "Europe/Berlin",                     "slug": "berlin"},
    {"city": "Madrid",         "country": "Spain",         "cc": "ES", "flag": "🇪🇸", "lat": 40.4168,  "lon": -3.7038,   "tz": "Europe/Madrid",                     "slug": "madrid"},
    {"city": "Rome",           "country": "Italy",         "cc": "IT", "flag": "🇮🇹", "lat": 41.9028,  "lon": 12.4964,   "tz": "Europe/Rome",                       "slug": "rome"},
    {"city": "Amsterdam",      "country": "Netherlands",   "cc": "NL", "flag": "🇳🇱", "lat": 52.3676,  "lon": 4.9041,    "tz": "Europe/Amsterdam",                  "slug": "amsterdam"},
    {"city": "Brussels",       "country": "Belgium",       "cc": "BE", "flag": "🇧🇪", "lat": 50.8503,  "lon": 4.3517,    "tz": "Europe/Brussels",                   "slug": "brussels"},
    {"city": "Vienna",         "country": "Austria",       "cc": "AT", "flag": "🇦🇹", "lat": 48.2082,  "lon": 16.3738,   "tz": "Europe/Vienna",                     "slug": "vienna"},
    {"city": "Zurich",         "country": "Switzerland",   "cc": "CH", "flag": "🇨🇭", "lat": 47.3769,  "lon": 8.5417,    "tz": "Europe/Zurich",                     "slug": "zurich"},
    {"city": "Stockholm",      "country": "Sweden",        "cc": "SE", "flag": "🇸🇪", "lat": 59.3293,  "lon": 18.0686,   "tz": "Europe/Stockholm",                  "slug": "stockholm"},
    {"city": "Oslo",           "country": "Norway",        "cc": "NO", "flag": "🇳🇴", "lat": 59.9139,  "lon": 10.7522,   "tz": "Europe/Oslo",                       "slug": "oslo"},
    {"city": "Copenhagen",     "country": "Denmark",       "cc": "DK", "flag": "🇩🇰", "lat": 55.6761,  "lon": 12.5683,   "tz": "Europe/Copenhagen",                 "slug": "copenhagen"},
    {"city": "Helsinki",       "country": "Finland",       "cc": "FI", "flag": "🇫🇮", "lat": 60.1699,  "lon": 24.9384,   "tz": "Europe/Helsinki",                   "slug": "helsinki"},
    {"city": "Warsaw",         "country": "Poland",        "cc": "PL", "flag": "🇵🇱", "lat": 52.2297,  "lon": 21.0122,   "tz": "Europe/Warsaw",                     "slug": "warsaw"},
    {"city": "Prague",         "country": "Czech Republic","cc": "CZ", "flag": "🇨🇿", "lat": 50.0755,  "lon": 14.4378,   "tz": "Europe/Prague",                     "slug": "prague"},
    {"city": "Budapest",       "country": "Hungary",       "cc": "HU", "flag": "🇭🇺", "lat": 47.4979,  "lon": 19.0402,   "tz": "Europe/Budapest",                   "slug": "budapest"},
    {"city": "Athens",         "country": "Greece",        "cc": "GR", "flag": "🇬🇷", "lat": 37.9838,  "lon": 23.7275,   "tz": "Europe/Athens",                     "slug": "athens"},
    {"city": "Lisbon",         "country": "Portugal",      "cc": "PT", "flag": "🇵🇹", "lat": 38.7223,  "lon": -9.1393,   "tz": "Europe/Lisbon",                     "slug": "lisbon"},
    {"city": "Moscow",         "country": "Russia",        "cc": "RU", "flag": "🇷🇺", "lat": 55.7558,  "lon": 37.6176,   "tz": "Europe/Moscow",                     "slug": "moscow"},
    {"city": "Istanbul",       "country": "Turkey",        "cc": "TR", "flag": "🇹🇷", "lat": 41.0082,  "lon": 28.9784,   "tz": "Europe/Istanbul",                   "slug": "istanbul"},
    {"city": "Dubai",          "country": "UAE",           "cc": "AE", "flag": "🇦🇪", "lat": 25.2048,  "lon": 55.2708,   "tz": "Asia/Dubai",                        "slug": "dubai"},
    {"city": "Abu Dhabi",      "country": "UAE",           "cc": "AE", "flag": "🇦🇪", "lat": 24.4539,  "lon": 54.3773,   "tz": "Asia/Dubai",                        "slug": "abu-dhabi"},
    {"city": "Riyadh",         "country": "Saudi Arabia",  "cc": "SA", "flag": "🇸🇦", "lat": 24.7136,  "lon": 46.6753,   "tz": "Asia/Riyadh",                       "slug": "riyadh"},
    {"city": "Doha",           "country": "Qatar",         "cc": "QA", "flag": "🇶🇦", "lat": 25.2854,  "lon": 51.5310,   "tz": "Asia/Qatar",                        "slug": "doha"},
    {"city": "Cairo",          "country": "Egypt",         "cc": "EG", "flag": "🇪🇬", "lat": 30.0444,  "lon": 31.2357,   "tz": "Africa/Cairo",                      "slug": "cairo"},
    {"city": "Lagos",          "country": "Nigeria",       "cc": "NG", "flag": "🇳🇬", "lat": 6.5244,   "lon": 3.3792,    "tz": "Africa/Lagos",                      "slug": "lagos"},
    {"city": "Nairobi",        "country": "Kenya",         "cc": "KE", "flag": "🇰🇪", "lat": -1.2921,  "lon": 36.8219,   "tz": "Africa/Nairobi",                    "slug": "nairobi"},
    {"city": "Johannesburg",   "country": "South Africa",  "cc": "ZA", "flag": "🇿🇦", "lat": -26.2041, "lon": 28.0473,   "tz": "Africa/Johannesburg",               "slug": "johannesburg"},
    {"city": "Cape Town",      "country": "South Africa",  "cc": "ZA", "flag": "🇿🇦", "lat": -33.9249, "lon": 18.4241,   "tz": "Africa/Johannesburg",               "slug": "cape-town"},
    {"city": "Tokyo",          "country": "Japan",         "cc": "JP", "flag": "🇯🇵", "lat": 35.6762,  "lon": 139.6503,  "tz": "Asia/Tokyo",                        "slug": "tokyo"},
    {"city": "Osaka",          "country": "Japan",         "cc": "JP", "flag": "🇯🇵", "lat": 34.6937,  "lon": 135.5023,  "tz": "Asia/Tokyo",                        "slug": "osaka"},
    {"city": "Seoul",          "country": "South Korea",   "cc": "KR", "flag": "🇰🇷", "lat": 37.5665,  "lon": 126.9780,  "tz": "Asia/Seoul",                        "slug": "seoul"},
    {"city": "Beijing",        "country": "China",         "cc": "CN", "flag": "🇨🇳", "lat": 39.9042,  "lon": 116.4074,  "tz": "Asia/Shanghai",                     "slug": "beijing"},
    {"city": "Shanghai",       "country": "China",         "cc": "CN", "flag": "🇨🇳", "lat": 31.2304,  "lon": 121.4737,  "tz": "Asia/Shanghai",                     "slug": "shanghai"},
    {"city": "Hong Kong",      "country": "Hong Kong",     "cc": "HK", "flag": "🇭🇰", "lat": 22.3193,  "lon": 114.1694,  "tz": "Asia/Hong_Kong",                    "slug": "hong-kong"},
    {"city": "Singapore",      "country": "Singapore",     "cc": "SG", "flag": "🇸🇬", "lat": 1.3521,   "lon": 103.8198,  "tz": "Asia/Singapore",                    "slug": "singapore"},
    {"city": "Bangkok",        "country": "Thailand",      "cc": "TH", "flag": "🇹🇭", "lat": 13.7563,  "lon": 100.5018,  "tz": "Asia/Bangkok",                      "slug": "bangkok"},
    {"city": "Jakarta",        "country": "Indonesia",     "cc": "ID", "flag": "🇮🇩", "lat": -6.2088,  "lon": 106.8456,  "tz": "Asia/Jakarta",                      "slug": "jakarta"},
    {"city": "Manila",         "country": "Philippines",   "cc": "PH", "flag": "🇵🇭", "lat": 14.5995,  "lon": 120.9842,  "tz": "Asia/Manila",                       "slug": "manila"},
    {"city": "Kuala Lumpur",   "country": "Malaysia",      "cc": "MY", "flag": "🇲🇾", "lat": 3.1390,   "lon": 101.6869,  "tz": "Asia/Kuala_Lumpur",                 "slug": "kuala-lumpur"},
    {"city": "Mumbai",         "country": "India",         "cc": "IN", "flag": "🇮🇳", "lat": 19.0760,  "lon": 72.8777,   "tz": "Asia/Kolkata",                      "slug": "mumbai"},
    {"city": "Delhi",          "country": "India",         "cc": "IN", "flag": "🇮🇳", "lat": 28.7041,  "lon": 77.1025,   "tz": "Asia/Kolkata",                      "slug": "delhi"},
    {"city": "Sydney",         "country": "Australia",     "cc": "AU", "flag": "🇦🇺", "lat": -33.8688, "lon": 151.2093,  "tz": "Australia/Sydney",                  "slug": "sydney"},
    {"city": "Melbourne",      "country": "Australia",     "cc": "AU", "flag": "🇦🇺", "lat": -37.8136, "lon": 144.9631,  "tz": "Australia/Melbourne",               "slug": "melbourne"},
    {"city": "Auckland",       "country": "New Zealand",   "cc": "NZ", "flag": "🇳🇿", "lat": -36.8485, "lon": 174.7633,  "tz": "Pacific/Auckland",                  "slug": "auckland"},
]

BASE_URL = "https://worldtimeclock.com"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "city")

def read_template():
    tpl_path = os.path.join(OUTPUT_DIR, "_template.html")
    with open(tpl_path, encoding="utf-8") as f:
        return f.read()

def generate_page(city, template):
    """Gera HTML estático com metadados da cidade inseridos no head."""
    c = city
    title    = f"Current Time in {c['city']}, {c['country']} — WorldTime.live"
    desc     = (f"What time is it in {c['city']}, {c['country']} right now? "
                f"Check the live local time, date, UTC offset ({c['tz']}) "
                f"and current weather conditions.")
    canon    = f"{BASE_URL}/city/{c['slug']}.html"
    og_img   = f"{BASE_URL}/og-image.jpg"
    
    html = template
    # Injeta title/meta antes do JS dinâmico (para crawlers)
    static_head = f"""
  <!-- Static SEO (for crawlers) -->
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <link rel="canonical" href="{canon}">
  <meta property="og:title" content="Current Time in {c['city']}">
  <meta property="og:description" content="{desc}">
  <meta property="og:url" content="{canon}">
  <meta property="og:image" content="{og_img}">
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "WebPage",
    "name": "{title}",
    "description": "{desc}",
    "url": "{canon}",
    "about": {{
      "@type": "City",
      "name": "{c['city']}",
      "containedInPlace": {{"@type": "Country", "name": "{c['country']}"}}
    }}
  }}
  </script>"""

    html = html.replace("<!-- Static SEO -->", static_head, 1)
    return html

def generate_sitemap(cities):
    urls = [f"  <url><loc>{BASE_URL}/</loc><changefreq>hourly</changefreq><priority>1.0</priority></url>"]
    urls.append(f"  <url><loc>{BASE_URL}/cities.html</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>")
    for c in cities:
        urls.append(
            f"  <url>"
            f"<loc>{BASE_URL}/city/{c['slug']}.html</loc>"
            f"<changefreq>hourly</changefreq>"
            f"<priority>0.9</priority>"
            f"</url>"
        )
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sitemap += "\n".join(urls)
    sitemap += "\n</urlset>"
    return sitemap

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    template = read_template()

    print(f"Generating {len(CITIES)} city pages...")
    for city in CITIES:
        html = generate_page(city, template)
        out_path = os.path.join(OUTPUT_DIR, f"{city['slug']}.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"  ✓ {city['slug']}.html")

    # Sitemap
    sitemap = generate_sitemap(CITIES)
    sitemap_path = os.path.join(os.path.dirname(__file__), "sitemap.xml")
    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write(sitemap)
    print(f"\n✓ sitemap.xml gerado com {len(CITIES) + 2} URLs")
    print("\n✅ Geração concluída!")

if __name__ == "__main__":
    main()
