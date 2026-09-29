import pytest

from app.services.resume_fallback import extract_fallback_profile


@pytest.mark.parametrize('text', ['', 'Office administration and payroll.', 'Experienced accountant with excellent communication.'])
def test_unrecognized_resume_does_not_invent_technical_skills(text):
    profile = extract_fallback_profile(text, 'resume.txt')
    assert profile.competencies == []
    assert profile.history == []
    assert profile.profile_metadata.confidence_score == 0.0


def test_complete_names_do_not_create_substring_skills_or_proficiency():
    profile = extract_fallback_profile('JavaScript, PostgreSQL, React and C++. python/PYTHON.', 'resume.txt')
    assert {skill.name for skill in profile.competencies} == {'JavaScript', 'PostgreSQL', 'React', 'C++', 'Python'}
    assert all(skill.level is None for skill in profile.competencies)
    assert len(profile.competencies) == 5


def test_single_letter_c_requires_a_standalone_mention():
    profile = extract_fallback_profile('Languages: C, C# and Java.', 'resume.txt')
    assert {skill.name for skill in profile.competencies} == {'C', 'Java'}
