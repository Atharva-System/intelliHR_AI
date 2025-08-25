from pydantic import BaseModel, Field
from typing import Optional, List


class JobInput(BaseModel):
    title: str
    experienceRange: str
    department: str
    subDepartment: Optional[str] = None