import mysql.connector
import json
import uuid
from datetime import datetime

# Configura la conexión a la base de datos MySQL
conexion = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Danielita29',
    database='dinoshop'
)

# Lee el archivo JSON
with open('result.json', 'r',encoding='utf-8') as archivo:
    datos_json = json.load(archivo)

# Crea un cursor para ejecutar consultas en la base de datos
cursor = conexion.cursor()

def get_float_price(price_str):
    try:
        # Eliminar los caracteres no numéricos del precio y convertirlo a float
        cleaned_price = price_str.replace('$', '').replace('.', '').replace(' ', '')
        return float(cleaned_price)
    except ValueError:
        # Si no se puede convertir a float, devolver None
        return None

# Recorre cada elemento del JSON y agrega los datos a la base de datos
for elemento in datos_json:
    print(elemento)
    # Inserta la categoría y obtén su ID
    if isinstance(elemento['category'], dict):
        type1 = elemento['category']['type1']
    else:
        type1 = 'Sin categoría'
    
    cursor.execute("INSERT INTO categorias (nombre) VALUES (%s)", (type1,))
    categoria_id = cursor.lastrowid

    # Inserta el color y obtén su ID
    color = elemento['color']
    cursor.execute("INSERT INTO colores (nombre) VALUES (%s)", (color,))
    color_id = cursor.lastrowid

    # Inserta la marca y obtén su ID
    marca = "mango"
    cursor.execute("INSERT INTO marcas (nombre) VALUES (%s)", (marca,))
    marca_id = cursor.lastrowid

    # Inserta el producto con las llaves foráneas correspondientes
    uuid_value = str(uuid.uuid4())
    codigo_dino = uuid_value[:10] + "_" + datetime.now().strftime('%Y%m%d%H%M%S')
    titulo = elemento['title']
    reference = elemento['reference']    
    precio_inicial = get_float_price(elemento['initialPrice'])
    precio_oferta = get_float_price(elemento['currentPrice'])    
    cursor.execute("INSERT INTO productos (codigo_dino, titulo, categoria_id, marca_id, referencia, precio_inicial, precio_oferta) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                   (codigo_dino, titulo, categoria_id, marca_id, reference, precio_inicial, precio_oferta))

    # Inserta las imágenes del producto en la tabla galeria_productos
    for imagen in elemento['img']:
        url_img = imagen
        cursor.execute("INSERT INTO galeria_productos (codigo_dino, color_id,url_img) VALUES (%s, %s, %s)",
                       (codigo_dino, color_id, url_img))

    # Inserta las tallas disponibles del producto en la tabla producto_tallas
    for talla_disponible in elemento['availableSizes']:
        cursor.execute("INSERT INTO tallas (talla) VALUES (%s)", (talla_disponible,))
        talla_id = cursor.lastrowid
        cursor.execute("INSERT INTO producto_tallas (codigo_dino, talla_id) VALUES (%s, %s)",
                       (codigo_dino, talla_id))

    # Inserta las características del producto en las tablas tipo_caracteristicas y caracteristica_productos
    if isinstance(elemento['specification'], dict):
        for tipo_caracteristica, valor in elemento['specification'].items():
            cursor.execute("INSERT INTO tipo_caracteristicas (categoria_id, descripcion) VALUES (%s, %s)",
                           (categoria_id, tipo_caracteristica))
            tipo_caracteristica_id = cursor.lastrowid
            
            # Inserta el valor como una cadena si es una lista
            if isinstance(valor, list):
                valor = ', '.join(valor)

            cursor.execute("INSERT INTO caracteristica_productos (codigo_dino,tipo_id, detalle) VALUES (%s, %s,%s)",
                           (codigo_dino,tipo_caracteristica_id, valor))


# Realiza la confirmación para guardar los cambios en la base de datos
conexion.commit()

# Cierra el cursor y la conexión a la base de datos
cursor.close()
conexion.close()