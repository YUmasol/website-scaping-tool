readme_content = '''# 🕷️ Rekvizitai.lt Web Scraper

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

Automated tool for scraping Lithuanian company data from the rekvizitai.vz.lt directory.

## ✨ Features

- 🔍 **Automatic category detection** - Discovers all catalog categories
- 📊 **Bulk data collection** - Scrape hundreds of companies in minutes
- 🛡️ **Rate limiting** - Protection against IP blocking
- 💾 **Export options** - CSV and JSON formats
- 📈 **Statistics** - Automatic data summary generation
- ⚙️ **Highly configurable** - Adaptable to any category

## 📦 Installation

### Requirements
- Python 3.8+
- pip

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/YUmasol/rekvizitai-scraper.git
cd rekvizitai-scraper

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the scraper
python rekvizitai_scraper.py
```

## 🚀 Usage

### Simple Example

```python
from rekvizitai_scraper import RekvizitaiScraper

# Initialize the scraper
scraper = RekvizitaiScraper()

# Scrape a single category
scraper.scrape_category(
    category_name="IT Companies",
    category_url="https://rekvizitai.vz.lt/imones/kompiuteriai-ir-programine-iranga/",
    max_pages=3,
    max_companies=50
)

# Save results
scraper.save_to_csv("it_companies.csv")
scraper.save_to_json("it_companies.json")
```

### Multiple Scenarios

<details>
<summary><b>Scenario 1: Single Category</b></summary>

```python
scraper = RekvizitaiScraper()

scraper.scrape_category(
    category_name="Construction",
    category_url="https://rekvizitai.vz.lt/imones/statyba/",
    max_pages=5,
    max_companies=100
)

df = scraper.save_to_csv("construction_companies.csv")
```
</details>

<details>
<summary><b>Scenario 2: Multiple Categories</b></summary>

```python
scraper = RekvizitaiScraper()

categories = [
    {"name": "IT", "url": "https://rekvizitai.vz.lt/imones/kompiuteriai-ir-programine-iranga/"},
    {"name": "Construction", "url": "https://rekvizitai.vz.lt/imones/statyba/"},
    {"name": "Transport", "url": "https://rekvizitai.vz.lt/imones/transporto-paslaugos/"}
]

for cat in categories:
    scraper.scrape_category(
        category_name=cat["name"],
        category_url=cat["url"],
        max_pages=2,
        max_companies=30
    )

scraper.save_to_csv("all_companies.csv")
```
</details>

<details>
<summary><b>Scenario 3: Full Catalog</b></summary>

```python
scraper = RekvizitaiScraper()

# Automatically discover all categories
categories = scraper.get_categories()
print(f"Found {len(categories)} categories")

# Scrape first 10 categories
for cat in categories[:10]:
    scraper.scrape_category(
        category_name=cat["name"],
        category_url=cat["url"],
        max_pages=1,
        max_companies=20
    )

scraper.save_to_csv("full_catalog.csv")
```
</details>

## 📋 Data Fields

| Field | Description | Example |
|-------|-------------|---------|
| `pavadinimas` | Company name | UAB "Technologies" |
| `imones_kodas` | 9-digit company code | 123456789 |
| `adresas` | Legal address | Vilnius, Gedimino g. 1 |
| `telefonas` | Contact phone | +370 5 123 4567 |
| `el_pastas` | Email address | info@example.lt |
| `svetaine` | Website URL | www.example.lt |
| `kategorija` | Business category | IT Companies |
| `url` | Profile link | https://rekvizitai.vz.lt/... |

## 📊 Output Formats

### CSV Example
```csv
pavadinimas,imones_kodas,adresas,telefonas,el_pastas,svetaine,kategorija
"UAB Example",123456789,"Vilnius, Gedimino g. 1","+370 5 123 4567","info@example.lt","www.example.lt","IT Companies"
```

### JSON Example
```json
[
  {
    "pavadinimas": "UAB Example",
    "imones_kodas": "123456789",
    "adresas": "Vilnius, Gedimino g. 1",
    "telefonas": "+370 5 123 4567",
    "el_pastas": "info@example.lt",
    "svetaine": "www.example.lt",
    "kategorija": "IT Companies",
    "url": "https://rekvizitai.vz.lt/imone/123456789/"
  }
]
```

## ⚙️ Configuration

### Main Parameters

```python
# RekvizitaiScraper initialization
scraper = RekvizitaiScraper(
    base_url="https://rekvizitai.vz.lt"  # Base URL
)

# scrape_category parameters
scraper.scrape_category(
    category_name="Category Name",     # For statistics
    category_url="https://...",        # Category URL
    max_pages=3,                       # Page limit
    max_companies=50                   # Company limit
)

# Rate limiting
soup = scraper.get_page(url, delay=1.0)  # Seconds between requests
```

## 🛠️ Adapting to Other Websites

To use with a different directory, modify:

1. **base_url** - change the domain
2. **scrape_company_list()** - adapt URL structure
3. **scrape_company_details()** - update CSS selectors

```python
# Example: change selector
class CustomScraper(RekvizitaiScraper):
    def scrape_company_details(self, company_url):
        soup = self.get_page(company_url)
        # Update selectors for new website
        title = soup.find('h2', class_='company-title')  # instead of h1
        # ...
```

## 📈 Statistics Example

```
============================================================
STATISTICS:
============================================================
Total companies: 145

Companies by category:
IT Companies           50
Construction           45
Transport Services     30
Food Production        20

Companies with phone: 128
Companies with email: 98
Companies with website: 115
============================================================
```

## ⚠️ Important Notes

### Legal Aspects
- ✅ Ensure scraping complies with the website's **Terms of Service**
- ✅ Respect **robots.txt** directives
- ✅ Use data only for lawful purposes

### Technical Aspects
- 🕐 Use reasonable delays (min. 1 sec)
- 🔄 Monitor website structure changes
- 💾 Don't upload scraped data to public repositories

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

MIT License - see the [LICENSE](LICENSE) file for details.

## 🐛 Issues and Questions

If you find a bug or have a question, please create an [Issue](https://github.com/YUmasol/rekvizitai-scraper/issues).

## 📧 Contact

Project Author - [@YUmasol](https://github.com/YUmasol)

---

⭐ If this project is useful to you, please give it a star!
'''

with open('README.md', 'w', encoding='utf-8') as f:
    f.write(readme_content)

print("✓ README.md created (English version with username: YUmasol)")
