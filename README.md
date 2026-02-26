<img width="1901" height="866" alt="image" src="https://github.com/user-attachments/assets/5d223b42-7f14-4d30-b554-e4d5c61c099b" />


# EvoGraph: AI-Powered Phylogenetic Tree API 🧬

A REST API that visualizes the evolutionary connections between animals, using public APIs for data and Google Gemini AI for biological facts.

## 🧠 About This Learning Project
This project was developed as a hands-on learning experience to dive deep into modern backend engineering. My primary goal was to explore and master **FastAPI**, **PostgreSQL** (complex SQL queries and database management), and third-party **API integrations**. 

To accelerate my learning process, write cleaner code, and understand industry best practices, this project was built with the guidance and assistance of AI tools acting as a coding mentor.

## 🚀 Features
* **Asynchronous REST API:** Built with **FastAPI** for high performance and non-blocking I/O operations.
* **Recursive SQL (CTEs):** Automatically calculates evolutionary lineages and finds the Lowest Common Ancestor (LCA) between species using advanced PostgreSQL queries.
* **AI Integration:** Uses **Google Gemini AI** via FastAPI Background Tasks to dynamically generate interesting biological facts without slowing down API responses.
* **API Orchestration:** Fetches and combines real-time data from **API Ninjas** (taxonomy) and **Unsplash** (images).
* **Dockerized:** Fully containerized with **Docker & Docker Compose** for seamless database provisioning and application deployment.

## 🛠️ Technologies Used
* **Backend:** Python 3.12, FastAPI, SQLAlchemy 2.0 (Async), Pydantic V2
* **Database:** PostgreSQL (asyncpg)
* **AI & External APIs:** Google Gemini 1.5/2.5 Flash, API Ninjas, Unsplash API
* **Deployment:** Docker, Docker Compose
* **Frontend:** HTML/CSS/JS with Vis.js for network visualization

## ⚙️ Quick Start (Docker)

You don't need to install Python or PostgreSQL locally. Just use Docker!

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/Kerim-Altny/evograph.git](https://github.com/Kerim-Altny/evograph.git)
   cd evograph
Environment Variables:
Create a .env file in the root directory and add your API keys:

Kod snippet'i
DATABASE_URL=postgresql+asyncpg://evouser:evopassword@db:5432/evograph
API_NINJAS_KEY=your_api_ninjas_key_here
GEMINI_API_KEY=your_gemini_api_key_here
UNSPLASH_ACCESS_KEY=your_unsplash_access_key_here
Run the Application:

Bash
docker-compose up -d --build
Access the App:

Frontend Interface: http://localhost:8000/

Interactive API Docs (Swagger UI): http://localhost:8000/docs
