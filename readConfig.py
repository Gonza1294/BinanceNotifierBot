import yaml

def readConfig(ruta_clave):
    try:
        with open("conf.yaml", 'r') as archivo:
            configuracion = yaml.safe_load(archivo)
            valor = configuracion
            for clave in ruta_clave:
                if clave in valor:
                    valor = valor[clave]
                else:
                    print(f"La clave '{'/'.join(ruta_clave)}' no se encontró en el archivo de configuración.")
                    return None
            return valor
    except FileNotFoundError:
        print("El archivo de configuración no se encontró.")
        return None
    except yaml.YAMLError as e:
        print("Error al cargar el archivo de configuración:", e)
        return None