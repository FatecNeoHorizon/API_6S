# User Manual - API_6S Zeus Project

Guide for operating the Zeus system with a focus on interface navigation, APIs, and ETL execution.

## Contents

- Access to web application and backend
- Use of current available dashboards
- Processing of DEC/FEC indicators and API queries
- Limitations observed in the current ZIP version

**Documentation sources consulted:** Main README, documentation in `docs/`, `docker-compose.yml`, backend/frontend files, SQL migrations, and project folder structure.

---

## 1. System Purpose

According to the project README, the platform's objective is to process public data from ANEEL and transform raw information into actionable indicators, enabling:

- Identification of priority regions by power supply quality
- Analysis of energy losses
- Assessment of network vulnerability

In the available ZIP version, usage focuses on three fronts:
- Web interface
- Backend Swagger documentation
- Processing and querying of indicators data in MongoDB

---

## 2. How to Access the System

After installation, the user interacts with three main points:

| Resource | Default Address | Use |
|----------|-----------------|-----|
| Web application | `http://localhost:5173` | Visual navigation through dashboards |
| API / Swagger | `http://localhost:8000/docs` | Testing endpoints and inspecting contracts |
| Mongo Express | `http://localhost:8081` | Verification of collections loaded in MongoDB |

---

## 3. Navigation Through the Web Application

The frontend uses React Router and focuses usage on the `/dashboard` path. The main layout includes:
- Sidebar with available modules
- Top header with user identification

### 3.1 Modules Found in the Sidebar Menu

| Menu | Route | Functional Description |
|------|-------|----------------------|
| Indicators | `/dashboard/indicadores` | Displays cards, charts, and rankings of continuity and loss indicators |
| DEC/FEC and Losses | `/dashboard/indicadores` | Visualizes DEC, FEC, and energy loss data |
| Network Structure | `/dashboard/estrutura-redes` | Displays network assets, filters, and operational details |

### 3.2 Dashboard Home Page

The `/dashboard` route loads a summary panel with:
- Statistics cards
- List of recent activities
- Relation of main regions

This area serves as a quick executive view of the network situation.

---

## 4. Using the Indicators Page

The indicators screen organizes the experience into two tabs:

### 4.1 DEC/FEC Tab

Shows:
- Summary cards
- Evolution chart
- Comparison between distributors

### 4.2 Losses Tab

Shows:
- Cards and visualizations of technical losses
- Losses in currency
- Total losses

### 4.3 Periods

The user can switch between:
- 3 months
- 6 months
- 9 months
- 1 year
- Custom period (dedicated button)

> **⚠️ Important:** The data currently displayed in the frontend of this version is mostly **mocked** (illustrative) in React components. The page demonstrates the navigation structure and visual presentation, but does not necessarily reflect a dynamic real-time query to the backend in all blocks.

---

## 5. Using the Network Structure Page

The **Network Structure** screen presents a list of infrastructure assets such as substations and transformers.

### Features

- **Search field** by asset name or code
- **Filters** by region, asset type, and status
- **Item selection** to view operational details, capacity, load, temperature, and maintenance
- **Visual actions** for update/export in the layout

> **Note:** The data used in the frontend present in the ZIP is also simulated for interface demonstration purposes.

---

## 6. Using the API via Swagger

The FastAPI offers simple example endpoints, an endpoint to process the CSV of indicators, and endpoints to query MongoDB.

**Most practical way of use:** Open Swagger at `/docs`, expand the desired route, fill in parameters, and click **Execute**.

### 6.1 Available Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Simple test return |
| `/process-decfec` | GET | Processes CSV file and loads DEC/FEC into MongoDB |
| `/get-dec-fec` | GET | Queries `distribution_indices` collection with filters |
| `/get-energy-losses` | GET | Queries `energy_losses_tariff` collection with filters |
| `/exemplo-post-body-schema` | POST | Example of body submission with Pydantic schema |

### 6.2 Processing CSV Indicators

To populate the continuity indicators collection, run:

```bash
GET http://localhost:8000/process-decfec
```

The backend will:
1. Read the file defined by `CSV_FILE_PATH`
2. Call the `load_decfec.py` routine
3. Apply the transformation step
4. Record valid entries in MongoDB

If all goes well, the response will inform how many lines were inserted.

### 6.3 Querying DEC/FEC with Filters

After processing, use the `/get-dec-fec` endpoint. The filters accepted in the current code are:

- `agent_acronym`
- `cnpj_number`
- `consumer_unit_set_id`
- `indicator_type_code`
- `year`
- `period`

**Example:**
```
/get-dec-fec?indicator_type_code=DEC&year=2024&period=1
```

### 6.4 Querying Energy Losses

The `/get-energy-losses` route accepts filters such as:
- `distributor`
- `distributor_slug`
- `state`
- `uf`
- `process_date`

> **Important:** This query depends on the `energy_losses_tariff` collection already existing and containing valid data in MongoDB.

**Example:**
```
/get-energy-losses?uf=SP
```

---

## 7. What Happens in the ETL During Use

The ETL part observed in the ZIP follows the flow: **Extract → Transform → Load**

The CSV file is read by the backend, the transformation step is triggered, and documents are prepared for recording in the `distribution_indices` collection. The project structure also includes schema and index preparation in MongoDB in the `src/etl/database.py` routine.

### 7.1 ETL Flow

| Step | Main File | Operational Function |
|------|-----------|----------------------|
| **Extraction** | `src/etl/get_decfec_file.py` + `load_decfec.py` | Read the CSV path and load the file with pandas |
| **Transformation** | `src/etl/transform_decfec.py` | Execute validations/preparations without changing final structure |
| **Loading** | `src/etl/load_decfec.py` | Filter DEC/FEC, adjust types, and insert into MongoDB collection |

---

## 8. Query and Verification in Mongo Express

After the loading is executed, open Mongo Express and navigate:

1. Access the database defined in `MONGO_DB_NAME`
2. Confirm the presence of collections:
   - `distribution_indices`
   - `domain_indicators`
   - `energy_losses_tariff` (when data is loaded)

This verification is useful for reviewing whether the ETL actually persisted the expected data.

---

## 9. Profiles and Sensitive Data

The project documentation and SQL migrations indicate a separation between:

- **Public data** (MongoDB)
- **Sensitive/LGPD data** (PostgreSQL)

Relational tables include:
- Profiles
- Users
- Sessions
- Authentication attempts
- Consents
- Policies

> **Note:** The frontend version present in the ZIP does not yet expose a complete operational authentication flow. Therefore, current practical use is more centered on dashboards and technical endpoints than on a finalized multi-user portal.

---

## 10. Limitations Observed in This ZIP Version

- Much of the frontend uses **demonstration data** loaded directly in React components
- Not all endpoints mentioned by the frontend exist in a functional form in the current backend
- Energy loss processing depends on a specific collection already populated
- The `data` folder came empty in the ZIP, so the user needs to provide the CSV to test the ETL

---

## 11. Suggested Usage Routine

1. Start the environment with Docker Compose
2. Open Swagger and execute `/process-decfec` to load the indicators file
3. Validate the data in Mongo Express
4. Use `/get-dec-fec` and `/get-energy-losses` to test filters and API responses
5. Open the frontend at `/dashboard` to navigate the visual experience of the system

---

**Last updated:** April 5, 2026
