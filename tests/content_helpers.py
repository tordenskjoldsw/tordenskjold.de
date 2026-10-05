from pathlib import Path

SAMPLE_CERTIFICATIONS = """
- name: Example Certification
  exam_code: EX-100
  issuer: Example Issuer
  credential_url: https://example.com/credential
"""


def write_entry(directory: Path, slug: str, front_matter: str, body: str = "") -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / f"{slug}.md").write_text(f"---\n{front_matter}\n---\n{body}")
