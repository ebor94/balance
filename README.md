# Báscula Digital - Aplicación de Pesaje

## Descripción

Aplicación de escritorio desarrollada en Python para la gestión de una báscula digital. Permite la lectura de peso en tiempo real y el envío de datos a una API.

### Características principales

- Interfaz gráfica intuitiva
- Lectura de puerto serial
- Monitoreo en tiempo real
- Envío automático de datos a API
- Soporte para múltiples puertos seriales

## Requisitos previos

- Python 3.x
- Dependencias (instalar con pip):

```
pip install pyserialpip install requestspip install tkinter
```

## Estructura del proyecto

```
bascula-digital/│├── main.py              # Archivo principal
                ├── config.ini           # Archivo de configuración
                ├── requirements.txt     # Dependencias del proyecto
                └── assets/
                └── icon.ico        # Ícono de la aplicación
```

## Configuración

El archivo `config.ini` debe contener:

```
[APP]title = BASCULA SERVITECA-PC[SERIAL]baudrate = 9600timeout = 1[API]url = https://lilix.ceramicaitalia.com:3001/transporte/grabaPeso/
```

## Instalación

1. Clonar el repositorio
1. Instalar dependencias:

```
pip install -r requirements.txt
```

## Uso

1. Ejecutar la aplicación:

```
python main.py
```

1. Seleccionar el puerto serial de la báscula
1. Conectar el dispositivo
1. Usar el modo manual (botón "TOMAR PESO") o activar la lectura en tiempo real

## Funcionalidades

- **Conexión al puerto:** Permite seleccionar y conectar el puerto serial de la báscula
- **Lectura en tiempo real:** Monitoreo continuo del peso
- **Toma manual:** Botón para tomar lecturas individuales y transmite los datos al servidor via api

## Formato de datos

La aplicación espera datos en el siguiente formato:

```
LGxxxZx
```

donde 'xxx' representa el peso en el formato específico de la báscula.

## Creación de ejecutable

Para crear un archivo ejecutable:

```
pip install pyinstallerpyinstaller --name="Bascula" --windowed --onefile --icon=assets/icon.ico main.py
```

## Solución de problemas

- **Error de puerto:** Verificar que el puerto serial esté correctamente conectado
- **Error de lectura:** Asegurar que la báscula esté encendida y funcionando
- **Error de API:** Verificar la conexión a internet y la URL del servidor

## Contribución

1. Fork del repositorio
1. Crear rama para nueva característica
1. Commit de cambios
1. Push a la rama
1. Crear Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT.

## Contacto

Para soporte o consultas, contactar a [webmaster@ceramicaitalia.com]

## Notas de versión

- v1.0.0
  - Lanzamiento inicial
  - Soporte para lectura en tiempo real
  - Integración con API

<br>
