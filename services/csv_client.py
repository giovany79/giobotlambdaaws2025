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

def get_expenses_by_category_per_month():
    """
    Obtiene los gastos agrupados por categoría y mes
    
    Returns:
        dict: Diccionario con la estructura {
            'months': [lista de meses en formato 'YYYY-MM'],
            'categories': {
                'Categoría1': [gasto_mes1, gasto_mes2, ...],
                'Categoría2': [gasto_mes1, gasto_mes2, ...],
                ...
            }
        }
    """
    transactions = load_transactions()
    if not transactions:
        return {'months': [], 'categories': {}}
    
    df = pd.DataFrame(transactions)
    
    # Limpieza y conversión de datos
    df['Amount'] = df['Amount'].str.strip()
    df = df[df['Amount'] != '']
    df['Amount'] = (
        df['Amount']
        .str.replace('$', '', regex=False)
        .str.replace('.', '', regex=False)
        .str.replace(',', '.', regex=False)
        .astype(float)
    )
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])
    
    # Filtrar solo gastos
    expenses_df = df[df['Income/expensive'] == 'expensive'].copy()
    if len(expenses_df) == 0:
        return {'months': [], 'categories': {}}
    
    # Crear columna de mes
    expenses_df['Month'] = expenses_df['Date'].dt.to_period('M').dt.strftime('%Y-%m')
    
    # Obtener todos los meses únicos ordenados
    all_months = sorted(expenses_df['Month'].unique())
    
    # Agrupar por categoría y mes
    grouped = expenses_df.groupby(['Category', 'Month'])['Amount'].sum().unstack(fill_value=0)
    
    # Asegurarse de que todos los meses estén presentes para cada categoría
    for month in all_months:
        if month not in grouped.columns:
            grouped[month] = 0
    
    # Ordenar columnas (meses)
    grouped = grouped[all_months]
    
    # Convertir a diccionario
    result = {
        'months': all_months,
        'categories': {}
    }
    
    for category, row in grouped.iterrows():
        result['categories'][category] = row.tolist()
    
    return result

def analyze_finances(question):
    """Analizar datos financieros y responder preguntas"""
    transactions = load_transactions()
    
    # Convertir a DataFrame para análisis más fácil
    df = pd.DataFrame(transactions)
    
    # Limpiar y convertir montos a numérico
    df['Amount'] = df['Amount'].str.strip()
    df = df[df['Amount'] != '']
    
    if len(df) == 0:
        return "No se encontraron transacciones válidas para analizar."
    
    df['Amount'] = (
        df['Amount']
        .str.replace('$', '', regex=False)
        .str.replace('.', '', regex=False)
        .str.replace(',', '.', regex=False)
        .astype(float)
    )
    
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])
    
    if len(df) == 0:
        return "No se encontraron transacciones con fechas válidas para analizar."
    
    # Obtener gastos por categoría por mes con detalles de transacciones
    expenses_data = get_expenses_by_category_per_month()
    
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
    if expenses_data['months']:
        context += "\nGastos por categoría por mes:\n"
        
        # Obtener todas las categorías únicas
        categories = list(expenses_data['categories'].keys())
        
        # Procesar cada mes
        for month in expenses_data['months']:
            month_total = sum(expenses_data['categories'][category][expenses_data['months'].index(month)] 
                            for category in categories)
            
            context += f"\n  {month} (Total: ${month_total:,.0f}):\n"
            
            # Obtener y ordenar categorías por monto descendente
            sorted_categories = sorted(
                [(cat, expenses_data['categories'][cat][expenses_data['months'].index(month)]) 
                 for cat in categories 
                 if expenses_data['categories'][cat][expenses_data['months'].index(month)] > 0],
                key=lambda x: x[1],
                reverse=True
            )
            
            for category, amount in sorted_categories:
                context += f"    - {category}: ${amount:,.0f}\n"
    
    # Usar OpenAI para responder la pregunta basada en los datos
    prompt = f"""
    Eres un asistente financiero. Basándote en los siguientes datos:
    {context}
    
    Responde de manera clara y concisa la siguiente pregunta:
    {question}
    """
    
    return prompt