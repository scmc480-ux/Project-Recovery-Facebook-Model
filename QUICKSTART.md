# Quickstart

## 1. Clone And Enter The Repo

```powershell
git clone <repo-url> Project-Recovery
cd Project-Recovery
```

## 2. Optional Virtual Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Facebook Reader v1 uses only the Python standard library.

## 3. Run The Sample

```powershell
python -m recovery_engine.cli facebook --source examples/facebook_sample --case-id SAMPLE_FACEBOOK_CASE --output outputs
```

## 4. Inspect Outputs

Open:

```text
outputs/SAMPLE_FACEBOOK_CASE/00_README.md
outputs/SAMPLE_FACEBOOK_CASE/03_WORKBOOKS/messages.xlsx
outputs/SAMPLE_FACEBOOK_CASE/04_REPORTS/summary.md
```

## 5. Run Against Your Own Facebook Export

Use either an extracted export folder or a zip file:

```powershell
python -m recovery_engine.cli facebook --source "<path-to-facebook-export>" --case-id MY_CASE --output outputs
```

Do not commit your export or generated outputs.

To return the clone to release-check shape after experimenting, delete the
generated `outputs/` folder and run:

```powershell
python scripts/verify_public_repo.py .
```
