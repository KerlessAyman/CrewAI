import requests
from bs4 import BeautifulSoup
import time

def scrape_wuzzuf(query="AI", location="Egypt", max_pages=3):
    jobs = []
    base_url = f"https://wuzzuf.net/search/jobs/?q={query}&a=hpb&l={location}"

    for page in range(max_pages):
        start = page * 10
        url = base_url + f"&start={start}"
        print(f"Scraping page {page+1}: {url}")
        resp = requests.get(url)
        if resp.status_code != 200:
            print(f"Failed to retrieve page {page+1}")
            break

        soup = BeautifulSoup(resp.text, "html.parser")
        job_cards = soup.find_all('div', class_='css-1gatmva e1v1l3u10')  # تحقق إذا هذا هو الكلاس الصحيح

        for card in job_cards:
            try:
                title = card.find('h2').text.strip()
                company = card.find('a', class_='css-17s97q8').text.strip()
                loc = card.find('span', class_='css-5wys0k').text.strip()
                link = card.find('a')['href']

                # تأكد أن الرابط كامل
                if link.startswith('http'):
                    full_link = link
                else:
                    full_link = "https://wuzzuf.net" + link

                jobs.append({
                    'title': title,
                    'company': company,
                    'location': loc,
                    'link': full_link
                })
            except Exception as e:
                print(f"Error parsing job card: {e}")
                continue

        time.sleep(1)  # احترام السيرفر بتأخير 1 ثانية بين كل صفحة

    return jobs

if __name__ == "__main__":
    data = scrape_wuzzuf(query="Machine Learning", location="Egypt", max_pages=2)
    print(f"Total jobs scraped: {len(data)}")
    for job in data[:3]:  # عرض أول 3 وظائف كمثال
        print(job)
