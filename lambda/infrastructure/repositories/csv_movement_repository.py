import os
from datetime import datetime
from typing import List, Optional
from pathlib import Path

from domain.entities.movement import Movement, MovementType
from domain.interfaces.movement_repository_interface import MovementRepositoryInterface


class CSVMovementRepository(MovementRepositoryInterface):
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Ensure the CSV file exists with headers if it doesn't exist."""
        if not os.path.exists(self.file_path):
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.write("Description;Income/expensive;Amount;Category;Date\n")
    
    def add_movement(self, movement: Movement) -> bool:
        try:
            with open(self.file_path, 'a', encoding='utf-8') as f:
                f.write(movement.to_csv_row())
            return True
        except Exception as e:
            return False
    
    def get_movements(
        self, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        category: Optional[str] = None,
        movement_type: Optional[MovementType] = None
    ) -> List[Movement]:
        movements = []
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    movement = Movement.from_csv_row(line)
                    if movement is None:
                        continue
                        
                    # Apply filters
                    if start_date and movement.date < start_date:
                        continue
                    if end_date and movement.date > end_date:
                        continue
                    if category and movement.category.lower() != category.lower():
                        continue
                    if movement_type and movement.movement_type != movement_type:
                        continue
                        
                    movements.append(movement)
        except FileNotFoundError:
            pass
            
        return movements
    
    def get_categories(self) -> List[str]:
        categories = set()
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                next(f)  # Skip header
                for line in f:
                    movement = Movement.from_csv_row(line)
                    if movement and movement.category:
                        categories.add(movement.category.strip().lower())
        except FileNotFoundError:
            pass
            
        return sorted(categories)
