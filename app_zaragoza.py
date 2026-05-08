import tkinter as tk
from tkinter import messagebox

def calcular():
    try:
        # Obtenemos los datos de la interfaz
        ancho = float(entry_ancho.get())
        alto = float(entry_alto.get())
        precio_tira = float(entry_precio_tira.get())
        
        # LÓGICA DE NEGOCIO (Basada en la libreta de tu papá)
        # 1. Calculamos el costo por metro (Tiras de 6m)
        precio_por_metro = precio_tira / 6
        
        # 2. Metros lineales necesarios para el marco (Perímetro simple)
        # Sumamos un 10% por el desperdicio al cortar
        metros_totales = ((ancho * 2) + (alto * 2)) * 1.10
        
        costo_final = metros_totales * precio_por_metro
        
        # Mostramos el resultado de forma clara
        label_resultado.config(text=f"Costo Estimado Aluminio: ${costo_final:.2f}", fg="green")
        
    except ValueError:
        messagebox.showerror("Error", "Por favor, ingresa números válidos (usa punto para decimales)")

# Configuración de la Ventana Principal
ventana = tk.Tk()
ventana.title("VIDRIOS Y ALUMINIOS ZARAGOZA - Cotizador")
ventana.geometry("400x450")
ventana.config(padx=20, pady=20)

# Título visual
tk.Label(ventana, text="Cotizador de Ventanas", font=("Arial", 16, "bold")).pack(pady=10)

# Campos de entrada
tk.Label(ventana, text="Ancho de la ventana (metros):").pack()
entry_ancho = tk.Entry(ventana)
entry_ancho.pack(pady=5)

tk.Label(ventana, text="Alto de la ventana (metros):").pack()
entry_alto = tk.Entry(ventana)
entry_alto.pack(pady=5)

tk.Label(ventana, text="Precio de la TIRA completa ($):").pack()
entry_precio_tira = tk.Entry(ventana)
entry_precio_tira.pack(pady=5)

# Botón de acción
btn_calcular = tk.Button(ventana, text="CALCULAR COSTO", command=calcular, bg="#0078D7", fg="white", font=("Arial", 10, "bold"))
btn_calcular.pack(pady=20)

# Etiqueta para el resultado
label_resultado = tk.Label(ventana, text="Costo: $0.00", font=("Arial", 14))
label_resultado.pack()

ventana.mainloop()