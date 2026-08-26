# Event Registration Platform

A full-stack event registration and management system built with Django, developed as part of the **Infosys Springboard Virtual Internship 7.0**.

## About

The platform allows admins to create and manage events, while students can register and receive QR-code tickets for check-in. It includes role-based dashboards, attendance verification, budget tracking, and a customizable theme panel.

**Student:** Rahul Mule — B.Tech 2nd Year, AI & Data Science, TPCT College of Engineering, Osmanabad  
**Status:** Milestone 4 — Feature Enhancement, Testing & Integration

## Features

- Role-based access control (Admin / Student)
- Event and category management
- QR-code ticket generation and scan-based attendance verification
- Finance and budget tracking with charts
- Notifications via Django signals
- Customizable theme panel (colors, fonts, dark mode)
- Event wishlist
- AI-assisted FAQ chatbot

## Tech Stack

**Backend:** Django, Python 
**Frontend:** HTML, CSS, Bootstrap, JavaScript  
**Database:** SQLite

## Setup

```bash
git clone https://github.com/byrahul11/event-registration-platform.git
cd event-registration-platform
python -m venv env
env\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## License

MIT License
