# Open Source Contribution: 20 Proposed Issues for EcoBuddy AI

This document contains 20 detailed GitHub issue templates ready to be opened in the repository. These issues cover architecture refactoring, new features, testing, DevOps, and UI/UX enhancements, designed to elevate the project to production-grade quality.

---

## Issue 1: Refactor Monolithic `app.py` into Streamlit Multipage Application
**Labels:** `enhancement`, `refactoring`, `architecture`, `good first issue`

**Description:**
### The Problem
Currently, the entire user interface, routing logic, session state management, and view rendering for EcoBuddy AI are housed within a single monolithic file: `app.py`. This file spans over 1,700 lines of code. As the application scales and new features (like the gamification dashboard, offset marketplace, and energy audits) are expanded, maintaining this single file will become increasingly difficult. It increases the likelihood of merge conflicts for multiple contributors and makes the codebase harder to navigate for newcomers.

### The Proposed Solution
Streamlit natively supports multipage applications by utilizing a `pages/` directory. We should refactor the application to break down the UI into logical, separate pages. 
1. **`app.py` (Main Page):** Should serve as the landing page, introducing the application, handling high-level session state initialization, and perhaps displaying a high-level summary dashboard.
2. **`pages/1_Dashboard.py`:** For entering assessment data (transport, diet, energy) and viewing immediate results.
3. **`pages/2_Gamification.py`:** To display user challenges, badges, level progress, and XP logs.
4. **`pages/3_Marketplace.py`:** To browse carbon offset projects and view transaction history.
5. **`pages/4_Energy_Audit.py`:** To handle deep-dive home appliance and solar calculations.
6. **`pages/5_Settings.py`:** For user configuration and data export/import.

### Acceptance Criteria
- `app.py` is reduced in size significantly (targeting < 400 lines).
- A `pages/` directory is created with the respective split functionality.
- The sidebar navigation accurately reflects the new multipage structure and works seamlessly.
- All existing functionality and session state are preserved across page transitions.

### Benefits
This architectural shift will dramatically improve code readability, maintainability, and developer experience. It allows concurrent work by multiple open-source contributors without stepping on each other's toes in a single file.

---

## Issue 2: Implement User Authentication System
**Labels:** `enhancement`, `security`, `feature`

**Description:**
### The Problem
Presently, EcoBuddy AI acts as a single-tenant, local application. If you look at `database.py`, user identifiers are hardcoded (e.g., `user_id = 1`) across gamification, water, marketplace, and appliance databases. If this app were to be deployed to the cloud (e.g., Streamlit Community Cloud or Heroku) for public use, all users would be overriding and sharing the same database rows, completely breaking the user experience and violating data privacy.

### The Proposed Solution
We need to implement a robust authentication layer to support multi-tenancy. We can utilize `streamlit-authenticator` or a custom JWT-based authentication flow if we plan to separate the backend later.
1. Create a `users` table in the SQLite database to store `username`, `email`, and securely hashed passwords (using `bcrypt`).
2. Build a Login/Registration page that acts as a gatekeeper before users can access the main dashboards.
3. Update Streamlit session state to hold the logged-in `user_id`.
4. Refactor `database.py` functions to accept the dynamic `user_id` from the session state rather than defaulting to `1`.

### Acceptance Criteria
- Users can securely sign up, log in, and log out.
- Passwords are encrypted before being stored in the database.
- A user can only see, edit, and interact with their own assessments, gamification stats, and marketplace transactions.
- Unauthenticated users are redirected to the login screen.

### Benefits
This is the most critical feature required to take EcoBuddy AI from a local portfolio project to a live, multi-user web application capable of serving thousands of individuals simultaneously.

---

## Issue 3: Migrate from Raw SQL to an ORM (e.g., SQLAlchemy)
**Labels:** `architecture`, `tech-debt`, `backend`

**Description:**
### The Problem
All database interactions in `database.py` currently use the standard library `sqlite3` with raw SQL strings. While parameterized queries are used to prevent SQL injection, writing raw SQL strings is prone to typos, lacks schema validation at the application layer, makes complex table joins cumbersome, and tightly couples the application to SQLite. If the project ever needs to scale to PostgreSQL or MySQL, this will require rewriting every single database function.

### The Proposed Solution
We should introduce an Object-Relational Mapper (ORM), specifically SQLAlchemy (or alternatively, Peewee or SQLModel), to handle database operations. 
1. Define Python classes for all tables (`Assessment`, `Appliance`, `SolarConfig`, `UserChallenge`, `UnlockedBadge`, `XpTransaction`, `JourneyProfile`, `OffsetTransaction`, `WaterConsumption`).
2. Define proper foreign key relationships (e.g., a `User` has many `Assessments`).
3. Replace all raw `cursor.execute()` calls in `database.py` with the equivalent SQLAlchemy ORM queries (e.g., `session.query(Assessment).filter_by(user_id=1).all()`).
4. Set up an engine that connects to the SQLite database by default but uses environment variables to allow connecting to other databases easily.

### Acceptance Criteria
- `database.py` is fully refactored to use SQLAlchemy models and sessions.
- No raw SQL strings remain in the codebase.
- The application functions exactly as it did before, with all unit tests passing.

### Benefits
Using an ORM drastically improves backend code maintainability, provides a clear schema definition in Python, enables the use of migration tools like Alembic, and abstracts away database dialect specifics, allowing easy migration to production-grade databases like PostgreSQL in the future.

---

## Issue 4: Decouple CSS Styling from Python Logic in `app.py`
**Labels:** `refactoring`, `ui/ux`, `good first issue`

**Description:**
### The Problem
EcoBuddy AI boasts a highly polished, premium UI. However, this is achieved by injecting over 200 lines of custom CSS directly into `app.py` using `st.markdown("<style>...</style>", unsafe_allow_html=True)`. Mixing large blocks of CSS inside Python files violates the principle of separation of concerns. It clutters the Python code, prevents syntax highlighting for CSS in most IDEs, and makes UI debugging difficult.

### The Proposed Solution
We should extract all CSS styling into a dedicated stylesheet file and load it dynamically.
1. Create a new directory named `assets/` or `styles/`.
2. Create a `main.css` file and move all the CSS rules currently in `app.py` into this file.
3. Write a helper function in `app.py` (e.g., `load_css(file_name)`) that reads the contents of the CSS file and renders it using `st.markdown()`.
4. Optionally, split the CSS further into logical files (e.g., `sidebar.css`, `cards.css`, `buttons.css`) if it gets too large.

### Acceptance Criteria
- The `<style>` blocks in `app.py` are completely removed.
- A `styles/main.css` file exists and contains all the styling.
- The application looks exactly the same as before; the styles are successfully loaded and applied at runtime.

### Benefits
Separating CSS from Python code improves readability, enables proper CSS tooling and linting, and makes it drastically easier for frontend-focused open-source contributors to improve the UI without having to parse through complex Python logic.

---

## Issue 5: Implement Comprehensive Unit Testing Suite for API Fallbacks
**Labels:** `testing`, `reliability`

**Description:**
### The Problem
EcoBuddy AI integrates with several third-party APIs (Climatiq for emissions, Gemini/Groq for LLM parsing). The codebase features excellent fallback mechanisms (e.g., using static emission factors if Climatiq fails, or falling back to Groq if Gemini fails). However, these critical resilience paths are not currently covered by automated tests. If future changes break these fallbacks, we won't know until the application crashes in production when an API goes down.

### The Proposed Solution
We need to expand the testing suite (`test_emissions.py`, `test_recommendations.py`, etc.) to explicitly test these API fallback behaviors using mocking libraries.
1. Use `unittest.mock.patch` or `pytest-mock` to mock the `requests.post` calls in `fetch_emission_factors` and `parse_quick_log`.
2. Create test cases simulating an API timeout (`Timeout` exception).
3. Create test cases simulating an HTTP 500 server error.
4. Create test cases simulating invalid JSON responses.
5. Assert that the functions correctly handle these errors and return the expected fallback data (e.g., the static dictionary in `emissions.py`) without raising unhandled exceptions.

### Acceptance Criteria
- Unit tests exist for all external API calls.
- The tests achieve >90% coverage for the `llm_parser.py` and `fetch_emission_factors` functions, specifically covering the `except` blocks.
- Tests can run independently without requiring active internet connections or API keys.

### Benefits
By ensuring our fallback mechanisms are tested, we guarantee high availability and reliability for the application. It prevents regressions where a developer might accidentally remove or break the `try/except` blocks that keep the app running during API outages.

---

## Issue 6: Add Docker Support for Standardized Deployment
**Labels:** `devops`, `deployment`, `enhancement`

**Description:**
### The Problem
Currently, developers looking to contribute to EcoBuddy AI or deploy it themselves must manually clone the repo, create a virtual environment, install requirements, and run the Streamlit command. This process is susceptible to the "it works on my machine" problem due to varying OS environments, Python versions, or system-level dependencies (like those needed for Tesseract OCR).

### The Proposed Solution
We should containerize the application using Docker to ensure consistent environments across all stages of development and deployment.
1. Create a `Dockerfile` at the root of the project.
2. Use an official lightweight Python image (e.g., `python:3.10-slim`).
3. Install necessary system dependencies (e.g., `tesseract-ocr` for the OCR module).
4. Install Python requirements via `pip`.
5. Expose Streamlit's default port (`8501`).
6. Create a `docker-compose.yml` file to make it even easier to spin up the app with a single command (`docker-compose up`).

### Acceptance Criteria
- A working `Dockerfile` is added.
- A `docker-compose.yml` is added.
- A user can build and run the application entirely within Docker, and it functions correctly at `localhost:8501`.
- The `README.md` is updated with instructions on how to run the app using Docker.

### Benefits
Dockerization significantly lowers the barrier to entry for new open-source contributors, eliminates environment disparity issues, and prepares the application for modern cloud deployments (e.g., AWS ECS, Google Cloud Run, Kubernetes).

---

## Issue 7: Create CI/CD Pipeline using GitHub Actions
**Labels:** `devops`, `automation`, `ci-cd`

**Description:**
### The Problem
While the project contains unit tests (`test_db.py`, `test_emissions.py`, etc.), they must be run manually by the developer. In an open-source setting, contributors may submit Pull Requests with code that breaks existing functionality, and reviewers would have to pull the code and run the tests locally to verify.

### The Proposed Solution
Implement Continuous Integration (CI) using GitHub Actions to automatically lint the code, run tests, and check coverage on every push and pull request.
1. Create a `.github/workflows/ci.yml` file.
2. Configure the workflow to trigger on pushes to the main branch and on PRs.
3. Set up the Python environment.
4. Install dependencies from `requirements.txt`.
5. Add a linting step using `flake8` or `black` to enforce code style.
6. Add a testing step that runs `pytest` and generates a coverage report.
7. (Optional) Fail the build if code coverage drops below a certain threshold.

### Acceptance Criteria
- A GitHub Actions workflow is actively running on the repository.
- PRs display a status check indicating whether the tests passed or failed.
- The workflow executes successfully in under 3 minutes.
- A status badge is added to the `README.md`.

### Benefits
Automated CI ensures code quality and prevents regressions from being merged into the main branch. It saves maintainers time by automatically verifying that new contributions don't break the existing application.

---

## Issue 8: Integrate Real-Time Currency Conversion for Carbon Offset Pricing
**Labels:** `enhancement`, `feature`, `api`

**Description:**
### The Problem
The simulated carbon offset marketplace in `marketplace.py` lists the `cost_per_tonne` of various projects in a static, assumed currency (presumably USD). As a global application, users worldwide will want to view and "purchase" offsets in their local currency (EUR, GBP, INR, etc.) to better understand the financial impact.

### The Proposed Solution
Implement a real-time currency conversion feature in the marketplace module.
1. Add a dropdown in the UI (e.g., in the sidebar or settings) allowing the user to select their preferred currency.
2. Integrate a free, public exchange rate API (such as `exchangerate-api.com` or `frankfurter.app`) in a new utility file (e.g., `currency_utils.py`).
3. Fetch exchange rates relative to the base currency (USD) and cache the response using `@st.cache_data(ttl=3600)` to avoid hitting API rate limits.
4. Update the marketplace UI to display `cost_per_tonne` and total transaction costs dynamically converted to the selected currency.

### Acceptance Criteria
- Users can select a preferred currency from a list of major global currencies.
- The marketplace dynamically updates all pricing to reflect the chosen currency based on live or daily exchange rates.
- API calls are properly cached to prevent rate limit exhaustion.
- Fallback logic exists to revert to USD if the exchange rate API is unavailable.

### Benefits
This heavily improves the localization and user experience of the marketplace feature, making the financial aspect of offsetting carbon emissions tangible and relatable to a global user base.

---

## Issue 9: Implement Caching Layer for External API Calls
**Labels:** `performance`, `optimization`

**Description:**
### The Problem
The application makes frequent calls to external APIs. While `@st.cache_data` is used on `fetch_emission_factors` in `emissions.py`, the LLM parsing logic in `llm_parser.py` (which calls Gemini and Groq APIs) does not appear to utilize caching. Furthermore, if the user modifies an assessment form and submits it, redundant API calls might be made for data that has already been processed or fetched recently. This increases latency and risks hitting rate limits on free API tiers.

### The Proposed Solution
Implement a robust caching strategy across all network-bound functions.
1. Apply `@st.cache_data` with an appropriate time-to-live (TTL) to the `parse_quick_log` function. We can hash the input text string so that if a user types the exact same quick log phrase, the parsed JSON is instantly returned from the cache rather than querying the LLM again.
2. Review the Climatiq API caching strategy to ensure the cache is keyed securely and effectively by the selected `region`.
3. Implement a retry mechanism with exponential backoff (using a library like `tenacity`) for API calls to handle transient network blips gracefully before falling back to static data.

### Acceptance Criteria
- `llm_parser.py` functions utilize Streamlit caching.
- Identical natural language inputs bypass the network and return cached JSON instantly.
- Transient API failures are retried automatically before triggering fallback logic.

### Benefits
Caching drastically improves the perceived speed of the application for the user. It also saves costs and preserves API quotas by preventing redundant requests to third-party providers.

---

## Issue 10: Add Support for Exporting Reports to Excel/CSV directly from UI
**Labels:** `feature`, `data-export`

**Description:**
### The Problem
EcoBuddy AI generates a visual PDF report via ReportLab, and `data_io.py` supports exporting the entire database state as a JSON or a ZIP of CSVs for backup purposes. However, users often want to export specific views—like their historical assessment trends or marketplace transaction history—into a simple, immediately usable Excel or standalone CSV file for personal tracking in tools like Excel or Google Sheets.

### The Proposed Solution
Add simple, single-click CSV/Excel export buttons to the relevant data tables in the UI.
1. On the "History" or "Dashboard" view where past assessments are listed, utilize Streamlit's `st.download_button`.
2. Use pandas to convert the dataframes (e.g., `get_assessments()`) directly into CSV or Excel formats (`df.to_csv()` or `df.to_excel()`).
3. Allow the user to filter the date range before exporting.
4. Implement similar export buttons for Gamification (XP history) and Marketplace (Transaction history).

### Acceptance Criteria
- UI features "Export to CSV" buttons below major data tables.
- The downloaded files are properly formatted and include headers.
- Date filters applied in the UI are respected in the exported data file.

### Benefits
Provides users with data portability in universally accepted formats (CSV/Excel), allowing power users to conduct their own analysis on their environmental data outside of the application.

---

## Issue 11: Localize Application for Internationalization (i18n) Support
**Labels:** `feature`, `i18n`, `localization`

**Description:**
### The Problem
EcoBuddy AI's UI text, recommendations, and gamification strings are entirely hardcoded in English. Climate change is a global issue, and the application's impact is severely limited if it cannot be used by non-English speakers. 

### The Proposed Solution
Introduce an Internationalization (i18n) framework to support multiple languages.
1. Choose an i18n library suitable for Python/Streamlit (e.g., `gettext`, or a simple JSON-based dictionary mapping system).
2. Extract all hardcoded strings (UI labels, button texts, recommendation insights, badge descriptions) from `app.py`, `recommendations.py`, and `gamification.py` into language files (e.g., `locales/en.json`, `locales/es.json`, `locales/fr.json`).
3. Add a language selector dropdown in the application settings or sidebar.
4. Update the codebase to dynamically render text based on the selected locale (e.g., using a translation function like `t("button.submit")`).

### Acceptance Criteria
- All hardcoded user-facing strings are extracted into translation files.
- The app supports at least two languages (e.g., English and Spanish) initially to prove the concept.
- The user can switch languages dynamically from the UI, and the interface updates immediately.

### Benefits
Localization opens the application up to a massive global audience, dramatically increasing its potential user base and environmental impact.

---

## Issue 12: Implement Dark Mode/Light Mode Toggle Functionality
**Labels:** `ui/ux`, `enhancement`

**Description:**
### The Problem
The current application uses a highly customized, premium "light mode" theme injected via CSS in `app.py`. While beautiful, many users prefer dark mode for reduced eye strain and aesthetic preference. Currently, there is no way for the user to switch themes, and the hardcoded CSS overrides Streamlit's native theme settings.

### The Proposed Solution
Implement a dynamic theme switcher that allows users to toggle between the current light theme and a new, specifically designed dark theme.
1. Define CSS variables (CSS custom properties) for all colors (backgrounds, text, borders, accents) in the main stylesheet.
2. Create two sets of variables: one for `.light-theme` and one for `.dark-theme`.
3. Add a toggle switch in the Streamlit UI (e.g., `st.toggle('Dark Mode')`).
4. Based on the toggle's state, inject a JavaScript snippet or use Streamlit's HTML components to apply the appropriate class to the `<body>` or root container.
5. Save the user's theme preference in session state (and eventually the database).

### Acceptance Criteria
- A functional theme toggle exists in the UI.
- Toggling the switch instantly changes the application's color palette without requiring a page reload.
- The dark mode theme maintains the premium feel (e.g., using deep slate grays and neon green accents).
- Charts (Plotly/Matplotlib) also update their background and font colors to match the active theme.

### Benefits
Provides a massive UX improvement, catering to user preferences and modern web application standards, making the app more accessible and visually versatile.

---

## Issue 13: Add Data Validation Models using Pydantic
**Labels:** `architecture`, `reliability`, `backend`

**Description:**
### The Problem
Data moving between the UI, the calculation modules (`emissions.py`, `water.py`), and the database (`database.py`) is passed as raw variables or basic dictionaries. For example, `save_assessment` takes seven separate arguments. The `llm_parser.py` returns an unvalidated dictionary. This lack of strict typing and validation can lead to runtime errors, database integrity issues, and makes the code harder to reason about and refactor.

### The Proposed Solution
Integrate `Pydantic` to enforce data validation and serialization across the application.
1. Create a new module (e.g., `models.py`).
2. Define Pydantic models for core concepts: `AssessmentCreate`, `ApplianceModel`, `JourneyProfileModel`, `OffsetTransactionModel`, etc.
3. Update `llm_parser.py` to validate the JSON returned by the LLM against an `LLMParsedLog` Pydantic model before returning it to the UI.
4. Refactor backend functions to accept Pydantic model instances instead of long lists of individual arguments.

### Acceptance Criteria
- Pydantic models are defined for all major data structures.
- API responses and LLM outputs are validated through Pydantic.
- Database insertion functions accept validated Pydantic objects.
- Type hints are updated across the codebase to utilize these models.

### Benefits
Pydantic ensures that invalid data is caught at the boundaries of the application before it crashes logic or corrupts the database. It heavily improves code quality, IDE auto-completion, and serves as self-documenting code.

---

## Issue 14: Create a Unified Error Handling and Logging Mechanism
**Labels:** `reliability`, `architecture`

**Description:**
### The Problem
Throughout the application (especially in `database.py`, `llm_parser.py`, and `emissions.py`), errors are handled inconsistently. Most exceptions are caught with a broad `except Exception as e:`, followed by a simple `print(e)`, and return `False` or `None`. This makes debugging in a production environment nearly impossible, as `print` statements are easily lost, and the UI often fails silently without informing the user what went wrong.

### The Proposed Solution
Implement a centralized, standard Python logging mechanism and uniform error handling strategies.
1. Create a `logger_config.py` to set up the standard Python `logging` module with console and file handlers, formatting timestamps and severity levels.
2. Replace all `print()` statements used for error tracking with `logger.error()`, `logger.warning()`, or `logger.info()`.
3. Create custom exception classes (e.g., `DatabaseError`, `APIConnectionError`) for more granular error catching.
4. In the UI (`app.py`), ensure that when an operation fails (returns False/None), a user-friendly `st.error()` message is displayed rather than failing silently.

### Acceptance Criteria
- The `logging` module replaces all debugging `print` statements.
- Logs are written to a rotating log file as well as the console.
- The UI gracefully informs the user when a backend operation fails.
- No broad `except Exception:` blocks exist without logging the stack trace.

### Benefits
Centralized logging is essential for production deployment. It allows maintainers to monitor application health, diagnose bugs quickly, and ensures users aren't left confused when something fails silently.

---

## Issue 15: Enhance Gamification: Implement Leaderboards and Social Sharing
**Labels:** `feature`, `gamification`, `ui/ux`

**Description:**
### The Problem
The gamification system currently rewards users with XP, levels, and beautiful generated badge images (`gamification.py`). However, this system is entirely isolated. Users cannot compare their progress with others or easily share their achievements outside of downloading the badge image, limiting the organic growth and community aspect of the app.

### The Proposed Solution
Expand the gamification module to include competitive and social elements.
1. **Leaderboard:** Create a new UI component that aggregates the `get_total_xp()` for all users in the database and displays a Top 10 Leaderboard. (Requires Issue #2: Authentication to be implemented first so users have usernames).
2. **Social Sharing:** Add "Share to Twitter/X" and "Share to LinkedIn" buttons next to unlocked badges or upon completing an assessment. These buttons should generate a pre-formatted intent URL containing text like "I just reached Level 5 and reduced my carbon footprint by 20% on EcoBuddy AI! 🌱 [Link]".

### Acceptance Criteria
- A global leaderboard is visible in the Gamification dashboard, ranking users by total XP.
- Social share buttons are functional and pre-populate engaging text.
- Privacy controls: Allow users to opt-out of appearing on the public leaderboard.

### Benefits
Leaderboards introduce friendly competition, driving higher user engagement and retention. Social sharing acts as free organic marketing, helping the open-source project gain visibility.

---

## Issue 16: Expand Water Footprint Calculator with Regional Scarcity Factors
**Labels:** `enhancement`, `feature`, `logic`

**Description:**
### The Problem
The `water.py` module calculates water footprints based on static global averages (e.g., a shower uses 10L/min). However, the environmental impact of using 1,000 liters of water in a water-abundant region (like Scotland) is vastly different from using 1,000 liters in a drought-prone region (like California or Sub-Saharan Africa). The current recommendations do not account for regional water scarcity.

### The Proposed Solution
Enhance the water calculation logic to contextualize water usage based on geography.
1. Integrate a dataset or API (such as the WRI Aqueduct Water Risk Atlas data) that maps geographic regions to water scarcity indexes.
2. Update the UI to ask the user for their location (Country/Region) alongside their water usage habits.
3. Modify the water eco-score and recommendations logic: if a user is in a high-water-stress area, penalize high water usage more heavily and prioritize water-saving recommendations above carbon-saving ones.

### Acceptance Criteria
- `water.py` accepts a `region` parameter.
- The application factors in a "scarcity multiplier" when generating the final eco-score or insights.
- Recommendations specifically mention regional water stress if applicable.

### Benefits
Provides a much more accurate, scientifically rigorous, and personalized environmental assessment. It elevates the app from a basic calculator to an intelligent, context-aware environmental advisor.

---

## Issue 17: Integrate OAuth2 Login (Google, GitHub, Apple)
**Labels:** `security`, `feature`, `ux`

**Description:**
### The Problem
Assuming Issue #2 (User Authentication) is implemented with basic email/password, managing passwords is a security liability and creates friction for new users during onboarding. Users are much more likely to try an application if they can log in with a single click using an existing account.

### The Proposed Solution
Integrate third-party OAuth2 providers for Single Sign-On (SSO).
1. Utilize a library like `Authlib` or `streamlit-oauth`.
2. Register OAuth applications with Google, GitHub, and Apple to obtain Client IDs and Secrets.
3. Add "Sign in with Google", "Sign in with GitHub" buttons to the login page.
4. Upon successful OAuth callback, securely create or map the user to the local `users` table in the database and establish the session.

### Acceptance Criteria
- Users can log in seamlessly using Google or GitHub.
- OAuth secrets are securely managed via `.env` variables.
- Returning OAuth users are correctly mapped to their existing data.

### Benefits
Drastically reduces onboarding friction, leading to higher user acquisition rates. Offloads password security and reset flows to trusted tech giants, improving overall application security.

---

## Issue 18: Add User Profile Settings Page for Default Values and Preferences
**Labels:** `feature`, `ui/ux`

**Description:**
### The Problem
Every time a user visits the dashboard to log a new assessment, the form resets to the system defaults defined in `DEFAULT_VALUES` inside `app.py` (e.g., Transport: Car, Diet: Vegetarian, Distance: 10). If a user is a vegan who commutes 40km via train every day, they have to manually change these dropdowns and sliders every single time they use the app, which is a poor user experience.

### The Proposed Solution
Create a User Profile settings page where users can define their own baseline defaults.
1. Create a `user_preferences` table in the database.
2. Build a "Settings" page UI where users can set their default Transport Mode, standard commute distance, Diet type, and preferred Currency (linking to Issue #8).
3. Update the initialization logic in `app.py` to fetch these preferences from the database upon login and populate the form `st.session_state` variables with them instead of the hardcoded `DEFAULT_VALUES`.

### Acceptance Criteria
- A Settings page exists and correctly saves data to the database.
- Assessment forms initialize with the user's specific saved preferences.
- Users can update their preferences at any time.

### Benefits
Greatly improves the daily usability of the app for returning users. Making data entry frictionless is key for a tracking app where users are expected to log data frequently.

---

## Issue 19: Develop a RESTful API Wrapper using FastAPI for EcoBuddy Logic
**Labels:** `architecture`, `backend`, `expansion`

**Description:**
### The Problem
EcoBuddy AI currently tightly couples its frontend (Streamlit) with its backend logic (`emissions.py`, `recommendations.py`, `database.py`). If a developer wanted to build a mobile app version (iOS/Android) or a browser extension for EcoBuddy, they would have to completely rewrite the backend logic in another language or extract it manually.

### The Proposed Solution
Decouple the backend logic by wrapping it in a RESTful API using FastAPI.
1. Create a new directory `/api` alongside the Streamlit app.
2. Build FastAPI endpoints for core logic: `/api/calculate_emissions`, `/api/gamification/award_xp`, `/api/marketplace/projects`.
3. Modify the Streamlit frontend (`app.py`) to make HTTP requests to this local FastAPI server instead of importing the Python functions directly.
4. Document the API automatically using FastAPI's built-in Swagger UI.

### Acceptance Criteria
- A functional FastAPI server runs alongside the Streamlit app.
- Core business logic is exposed via REST endpoints.
- The Streamlit app successfully functions by consuming the new API.
- Swagger documentation is available at `/docs`.

### Benefits
Transforms EcoBuddy from a standalone script into a scalable platform. By exposing an API, the open-source project can spawn mobile apps, Discord/Slack bots, or browser extensions, drastically increasing the reach of the project.

---

## Issue 20: Implement Automated Database Migrations using Alembic
**Labels:** `architecture`, `tech-debt`, `devops`

**Description:**
### The Problem
Currently, database tables are created using `CREATE TABLE IF NOT EXISTS` commands inside initialization functions in `database.py` (e.g., `init_db()`). If we need to modify an existing table (e.g., adding a `currency` column to the `users` table or changing a data type), SQLite does not make this easy, and `IF NOT EXISTS` will completely ignore the changes if the table is already there. Users would have to manually delete their `eco_buddy.db` file (losing all data) to get the new schema.

### The Proposed Solution
Assuming the project migrates to an ORM like SQLAlchemy (Issue #3), we must implement Alembic to handle database migrations.
1. Initialize an Alembic environment (`alembic init alembic`).
2. Configure Alembic to read the metadata from our SQLAlchemy models.
3. Generate the initial baseline migration script based on the current database state.
4. Update the `README.md` to instruct contributors to run `alembic upgrade head` when deploying or pulling new code instead of relying on `init_db()`.

### Acceptance Criteria
- Alembic is fully configured and integrated into the project.
- The `CREATE TABLE IF NOT EXISTS` functions are removed from `database.py`.
- Adding a new column to a model and running `alembic revision --autogenerate` successfully generates a valid migration script.
- Existing databases can be upgraded without data loss.

### Benefits
Database migrations are a mandatory requirement for any production-grade software that evolves over time. It allows developers to seamlessly add features that alter the database schema without destroying users' historical data.
