"""Conservative extraction when an AI parser is unavailable."""
import re

from app.domains.resume.schemas import UniversalProfile


def extract_fallback_profile(text: str, filename: str) -> UniversalProfile:
    # Match complete skill names: C must not match 'experience', Java must not
    # match JavaScript, and SQL must not match PostgreSQL. A mention alone does
    # not establish proficiency or verified experience.
    skills = (
        'Python', 'Java', 'C++', 'C', 'JavaScript', 'TypeScript', 'React',
        'Next.js', 'FastAPI', 'Node.js', 'PostgreSQL', 'MySQL', 'MongoDB',
        'Docker', 'Kubernetes', 'AWS', 'Git', 'Linux', 'System Design',
        'SQL', 'AIML', 'ETL', 'Celery', 'Redis',
    )
    found = [
        {'name': skill, 'category': 'general', 'level': None}
        for skill in skills
        if re.search(r'(?<![\w+#])' + re.escape(skill) + r'(?![\w+#])', text, re.IGNORECASE)
    ]
    return UniversalProfile(
        profile_metadata={'source': filename, 'confidence_score': 0.0},
        competencies=found,
        history=[],
        reasoning_metadata='AI parsing unavailable. Only recognized skill mentions were extracted; proficiency and work history were not inferred.',
    )
