import sqlite3
import pandas as pd
import streamlit as st

from datetime import datetime


def obtener_stock_producto(id_producto):
    """Obtiene el stock del producto en cada tienda."""
    with sqlite3.connect('BD_Pfinal.db') as conexion:
        query = """
        SELECT
            Id_productos,
            Nombre_producto,
            StockA AS Tienda_Sur,
            StockB AS Tienda_Norte,
            StockC AS Tienda_Central,
            StockD AS Tienda_Panamericana
        FROM
            Productos
        WHERE
            Id_productos = ?;
        """
        resultado = pd.read_sql_query(query, conexion, params=(id_producto,))
    
    return resultado

def analizar_stock(tiendas):
    """Analiza el stock de cada tienda y realiza ajustes."""
    # ... (implementa la lógica de análisis de stock aquí)
    return tiendas

def trasladar_stock(stock_tiendas):
    """Traslada la mitad del stock de la tienda que menos vendió a la tienda que más vendió."""
    # Implementa la lógica de traslado de stock aquí
    # ...
    return stock_tiendas  # Retorna el DataFrame actualizado

def mostrar_nuevo_stock(stock_tiendas):
    """Muestra el nuevo stock de manera ordenada."""
    mensaje = ""
    for index, row in stock_tiendas.iterrows():
        mensaje += f"\n\nID: {row['Id_productos']}\n"
        mensaje += f"Nombre del producto: {row['Nombre_producto']}\n"
        mensaje += f"Nuevo Stock en Tienda Sur: {row['Tienda_Sur']}\n"
        mensaje += f"Nuevo Stock en Tienda Norte: {row['Tienda_Norte']}\n"
        mensaje += f"Nuevo Stock en Tienda Central: {row['Tienda_Central']}\n"
        mensaje += f"Nuevo Stock en Tienda Panamericana: {row['Tienda_Panamericana']}\n"
    return mensaje

def formatear_mensaje(stock_tiendas):
    """Formatea el DataFrame de stock para mostrarlo de manera ordenada."""
    mensaje = ""
    for index, row in stock_tiendas.iterrows():
        mensaje += f"\n\nID: {row['Id_productos']}\n"
        mensaje += f"Nombre del producto: {row['Nombre_producto']}\n"
        mensaje += f"Tienda Sur: {row['Tienda_Sur']}\n"
        mensaje += f"Tienda Norte: {row['Tienda_Norte']}\n"
        mensaje += f"Tienda Central: {row['Tienda_Central']}\n"
        mensaje += f"Tienda Panamericana: {row['Tienda_Panamericana']}\n"
    return mensaje

class MenuInteractivoStreamlit:
    def __init__(self):
        st.title("Administración de inventarios entre tiendas")

        # Campo de entrada para el código del producto
        id_producto_usuario = st.text_input("Ingrese el código del producto:")

        # Botón de búsqueda
        if st.button("Buscar"):
            try:
                stock_tiendas = obtener_stock_producto(id_producto_usuario)

                if stock_tiendas.empty:
                    st.info("El producto no existe.")
                else:
                    mensaje_formateado = formatear_mensaje(stock_tiendas)
                    st.info(mensaje_formateado)

                    # Preguntar al usuario si desea trasladar el stock
                    if st.button("¿Desea trasladar la mitad del stock de la tienda que menos vendió a la tienda que más vendió?"):
                        stock_modificado = trasladar_stock(stock_tiendas)
                        nuevo_stock_mensaje = mostrar_nuevo_stock(stock_modificado)
                        st.success("Nuevo stock después del análisis y ajuste:" + nuevo_stock_mensaje)

            except Exception as e:
                st.error(f"Ocurrió un error: {str(e)}")

class RegistroVentasStreamlit:
    def __init__(self):
        st.title("Registro de Ventas")

        self.id_producto_usuario = st.text_input("Ingrese el ID del producto:")

        if st.button("Registrar Venta"):
            self.registrar_venta()

    def obtener_info_producto(self, id_producto):
        """Obtiene la información del producto (precio y stock)"""
        with sqlite3.connect('BD_Pfinal.db') as conexion:
            query = """
            SELECT
                Id_productos,
                Nombre_producto,
                Precio,
                StockA AS Tienda_Sur,
                StockB AS Tienda_Norte,
                StockC AS Tienda_Central,
                StockD AS Tienda_Panamericana
            FROM
                Productos
            WHERE
                Id_productos = ?;
            """
            resultado = pd.read_sql_query(query, conexion, params=(id_producto,))

        if resultado.empty:
            st.error("El producto no existe.")
            return None
        else:
            st.info(resultado[['Id_productos', 'Nombre_producto', 'Precio']].to_string(index=False))
            return resultado.iloc[0]

    def obtener_nuevo_id_venta(self):
        """Genera un nuevo Id_venta único y actualiza el valor en la base de datos."""
        with sqlite3.connect('BD_Pfinal.db') as conexion:
            cursor = conexion.cursor()
            cursor.execute("SELECT valor FROM ContadorIdVenta;")
            valor_actual = cursor.fetchone()[0]

            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            nuevo_valor = valor_actual + 1
            cursor.execute("UPDATE ContadorIdVenta SET valor = ?, Fecha = ?;", (nuevo_valor, fecha_actual))

            conexion.commit()

            return nuevo_valor, fecha_actual

    def registrar_venta(self):
        info_producto = self.obtener_info_producto(self.id_producto_usuario)

        if info_producto is not None:
            nombre_producto = info_producto['Nombre_producto']
            precio_producto = info_producto['Precio']

           
            cantidad_venta = st.number_input(f"Ingrese la cantidad de '{nombre_producto}' que desea vender:", min_value=1)

            monto_total = precio_producto * cantidad_venta

            st.info(f"Precio unitario: {precio_producto}\nStock disponible: {info_producto['Tienda_Sur']}\nMonto total de la venta: {monto_total}")

            if cantidad_venta > info_producto['Tienda_Sur']:
                st.error("No hay suficiente stock para completar la venta.")
                return

            info_producto['Tienda_Sur'] -= cantidad_venta

            nuevo_id_venta, fecha_venta = self.obtener_nuevo_id_venta()

            with sqlite3.connect('BD_Pfinal.db') as conexion:
                cursor = conexion.cursor()
                cursor.execute("""
                    UPDATE Productos
                    SET StockA = ?
                    WHERE Id_productos = ?;
                """, (info_producto['Tienda_Sur'], self.id_producto_usuario))

                conexion.commit()

            st.success(f"Venta registrada\nId_venta: {nuevo_id_venta}\nFecha de registro: {fecha_venta}\nInventario actualizado.")

if __name__ == '__main__':
    menu_interactivo = MenuInteractivoStreamlit()
    registro_ventas = RegistroVentasStreamlit()
