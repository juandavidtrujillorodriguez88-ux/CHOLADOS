from flask import Flask, jsonify
from flask import flash, get_flashed_messages  # se importan para poder enviar mensajes a sweetAlert2
from flask import render_template, session
from flask import url_for
from flask import request                 # recepciona la informacion "DEL FORMULARIO"
from flask import redirect                # redirecciona "MUESTRA LA INFORMACION PARA LAS TABLAS"
import mysql.connector                    # Se importa libreria para conexion a base de datos
from datetime import datetime
from flask import send_from_directory
from flask import abort
import os
 
 
app = Flask(__name__)  # se crea la aplicacion
app.secret_key = "ingRamirez"
 
# Configuración de la conexión MySQL
config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'port': 3306,
    'database': 'cholados_tropical'
}
 
 
@app.route('/')
def inicio():
    return render_template('sitio/index.html')
 
 
@app.route('/nosotros')
def nosotros():
    return render_template('sitio/nosotros.html')
 
 
@app.route('/admin')
def admin_index():
 
    """ Preguntamos si el usuario esta logeado o
        tiene una session activa """
    if not 'login' in session:
        return redirect('/admin/loginAdmin')
 
    return render_template('admin/index.html')
 
 
@app.route('/admin/loginAdmin')
def admin_login():
    return render_template('admin/loginAdmin.html')
 
 
""" Ruta para login, solo se valida por codigo, NO por
    base de datos """
@app.route('/admin/loginAdmin', methods=['POST'])
def admin_login_post():
 
    usuario = request.form['usuario']
    password = request.form['password']
 
    if usuario == "Juan" and password == "040506":
        session["login"] = True
        session["user"] = "Juan"
        return redirect('/admin')
    else:
        print("datos incorrectos")
 
    return render_template('admin/loginAdmin.html', mensaje="Datos incorrectos .|.")
 
 
@app.route('/admin/cerrar')
def admin_cerrar_session():
    session.clear()
    return redirect('/admin/loginAdmin')
 
 
# ==========================================================
#  CRUD de Clientes -> tabla `cliente` de la base `cholados`
#  columnas reales (segun phpMyAdmin):
#  id_cliente, nombre, apellido, direccion, correo
# ==========================================================
 
@app.route('/clienteAdmin')
def clienteAdmin():
 
    """ Preguntamos si el usuario esta logeado o
        tiene una session activa """
    if not 'login' in session:
        return redirect('/admin/loginAdmin')
 
    """ Esta funcion me sirve para mostrar todos los clientes
        de mi base de datos """
    conn = mysql.connector.connect(**config)  # Crear una conexión al servidor MySQL
    cursor = conn.cursor()                    # Crear un cursor para ejecutar comandos SQL
    try:
        cursor.execute('SELECT * FROM cliente')   # Ejecutar una consulta SQL
        listaClientes = cursor.fetchall()         # Obtener los resultados de la consulta
    finally:
        # Cerrar el cursor y la conexión (siempre, incluso si algo falla arriba)
        cursor.close()
        conn.close()
 
    return render_template('admin/clienteAdmin.html', listaClientes=listaClientes)
 
 
@app.route('/admin/clienteAdmin/guardar', methods=['POST'])  # Recibe los datos enviados por POST
def admin_cliente_guardar():
 
    """ Preguntamos si el usuario esta logeado o
        tiene una session activa """
    if not 'login' in session:
        return redirect('/admin/loginAdmin')
 
    """ Esta funcion me sirve para ingresar los datos enviados
        mediante un formulario a mi base de datos. """
    nombre    = request.form['nombre']
    apellido  = request.form['apellido']
    direccion = request.form['direccion']
    correo    = request.form['correo']
 
    conn = mysql.connector.connect(**config)  # Crear una conexión al servidor MySQL
    datos = (nombre, apellido, direccion, correo)
    sql = "INSERT INTO `cliente` (`nombre`, `apellido`, `direccion`, `correo`) VALUES (%s,%s,%s,%s);"
    cursor = conn.cursor()   # Crear un cursor para ejecutar comandos SQL
    try:
        cursor.execute(sql, datos)
        conn.commit()  # confirma la insercion SQL.... sin este paso no se ejecuta nada
    finally:
        # Cerrar el cursor y la conexión (siempre, incluso si algo falla arriba)
        cursor.close()
        conn.close()
 
    """ se envia un mensaje de confirmacion a la ruta clienteAdmin
        para que dicha ruta muestre la vista y el mensaje """
    flash("Cliente Ingresado Correctamente")
    return redirect(url_for('clienteAdmin'))
 
 
@app.route('/admin/clienteAdmin/actualizar', methods=['POST'])  # Recibe los datos enviados por POST
def admin_cliente_actualizar():
 
    """ Preguntamos si el usuario esta logeado o
        tiene una session activa """
    if not 'login' in session:
        return redirect('/admin/loginAdmin')
 
    """ Esta funcion me sirve para actualizar los datos de un cliente
        ya existente, enviados mediante un formulario, en mi base de datos. """
    id_cliente = request.form['id_cliente']
    nombre     = request.form['nombre']
    apellido   = request.form['apellido']
    direccion  = request.form['direccion']
    correo     = request.form['correo']
 
    conn = mysql.connector.connect(**config)  # Crear una conexión al servidor MySQL
    datos = (nombre, apellido, direccion, correo, id_cliente)
    sql = "UPDATE `cliente` SET `nombre` = %s, `apellido` = %s, `direccion` = %s, `correo` = %s WHERE `id_cliente` = %s;"
    cursor = conn.cursor()
    try:
        cursor.execute(sql, datos)
        conn.commit()  # confirma la actualizacion SQL.... sin este paso no se ejecuta nada
    finally:
        # Cerrar el cursor y la conexión (siempre, incluso si algo falla arriba)
        cursor.close()
        conn.close()
 
    """ se envia un mensaje de confirmacion a la ruta clienteAdmin
        para que dicha ruta muestre la vista y el mensaje """
    flash("Cliente Actualizado Correctamente")
    return redirect(url_for('clienteAdmin'))
 
 
@app.route('/admin/clienteAdmin/borrar', methods=['POST'])
def admin_cliente_borrar():
 
    """ Preguntamos si el usuario esta logeado o
        tiene una session activa """
    if not 'login' in session:
        return redirect('/admin/loginAdmin')
 
    id_cliente = request.form['id_cliente']
 
    conn = mysql.connector.connect(**config)  # Crear una conexión al servidor MySQL
    sql = "DELETE FROM cliente WHERE id_cliente = %s;"
    cursor = conn.cursor()
    try:
        cursor.execute(sql, [id_cliente])
        conn.commit()  # confirma la eliminacion SQL.... sin este paso no se ejecuta nada
    finally:
        # Cerrar el cursor y la conexión (siempre, incluso si algo falla arriba)
        cursor.close()
        conn.close()
 
    flash("Cliente Eliminado")
    return redirect(url_for('clienteAdmin'))
 
 
@app.route('/vendedorAdmin')
def vendedorAdmin():
 
    if not 'login' in session:
        return redirect('/admin/loginAdmin')
 
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM vendedor')
        listaVendedores = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
 
    return render_template('admin/vendedorAdmin.html', listaVendedores=listaVendedores)
 
 
@app.route('/admin/vendedorAdmin/guardar', methods=['POST'])
def admin_vendedor_guardar():
 
    if not 'login' in session:
        return redirect('/admin/loginAdmin')
 
    nombre    = request.form['nombre']
    telefono  = request.form['telefono']
    direccion = request.form['direccion']
    correo    = request.form['correo']
 
    conn = mysql.connector.connect(**config)
    datos = (nombre, telefono, direccion, correo)
    sql = "INSERT INTO `vendedor` (`nombre`, `telefono`, `direccion`, `correo`) VALUES (%s,%s,%s,%s);"
    cursor = conn.cursor()
    try:
        cursor.execute(sql, datos)
        conn.commit()
    finally:
        cursor.close()
        conn.close()
 
    flash("Vendedor Ingresado Correctamente")
    return redirect(url_for('vendedorAdmin'))
 
 
@app.route('/admin/vendedorAdmin/actualizar', methods=['POST'])
def admin_vendedor_actualizar():
 
    if not 'login' in session:
        return redirect('/admin/loginAdmin')
 
    id_vendedor = request.form['id_vendedor']
    nombre      = request.form['nombre']
    telefono    = request.form['telefono']
    direccion   = request.form['direccion']
    correo      = request.form['correo']
 
    conn = mysql.connector.connect(**config)
    datos = (nombre, telefono, direccion, correo, id_vendedor)
    sql = "UPDATE `vendedor` SET `nombre` = %s, `telefono` = %s, `direccion` = %s, `correo` = %s WHERE `id_vendedor` = %s;"
    cursor = conn.cursor()
    try:
        cursor.execute(sql, datos)
        conn.commit()
    finally:
        cursor.close()
        conn.close()
 
    flash("Vendedor Actualizado Correctamente")
    return redirect(url_for('vendedorAdmin'))
 
 
@app.route('/admin/vendedorAdmin/borrar', methods=['POST'])
def admin_vendedor_borrar():
 
    if not 'login' in session:
        return redirect('/admin/loginAdmin')
 
    id_vendedor = request.form['id_vendedor']
 
    conn = mysql.connector.connect(**config)
    sql = "DELETE FROM vendedor WHERE id_vendedor = %s;"
    cursor = conn.cursor()
    try:
        cursor.execute(sql, [id_vendedor])
        conn.commit()
    finally:
        cursor.close()
        conn.close()
 
    flash("Vendedor Eliminado Correctamente")
    return redirect(url_for('vendedorAdmin'))
 
 
@app.route('/tipoproductoAdmin')
def tipoproductoAdmin():
 
    if not 'login' in session:
        return redirect('/admin/loginAdmin')
 
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM tipoproducto')
        listaTiposProducto = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
 
    return render_template('admin/tipoproductoAdmin.html', listaTiposProducto=listaTiposProducto)
 
 
@app.route('/admin/tipoproductoAdmin/guardar', methods=['POST'])
def admin_tipoproducto_guardar():
 
    if not 'login' in session:
        return redirect('/admin/loginAdmin')
 
    nombre = request.form['nombre']
 
    conn = mysql.connector.connect(**config)
    datos = (nombre,)
    sql = "INSERT INTO `tipoproducto` (`nombre`) VALUES (%s);"
    cursor = conn.cursor()
    try:
        cursor.execute(sql, datos)
        conn.commit()
    finally:
        cursor.close()
        conn.close()
 
    flash("Tipo de Producto Ingresado Correctamente")
    return redirect(url_for('tipoproductoAdmin'))
 
 
@app.route('/admin/tipoproductoAdmin/actualizar', methods=['POST'])
def admin_tipoproducto_actualizar():
 
    if not 'login' in session:
        return redirect('/admin/loginAdmin')
 
    id_tipoproducto = request.form['id_tipoproducto']
    nombre          = request.form['nombre']
 
    conn = mysql.connector.connect(**config)
    datos = (nombre, id_tipoproducto)
    sql = "UPDATE `tipoproducto` SET `nombre` = %s WHERE `id_tipoproducto` = %s;"
    cursor = conn.cursor()
    try:
        cursor.execute(sql, datos)
        conn.commit()
    finally:
        cursor.close()
        conn.close()
 
    flash("Tipo de Producto Actualizado Correctamente")
    return redirect(url_for('tipoproductoAdmin'))
 
 
@app.route('/admin/tipoproductoAdmin/borrar', methods=['POST'])
def admin_tipoproducto_borrar():
 
    if not 'login' in session:
        return redirect('/admin/loginAdmin')
 
    id_tipoproducto = request.form['id_tipoproducto']
 
    conn = mysql.connector.connect(**config)
    sql = "DELETE FROM tipoproducto WHERE id_tipoproducto = %s;"
    cursor = conn.cursor()
    try:
        cursor.execute(sql, [id_tipoproducto])
        conn.commit()
    finally:
        cursor.close()
        conn.close()
 
    flash("Tipo de Producto Eliminado Correctamente")
    return redirect(url_for('tipoproductoAdmin'))
 
 
@app.route('/facturaAdmin')
def facturaAdmin():
 
    if not 'login' in session:
        return redirect('/admin/loginAdmin')
 
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM factura')
        listafacturas = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
 
    return render_template('admin/facturaAdmin.html', listafactura=listafacturas)
 
 
@app.route('/admin/facturaAdmin/guardar', methods=['POST'])
def admin_factura_guardar():
 
    if not 'login' in session:
        return redirect('/admin/loginAdmin')
 
    id_factura  = request.form['id_factura']
    fecha       = request.form['fecha']
    id_cliente  = request.form['id_cliente']
    id_vendedor = request.form['id_vendedor']
 
    conn = mysql.connector.connect(**config)
    datos = (id_factura, fecha, id_cliente, id_vendedor)
    sql = "INSERT INTO `factura` (`id_factura`, `fecha`, `id_cliente`, `id_vendedor`) VALUES (%s,%s,%s,%s);"
    cursor = conn.cursor()
    try:
        cursor.execute(sql, datos)
        conn.commit()
    finally:
        cursor.close()
        conn.close()
 
    flash("factura Ingresado Correctamente")
    return redirect(url_for('facturaAdmin'))
 
 
@app.route('/admin/facturaAdmin/actualizar', methods=['POST'])
def admin_factura_actualizar():
 
    if not 'login' in session:
        return redirect('/admin/loginAdmin')
 
    id_factura = request.form['id_factura']
    fecha       = request.form['fecha']
    id_cliente     = request.form['id_cliente']
    id_vendedor     = request.form['id_vendedor']
 
    conn = mysql.connector.connect(**config)
    datos = (id_factura, fecha, id_cliente, id_vendedor, id_factura)
    sql = "UPDATE `factura` SET `id_factura` = %s, `fecha` = %s, `id_cliente` = %s, `id_vendedor` = %s WHERE `id_factura` = %s;"
    cursor = conn.cursor()
    try:
        cursor.execute(sql, datos)
        conn.commit()
    finally:
        cursor.close()
        conn.close()
 
    flash("factura Actualizado Correctamente")
    return redirect(url_for('facturaAdmin'))
 
 
@app.route('/admin/facturaAdmin/borrar', methods=['POST'])
def admin_factura_borrar():
 
    if not 'login' in session:
        return redirect('/admin/loginAdmin')
 
    id_factura = request.form['id_factura']
 
    conn = mysql.connector.connect(**config)
    sql = "DELETE FROM factura WHERE id_factura = %s;"
    cursor = conn.cursor()
    try:
        cursor.execute(sql, [id_factura])
        conn.commit()
    finally:
        cursor.close()
        conn.close()
 
    flash("factura Eliminado Correctamente")
    return redirect(url_for('facturaAdmin'))


@app.route('/proveedorAdmin')
def proveedorAdmin():
 
    if not 'login' in session:
        return redirect('/admin/loginAdmin')
 
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM proveedor')
        listaProveedores = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
 
    return render_template('admin/proveedorAdmin.html', listaProveedores=listaProveedores)
 
 
@app.route('/admin/proveedorAdmin/guardar', methods=['POST'])
def admin_proveedor_guardar():
 
    if not 'login' in session:
        return redirect('/admin/loginAdmin')
 
    nombre    = request.form['nombre']
    telefono  = request.form['telefono']
    producto  = request.form['producto']
    correo    = request.form['correo']
    direccion = request.form['direccion']
 
    conn = mysql.connector.connect(**config)
    datos = (nombre, telefono, producto, correo, direccion)
    sql = "INSERT INTO `proveedor` (`nombre`, `telefono`, `producto`, `correo`, `direccion`) VALUES (%s,%s,%s,%s,%s);"
    cursor = conn.cursor()
    try:
        cursor.execute(sql, datos)
        conn.commit()
    finally:
        cursor.close()
        conn.close()
 
    flash("Proveedor Ingresado Correctamente")
    return redirect(url_for('proveedorAdmin'))
 
 
@app.route('/admin/proveedorAdmin/actualizar', methods=['POST'])
def admin_proveedor_actualizar():
 
    if not 'login' in session:
        return redirect('/admin/loginAdmin')
 
    id_proveedor = request.form['id_proveedor']
    nombre       = request.form['nombre']
    telefono     = request.form['telefono']
    producto     = request.form['producto']
    correo       = request.form['correo']
    direccion    = request.form['direccion']
 
    conn = mysql.connector.connect(**config)
    datos = (nombre, telefono, producto, correo, direccion, id_proveedor)
    sql = "UPDATE `proveedor` SET `nombre` = %s, `telefono` = %s, `producto` = %s, `correo` = %s, `direccion` = %s WHERE `id_proveedor` = %s;"
    cursor = conn.cursor()
    try:
        cursor.execute(sql, datos)
        conn.commit()
    finally:
        cursor.close()
        conn.close()
 
    flash("Proveedor Actualizado Correctamente")
    return redirect(url_for('proveedorAdmin'))
 
 
@app.route('/admin/proveedorAdmin/borrar', methods=['POST'])
def admin_proveedor_borrar():
 
    if not 'login' in session:
        return redirect('/admin/loginAdmin')
 
    id_proveedor = request.form['id_proveedor']
 
    conn = mysql.connector.connect(**config)
    sql = "DELETE FROM proveedor WHERE id_proveedor = %s;"
    cursor = conn.cursor()
    try:
        cursor.execute(sql, [id_proveedor])
        conn.commit()
    finally:
        cursor.close()
        conn.close()
 
    flash("Proveedor Eliminado Correctamente")
    return redirect(url_for('proveedorAdmin'))


@app.route('/productoAdmin')
def productoAdmin():
 
    if not 'login' in session:
        return redirect('/admin/loginAdmin')
 
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM producto')
        listaproductos = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
 
    return render_template('admin/productoAdmin.html', listaproducto=listaproductos)
 
 
@app.route('/admin/productoAdmin/guardar', methods=['POST'])
def admin_producto_guardar():
 
    if not 'login' in session:
        return redirect('/admin/loginAdmin')
 
    id_producto  = request.form['id_producto']
    nombre       = request.form['nombre']
    precio  = request.form['precio']
    tamaño = request.form['tamaño']
    id_tipoproducto = request.form['id_tipoproducto']
    id_proveedor = request.form['id_proveedor']
 
    conn = mysql.connector.connect(**config)
    datos = (id_producto, nombre, precio, tamaño, id_tipoproducto, id_proveedor)
    sql = "INSERT INTO `producto` (`id_producto`, `nombre`, `precio`, `tamaño`, `id_tipoproducto`, `id_proveedor`) VALUES (%s,%s,%s,%s,%s,%s);"
    cursor = conn.cursor()
    try:
        cursor.execute(sql, datos)
        conn.commit()
    finally:
        cursor.close()
        conn.close()
 
    flash("producto Ingresado Correctamente")
    return redirect(url_for('productoAdmin'))
 
 
@app.route('/admin/productoAdmin/actualizar', methods=['POST'])
def admin_producto_actualizar():
 
    if not 'login' in session:
        return redirect('/admin/loginAdmin')
 
    id_producto  = request.form['id_producto']
    nombre       = request.form['nombre']
    precio  = request.form['precio']
    tamaño = request.form['tamaño']
    id_tipoproducto = request.form['id_tipoproducto']
    id_proveedor = request.form['id_proveedor']
 
    conn = mysql.connector.connect(**config)
    datos = (id_producto, nombre, precio, tamaño, id_tipoproducto, id_proveedor, id_producto)
    sql = "UPDATE `producto` SET `id_producto` = %s, `nombre` = %s, `precio` = %s, `tamaño` = %s, `id_tipoproducto` = %s, `id_proveedor` = %s WHERE `id_producto` = %s;"
    cursor = conn.cursor()
    try:
        cursor.execute(sql, datos)
        conn.commit()
    finally:
        cursor.close()
        conn.close()
 
    flash("producto Actualizado Correctamente")
    return redirect(url_for('productoAdmin'))
 
 
@app.route('/admin/productoAdmin/borrar', methods=['POST'])
def admin_producto_borrar():
 
    if not 'login' in session:
        return redirect('/admin/loginAdmin')
 
    id_producto = request.form['id_producto']
 
    conn = mysql.connector.connect(**config)
    sql = "DELETE FROM producto WHERE id_producto = %s;"
    cursor = conn.cursor()
    try:
        cursor.execute(sql, [id_producto])
        conn.commit()
    finally:
        cursor.close()
        conn.close()
 
    flash("producto Eliminado Correctamente")
    return redirect(url_for('productoAdmin'))


@app.route('/detalle_ventaAdmin')
def detalle_ventaAdmin():
 
    if not 'login' in session:
        return redirect('/admin/loginAdmin')
 
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM detalle_venta')
        listadetalle_ventas = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
 
    return render_template('admin/detalle_ventaAdmin.html', listadetalle_venta=listadetalle_ventas)
 
 
@app.route('/admin/detalle_ventaAdmin/guardar', methods=['POST'])
def admin_detalle_venta_guardar():
 
    if not 'login' in session:
        return redirect('/admin/loginAdmin')
 
    id_detalle_venta     = request.form['id_detalle_venta']
    fecha                = request.form['fecha']
    cantidad             = request.form['cantidad']
    id_factura           = request.form['id_factura']
    id_producto          = request.form['id_producto']
 
    conn = mysql.connector.connect(**config)
    datos = (id_detalle_venta, fecha, cantidad, id_factura, id_producto)
    sql = "INSERT INTO `detalle_venta` (`id_detalle_venta`, `fecha`, `cantidad`, `id_factura`, `id_producto`) VALUES (%s,%s,%s,%s,%s);"
    cursor = conn.cursor()
    try:
        cursor.execute(sql, datos)
        conn.commit()
    finally:
        cursor.close()
        conn.close()
 
    flash("detalle_venta Ingresado Correctamente")
    return redirect(url_for('detalle_ventaAdmin'))
 
 
@app.route('/admin/detalle_ventaAdmin/actualizar', methods=['POST'])
def admin_detalle_venta_actualizar():
 
    if not 'login' in session:
        return redirect('/admin/loginAdmin')
 
    id_detalle_venta     = request.form['id_detalle_venta']
    fecha                = request.form['fecha']
    cantidad             = request.form['cantidad']
    id_factura           = request.form['id_factura']
    id_producto          = request.form['id_producto']
 
    conn = mysql.connector.connect(**config)
    datos = (id_detalle_venta, fecha, cantidad, id_factura, id_producto, id_detalle_venta)
    sql = "UPDATE `detalle_venta` SET `id_detalle_venta` = %s, `fecha` = %s, `cantidad` = %s, `id_factura` = %s, `id_producto` = %s WHERE `id_detalle_venta` = %s;"
    cursor = conn.cursor()
    try:
        cursor.execute(sql, datos)
        conn.commit()
    finally:
        cursor.close()
        conn.close()
 
    flash("detalle_venta Actualizado Correctamente")
    return redirect(url_for('detalle_ventaAdmin'))
 
 
@app.route('/admin/detalle_ventaAdmin/borrar', methods=['POST'])
def admin_detalle_venta_borrar():
 
    if not 'login' in session:
        return redirect('/admin/loginAdmin')
 
    id_detalle_venta = request.form['id_detalle_venta']
 
    conn = mysql.connector.connect(**config)
    sql = "DELETE FROM detalle_venta WHERE id_detalle_venta = %s;"
    cursor = conn.cursor()
    try:
        cursor.execute(sql, [id_detalle_venta])
        conn.commit()
    finally:
        cursor.close()
        conn.close()
 
    flash("detalle_venta Eliminado Correctamente")
    return redirect(url_for('detalle_ventaAdmin'))




"""
Este comando es necesario para
correr nuestra aplicacion
"""
if __name__ == '__main__':
    app.run(debug=True)
 