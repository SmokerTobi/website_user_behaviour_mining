# Website User Behaviour Mining

A complete college project implementing all five units of the Data Mining & KDD syllabus on the Retailrocket e-commerce dataset.

## Student Details
**Himesh Bhure** | B.Tech CSE | SIT, Nagpur | Batch 2024–2028 | Semester 5 | Section A

## Project Structure
- `data/raw`: Raw Kaggle dataset files
- `data/processed`: Cleaned events, derived sessions, SQLite database
- `src/`: Source code for data processing, modeling, and Streamlit app
- `outputs/`: Model results, rules, clustering profiles
- `report/`: Generated DOCX report
- `presentation/`: Generated PPTX presentation
- `docs/`: Viva questions and demo script

## Setup and Run Instructions (Windows)

1. Ensure Python 3.9+ is installed.
2. Open PowerShell in this directory.
3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
4. Run Data Processing pipeline (this handles KDD steps like sessionization, aggregation, SQLite DB creation):
   ```powershell
   python src\data_processing.py
   ```
5. Run Modeling pipeline (Classification, Clustering, Association Rules):
   ```powershell
   python src\modeling.py
   ```
6. Generate Deliverables (Word Report & PowerPoint):
   ```powershell
   python src\create_report.py
   python src\create_presentation.py
   ```
7. Start the Dashboard:
   ```powershell
   streamlit run src\app.py
   ```

## Syllabus Coverage
- **Unit 1**: Data preprocessing, session derivation, cleaning implemented in `data_processing.py`.
- **Unit 2**: Concept description via aggregations and distributions in SQLite (App Tab 2).
- **Unit 3**: Classification models (Decision Tree, Naive Bayes, KNN) in `modeling.py`.
- **Unit 4**: Clustering (K-Means, etc.) & Association Rules (Apriori, FP-Growth) in `modeling.py`.
- **Unit 5**: Advanced web mining topics (Usage funnels, Synthetic Content/Structure/Spatial) in `app.py`.
