"""
ApplyMate AI – Frontend Architecture, Accessibility & Design Token Tests
Verifies DOM structure, WCAG 2.2 AA accessibility, routing configs, and brand design tokens.
"""

from pathlib import Path
from bs4 import BeautifulSoup
import json
import pytest

FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"


def test_html_files_exist():
    """Verify all primary application pages are present."""
    required_files = [
        "index.html",
        "login.html",
        "signup.html",
        "dashboard.html",
        "forgot-password.html",
        "reset-password.html",
        "admin.html",
    ]
    for filename in required_files:
        filepath = FRONTEND_DIR / filename
        assert filepath.exists(), f"Missing required page: {filename}"


def test_landing_page_accessibility_and_headings():
    """Verify landing page adheres to WCAG 2.2 AA accessibility standards."""
    html_path = FRONTEND_DIR / "index.html"
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "lxml")

    # 1. Document language
    html_tag = soup.find("html")
    assert html_tag is not None
    assert html_tag.get("lang") == "en"

    # 2. Skip to content link
    skip_link = soup.find("a", class_="skip-link")
    assert skip_link is not None
    assert skip_link.get("href") == "#main-content"

    # 3. Main landmarks
    assert soup.find("header") is not None
    assert soup.find("nav") is not None
    assert soup.find("main") is not None
    assert soup.find("footer") is not None

    # 4. Heading hierarchy: h1 must exist
    h1 = soup.find("h1")
    assert h1 is not None
    assert "Never miss the opportunity you've been preparing for." in h1.text

    # 5. Buttons have accessible text or aria-label
    for btn in soup.find_all("button"):
        has_text = bool(btn.get_text(strip=True))
        has_aria = bool(btn.get("aria-label")) or bool(btn.get("title"))
        assert has_text or has_aria, f"Button missing accessible label: {btn}"


def test_login_and_signup_form_accessibility():
    """Verify auth forms have properly associated labels and autocomplete attributes."""
    for page in ["login.html", "signup.html"]:
        html_path = FRONTEND_DIR / page
        soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "lxml")

        # Skip link
        assert soup.find("a", class_="skip-link") is not None

        # Every input has an associated label or aria-label
        inputs = soup.find_all("input")
        assert len(inputs) > 0
        for inp in inputs:
            inp_id = inp.get("id")
            inp_type = inp.get("type", "text")
            if inp_type == "hidden":
                continue
            has_label = bool(soup.find("label", {"for": str(inp_id)}))
            has_aria = bool(inp.get("aria-label"))
            assert has_label or has_aria, f"Input #{inp_id} in {page} missing accessible label"

            # Check autocomplete attribute on key fields
            if inp_type == "email":
                assert inp.get("autocomplete") == "email"


def test_midnight_brand_tokens_in_css():
    """Verify ApplyMate Midnight color system tokens are strictly configured."""
    css_path = FRONTEND_DIR / "css" / "main.css"
    content = css_path.read_text(encoding="utf-8")

    expected_tokens = [
        ("#080B0A", "Main background"),
        ("#101512", "Secondary background"),
        ("#151C18", "Card background"),
        ("#1B2520", "Elevated surfaces"),
        ("#F0F3EF", "Primary text"),
        ("#A1ADA5", "Secondary text"),
        ("#727E76", "Muted text"),
        ("#B6F36B", "Primary accent"),
    ]
    for token, desc in expected_tokens:
        assert token.lower() in content.lower(), f"Missing required Midnight design token: {token} ({desc})"


def test_vercel_clean_urls_and_rewrites():
    """Verify vercel.json specifies clean URLs and rewrites for SPA routing."""
    v_path = FRONTEND_DIR / "vercel.json"
    assert v_path.exists()
    config = json.loads(v_path.read_text(encoding="utf-8"))
    assert config.get("cleanUrls") is True

    sources = [r["source"] for r in config.get("rewrites", [])]
    assert "/login" in sources
    assert "/signup" in sources
    assert "/dashboard" in sources
    assert "/forgot-password" in sources
    assert "/reset-password" in sources

