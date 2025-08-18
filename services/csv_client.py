import os
import csv
from datetime import datetime
import pandas as pd

# Get the absolute path to the CSV file
CSV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'movements.csv')

def load_transactions():
    """Cargar transacciones desde el archivo CSV"""
    transactions = []
    try:
        with open(CSV_FILE, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=';')
            for row in reader:
                # Limpiar los valores de espacios en blanco
                row = {k.strip(): v.strip() for k, v in row.items()}
                transactions.append(row)
        return transactions
    except Exception as e:
        print(f"Error al cargar transacciones: {str(e)}")
        return []

def analyze_finances(question):
    """Analizar datos financieros y responder preguntas"""
    transactions = load_transactions()
    
    # Convertir a DataFrame para análisis más fácil
    df = pd.DataFrame(transactions)
    
    # Limpiar y convertir montos a numérico
    # Primero, reemplazar valores vacíos con NaN y luego eliminarlos
    df['Amount'] = df['Amount'].str.strip()
    df = df[df['Amount'] != '']  # Eliminar filas con montos vacíos
    
    # Verificar si hay datos después de la limpieza
    if len(df) == 0:
        return "No se encontraron transacciones válidas para analizar."
    
    # Convertir los montos a numérico
    df['Amount'] = (
        df['Amount']
        .str.replace('$', '', regex=False)
        .str.replace('.', '', regex=False)
        .str.replace(',', '.', regex=False)
        .astype(float)
    )
    
    # Convertir fechas
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    
    # Eliminar filas con fechas inválidas
    df = df.dropna(subset=['Date'])
    
    # Verificar si hay datos después de la limpieza
    if len(df) == 0:
        return "No se encontraron transacciones con fechas válidas para analizar."
    
    # Análisis básico
    total_income = df[df['Income/expensive'] == 'income']['Amount'].sum()
    total_expenses = df[df['Income/expensive'] == 'expensive']['Amount'].sum()
    balance = total_income - total_expenses
    
    # Gastos por categoría
    expense_by_category = df[df['Income/expensive'] == 'expensive'].groupby('Category')['Amount'].sum().sort_values(ascending=False)
    
    # Cálculos mensuales
    df['Month'] = df['Date'].dt.to_period('M')
    
    # Ingresos por mes
    monthly_income = (
        df[df['Income/expensive'] == 'income']
        .groupby('Month')['Amount']
        .sum()
        .reset_index()
    )
    monthly_income['Month'] = monthly_income['Month'].dt.strftime('%Y-%m')
    
    # Gastos por mes
    monthly_expenses = (
        df[df['Income/expensive'] == 'expensive']
        .groupby('Month')['Amount']
        .sum()
        .reset_index()
    )
    monthly_expenses['Month'] = monthly_expenses['Month'].dt.strftime('%Y-%m')
    
    # Gastos por categoría por mes
    monthly_expenses_by_category = (
        df[df['Income/expensive'] == 'expensive']
        .groupby(['Month', 'Category'])['Amount']
        .sum()
        .unstack(fill_value=0)
        .reset_index()
    )
    monthly_expenses_by_category['Month'] = monthly_expenses_by_category['Month'].dt.strftime('%Y-%m')
    
    # Preparar contexto para la respuesta
    context = f"""
    Resumen Financiero:
    - Ingresos totales: ${total_income:,.0f}
    - Gastos totales: ${total_expenses:,.0f}
    - Balance: ${balance:,.0f}
    
    Ingresos por mes:
    """
    
    for _, row in monthly_income.iterrows():
        context += f"  - {row['Month']}: ${row['Amount']:,.0f}\n"
    
    context += "\nGastos por mes:\n"
    for _, row in monthly_expenses.iterrows():
        context += f"  - {row['Month']}: ${row['Amount']:,.0f}\n"
    
    context += "\nGastos por categoría:\n"
    for category, amount in expense_by_category.items():
        context += f"  - {category}: ${amount:,.0f}\n"
    
    # Agregar gastos por categoría por mes con totales
    if not monthly_expenses_by_category.empty:
        context += "\nGastos por categoría por mes:\n"
        
        # Obtener todas las categorías únicas
        categories = [col for col in monthly_expenses_by_category.columns if col != 'Month']
        
        # Crear un diccionario para almacenar totales por categoría
        category_totals = {category: 0 for category in categories}
        
        # Procesar cada mes
        for _, month_data in monthly_expenses_by_category.iterrows():
            month = month_data['Month']
            month_total = sum(month_data[category] for category in categories)
            
            context += f"\n  {month} (Total: ${month_total:,.0f}):\n"
            
            # Ordenar categorías por monto descendente para el mes actual
            sorted_categories = sorted(
                [(cat, month_data[cat]) for cat in categories if month_data[cat] > 0],
                key=lambda x: x[1],
                reverse=True
            )
            
            for category, amount in sorted_categories:
                percentage = (amount / month_total) * 100 if month_total > 0 else 0
                context += f"    - {category}: ${amount:,.0f} ({percentage:.1f}%)\n"
                # Acumular totales por categoría
                category_totals[category] += amount
        
        # Agregar totales por categoría
        context += "\n  Total por categoría (todos los meses):\n"
        for category, total in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
            if total > 0:  # Solo mostrar categorías con gastos
                percentage = (total / total_expenses) * 100 if total_expenses > 0 else 0
                context += f"    - {category}: ${total:,.0f} ({percentage:.1f}% del total de gastos)\n"
    
    # Usar OpenAI para responder la pregunta basada en los datos
    prompt = f"""
    Eres un asistente financiero. Basándote en los siguientes datos:
    {context}
    
    Responde de manera clara y concisa la siguiente pregunta:
    {question}
    """
    
    return prompt