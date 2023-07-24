import numpy as np
import matplotlib.pyplot as plt     #https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.html
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvas #la matplotlib.backend_bases.FigureCanvases el área en la que se dibuja la figura
from matplotlib.figure import Figure

import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
import math

import matplotlib.image as mpimg
from matplotlib.cbook import get_sample_data
from matplotlib.offsetbox import OffsetImage, AnnotationBbox


class RadarWidget(QWidget):
    """
    Es el widget donde se muestra el radar y los blancos simulados.
    """
    def __init__(self,parent=None,area=200,h=300,w=256):     #metodo que inicializa la clase.
        QWidget.__init__(self,parent)
        
        # Self -> Vars
        self.RMillaMuestra = 1 
        self.RTA = 1
        self.area = area
        self.h=h
        self.w=w
        self.figure = plt.figure()                  #crea una nueva figura(pantalla de la GUI)
        self.figure.set_facecolor("#b5b5b5")        #seteo el color de fondo del widget (fondo gris).
        self.canvas = FigureCanvas(self.figure)     #XXX
        layOut = QVBoxLayout()                      #alinea los widgets verticalmente.
        layOut.addWidget(self.canvas)               #agrego el canvas a la figura
        
        self.origen_x = 0
        self.origen_y = 0
        self.escala_DM = 256    #cuanto es mi R partiendo del centro de coordenadas

        self.color_punto = "ro"


        # Self -> Canvas -> (Widget)
        self.canvas.plt = plt
        self.canvas.plt.rc('xtick', labelsize=14)
        self.canvas.ax = self.figure.add_subplot(111, projection='polar')
        self.canvas.ax.set_theta_zero_location('N')
        self.canvas.ax.set_theta_direction(-1)       
        #self.canvas.ax.set_rmax(self.w/self.RMillaMuestra)
        self.canvas.ax.set_rmax(self.escala_DM)
        self.canvas.ax.set_rmin(0)
        self.canvas.ax.set_aspect('equal')
        self.canvas.ax.set_facecolor('#a9d9b6')     #coloreo el circulo del radar en verde.
        self.setLayout(layOut)
        
        plt.connect('button_press_event', self.on_click)        #cada vez que hago un click en la pantalla, se ejecute el metodo on_click()

        self.lista_coordenadas = []
        #####   variables de escala y cambio de origen  #####
        self.origen = "(" + str(self.origen_x) + ";" + str(self.origen_y) + ")"
        self.canvas.ax.text(math.pi, self.escala_DM/27, s=self.origen, fontsize=10, va = "center", ha = "center")

    def plotear(self,angulo,distancia):
        """
        Dibuja un punto en el radar simulando un blanco detectado.
        """
        self.canvas.ax.plot(angulo, distancia, self.color_punto)
        #self.canvas.ax.set_rmax(self.w/self.RMillaMuestra)
        self.canvas.ax.set_rmax(self.escala_DM)
        self.canvas.ax.set_rmin(0)
    
    def borrarPuntos(self):
        """
        Limpia ploteos anteriores.
        """
        self.canvas.ax.clear()
        self.canvas.ax.set_theta_zero_location('N')
        self.canvas.ax.set_theta_direction(-1)       
        #self.canvas.ax.set_rmax(self.w/self.RMillaMuestra)
        self.canvas.ax.set_rmax(self.escala_DM)
        self.canvas.ax.set_rmin(0)
        self.canvas.ax.set_aspect('equal')
    
    """
    def setParametrosADC(self, RMillaMuestra, RTA):
        self.RMillaMuestra = RMillaMuestra
        self.RTA = RTA            
        self.canvas.ax.set_rmax(self.w/self.RMillaMuestra)
        self.canvas.ax.set_rmin(0)
    """
    def graficar_markers (self, lista):     #grafico un punto en las coordenadas recibidas (cuando recibo "muestra")
        bool_graf_simbolo = True
        for i in range(len(lista)):
            if lista[i][2] == "muestro":
                x_escalado = lista[i][0] - self.origen_x    #cambio de coordenadas
                y_escalado = lista[i][1] - self.origen_y
                theta, radio = self.xy_2_polar (y_escalado, x_escalado)
                self.plotear(theta, radio)

            if len(lista[i])>3:    #si tengo simbolos para graficar:
                texto = "  "
                simbolo = ""
                bool_graf_simbolo = True
                for ii in range(len(lista[i][3])):  #recorro la lista de simbolos
                    if type(lista[i][3][ii]) == str:    #si es un caracter, lo escribo
                        texto += lista[i][3][ii]
                    if type(lista[i][3][ii]) == int: 
                        if lista[i][3][ii] == 33:       #es el guion desp del simbolo
                            texto = "-" + texto
                        simbolo += str(lista[i][3][ii])
                #busco qué simbolo debo dibujar -> tabla de simbolos de la LPD
                        # superficie
                if simbolo == "8":          #cursor
                    simbolo_png = "cursor2" 
                    self.color_punto = "ko"
                elif simbolo == "15":      #cursor alargado
                    simbolo_png = "cursor_alargado"
                    self.color_punto = "ko"
                elif simbolo == "2996":
                    simbolo_png = "sup_desconocido"
                    self.color_punto = "ro"
                elif simbolo == "29100":
                    simbolo_png = "sup_posible_amigo"
                    self.color_punto = "ro"
                elif simbolo == "30":
                    simbolo_png = "sup_amigo_confirmado"
                    self.color_punto = "ro"
                elif simbolo == "29123":
                    simbolo_png = "sup_posible_hostil"
                    self.color_punto = "ro"
                elif simbolo == "31":
                    simbolo_png = "sup_hostil_confirmado"
                    self.color_punto = "ro"
                elif simbolo == "29":
                    simbolo_png = "pendiente"
                    self.color_punto = "ro"
                        # aire
                elif simbolo == "196":
                    simbolo_png = "aire_desconocido"
                    self.color_punto = "go"
                elif simbolo == "1100":
                    simbolo_png = "aire_posible_amigo"
                    self.color_punto = "go"
                elif simbolo == "2":
                    simbolo_png = "aire_amigo_confirmado"
                    self.color_punto = "go"
                elif simbolo == "1123":
                    simbolo_png = "aire_posible_hostil"
                    self.color_punto = "go"
                elif simbolo == "3":
                    simbolo_png = "aire_hostil_confirmado"
                    self.color_punto = "go"
                elif simbolo == "1":
                    simbolo_png = "pendiente"
                    self.color_punto = "go"
                        # submarino
                elif simbolo == "2596":
                    simbolo_png = "sub_desconocido"
                    self.color_punto = "bo"
                elif simbolo == "25100":
                    simbolo_png = "sub_posible_amigo"
                    self.color_punto = "bo"
                elif simbolo == "26":
                    simbolo_png = "sub_amigo_confirmado"
                    self.color_punto = "bo"
                elif simbolo == "25123":
                    simbolo_png = "sub_posible_hostil"
                    self.color_punto = "bo"
                elif simbolo == "27":
                    simbolo_png = "sub_hostil_confirmado"
                    self.color_punto = "bo"
                elif simbolo == "25":
                    simbolo_png = "pendiente"
                    self.color_punto = "bo"
                        # puntos de referencia
                elif simbolo == "24":
                    simbolo_png = "pdr_no_sub"
                    self.color_punto = "yo"
                elif simbolo == "19":
                    simbolo_png = "pdr_punto_dato"
                    self.color_punto = "yo"
                elif simbolo == "17":
                    simbolo_png = "pdr_fix"
                    self.color_punto = "yo"
                elif simbolo == "18":
                    simbolo_png = "punto_de_referencia"
                    self.color_punto = "yo"
                
                ###   agrego simbolos faltantes   ###
                elif simbolo =="5":
                    simbolo_png = "0000100"
                    self.color_punto = "mo"     #color magenta
                elif simbolo =="7":
                    simbolo_png = "0000111"
                    self.color_punto = "mo" 
                elif simbolo =="11":
                    simbolo_png = "0001011"
                    self.color_punto = "mo" 
                elif simbolo =="13":
                    simbolo_png = "0001101"
                    self.color_punto = "mo" 
                elif simbolo =="16":
                    simbolo_png = "0010000"
                    self.color_punto = "mo" 
                elif simbolo =="20":
                    simbolo_png = "0010100"
                    self.color_punto = "mo" 
                elif simbolo =="22":
                    simbolo_png = "0010110"
                    self.color_punto = "mo" 
                elif simbolo =="33":
                    simbolo_png = "0100001"
                    self.color_punto = "mo" 
                elif simbolo =="35":
                    simbolo_png = "0100011"
                    self.color_punto = "mo" 
                elif simbolo =="37":
                    simbolo_png = "0100101"
                    self.color_punto = "mo" 
                elif simbolo =="42":
                    simbolo_png = "0101010"
                    self.color_punto = "mo" 
                elif simbolo =="92":
                    simbolo_png = "1011100"
                    self.color_punto = "mo" 
                elif simbolo =="94":
                    simbolo_png = "1011110"
                    self.color_punto = "mo" 
                #-------------------------
                elif simbolo =="6":
                    simbolo_png = "0000110"
                    self.color_punto = "mo" 
                elif simbolo =="9":
                    simbolo_png = "0001001"
                    self.color_punto = "mo" 
                elif simbolo =="12":
                    simbolo_png = "0001100"
                    self.color_punto = "mo"
                elif simbolo =="14":
                    simbolo_png = "0001110"
                    self.color_punto = "mo"
                elif simbolo =="19":
                    simbolo_png = "0010011"
                    self.color_punto = "mo"
                elif simbolo =="21":
                    simbolo_png = "0010101"
                    self.color_punto = "mo"
                elif simbolo =="32":
                    simbolo_png = "0100000"
                    self.color_punto = "mo"
                elif simbolo =="34":
                    simbolo_png = "0100010"
                    self.color_punto = "mo"
                elif simbolo =="36":
                    simbolo_png = "0100100"
                    self.color_punto = "mo"
                elif simbolo =="38":
                    simbolo_png = "0100110"
                    self.color_punto = "mo"
                elif simbolo =="91":
                    simbolo_png = "1011011"
                    self.color_punto = "mo"
                elif simbolo =="93":
                    simbolo_png = "1011101"
                    self.color_punto = "mo"


                else:       #si me llega un simbolo que no tengo el png
                    texto = "¡" + texto  # el simbolo binario recibido no se encuentra en la carpeta de simbolos png, se debe agregar
                    #print("Falta el simbolo: ", simbolo)    #imprimo el simbolo (en su valor de entero) en consola para que se sepa cual es
                    bool_graf_simbolo = False

                x_escalado = lista[i][0] - self.origen_x    #cambio de coordenadas
                y_escalado = lista[i][1] - self.origen_y
                if (math.sqrt(x_escalado*x_escalado+y_escalado*y_escalado)) <= self.escala_DM:      #si el texto se encuentra dentro del radar:
                    self.graficar_texto(x_escalado, y_escalado,texto)
                """
                ---> se comento para que no se grafiquen los simbolos BMP
                """
                if bool_graf_simbolo:
                    self.plot_imagen(x_escalado, y_escalado,simbolo_png)
                    #pass
                

    def graficar_cursores(self,lista):
        leng = len (lista)
        for i in range(leng):
            cursor_angle = (lista[i][0])*3.141592/180       #angulo en radianes
            cursor_length = lista[i][1]
            tipo_linea = lista[i][2]
            cox = lista[i][3]   #cursor origin X
            coy = lista[i][4]   #cursor origin Y

            # 1ro) paso el punto cursor_length y cursor_angle a coordenadas cartesianas
            if cursor_angle >= 0 and cursor_angle <= (3.141592/2):
                Rx = round(cursor_length * math.sin(cursor_angle),3)
                Ry = round(cursor_length * math.cos(cursor_angle),3)
            elif cursor_angle > (3.141592/2) and cursor_angle <= 3.141592:
                Rx = round(cursor_length * math.sin(3.141592-cursor_angle),3)
                Ry = round(-cursor_length * math.cos(3.141592-cursor_angle),3)
            elif cursor_angle >= (-3.141592/2) and cursor_angle < 0:
                Rx = round(cursor_length * math.sin(cursor_angle),3)
                Ry = round(cursor_length * math.cos(cursor_angle),3)
            else:
                Rx = round(cursor_length * math.sin(3.141592-cursor_angle),3)
                Ry = round(-cursor_length * math.cos(3.141592-cursor_angle),3)
            #calculo los puntos A y B y aplico el cambio de coordenadas para graficarlos
            puntoA = [cox-self.origen_x, coy-self.origen_y]
            puntoB = [cox+Rx-self.origen_x, coy+Ry-self.origen_y]
            radio0 = round(math.sqrt(pow(puntoA[0],2)+pow(puntoA[1],2)),3)
            radio1 = round(math.sqrt(pow(puntoB[0],2)+pow(puntoB[1],2)),3)

            if puntoA [0] == 0:
                if puntoA[1] < 0:
                    theta0 = 3.141592
                else:
                    theta0 = 0
            elif puntoA[1] == 0:    
                if puntoA[0] > 0:
                    theta0 = 3.141592/2
                elif puntoA[0] < 0:
                    theta0 = 3*3.141592/2
                else:  
                    theta0 = 0
            else:    
                theta = round(math.atan(abs(puntoA[0])/abs(puntoA[1])),3)
                if puntoA[0] >= 0 and puntoA[1] >= 0:   #1er cuadrante
                    theta0 = theta
                elif puntoA[0] >= 0 and puntoA[1] < 0:  #4to cuadrante
                    theta0 = 3.141592 - theta
                elif puntoA[0] < 0 and puntoA[1] < 0:   #3er cuadrante
                    theta0 = 3.141592 + theta
                else:                                   #2do cuadrante
                    theta0 = 2*3.141592 - theta
            theta0 = round(theta0,3)
    
            if puntoB [0] == 0:
                if puntoB[1] < 0:
                    theta1 = 3.141592
                else:
                    theta1 = 0
            elif puntoB[1] == 0:     
                if puntoB[0] > 0:
                    theta1 = 3.141592/2
                elif puntoB[0] < 0:
                    theta1 = 3*3.141592/2
                else:  
                    theta1 = 0
            else:    
                theta = round(math.atan(abs(puntoB[0])/abs(puntoB[1])),3)
                if puntoB[0] >= 0 and puntoB[1] >= 0:   #1er cuadrante
                    theta1 = theta
                elif puntoB[0] >= 0 and puntoB[1] < 0:  #4to cuadrante
                    theta1 = 3.141592 - theta
                elif puntoB[0] < 0 and puntoB[1] < 0:   #3er cuadrante
                    theta1 = 3.141592 + theta
                else:                                   #2do cuadrante
                    theta1 = 2*3.141592 - theta
            theta1 = round(theta1,3)

            # https://matplotlib.org/stable/gallery/lines_bars_and_markers/linestyles.html -> tipos de linea: libreria matplotlib
            if tipo_linea == 0:
                tipo_linea = 'solid'
                color = 'black'
            elif tipo_linea == 1:
                tipo_linea = (0,(2,2))
                color = 'black'
            elif tipo_linea == 2:
                tipo_linea = (0,(4,4))
                color = 'black'
            elif tipo_linea == 3:
                tipo_linea = (0,(6,2))
                color = 'black'
            elif tipo_linea == 4:
                tipo_linea = (0,(12,4))
                color = 'black'
            elif tipo_linea == 5:
                tipo_linea = (0,(6,4,2,4))
                color = 'black'
            elif tipo_linea == 6:
                tipo_linea = (0,(2,2,4,2,2,4))
                color = 'black'
            else:       #tipo_linea = 7
                tipo_linea = (0,(10,2,2,2))
                color = 'black'
            
            linea = self.canvas.ax.plot([theta0, theta1], [radio0, radio1], c=color,linestyle=tipo_linea)
            #self.canvas.ax.set_rmax(self.w/self.RMillaMuestra)
            self.canvas.ax.set_rmax(self.escala_DM)
            self.canvas.ax.set_rmin(0)
    
    def graficar_texto (self, coord_y, coord_x, texto):
        texto = " " + texto
        theta, radio = self.xy_2_polar(coord_x, coord_y)
        self.canvas.ax.text(theta, radio, s=texto, fontsize=10, va = "center", ha = "left")
    
    def on_click(self,event):
        lista_aux = []
        phi, rho = event.xdata, event.ydata
        ix = round(rho * math.sin(phi),2) + self.origen_x   #aplico cambio de coordenadas
        iy = round(rho * math.cos(phi),2) + self.origen_y   #aplico cambio de coordenadas
        lista_aux.append(ix)
        lista_aux.append(iy)
        if math.sqrt(ix*ix+iy*iy) <= 256:       #controlo que la coordenada seleccionada entre en el rango [-256,256] para no enviar coordenadas erroneas (imposibles de pasar a binario, provocando un error)
            self.lista_coordenadas.append(lista_aux)
            print(self.lista_coordenadas)

    def get_lista_coordenadas(self):
        lista_coord = self.lista_coordenadas
        self.lista_coordenadas = []
        return lista_coord

    def plot_imagen (self, coord_x, coord_y, nombre_png):
        x_escalado = coord_x #- self.origen_x
        y_escalado = coord_y #- self.origen_y
        #image = plt.imread('Nueva carpeta/image/png/' + nombre_png + '.png', format = 'png')                           #pongo la ruta de la imagen que quiero colocar: PNG
        image = plt.imread('Nueva carpeta/image/bmp/' + nombre_png + '.bmp', format = 'bmp')                            #pongo la ruta de la imagen que quiero colocar: BMP
        #radio = round(math.sqrt(coord_x**2 + coord_y**2),3)
        #angulo = round(math.atan2(coord_x, coord_y),3)
        radio = round(math.sqrt(x_escalado**2 + y_escalado**2),2)
        angulo = round(math.atan2(x_escalado, y_escalado),2)
        self.canvas.ax.add_artist(AnnotationBbox(OffsetImage(image, zoom = 0.4), (angulo, radio), frameon = False))       #con zoom vario el tamaño de la imagen, (1,1) -> coordenadas de la imagen (CENTRO)
        #plt.draw()
    
    def set_range_scale (self,escala):
        self.escala_DM = escala
    
    def set_origen_x_y (self, lista_1):
        if len(lista_1) == 0:
            #print("coordenadas no validas")
            pass
        else: # si la lista no esta vacia -> las coordenadas son validas
            self.origen_x = lista_1[0][0]
            self.origen_y = lista_1[0][1]
            self.origen = "(" + str(self.origen_x) + ";" + str(self.origen_y) + ")"
            self.canvas.ax.text(math.pi, self.escala_DM/25, s=self.origen, fontsize=10, va = "center", ha = "center")
            #print("origen :", self.origen_x, self.origen_y, "son validos")
        

    def polar_2_xy (self, theta, radio):
        # theta esta en radianes
        x = round(radio * math.cos(theta),2)
        y = round(radio * math.sin(theta),2)
        return x,y

    def xy_2_polar (self, x, y):
        # devuelve theta en radianes
        theta = round(math.atan2(y,x),3)
        radio = round(math.sqrt(x*x + y*y),2)
        return theta, radio