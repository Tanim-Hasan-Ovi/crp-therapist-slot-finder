# CRP Bangladesh Appointment Slot Finder

A personal automated tool built with Python and Playwright to check available therapy and appointment slots at **CRP Bangladesh** (Centre for the Rehabilitation of the Paralysed).

---

## Why Use This?

Normally, booking or checking appointments at CRP Bangladesh requires selecting a doctor's name, manually inputting dates, and checking slot availability one by one through their portal. 

This tool automates that tedious process by:
- Allowing you to view free appointment and therapy times across multiple doctors simultaneously.
- Giving you a unified view of all open slots without clicking back and forth.
- Authenticating using your official patient ID and password (obtained by signing up at the hospital).

---

## Features

- **Automated Scraping:** Uses Playwright to navigate the CRP portal, select doctors, and pull live slot availability.
- **Multi-Doctor Overview:** Instantly check free schedules for multiple doctors at the same time.
- **Credential-Based Access:** Securely logs in using your legitimate hospital patient credentials.

---

## Requirements

- Python 3.8 or higher
- Playwright

---

## Installation & Setup

1. Clone or download the repository to your local machine.
2. Install the required dependencies using the `requirements.txt` file:
   ```bash
   pip install -r requirements.txt
   app.py
