# 🏦 SimpleBank — Online Banking Web Application

SimpleBank is a full-stack banking web application built with **Python, Flask, MySQL, HTML, CSS, and JavaScript**.

The application provides a modern banking dashboard where users can securely log in, manage their account, view transactions, manage debit cards, transfer money between registered users, and analyze their financial activity.

---

## ✨ Features

### 🔐 Authentication

* User registration
* User login and logout
* Password hashing using Werkzeug
* Session-based authentication
* Protected banking pages

### 💰 Banking Dashboard

* View total account balance
* View available balance
* View total income
* View total expenses
* View total savings
* View recent transactions
* Financial spending overview

### 💳 Card Management

* Create a debit card
* View card information
* Activate/freeze card
* Unfreeze card
* View card status
* Card details management

### 💸 Money Transfer

* Transfer money between registered users
* Search recipient using mobile number
* Recipient validation
* Insufficient-balance validation
* Sender and recipient transaction records
* Automatic balance synchronization

### 📊 Financial Analytics

* Income vs expenses analysis
* Monthly financial activity
* Current month analysis
* Previous month analysis
* Last 6 months analysis
* Interactive charts using Chart.js

### 💵 Account Management

* Add money transaction simulation
* Automatic account balance calculation
* Transaction history
* Account information

### ⚙️ Settings

* Update profile information
* Update email address
* Update mobile number
* Change password

---

## 🛠️ Technologies Used

### Backend

* Python
* Flask
* Flask-CORS
* Werkzeug

### Frontend

* HTML5
* CSS3
* JavaScript
* Chart.js

### Database

* MySQL

### Security

* Password hashing
* Session-based authentication
* Protected API endpoints
* Input validation

---

## 📁 Project Structure

```text
SimpleBank/
│
├── app.py
├── requirements.txt
├── .gitignore
├── README.md
├── .env
│
├── templates/
│   ├── login.html
│   ├── dashboard.html
│   ├── cards.html
│   ├── transactions.html
│   ├── analytics.html
│   ├── transfer.html
│   └── settings.html
│
└── static/
    │
    ├── css/
    │   ├── login.css
    │   ├── dashboard.css
    │   ├── cards.css
    │   ├── transactions.css
    │   ├── analytics.css
    │   ├── transfer.css
    │   └── settings.css
    │
    └── js/
        ├── login.js
        ├── dashboard.js
        ├── cards.js
        ├── transactions.js
        ├── analytics.js
        ├── transfer.js
        └── settings.js
```

---

## 🗄️ Database

SimpleBank uses **MySQL** as its relational database.

The application stores information such as:

* User accounts
* User profile information
* Bank account details
* Transactions
* Debit card information

The backend communicates with MySQL using:

```text
mysql-connector-python
```

---

## 🔄 Application Flow

```text
User
 │
 ▼
Login / Registration
 │
 ▼
Flask Backend
 │
 ├──────────────► MySQL Database
 │
 ▼
Dashboard
 │
 ├── Account Balance
 ├── Income
 ├── Expenses
 ├── Transactions
 ├── Cards
 ├── Transfers
 └── Analytics
```

---

## 📊 Financial Analytics

The dashboard provides an interactive **Income vs Expenses** visualization.

Chart.js is used on the frontend to display financial data retrieved from the Flask backend.

The dashboard supports:

* This Month
* Last Month
* Last 6 Months

The backend calculates the required financial data from MySQL and exposes it through an API endpoint.

---

## 🔌 API Endpoints

Some of the main API endpoints include:

| Method | Endpoint                        | Purpose                       |
| ------ | ------------------------------- | ----------------------------- |
| POST   | `/api/register`                 | Register a new user           |
| POST   | `/api/login`                    | Authenticate user             |
| POST   | `/api/add-money`                | Add a credit transaction      |
| GET    | `/api/dashboard-chart`          | Retrieve dashboard chart data |
| POST   | `/api/transfer`                 | Transfer money                |
| POST   | `/api/check-recipient`          | Validate recipient            |
| POST   | `/api/cards/create`             | Create debit card             |
| POST   | `/api/cards/toggle-freeze`      | Freeze/unfreeze card          |
| GET    | `/api/cards/<card_id>`          | Retrieve card details         |
| POST   | `/api/settings/profile`         | Update user profile           |
| POST   | `/api/settings/change-password` | Change password               |

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/AmithValluri07/SimpleBank.git
```

### 2. Navigate into the project

```bash
cd SimpleBank
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

### Windows

```bash
venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🗄️ MySQL Configuration

Create a MySQL database named:

```sql
CREATE DATABASE simplebank;
```

Create the required tables according to the database schema used by the application.

Configure your database credentials using environment variables.

Example:

```env
DB_PASSWORD=your_mysql_password
```

**Do not commit `.env` to GitHub.**

---

## ▶️ Run the Application

Start the Flask application:

```bash
python app.py
```

The application will run locally at:

```text
http://127.0.0.1:5000
```

Open the address in your browser.

---

## 🔐 Security

The project includes several basic security practices:

* Passwords are stored using secure password hashing.
* User sessions are used to protect authenticated pages.
* Database queries use parameterized SQL queries.
* Sensitive environment variables are excluded from Git.
* API endpoints validate authenticated users.
* User-specific database records are protected using the logged-in user's ID.

> This project is intended as an educational/portfolio banking application and is not designed for handling real financial transactions.

---

## 🚀 Future Improvements

Possible future improvements include:

* Real bank/payment gateway integration
* OTP authentication
* Two-factor authentication
* Email notifications
* Transaction receipts
* Advanced fraud detection
* Production database deployment
* Docker containerization
* Cloud deployment
* Improved API authentication
* Automated testing

---

## 🎯 Project Purpose

This project was developed as a **full-stack portfolio project** to demonstrate practical experience with:

* Python
* Flask
* REST APIs
* MySQL
* HTML
* CSS
* JavaScript
* Database operations
* Authentication
* Session management
* CRUD operations
* Financial data visualization
* Frontend-backend integration

---

## 👨‍💻 Author

**Amith Valluri**

B.Tech — Information Technology
2026 Graduate

GitHub: **AmithValluri07**

---

## 📌 Disclaimer

SimpleBank is a **student/portfolio project** created for learning and demonstration purposes.

It does not connect to real banking systems or process real-world financial transactions.
