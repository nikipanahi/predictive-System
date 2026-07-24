# MRO Inventory Predictive System & Dashboard

This repository contains the source code for the Django-based MRO (Maintenance, Repair, and Overhaul) inventory management system.
## 🏗️ System Architecture

The system is split into two primary layers to prevent computational bottlenecks on live transactional databases:

1. **Online Transactional Layer (Django):** 
   - Manages live MRO database transactions, user management, and core inventory operations.
   - Handles real-time data entry and part tracking.
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
### 📂 Project Structure
```bash
predictive-system/
└── aviation_project_file/
    ├── mro_app/              # Main Django application
    ├── inventory_site/       # Django configuration
    ├── manage.py             # Django CLI script
    ├── requirements.txt      # Dependencies
    └── db.sqlite3            # Pre-populated database
```
2. **Offline Analytical & Mining Layer (Streamlit):** 
   - A dedicated dashboard (`app.py` / `dashboard_test.py`) for processing historical, unstructured shop-floor logs.
   - Performs heavy analytical computations, data visualization, and performance tracking asynchronously.
   ## 🧠 Machine Learning & Text Mining Methodologies

* **Fuzzy Text Mining:** Utilizes `rapidfuzz` and `scikit-fuzzy` to handle human-written log typos, standardize technical actions, and map complex sub-components dynamically.
* **Predictive Maintenance:** Employs Single-variable Linear Regression for MTTR (Mean Time to Repair) prediction based on Part Numbers.
* **Model Evaluation:** Automated Confusion Matrix generation and live system accuracy calculation against ground-truth labels.

---

## 📂 Repository Structure

```text
├── Offline_Portal/
│   ├── app.py                 # Main Streamlit Analytical Dashboard
│   ├── dashboard_test.py      # Testing and validation script
│   ├── data.json              # Structured historical shop-floor logs
│   └── requirements.txt       # Python dependencies (Streamlit, Pandas, RapidFuzz, etc.)
├── templates/                 # Django HTML templates
├── manage.py                  # Django project manager
└── README.md                  # Project documentation
```
### 🚀 Getting Started
## 1. Run the Offline Analytical Dashboard
Navigate to the analytical directory and run the Streamlit app:
```bash
cd Offline_Portal
streamlit run app.py
```
