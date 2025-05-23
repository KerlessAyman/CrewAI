from scrape_wuzzuf import *
def get_job_description(job_url):
    try:
        resp = requests.get(job_url)
        if resp.status_code != 200:
            print(f"Failed to fetch job description: {job_url}")
            return ""

        soup = BeautifulSoup(resp.text, "html.parser")

      
        desc_div = soup.find('div', class_='css-1m4cuuf') 

        if desc_div:
            description = desc_div.get_text(separator=' ').strip()
            return description
        else:
            return ""

    except Exception as e:
        print(f"Error fetching job description: {e}")
        return ""
def scrape_wuzzuf_with_desc(query="AI", location="Egypt", max_pages=2):
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
        job_cards = soup.find_all('div', class_='css-1gatmva e1v1l3u10')

        for card in job_cards:
            try:
                title = card.find('h2').text.strip()
                company = card.find('a', class_='css-17s97q8').text.strip()
                loc = card.find('span', class_='css-5wys0k').text.strip()
                link = card.find('a')['href']

                if link.startswith('http'):
                    full_link = link
                else:
                    full_link = "https://wuzzuf.net" + link

                description = get_job_description(full_link)

                jobs.append({
                    'title': title,
                    'company': company,
                    'location': loc,
                    'link': full_link,
                    'description': description
                })
            except Exception as e:
                print(f"Error parsing job card: {e}")
                continue

        time.sleep(1)
    return jobs

if __name__ == "__main__":
    jobs_data = scrape_wuzzuf_with_desc(query="Machine Learning", location="Egypt", max_pages=1)
    for job in jobs_data[:3]:
        print(job['title'])
        print(job['description'][:300]) 
        print('-'*50)
