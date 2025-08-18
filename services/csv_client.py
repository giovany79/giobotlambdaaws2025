import csv
from datetime import datetime
import pandas as pd

CSV_FILE = 'movements.csv'

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
    
    # Categorías de gastos
    expense_by_category = df[df['Income/expensive'] == 'expensive'].groupby('Category')['Amount'].sum().sort_values(ascending=False)
    
    # Preparar contexto para la respuesta
    context = f"""
    Resumen Financiero:
    - Ingresos totales: ${total_income:,.0f}
    - Gastos totales: ${total_expenses:,.0f}
    - Balance: ${balance:,.0f}
    
    Gastos por categoría:
    """
    
    for category, amount in expense_by_category.items():
        context += f"  - {category}: ${amount:,.0f}\n"
    
    # Usar OpenAI para responder la pregunta basada en los datos
    prompt = f"""
    Eres un asistente financiero. Basándote en los siguientes datos:
    {context}
    
    Responde de manera clara y concisa la siguiente pregunta:
    {question}
    """
    
    return prompt