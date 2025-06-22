# QAPRO Sample Implementation

This directory contains a lightweight prototype of the QAPRO accreditation workflow. It is not production-ready but demonstrates the core flow:

1. Provider registration
2. Task creation and completion
3. Document uploads
4. Simple internal audit that checks if tasks are complete

## Running

Install dependencies and run the Flask development server:

```bash
pip install flask flask_sqlalchemy
python qapro/app.py
```

The app will create an SQLite database (`qapro.db`) and a folder `uploads/` for uploaded documents.
