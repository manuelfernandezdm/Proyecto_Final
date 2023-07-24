from radarwidget import RadarWidget     #importo el widget "radarwidget" (clase modificada por mi)
import os,sys,inspect 
from PyQt5 import QtCore, QtGui, QtWidgets, uic        #uic: funcion encargada de cargar la interfaz grafica
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget     
from PyQt5.QtGui import *
import numpy as np 
import math
#from AND1_2 import Ui_AND1        #importo la AND1      #AND1 achicada
#from AND1_3 import Ui_AND1
#from AND2_2 import Ui_AND2        #importo la AND2      #AND2 achicada
#from AND_4 import Ui_AND
from AND_5 import Ui_AND

from os import environ

from pynput.keyboard import Key #, Listener   #para manejar las entradas del teclado
#from pynput import keyboard

class TDC_GUI(QtWidgets.QMainWindow):     #QMainWindow: ventana ya creada en el Qt Design

    def __init__(self):     #metodo que inicializa la clase
        super().__init__()
        uic.loadUi("TDC_3_aux2.ui", self)       #abrimos la interfaz creada. ("archivo de la interfaz",self)
        #self.suppress_qt_warnings()
        #self.cerrar_TDC_logica = False
        """
        variales de la clase TDC_GUI para poder recolectar y enviar
        el estado del DCL CONC
        """
        self.range_scale = "111"        #valor inicial: 256 DM (escala maxima)
        self.disp_select_AIR = "0"
        self.disp_select_SURF = "0"
        self.disp_select_SUBSURF = "0"
        #self.display_selection = "00000" :
        self.ref_pos = "0"
        self.bear_sel = "0"
        self.link_sel = "0"
        self.warf_sel = "0"
        self.fig = "0"

        #### BORRAR ####
        self.lista_dx = []
        self.lista_dy = []
        ################


        self.threat_ass = "00100"       #valor inicial en 6 minutos
        self.mode1_L = "00"       #cu or cent off/cu or cent
        self.mode2_L = "000"       #off cent/ cent/ reset obm
        self.mode3_L = "0"       #data request
        self.true_motion = "0"           #CB1#2: true motion (bit 18)
        self.own_cursor = "0"    #own cursor(bit 17)
        self.mode1_R = "00"
        self.mode2_R = "000"
        self.mode3_R = "0"
        self.syst_alarm = "0"        #CB1#2 system alarm(bit 10)
        self.radar_recorder = "0"    #CB!#2 radar recorder (bit9)
        self.mik_L = []
        self.mik_l = "01000000"
        self.mik_R = []
        self.mik_r = "01000000"
        self.qek_L = []
        self.qek_R = []
        self.icm_L = "000"
        self.overlay_L = "0001"     #inicia en overlay: AAW/AWW
        self.icm_R = "000"
        self.overlay_R = "0011"     #inicia en overlay: AIR/EW/IFF
        self.handwheel_DA = []
        self.handwheel_da = "00000000"
        self.handwheel_DR = []
        self.handwheel_dr = "00000000"
        self.rollball_L_DX = []
        self.rollball_L_dx = "00000000"
        self.rollball_L_DY = []
        self.rollball_L_dy = "00000000"
        self.rollball_R_DX = []
        self.rollball_R_dx = "00000000"
        self.rollball_R_DY = []
        self.rollball_R_dy = "00000000"

        #variables de las AND
        self.matriz_vacia = np.full((16,32)," ")        #matriz de la AND auxiliar
        #self.matriz_vacia = np.full((17,32)," ")        #matriz de la AND auxiliar
        self.matriz_AND1 = self.matriz_vacia                 #matriz de la AND1
        self.matriz_AND2 = self.matriz_vacia                 #matriz de la AND2

        self.rolling_o_handwheel = "rolling"        #variable que me permite saber cual de los dos esta activado
        #variables que permiten el manejo de los delta handwheel y rolling ball:
        self.coord_rolling_L = [0, 0]       #guardo las coordenadas del punto actual de la rolling_L
        self.coord_handwheel = [0, 0]       #coordenadas en polares, [angulo, radio]

        #variable para graficar menos mensajes LPD
        self.nro_msj_lpd = 2
        self.contador_lpd = 0

        #   ----- SETEO EL ESTADO INICIAL DE LOS BOTONES (PARTE GRAFICA) -----  #
        self.btn_rolling_ball.setEnabled(False)     #comienzo apretado
        self.btn_handwheel.setEnabled(True)
            #RANGE SCALE:
        self.btn_rsl_2.setEnabled(True)
        self.btn_rsl_4.setEnabled(True)
        self.btn_rsl_8.setEnabled(True)
        self.btn_rsl_16.setEnabled(True)
        self.btn_rsl_32.setEnabled(True)
        self.btn_rsl_64.setEnabled(True)
        self.btn_rsl_128.setEnabled(True)
        self.btn_rsl_256.setEnabled(False)      #comienza apretado
            #ICM-L
        self.btn_icml_1.setEnabled(False)       #comienza apretado
        self.btn_icml_2.setEnabled(True)
        self.btn_icml_3.setEnabled(True)
        self.btn_icml_4.setEnabled(True)
        self.btn_icml_5.setEnabled(True)
        self.btn_icml_6.setEnabled(True)
        self.btn_icml_7.setEnabled(True)       
            #ICM-R
        self.btn_icmr_1.setEnabled(False)       #comienza apretado
        self.btn_icmr_2.setEnabled(True)
        self.btn_icmr_3.setEnabled(True)
        self.btn_icmr_4.setEnabled(True)
        self.btn_icmr_5.setEnabled(True)
        self.btn_icmr_6.setEnabled(True)
        self.btn_icmr_7.setEnabled(True)       
            #THREAT ASSESSMENT
        self.btn_tal_12sec.setEnabled(False)
        self.btn_tal_30sec.setEnabled(True)
        self.btn_tal_6min.setEnabled(True)
        self.btn_tal_15min.setEnabled(True)
        self.btn_tal_reset.setEnabled(True)
            #OVERLAY-L
        self.btn_overlayl_aaw.setEnabled(False)
        self.btn_overlayl_asw.setEnabled(True)
        self.btn_overlayl_air_ew_iff.setEnabled(True)
        self.btn_overlayl_surface.setEnabled(True)
            #OVERLAY-R
        self.btn_overlayr_aaw.setEnabled(True)
        self.btn_overlayr_asw.setEnabled(True)
        self.btn_overlayr_air_ew_iff.setEnabled(False)
        self.btn_overlayr_surface.setEnabled(True)

        #   ----- SETEO QUE BOTONES MUESTRAN SI ESTAN APRETADOS O NO (PARTE GRAFICA) -----  #
            #DISPLAY SELECTION
        self.btn_ds_air.setCheckable(True)
        self.btn_ds_surf.setCheckable(True)
        self.btn_ds_subsurf.setCheckable(True)
            #DISPLAY MODE
        self.btn_dml_hm.setCheckable(True)          #no funciona
        self.btn_dml_rr.setCheckable(True)          #no funciona
        self.btn_dml_owncursor.setCheckable(True)
        self.btn_dml_symblarge.setCheckable(True)   #no funciona
        self.btn_dml_tm.setCheckable(True)
        self.btn_dml_emrg.setCheckable(True)        #no funciona
        #self.btn_dml_systalarm.setCheckable(True)  #syst alarm no es tecla, es pulsador
            #DISPLAY SELECTION
        self.btn_ds_air.setCheckable(True)
        self.btn_ds_surf.setCheckable(True)
        self.btn_ds_subsurf.setCheckable(True)      
        self.btn_ds_refpost.setCheckable(True)      
        self.btn_ds_bearsel.setCheckable(True)      
        self.btn_ds_linksel.setCheckable(True)      
        self.btn_ds_warfsel.setCheckable(True)     
        self.btn_ds_fig.setCheckable(True)          
            #LABEL SELECTION
        self.btn_lsl_ms.setCheckable(True)
        self.btn_lsl_trkm.setCheckable(True)
        self.btn_lsl_amplinfo.setCheckable(True)
        self.btn_lsl_linkstat.setCheckable(True)
        self.pushButton_68.setCheckable(True)       #track number


        """
        self.btn_datreql_1.setCheckable(True)
        self.btn_datreql_2.setCheckable(False)
        self.btn_datreql_3.setCheckable(True)
        self.btn_qekl20.setCheckable(True)
        self.estado_prueba = False
        """

        #-----------------------

        #conecto los botones con sus respectivas funciones:
        
            #AND1:
        self.btn_AND1.clicked.connect(self.fn_abrir_AND1)
            #AND2:
        self.btn_AND2.clicked.connect(self.fn_abrir_AND2)
        
            #QEK_L:
        self.btn_qekl20.clicked.connect(lambda: self.fn_returnCONC())
        #self.btn_qekl20.clicked.connect(lambda: self.fn_QEK_L(20))
        self.btn_qekl21.clicked.connect(lambda: self.fn_QEK_L(21))
        self.btn_qekl22.clicked.connect(lambda: self.fn_QEK_L(22))
        self.btn_qekl23.clicked.connect(lambda: self.fn_QEK_L(23))
        self.btn_qekl24.clicked.connect(lambda: self.fn_QEK_L(24))
        self.btn_qekl25.clicked.connect(lambda: self.fn_QEK_L(25))
        self.btn_qekl26.clicked.connect(lambda: self.fn_QEK_L(26))
        self.btn_qekl27.clicked.connect(lambda: self.fn_QEK_L(27))
        self.btn_qekl30.clicked.connect(lambda: self.fn_QEK_L(30))
        self.btn_qekl31.clicked.connect(lambda: self.fn_QEK_L(31))
        self.btn_qekl32.clicked.connect(lambda: self.fn_QEK_L(32))
        self.btn_qekl33.clicked.connect(lambda: self.fn_QEK_L(33))
        self.btn_qekl34.clicked.connect(lambda: self.fn_QEK_L(34))
        self.btn_qekl35.clicked.connect(lambda: self.fn_QEK_L(35))
        self.btn_qekl36.clicked.connect(lambda: self.fn_QEK_L(36))
        self.btn_qekl37.clicked.connect(lambda: self.fn_QEK_L(37))
        self.btn_qekl40.clicked.connect(lambda: self.fn_QEK_L(40))
        self.btn_qekl41.clicked.connect(lambda: self.fn_QEK_L(41))
        self.btn_qekl42.clicked.connect(lambda: self.fn_QEK_L(42))
        self.btn_qekl43.clicked.connect(lambda: self.fn_QEK_L(43))
        self.btn_qekl44.clicked.connect(lambda: self.fn_QEK_L(44))
        self.btn_qekl45.clicked.connect(lambda: self.fn_QEK_L(45))
        self.btn_qekl46.clicked.connect(lambda: self.fn_QEK_L(46))
        self.btn_qekl47.clicked.connect(lambda: self.fn_QEK_L(47))
        self.btn_qekl50.clicked.connect(lambda: self.fn_QEK_L(50))
        self.btn_qekl51.clicked.connect(lambda: self.fn_QEK_L(51))
        self.btn_qekl52.clicked.connect(lambda: self.fn_QEK_L(52))
        self.btn_qekl53.clicked.connect(lambda: self.fn_QEK_L(53))
        self.btn_qekl54.clicked.connect(lambda: self.fn_QEK_L(54))
        self.btn_qekl55.clicked.connect(lambda: self.fn_QEK_L(55))
        self.btn_qekl56.clicked.connect(lambda: self.fn_QEK_L(56))
        self.btn_qekl57.clicked.connect(lambda: self.fn_QEK_L(57))
            #ICM_L:
        self.btn_icml_1.clicked.connect(lambda: self.fn_ICM_L(1))
        self.btn_icml_2.clicked.connect(lambda: self.fn_ICM_L(2))
        self.btn_icml_3.clicked.connect(lambda: self.fn_ICM_L(3))
        self.btn_icml_4.clicked.connect(lambda: self.fn_ICM_L(4))
        self.btn_icml_5.clicked.connect(lambda: self.fn_ICM_L(5))
        self.btn_icml_6.clicked.connect(lambda: self.fn_ICM_L(6))
        self.btn_icml_7.clicked.connect(lambda: self.fn_ICM_L(7))
            #TA_L:  Threat Assessment
        self.btn_tal_12sec.clicked.connect(lambda: self.fn_TA_L(1))
        self.btn_tal_30sec.clicked.connect(lambda: self.fn_TA_L(2))
        self.btn_tal_6min.clicked.connect(lambda: self.fn_TA_L(3))
        self.btn_tal_15min.clicked.connect(lambda: self.fn_TA_L(4))
        self.btn_tal_reset.clicked.connect(lambda: self.fn_TA_L(5))
            #RS_L:  #RangeScale
        self.btn_rsl_2.clicked.connect(lambda: self.fn_RS_L(1))
        self.btn_rsl_4.clicked.connect(lambda: self.fn_RS_L(2))
        self.btn_rsl_8.clicked.connect(lambda: self.fn_RS_L(3))
        self.btn_rsl_16.clicked.connect(lambda: self.fn_RS_L(4))
        self.btn_rsl_32.clicked.connect(lambda: self.fn_RS_L(5))
        self.btn_rsl_64.clicked.connect(lambda: self.fn_RS_L(6))
        self.btn_rsl_128.clicked.connect(lambda: self.fn_RS_L(7))
        self.btn_rsl_256.clicked.connect(lambda: self.fn_RS_L(8))
            #QEK_R:
        self.btn_qekr20.clicked.connect(lambda: self.fn_QEK_R(20))
        self.btn_qekr21.clicked.connect(lambda: self.fn_QEK_R(21))
        self.btn_qekr22.clicked.connect(lambda: self.fn_QEK_R(22))
        self.btn_qekr23.clicked.connect(lambda: self.fn_QEK_R(23))
        self.btn_qekr24.clicked.connect(lambda: self.fn_QEK_R(24))
        self.btn_qekr25.clicked.connect(lambda: self.fn_QEK_R(25))
        self.btn_qekr26.clicked.connect(lambda: self.fn_QEK_R(26))
        self.btn_qekr27.clicked.connect(lambda: self.fn_QEK_R(27))
        self.btn_qekr30.clicked.connect(lambda: self.fn_QEK_R(30))
        self.btn_qekr31.clicked.connect(lambda: self.fn_QEK_R(31))
        self.btn_qekr32.clicked.connect(lambda: self.fn_QEK_R(32))
        self.btn_qekr33.clicked.connect(lambda: self.fn_QEK_R(33))
        self.btn_qekr34.clicked.connect(lambda: self.fn_QEK_R(34))
        self.btn_qekr35.clicked.connect(lambda: self.fn_QEK_R(35))
        self.btn_qekr36.clicked.connect(lambda: self.fn_QEK_R(36))
        self.btn_qekr37.clicked.connect(lambda: self.fn_QEK_R(37))
        self.btn_qekr40.clicked.connect(lambda: self.fn_QEK_R(40))
        self.btn_qekr41.clicked.connect(lambda: self.fn_QEK_R(41))
        self.btn_qekr42.clicked.connect(lambda: self.fn_QEK_R(42))
        self.btn_qekr43.clicked.connect(lambda: self.fn_QEK_R(43))
        self.btn_qekr44.clicked.connect(lambda: self.fn_QEK_R(44))
        self.btn_qekl45.clicked.connect(lambda: self.fn_QEK_R(45))
        self.btn_qekr46.clicked.connect(lambda: self.fn_QEK_R(46))
        self.btn_qekr47.clicked.connect(lambda: self.fn_QEK_R(47))
        self.btn_qekr50.clicked.connect(lambda: self.fn_QEK_R(50))
        self.btn_qekr51.clicked.connect(lambda: self.fn_QEK_R(51))
        self.btn_qekr52.clicked.connect(lambda: self.fn_QEK_R(52))
        self.btn_qekr53.clicked.connect(lambda: self.fn_QEK_R(53))
        self.btn_qekr54.clicked.connect(lambda: self.fn_QEK_R(54))
        self.btn_qekr55.clicked.connect(lambda: self.fn_QEK_R(55))
        self.btn_qekr56.clicked.connect(lambda: self.fn_QEK_R(56))
        self.btn_qekr57.clicked.connect(lambda: self.fn_QEK_R(57))
            #ICM_R:
        self.btn_icmr_1.clicked.connect(lambda: self.fn_ICM_R(1))
        self.btn_icmr_2.clicked.connect(lambda: self.fn_ICM_R(2))
        self.btn_icmr_3.clicked.connect(lambda: self.fn_ICM_R(3))
        self.btn_icmr_4.clicked.connect(lambda: self.fn_ICM_R(4))
        self.btn_icmr_5.clicked.connect(lambda: self.fn_ICM_R(5))
        self.btn_icmr_6.clicked.connect(lambda: self.fn_ICM_R(6))
        self.btn_icmr_7.clicked.connect(lambda: self.fn_ICM_R(7))
            #DATREQ_L
        self.btn_datreql_1.clicked.connect(lambda: self.fn_DATREQ1_L(1))
        self.btn_datreql_2.clicked.connect(lambda: self.fn_DATREQ1_L(2))
        self.btn_datreql_3.clicked.connect(lambda: self.fn_DATREQ2_L(3))
        self.btn_datreql_4.clicked.connect(lambda: self.fn_DATREQ2_L(4))
        self.btn_datreql_5.clicked.connect(lambda: self.fn_DATREQ2_L(5))
        self.btn_datreql_6.clicked.connect(lambda: self.fn_DATREQ3_L(6))
             #DATREQ_R
        self.btn_datreqr_1.clicked.connect(lambda: self.fn_DATREQ1_R(1))
        self.btn_datreqr_2.clicked.connect(lambda: self.fn_DATREQ1_R(2))
        self.btn_datreqr_3.clicked.connect(lambda: self.fn_DATREQ2_R(3))
        self.btn_datreqr_4.clicked.connect(lambda: self.fn_DATREQ2_R(4))
        self.btn_datreqr_5.clicked.connect(lambda: self.fn_DATREQ2_R(5))
        self.btn_datreqr_6.clicked.connect(lambda: self.fn_DATREQ3_R(6))
            #DSelect_R
        self.btn_ds_air.clicked.connect(lambda: self.fn_DSelect_R(1))
        self.btn_ds_surf.clicked.connect(lambda: self.fn_DSelect_R(2))
        self.btn_ds_subsurf.clicked.connect(lambda: self.fn_DSelect_R(3))
        self.btn_ds_refpost.clicked.connect(lambda: self.fn_DSelect_R(4))
        self.btn_ds_bearsel.clicked.connect(lambda: self.fn_DSelect_R(5))
        self.btn_ds_linksel.clicked.connect(lambda: self.fn_DSelect_R(6))
        self.btn_ds_warfsel.clicked.connect(lambda: self.fn_DSelect_R(7))
        self.btn_ds_fig.clicked.connect(lambda: self.fn_DSelect_R(8))
            #Rolling y Handwheel
        self.btn_rolling_ball.clicked.connect(lambda: self.fn_activar_rolling())
        self.btn_handwheel.clicked.connect(lambda: self.fn_activar_handwheel())
            #Overlat L
        self.btn_overlayl_aaw.clicked.connect(lambda: self.fn_overlay_L(1))
        self.btn_overlayl_asw.clicked.connect(lambda: self.fn_overlay_L(2))
        self.btn_overlayl_air_ew_iff.clicked.connect(lambda: self.fn_overlay_L(3))
        self.btn_overlayl_surface.clicked.connect(lambda: self.fn_overlay_L(4))
            #Overlay R
        self.btn_overlayr_aaw.clicked.connect(lambda: self.fn_overlay_R(1))
        self.btn_overlayr_asw.clicked.connect(lambda: self.fn_overlay_R(2))
        self.btn_overlayr_air_ew_iff.clicked.connect(lambda: self.fn_overlay_R(3))
        self.btn_overlayr_surface.clicked.connect(lambda: self.fn_overlay_R(4))
            #Boton EXIT
        self.btn_EXIT.clicked.connect(lambda: self.fn_cerrar_programa())
            #MIK - L
                #parte izquierda
        self.mik_l_0.clicked.connect(lambda: self.fn_mik_L(0))
        self.mik_l_1.clicked.connect(lambda: self.fn_mik_L(1))
        self.mik_l_2.clicked.connect(lambda: self.fn_mik_L(2))
        self.mik_l_3.clicked.connect(lambda: self.fn_mik_L(3))
        self.mik_l_4.clicked.connect(lambda: self.fn_mik_L(4))
        self.mik_l_5.clicked.connect(lambda: self.fn_mik_L(5))
        self.mik_l_6.clicked.connect(lambda: self.fn_mik_L(6))
        self.mik_l_7.clicked.connect(lambda: self.fn_mik_L(7))
        self.mik_l_8.clicked.connect(lambda: self.fn_mik_L(8))
        self.mik_l_9.clicked.connect(lambda: self.fn_mik_L(9))
        self.mik_l_punto.clicked.connect(lambda: self.fn_mik_L(10))
        self.mik_l_rb.clicked.connect(lambda: self.fn_mik_L(11))
        self.mik_l_mas.clicked.connect(lambda: self.fn_mik_L(12))
        self.mik_l_menos.clicked.connect(lambda: self.fn_mik_L(13))
                #parte derecha
        self.mik_l_a.clicked.connect(lambda: self.fn_mik_L(20))
        self.mik_l_b.clicked.connect(lambda: self.fn_mik_L(21))
        self.mik_l_c.clicked.connect(lambda: self.fn_mik_L(22))
        self.mik_l_d.clicked.connect(lambda: self.fn_mik_L(23))
        self.mik_l_e.clicked.connect(lambda: self.fn_mik_L(24))
        self.mik_l_f.clicked.connect(lambda: self.fn_mik_L(25))
        self.mik_l_g.clicked.connect(lambda: self.fn_mik_L(26))
        self.mik_l_h.clicked.connect(lambda: self.fn_mik_L(27))
        self.mik_l_i.clicked.connect(lambda: self.fn_mik_L(28))
        self.mik_l_j.clicked.connect(lambda: self.fn_mik_L(29))
        self.mik_l_k.clicked.connect(lambda: self.fn_mik_L(30))
        self.mik_l_l.clicked.connect(lambda: self.fn_mik_L(31))
        self.mik_l_m.clicked.connect(lambda: self.fn_mik_L(32))
        self.mik_l_n.clicked.connect(lambda: self.fn_mik_L(33))
        self.mik_l_o.clicked.connect(lambda: self.fn_mik_L(34))
        self.mik_l_p.clicked.connect(lambda: self.fn_mik_L(35))
        self.mik_l_q.clicked.connect(lambda: self.fn_mik_L(36))
        self.mik_l_r.clicked.connect(lambda: self.fn_mik_L(37))
        self.mik_l_s.clicked.connect(lambda: self.fn_mik_L(38))
        self.mik_l_t.clicked.connect(lambda: self.fn_mik_L(39))
        self.mik_l_u.clicked.connect(lambda: self.fn_mik_L(40))
        self.mik_l_v.clicked.connect(lambda: self.fn_mik_L(41))
        self.mik_l_w.clicked.connect(lambda: self.fn_mik_L(42))
        self.mik_l_x.clicked.connect(lambda: self.fn_mik_L(43))
        self.mik_l_y.clicked.connect(lambda: self.fn_mik_L(44))
        self.mik_l_z.clicked.connect(lambda: self.fn_mik_L(45))

        self.mik_l_dr_obm.clicked.connect(lambda: self.fn_mik_L(50))
        self.mik_l_dr_ocm.clicked.connect(lambda: self.fn_mik_L(51))
        self.mik_l_dr_warn.clicked.connect(lambda: self.fn_mik_L(52))
        self.mik_l_wipe_warn.clicked.connect(lambda: self.fn_mik_L(53))
        self.mik_l_space_bwd.clicked.connect(lambda: self.fn_mik_L(54))
        self.mik_l_next_field.clicked.connect(lambda: self.fn_mik_L(55))
        self.mik_l_space_fwd.clicked.connect(lambda: self.fn_mik_L(56))
        self.mik_l_execute.clicked.connect(lambda: self.fn_mik_L(57))
        self.mik_l_space.clicked.connect(lambda: self.fn_mik_L(58))
        self.mik_l_erase.clicked.connect(lambda: self.fn_mik_L(59))
        self.mik_l_sel.clicked.connect(lambda: self.fn_mik_L(60))
                                                                                                                                                                                                                                                                                                                      #G          #H         #I       #J          #K          #L          M           N          O        P           Q           R       S           T           U           V       W           X          Y           Z                                 
        self.lista_mik = ["00110000","00110001","00110010","00110011","00110100","00110101","00110110","00110111","00111000","00111001","00101110","00100100","00101011","00101101","vacio14","vacio15","vacio16","vacio17","vacio18","vacio19","01000001","01000010","01000011","01000100","01000101","01000110","01000111","01001000","01001001","01001010","01001011","01001100","01001101","01001110","01001111","01010000","01010001","01010010","01010011","01010100","01010101","01010110","01010111","01011000","01011001","01011010","vacio46","vacio47","vacio48","vacio49","00111011","00111100","00111101","00111110","00101100","00100101","00100110","00100011","00100001","00100010","00100000"]
        
        #DISPLAY MODES
        self.btn_dml_hm.clicked.connect(lambda: self.fn_disp_modes_L(1))
        self.btn_dml_rr.clicked.connect(lambda: self.fn_disp_modes_L(2))
        self.btn_dml_owncursor.clicked.connect(lambda: self.fn_disp_modes_L(3))
        self.btn_dml_symblarge.clicked.connect(lambda: self.fn_disp_modes_L(4))
        self.btn_dml_tm.clicked.connect(lambda: self.fn_disp_modes_L(5))
        self.btn_dml_emrg.clicked.connect(lambda: self.fn_disp_modes_L(6))
        self.btn_dml_systalarm.clicked.connect(lambda: self.fn_disp_modes_L(7))


        self.btn_nro_msj_lpd.clicked.connect(self.set_nro_msj_lpd)
    #---------------------------------------------------------------------------
    # aca implemento las funciones correspondientes a los botones de la tactica:
    #---------------------------------------------------------------------------
    """
    def closeEvent (self, event):
        print("cerrando TDC_GUI")
        self.cerrar_TDC_LOGICA = True
    """
    def fn_abrir_AND1(self):        #funcion para abrir la AND1
        self.And1 = QtWidgets.QWidget()
        #self.ui1 = Ui_AND1()
        #self.ui1.setupUi(self.And1)

        self.ui1 = Ui_AND()
        self.ui1.setupUi(self.And1, "AND1")

        self.fn_actualizar_AND1(self.matriz_AND1)
        self.And1.show()

    def fn_abrir_AND2(self):        #funcion para abrir la AND2
        self.And2 = QtWidgets.QWidget()
        #self.ui2 = Ui_AND2()
        #self.ui2.setupUi(self.And2) 

        self.ui2 = Ui_AND()
        self.ui2.setupUi(self.And2, "AND2") 

        self.fn_actualizar_AND2(self.matriz_AND2)
        self.And2.show()

    def fn_actualizar_AND1(self, matriz):   #funcion que recibe la matriz AND1 de TDC_logica y actualiza la AND1
        self.ui1.retranslateUi(self.And1, matriz) 
    
    def fn_actualizar_AND2(self, matriz):   #funcion que recibe la matriz AND1 de TDC_logica y actualiza la AND1
        self.ui2.retranslateUi(self.And2, matriz) 

    def get_matrizAND1(self, matriz):       #metodo para guardar la info de la AND1 cuando no esta abierta
        self.matriz_AND1 = matriz

    def get_matrizAND2(self, matriz):       #metodo para guardar la info de la AND2 cuando no esta abierta
        self.matriz_AND2 = matriz
   
    def fn_returnCONC(self):    #funcion auxiliar para ver el estado del DCL CONC en la consola (para control de pruebas locales)
        #estado = self.return_estado_CONC()
        self.return_estado_CONC()
        """
        handwheel = estado [120:136]
        rollball = estado [144:160]
        #print(estado)
        print("HANDWHEEL: ", handwheel)
        print("ROLLBALLL: ", rollball)
        """
    
    def binario_2_int (self,binario):
        if binario[0] == "0":   #numero binario positivo:
            num_int = int(binario,2)
        else:                   #el numero binario es negativo -> complemento A2
            num_bin = ""
            for i in range(len(binario)):  
                if binario[i] == "0":
                    num_bin += "1"
                else:
                    num_bin += "0"
            num_int = (-1)*(int(num_bin,2)+1)   
        return num_int
    
    def int_2_binario (self,entero,bits):
        if entero >= 0:     #numero decimal positivo o igual a 0
            num_bin = "{0:b}".format(entero).zfill(bits)
        else:       #numero decimal negativo
            num_bin_1 = "{0:b}".format(abs(entero)-1).zfill(bits)
            num_bin = ""
            for i in range (len(num_bin_1)):
                if num_bin_1[i] == "0":
                    num_bin += "1"
                else:
                    num_bin += "0"
        return num_bin
    
    def graficar_info_LPD(self, lista1, lista2, lista3):
        if self.contador_lpd < self.nro_msj_lpd:
            self.contador_lpd += 1
        else:
            self.RadarWidget.borrarPuntos()     #limpio el radar
            #self.RadarWidget.set_origen_x_y (lista1)
            self.graficar_marker_message(lista2)
            self.graficar_cursor_message(lista3)
            self.RadarWidget.canvas.draw()      #para graficar la actualizacion en el radar.  
            self.contador_lpd = 0                            
    """
    #   esta parte se descomenta y se comenta la de arriba para las pruebas locales (no tener que mandar 10 mensajes para que se grafique en la LPD)
    def graficar_info_LPD(self, lista1, lista2, lista3):
        self.RadarWidget.borrarPuntos()     #limpio el radar
        self.RadarWidget.set_origen_x_y (lista1)
        self.graficar_marker_message(lista2)
        self.graficar_cursor_message(lista3)
        self.RadarWidget.canvas.draw()      #para graficar la actualizacion en el radar.  
        self.contador_lpd = 0  
    """
    def graficar_marker_message (self, lista):
        self.RadarWidget.graficar_markers(lista)

    def graficar_cursor_message (self, lista):  #llamo a la funcion graficar_cursores de la clase radar widget
        self.RadarWidget.graficar_cursores(lista)
    
    def fn_activar_rolling (self):
        self.btn_rolling_ball.setEnabled(False)
        self.btn_handwheel.setEnabled(True)
        self.rolling_o_handwheel = "rolling"
        print(self.rolling_o_handwheel)

    def fn_activar_handwheel (self):
        self.btn_handwheel.setEnabled(False)
        self.btn_rolling_ball.setEnabled(True)
        self.rolling_o_handwheel = "handwheel"
        print(self.rolling_o_handwheel)
    
    #def agregar_caracter_lista_MIK (self, caracter):
    """
    def mik_to_bin(self, letra=""):       #funcion que transforma el caracter a su valor binario en ASCII. Necesaria para codificar la entrada de los MIKs (teclados)
        letra_dec = ord(letra)
        if letra_dec>53 and letra_dec>132:
            letra_bin = ''.join(format(letra_dec, '08b'))
        else:       #la tecla ingresada no corresponde al MIK:
            letra_bin = "01000000"
        return letra_bin
    """
    #def tecla_apretada_mik_L(self, tecla):  #metodo que es llamado por la clase TDC_logica para pasar la tecla apretada (ya en binario)
    #   self.mik_L.append(tecla)
    """
    codigo que me mando Sergio, funciona
    """
    def tecla_apretada_mik_L(self, tecla):  #metodo que es llamado por la clase TDC_logica para pasar la tecla apretada (ya en binario)
        #self.mik_L.append(tecla)

        #print(tecla.vk) #tecla precionada

        try:

            if self.And1.isActiveWindow(): #se filtra cuando la ventana AND1 esta como foco
                #print("and1")
                #print(tecla)
                #aca van las teclas que no son letras -> flechas, espacio, excecute, etc.
                """
                if tecla == Key.left:       #<--    space BWD
                    self.mik_L.append("00101100")
                elif tecla == Key.right:    #-->    space FWD
                    self.mik_L.append("00100110")
                elif tecla == Key.space:    #space
                    self.mik_L.append("00100001")
                elif tecla == Key.enter:    #enter  EXECUTE
                    self.mik_L.append("00100011")
                elif tecla == Key.backspace:    #borrar ERASE LINE
                    self.mik_L.append("00100010")
                """
                if tecla == Key.left:       #<--    space BWD
                    self.mik_L.append("00101100")
                elif tecla == Key.right:    #-->    space FWD
                    self.mik_L.append("00100110")
                elif tecla == Key.space:    #space
                    #self.mik_L.append("00100001")  SEL
                    self.mik_L.append("00100101") 
                elif tecla == Key.enter:    #enter  EXECUTE
                    self.mik_L.append("00100011")
                elif tecla == Key.backspace:    #borrar ERASE LINE
                    self.mik_L.append("00100010")
                elif tecla == Key.down:    #flecha abajo SEL
                    self.mik_L.append("00100000")
                else:
                #aca van las teclas que son letras. OBS: los numeros deben ser los de arriba!!
                    tecla = str(tecla)
                    if len(tecla) == 3:
                        tecla = tecla[1]
                        tecla = tecla.upper()
                        tecla_ord = ord(tecla)
                        if tecla_ord>32 and tecla_ord<91:
                            letra_bin = ''.join(format(tecla_ord, '08b'))
                        else:       #la tecla ingresada no corresponde al MIK:
                            letra_bin = "01000000"  #"01000000": ninguna tecla fue apretada

                        self.mik_L.append(letra_bin)

                #print(self.mik_L)
            elif self.And2.isActiveWindow(): #se filtra cuando la ventana AND1 esta como foco
                print("and2")
                #aca iria lo mismo que arriba pero para el MIK R

        except AttributeError:  #si la AND no esta abierta, no tiene sentido que se ingresen las teclas.
                #print("No abierta")
                pass
        

        """
        try:
            print("alphanumeric key {0} pressed".format(tecla.char))
            print(type(tecla.char))
            #print("alphanumeric key {0} pressed".format(tecla))
            #print(type(tecla))
        except AttributeError:
            print("special key {0} pressed".format(tecla))
        """

    def return_estado_CONC(self):           #armo la palabra con el estado del CONC
        self.actualizar_listas_coord_CONC()
        estado = ""
#----------WORD 1----------
        estado += self.range_scale + self.disp_select_AIR + self.disp_select_SURF + self.disp_select_SUBSURF + self.ref_pos + self.bear_sel + self.link_sel + self.warf_sel + self.fig + self.threat_ass + "00000000"
#----------WORD 2----------
        estado += self.mode1_L + self.mode2_L + self.mode3_L + self.true_motion + self.own_cursor + self.mode1_R + self.mode2_R + self.mode3_R + self.syst_alarm + self.radar_recorder + "00000000"
        self.mode1_L = "00"
        self.mode2_L = "000"
        self.mode3_L = "0"
        self.mode1_L = "00"
        self.mode2_L = "000"
        self.mode3_L = "0"
        self.syst_alarm = "0"   #como es pulsador, una vez que envio su estado, lo seteo en 0.
#----------WORD 3----------
        if len(self.mik_L) == 0:      #si la lista de caracteres apretados esta vacia: devolver no key pressed (100 en octal)
            self.mik_l = "01000000"
        else:       #si no esta vacia, devuelvo el valor de la tecla apretada y la borro de la lista
            self.mik_l = self.mik_L[0]
            del(self.mik_L[0])      #elimino la letra de la lista
        
        if len(self.mik_R) == 0:      #si la lista de caracteres apretados esta vacia: devolver no key pressed (100 en octal)
            self.mik_r = "01000000"
        else:       #si no esta vacia, devuelvo el valor de la tecla apretada y la borro de la lista
            self.mik_r = self.mik_R[0]
            del(self.mik_R[0])      #elimino la letra de la lista

        estado += self.mik_l + self.mik_r + "00000000"
#----------WORD 4----------
        if len(self.qek_L) == 0:        #si la lista esta vacia, no se presiono ningun qek
            self.qek_l = "00000000"
        else:                           #sino, envio la primera tecla de la lista y la elimino de la lista
            self.qek_l = self.qek_L[0]
            del(self.qek_L[0])
        
        if len(self.qek_R) == 0:        #si la lista esta vacia, no se presiono ningun qek
            self.qek_r = "00000000"
        else:                           #sino, envio la primera tecla de la lista y la elimino de la lista
            self.qek_r = self.qek_R[0]
            del(self.qek_R[0])

        estado += self.qek_l + self.qek_r + "00000000"
#----------WORD 5----------
        estado += self.icm_L + "0" + self.overlay_L + self.icm_R + "0" + self.overlay_R + "00000000"
#----------WORD 6----------
        if len(self.handwheel_DA) == 0:
            self.handwheel_da = "00000000"
        else:
            self.handwheel_da = self.handwheel_DA[0]
            del(self.handwheel_DA[0])

        if len(self.handwheel_DR) == 0:
            self.handwheel_dr = "00000000"
        else:
            self.handwheel_dr = self.handwheel_DR[0]
            del(self.handwheel_DR[0])
        
        estado += self.handwheel_da + self.handwheel_dr + "00000000"
#----------WORD 7----------
        if len(self.rollball_L_DX) == 0:
            self.rollball_L_dx = "00000000"
        else:
            self.rollball_L_dx = self.rollball_L_DX[0]
            del(self.rollball_L_DX[0])

        if len(self.rollball_L_DY) == 0:
            self.rollball_L_dy = "00000000"
        else:
            self.rollball_L_dy = self.rollball_L_DY[0]
            del(self.rollball_L_DY[0])

        estado += self.rollball_L_dx + self.rollball_L_dy + "00000000"
#----------WORD 8----------
        if len(self.rollball_R_DX) == 0:
            self.rollball_R_dx = "00000000"
        else:
            self.rollball_R_dx = self.rollball_R_DX[0]
            del(self.rollball_R_DX[0])

        if len(self.rollball_R_DY) == 0:
            self.rollball_R_dy = "00000000"
        else:
            self.rollball_R_dy = self.rollball_R_DY[0]
            del(self.rollball_R_DY[0])

        estado += self.rollball_R_dx + self.rollball_R_dy + "00000000"
#----------WORD 9----------
        estado += "000000000000000000000000"    #palabra de status

        return estado
#-----------------------------------------------------------------------#

    def actualizar_listas_coord_CONC(self):
        lista_radar_widget = self.RadarWidget.get_lista_coordenadas()        #tomo los nuevos valores de coordenadas introducidas por el usuario.
        if self.rolling_o_handwheel == "rolling":               #si esta activado el modo rolling: los datos que recibo son de la rolling
            for i in range (len(lista_radar_widget)):
                if len(lista_radar_widget[i]) > 0:      #si la lista que recibo no esta vacia (significa que hubo coordenadas nuevas introducidas):

                    #print("Coord_L: ",self.coord_rolling_L[0], "Coord_L: ", self.coord_rolling_L[1])
                    #print("Nueva_coord: ", lista_radar_widget[i][0], "Nueva_coord ", lista_radar_widget[i][1])            

                    delta_x = lista_radar_widget[i][0] - self.coord_rolling_L[0]
                    self.coord_rolling_L[0] = lista_radar_widget[i][0]
                    delta_y = lista_radar_widget[i][1] - self.coord_rolling_L [1]
                    self.coord_rolling_L [1] = lista_radar_widget [i][1]

                    #print("Delta_X: ", delta_x, "Delta_Y: ", delta_y)

                    #paso los deltas a valores de rotacion
                    x = round(delta_x*570/256,1)        #cuantos l.s.b debo mandar
                    y = round(delta_y*570/256,1)        #   "       "
                    if abs(x) >= abs(y):
                        cant_deltas = round((abs(x)//128)+1)
                    else:
                        cant_deltas = round((abs(y)//128)+1)

                    #print("Debo mandar lsb x: ", x, "lsb y: ", y)
                    #print("Envio cant_deltas: ", cant_deltas)

                    x_delta = round(x/cant_deltas)
                    x_delta_ultimo = round(x - (cant_deltas-1)*x_delta)

                    y_delta = round(y/cant_deltas)
                    y_delta_ultimo = round(y - (cant_deltas-1)*y_delta)

                    #print("X_delta: ", x_delta, "X_delta_ult: ", x_delta_ultimo)
                    #print("Y_delta: ", y_delta, "Y_delta_ult: ", y_delta_ultimo)

                    #paso los delta a palabra binaria:
                    x_delta_bin = self.int_2_binario(x_delta,8)
                    x_delta_ultimo_bin = self.int_2_binario(x_delta_ultimo, 8)
                    y_delta_bin = self.int_2_binario(y_delta, 8)
                    y_delta_ultimo_bin = self.int_2_binario(y_delta_ultimo, 8)
                    #agrego los delta_bin a la lista correspondiente:
                    for i in range(cant_deltas-1):
                        self.rollball_L_DX.append(x_delta_bin)
                    self.rollball_L_DX.append(x_delta_ultimo_bin)
                    for i in range(cant_deltas-1):
                        self.rollball_L_DY.append(y_delta_bin)
                    self.rollball_L_DY.append(y_delta_ultimo_bin)

                    #### AUXILIAR ####
                    for i in range(cant_deltas-1):
                        self.lista_dx.append(x_delta)
                    self.lista_dx.append(x_delta_ultimo)
                    for i in range(cant_deltas-1):
                        self.lista_dy.append(y_delta)
                    self.lista_dy.append(y_delta_ultimo)
                    #print("lista x: ", self.lista_dx)
                    #print("lista y: ", self.lista_dy)
                        
                    

        elif self.rolling_o_handwheel == "handwheel":    #si tengo apretado el boton handwheel y llegan datos:
            for i in range(len(lista_radar_widget)):
                if len(lista_radar_widget[i]) > 0:      #si la lista que recibo no esta vacia (significa que hubo coordenadas nuevas introducidas):
                    #primero, paso las coordenadas x-y a polares:
                    radio = round (math.sqrt(lista_radar_widget[i][0]**2+lista_radar_widget[i][1]**2),1)
                    angulo = round((math.atan2(lista_radar_widget[i][1], lista_radar_widget[i][0]))*180/math.pi,1)

                    if lista_radar_widget[i][0] >= 0 and lista_radar_widget[i][1] >= 0:
                        angulo = 90 - angulo
                    elif lista_radar_widget[i][0] >= 0 and lista_radar_widget[i][1] < 0:
                        angulo = 90 + abs(angulo)
                    elif lista_radar_widget[i][0] < 0 and lista_radar_widget[i][1] < 0:
                        angulo = -270 + abs(angulo)
                    else:
                        angulo = round(90 - angulo,1)

                    delta_ang = angulo - self.coord_handwheel[0]
                    self.coord_handwheel[0] = angulo
                    delta_radio = round(radio - self.coord_handwheel[1], 1)
                    self.coord_handwheel[1] = radio

                    #paso los valores de delta a rotaciones
                    a = round(delta_ang *1024/90,1)         #cuantos l.s.b debo mandar
                    r = round(delta_radio *414/256,1)       #   "       "

                    if abs(a) >= abs(r):
                        cant_deltas = round((abs(a)//127)+1)        
                    else:
                        cant_deltas = round((abs(r)//127)+1)        

                    delta_a = round(a/cant_deltas)
                    delta_a_ultimo = round(a - (cant_deltas-1)*delta_a)
                    delta_r = round(r/cant_deltas)
                    delta_r_ultimo = round(r - (cant_deltas-1)*delta_r)

                    #paso los deltas a binario:
                    delta_a_bin = self.int_2_binario(delta_a, 8)
                    delta_a_ultimo_bin = self.int_2_binario (delta_a_ultimo, 8)
                    delta_r_bin = self.int_2_binario(delta_r, 8)
                    delta_r_ultimo_bin = self.int_2_binario(delta_r_ultimo, 8)
                    #agrego los delta_bin a la lista correspondiente:
                    for i in range(cant_deltas-1):
                        #self.lista_handwheel_angulo.append(delta_a_bin)
                        self.handwheel_DA.append(delta_a_bin)
                    #self.lista_handwheel_angulo.append(delta_a_ultimo_bin)
                    self.handwheel_DA.append(delta_a_ultimo_bin)
                    for i in range(cant_deltas-1):
                        #self.lista_handwheel_radio.append(delta_r_bin)
                        self.handwheel_DR.append(delta_r_bin)
                    #self.lista_handwheel_radio.append(delta_r_ultimo_bin)
                    self.handwheel_DR.append(delta_r_ultimo_bin) 
    #---------------------------------------------------------------#
    #                     METODOS DE LOS BOTONES                    #
    #---------------------------------------------------------------#
#----------WORD 1----------
    #RANGE SCALE
    def fn_RS_L (self, boton):
        if boton == 1:      #2DM
            palabra = '000'
            self.RadarWidget.set_range_scale(2)     #seteo el valor de escala en el radar para poder graficar
            self.btn_rsl_2.setEnabled(False)
            self.btn_rsl_4.setEnabled(True)
            self.btn_rsl_8.setEnabled(True)
            self.btn_rsl_16.setEnabled(True)
            self.btn_rsl_32.setEnabled(True)
            self.btn_rsl_64.setEnabled(True)
            self.btn_rsl_128.setEnabled(True)
            self.btn_rsl_256.setEnabled(True)
        elif boton == 2:    #4DM
            palabra = '001'
            self.RadarWidget.set_range_scale(4)
            self.btn_rsl_2.setEnabled(True)
            self.btn_rsl_4.setEnabled(False)
            self.btn_rsl_8.setEnabled(True)
            self.btn_rsl_16.setEnabled(True)
            self.btn_rsl_32.setEnabled(True)
            self.btn_rsl_64.setEnabled(True)
            self.btn_rsl_128.setEnabled(True)
            self.btn_rsl_256.setEnabled(True)
        elif boton == 3:    #8DM
            palabra = '010'
            self.RadarWidget.set_range_scale(8)
            self.btn_rsl_2.setEnabled(True)
            self.btn_rsl_4.setEnabled(True)
            self.btn_rsl_8.setEnabled(False)
            self.btn_rsl_16.setEnabled(True)
            self.btn_rsl_32.setEnabled(True)
            self.btn_rsl_64.setEnabled(True)
            self.btn_rsl_128.setEnabled(True)
            self.btn_rsl_256.setEnabled(True)
        elif boton == 4:    #16DM
            palabra = '011'
            self.RadarWidget.set_range_scale(16)
            self.btn_rsl_2.setEnabled(True)
            self.btn_rsl_4.setEnabled(True)
            self.btn_rsl_8.setEnabled(True)
            self.btn_rsl_16.setEnabled(False)
            self.btn_rsl_32.setEnabled(True)
            self.btn_rsl_64.setEnabled(True)
            self.btn_rsl_128.setEnabled(True)
            self.btn_rsl_256.setEnabled(True)
        elif boton == 5:    #32DM
            palabra = '100'
            self.RadarWidget.set_range_scale(32)
            self.btn_rsl_2.setEnabled(True)
            self.btn_rsl_4.setEnabled(True)
            self.btn_rsl_8.setEnabled(True)
            self.btn_rsl_16.setEnabled(True)
            self.btn_rsl_32.setEnabled(False)
            self.btn_rsl_64.setEnabled(True)
            self.btn_rsl_128.setEnabled(True)
            self.btn_rsl_256.setEnabled(True)
        elif boton == 6:    #64DM
            palabra = '101'
            self.RadarWidget.set_range_scale(64)
            self.btn_rsl_2.setEnabled(True)
            self.btn_rsl_4.setEnabled(True)
            self.btn_rsl_8.setEnabled(True)
            self.btn_rsl_16.setEnabled(True)
            self.btn_rsl_32.setEnabled(True)
            self.btn_rsl_64.setEnabled(False)
            self.btn_rsl_128.setEnabled(True)
            self.btn_rsl_256.setEnabled(True)
        elif boton == 7:    #128DM
            palabra = '110'
            self.RadarWidget.set_range_scale(128)
            self.btn_rsl_2.setEnabled(True)
            self.btn_rsl_4.setEnabled(True)
            self.btn_rsl_8.setEnabled(True)
            self.btn_rsl_16.setEnabled(True)
            self.btn_rsl_32.setEnabled(True)
            self.btn_rsl_64.setEnabled(True)
            self.btn_rsl_128.setEnabled(False)
            self.btn_rsl_256.setEnabled(True)
        else:               #256DM
            palabra = '111'
            self.RadarWidget.set_range_scale(256)
            self.btn_rsl_2.setEnabled(True)
            self.btn_rsl_4.setEnabled(True)
            self.btn_rsl_8.setEnabled(True)
            self.btn_rsl_16.setEnabled(True)
            self.btn_rsl_32.setEnabled(True)
            self.btn_rsl_64.setEnabled(True)
            self.btn_rsl_128.setEnabled(True)
            self.btn_rsl_256.setEnabled(False)
        self.range_scale = palabra

    #DISPLAY SELECTION
    """
    AIR-SURF-SUB SURF-ELECTRONIC WAR-NAV AIDS-BLINDS ARCS-BLIND ARCS STEP-LPD TEST
    """
    def fn_DSelect_R (self, boton): 
        if boton == 1:
            if self.disp_select_AIR == "1":
                self.disp_select_AIR = "0"
            else:
                self.disp_select_AIR = "1"
        elif boton == 2:
            if self.disp_select_SURF == "1":
                self.disp_select_SURF = "0"
            else:
                self.disp_select_SURF = "1"
        elif boton == 3:
            if self.disp_select_SUBSURF == "1":
                self.disp_select_SUBSURF = "0"
            else:
                self.disp_select_SUBSURF = "1"
        elif boton == 4:
            if self.ref_pos == "1":
                self.ref_pos = "0"
            else:
                self.ref_pos = "1"
        elif boton == 5:
            if self.bear_sel == "1":
                self.bear_sel = "0"
            else:
                self.bear_sel = "1"
        elif boton == 6:
            if self.link_sel == "1":
                self.link_sel = "0"
            else:
                self.link_sel = "1"
        elif boton == 7:
            if self.warf_sel == "1":
                self.warf_sel = "0"
            else:
                self.warf_sel = "1"
        else:       #boton == 8
            if self.fig == "1":
                self.fig = "0"
            else:
                self.fig = "1"


    #THREAT ASSESSMENT
    def fn_TA_L (self, boton): 
        if boton == 1:      #12 sec
            palabra = '10000'
            self.btn_tal_12sec.setEnabled(False)
            self.btn_tal_30sec.setEnabled(True)
            self.btn_tal_6min.setEnabled(True)
            self.btn_tal_15min.setEnabled(True)
            self.btn_tal_reset.setEnabled(True)
        elif boton == 2:    #30sec
            palabra = '01000'
            self.btn_tal_12sec.setEnabled(True)
            self.btn_tal_30sec.setEnabled(False)
            self.btn_tal_6min.setEnabled(True)
            self.btn_tal_15min.setEnabled(True)
            self.btn_tal_reset.setEnabled(True)
        elif boton == 3:    #6min
            palabra = '00100'
            self.btn_tal_12sec.setEnabled(True)
            self.btn_tal_30sec.setEnabled(True)
            self.btn_tal_6min.setEnabled(False)
            self.btn_tal_15min.setEnabled(True)
            self.btn_tal_reset.setEnabled(True)
        elif boton == 4:    #15min
            palabra = '00010'
            self.btn_tal_12sec.setEnabled(True)
            self.btn_tal_30sec.setEnabled(True)
            self.btn_tal_6min.setEnabled(True)
            self.btn_tal_15min.setEnabled(False)
            self.btn_tal_reset.setEnabled(True)
        else:   #boton 5 -> RESET
            palabra = '00001'
            self.btn_tal_12sec.setEnabled(True)
            self.btn_tal_30sec.setEnabled(True)
            self.btn_tal_6min.setEnabled(True)
            self.btn_tal_15min.setEnabled(True)
            self.btn_tal_reset.setEnabled(False)
        self.threat_ass = palabra

#----------WORD 2----------
    #DISPLAY MODE LEFT
    def fn_DATREQ1_L (self, boton):
        palabra1 = '00'     #own cursor control:
        if boton == 1:      
            palabra1 = '10'
        elif boton == 2:
            palabra1 = '01' 
        self.mode1_L = palabra1

    def fn_DATREQ2_L (self, boton):    
        palabra2 = '000'    #rolling ball control:  
        if boton == 3:   
            palabra2 = '100'   
        elif boton == 4:
            palabra2 = '010'
        elif boton == 5: #boton RESET OBM
            palabra2 = '001'
        self.mode2_L = palabra2

    def fn_DATREQ3_L (self, boton):
        palabra3 = "0"      #dat request
        if boton == 6:
            palabra3 = "1"
        self.mode3_L = palabra3

    def fn_disp_modes_L(self, boton):
        if boton == 2:
            if self.radar_recorder == "1":
                self.radar_recorder = "0"
            else:
                self.radar_recorder = "1"
        elif boton == 3:
            if self.own_cursor == "1":
                self.own_cursor = "0"
            else:
                self.own_cursor = "1"
        elif boton == 5:
            if self.true_motion == "1":
                self.true_motion = "0"
            else:
                self.true_motion = "1"
        elif boton == 7:
            self.syst_alarm = "1"
            """
            if self.syst_alarm == "1":
                self.syst_alarm = "0"
            else:
                self.syst_alarm = "1"
            """


    def fn_DATREQ1_R (self, boton):
        palabra1 = '00'     #own cursor control:
        if boton == 1:      
            palabra1 = '10'
        elif boton == 2:
            palabra1 = '01' 
        self.mode1_R = palabra1

    def fn_DATREQ2_R (self, boton):    
        palabra2 = '000'    #rolling ball control:  
        if boton == 3:   
            palabra2 = '100'   
        elif boton == 4:
            palabra2 = '010'
        elif boton == 5: #boton RESET OBM
            palabra2 = '001'
        self.mode2_R = palabra2

    def fn_DATREQ3_R (self, boton):
        palabra3 = '0'      #dat request
        if boton == 6:
            palabra3 = '1'
        self.mode3_R = palabra3

#----------WORD 3----------
    #MIK-L
    def fn_mik_L(self, boton):
        tecla_bin = self.lista_mik[boton]
        if len(tecla_bin) == 8:
            self.mik_L.append(tecla_bin)
            #print(tecla_bin)
        """
        if tecla_bin == "00101100"  #tecla apretada: <-- (space BWD)
            #corro el asterisco un lugar hacia la izquierda
        elif tecla_bin == "00100110"    #tecla apretada: --> (space FWD)
            #corro el asterisco un lugar hacia la derecha
        """
    #MIK-R
    """
    LO MISMO PERO CON UN NUEVO TECLADO EN LA PARTE DERECHA
    """
#----------WORD 4----------
    #QEK-L
    def fn_QEK_L (self, boton):
        if boton == 20:
            palabra = "00010000"
        elif boton == 21:
            palabra = "00010001"
        elif boton == 22:
            palabra = "00010010"
        elif boton == 23:
            palabra = '00010011'
        elif boton == 24:
            palabra = '00010100'
        elif boton == 25:
            palabra = '00010101'
        elif boton == 26:
            palabra = '00010110'
        elif boton == 27:
            palabra = '00010111'
        elif boton == 30:
            palabra = '00011000'
        elif boton == 31:
            palabra = '00011001'
        elif boton == 32:
            palabra = '00011010'
        elif boton == 33:
            palabra = '00011011'
        elif boton == 34:
            palabra = '00011100'
        elif boton == 35:
            palabra = '00011101'
        elif boton == 36:
            palabra = '00011110'
        elif boton == 37:
            palabra = '00011111'
        elif boton == 40:
            palabra = '00100000'
        elif boton == 41:
            palabra = '00100001'
        elif boton == 42:
            palabra = '00100010'
        elif boton == 43:
            palabra = '00100011'
        elif boton == 44:
            palabra = '00100100'
        elif boton == 45:
            palabra = '00100101'
        elif boton == 46:
            palabra = '00100110'
        elif boton == 47:
            palabra = '00100111'
        elif boton == 50:
            palabra = '00101000'
        elif boton == 51:
            palabra = '00101001'
        elif boton == 52:
            palabra = '00101010'
        elif boton == 53:
            palabra = '00101011'
        elif boton == 54:
            palabra = '00101100'
        elif boton == 55:
            palabra = '00101101'
        elif boton == 56:
            palabra = '00101110'
        else: # boton == 57:
            palabra = '00101111'
        self.qek_L.append(palabra)
    #QEK-R 
    def fn_QEK_R (self, boton):
        if boton == 20:
            palabra = '00010000'
        elif boton == 21:
            palabra = '00010001'
        elif boton == 22:
            palabra = '00010010'
        elif boton == 23:
            palabra = '00010011'
        elif boton == 24:
            palabra = '00010100'
        elif boton == 25:
            palabra = '00010101'
        elif boton == 26:
            palabra = '00010110'
        elif boton == 27:
            palabra = '00010111'
        elif boton == 30:
            palabra = '00011000'
        elif boton == 31:
            palabra = '00011001'
        elif boton == 32:
            palabra = '00011010'
        elif boton == 33:
            palabra = '00011011'
        elif boton == 34:
            palabra = '00011100'
        elif boton == 35:
            palabra = '00011101'
        elif boton == 36:
            palabra = '00011110'
        elif boton == 37:
            palabra = '00011111'
        elif boton == 40:
            palabra = '00100000'
        elif boton == 41:
            palabra = '00100001'
        elif boton == 42:
            palabra = '00100010'
        elif boton == 43:
            palabra = '00100011'
        elif boton == 44:
            palabra = '00100100'
        elif boton == 45:
            palabra = '00100101'
        elif boton == 46:
            palabra = '00100110'
        elif boton == 47:
            palabra = '00100111'
        elif boton == 50:
            palabra = '00101000'
        elif boton == 51:
            palabra = '00101001'
        elif boton == 52:
            palabra = '00101010'
        elif boton == 53:
            palabra = '00101011'
        elif boton == 54:
            palabra = '00101100'
        elif boton == 55:
            palabra = '00101101'
        elif boton == 56:
            palabra = '00101110'
        else: # boton == 57:
            palabra = '00101111'
        self.qek_R.append(palabra)

#----------WORD 5----------
    #ICM-L
    def fn_ICM_L (self, boton):
        if boton == 1:
            palabra = '000'
            self.btn_icml_1.setEnabled(False)
            self.btn_icml_2.setEnabled(True)
            self.btn_icml_3.setEnabled(True)
            self.btn_icml_4.setEnabled(True)
            self.btn_icml_5.setEnabled(True)
            self.btn_icml_6.setEnabled(True)
            self.btn_icml_7.setEnabled(True) 
        elif boton == 2:
            palabra = '001'
            self.btn_icml_1.setEnabled(True)
            self.btn_icml_2.setEnabled(False)
            self.btn_icml_3.setEnabled(True)
            self.btn_icml_4.setEnabled(True)
            self.btn_icml_5.setEnabled(True)
            self.btn_icml_6.setEnabled(True)
            self.btn_icml_7.setEnabled(True) 
        elif boton == 3:
            palabra = '010'
            self.btn_icml_1.setEnabled(True)
            self.btn_icml_2.setEnabled(True)
            self.btn_icml_3.setEnabled(False)
            self.btn_icml_4.setEnabled(True)
            self.btn_icml_5.setEnabled(True)
            self.btn_icml_6.setEnabled(True)
            self.btn_icml_7.setEnabled(True) 
        elif boton == 4:
            palabra = '011'
            self.btn_icml_1.setEnabled(True)
            self.btn_icml_2.setEnabled(True)
            self.btn_icml_3.setEnabled(True)
            self.btn_icml_4.setEnabled(False)
            self.btn_icml_5.setEnabled(True)
            self.btn_icml_6.setEnabled(True)
            self.btn_icml_7.setEnabled(True) 
        elif boton == 5:
            palabra = '100'
            self.btn_icml_1.setEnabled(True)
            self.btn_icml_2.setEnabled(True)
            self.btn_icml_3.setEnabled(True)
            self.btn_icml_4.setEnabled(True)
            self.btn_icml_5.setEnabled(False)
            self.btn_icml_6.setEnabled(True)
            self.btn_icml_7.setEnabled(True) 
        elif boton == 6:
            palabra = '101'
            self.btn_icml_1.setEnabled(True)
            self.btn_icml_2.setEnabled(True)
            self.btn_icml_3.setEnabled(True)
            self.btn_icml_4.setEnabled(True)
            self.btn_icml_5.setEnabled(True)
            self.btn_icml_6.setEnabled(False)
            self.btn_icml_7.setEnabled(True) 
        else: #boton == 7
            palabra = '110'
            self.btn_icml_1.setEnabled(True)
            self.btn_icml_2.setEnabled(True)
            self.btn_icml_3.setEnabled(True)
            self.btn_icml_4.setEnabled(True)
            self.btn_icml_5.setEnabled(True)
            self.btn_icml_6.setEnabled(True)
            self.btn_icml_7.setEnabled(False) 
        self.icm_L = palabra

    #OVERLAY-L
    def fn_overlay_L (self, boton):
        if boton == 1:          #AAW/AWW
            palabra = "0001"
            self.btn_overlayl_aaw.setEnabled(False)
            self.btn_overlayl_asw.setEnabled(True)
            self.btn_overlayl_air_ew_iff.setEnabled(True)
            self.btn_overlayl_surface.setEnabled(True)

        elif boton == 2:        #ASW
            palabra = "0010"
            self.btn_overlayl_aaw.setEnabled(True)
            self.btn_overlayl_asw.setEnabled(False)
            self.btn_overlayl_air_ew_iff.setEnabled(True)
            self.btn_overlayl_surface.setEnabled(True)

        elif boton == 3:        #AIR/EW/IFF
            palabra = "0011"
            self.btn_overlayl_aaw.setEnabled(True)
            self.btn_overlayl_asw.setEnabled(True)
            self.btn_overlayl_air_ew_iff.setEnabled(False)
            self.btn_overlayl_surface.setEnabled(True)

        else:   #boton == 4     #SURFACE
            palabra = "0100"
            self.btn_overlayl_aaw.setEnabled(True)
            self.btn_overlayl_asw.setEnabled(True)
            self.btn_overlayl_air_ew_iff.setEnabled(True)
            self.btn_overlayl_surface.setEnabled(False)
        self.overlay_L = palabra

    #ICM-R
    def fn_ICM_R (self, boton):
        if boton == 1:
            palabra = '000'
            self.btn_icmr_1.setEnabled(False)
            self.btn_icmr_2.setEnabled(True)
            self.btn_icmr_3.setEnabled(True)
            self.btn_icmr_4.setEnabled(True)
            self.btn_icmr_5.setEnabled(True)
            self.btn_icmr_6.setEnabled(True)
            self.btn_icmr_7.setEnabled(True)
        elif boton == 2:
            palabra = '001'
            self.btn_icmr_1.setEnabled(True)
            self.btn_icmr_2.setEnabled(False)
            self.btn_icmr_3.setEnabled(True)
            self.btn_icmr_4.setEnabled(True)
            self.btn_icmr_5.setEnabled(True)
            self.btn_icmr_6.setEnabled(True)
            self.btn_icmr_7.setEnabled(True)
        elif boton == 3:
            palabra = '010'
            self.btn_icmr_1.setEnabled(True)
            self.btn_icmr_2.setEnabled(True)
            self.btn_icmr_3.setEnabled(False)
            self.btn_icmr_4.setEnabled(True)
            self.btn_icmr_5.setEnabled(True)
            self.btn_icmr_6.setEnabled(True)
            self.btn_icmr_7.setEnabled(True)
        elif boton == 4:
            palabra = '011'
            self.btn_icmr_1.setEnabled(True)
            self.btn_icmr_2.setEnabled(True)
            self.btn_icmr_3.setEnabled(True)
            self.btn_icmr_4.setEnabled(False)
            self.btn_icmr_5.setEnabled(True)
            self.btn_icmr_6.setEnabled(True)
            self.btn_icmr_7.setEnabled(True)
        elif boton == 5:
            palabra = '100'
            self.btn_icmr_1.setEnabled(True)
            self.btn_icmr_2.setEnabled(True)
            self.btn_icmr_3.setEnabled(True)
            self.btn_icmr_4.setEnabled(True)
            self.btn_icmr_5.setEnabled(False)
            self.btn_icmr_6.setEnabled(True)
            self.btn_icmr_7.setEnabled(True)
        elif boton == 6:
            palabra = '101'
            self.btn_icmr_1.setEnabled(True)
            self.btn_icmr_2.setEnabled(True)
            self.btn_icmr_3.setEnabled(True)
            self.btn_icmr_4.setEnabled(True)
            self.btn_icmr_5.setEnabled(True)
            self.btn_icmr_6.setEnabled(False)
            self.btn_icmr_7.setEnabled(True)
        else: #boton == 7
            palabra = '110'
            self.btn_icmr_1.setEnabled(True)
            self.btn_icmr_2.setEnabled(True)
            self.btn_icmr_3.setEnabled(True)
            self.btn_icmr_4.setEnabled(True)
            self.btn_icmr_5.setEnabled(True)
            self.btn_icmr_6.setEnabled(True)
            self.btn_icmr_7.setEnabled(False)
        self.icm_R = palabra
    
    #OVERLAY-R
    def fn_overlay_R (self, boton):
        if boton == 1:          #AAW/AWW
            palabra = "0001"
            self.btn_overlayr_aaw.setEnabled(False)
            self.btn_overlayr_asw.setEnabled(True)
            self.btn_overlayr_air_ew_iff.setEnabled(True)
            self.btn_overlayr_surface.setEnabled(True)

        elif boton == 2:        #ASW
            palabra = "0010"
            self.btn_overlayr_aaw.setEnabled(True)
            self.btn_overlayr_asw.setEnabled(False)
            self.btn_overlayr_air_ew_iff.setEnabled(True)
            self.btn_overlayr_surface.setEnabled(True)

        elif boton == 3:        #AIR/EW/IFF
            palabra = "0011"
            self.btn_overlayr_aaw.setEnabled(True)
            self.btn_overlayr_asw.setEnabled(True)
            self.btn_overlayr_air_ew_iff.setEnabled(False)
            self.btn_overlayr_surface.setEnabled(True)

        else:   #boton == 4     #SURFACE
            palabra = "0100"
            self.btn_overlayr_aaw.setEnabled(True)
            self.btn_overlayr_asw.setEnabled(True)
            self.btn_overlayr_air_ew_iff.setEnabled(True)
            self.btn_overlayr_surface.setEnabled(False)
        self.overlay_R = palabra

#----------WORD 6----------
    #HANDWHEEL delta PHI --> implementado mas arriba

    #HANDWHEEL delta RHO --> implementado mas arriba

#----------WORD 7----------
    #ROLLING BALL-L: delta X --> implementado mas arriba

    #ROLLING BALL-L: delta Y --> implementado mas arriba

#----------WORD 8----------
    #ROLLING BALL-R: delta X --> implementado mas arriba

    #ROLLING BALL-R: delta Y --> implementado mas arriba

    def set_nro_msj_lpd(self):
        self.nro_msj_lpd = int(self.le_nro_msj_lpd.text())
        #print(self.nro_msj_lpd)

    """
    def suppress_qt_warnings(self):
        environ["QT_DEVICE_PIXEL_RATIO"] = "0"
        environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
        environ["QT_SCREEN_SCALE_FACTORS"] = "1"
        environ["QT_SCALE_FACTOR"] = "1"
    """

 
