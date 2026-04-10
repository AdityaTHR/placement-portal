# 🎓 Placement Portal 

A full-stack Placement Portal web application developed using Flask, SQLite, and Jinja2.
This system enables seamless interaction between **Students**, **Companies**, and **Admin** for managing placement activities efficiently.

---

## 🚀 Features

### 🔐 Authentication & Role-Based Access

* Secure login and registration system
* Three distinct roles:

  * **Admin**
  * **Company**
  * **Student**
* Role-based dashboards and access control

---

### 👨‍💼 Admin Dashboard

* Approve or reject company registrations
* View all registered students and companies
* Manage placement drives
* Monitor system statistics (students, companies, drives, applications)

---

### 🏢 Company Dashboard

* Create placement drives
* Edit job postings
* View applicants for each drive
* Update application status:

  * Shortlisted
  * Selected
  * Rejected

---

### 🎓 Student Dashboard

* View available placement drives
* Apply for jobs
* Track application history
* View real-time status updates

---

### 📊 Placement Tracking System

* Tracks each student application
* Status flow:

  * **Applied → Shortlisted → Selected / Rejected**

---

### 🔗 REST API (Optional Feature)

* API endpoints available via `/api`
* Documented using `api.yaml`

---

## 🛠️ Tech Stack

* **Backend:** Flask (Python)
* **Database:** SQLite
* **Frontend:** HTML, CSS, Bootstrap
* **Templating:** Jinja2
* **Authentication:** Flask-Login
* **ORM:** Flask-SQLAlchemy

---

## 📂 Project Structure

```
PLACEMENT_PORTAL_IITM/
│
├── routes/
│   ├── auth.py
│   ├── admin.py
│   ├── company.py
│   ├── student.py
│   └── api.py
│
├── templates/
├── static/
│
├── app.py
├── models.py
├── init_db.py
├── requirements.txt
├── api.yaml
└── .gitignore
```

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/AdityaTHR/placement-portal.git
cd placement-portal
```

---

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Initialize Database

```bash
python init_db.py
```

---

### 5️⃣ Run Application

```bash
python app.py
```

---

### 6️⃣ Open in Browser

```
http://127.0.0.1:5000
```

---

## 🧪 Application Flow

1. Register as **Student** or **Company**
2. Admin logs in and approves company registration
3. Company creates placement drives
4. Student applies for drives
5. Company reviews applicants and updates status
6. Student tracks application status in dashboard

---

## 📌 Key Highlights

* Role-Based Access Control (RBAC)
* Modular architecture using Flask Blueprints
* End-to-end placement workflow implementation
* Database relational integrity maintained
* Clean UI using Bootstrap
* REST API integration

---

## 📄 ER Diagram

ER Diagram is included in the project submission.

---

## 📹 Demo Video

Demo video is included in the submission.

---

## 👨‍💻 Author

**Aditya Kashyap Mohanty**
IIT Madras BS Degree Program

---

## 📜 License

This project is developed for academic purposes only.
