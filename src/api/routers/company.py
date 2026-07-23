from fastapi import APIRouter, HTTPException
import pandas as pd

from src.api.database import get_connection

router = APIRouter(prefix="/companies", tags=["Companies"])


@router.get("/")
def get_all_companies():
    """
    Return all companies.
    """
    conn = get_connection()

    query = """
    SELECT
        id AS company_id,
        company_name
    FROM companies
    ORDER BY company_name
    """

    df = pd.read_sql(query, conn)
    conn.close()

    return df.to_dict(orient="records")


@router.get("/{company_id}")
def get_company(company_id: str):

    conn = get_connection()

    company = pd.read_sql(
        """
        SELECT *
        FROM companies
        WHERE id=?
        """,
        conn,
        params=(company_id,),
    )

    if company.empty:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )

    ratios = pd.read_sql(
        """
        SELECT *
        FROM financial_ratios
        WHERE company_id=?
        ORDER BY year
        """,
        conn,
        params=(company_id,),
    )

    conn.close()

    # Convert NaN -> None
    company_records = json.loads(company.to_json(orient="records"))
    ratio_records = json.loads(ratios.to_json(orient="records"))

    return {
        "company": company_records[0],
        "financial_ratios": ratio_records
    }