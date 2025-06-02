# 🧑‍💼 Employee Management System (Flask)

This is a **Flask-based Employee Management System** designed to manage HR operations like employee records, departments, attendance, leaves, payroll, and performance evaluations.

---

## 🚀 Features

- 🔐 Authentication & User Roles (Admin / Employee)
- 👥 Employee & Department Management
- 🗓️ Daily Attendance
- 🌴 Leave Application & Approval Workflow
- 💵 Payroll
- 📈 Performance Reviews
- 🧾 REST API with Swagger (via flasgger)

---

## 🧱 Tech Stack

| Component       | Description                  |
| --------------- | ---------------------------- |
| 🐍 Python       | Backend language             |
| 🌐 Flask        | Web framework                |
| 🗃️ SQLAlchemy | ORM for database interaction |
| 🛡 Flask-Login  | Session-based login          |
| 🔐 JWT          | Optional token-based auth    |
| 🧾 Flasgger     | Swagger API docs             |

---

## 🔧 Setup Instructions

1. **Clone Repository**

   ```bash
   git clone https://github.com/deinf/hrsystemapi.git
   cd hrsystemapi
   ```
2. **Create Virtual Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```
4. **Configure Environment**
   Create a `.env` file:

   ```env
   FLASK_APP=src
   FLASK_DEBUG=True
   JWT_SECRET_KEY=your-secret-key
   db_path=sqlite:///database.db  # Or PostgreSQL URI
   admin_password='your-admin-pasword'
   ```
5. **Run Migrations**

   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```
6. **Run App**

   ```bash
   flask run
   ```
   api is located on:

   ```
   http://localhost:5000/api/v1/
   ```
   

---

## 📋 API Endpoints Checklist

You can use this as a dev checklist for what's implemented or still pending:

### ✅ Authentication

- [X] Login and get JWT/token
- [X] Refresh Token

### 👥 Employees

- [X] List all employees
- [X] Add a new employee
- [x] Update employee
- [x] Delete employee

### 🏢 Departments

- [X] List departments
- [X] Add new department
- [x] Update department
- [x] Delete department

### 🕒 Attendance

- [X] Mark check-in/out
- [x] View attendance records
- [x] Delete attendance record

### 🌴 Leave

- [X] Apply for leave
- [x] View leave history
- [x] Approve/Reject leave
- [x] Delete leave record

### 💵 Payroll

- [X] Add payroll entry
- [x] Delete payroll
- [x] View all payroll entries (admin)

### 📈 Performance

- [X] Submit performance review
- [x] View reviews
- [x] Edit review
- [x] Delete review

Soon to be added

---

## 📬 Contact

**Danang Eka Saputra**
GitHub: [@deinf]([https://github.com/yourusername](https://github.com/deinf))
Email: danangekasaputra@outlook.com

---

