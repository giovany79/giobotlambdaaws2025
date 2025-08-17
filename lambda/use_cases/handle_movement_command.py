from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from domain.entities.movement import Movement, MovementType
from domain.interfaces.movement_repository_interface import MovementRepositoryInterface


@dataclass
class HandleMovementCommandRequest:
    command: str
    chat_id: str
    user_id: str
    message_id: str
    

@dataclass
class HandleMovementCommandResponse:
    success: bool
    message: str
    movements: List[Movement] = None


class HandleMovementCommandUseCase:
    def __init__(self, movement_repo: MovementRepositoryInterface):
        self.movement_repo = movement_repo
    
    def execute(self, request: HandleMovementCommandRequest) -> HandleMovementCommandResponse:
        command_parts = request.command.lower().split()
        if not command_parts:
            return self._create_response(False, "Comando no válido")
            
        action = command_parts[0]
        
        if action == "agregar":
            return self._handle_add_movement(' '.join(command_parts[1:]))
        elif action in ["ver", "mostrar"]:
            return self._handle_view_movements(' '.join(command_parts[1:]))
        elif action == "categorias":
            return self._handle_list_categories()
        elif action == "resumen":
            return self._handle_summary(' '.join(command_parts[1:]))
        else:
            return self._create_response(False, "Comando no reconocido. Usa 'ayuda' para ver comandos disponibles.")
    
    def _handle_add_movement(self, args: str) -> HandleMovementCommandResponse:
        try:
            # Expected format: "descripcion;tipo;monto;categoria [;fecha]"
            parts = [p.strip() for p in args.split(';')]
            if len(parts) < 4:
                return self._create_response(False, "Formato incorrecto. Usa: agregar descripcion;tipo(ingreso/gasto);monto;categoria[;fecha]")
            
            description = parts[0]
            movement_type = MovementType(parts[1].lower())
            amount = float(parts[2].replace('$', '').replace(',', '').strip())
            category = parts[3]
            
            # Parse date if provided, otherwise use current date
            if len(parts) > 4:
                date = datetime.strptime(parts[4], "%Y-%m-%d")
            else:
                date = datetime.now()
            
            movement = Movement(
                description=description,
                movement_type=movement_type,
                amount=amount,
                category=category,
                date=date
            )
            
            if self.movement_repo.add_movement(movement):
                return self._create_response(True, f"✅ Movimiento agregado: {movement.description} - ${movement.amount:,.0f}")
            else:
                return self._create_response(False, "❌ Error al guardar el movimiento")
                
        except ValueError as e:
            return self._create_response(False, f"Error en el formato: {str(e)}")
    
    def _handle_view_movements(self, args: str) -> HandleMovementCommandResponse:
        # Parse filters
        filters = {}
        if 'ultimos' in args:
            try:
                days = int(args.split('ultimos')[1].split()[0])
                filters['end_date'] = datetime.now()
                filters['start_date'] = datetime.now() - timedelta(days=days)
            except (ValueError, IndexError):
                pass
        
        if 'tipo:' in args:
            try:
                tipo = args.split('tipo:')[1].split()[0].lower()
                if tipo in ['ingreso', 'income']:
                    filters['movement_type'] = MovementType.INCOME
                elif tipo in ['gasto', 'expense']:
                    filters['movement_type'] = MovementType.EXPENSE
            except (ValueError, IndexError):
                pass
        
        if 'categoria:' in args:
            try:
                category = args.split('categoria:')[1].split(';')[0].strip()
                filters['category'] = category
            except (ValueError, IndexError):
                pass
        
        # Get filtered movements
        movements = self.movement_repo.get_movements(
            start_date=filters.get('start_date'),
            end_date=filters.get('end_date'),
            category=filters.get('category'),
            movement_type=filters.get('movement_type')
        )
        
        if not movements:
            return self._create_response(True, "No se encontraron movimientos con los filtros aplicados.")
        
        # Format response
        response = self._create_response(True, f"📊 Movimientos encontrados: {len(movements)}")
        response.movements = movements
        return response
    
    def _handle_list_categories(self) -> HandleMovementCommandResponse:
        categories = self.movement_repo.get_categories()
        if not categories:
            return self._create_response(True, "No hay categorías disponibles.")
        
        categories_text = "\n- " + "\n- ".join(categories)
        return self._create_response(True, f"📋 Categorías disponibles:{categories_text}")
    
    def _handle_summary(self, args: str) -> HandleMovementCommandResponse:
        # Default to last 30 days if no period specified
        days = 30
        if 'ultimos' in args:
            try:
                days = int(args.split('ultimos')[1].split()[0])
            except (ValueError, IndexError):
                pass
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get all movements in the period
        movements = self.movement_repo.get_movements(start_date=start_date, end_date=end_date)
        
        if not movements:
            return self._create_response(True, f"No hay movimientos en los últimos {days} días.")
        
        # Calculate totals
        total_income = sum(m.amount for m in movements if m.movement_type == MovementType.INCOME)
        total_expenses = sum(m.amount for m in movements if m.movement_type == MovementType.EXPENSE)
        balance = total_income - total_expenses
        
        # Group by category
        categories = {}
        for m in movements:
            if m.movement_type == MovementType.EXPENSE:
                categories[m.category] = categories.get(m.category, 0) + m.amount
        
        # Sort categories by amount (descending)
        sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        
        # Build response
        response_lines = [
            f"📊 Resumen de los últimos {days} días:",
            f"💰 Ingresos: ${total_income:,.0f}",
            f"💸 Gastos: ${total_expenses:,.0f}",
            f"⚖️ Balance: ${balance:,.0f}",
            "",
            "📋 Gastos por categoría:"
        ]
        
        for category, amount in sorted_categories:
            percentage = (amount / total_expenses * 100) if total_expenses > 0 else 0
            response_lines.append(f"- {category}: ${amount:,.0f} ({percentage:.1f}%)")
        
        return self._create_response(True, "\n".join(response_lines))
    
    def _create_response(self, success: bool, message: str, movements: List[Movement] = None) -> HandleMovementCommandResponse:
        return HandleMovementCommandResponse(
            success=success,
            message=message,
            movements=movements or []
        )
