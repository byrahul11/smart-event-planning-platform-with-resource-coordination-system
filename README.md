# EventHub — Smart Event Planning Platform with Resource Coordination System

A full-stack event registration and management platform built with **Django**, developed as part of the **Infosys Springboard Virtual Internship 7.0 (B1)**. EventHub gives admins a complete toolkit to plan, run, and track campus events, while students get a simple portal to discover events, register, and receive QR-code tickets.

---

## 🚀 Key Features

**Student / Attendee Portal**
- Browse and search events by category
- One-click registration with instant QR-code ticket generation
- Downloadable PDF tickets
- Personal "My Tickets" dashboard
- Event wishlist to save events for later
- Light/dark mode and a personalized theme (font, colors, size)

**Admin Dashboard**
- Role-based access control (Admin / Student, with an Organiser tier in progress)
- Full event and category management, with banner image uploads
- Organizing-team member management (Organizer / Coordinator / Volunteer)
- Image-based QR scanning for attendee check-in
- Real-time notification feed (new events, registrations, completions)

**Finance & Logistics**
- Per-event budget creation and tracking (allocated vs. spent)
- Visual budget-utilization dashboard with Chart.js

**AI Assistant**
- Built-in FAQ chatbot powered by Google Gemini, answering event and registration questions in real time

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Django |
| Frontend | HTML5, CSS3, Bootstrap, JavaScript |
| Database | SQLite (via Django ORM) |
| QR Codes | `qrcode` (generation), OpenCV (scanning) |
| PDF Tickets | ReportLab |
| Charts | Chart.js |
| AI Chatbot | Google Gemini (`google-genai`) |

---

## ⚡ Quick Start

**1. Clone the repo & create a virtual environment**
```bash
git clone https://github.com/byrahul11/smart-event-planning-platform-with-resource-coordination-system.git
cd smart-event-planning-platform-with-resource-coordination-system
python -m venv env
env\Scripts\activate
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Apply migrations & create an admin account**
```bash
python manage.py migrate
python manage.py createsuperuser
```

**4. Run the development server**
```bash
python manage.py runserver
```
Visit **http://127.0.0.1:8000/** — log in with your superuser account for the admin dashboard, or sign up as a student for the attendee portal.

---

## 📂 Project Structure

## License

MIT License
