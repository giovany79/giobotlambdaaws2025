from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from domain.entities.movement import Movement, MovementType


class MovementRepositoryInterface(ABC):
    @abstractmethod
    def add_movement(self, movement: Movement) -> bool:
        pass
        
    @abstractmethod
    def get_movements(
        self, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        category: Optional[str] = None,
        movement_type: Optional[MovementType] = None
    ) -> List[Movement]:
        pass
        
    @abstractmethod
    def get_categories(self) -> List[str]:
        pass
