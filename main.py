scraper_code = '''import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from urllib.parse import urljoin, urlparse
import json
from typing import List, Dict, Optional
import re

class RekvizitaiScraper:
    """
    Universalus scraper'is rekvizitai.vz.lt įmonių katalogo duomenims surinkti
    """
    
    def __init__(self, base_url: str = "https://rekvizitai.vz.lt"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'lt-LT,lt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
        self.companies_data = []
        
    def get_page(self, url: str, delay: float = 1.0) -> Optional[BeautifulSoup]:
        """Gauti puslapio turinį su rate limiting"""
        try:
            time.sleep(delay)  # Rate limiting
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"Klaida gaunant {url}: {e}")
            return None
    
    def get_categories(self) -> List[Dict[str, str]]:
        """Surinkti visas verslo kategorijas"""
        soup = self.get_page(self.base_url)
        if not soup:
            return []
        
        categories = []
        # Ieškoti kategorijų sąrašo
        category_links = soup.find_all('a', href=re.compile(r'/imones/'))
        
        for link in category_links:
            cat_name = link.get_text(strip=True)
            cat_url = urljoin(self.base_url, link['href'])
            if cat_name and cat_url:
                categories.append({
                    'name': cat_name,
                    'url': cat_url
                })
        
        return categories
    
    def scrape_company_list(self, category_url: str, max_pages: int = 5) -> List[str]:
        """Surinkti įmonių URL iš kategorijos puslapių"""
        company_urls = []
        
        for page_num in range(1, max_pages + 1):
            # Daugelis katalogų naudoja ?page= ar /page/ struktūrą
            if '?' in category_url:
                page_url = f"{category_url}&page={page_num}"
            else:
                page_url = f"{category_url}?page={page_num}"
            
            soup = self.get_page(page_url)
            if not soup:
                break
            
            # Ieškoti įmonių nuorodų (adaptuoti pagal tikrą svetainės struktūrą)
            company_links = soup.find_all('a', href=re.compile(r'/imone/|/company/'))
            
            if not company_links:
                break
            
            for link in company_links:
                company_url = urljoin(self.base_url, link['href'])
                if company_url not in company_urls:
                    company_urls.append(company_url)
            
            print(f"Surinkta {len(company_urls)} įmonių URL iš {page_num} puslapių...")
        
        return company_urls
    
    def scrape_company_details(self, company_url: str) -> Optional[Dict]:
        """Surinkti detalią informaciją apie įmonę"""
        soup = self.get_page(company_url)
        if not soup:
            return None
        
        company_data = {
            'url': company_url,
            'pavadinimas': None,
            'imones_kodas': None,
            'adresas': None,
            'telefonas': None,
            'el_pastas': None,
            'svetaine': None,
            'veiklos_sritis': None,
            'darbuotoju_skaicius': None,
            'steigimo_data': None,
        }
        
        # Pavadinimas (paprastai h1 arba .company-name)
        title = soup.find('h1') or soup.find(class_=re.compile('company.*name|title'))
        if title:
            company_data['pavadinimas'] = title.get_text(strip=True)
        
        # Įmonės kodas
        code_elem = soup.find(text=re.compile(r'Įmonės kodas|Kodas'))
        if code_elem:
            code_parent = code_elem.find_parent()
            if code_parent:
                code_text = code_parent.get_text(strip=True)
                code_match = re.search(r'\\d{9}', code_text)
                if code_match:
                    company_data['imones_kodas'] = code_match.group()
        
        # Adresas
        address_elem = soup.find(text=re.compile(r'Adresas|Address'))
        if address_elem:
            addr_parent = address_elem.find_parent()
            if addr_parent:
                company_data['adresas'] = addr_parent.get_text(strip=True).replace('Adresas:', '').strip()
        
        # Telefonas
        phone = soup.find('a', href=re.compile(r'tel:'))
        if phone:
            company_data['telefonas'] = phone.get_text(strip=True)
        
        # El. paštas
        email = soup.find('a', href=re.compile(r'mailto:'))
        if email:
            company_data['el_pastas'] = email['href'].replace('mailto:', '')
        
        # Svetainė
        website = soup.find('a', href=re.compile(r'http'), text=re.compile(r'www\\.'))
        if website:
            company_data['svetaine'] = website['href']
        
        return company_data
    
    def scrape_category(self, category_name: str, category_url: str, 
                       max_pages: int = 3, max_companies: int = 50):
        """Scrape'inti visą kategoriją"""
        print(f"\\n{'='*60}")
        print(f"Pradedamas scraping: {category_name}")
        print(f"{'='*60}")
        
        # 1. Surinkti įmonių URL
        company_urls = self.scrape_company_list(category_url, max_pages)
        company_urls = company_urls[:max_companies]  # Limitas
        
        print(f"Rasta {len(company_urls)} įmonių. Renkama detali informacija...")
        
        # 2. Surinkti kiekvienos įmonės detales
        for idx, url in enumerate(company_urls, 1):
            print(f"  [{idx}/{len(company_urls)}] Scraping'inama: {url}")
            company_data = self.scrape_company_details(url)
            if company_data:
                company_data['kategorija'] = category_name
                self.companies_data.append(company_data)
        
        print(f"Baigta. Surinkta {len([c for c in self.companies_data if c['kategorija'] == category_name])} įmonių.")
    
    def save_to_csv(self, filename: str = "imones_duomenys.csv"):
        """Išsaugoti duomenis CSV formatu"""
        if not self.companies_data:
            print("Nėra duomenų išsaugojimui!")
            return
        
        df = pd.DataFrame(self.companies_data)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"\\nDuomenys išsaugoti: {filename}")
        print(f"Iš viso įmonių: {len(df)}")
        return df
    
    def save_to_json(self, filename: str = "imones_duomenys.json"):
        """Išsaugoti duomenis JSON formatu"""
        if not self.companies_data:
            print("Nėra duomenų išsaugojimui!")
            return
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.companies_data, f, ensure_ascii=False, indent=2)
        print(f"Duomenys išsaugoti: {filename}")


# ============================================================================
# NAUDOJIMO PAVYZDYS
# ============================================================================

def main():
    """Pagrindinis scraping scenarijus"""
    
    # Inicijuoti scraper'į
    scraper = RekvizitaiScraper()
    
    # VARIANTAS 1: Scrape'inti konkrečią kategoriją
    # Pavyzdžiui, IT įmones
    scraper.scrape_category(
        category_name="IT ir programinė įranga",
        category_url="https://rekvizitai.vz.lt/imones/kompiuteriai-ir-programine-iranga/",
        max_pages=2,  # Kiek puslapių scrape'inti
        max_companies=20  # Maksimalus įmonių skaičius
    )
    
    # VARIANTAS 2: Scrape'inti kelias kategorijas
    categories_to_scrape = [
        {
            "name": "Statybos įmonės",
            "url": "https://rekvizitai.vz.lt/imones/statyba/"
        },
        {
            "name": "Transporto paslaugos",
            "url": "https://rekvizitai.vz.lt/imones/transporto-paslaugos/"
        }
    ]
    
    # for cat in categories_to_scrape:
    #     scraper.scrape_category(
    #         category_name=cat["name"],
    #         category_url=cat["url"],
    #         max_pages=2,
    #         max_companies=15
    #     )
    
    # VARIANTAS 3: Automatiškai surinkti visas kategorijas
    # print("Renkamos visos kategorijos...")
    # all_categories = scraper.get_categories()
    # print(f"Rasta {len(all_categories)} kategorijų")
    # 
    # for cat in all_categories[:5]:  # Pirmos 5 kategorijos
    #     scraper.scrape_category(
    #         category_name=cat["name"],
    #         category_url=cat["url"],
    #         max_pages=1,
    #         max_companies=10
    #     )
    
    # Išsaugoti duomenis
    df = scraper.save_to_csv("imones_duomenys.csv")
    scraper.save_to_json("imones_duomenys.json")
    
    # Parodyti pavyzdinę statistiką
    if df is not None and not df.empty:
        print("\\n" + "="*60)
        print("STATISTIKA:")
        print("="*60)
        print(f"Iš viso įmonių: {len(df)}")
        print(f"\\nĮmonių pagal kategorijas:")
        print(df['kategorija'].value_counts())
        print(f"\\nĮmonių su telefonu: {df['telefonas'].notna().sum()}")
        print(f"Įmonių su el. paštu: {df['el_pastas'].notna().sum()}")
        print(f"Įmonių su svetaine: {df['svetaine'].notna().sum()}")


if __name__ == "__main__":
    main()
'''

# Išsaugoti į Python failą
with open('rekvizitai_scraper.py', 'w', encoding='utf-8') as f:
    f.write(scraper_code)

print("✓ Scraper failas išsaugotas: rekvizitai_scraper.py")
print("\n" + "="*70)
print("KAIP NAUDOTI:")
print("="*70)
print("\n1. Paleisti scenarijų:")
print("   python rekvizitai_scraper.py")
print("\n2. Arba importuoti į savo kodą:")
print("   from rekvizitai_scraper import RekvizitaiScraper")
print("   scraper = RekvizitaiScraper()")
print("   scraper.scrape_category(...)")
