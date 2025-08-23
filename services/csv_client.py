import os
import csv
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union
import pandas as pd
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Transaction:
    """Clase para representar una transacción financiera."""
    date: datetime
    description: str
    amount: float
    category: str
    type: str  # 'income' o 'expensive'


class CSVFinanceManager:
    """Clase para manejar operaciones financieras con archivos CSV."""
    
    def __init__(self, csv_path: Optional[str] = None):
        """
        Inicializa el gestor de finanzas con la ruta al archivo CSV.
        
        Args:
            csv_path: Ruta al archivo CSV. Si es None, usa el archivo por defecto.
        """
        if csv_path is None:
            self.csv_path = Path(__file__).parent / 'movements.csv'
        else:
            self.csv_path = Path(csv_path)
        
        self.df = self._load_and_clean_data()
    
    def _load_and_clean_data(self) -> pd.DataFrame:
        """Carga y limpia los datos del archivo CSV."""
        try:
            # Cargar datos
            df = pd.read_csv(
                self.csv_path, 
                delimiter=';',
                parse_dates=['Date'],
                dayfirst=True
            )
            
            # Limpiar nombres de columnas
            df.columns = [col.strip() for col in df.columns]
            
            # Limpiar y convertir montos
            df['Amount'] = (
                df['Amount']
                .astype(str)
                .str.strip()
                .str.replace('$', '', regex=False)
                .str.replace('.', '', regex=False)
                .str.replace(',', '.', regex=False)
                .astype(float)
            )
            
            # Filtrar filas con montos o fechas inválidas
            df = df.dropna(subset=['Date', 'Amount'])
            
            # Normalizar categoría y tipo
            if 'Category' in df.columns:
                df['Category'] = df['Category'].str.strip()
            
            if 'Income/expensive' in df.columns:
                df['Type'] = df['Income/expensive'].str.strip().str.lower()
            
            return df
            
        except Exception as e:
            raise ValueError(f"Error al cargar el archivo CSV: {str(e)}")
    
    def get_transactions(self) -> List[Transaction]:
        """Devuelve una lista de objetos Transaction."""
        transactions = []
        for _, row in self.df.iterrows():
            try:
                tx = Transaction(
                    date=row['Date'],
                    description=row.get('Description', '').strip(),
                    amount=float(row['Amount']),
                    category=row.get('Category', 'Sin categoría').strip(),
                    type=row.get('Type', 'expensive' if float(row['Amount']) < 0 else 'income')
                )
                transactions.append(tx)
            except Exception as e:
                print(f"Error al procesar transacción: {row}. Error: {str(e)}")
        return transactions
    
    def get_monthly_summary(self) -> Dict:
        """
        Genera un resumen financiero mensual.
        
        Returns:
            Dict con el formato:
            {
                'months': [lista de meses en formato 'YYYY-MM'],
                'categories': {
                    'Categoría1': [gasto_mes1, gasto_mes2, ...],
                    'Categoría2': [gasto_mes1, gasto_mes2, ...],
                    ...
                }
            }
        """
        if self.df.empty:
            return {'months': [], 'categories': {}}
        
        # Crear copia para no modificar el DataFrame original
        df = self.df.copy()
        
        # Filtrar solo gastos
        expenses_df = df[df['Type'] == 'expensive']
        if expenses_df.empty:
            return {'months': [], 'categories': {}}
        
        # Crear columna de mes
        expenses_df['Month'] = expenses_df['Date'].dt.to_period('M').dt.strftime('%Y-%m')
        
        # Obtener meses únicos ordenados
        all_months = sorted(expenses_df['Month'].unique())
        
        # Agrupar por categoría y mes
        grouped = expenses_df.groupby(['Category', 'Month'])['Amount'].sum().unstack(fill_value=0)
        
        # Asegurar que todos los meses estén presentes
        for month in all_months:
            if month not in grouped.columns:
                grouped[month] = 0
        
        # Ordenar columnas (meses)
        grouped = grouped[all_months] if all_months else pd.DataFrame()
        
        # Convertir a diccionario
        return {
            'months': all_months,
            'categories': {category: amounts.tolist() 
                         for category, amounts in grouped.iterrows()}
        }
    
    def get_financial_summary(self) -> Dict:
        """
        Genera un resumen financiero general.
        
        Returns:
            Dict con el resumen financiero.
        """
        if self.df.empty:
            return {}
        
        # Cálculos básicos
        income = self.df[self.df['Type'] == 'income']['Amount'].sum()
        expenses = self.df[self.df['Type'] == 'expensive']['Amount'].sum()
        balance = income - expenses
        
        # Gastos por categoría
        expenses_by_category = (
            self.df[self.df['Type'] == 'expensive']
            .groupby('Category')['Amount']
            .sum()
            .sort_values(ascending=False)
            .to_dict()
        )
        
        return {
            'total_income': income,
            'total_expenses': expenses,
            'balance': balance,
            'expenses_by_category': expenses_by_category
        }
    
    def analyze_finances(self, question: str) -> str:
        """
        Analiza las finanzas y genera una respuesta a una pregunta.
        
        Args:
            question: Pregunta sobre los datos financieros.
            
        Returns:
            Respuesta formateada.
        """
        # Obtener datos para el análisis
        monthly_data = self.get_monthly_summary()
        summary = self.get_financial_summary()
        
        # Generar contexto
        context = f"""
        Resumen Financiero:
        - Ingresos totales: ${summary['total_income']:,.0f}
        - Gastos totales: ${summary['total_expenses']:,.0f}
        - Balance: ${summary['balance']:,.0f}
        
        Gastos por categoría:
        """
        
        for category, amount in summary['expenses_by_category'].items():
            context += f"  - {category}: ${amount:,.0f}\n"
        
        # Agregar gastos por categoría por mes
        if monthly_data['months']:
            context += "\nGastos por categoría por mes:\n"
            
            for month in monthly_data['months']:
                month_total = sum(
                    monthly_data['categories'][cat][monthly_data['months'].index(month)]
                    for cat in monthly_data['categories']
                )
                
                context += f"\n  {month} (Total: ${month_total:,.0f}):\n"
                
                # Ordenar categorías por monto descendente
                sorted_categories = sorted(
                    [(cat, monthly_data['categories'][cat][monthly_data['months'].index(month)]) 
                     for cat in monthly_data['categories'] 
                     if monthly_data['categories'][cat][monthly_data['months'].index(month)] > 0],
                    key=lambda x: x[1],
                    reverse=True
                )
                
                for category, amount in sorted_categories:
                    context += f"    - {category}: ${amount:,.0f}\n"
        
        # Aquí podrías integrar con OpenAI para responder preguntas específicas
        # Por ahora, simplemente devolvemos el contexto
        return context


# Funciones de conveniencia para mantener compatibilidad con el código existente
def get_expenses_by_category_per_month():
    """Función de conveniencia para mantener compatibilidad."""
    manager = CSVFinanceManager()
    return manager.get_monthly_summary()

def analyze_finances(question: str) -> str:
    """Función de conveniencia para mantener compatibilidad."""
    manager = CSVFinanceManager()
    return manager.analyze_finances(question)