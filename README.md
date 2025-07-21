# 🗳️ Online Voting System

A simple and secure web app for online voting, built using **Python Flask** and **MySQL**.  
This system allows users to register, verify their email, vote for candidates, and lets the admin manage everything easily.

---

## ✅ Features

- User sign-up with email verification
- Secure one-vote-per-user system
- Admin dashboard to manage users and candidates
- Light & dark mode switch
- Clean, responsive design
- Block/unblock users
- Add/delete candidates
- Passwords are securely hashed
- Emails sent using Flask-Mail

---

## 💻 Tech Stack

- **Backend:** Python (Flask)
- **Database:** MySQL
- **Frontend:** HTML, CSS
- **Auth & Security:** Flask session, bcrypt
- **Email:** Flask-Mail (SMTP)
- **Environment:** `.env` with python-dotenv

---

### Home Screen
![Screenshot 2025-06-09 000153](https://github.com/TarunKanth007/Online-Voting-System/blob/main/images/Screenshot%202025-06-09%20000153.png)
![Screenshot 2025-06-09 000204](https://github.com/TarunKanth007/Online-Voting-System/blob/main/images/Screenshot%202025-06-09%20000204.png)

### Contestants
![Screenshot 2025-06-09 000238](https://github.com/TarunKanth007/Online-Voting-System/blob/main/images/Screenshot%202025-06-09%20000238.png)

### After vote
![Screenshot 2025-06-09 000249](https://github.com/TarunKanth007/Online-Voting-System/blob/main/images/Screenshot%202025-06-09%20000249.png)

### Admin Page
![Screenshot 2025-06-09 000314](https://github.com/TarunKanth007/Online-Voting-System/blob/main/images/Screenshot%202025-06-09%20000314.png)
![Screenshot 2025-06-09 000336](https://github.com/TarunKanth007/Online-Voting-System/blob/main/images/Screenshot%202025-06-09%20000336.png)

---

## 🛠️ How to Run

### 1. Prerequisites

- Python 3.10+
- MySQL Server
- Gmail account for email verification (App Password required)

### 2. Setup Steps

**Step 1: Clone the Project**

```bash
git clone https://github.com/yourusername/online-voting-system.git
cd online-voting-system
```

**Step 2: Create Virtual Environment**

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

**Step 3: Install Required Packages**

```bash
pip install -r requirements.txt
```

**Step 4: Create Database in MySQL**

```sql
CREATE DATABASE online_voting;
USE online_voting;

CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  is_verified BOOLEAN DEFAULT FALSE,
  has_voted BOOLEAN DEFAULT FALSE,
  blocked BOOLEAN DEFAULT FALSE,
  verification_code VARCHAR(100)
);

CREATE TABLE contestants (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  description TEXT,
  votes INT DEFAULT 0
);
```

**Step 5: Create a `.env` File**

```env
DB_HOST=localhost
DB_USER=root
DB_PASS=your_mysql_password
DB_NAME=online_voting

SECRET_KEY=your_random_secret_key

MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

**Step 6: Run the App**

```bash
flask run
```

Visit: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 👥 How It Works

- Users sign up and verify their email
- After login, they can vote (only once)
- Admin can log in via `/admin/login` (default: admin/admin)
- Admin can manage users and candidates
- Blocked users cannot log in

---

## 🙌 Contribute

Found a bug or have an idea? Feel free to fork and make a pull request.

---

## 📜 License

MIT License © Sri Harsha  © Tarun Kanth

---

## 📧 Contact

Questions? Email me at [harshaparasa20@gmail.com]

---

**Thanks for checking out the Online Voting System! 🚀**
