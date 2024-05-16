from flask import Flask, render_template, request
from pymongo import MongoClient

# Configuración de la conexión a la base de datos MongoDB Atlas
MONGO_URI = 'mongodb+srv://claylol:souled123@contaminacion.1sqkive.mongodb.net/'
client = MongoClient(MONGO_URI)
db = client.get_database('ContaminacionBCN')

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Obtener los datos del formulario
        barrio = request.form['barrio']
        dia_mes = request.form['dia_mes']
        
        # Validar que el campo "dia_mes" no esté vacío
        if not dia_mes:
            return render_template('error.html', message="Debe proporcionar un día del mes.")
        
        # Convertir el día del mes a entero
        try:
            dia_mes = int(dia_mes)
        except ValueError:
            return render_template('error.html', message="El día del mes debe ser un número entero.")
        
        # Obtener el código de la estación de monitoreo para el barrio seleccionado
        estacion_info = db.Estaciones.find_one({'Nom_barri': barrio})
        if estacion_info:
            estacion_codigo = estacion_info['Estacio']
            
            # Consultar la base de datos para obtener los datos de contaminación
            collection = db.CalidadAire
            contaminacion_data = collection.find_one({'ESTACIO': estacion_codigo, 'DIA': dia_mes})
            
            if contaminacion_data:
                # Obtener el tipo de contaminante correspondiente
                codi_contaminant = contaminacion_data['CODI_CONTAMINANT']
                contaminante_info = db.Contaminantes.find_one({'Codi_Contaminant': codi_contaminant})
                if contaminante_info:
                    desc_contaminant = contaminante_info['Desc_Contaminant']
                    unitats = contaminante_info.get('Unitats', 'Desconocidas')
                else:
                    desc_contaminant = "Tipo de contaminante desconocido"
                    unitats = "Desconocidas"
                
                # Pasar el nombre del barrio seleccionado y el tipo de contaminante a la plantilla resultado.html
                return render_template('resultado.html', 
                                       barrio=barrio, 
                                       contaminacion_data=contaminacion_data, 
                                       desc_contaminant=desc_contaminant, 
                                       unitats=unitats,
                                       h12=contaminacion_data['H12'])
        
        # Si no se encontraron datos de contaminación para el barrio y día seleccionados
        return render_template('error.html', message="No se encontraron datos de contaminación para el barrio y día seleccionados.")
        
    else:
        # Obtener la lista de nombres de barrio desde la colección Estaciones
        barrios = db.Estaciones.distinct("Nom_barri")
        return render_template('formulario.html', barrios=barrios)

if __name__ == '__main__':
    app.run(debug=True)
