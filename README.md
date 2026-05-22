# RTI Filer

A small application for preparing and submitting RTI (Right to Information) requests.

## Project structure

- `RTI_Filer/` — Backend Python application and supporting files
  - `app.py`, `main.py` — application entry points
  - `core/` — backend modules (`classifier.py`, `db.py`, `pdf_gen.py`, `validator.py`, `fallback.py`)
  - `data/ministries.json` — reference data used by the app
  - `database/schema.sql` — DB schema and initialization SQL
  - `outputs/` — generated outputs (PDFs, logs, exports)
- `rti-frontend/` — Angular frontend application

## Features

- Compose RTI requests via a web UI
- Backend validation, classification and PDF generation
- Simple DB schema for storing requests and metadata

## Prerequisites

- Python 3.9+ (or your preferred 3.x)
- Node.js 16+ and npm (for frontend)

## Backend — Quick start

1. Create a virtual environment and activate it:

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1   # PowerShell
# or use .venv\\Scripts\\activate for cmd
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Initialize the database (if needed):

```bash
sqlite3 database/app.db < database/schema.sql
```

4. Run the backend:

```bash
python app.py
# or
python main.py
```

Adjust the command above based on which file starts your web server.

## Frontend — Quick start

1. Change into the frontend folder and install packages:

```bash
cd rti-frontend
npm install
```

2. Run the dev server:

```bash
npm start
```

The frontend typically runs on `http://localhost:4200` unless configured otherwise in `angular.json`.

## Configuration

- Place or update environment-specific settings in the appropriate config files (backend environment vars, `rti-frontend/src/environments/`).
- The backend reads initial data from `data/ministries.json`.

## Database

- The SQL schema is in `database/schema.sql` — adapt and apply to your chosen DB.
- Default setup in examples uses SQLite and `database/app.db`.

## Generating PDFs and outputs

- Generated artifacts are written to the `outputs/` folder. Ensure it exists and is writable.

## Testing and linting

- Backend: add or run tests as appropriate (no tests included by default).
- Frontend: run `npm test` inside `rti-frontend` if tests are configured.

## Contributing

Contributions are welcome. Please open issues or pull requests with clear descriptions.

## License

Add a license file (e.g., `LICENSE`) and update this section accordingly.

## Contact

For questions or help, open an issue in this repository or contact the maintainers.
