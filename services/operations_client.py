import json
import os
import pandas as pd
from services import csv_client

MONTH_MAP = {
    # Spanish months
    'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6,
    'julio': 7, 'agosto': 8, 'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12,
    # English months
    'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
    'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12,
    # Short forms (both languages)
    'ene': 1, 'feb': 2, 'mar': 3, 'abr': 4, 'may': 5, 'jun': 6,
    'jul': 7, 'ago': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dic': 12,
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'jun': 6,
    'jul': 7, 'aug': 8, 'sept': 9, 'oct': 10, 'nov': 11, 'dec': 12
}

def _get_prepared_data():
    """Loads and prepares the financial data from the CSV file."""
    transactions = csv_client.load_transactions()
    if not transactions:
        return pd.DataFrame()

    df = pd.DataFrame(transactions)

    # Clean and convert 'Amount' column
    df['Amount'] = df['Amount'].str.strip()
    df = df[df['Amount'] != '']
    df['Amount'] = (
        df['Amount']
        .str.replace('$', '', regex=False)
        .str.replace('.', '', regex=False)
        .str.replace(',', '.', regex=False)
        .astype(float)
    )

    # Convert 'Date' column
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])

    # Add Year and Month columns
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month

    return df


def get_operations():
    """
    Reads the operations from the operations.json file.
    """
    # Get the absolute path to the directory of the current script
    dir_path = os.path.dirname(os.path.realpath(__file__))
    # Construct the full path to the operations.json file
    json_path = os.path.join(dir_path, 'operations.json')

    try:
        with open(json_path, 'r') as f:
            operations = json.load(f)
        return operations
    except FileNotFoundError:
        # Handle case where file doesn't exist
        return {"error": "operations.json not found"}
    except json.JSONDecodeError:
        # Handle case where JSON is invalid
        return {"error": "Invalid JSON format in operations.json"}

def analize_operation_prompt(operations, message_text):
    # Usar OpenAI para responder la pregunta basada en los datos
    prompt = f"""
    Eres un asistente financiero. Basándote en la siguiente lista de operaciones disponibles:
    {operations}
    
    Y el siguiente mensaje del cliente:
    '{message_text}'
    
    Interpreta cuál de la lista de operaciones pide el cliente. Interpreta correctamente el mes si esta en español o ingles y obten el numero del mes. Devuelve únicamente un JSON con la clave 'operation' y, si aplica, la clave 'params' con sus valores. Por ejemplo:
    {{"operation": "expenses_by_month", "params": {{"month": "september"}}}}
    O si no tiene parámetros:
    {{"operation": "incomes_expenses_by_year"}}
    """
    return prompt

def incomes_expenses_by_year():
    """Calculates incomes and expenses by year."""
    df = _get_prepared_data()
    if df.empty:
        return {"error": "No data available"}

    result = df.groupby(['Year', 'Income/expensive'])['Amount'].sum().unstack(fill_value=0)
    return result.to_dict('index')


def expenses_by_month(month):
    """Calculates expenses by month."""
    df = _get_prepared_data()
    if df.empty:
        return {"error": "No data available"}

    if not month:
        return {"error": "Month not provided"}

    month_number = _get_month_number(month)
    if not month_number:
        return {"error": f"Invalid month provided: {month}"}

    df_filtered = df[(df['Income/expensive'] == 'expensive') & (df['Month'] == month_number)]
    result = df_filtered.groupby('Year')['Amount'].sum()
    return result.to_dict()


def incomes_by_month(month):
    """Calculates incomes by month."""
    df = _get_prepared_data()
    if df.empty:
        return {"error": "No data available"}

    if not month:
        return {"error": "Month not provided"}

    month_number = _get_month_number(month)
    if not month_number:
        return {"error": f"Invalid month provided: {month}"}

    df_filtered = df[(df['Income/expensive'] == 'income') & (df['Month'] == month_number)]
    result = df_filtered.groupby('Year')['Amount'].sum()
    return result.to_dict()


def expenses_by_category_by_year(category):
    """Calculates expenses by category by year."""
    df = _get_prepared_data()
    if df.empty:
        return {"error": "No data available"}

    if not category:
        return {"error": "Category not provided"}

    df_filtered = df[(df['Income/expensive'] == 'expensive') & (df['Category'].str.lower() == category.lower())]
    result = df_filtered.groupby('Year')['Amount'].sum()
    return result.to_dict()


def incomes_by_category_by_year(category):
    """Calculates incomes by category by year."""
    df = _get_prepared_data()
    if df.empty:
        return {"error": "No data available"}

    if not category:
        return {"error": "Category not provided"}

    df_filtered = df[(df['Income/expensive'] == 'income') & (df['Category'].str.lower() == category.lower())]
    result = df_filtered.groupby('Year')['Amount'].sum()
    return result.to_dict()


def _convert_datetime_to_str(obj):
    """Recursively convert datetime objects to strings in a dictionary."""
    from datetime import datetime, date
    
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: _convert_datetime_to_str(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_convert_datetime_to_str(item) for item in obj]
    return obj

def expenses_by_category_by_month(category, month):
    """Calculates expenses by category by month.
    
    Args:
        category (str): The category to filter by. Can be None to get all categories.
        month (str or int): The month to filter by (can be name or number).
        
    Returns:
        dict: A dictionary with the expenses data or an error message.
    """
    try:
        month_number = _get_month_number(month)
        if not month_number:
            return {"error": f"Invalid month provided: {month}", "status": "error"}
        
        # Use the csv_client function which handles the data loading and processing
        result = csv_client.get_expenses_by_category_and_month(
            category=category if category != "category" else None,
            month=month_number
        )
        
        # Convert any datetime objects to strings for JSON serialization
        result = _convert_datetime_to_str(result)
        
        # If we got an empty result, return a helpful message
        if not result or (isinstance(result, dict) and not result.get('categories') and not result.get('total')):
            month_name = next((k for k, v in MONTH_MAP.items() if v == month_number), str(month_number))
            month_name = month_name.capitalize()
            if category and category != "category":
                return {
                    "message": f"No se encontraron gastos para la categoría '{category}' en {month_name}.",
                    "status": "no_data"
                }
            else:
                return {
                    "message": f"No se encontraron gastos registrados para {month_name}.",
                    "status": "no_data"
                }
        
        return result
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return {
            "error": f"Error al procesar la solicitud: {str(e)}\n\n{error_details}",
            "status": "error"
        }

def movements_by_category_and_month(category, month):
    """Calculates movements by category and month."""
    df = _get_prepared_data()
    if df.empty:
        return {"error": "No data available"}

    if not category or not month:
        return {"error": "Category or month not provided"}

    month_number = _get_month_number(month)
    if not month_number:
        return {"error": f"Invalid month provided: {month}"}


    df_filtered = df[(
        (df['Category'].str.lower() == category.lower()) &
        (df['Month'] == month_number)
    )]
    
    print("data filtered", df_filtered)
    result = df_filtered
    return result.to_dict('records')


def _get_month_number(month):
    try:
        return int(month)
    except ValueError:
        return MONTH_MAP.get(month.lower())


operation_functions = {
    "incomes_expenses_by_year": incomes_expenses_by_year,
    "expenses_by_month": expenses_by_month,
    "incomes_by_month": incomes_by_month,
    "expenses_by_category_by_year": expenses_by_category_by_year,
    "incomes_by_category_by_year": incomes_by_category_by_year,
    "expenses_by_category_by_month": expenses_by_category_by_month,
    "movements_by_category_and_month": movements_by_category_and_month,
}