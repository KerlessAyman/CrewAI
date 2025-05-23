from analyze_job_titles import *
def extract_skills_from_description(description, skill_keywords):
    found_skills = []
    desc_lower = description.lower()
    for skill in skill_keywords:
        if skill.lower() in desc_lower:
            found_skills.append(skill)
    return list(set(found_skills))  # إزالة التكرار
from collections import Counter

def analyze_jobs(jobs, skill_keywords):
    titles = [job['title'] for job in jobs]
    locations = [job['location'] for job in jobs]

    # جمع كل المهارات في كل الوظائف
    all_skills = []
    for job in jobs:
        skills = extract_skills_from_description(job.get('description', ''), skill_keywords)
        all_skills.extend(skills)

    # العد والتكرار
    title_counts = Counter(titles)
    skill_counts = Counter(all_skills)
    location_counts = Counter(locations)

    return title_counts.most_common(), skill_counts.most_common(), location_counts.most_common()
if __name__ == "__main__":
  
    jobs_data = scrape_wuzzuf_with_desc(query="Machine Learning", location="Egypt", max_pages=2)

    skill_keywords = ["Python", "TensorFlow", "PyTorch", "Deep Learning", "NLP", "SQL", "Docker", "Keras", "Scikit-learn"]

    top_titles, top_skills, top_locations = analyze_jobs(jobs_data, skill_keywords)

    print("Top Job Titles:")
    for title, count in top_titles[:10]:
        print(f"{title}: {count}")

    print("\nTop Skills:")
    for skill, count in top_skills[:10]:
        print(f"{skill}: {count}")

    print("\nJob Locations Distribution:")
    for loc, count in top_locations:
        print(f"{loc}: {count}")
