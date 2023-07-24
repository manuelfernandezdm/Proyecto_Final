# Proyecto_Final

En este repositprio se encuentra mi proyecto final de carrera.

Es un software que permite la comunicacion con un dispositivo FPGA via puerto Ethernet. El programa recibe y envia mensajes utilizando el protocolo UDP y muestra toda la informacion en una interfaz grafica desarrollada con Qt. Esta interfaz simula la interfaz fisica de una consola de un barco.

Archivos:
* TDC_logica.py : se implementa la clase principal, encargada de manejar la comunicacion con la FPGA
* TDC_GUI.py : se implementa todos los metodos necesarios para conectar la interfaz grafica hecha con Qt con la clase de logica
* AND_5.py : implementacion de un monitor auxiliar para la visualizacion de caracteres
* radarwidget.ui : desarrollo de la interfaz grafica de la consola del barco.

Se muestra el diagrama de flujo simplificado del programa en el archivo diagrama de flujo.

