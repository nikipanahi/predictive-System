# MRO Inventory Predictive System & Dashboard

This repository contains the source code for the Django-based MRO (Maintenance, Repair, and Overhaul) inventory management system.

---

## 📌 Project Overview
The system optimizes MRO spare-parts inventory using machine learning models integrated with a web dashboard.

Key features:
* **Predictive Analytics:** ML models for repair estimation.
* **Inventory Control:** Real-time stock tracking.

---

## 🛠️ Prerequisites
* **Python:** 3.10 or higher
* **Dependencies:** Listed in `aviation_project_file/requirements.txt`

---

## 🚀 Installation & Quick Start

Follow these steps to replicate the local environment:

### 1. Clone the Repository

Run this in your terminal:
```bash
git clone https://github.com/nikipanahi/predictive-system.git
cd predictive-system/aviation_project_file

```
### 2. Create Virtual Environment
Choose your OS command:
* **Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\activate
  ```
* **Linux / macOS:**
```bash
  python3 -m venv venv
  source venv/bin/activate
```
### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
### 4. Apply Database Migrations
```bash
python manage.py migrate
```
### 5. Run the Server
```bash
python manage.py runserver
```
Access at: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
### 🔑 Demo Credentials (For Peer Review)
* **Admin URL:** [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
* **Username:** demo-admin
* **Password:** mroadmin
