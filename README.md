# 🧞 JobGenie — AI-Powered Resume Parser & Job Matcher

A smart **Flask** web app that parses your PDF resume, detects your career domain, computes an ATS score, and matches you with the most relevant jobs from LinkedIn, Indeed, and Naukri — all in seconds.

---

## 📌 Overview

Job hunting is exhausting — scrolling through hundreds of irrelevant listings, not knowing why your resume keeps getting rejected. JobGenie solves this by parsing your PDF resume, automatically detecting your professional domain (Data Science, Software Dev, Finance, etc.), and surfacing only the jobs that match your background.

It also scores your resume against ATS (Applicant Tracking System) criteria so you know exactly what to fix before applying.

🔗 **GitHub Repository:** [tanishcode-12/jobgenie](https://github.com/tanishcode-12/jobgenie)

---

## ✨ Features

- 📄 **PDF Resume Parser** — Extracts skills, education, work experience, certifications, contact info, and summary from any PDF resume using `pdfplumber`.
- 🎯 **Domain Detection** — Automatically identifies your career profile (Data Science / ML, Software Dev, Finance, Marketing, HR, or Data Entry) and filters jobs accordingly.
- 🤖 **ATS Score Calculator** — Scores your resume out of 100 across six categories: Contact Info, Skills, Education, Experience, Certifications, and Summary — with a visual ring chart and improvement tips.
- 💯 **Job Match Scoring** — Computes a Jaccard + coverage-based similarity score between your resume skills and each job description, with title and role bonuses.
- 🔍 **Smart Filters** — Filter 600 job listings by source platform (LinkedIn / Indeed / Naukri), skill, experience level (0–2 / 2–3 / 3+ years), and city.
- 🧞 **Built-in Chatbot** — A floating chat assistant answers questions about ATS scores, match logic, resume tips, and how to use filters — with typing indicators and quick-reply chips.
- 🌙 **Dark Mode** — Toggle between light and dark themes, persisted via `localStorage`.
- 📥 **Drag & Drop Upload** — Drop your PDF directly onto the homepage upload zone with live filename feedback.
- 📄 **Paginated Results** — Job cards are paginated (9 per page) with smooth animations, shuffled middle results, and top matches pinned to the front.
- 🚀 **Deployable** — Ships with a `Procfile` for one-click deployment to Heroku or Render via **Gunicorn**.

---

## 🗂️ Project Structure

```
📦 jobgenie/
├── 🚀 app.py                    # Flask app — resume parsing, job matching, ATS scoring, chatbot API
├── 📋 jobs.csv                  # Master dataset of 600 job listings
├── 🎨 static/
│   ├── 🖌️  style.css            # Full UI styling — dark mode, cards, filters, modals
│   ├── 💬  chatbot.js           # Chatbot toggle, message send/receive, typing indicator
│   ├── 🖼️  logo.png             # JobGenie logo
│   └── 🖼️  secondimage.jpg      # Hero section illustration
├── 🌐 templates/
│   ├── 🏠  index.html           # Homepage — hero, drag & drop upload, stats bar
│   └── 📊  results.html         # Results page — ATS modal, job cards, sidebar filters
├── 🛑 Procfile                  # Gunicorn config for Heroku/Render deployment
└── 🚫 .gitignore
```

---

## ⚙️ Installation

### 🧰 Prerequisites

- 🐍 Python 3.8 or higher
- 📦 pip

### 🪜 Steps

**📥 Clone the repository**

```bash
git clone https://github.com/tanishcode-12/jobgenie.git
cd jobgenie/jobgenie
```

**📦 Install dependencies**

```bash
pip install flask pdfplumber pandas gunicorn
```

**▶️ Run the app locally**

```bash
python app.py
```

**🌐 Open in browser**

Navigate to `http://localhost:5000`

> ⚠️ Make sure `jobs.csv` is in the same directory as `app.py` before launching.

### ☁️ Deploy to Heroku / Render

The repo includes a `Procfile` so deployment is plug-and-play.

> ⚠️ Make sure `jobs.csv` is accessible at the path expected by `app.py` in your deployment environment.

```
web: gunicorn jobgenie.app:app
```

Push to Heroku or connect the repo to Render and it will auto-detect the Procfile.

---

## 🚀 Usage

1. 📄 **Upload your PDF resume** — Drag and drop (or click to browse) on the homepage. PDF only, max 2MB.
2. 🧞 **Click "Summon Genie"** — JobGenie parses your resume and detects your domain in seconds.
3. 📊 **Review your ATS Score** — Click **"View Detailed Analysis"** on the results banner to see your full score breakdown, detected skills, education, experience, and improvement tips.
4. 💼 **Browse matched jobs** — All 600+ listings are sorted by match score, filtered to your detected domain.
5. 🔧 **Use sidebar filters** — Narrow results by job source, required skills, experience level, or city.
6. 🚀 **Apply directly** — Hit **"Apply Now"** on any card to open the original job listing on LinkedIn, Indeed, or Naukri.
7. 🧞 **Chat with JobGenie** — Click the floating genie button for help with ATS scores, match logic, or resume tips.

> 📁 **Tip:** If fewer than 10 domain-matched jobs are found, JobGenie automatically falls back to showing all top matches across every domain.

---

## 🌐 API Endpoints

| Endpoint   | Method | Description                                                   |
| ---------- | ------ | ------------------------------------------------------------- |
| 🏠 `/`     | `GET`  | Renders the homepage with the resume upload form              |
| 📤 `/`     | `POST` | Accepts PDF upload → parses resume → returns job results page |
| 💬 `/chat` | `POST` | Accepts `{ "message": "..." }` JSON → returns chatbot reply   |

---

## 📁 Data Files

### 📋 jobs.csv

The master dataset of 600 job listings scraped equally from LinkedIn, Indeed, and Naukri (200 each).

| Column            | Type   | Description                                                         |
| ----------------- | ------ | ------------------------------------------------------------------- |
| 🔤 `job_title`    | string | Title of the job role (e.g. Data Analyst, Software Engineer)        |
| 🏢 `company`      | string | Company name (370 unique companies)                                 |
| 📍 `location`     | string | Job location — city, state, or Remote (219 unique locations)        |
| 📝 `description`  | string | Full job description text used for skill extraction and matching    |
| 🔗 `job_url`      | string | Direct link to the original listing on LinkedIn / Indeed / Naukri   |
| 💰 `salary`       | string | Monthly salary range in ₹ if disclosed, else "Not disclosed"        |
| 🖼️ `company_logo` | string | URL to the company logo image                                       |
| ⭐ `rating`       | float  | Company rating on a 0–5 scale                                       |
| 🕐 `experience`   | string | Required experience range (e.g. 1-2 years, 3-4 years)               |
| 🧠 `skills`       | string | Space-separated skills extracted from the job description           |
| 🌐 `source`       | string | Platform the listing was scraped from — LinkedIn, Indeed, or Naukri |

---

## 🤖 Resume Parsing & Scoring Logic

### 📊 ATS Score Breakdown

| Category          | Max Points | How It's Scored                                                |
| ----------------- | ---------- | -------------------------------------------------------------- |
| 📞 Contact Info   | 20         | 5pts each for name, email, phone + 5pts for LinkedIn or GitHub |
| 🧠 Skills         | 30         | 2pts per detected skill, capped at 30                          |
| 🎓 Education      | 20         | 20pts if any degree is detected                                |
| 💼 Experience     | 15         | 5pts per experience line, capped at 15                         |
| 🏆 Certifications | 10         | 3pts per certification, capped at 10                           |
| 📝 Summary        | 5          | 5pts if a summary/objective section is found                   |

### 💯 Match Score Formula

| Component                                          | Weight                |
| -------------------------------------------------- | --------------------- |
| 📐 Jaccard similarity (resume skills ∩ job skills) | 40%                   |
| 📊 Coverage (% of resume skills found in job)      | 60%                   |
| 🎯 Title keyword bonus                             | +12 pts               |
| 🏷️ Role type bonus (engineer, analyst, etc.)       | +10 pts               |
| 🔢 Per-skill match bonus                           | +2 pts each (max +18) |

### 🎯 Domain Detection

| Domain                | Label                           |
| --------------------- | ------------------------------- |
| 🔬 `data_science`     | Data Science / ML / AI          |
| 💻 `software_dev`     | Software Development / IT       |
| 💰 `finance_commerce` | Finance / Commerce / Accounting |
| 📣 `marketing_sales`  | Marketing / Sales / Business    |
| 👥 `hr_admin`         | HR / Administration             |
| 📋 `data_entry_ops`   | Data Entry / Operations         |

---

## 📦 Dependencies

| Library         | Purpose                                             |
| --------------- | --------------------------------------------------- |
| 🌐 `flask`      | Web framework — routing, templates, JSON API        |
| 📄 `pdfplumber` | PDF text extraction with layout awareness           |
| 🐼 `pandas`     | CSV loading, deduplication, and job data management |
| 🚀 `gunicorn`   | Production WSGI server for deployment               |

> Frontend uses vanilla **HTML**, **CSS**, and **JavaScript** — no frontend framework required.

---

## 🤝 Contributing

🙌 Contributions are welcome! Here's how you can help:

1. 🍴 Fork the repository
2. 🌿 Create a new branch (`git checkout -b feature/your-feature`)
3. 💾 Make your changes and commit (`git commit -m 'Add your feature'`)
4. 📤 Push to the branch (`git push origin feature/your-feature`)
5. 🔁 Open a Pull Request

✅ Please make sure your code is clean and well-commented.

---

## 👤 Author

**Tanish** — [@tanishcode-12](https://github.com/tanishcode-12)

---

> ⭐ If you found this project helpful, consider giving it a star on GitHub!
