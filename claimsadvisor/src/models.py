from pydantic import BaseModel, Field
from typing import List, Optional

class ExpenseItem(BaseModel):
    description: str = Field(..., description="Description of the expense or transaction")
    amount: float = Field(..., description="The monetary amount of the transaction")
    date: Optional[str] = Field(None, description="The date of the transaction if available")
    vendor: Optional[str] = Field(None, description="The vendor or merchant name")

class ExtractedData(BaseModel):
    items: List[ExpenseItem] = Field(..., description="List of all extracted expense items")

class AuditResult(BaseModel):
    description: str = Field(..., description="Description of the expense")
    amount: float = Field(..., description="Amount claimed")
    section: str = Field(..., description="Tax section (e.g., 80C, 80D, HRA)")
    category: str = Field(..., description="Category (Valid, Review Needed, Rejected)")
    reasoning: str = Field(..., description="Reasoning for the audit decision")

class FinalAuditReport(BaseModel):
    audited_claims: List[AuditResult] = Field(..., description="List of all audited claims with their status")
    total_valid_amount: float = Field(..., description="Total sum of valid claims")
    summary: str = Field(..., description="A brief executive summary of the audit")
