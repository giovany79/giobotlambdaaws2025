from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class MovementType(str, Enum):
    INCOME = "income"
    EXPENSE = "expensive"


@dataclass
class Movement:
    description: str
    movement_type: MovementType
    amount: float
    category: str
    date: datetime
    
    def to_csv_row(self) -> str:
        return (
            f'{";".join([
                self.description,
                self.movement_type,
                f"${self.amount:,.0f}",
                self.category,
                self.date.strftime("%Y-%m-%d %H:%M:%S")
            ])}\n'
        )
    
    @classmethod
    def from_csv_row(cls, row: str) -> 'Movement':
        if not row.strip() or row.startswith('Description'):
            return None
            
        parts = [p.strip() for p in row.split(';')]
        if len(parts) != 5:
            return None
            
        try:
            amount_str = parts[2].replace('$', '').replace(',', '').strip()
            return cls(
                description=parts[0],
                movement_type=MovementType(parts[1].lower()),
                amount=float(amount_str),
                category=parts[3],
                date=datetime.strptime(parts[4], "%Y-%m-%d %H:%M:%S")
            )
        except (ValueError, IndexError) as e:
            return None
