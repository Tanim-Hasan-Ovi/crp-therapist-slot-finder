import time

from playwright.sync_api import sync_playwright

LOGIN_URL = "http://eappt-mirpur.crp-bangladesh.org:8002/apex/f?p=150:5:5744853320245::NO:5:"
SERVICE_LABEL = "Autism Corner Service"

UNIT_LABELS = {
    "OT": "Autism Corner (OT)",
    "SLT": "Autism Corner (SLT)",
    "GROUP_OT": "Autism Group (OT)",
    "GROUP_SLT": "Autism Group (SLT)",
}

DEFAULT_DOCTOR_QUERY = {
    "OT": "01117",
    "SLT": "00448",
    "GROUP_OT": "",
    "GROUP_SLT": "00804",
}

POLL_MS = 300
REQUIRED_STABLE_READS = 3
STABLE_TIMEOUT_MS = 8000


def _option_texts(page, selector):
    return [t.strip() for t in page.locator(f"{selector} option").all_inner_texts()]


def _read_stable_options(page, selector, poll_ms=POLL_MS, required_stable=REQUIRED_STABLE_READS, timeout_ms=STABLE_TIMEOUT_MS):
    # APEX's cascading dropdowns update via AJAX after a short client-side delay that
    # networkidle does not reliably capture (the request hasn't started yet when
    # networkidle resolves). Polling until the option list is unchanged across several
    # consecutive reads avoids reading a stale/empty list mid-update.
    deadline = time.monotonic() + timeout_ms / 1000
    prev = None
    stable_count = 0
    last = []
    while time.monotonic() < deadline:
        page.wait_for_timeout(poll_ms)
        current = _option_texts(page, selector)
        last = current
        if current == prev:
            stable_count += 1
            if stable_count >= required_stable:
                return current
        else:
            stable_count = 1
        prev = current
    return last


def _select_and_wait(page, select_selector, label, read_selector):
    page.select_option(select_selector, label=label)
    page.wait_for_load_state("networkidle", timeout=20000)
    return _read_stable_options(page, read_selector)


def search_appointments(username, password, unit_key, doctor_query, headless=True):
    unit_label = UNIT_LABELS.get(unit_key)
    if not unit_label:
        return {"ok": False, "error": f"Unknown unit '{unit_key}'"}

    query = (doctor_query or "").strip() or DEFAULT_DOCTOR_QUERY[unit_key]
    query_lower = query.lower()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        try:
            page.goto(LOGIN_URL, wait_until="networkidle", timeout=30000)
            page.fill("#P101_USERNAME", username)
            page.fill("#P101_PASSWORD", password)
            page.click("#B16402616618442493")
            page.wait_for_load_state("networkidle", timeout=20000)

            if "Login Page" in (page.title() or ""):
                return {"ok": False, "error": "Invalid patient code or password."}

            page.click("text=Appointment Scheduling and Payment")
            page.wait_for_load_state("networkidle", timeout=20000)

            if page.locator("#P5_PFN_ID").count() == 0:
                return {"ok": False, "error": "Could not reach the appointment booking form."}

            _select_and_wait(page, "#P5_PFN_ID", SERVICE_LABEL, "#P5_DEPTS_ID")
            _select_and_wait(page, "#P5_DEPTS_ID", unit_label, "#P5_ADM_ID")

            date_options = []
            for opt in page.locator("#P5_ADM_ID option").all():
                value = opt.get_attribute("value")
                text = (opt.inner_text() or "").strip()
                if value:
                    date_options.append(text)

            matched_doctor_name = None
            results = []
            dates_checked = 0
            dates_doctor_unavailable = 0

            for date_text in date_options:
                doctor_texts = _select_and_wait(page, "#P5_ADM_ID", date_text, "#P5_AM_ID")
                dates_checked += 1

                doctor_label = next(
                    (t for t in doctor_texts if t and query_lower in t.lower()), None
                )
                if not doctor_label:
                    dates_doctor_unavailable += 1
                    continue

                matched_doctor_name = doctor_label
                schedule_texts = _select_and_wait(page, "#P5_AM_ID", doctor_label, "#P5_TS_ID")

                times = [t for t in schedule_texts if t]
                if times:
                    results.append({"date": date_text, "times": times})

            return {
                "ok": True,
                "unit": unit_label,
                "doctor_query": query,
                "matched_doctor_name": matched_doctor_name,
                "dates_checked": dates_checked,
                "dates_doctor_unavailable": dates_doctor_unavailable,
                "available": results,
            }
        except Exception as exc:
            return {"ok": False, "error": f"Automation error: {exc}"}
        finally:
            browser.close()
