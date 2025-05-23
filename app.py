import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
from collections import Counter
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="AI/ML Job Market Analyzer", 
    layout="wide",
    page_icon="🔍"
)

# Title and description
st.title("🔍 AI/ML Job Market Analyzer - MENA Region")
st.markdown("""
This tool scrapes job postings from Wuzzuf based on your search criteria, analyzes required skills, 
and presents insights about the AI/ML job market.
""")

# Sidebar controls
with st.sidebar:
    st.header("⚙️ Search Parameters")
    
    # User inputs
    col1, col2 = st.columns(2)
    with col1:
        job_query = st.text_input("Job Keywords", placeholder="e.g. Machine Learning")
    with col2:
        location = st.text_input("Location", placeholder="e.g. Egypt or Saudi Arabia")
    
    max_pages = st.slider("Number of Pages", 1, 10, 2, help="Each page contains ~10 jobs")
    
    advanced = st.expander("Advanced Options")
    with advanced:
        skill_keywords = st.text_area("Skills to Track (comma-separated)", 
                                    "Python, TensorFlow, PyTorch, Deep Learning, NLP, SQL, Docker, Keras, Scikit-learn")
        skill_list = [skill.strip() for skill in skill_keywords.split(",") if skill.strip()]
    
    st.markdown("---")
    st.markdown("**Note:** Please use responsibly and avoid excessive server requests")

# Job description scraper
def get_job_description(job_url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        resp = requests.get(job_url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return ""
        soup = BeautifulSoup(resp.text, "html.parser")
        desc_div = soup.find('div', class_='css-1m4cuuf') or soup.find('div', class_='css-1uobp1k')
        return desc_div.get_text(separator=' ').strip() if desc_div else ""
    except Exception as e:
        st.error(f"Error fetching description: {str(e)}")
        return ""

# Main scraping function
def scrape_wuzzuf_jobs(query, location, max_pages):
    jobs = []
    base_url = f"https://wuzzuf.net/search/jobs/?q={query}&a=hpb&l={location}"
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for page in range(max_pages):
        current_page = page + 1
        status_text.text(f"Processing page {current_page}/{max_pages}...")
        progress_bar.progress(current_page/max_pages)
        
        url = f"{base_url}&start={page*10}"
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code != 200:
                st.warning(f"Failed to retrieve page {current_page} (Status: {resp.status_code})")
                continue
                
            soup = BeautifulSoup(resp.text, "html.parser")
            job_cards = soup.find_all('div', class_='css-1gatmva e1v1l3u10') or soup.find_all('div', class_='css-1t7spv1')
            
            for card in job_cards:
                try:
                    title = card.find('h2').text.strip()
                    company = card.find('a', class_='css-17s97q8').text.strip()
                    loc = card.find('span', class_='css-5wys0k').text.strip()
                    link = card.find('a')['href']
                    full_link = link if link.startswith('http') else f"https://wuzzuf.net{link}"
                    
                    jobs.append({
                        'Job Title': title,
                        'Company': company,
                        'Location': loc,
                        'Link': full_link,
                        'Page': current_page
                    })
                except Exception as e:
                    continue
                    
            time.sleep(1.5)  # Respectful scraping delay
            
        except Exception as e:
            st.error(f"Error processing page {current_page}: {str(e)}")
            continue
    
    progress_bar.empty()
    status_text.empty()
    
    if not jobs:
        st.error("No jobs found. Please adjust your search criteria.")
        return None
    
    # Get descriptions for top jobs only (for performance)
    with st.spinner("Analyzing job descriptions..."):
        for job in jobs[:50]:  # Limit for performance
            job['Description'] = get_job_description(job['Link'])
    
    return jobs

# Analysis functions
def analyze_results(jobs, skills):
    if not jobs:
        return None, None, None
    
    # Title analysis
    titles = [job['Job Title'] for job in jobs]
    title_counts = Counter(titles).most_common()
    
    # Skill analysis
    all_skills = []
    for job in jobs:
        desc = job.get('Description', '').lower()
        found_skills = [skill for skill in skills if skill.lower() in desc]
        all_skills.extend(found_skills)
    skill_counts = Counter(all_skills).most_common()
    
    # Location analysis
    locations = [job['Location'] for job in jobs]
    location_counts = Counter(locations).most_common()
    
    return title_counts, skill_counts, location_counts

# Main app flow
if st.button("Start Search", type="primary"):
    if not job_query or not location:
        st.warning("Please enter both job keywords and location")
    else:
        with st.spinner("Searching for jobs..."):
            jobs_data = scrape_wuzzuf_jobs(job_query, location, max_pages)
        
        if jobs_data:
            st.success(f"Found {len(jobs_data)} jobs!")
            
            # Analyze data
            titles, skills, locations = analyze_results(jobs_data, skill_list)
            
            # Display results in tabs
            tab1, tab2, tab3 = st.tabs(["Job Listings", "Market Analysis", "Raw Data"])
            
            with tab1:
                st.subheader("Recent Job Postings")
                cols = st.columns(3)
                for idx, job in enumerate(jobs_data[:9]):  # Show 9 jobs in 3x3 grid
                    with cols[idx%3]:
                        with st.expander(f"{job['Job Title'][:30]}..."):
                            st.markdown(f"""
                            **Company:** {job['Company']}  
                            **Location:** {job['Location']}  
                            **Page:** {job['Page']}  
                            [View Job]({job['Link']})
                            """)
                            if job.get('Description'):
                                st.caption(job['Description'][:200] + "...")
            
            with tab2:
                st.subheader("Job Market Insights")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### Top Job Titles")
                    if titles:
                        title_df = pd.DataFrame(titles[:10], columns=['Job Title', 'Count'])
                        st.bar_chart(title_df.set_index('Job Title'))
                    else:
                        st.warning("No title data available")
                
                with col2:
                    st.markdown("#### Most Demanded Skills")
                    if skills:
                        skill_df = pd.DataFrame(skills[:10], columns=['Skill', 'Count'])
                        st.bar_chart(skill_df.set_index('Skill'))
                    else:
                        st.warning("No skill data available")
                
                st.markdown("#### Geographic Distribution")
                if locations:
                    loc_df = pd.DataFrame(locations, columns=['Location', 'Count'])
                    st.dataframe(loc_df)
                else:
                    st.warning("No location data available")
            
            with tab3:
                st.subheader("Complete Job Data")
                st.dataframe(pd.DataFrame(jobs_data), height=500)
                
                # Export button
                csv = pd.DataFrame(jobs_data).to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download as CSV",
                    data=csv,
                    file_name=f"jobs_{job_query}_{location}.csv",
                    mime='text/csv'
                )

else:
    st.info("Click the 'Start Search' button to begin your job market analysis")

# Footer
st.markdown("---")
st.caption("Developed by [Your Name] - © 2023 | Data sourced from Wuzzuf.net")
