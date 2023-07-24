#from auxiliar1 import tecla_mik_L
import sys  
from PyQt5 import uic, QtWidgets        #uic: funcion encargada de cargar la interfaz grafica
from PyQt5.QtWidgets import QMainWindow, QApplication     
from radarwidget import RadarWidget     #importo el widget "radarwidget" 
from TDC_GUI import TDC_GUI
import numpy as np 
import socket
import time
import threading        # El paquete threading es necesaria para poder usar hilos
from pynput.keyboard import Key, Listener   #para manejar las entradas del teclado
from pynput import keyboard
from datetime import datetime


class TDC_logica:
    """
    esta es la clase principal, la encargada de implementar la logica de la 
    tactica, y su comunicacion con la FPGA
    """
    def __init__(self):
        self.gui = TDC_GUI()
        self.gui.show()

        #---------variables---------
        #self.IP_TDC = '192.168.1.2'
        """
        self.IP_TDC = 'localhost'
        self.PORT_TDC = 8000
        self.IP_FPGA = "0.0.0.0"
        self.PORT_FPGA = 8001
        """
        self.IP_TDC = '172.16.0.99'
        self.PORT_TDC = 8001
        self.IP_FPGA = '172.16.0.101'
        self.PORT_FPGA = 9000
        

        self.nro_secuencia = 0      #nro de secuencia propio para los mensajes de estado del CONC
        """
        self.matriz_vacia1 = np.full((17,32)," ")        #matriz de la AND auxiliar
        self.matriz_vacia2 = np.full((17,32)," ") 
        """
        self.matriz_vacia1 = np.full((16,32)," ")        #matriz de la AND auxiliar
        self.matriz_vacia2 = np.full((16,32)," ") 
        
        self.matriz_AND1 = self.matriz_vacia1                 #matriz de la AND1
        self.matriz_AND2 = self.matriz_vacia2                 #matriz de la AND2
        
        self.lista_caracteres_AND = [' ','!','"','#','$','%','&','´','(',')','*','+',',','-','.','/','0','1','2','3','4','5','6','7','8','9',':',';','<','=','>','?','@','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','[','|',']','°','_']
        
        self.label_selection = False    #variable booleana que me indica si el Label Selection esta habilitado o no.

        self.lista_AB1 = []
        self.lista_AB2 = []
        self.lista_AB3 = []
        self.graficar_LPD = False

        #variables auxiliares para reenviar el estado del DCL CONC hasta recibir el ACK de la FPGA   
        self.tiempo_reenvio_estado_conc = 0.2     #reenvio el estado del conc si no obtenog un ACK cada 0.2 segundos
        self.esperando_ACK_CONC = False
        self.rta_DCL_CONC = ""     
        self.tiempo_interruptor = 0.01

        #self.mensaje = ""
        self.mensajes_LPD = []          #lista donde se guardan los mensajes LPD recibidos
        self.dec_msj_LPD = False        #variable booleana para implementar decodificar_msj_LPD() en un hilo diferente.

    #-------------------------------------------------------------------
    #       Servicio que procesa los mensajes recibidos de la FPGA      
    #-------------------------------------------------------------------
    def receiveServer(self):
        global socket_TDC
        socket_TDC = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)           #AF.INET: IPV4, SOCK_DGRAM: UDP
        socket_TDC.bind((self.IP_TDC, self.PORT_TDC))   

        while True:
            try:
                msj_recibido, srcAddr = socket_TDC.recvfrom(1500)                     #recibo el msg y la direccion del emisor (cliente) [1500:buffer(bytes)]
                self.IP_FPGA = srcAddr[0]
                self.PORT_FPGA = srcAddr [1]
                mensaje = self.decodificar_bytearray(msj_recibido)
                self.decodificar_msj_recibido(mensaje)

            except Exception:
                print("Cerrando socket servidor")
                break
        socket_TDC.close()
    
        """
        msj_recibido, srcAddr = socket_TDC.recvfrom(1500)                     #recibo el msg y la direccion del emisor (cliente) [1500:buffer(bytes)]
        self.IP_FPGA = srcAddr[0]
        self.PORT_FPGA = srcAddr [1]
        #print("Source Addr: ", self.IP_FPGA, " ", self.PORT_FPGA)
        mensaje = self.decodificar_bytearray(msj_recibido)
        #print(mensaje)
        self.decodificar_msj_recibido(mensaje)
        #data = self.codificar_bytearray("11001100")
        #data = self.invertir_cadena(self.ack)
        #data = self.codificar_bytearray(data)
        #print(data)
        #socket_TDC.sendto(data, srcAddr)
        """
    """   
    def print_txt(self, texto):
        f = open('registro.txt','a')
        f.write(str(datetime.now().time())+ "  ")
        f.write(texto + '\n')
        f.close()
    """     
    #--------------------------------------------------    
    #           Envía el mensaje a la FPGA                                
    #--------------------------------------------------    
    def sendMsg(self, mensaje):  
        addr = (self.IP_FPGA, self.PORT_FPGA)
        msg = self.codificar_bytearray(mensaje)
        try:
            socket_TDC.sendto(msg,addr)            #envio el mensaje.
        except:
            print("Hay un error cuando mando el mensaje")
            #self.print_txt("Error cuando mando un msj (send message)")
       
    def reenviar_estado_CONC(self):     #metodo para reenviar el estado del CDL CONC a la FPGA hasta recibir el ACK
        global socket_TDC
        #while True:
        if self.esperando_ACK_CONC == True:         #si el mensaje ACK no llego todavia:
            time.sleep(self.tiempo_reenvio_estado_conc)     #espero un tiempo determinado para volver a enviarlo 
            if self.esperando_ACK_CONC == True:             #si todavia no recibo el ACK, reenvio el estado del CONC
                addr = (self.IP_FPGA, self.PORT_FPGA)
                msg = self.rta_DCL_CONC
                msg = self.codificar_bytearray (msg)
                try:
                    socket_TDC.sendto(msg, addr)
                except:
                    print("Error enviando el estado del DCL CONC")
                #print("reenviando estado DCL CONC")
    
    def codificar_bytearray (self, mensaje):    #funcion que convierte la palabra mensaje "10010...01" a un bytearray para poder mandarla por el socket
        leng = round(len (mensaje)/8)
        msj_ba = bytearray()
        for i in range(leng):
            msj_dec = int(mensaje [8*i:8*i+8],2)
            msj_ba.append(msj_dec)
        return msj_ba

    def decodificar_bytearray(self, mensaje):   #funcion que convierte el bytearray recibido en la palabra mensaje: "10010...10"
        leng = len(mensaje)
        msj = ""
        for i in range(leng):
            msj += "{0:08b}".format(mensaje[i])
        return msj
    
    def negar_palabra_binaria(self, mensaje):
        leng = len(mensaje)
        mensaje_negado = ""
        for i in range(leng):
            if mensaje[i] == "0":
                mensaje_negado += "1"
            else:
                mensaje_negado += "0"
        return mensaje_negado

    def decodificar_msj_recibido(self, msj_bin):
        confirmacion = msj_bin [0:24]
        reset = msj_bin [0:2]
        device_add = msj_bin [4:8]
        ack_o_msj= msj_bin [8]
        nro_sec_bin = msj_bin [9:24]        #nro secuencia binario
        #nro_secuencia = int(nro_sec_bin,2)  #nro de secuencia decimal

        mensaje = msj_bin [24:]             #la parte util del mensaje recibido
        mensaje = self.negar_palabra_binaria(mensaje)    # la info de la FPGA viene negada, por lo que debo volver a negarla para poder decodificarla

        #1ro) mando el ACK
        if ack_o_msj == "0":        #si el mensaje recibido es MSJ 
            if device_add != "0000":    #y no es de la LPD -> envio el ACK ("0000"->msj de la LPD)
                if device_add != "0001":    #y tampoco es un mensaje de peticion del estado del DCL CONC:
                    ack = "00" + "00" + device_add + "1" + nro_sec_bin
                    self.sendMsg(ack)   

            if device_add == "0000":     #mensaje de la LPD
                #print("Mensaje LPD")
                #self.print_txt("Mensaje LPD")
                #self.decodificar_msj_LPD(mensaje)
                #self.mensaje = mensaje
                print(len(self.mensajes_LPD))
                self.mensajes_LPD.append(mensaje)
                self.dec_msj_LPD = True
                #self.decodificar_msj_LPD()


            elif device_add == "0001":   #mensaje de peticion del DCL CONC
                self.esperando_ACK_CONC = False 
                encabezado = "00" + "00" + "0100" + "0" + "{0:b}".format(self.nro_secuencia).zfill(15)
                estado_CONC = self.gui.return_estado_CONC() # objeto de la clase TDC.return_estado_CONC
                estado_CONC = self.negar_palabra_binaria(estado_CONC)    #debo negar el estado del DCL CONC para enviarlo a la FPGA
                mensaje_conc = encabezado + estado_CONC

                #self.print_txt(mensaje_conc)
                
                self.rta_DCL_CONC = mensaje_conc
                self.sendMsg(mensaje_conc)
                self.esperando_ACK_CONC = True
                if self.nro_secuencia < 32767:
                    self.nro_secuencia += 1
                else:
                    self.nro_secuencia = 0
                
            elif device_add == "0010":   #mensaje de la AND1
                #print("Mensaje de la AND1")
                #self.print_txt("Mensaje AND1")
                #actualizo la fila de la matriz de AND1          
                row_num = int(mensaje [20:24],2)
                col_num = int(mensaje [35:40],2)
                indice = 0
                caracter_bin = mensaje[41: 48] #primer caracter recibido
                #lleno la matriz_AND con los caracteres recibidos, hasta recibir ETX o llegar al final del mensaje
                while caracter_bin != "0000011" and indice<32:     #ETX: End of Text (se termina la cadena de caracteres)
                # ojo, me pueden mandar info erronea, tengo que descartar el mensaje !!! controlar que no se me quede fuera de rango.
                    if col_num < 32:   # recibo de a una fila por vez
                        try:        #este try cae en except cuando el caracter recibido no es valido -> la info que me llega es erronea
                            self.matriz_AND1 [row_num][col_num] = self.lista_caracteres_AND [int(caracter_bin, 2)-32]
                            col_num += 1
                            indice += 1
                            caracter_bin = mensaje [41+8*indice : 48+8*indice]
                        except:
                            #print("caracter incorrecto")
                            break    
                    else:
                        #print("Numero de columna incorrecta")
                        break  
                if row_num == 15:   #en los mensajes AND1 con info de la fila 15 viene la posicion del asterisco en la palabra 15, del bit 23 al 17!
                    nro_col_asterisco = int(mensaje[339:344],2)
                    self.matriz_AND1[row_num][nro_col_asterisco] = "*"
                    #print("Nro columna asterisco: ",nro_col_asterisco)

                #envio la matriz al objeto AND1 para que actualice la pantalla
                self.gui.get_matrizAND1(self.matriz_AND1)
                try:
                    self.gui.fn_actualizar_AND1(self.matriz_AND1)
                except:
                    #print("Abrir pantalla AND1")
                    pass

            elif device_add == "0011":   #mensaje de la AND2
                #print("Mensaje de la AND2")
                #self.print_txt("Mensaje AND2")
                #actualizo la fila de la matriz de AND2          
                row_num = int(mensaje [20:24],2)
                col_num = int(mensaje [35:40],2)
                indice = 0
                caracter_bin = mensaje[41: 48] #primer caracter recibido
                #lleno la matriz_AND con los caracteres recibidos, hasta recibir ETX o llegar al final del mensaje
                while caracter_bin != "0000011" and indice<32:     #ETX: End of Text (se termina la cadena de caracteres)
                # ojo, me pueden mandar info erronea, tengo que descartar el mensaje !!! controlar que no se me quede fuera de rango.
                    if col_num < 32:   # recibo de a una fila por vez
                        try:        #este try cae en except cuando el caracter recibido no es valido -> la info que me llega es erronea
                            self.matriz_AND2 [row_num][col_num] = self.lista_caracteres_AND [int(caracter_bin, 2)-32]
                            col_num += 1
                            indice += 1
                            caracter_bin = mensaje [41+8*indice : 48+8*indice]
                        except:
                            #print("caracter incorrecto")
                            break   
                    else:
                        #print("Numero de columna incorrecta")
                        break   
                if row_num == 15:   #en los mensajes AND1 con info de la fila 15 viene la posicion del asterisco en la palabra 15, del bit 23 al 17!
                    nro_col_asterisco = int(mensaje[339:344],2)
                    self.matriz_AND2[row_num][nro_col_asterisco] = "*"
                    
                    #print("Nro columna asterisco: ",nro_col_asterisco)      
                #envio la matriz al objeto AND1 para que actualice la pantalla
                self.gui.get_matrizAND2(self.matriz_AND2)
                try:
                    self.gui.fn_actualizar_AND2(self.matriz_AND2)
                except:
                    #print("Abrir pantalla AND1")
                    pass
                    
            else:
                print("no entro a ningun device address")

        elif device_add == "0100": #mensaje del DCL CONC -> recibo el ACK del estado del CONC
            #nro_sec_conc_recibido = nro_sec_bin     #numero de secuencia del ACK desl estado del CONC recibido
            self.esperando_ACK_CONC = False
            #print("Llego ACK de la FPGA")
            """
            self.nro_secuencia += 1
            """
        else:
            print("el device address recibido no es valido")

    def decodificar_msj_LPD(self):
        """
        self.lista_AB1 = []     #vacio las listas porque llega info nueva
        self.lista_AB2 = []     # 
        self.lista_AB3 = []     # 
        """
        #if len(self.mensajes_LPD) > 0:
        while len(self.mensajes_LPD) > 0:
            mensaje = self.mensajes_LPD[0]
            del(self.mensajes_LPD[0])       #elimino el elemento de la lista ya tomado.
            leng = round(len(mensaje)/24)   #cantidad de palabras dentro del mensaje
            i = 0
            contador_padding = 0        #variable que permite dejar de decodificar el mensaje LPD cuando recibe 10 mensajes seguidos con padding (para optimizar la recepcion)
            while i < leng:
                lista_aux = []      #lista auxiliar donde voy guardando los datos que me llegan
                identificador = mensaje[20+24*i: 24+24*i]    #tomo los ultimos 4 bits de cada palabra
                if identificador == "0000":     #si el identificador es "0000", quiere decir que la palabra corresponde al relleno del mensaje (no aporta valor)
                    if contador_padding == 9:
                        i = leng                #si me llega relleno, salgo del while
                    else:
                        contador_padding += 1   
                #----- mensaje AB1 -----#   Picture off centre
                elif identificador == "1001": 
                    #print("Es un mensaje AB1")
                    #self.print_txt("    Mensaje AB1")
                    if mensaje [19+24*i] == "1": #si el bit 05 es 1: las coordenadas son validas
                        #1  COORDENADA "X"  
                        coord_x = round(self.gui.binario_2_int(mensaje[0+24*i : 17+24*i])*256/65535,2)      #pasaje palabra binaria a entero -> entero. max (65535 equivalente a 256 DM.)
                        i += 1
                        #2  COORDENADA "Y"  
                        coord_y = round(self.gui.binario_2_int(mensaje[0+24*i : 17+24*i])*256/65535,2)
                        i += 1
                    
                        lista_aux.append(coord_x)
                        lista_aux.append(coord_y)
                        self.lista_AB1.append(lista_aux)
                        lista_aux = []
                    else:   #si las coordenadas no son validas, solo incremento la variable i
                        i += 2
                    self.graficar_LPD = True    #solo se grafica la info recibida en la LPD cuando llega un mensaje AB1, sino se acumula la info de los mensasjes AB2 y AB3 en sus respectivas listas

                #----- mensaje AB2 -----#   Marker Message
                elif identificador == "0001":
                    #print("Es un mensaje AB2")
                    #self.print_txt("    Mensaje AB2")
                    #if mensaje [19+24*i] == "1": #si el bit 05 es 1: el Marker Message es valido, se muestra
                    v_valid = mensaje [19+24*i]     #variable que guarda si el marcador es valido o no

                    #1  MARKER "X"
                    marker_x = round(self.gui.binario_2_int(mensaje[0+24*i : 17+24*i])*256/65535,2)
                    PV = mensaje [18+24*i]
                    LS = mensaje [17+24*i]
                    """
                    if LS == "0":
                        self.label_selection = True
                    else:
                        self.label_selection = False
                    """
                    i += 1

                    #2  MARKER "Y"
                    marker_y = round(self.gui.binario_2_int(mensaje[0+24*i : 17+24*i])*256/65535,2)
                    AP = mensaje [18+24*i]
                    i += 1

                    #----- implemento cuadro PV y AP -----
                    if PV == "0" and AP == "0":     #muestro el punto y fin del mensaje
                        lista_aux.append(marker_x)
                        lista_aux.append(marker_y)
                        lista_aux.append("muestro")
                        fin_mensaje = True
                    elif PV == "0" and AP == "1":   #muestro el punto y siguen las palabras trios
                        lista_aux.append(marker_x)
                        lista_aux.append(marker_y)
                        lista_aux.append("muestro")
                        fin_mensaje = False
                    else:   #PV == "1" and AP == "1" --> no muestro el punto y siguen las palabras trio
                        lista_aux.append(marker_x)
                        lista_aux.append(marker_y)
                        lista_aux.append("nomuestro")
                        fin_mensaje = False

                    #3 Caracteres Marker Message
                    if fin_mensaje == False:
                        indice = 0
                        lista_aux2 = []     #lista donde voy poniendo los simbolos que van llegando
                        simbolo_bin = mensaje [1+24*i:8+24*i]
                        while simbolo_bin != "0010111":  #si el simbolo no es EOMM: ENd of Message Marker:
                            #logica de que hacer con los simbolos: si es un caracter lo agrego a la lista. si es un dibujo, paso el numero y en la clase radar_widget los dibujo
                            if simbolo_bin == "0000000":
                                lista_aux2.append(" ")
                            else:
                                simbolo = int(simbolo_bin, 2)       #obtengo el numero decimal 
                                if simbolo > 39 and simbolo < 91:
                                    lista_aux2.append (self.lista_caracteres_AND[simbolo-32])
                                else:
                                    lista_aux2.append(simbolo)
                            indice += 1
                            simbolo_bin = mensaje [1+24*i+8*indice: 8+24*i+8*indice]
                            #funcion para mostrar todo esto en la LPD. 
                        lista_aux.append(lista_aux2)
                        i += int((indice+1)/3)

                    if v_valid == "1":       #si V = 1: el marcador es valido y se muestra, sino no se hace nada.
                        #self.lista_AB2.append(lista_aux)
                        self.lista_AB2.append(lista_aux)
                    
                    lista_aux = []

                #----- mensaje AB3 -----#
                elif identificador == "0101":  
                    #print("Es un mensaje AB3")
                    #self.print_txt("    Mensaje AB3")
                    if mensaje [19+24*i] == "1":     #si el bit 5 de la palabra AB3#1 es 1: el cursor es valido
                        # CURSOR ANGLE
                        cursor_angle = round(self.gui.binario_2_int(mensaje[0+24*i : 12+24*i])*180/2048,2)
                        i += 1

                        #2: CURSOR LENGTH
                        cursor_length = round(self.gui.binario_2_int(mensaje[0+24*i : 17+24*i])*256/65535, 2)
                        cursor_type = int(mensaje[17+24*i : 20+24*i], 2)
                        i += 1

                        #3: CURSOR ORIGIN "X"
                        cursor_origin_x = round(self.gui.binario_2_int(mensaje[0+24*i : 17+24*i])*256/65535, 2)
                        i += 1

                        #4: CURSOR ORIGIN "Y"
                        cursor_origin_y = round(self.gui.binario_2_int(mensaje[0+24*i : 17+24*i])*256/65535, 2)
                        i +=1

                        lista_aux.append(cursor_angle)
                        lista_aux.append(cursor_length)
                        lista_aux.append(cursor_type)
                        lista_aux.append(cursor_origin_x)
                        lista_aux.append(cursor_origin_y)
                        self.lista_AB3.append(lista_aux)
                        lista_aux = []
                    else:
                        i += 4
                
                else:   #palabra incorrecta, no hago nada e incremento i. Nunca deberia llegar a esta instancia pero es por si hay un error en el envio/recepcion del mensaje
                    i += 1

            self.dec_msj_LPD = False    #que no entre a decodificar_msj_LPD() hasta que no llegue otro mensaje LPD (por el Timer)         
            
            if len(self.mensajes_LPD) > 0:         #si la lista de mensajes todavia tiene uno por decodificar, lo decodifico
               pass
               # self.decodificar_msj_LPD()

            # llamo al metodo graficar_info_LPD() para mostrar la info en el radar (siempre y cuando haya llegado un mensaje AB1):
            if self.graficar_LPD == True:
            
                #comento esta linea para que no grafique, y probar que la counicacion funciona
                self.gui.graficar_info_LPD(self.lista_AB1, self.lista_AB2, self.lista_AB3)
                
                #self.print_txt(str(self.lista_AB1))
                #self.print_txt(str(self.lista_AB2))
                #self.print_txt(str(self.lista_AB3))
                
                self.lista_AB1 = []     #vacio las listas para completarlas con la info nueva que recibiremos de la FPGA
                self.lista_AB2 = []
                self.lista_AB3 = []
                self.graficar_LPD = False 
            
            #self.dec_msj_LPD = False    #que no entre a decodificar_msj_LPD() hasta que no llegue otro mensaje LPD (por el Timer)             

    
    def timer_interrupt (self):
        #print("ocurre interrupcion del timer")
        self.reenviar_estado_CONC()
        t = threading.Timer(self.tiempo_interruptor, self.timer_interrupt)
        t.start()

    def timer_interrupt_lpd (self):
        #print("ocurre interrupcion del timer")
        if self.dec_msj_LPD == True:
            self.decodificar_msj_LPD()
        t = threading.Timer(self.tiempo_interruptor, self.timer_interrupt_lpd)
        t.start()

    def init_threads(self):
        global thread_server
        global thread_ack_CONC
        global thread_listener


        """
        thread_ack_CONC = threading.Thread(target = self.reenviar_estado_CONC)
        thread_ack_CONC.start()     #start hilo de la funcion reenviar_estado_CONC
        """
        #thread_listener = threading.Thread(target = self.thread_teclado)
        #thread_listener.start()
        timer_int = threading.Timer(self.tiempo_interruptor, self.timer_interrupt)
        timer_int.start()

        timer_int_lpd = threading.Timer(self.tiempo_interruptor, self.timer_interrupt_lpd)
        timer_int_lpd.start()

        #hilo que maneja el teclado. llama a la funcion self.gui.tecla_apretada_mik cuando se preciona una tecla.
        thread_listener = keyboard.Listener(on_press = self.gui.tecla_apretada_mik_L)
        thread_listener.start()

        thread_server = threading.Thread(target = self.receiveServer)
        thread_server.start()       #start hilo de la funcion receiveServer.

        

if __name__ == '__main__':      
    app = QApplication(sys.argv)
    GUI = TDC_logica()
    GUI.init_threads()
    sys.exit(app.exec_()) 