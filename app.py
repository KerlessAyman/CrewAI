import streamlit as st
import time
import requests
from bs4 import BeautifulSoup
from collections import Counter

# --- Scraper functions ---

def get_job_description(job_url):
    try:
        resp = requests.get(job_url)
        if resp.status_code != 200:
            st.warning(f"Failed to fetch job description: {job_url}")
            return ""

        soup = BeautifulSoup(resp.text, "html.parser")
        desc_div = soup.find('div', class_='css-1m4cuuf')  # Adjust if needed
        if desc_div:
            description = desc_div.get_text(separator=' ').strip()
            return description
        return ""
    except Exception as e:
        st.error(f"Error fetching job description: {e}")
        return ""

def scrape_wuzzuf_with_desc(query="AI", location="Egypt", max_pages=2):
    jobs = []
    base_url = f"https://wuzzuf.net/search/jobs/?q={query}&a=hpb&l={location}"

    for page in range(max_pages):
        start = page * 10
        url = base_url + f"&start={start}"
        st.info(f"Scraping page {page+1}: {url}")
        resp = requests.get(url)
        if resp.status_code != 200:
            st.warning(f"Failed to retrieve page {page+1}")
            break

        soup = BeautifulSoup(resp.text, "html.parser")
        job_cards = soup.find_all('div', class_='css-1gatmva e1v1l3u10')

        for card in job_cards:
            try:
                title = card.find('h2').text.strip()
                company = card.find('a', class_='css-17s97q8').text.strip()
                loc = card.find('span', class_='css-5wys0k').text.strip()
                link = card.find('a')['href']
                full_link = link if link.startswith('http') else "https://wuzzuf.net" + link
                description = get_job_description(full_link)
                jobs.append({
                    'title': title,
                    'company': company,
                    'location': loc,
                    'link': full_link,
                    'description': description
                })
            except Exception as e:
                st.warning(f"Error parsing job card: {e}")
                continue
        time.sleep(1)
    return jobs

# --- Analysis functions ---

def extract_skills_from_description(description, skill_keywords):
    found_skills = []
    desc_lower = description.lower()
    for skill in skill_keywords:
        if skill.lower() in desc_lower:
            found_skills.append(skill)
    return list(set(found_skills))

def analyze_jobs(jobs, skill_keywords):
    titles = [job['title'] for job in jobs]
    locations = [job['location'] for job in jobs]

    all_skills = []
    for job in jobs:
        skills = extract_skills_from_description(job.get('description', ''), skill_keywords)
        all_skills.extend(skills)

    title_counts = Counter(titles)
    skill_counts = Counter(all_skills)
    location_counts = Counter(locations)

    return title_counts.most_common(), skill_counts.most_common(), location_counts.most_common()

# --- Reporting functions ---

def create_trends_summary(top_roles, top_skills):
    if not top_roles or not top_skills:
        return "No data available to create trends summary."
    summary = f"The role '{top_roles[0][0]}' is currently the most demanded position, with {top_roles[0][1]} job postings. "
    summary += f"Key skills in demand include {', '.join([skill for skill, _ in top_skills[:5]])}. "
    summary += "The market shows strong growth in AI/ML jobs across the MENA region, especially in Egypt, UAE, and Saudi Arabia."
    return summary

def generate_markdown_report(top_roles, top_skills, location_distribution, trends_summary):
    md = "# Top AI/ML Jobs in MENA – May 2025\n\n"

    md += "## Top 10 AI/ML Roles\n"
    for i, (role, count) in enumerate(top_roles[:10], 1):
        md += f"{i}. {role} ({count} postings)\n"

    md += "\n## Key Skills Required\n"
    md += ", ".join([skill for skill, _ in top_skills[:15]]) + "\n"

    md += "\n## Country-wise Job Distribution\n"
    for country, count in location_distribution:
        md += f"- {country}: {count} jobs\n"

    md += "\n## Trends & Observations\n"
    md += trends_summary + "\n"

    return md

# --- Streamlit app UI ---

st.title("MENA AI/ML Jobs Dashboard - May 2025")

query = st.text_input("Job Query", value="Machine Learning")
location = st.text_input("Location", value="Egypt")
max_pages = st.slider("Pages to Scrape", min_value=1, max_value=5, value=2)
skill_keywords_input = st.text_area("Skills Keywords (comma separated)", 
                                   value="Python, TensorFlow, PyTorch, Deep Learning, NLP, SQL, Docker, Keras, Scikit-learn")

if st.button("Scrape and Analyze"):
    skill_keywords = [s.strip() for s in skill_keywords_input.split(",") if s.strip()]
    with st.spinner("Scraping jobs... this may take a while."):
        jobs_data = scrape_wuzzuf_with_desc(query=query, location=location, max_pages=max_pages)

    st.success(f"Scraped {len(jobs_data)} jobs.")

    with st.spinner("Analyzing data..."):
        top_roles, top_skills, top_locations = analyze_jobs(jobs_data, skill_keywords)
        trends_summary = create_trends_summary(top_roles, top_skills)
        report_md = generate_markdown_report(top_roles, top_skills, top_locations, trends_summary)

    st.markdown(report_md)

    if st.checkbox("Show raw jobs data"):
        st.write(jobs_data)
