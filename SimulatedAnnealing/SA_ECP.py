# Enfriamiento Simulado
# Planificador Consumo eléctrico
# MUIARFID, TIA LAB
# José Javier Calvo Moratilla
# 2021

#Lista de Dispositivos
########################
# 0 Horno              #
# 1 Cocina             #
# 2 Lavadora           #
# 3 Secadora           #
# 4 Termo              #
# 5 Lavavajillas       #
# 6 Aire               #
# 7 Microondas         #
# 8 tostadora          #
# 9 Máquina Café       #
########################

# Librerias
import numpy as np
import math
import random
import operator
import matplotlib.pyplot as plt
from tqdm import tqdm

# Se definen los dispositivos del sistema
name_dispositivos = ['Horno', 'Cocina','Lavadora', 'Secadora', 'Termo', 'Lavavajillas', 'Aire', 'Microndas', 'Tostadora', 'Cafe']
dispositivos = len(name_dispositivos)

# Se define el consumo de kw de cada dispositivo
consumo_dispositivos = [1.2, 1, 0.8, 3, 4.5, 1.3, 3.25, 1, 0.85, 0.8]
assert len(consumo_dispositivos) == dispositivos

# Se define el tiempo de uso medio de cada dispositivo
tiempo_uso_dispositivos = [1, 1, 2.5, 2, 0.5, 1.5, 5, 0.25, 0.25, 0.25]
assert len(tiempo_uso_dispositivos) == dispositivos

# Se definen las franjas horarias
divisiones_por_hora = 4 
franjas_horarias = divisiones_por_hora * 24

# Se definen los precios por hora de la tarifa electricidad
precios_por_hora = [0.16364, 0.16165, 0.15442, 0.15414, 0.15362, 0.16287, 0.18831, 0.22118, 0.2464, 0.22838, 0.22257, 
                    0.21475, 0.20769, 0.19385, 0.17929, 0.1784, 0.18255, 0.20195, 0.23366, 0.25676, 0.25938 ,0.25534, 0.22141, 0.1875]
assert len(precios_por_hora) == 24

#Se crea el índice de dispositivos, correspondiente a las filas del cromosoma
#indice_disp = {}
#for cont, disp in enumerate(name_dispositivos):
#  indice_disp[disp.lower()] = indice_disp.get(disp.lower(), cont) 
#  print(indice_disp)

# Se define la electrificación contratada KW a la compañia electrica
consumo_fijo_nevera = 0.3
consumo_fijo_congelador = 0.3
# Se descuenta el consumo instantaneo continuo de la nevera y del congelador
consumo_contratado = 5.750 - consumo_fijo_nevera - consumo_fijo_congelador

# Tareas seleccionadas por el usuario
tareas_seleccionadas = [] 

# Individuo creado a partir de la selección del usuario
individuo_actual = []

# Variables funciones de enfriamiento
t_inicial = 1
factor_enfriamiento = 1
factor_aleatoriedad = 0.2
t_iteracion = t_inicial

# Diccionario frecuencia tarea en solucion
freq_tarea_en_solucion = {}

# Cota superior
cota_superior = 17.0

# Funciones
###########################################################################################################################33

# Funciones de enfriamiento, retornan el decremento
def variante1(iter, t_ini):
  return t_ini - (iter * factor_enfriamiento)

def variante2(iter, t_iter):
  return factor_enfriamiento * t_iter

def variante3(iter, t_iter):
  return t_iter / (iter + factor_enfriamiento * t_iter)

def introducirDatos():
  ''' Se introducen los datos a través de la consola '''
  exit = 0
  while exit == 0:
    print('Dispositivos: \n', name_dispositivos)
    print('\n Introduce el dispositivo a utilizar: \n')
    disp_selec = indice_disp.get(input().lower())
    if disp_selec is not None:
      print('Hora de inicio para encender el dispositivo \n' ) 
      hora_selec = int(input())
      if hora_selec > 0 and hora_selec <= 24:     
        #Se obtiene las franjas correspondientes al uso del dispositivo
        tareas_seleccionadas.append(disp_selec)  
        individuo_actual.append(hora_selec) 

      else:
        print('Has introducido una hora no permitida \n' ) 
        print('El dispositivo no se ha introducido en el sistema \n' ) 
    else:
      print('Has introducido un dispositivo que no existe: \n')
      print('El dispositivo no se ha introducido al sistema: \n')

    print('\n Quieres introducir más dispositivos? S/N \n')
    if input().lower() == 'n':
      exit = 1

def hora2Franja(hora):
  ''' Traduce la hora a una franja horaria determinada 
  Input: Int -> Hora    
  Output: Int -> Número de la franja correspondiente
  '''
  return hora%24 * divisiones_por_hora

def precioFranja(franja):
  ''' Obtiene el precio de electricidad correspondiente a una franja determinada
  Input: Int -> Número de la franja horaria
  Output: Float -> Precio de la franja
   '''
  return precios_por_hora[math.floor(franja/4)]


def rangoFranjasUso(disp, hora):  
  ''' Obtiene el rango de uso de un dispositivo desde una hora determinada, por franjas 
  Input: Int -> Dispositivo, Int -> Hora
  Output: Int -> Franja inicial, Int -> Franja final
   '''   
  t_uso = tiempo_uso_dispositivos[disp]  
  franja_ini = hora2Franja(hora)  
  franja_fin = int(franja_ini + (t_uso * divisiones_por_hora))  
  return (franja_ini, franja_fin)

def tareaSolapada(disp1, hora1, disp2, hora2):  
  franjaIn1, franjaFin1 = rangoFranjasUso(disp1, hora1)
  franjaIn2, franjaFin2 = rangoFranjasUso(disp2, hora2)
  rango1 = set(range(franjaIn1, franjaFin1))
  rango2 =  set(range(franjaIn2, franjaFin2))
  #print('rango1: ', rango1)
  #print('rango2: ', rango2)
  #print('valores solapados: ', len(rango1.intersection(rango2)))
  return len(rango1.intersection(rango2)) > 0

def evaluacion(solucion, las_tareas):
  ''' Se evalua una solución
  Input: Lista -> Solucion, tareas_seleccionadas
  Output: Lista -> Coste consumo aparatos eléctricos
   '''
  #solucion: array de horas de inicio de tareas
  #Tareas: Tareas seleccionadas que identifian a un dispositivo concreto
  #Si dos tareas son iguales se solapan, return 1000.0

  # Obtener tarea duplicada y ver si se solapan
  franjas_tareas = {}

  for idx, dispo in enumerate(las_tareas):    

    # tarea
    hora_ini_tarea = solucion[idx]   
    
    #se obtiene el rango_uso de la tarea y se va guardando en un diccionario
    franja_ini, franja_fin = rangoFranjasUso(dispo, hora_ini_tarea)
    
    rango_uso = set(range(franja_ini, franja_fin))

    if franjas_tareas.get(dispo) == None:
      franjas_tareas[dispo] = franjas_tareas.get(dispo, [rango_uso])
    else:
      franjas_tareas[dispo].append(rango_uso)
  
  # una vez apilados los sets hay que comprobar si se solapan entre ellos
  tareas_unicas = set(las_tareas)   
  #print('Tareas Unicas ', tareas_unicas)

  # comprobamos para cada tarea de las que aparece si una de ellas al menos se solapa
  for ta_uni in tareas_unicas:
    ################################################################################################################################################3333333
    #print('Dispositivo Seleccionado: ', name_dispositivos[ta_uni])
    ################################################################################################################################################3333333

    #obtenemos los conjuntos de rangos
    conjuntos_rangos = franjas_tareas[ta_uni]
    
    cerca = False 
    cnt = 1

    #print(len(conjuntos_rangos))
    while cerca == False:
      if cnt < len(conjuntos_rangos):
        if len(conjuntos_rangos[0].intersection(conjuntos_rangos[cnt])) > 0:
            ################################################################################################################################################3333333
            #print('\nSe solapan: ', conjuntos_rangos[0], ' ', conjuntos_rangos[cnt])
            ################################################################################################################################################3333333
          return cota_superior
        else:
            cnt += 1
      else:
        cerca = True    
          ################################################################################################################################################3333333  
          #print('Dispositivo no se solapa')
          ################################################################################################################################################3333333


  consumo_simultaneo_franja = []
  
  for i in range(0, 24*divisiones_por_hora):
    consumo_simultaneo_franja.append(0)  
  res = 0 # Problema de minimización  

  #print('Lista consumo simultaneo: ', len(consumo_simultaneo_franja))

  for i, tarea in enumerate(las_tareas):
    #print('Dispositivo a evaluar: ', disp)
    franja_ini, franja_fin =  rangoFranjasUso(tarea, solucion[i])
    #print('Franjas de uso: ', franja_ini, franja_fin)
    for franja in range(franja_ini, franja_fin + 1):      
      franja_traducida = franja % (24*divisiones_por_hora)
      #print('Dispositivo seleccionado: ', disp)
      #print('Franja seleccionada: ', franja_traducida)
      
      consumo_simultaneo_franja[franja_traducida] += consumo_dispositivos[tarea]
      #Consumo dispositivo * precioKWH * tiempo     
      res += consumo_dispositivos[tarea] * precioFranja(franja_traducida) * (1 / divisiones_por_hora)  
    for consumo in consumo_simultaneo_franja:      
     if consumo > consumo_contratado:  
      #print('Se pasa el consumo contratado')      
      res = cota_superior    
  return res

def generaIndividuo(individuo_act, itera, t_iteracion):

  nuevo_individuo = individuo_act

  # Generamos un candidato nuevo con un factor de variabilidad
  for idx, individuo in enumerate(individuo_act):
    if random.randrange(0,1) < factor_aleatoriedad:
      nuevo_individuo[idx] = random.randrange(0,23)

  evaluacion_actual = evaluacion(individuo_act, tareas_seleccionadas)
  evaluacion_nuevo = evaluacion(nuevo_individuo, tareas_seleccionadas) 

  # Si mejora
  if (evaluacion_nuevo - evaluacion_actual ) < 0:

    return (nuevo_individuo, evaluacion_nuevo)

    # Si no mejora
  else:
    numero_boleto = random.randrange(0,t_inicial)
    if variante == 1:
      t_iteracion = variante1(itera, t_inicial)
      if numero_boleto < t_iteracion: #Enfriamos
        return (nuevo_individuo, evaluacion_nuevo)
      else:
        return (individuo_actual, evaluacion_actual)
      
    elif variante == 2:       
      t_iteracion_nueva = variante2(itera, t_iteracion)
      t_iteracion = t_iteracion_nueva
      if numero_boleto < t_iteracion: #Enfriamos
        return (nuevo_individuo, evaluacion_nuevo)
      else:
        return (individuo_actual, evaluacion_actual)

    elif variante == 3:
      t_iteracion_nueva = variante3(itera, t_iteracion)
      t_iteracion = t_iteracion_nueva
      if numero_boleto < t_iteracion: #Enfriamos
        return (nuevo_individuo, evaluacion_nuevo)
      else:
        return (individuo_actual, evaluacion_actual)

    else:
      raise 'Variante: ' + str(variante) + ' no reconocida.'



# Numero iteraciones algoritmo y poblacion
##########################################
iteraciones = 100000
#variante = 2

resultados_experimento = {}
resultados_por_iter = {}

print('Planificador de consumo eléctrico \n')
for variante in {1,2,3}:
  for temp in {1,25,100,200, 300,500}:

    t_it = temp
    
    # Variables para ploteo
    historico_resultado_iteracion = []
    historico_mejor_resultado = []

    mejor_coste_obtenido = 17.0
    mejor_solucion_obtenida = None

    print('\n ######################################################## \n')
    #introducirDatos()    
      #Poblacion de prueba
    ####################################
    tareas_seleccionadas = [3, 3, 6, 6, 2, 3, 0]
    individuo_actual = [21, 21, 9, 9, 19, 19, 21]
    #tareas_seleccionadas = [6, 6, 6]
    #individuo_actual = [21, 21, 21]
    #####################################

    # Se obtiene la frecuencia de cada tarea en las seleccionadas para comprobar los solapes horarios
    for i in tareas_seleccionadas:
      freq_tarea_en_solucion[i] = freq_tarea_en_solucion.get(i, 0) + 1

    for iter in tqdm(range(iteraciones)): 

      individuo, coste = generaIndividuo(individuo_actual, iter, t_it)

      if coste < mejor_coste_obtenido:
        mejor_solucion_obtenida  = individuo
        mejor_coste_obtenido = coste

      historico_resultado_iteracion.append(coste)
      historico_mejor_resultado.append(mejor_coste_obtenido)

    resultados_experimento[str(variante) + '_' + str(temp)] = resultados_experimento.get(str(variante) + '_' + str(temp), historico_mejor_resultado[0:]) 
    resultados_por_iter[str(variante) + '_' + str(temp)] = resultados_por_iter.get(str(variante) + '_' + str(temp), historico_resultado_iteracion[0:])

    #print('Iteración nº:',iter, ' Mejor resultado: ', mejor_solucion_obtenida, ' Mejor coste: ', mejor_coste_obtenido)  


    print('\n ########################################################')
    print('\n Menor coste obtenido', mejor_coste_obtenido, '€ \n')
    for i,tarea in enumerate(tareas_seleccionadas):
      print('El dispositivo: ', name_dispositivos[tarea], ' se debe de conectar a las: ', mejor_solucion_obtenida[i],' horas')
    print('\n ########################################################')