#!/usr/bin/env python3
"""
CLI Calculator
Author: Chiaki
"""

import sys
import math
import re
import os
from datetime import datetime


def tokenize(expression):
    """Convert a string expression into tokens"""

    expression = expression.replace(" ", "")

    pattern = r'(\d*\.\d+|\d+|[-+*/()^%]|sin|cos|tan|sqrt|log|ln|abs|pi|e)'
    tokens = re.findall(pattern, expression)
    return tokens


def apply_operator(operators, values):
    """Apply the top operator to the top two values"""
    if not operators:
        return
    
    operator = operators.pop()
    
    if operator == '(':  
        return
    
    if operator in ('sin', 'cos', 'tan', 'sqrt', 'log', 'ln', 'abs'):
        if not values:
            raise ValueError(f"Not enough operands for {operator}")
        
        value = values.pop()
        
        if operator == 'sin':
            values.append(math.sin(value))
        elif operator == 'cos':
            values.append(math.cos(value))
        elif operator == 'tan':
            values.append(math.tan(value))
        elif operator == 'sqrt':
            if value < 0:
                raise ValueError("Cannot take square root of negative number")
            values.append(math.sqrt(value))
        elif operator == 'log':
            if value <= 0:
                raise ValueError("Cannot take log of non-positive number")
            values.append(math.log10(value))
        elif operator == 'ln':
            if value <= 0:
                raise ValueError("Cannot take natural log of non-positive number")
            values.append(math.log(value))
        elif operator == 'abs':
            values.append(abs(value))
        return
    
    if operator == 'pi':
        values.append(math.pi)
        return
    elif operator == 'e':
        values.append(math.e)
        return

    if len(values) < 2:
        raise ValueError("Not enough operands for operator: " + operator)
    
    right = values.pop()
    left = values.pop()
    
    if operator == '+':
        values.append(left + right)
    elif operator == '-':
        values.append(left - right)
    elif operator == '*':
        values.append(left * right)
    elif operator == '/':
        if right == 0:
            raise ValueError("Division by zero")
        values.append(left / right)
    elif operator == '^':
        values.append(left ** right)
    elif operator == '%':
        values.append(left % right)


def evaluate(expression):
    """Evaluate a mathematical expression using the Shunting Yard algorithm"""
    expression = expression.lower()
    tokens = tokenize(expression)
    
    precedence = {'+': 1, '-': 1, '*': 2, '/': 2, '^': 3, '%': 2}
    
    values = []
    operators = []
    
    i = 0
    while i < len(tokens):
        token = tokens[i]
        
        if re.match(r'^(\d*\.\d+|\d+)$', token):
            values.append(float(token))
        
        elif token in ('sin', 'cos', 'tan', 'sqrt', 'log', 'ln', 'abs', 'pi', 'e'):
            operators.append(token)
        
        elif token == '(':
            operators.append(token)
        
        elif token == ')':
            while operators and operators[-1] != '(':
                apply_operator(operators, values)
            
            if operators and operators[-1] == '(':
                operators.pop() 
                if operators and operators[-1] in ('sin', 'cos', 'tan', 'sqrt', 'log', 'ln', 'abs'):
                    apply_operator(operators, values)
            else:
                raise ValueError("Mismatched parentheses")
        
        # If token is an operator
        elif token in '+-*/^%':
            while (operators and operators[-1] != '(' and
                   operators[-1] in precedence and
                   precedence.get(operators[-1], 0) >= precedence.get(token, 0)):
                apply_operator(operators, values)
            
            operators.append(token)
        
        else:
            raise ValueError(f"Unknown token: {token}")
        
        i += 1
    
    # Apply remaining operators
    while operators:
        apply_operator(operators, values)
    
    if len(values) != 1:
        raise ValueError("Invalid expression")
    
    return values[0]


def save_history(calculation, result):
    """Save calculation history to a file"""
    history_dir = os.path.expanduser("~/.calc_history")
    
    # Create directory if it doesn't exist
    if not os.path.exists(history_dir):
        try:
            os.makedirs(history_dir)
        except OSError:
            print("Warning: Could not create history directory")
            return
    
    history_file = os.path.join(history_dir, "history.txt")
    
    try:
        with open(history_file, "a") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{timestamp} | {calculation} = {result}\n")
    except Exception as e:
        print(f"Warning: Could not save to history file: {e}")


def load_history(limit=10):
    """Load calculation history from file"""
    history_file = os.path.expanduser("~/.calc_history/history.txt")
    
    if not os.path.exists(history_file):
        return []
    
    try:
        with open(history_file, "r") as f:
            lines = f.readlines()
            return lines[-limit:]
    except Exception as e:
        print(f"Warning: Could not load history file: {e}")
        return []


def convert_units(value, from_unit, to_unit):
    """Convert between different units of measurement"""
    # Temperature conversions
    temperature = {
        "c": {"f": lambda x: x * 9/5 + 32, "k": lambda x: x + 273.15},
        "f": {"c": lambda x: (x - 32) * 5/9, "k": lambda x: (x - 32) * 5/9 + 273.15},
        "k": {"c": lambda x: x - 273.15, "f": lambda x: (x - 273.15) * 9/5 + 32}
    }
    
    # Length conversions (meters as base unit)
    length = {
        "m": {"cm": lambda x: x * 100, "km": lambda x: x / 1000, "in": lambda x: x * 39.3701, "ft": lambda x: x * 3.28084, "mi": lambda x: x / 1609.344},
        "cm": {"m": lambda x: x / 100, "km": lambda x: x / 100000, "in": lambda x: x / 2.54, "ft": lambda x: x / 30.48, "mi": lambda x: x / 160934.4},
        "km": {"m": lambda x: x * 1000, "cm": lambda x: x * 100000, "in": lambda x: x * 39370.1, "ft": lambda x: x * 3280.84, "mi": lambda x: x / 1.60934},
        "in": {"m": lambda x: x / 39.3701, "cm": lambda x: x * 2.54, "km": lambda x: x / 39370.1, "ft": lambda x: x / 12, "mi": lambda x: x / 63360},
        "ft": {"m": lambda x: x / 3.28084, "cm": lambda x: x * 30.48, "km": lambda x: x / 3280.84, "in": lambda x: x * 12, "mi": lambda x: x / 5280},
        "mi": {"m": lambda x: x * 1609.344, "cm": lambda x: x * 160934.4, "km": lambda x: x * 1.60934, "in": lambda x: x * 63360, "ft": lambda x: x * 5280}
    }
    
    # Weight conversions (kg as base unit)
    weight = {
        "kg": {"g": lambda x: x * 1000, "lb": lambda x: x * 2.20462, "oz": lambda x: x * 35.274},
        "g": {"kg": lambda x: x / 1000, "lb": lambda x: x / 453.592, "oz": lambda x: x / 28.3495},
        "lb": {"kg": lambda x: x / 2.20462, "g": lambda x: x * 453.592, "oz": lambda x: x * 16},
        "oz": {"kg": lambda x: x / 35.274, "g": lambda x: x * 28.3495, "lb": lambda x: x / 16}
    }
    
    # Identify unit type
    unit_type = None
    for unit_dict in [temperature, length, weight]:
        if from_unit in unit_dict and to_unit in unit_dict[from_unit]:
            return unit_dict[from_unit][to_unit](value)
    
    raise ValueError(f"Cannot convert from {from_unit} to {to_unit}")


def display_help():
    """Display help information"""
    print("\CLI Calculator by Chiaki")
    print("Commands:")
    print("  exit, quit - Exit the calculator")
    print("  help       - Display this help message")
    print("  history    - Show calculation history")
    print("  clear      - Clear the screen")
    print("  ans        - Use the previous result")
    print("  convert    - Convert units (e.g., convert 32 f to c)")
    
    print("\nBasic Operations:")
    print("  + Addition        Example: 5 + 3")
    print("  - Subtraction     Example: 7 - 2")
    print("  * Multiplication  Example: 4 * 6")
    print("  / Division        Example: 9 / 3")
    print("  ^ Exponentiation  Example: 2 ^ 3")
    print("  % Modulo          Example: 10 % 3")
    print("  () Parentheses    Example: (2 + 3) * 4")
    
    print("\nFunctions:")
    print("  sin(x)  - Sine of x (in radians)")
    print("  cos(x)  - Cosine of x (in radians)")
    print("  tan(x)  - Tangent of x (in radians)")
    print("  sqrt(x) - Square root of x")
    print("  log(x)  - Base-10 logarithm of x")
    print("  ln(x)   - Natural logarithm of x")
    print("  abs(x)  - Absolute value of x")
    
    print("\nConstants:")
    print("  pi - The value of π (3.14159...)")
    print("  e  - The value of e (2.71828...)\n")


def main():
    """Main calculator loop"""
    print("CLI Calculator by Chiaki (Type 'help' for commands, 'exit' to quit)")
    
    last_result = 0
    
    while True:
        try:
            user_input = input("calc> ").strip()
            
            if user_input.lower() in ('exit', 'quit'):
                print("Goodbye!")
                break
            
            elif user_input.lower() == 'help':
                display_help()
            
            elif user_input.lower() == 'history':
                history = load_history()
                if history:
                    print("\nCalculation History:")
                    for entry in history:
                        print(entry.strip())
                    print()
                else:
                    print("No history found.")
            
            elif user_input.lower() == 'clear':
                os.system('cls' if os.name == 'nt' else 'clear')
                print("CLI Calculator by Chiaki (Type 'help' for commands, 'exit' to quit)")
            
            elif user_input.lower().startswith('convert '):
                parts = user_input.lower().split()
                if len(parts) == 5 and parts[3] == 'to':
                    try:
                        value = float(parts[1])
                        from_unit = parts[2]
                        to_unit = parts[4]
                        result = convert_units(value, from_unit, to_unit)
                        print(f"{value} {from_unit} = {result} {to_unit}")
                        last_result = result
                        save_history(f"convert {value} {from_unit} to {to_unit}", result)
                    except ValueError as e:
                        print(f"Error: {e}")
                else:
                    print("Usage: convert VALUE FROM_UNIT to TO_UNIT")
                    print("Example: convert 32 f to c")
            
            elif user_input:
                expression = user_input.replace('ans', str(last_result))
                result = evaluate(expression)
                
                if result == int(result):
                    print(int(result))
                    last_result = int(result)
                else:
                    print(result)
                    last_result = result
                
                # Save to history
                save_history(user_input, last_result)
        
        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()