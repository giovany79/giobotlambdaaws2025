import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from domain.entities.movement import Movement, MovementType
from domain.interfaces.movement_repository_interface import MovementRepositoryInterface
from use_cases.handle_movement_command import HandleMovementCommandUseCase, HandleMovementCommandRequest


class MockMovementRepository(MovementRepositoryInterface):
    def __init__(self):
        self.movements = []
    
    def add_movement(self, movement: Movement) -> bool:
        self.movements.append(movement)
        return True
    
    def get_movements(self, start_date=None, end_date=None, category=None, movement_type=None):
        result = self.movements.copy()
        
        if start_date:
            result = [m for m in result if m.date >= start_date]
        if end_date:
            result = [m for m in result if m.date <= end_date]
        if category:
            result = [m for m in result if m.category.lower() == category.lower()]
        if movement_type:
            result = [m for m in result if m.movement_type == movement_type]
            
        return result
    
    def get_categories(self) -> list:
        return list(set(m.category.lower() for m in self.movements))


class TestHandleMovementCommandUseCase(unittest.TestCase):
    def setUp(self):
        self.repo = MockMovementRepository()
        self.usecase = HandleMovementCommandUseCase(self.repo)
        self.now = datetime.now()
        
        # Add some test data
        self.test_movements = [
            Movement("Salary", MovementType.INCOME, 3000000, "salary", self.now - timedelta(days=10)),
            Movement("Rent", MovementType.EXPENSE, 1500000, "housing", self.now - timedelta(days=5)),
            Movement("Supermarket", MovementType.EXPENSE, 350000, "food", self.now - timedelta(days=3)),
            Movement("Restaurant", MovementType.EXPENSE, 45000, "food", self.now - timedelta(days=1)),
        ]
        
        for movement in self.test_movements:
            self.repo.add_movement(movement)
    
    def test_add_movement(self):
        # Test adding a new expense
        request = HandleMovementCommandRequest(
            command="agregar Uber;gasto;25000;transporte",
            chat_id="123",
            user_id="user1",
            message_id="msg1"
        )
        
        response = self.usecase.execute(request)
        self.assertTrue(response.success)
        self.assertIn("Uber", response.message)
        self.assertIn("25,000", response.message)
        
        # Verify the movement was added
        movements = self.repo.get_movements()
        self.assertEqual(len(movements), 5)  # 4 from setup + 1 new
        self.assertEqual(movements[-1].description, "Uber")
    
    def test_view_movements(self):
        # Test viewing all movements
        request = HandleMovementCommandRequest(
            command="ver",
            chat_id="123",
            user_id="user1",
            message_id="msg1"
        )
        
        response = self.usecase.execute(request)
        self.assertTrue(response.success)
        self.assertIn("Movimientos encontrados: 4", response.message)
    
    def test_filter_movements_by_category(self):
        # Test filtering by category
        request = HandleMovementCommandRequest(
            command="ver categoria:food",
            chat_id="123",
            user_id="user1",
            message_id="msg1"
        )
        
        response = self.usecase.execute(request)
        self.assertTrue(response.success)
        self.assertIn("Movimientos encontrados: 2", response.message)
    
    def test_get_summary(self):
        # Test getting a summary
        request = HandleMovementCommandRequest(
            command="resumen ultimos 30",
            chat_id="123",
            user_id="user1",
            message_id="msg1"
        )
        
        response = self.usecase.execute(request)
        self.assertTrue(response.success)
        self.assertIn("Resumen de los últimos 30 días", response.message)
        self.assertIn("Ingresos: $3,000,000", response.message)
        self.assertIn("Gastos: $1,895,000", response.message)  # 1,500,000 + 350,000 + 45,000
    
    def test_list_categories(self):
        # Test listing categories
        request = HandleMovementCommandRequest(
            command="categorias",
            chat_id="123",
            user_id="user1",
            message_id="msg1"
        )
        
        response = self.usecase.execute(request)
        self.assertTrue(response.success)
        self.assertIn("Categorías disponibles", response.message)
        self.assertIn("salary", response.message.lower())
        self.assertIn("housing", response.message.lower())
        self.assertIn("food", response.message.lower())


if __name__ == "__main__":
    unittest.main()
