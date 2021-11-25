# Algoritmos Genéticos
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

# Datos para la planificacion
###################################################################################################################################

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
indice_disp = {}
for cont, disp in enumerate(name_dispositivos):
  indice_disp[disp.lower()] = indice_disp.get(disp.lower(), cont) 

# Se define la electrificación contratada KW a la compañia electrica
consumo_fijo_nevera = 0.3
consumo_fijo_congelador = 0.3
# Se descuenta el consumo instantaneo continuo de la nevera y del congelador
consumo_contratado = 5.750 - consumo_fijo_nevera - consumo_fijo_congelador

# Se define la probabilidad de mutacion
p_mut = 0.2
# Tareas seleccionadas por el usuario
tareas_seleccionadas = [] 
# Cromosoma creado a partir de la selección del usuario
cromosoma_seleccionado = []
# Poblacion del problema
poblacion = []

# Cota superior
cota_superior = 13.0

# Funciones
###########################################################################################################################33

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
        cromosoma_seleccionado.append(hora_selec) 

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
  rango1 = set(range(franjaIn1, franjaFin1 + 1))
  rango2 =  set(range(franjaIn2, franjaFin2 + 1))
  return len(rango1.intersection(rango2)) > 0

def genPoblacion(numero):
  ''' Se genera la población inicial con los datos que introduce el usuario por la consola
  Input: Int -> Número de individuos en la población
  Output: Array -> Población inicial
   '''  
  poblacion_inicial = []  
  #introducirDatos()

  # Se añade la selección del usuario como primer elemento de la población
  poblacion_inicial.append(cromosoma_seleccionado)
  longitud_cromosoma = len(cromosoma_seleccionado)

  # Para rellenar la pbolación restante se realiza de manera aleatoria
  for individuo in range(1,numero):
    propuesta_individuo = []
    for tarea in range(longitud_cromosoma): 
      propuesta_individuo.append(random.randrange(0,23))
    poblacion_inicial.append(propuesta_individuo)
  return poblacion_inicial


def mejoresGenes(evaluacion):  
  ''' Se obtiene una lista ordenada de individuos según su puntuación (Minimización)
  Input: Lista -> Lista evaluacion población
  Output: Lista -> Índices de los individuos por puntuación
   '''
  sorted_pairs = sorted(enumerate(evaluacion), key=operator.itemgetter(1))
  lista_mejores_soluciones = []
  for index, element in sorted_pairs:
      lista_mejores_soluciones.append(index)  
  return lista_mejores_soluciones

def cruce(ind1, ind2):
  ''' Se cruzan dos individuos de la población obteniendo un descendiente
  Input: Lista -> Individuo 1, individuo 2
  Output: Lista -> Descendiente
   '''
  # Aleatoriamente se cruzan dos padres y se genera un descendiente
  descendiente = []
  long_cromosoma = len(ind1)

  # Se recorren los genes
  for gen in range(len(ind1)):
    rand = random.randint(0,1)
    if rand == 0:
      descendiente.append(ind1[gen])
    else:
      descendiente.append(ind2[gen])
  return descendiente

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

def seleccion(lista_mejores_genes):    
  ''' Selección previa al cruce
  Input: Lista -> Lista de mejores genes solución, Int -> División poblacion inicial 
  Output: Lista -> lista individuos pre cruce
   '''
  genes_pre_cruce = []
  # Se obtienen el 50% de los mejores genes en la iteracion 
  index_mitad = numero_poblacion // 2 #Para hacer que sean pares
  lista_mitad_mejores_genes = lista_mejores_genes[:index_mitad]  
  #print('Longitud lista mitad mejores genes: ', len(lista_mitad_mejores_genes))

  for gen in lista_mitad_mejores_genes:    
    genes_pre_cruce.append(poblacion[gen])  
  return genes_pre_cruce

def mutacion(genes_post_cruce):
  ''' Mutacion de la población, en base a un porcentaje P_mut
  Input: Lista -> Población 100% después de haber sido cruzada
  Output: Lista -> Población mutada
   '''
  genes_post_mutacion = []

  for gen in genes_post_cruce:
    individuo = []
    for subgen in range(len(gen)):
      if random.randrange(0,1) < p_mut:
        individuo.append(random.randint(0,23))
      else:
        individuo.append(subgen)
        
    genes_post_mutacion.append(individuo)
  return genes_post_mutacion


# Numero iteraciones algoritmo y poblacion
##########################################
iteraciones = 12000
numero_poblacion = 5

#Poblacion de prueba
####################################
#tareas_seleccionadas = [3, 6, 2]
#cromosoma_seleccionado = [21, 9, 19]
#####################################

tareas_seleccionadas = [3, 3, 6, 6, 2, 3, 0]
cromosoma_seleccionado = [21, 21, 9, 9, 19, 19, 21]

# Planificador consumo eléctrico en casa
#######################################################################################################################
print('Planificador de consumo eléctrico \n')

resultados_experimento = {}
resultados_por_iter = {}

for npob in {5, 10, 25, 50, 100, 200, 500}:
  # Se genera la población inicial
  poblacion = genPoblacion(npob)
  
  # Variables para ploteo
  historico_resultado_iteracion = []
  historico_mejor_resultado = []

  mejor_solucion_obtenida = []
  mejor_coste_obtenido = 100.0
  print('\n ######################################################## \n')
  for iter in tqdm(range(iteraciones)):  
    evaluacion_poblacion = []
    for individuo in poblacion:
    # Se realiza la evaluación de la solución    
      evaluacion_poblacion.append(evaluacion(individuo, tareas_seleccionadas))

    #print('\nEvaluación poblacion: ', evaluacion_poblacion)   
    
    # Se obtienen la lista de los mejores individuos en orden
    lista_mejores_genes = [] 
    lista_mejores_genes = mejoresGenes(evaluacion_poblacion)  
    #print('\nLista mejores genes: ', lista_mejores_genes)

    #print('Iteración nº:',iter, ' Mejor resultado:', evaluacion_poblacion[lista_mejores_genes[0]])
    mejor_evaluacion_iteracion = evaluacion_poblacion[lista_mejores_genes[0]]   
    #print('Mejor solucion obtenida: ', mejor_evaluacion_iteracion)

    if mejor_evaluacion_iteracion < mejor_coste_obtenido:
      mejor_coste_obtenido = evaluacion_poblacion[lista_mejores_genes[0]]
      mejor_solucion_obtenida = poblacion[lista_mejores_genes[0]] 

    historico_resultado_iteracion.append(mejor_evaluacion_iteracion)
    historico_mejor_resultado.append(mejor_coste_obtenido)

    # Se realiza la selección previa al cruce, dividiendo por 2 la poblvacion (obtenemos el mejor 50%)
    genes_pre_cruce = []
    genes_pre_cruce = seleccion(lista_mejores_genes)    
    
    #Se cruzan los genes y se obtienen 4 descendientes por cada pareja, obteniendo de nuevo un 100% de descendientes
    genes_post_cruce = []

    for gen in range(0,len(genes_pre_cruce)-1):
      #indices
      gen1 = genes_pre_cruce[gen]
      gen2 = genes_pre_cruce[gen+1]

      genes_post_cruce.append(cruce(gen1, gen2))
      genes_post_cruce.append(cruce(gen1, gen2))
      genes_post_cruce.append(cruce(gen1, gen2))
      genes_post_cruce.append(cruce(gen1, gen2))
    

    # Con una probabilidad de p_mut los hijos pueden mutar
    poblacion = mutacion(genes_post_cruce)
  resultados_experimento[npob] = resultados_experimento.get(npob, historico_mejor_resultado[1:]) 
  resultados_por_iter[npob] = resultados_por_iter.get(npob, historico_resultado_iteracion[1:])

print('\n ########################################################')
print('\n Menor coste obtenido', mejor_coste_obtenido, '€ \n')
for i,tarea in enumerate(tareas_seleccionadas):
  print('El dispositivo: ', name_dispositivos[tarea], ' se debe de conectar a las: ', mejor_solucion_obtenida[i],' horas')
print('\n ########################################################')