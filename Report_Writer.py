from Trend_Analysis import *
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
def create_trends_summary(top_roles, top_skills):
    summary = f"The role '{top_roles[0][0]}' is currently the most demanded position, with {top_roles[0][1]} job postings. "
    summary += f"Key skills in demand include {', '.join([skill for skill, _ in top_skills[:5]])}. "
    summary += "The market shows strong growth in AI/ML jobs across the MENA region, especially in Egypt, UAE, and Saudi Arabia."
    return summary
if __name__ == "__main__":
    # افترض إنك عندك نتائج التحليل من الخطوة السابقة
    top_roles = [('Machine Learning Engineer', 120), ('Data Scientist', 80), ('AI Researcher', 40)]
    top_skills = [('Python', 90), ('TensorFlow', 75), ('Deep Learning', 60), ('NLP', 55), ('SQL', 50)]
    location_distribution = [('Egypt', 150), ('UAE', 70), ('Saudi Arabia', 60)]

    trends_summary = create_trends_summary(top_roles, top_skills)
    report_md = generate_markdown_report(top_roles, top_skills, location_distribution, trends_summary)

    print(report_md)
