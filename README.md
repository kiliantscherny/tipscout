
<h1 align="center"><img src="images/tipscout-logo.png" alt="tipscout logo"></h1>
<h2 align="center"> tipscout: Stats about Tipster deals </h2>
<p align="center"> A data pipeline and visualization dashboard to analyze deals from Tipster.</p>

>[!NOTE]
>This project is very much a Work In Progress. It works, but it's not very useful yet. Hang tight, or better yet, contribute!
>
>**This project is not affiliated with TIPSTER S.M.B.A. ("Tipster") in any way. It's just a fun personal project driven by curiosity 😀**

## What this does
This project is a data pipeline and visualization dashboard to analyze deals from Tipster. It scrapes the Tipster website for deals, stores the data in a DuckDB database, and provides a web dashboard built with Evidence to visualize the data.

In the future... ✨ this might help you make better decisions about which deals to take and which to leave, as well as give useful insights into what deals are available and how much longer they will be available for.

## Tech stack
- **GitHub Actions**: To schedule the data pipeline and run the Python scripts which scrape the data and store it in the database
- **DuckDB**: To store the data in an OLAP database for speedy retrieval
- **Evidence**: To create the interactive web dashboard to visualize the data
- **Python with uv**: For dependency management and data scraping

## How to use

### Local Development
1. Clone the repository
2. Install Python dependencies: `uv sync`
3. Install Node.js dependencies: `npm install`
4. Run the scraper manually: `uv run python main.py`
5. Start the Evidence development server: `npm run dev`
6. Open your browser to the URL shown in the terminal

### Production
The project automatically deploys to GitHub Pages via GitHub Actions:
- **Data Collection**: Runs every 3 hours (matching the original Airflow schedule)
- **Dashboard**: Automatically builds and deploys to GitHub Pages after each data collection

>[!IMPORTANT]
>The app is set up to scrape the website once every 3 hours. You can adjust this in the `.github/workflows/scrape_and_build.yml` file if you want. Please scrape responsibly 🧡

## Development
- Run scraper: `uv run python main.py`
- Start Evidence dev server: `npm run dev`
- Build for production: `npm run build`
- Generate sources: `npm run sources`

## To-do list
- [ ] Show in greater detail the deals which are currently available
- [ ] Add more interactive visualizations to the Evidence dashboard
- [ ] Add filtering and search capabilities
- [ ] Implement deal alerts and notifications
