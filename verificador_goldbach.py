#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
═══════════════════════════════════════════════════════════════════════════
        VERIFICADOR MASIVO DE LA CONJETURA DE GOLDBACH
═══════════════════════════════════════════════════════════════════════════

Autor: Colaboración IA-Humano
Fecha: Noviembre 2025
Propósito: Verificar computacionalmente la conjetura de Goldbach para
           rangos masivos de números pares.

Conjetura de Goldbach:
    Todo número par n ≥ 6 puede expresarse como suma de dos primos.

Este programa:
    ✅ Verifica millones/billones de números
    ✅ Se ejecuta en paralelo (multi-core)
    ✅ Guarda progreso automáticamente
    ✅ Resume desde donde quedó si se interrumpe
    ✅ Genera reportes detallados

Uso:
    python verificador_goldbach.py

═══════════════════════════════════════════════════════════════════════════
"""

import os
import json
import time
import math
from datetime import datetime, timedelta
from multiprocessing import Pool, cpu_count
import sys

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN - ¡AJUSTA ESTOS VALORES SEGÚN TU PC Y OBJETIVOS!
# ═══════════════════════════════════════════════════════════════════════════

CONFIG = {
    # Rango de verificación
    "n_inicial": 6,                    # Primer número par a verificar
    "n_final": 10**6,                 # Último número a verificar (100,000,000,000,000,000)
    "paso": 2,                         # Siempre 2 (números pares)
    
    # Paralelización
    "num_cores": max(1, cpu_count() - 1),  # Usar todos los cores menos 1
    
    # Gestión de archivos
    "archivo_progreso": "progreso_goldbach.json",
    "archivo_log": "log_goldbach.txt",
    
    # Rendimiento
    "tamaño_batch": 10000,             # Números por lote
    "intervalo_guardado": 3600,        # Guardar cada hora (segundos)
    
    # Salida
    "verbose": True                    # Mostrar mensajes detallados
}

# ═══════════════════════════════════════════════════════════════════════════
# FUNCIONES MATEMÁTICAS OPTIMIZADAS
# ═══════════════════════════════════════════════════════════════════════════

def criba_eratostenes_segmentada(limite):
    """
    Criba de Eratóstenes optimizada usando segmentación de memoria.
    
    Esta implementación es eficiente incluso para límites muy grandes
    (millones o billones) ya que divide el problema en segmentos.
    
    Args:
        limite: Encontrar todos los primos hasta este número
        
    Returns:
        Lista de todos los números primos ≤ limite
    """
    if limite < 2:
        return []
    
    # Fase 1: Generar primos pequeños (hasta √limite)
    sqrt_limite = int(math.sqrt(limite)) + 1
    es_primo_pequeño = [True] * sqrt_limite
    es_primo_pequeño[0] = es_primo_pequeño[1] = False
    
    for i in range(2, int(math.sqrt(sqrt_limite)) + 1):
        if es_primo_pequeño[i]:
            for j in range(i*i, sqrt_limite, i):
                es_primo_pequeño[j] = False
    
    primos_pequeños = [i for i in range(sqrt_limite) if es_primo_pequeño[i]]
    
    if limite <= sqrt_limite:
        return [p for p in primos_pequeños if p <= limite]
    
    # Fase 2: Usar primos pequeños para cribar segmentos grandes
    tamaño_segmento = min(sqrt_limite, 10**6)
    primos = primos_pequeños.copy()
    
    for inicio in range(sqrt_limite, limite + 1, tamaño_segmento):
        fin = min(inicio + tamaño_segmento, limite + 1)
        segmento = [True] * (fin - inicio)
        
        for p in primos_pequeños:
            primer_multiplo = ((inicio + p - 1) // p) * p
            if primer_multiplo < inicio:
                primer_multiplo += p
            if primer_multiplo == p:
                primer_multiplo += p
            
            for j in range(primer_multiplo, fin, p):
                segmento[j - inicio] = False
        
        primos.extend([inicio + i for i in range(len(segmento)) if segmento[i]])
    
    return primos


# Cache global de primos (compartido entre procesos mediante fork)
_cache_primos = {}
_cache_set_primos = {}

def obtener_primos_hasta(n):
    """
    Obtiene lista de primos hasta n, usando cache para evitar recálculos.
    
    Args:
        n: Límite superior
        
    Returns:
        Tupla (lista_primos, set_primos)
    """
    if n not in _cache_primos:
        _cache_primos[n] = criba_eratostenes_segmentada(n)
        _cache_set_primos[n] = set(_cache_primos[n])
    return _cache_primos[n], _cache_set_primos[n]


def verificar_goldbach_rango(args):
    """
    Verifica la conjetura de Goldbach para un rango de números pares.
    
    Esta función es ejecutada en paralelo por múltiples procesos.
    
    Args:
        args: Tupla (n_inicio, n_fin, verbose)
        
    Returns:
        Diccionario con resultados de la verificación
    """
    n_inicio, n_fin, verbose = args
    
    # CORRECCIÓN: Asegurar que n_inicio es par
    if n_inicio % 2 != 0:
        n_inicio += 1
    
    # Obtener primos necesarios
    max_primo_necesario = n_fin
    primos, set_primos = obtener_primos_hasta(max_primo_necesario)
    
    resultados = {
        "rango": (n_inicio, n_fin),
        "verificados": 0,
        "cumple": 0,
        "no_cumple": [],
        "min_representaciones": float('inf'),
        "max_representaciones": 0,
        "tiempo": 0
    }
    
    inicio_tiempo = time.time()
    
    # Verificar cada número par en el rango
    for n in range(n_inicio, n_fin + 1, 2):
        representaciones = 0
        
        # Buscar pares de primos que suman n
        # Optimización: solo verificar hasta n/2 por simetría
        for p in primos:
            if p > n // 2:
                break
            q = n - p
            if q in set_primos:
                representaciones += 1
        
        resultados["verificados"] += 1
        
        if representaciones > 0:
            resultados["cumple"] += 1
            resultados["min_representaciones"] = min(
                resultados["min_representaciones"], 
                representaciones
            )
            resultados["max_representaciones"] = max(
                resultados["max_representaciones"], 
                representaciones
            )
        else:
            # ¡Contraejemplo encontrado!
            resultados["no_cumple"].append(n)
    
    resultados["tiempo"] = time.time() - inicio_tiempo
    
    return resultados


# ═══════════════════════════════════════════════════════════════════════════
# SISTEMA DE PERSISTENCIA (Guardado y recuperación)
# ═══════════════════════════════════════════════════════════════════════════

def cargar_progreso():
    """
    Carga el progreso de una ejecución anterior (si existe).
    
    Esto permite reanudar la verificación si el programa fue interrumpido.
    
    Returns:
        Diccionario con el estado del progreso
    """
    if os.path.exists(CONFIG["archivo_progreso"]):
        try:
            with open(CONFIG["archivo_progreso"], 'r') as f:
                progreso = json.load(f)
                escribir_log(f"📂 Progreso cargado desde {CONFIG['archivo_progreso']}")
                escribir_log(f"   Último n verificado: {progreso['ultimo_n_verificado']:,}")
                return progreso
        except Exception as e:
            escribir_log(f"⚠️ Error al cargar progreso: {e}")
            escribir_log("   Iniciando desde el principio...")
    
    return {
        "ultimo_n_verificado": CONFIG["n_inicial"] - 2,
        "total_verificados": 0,
        "total_cumple": 0,
        "contraejemplos": [],
        "tiempo_total": 0,
        "inicio_sesion": datetime.now().isoformat()
    }


def guardar_progreso(progreso):
    """
    Guarda el progreso actual en un archivo JSON.
    
    Args:
        progreso: Diccionario con el estado actual
    """
    try:
        with open(CONFIG["archivo_progreso"], 'w') as f:
            json.dump(progreso, f, indent=2)
    except Exception as e:
        escribir_log(f"❌ Error al guardar progreso: {e}")


def escribir_log(mensaje):
    """
    Escribe un mensaje en el archivo de log y opcionalmente en pantalla.
    
    Args:
        mensaje: Texto a escribir
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mensaje_completo = f"[{timestamp}] {mensaje}\n"
    
    try:
        with open(CONFIG["archivo_log"], 'a', encoding='utf-8') as f:
            f.write(mensaje_completo)
    except Exception as e:
        print(f"Error escribiendo log: {e}")
    
    if CONFIG["verbose"]:
        print(mensaje_completo.strip())


# ═══════════════════════════════════════════════════════════════════════════
# REPORTES Y VISUALIZACIÓN
# ═══════════════════════════════════════════════════════════════════════════

def generar_reporte(progreso):
    """
    Genera un reporte visual detallado del progreso actual.
    
    Args:
        progreso: Diccionario con el estado actual
        
    Returns:
        String con el reporte formateado
    """
    n_actual = progreso["ultimo_n_verificado"]
    
    # Calcular porcentaje
    if CONFIG["n_final"] > CONFIG["n_inicial"]:
        porcentaje = ((n_actual - CONFIG["n_inicial"]) / 
                     (CONFIG["n_final"] - CONFIG["n_inicial"])) * 100
    else:
        porcentaje = 100.0
    
    # Calcular tiempos
    tiempo_transcurrido = progreso["tiempo_total"]
    tiempo_str = str(timedelta(seconds=int(tiempo_transcurrido)))
    
    # Calcular velocidad y tiempo restante
    if tiempo_transcurrido > 0 and progreso["total_verificados"] > 0:
        velocidad = progreso["total_verificados"] / tiempo_transcurrido
        numeros_restantes = (CONFIG["n_final"] - n_actual) // 2
        if velocidad > 0:
            tiempo_restante = numeros_restantes / velocidad
            tiempo_restante_str = str(timedelta(seconds=int(tiempo_restante)))
        else:
            tiempo_restante_str = "Calculando..."
    else:
        velocidad = 0
        tiempo_restante_str = "Calculando..."
    
    # Construir reporte
    reporte = f"""
╔═══════════════════════════════════════════════════════════════╗
║           REPORTE DE VERIFICACIÓN - GOLDBACH                  ║
╚═══════════════════════════════════════════════════════════════╝

📊 PROGRESO:
   • Último n verificado: {n_actual:,}
   • Total verificados: {progreso['total_verificados']:,}
   • Porcentaje completado: {porcentaje:.10f}%
   
✅ RESULTADOS:
   • Cumplen Goldbach: {progreso['total_cumple']:,}
   • Contraejemplos encontrados: {len(progreso['contraejemplos'])}
   
⏱️  TIEMPO:
   • Transcurrido: {tiempo_str}
   • Velocidad: {velocidad:.2f} números/segundo
   • Estimado restante: {tiempo_restante_str}
   
🖥️  SISTEMA:
   • Cores en uso: {CONFIG['num_cores']}
   • Tamaño de batch: {CONFIG['tamaño_batch']:,}
"""
    
    if progreso['contraejemplos']:
        reporte += f"\n⚠️  CONTRAEJEMPLOS: {progreso['contraejemplos']}\n"
    
    reporte += "\n" + "═" * 65
    
    return reporte


# ═══════════════════════════════════════════════════════════════════════════
# FUNCIÓN PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════

def verificacion_masiva_goldbach():
    """
    Función principal que coordina toda la verificación masiva.
    
    Esta función:
    1. Carga progreso anterior (si existe)
    2. Divide el trabajo en batches
    3. Ejecuta batches en paralelo
    4. Guarda progreso periódicamente
    5. Genera reportes
    
    Returns:
        Diccionario con resultados finales
    """
    escribir_log("="*65)
    escribir_log("🚀 INICIANDO VERIFICACIÓN MASIVA DE GOLDBACH")
    escribir_log("="*65)
    
    # Cargar progreso previo
    progreso = cargar_progreso()
    n_inicio = progreso["ultimo_n_verificado"] + 2
    
    # CORRECCIÓN: Asegurar que n_inicio es par
    if n_inicio % 2 != 0:
        n_inicio += 1
    
    # Verificar si ya terminamos
    if n_inicio >= CONFIG["n_final"]:
        escribir_log("✅ ¡Verificación ya completada!")
        escribir_log(generar_reporte(progreso))
        return progreso
    
    # Mostrar configuración
    escribir_log(f"📋 Configuración:")
    escribir_log(f"   • Rango: {n_inicio:,} → {CONFIG['n_final']:,}")
    escribir_log(f"   • Cores: {CONFIG['num_cores']}")
    escribir_log(f"   • Batch size: {CONFIG['tamaño_batch']:,}")
    escribir_log(f"   • Intervalo de guardado: {CONFIG['intervalo_guardado']}s")
    escribir_log("")
    
    # Control de tiempo para guardado periódico
    ultimo_guardado = time.time()
    
    # Crear pool de procesos
    try:
        with Pool(processes=CONFIG["num_cores"]) as pool:
            n_actual = n_inicio
            
            while n_actual <= CONFIG["n_final"]:
                # Preparar batches para procesar en paralelo
                batches = []
                for _ in range(CONFIG["num_cores"]):
                    if n_actual > CONFIG["n_final"]:
                        break
                    
                    n_fin_batch = min(
                        n_actual + CONFIG["tamaño_batch"] - 1, 
                        CONFIG["n_final"]
                    )
                    batches.append((n_actual, n_fin_batch, False))
                    n_actual = n_fin_batch + 2
                
                if not batches:
                    break
                
                # Procesar batches en paralelo
                resultados = pool.map(verificar_goldbach_rango, batches)
                
                # Consolidar resultados
                for resultado in resultados:
                    progreso["total_verificados"] += resultado["verificados"]
                    progreso["total_cumple"] += resultado["cumple"]
                    progreso["contraejemplos"].extend(resultado["no_cumple"])
                    progreso["ultimo_n_verificado"] = resultado["rango"][1]
                    progreso["tiempo_total"] += resultado["tiempo"]
                
                # Guardar periódicamente
                tiempo_actual = time.time()
                if tiempo_actual - ultimo_guardado >= CONFIG["intervalo_guardado"]:
                    guardar_progreso(progreso)
                    escribir_log(generar_reporte(progreso))
                    ultimo_guardado = tiempo_actual
                    
                    # Si encontramos contraejemplos, reportar inmediatamente
                    if progreso["contraejemplos"]:
                        escribir_log("")
                        escribir_log("🚨" * 20)
                        escribir_log("¡CONTRAEJEMPLO(S) POTENCIAL(ES) ENCONTRADO(S)!")
                        escribir_log(f"Valores: {progreso['contraejemplos']}")
                        escribir_log("Continuando verificación para encontrar más...")
                        escribir_log("🚨" * 20)
                        escribir_log("")
    
    except KeyboardInterrupt:
        escribir_log("\n⏸️  Verificación interrumpida por el usuario.")
        guardar_progreso(progreso)
        escribir_log("   Progreso guardado. Puedes reanudar más tarde.")
        return progreso
    
    except Exception as e:
        escribir_log(f"\n❌ Error durante la verificación: {e}")
        guardar_progreso(progreso)
        escribir_log("   Progreso guardado hasta el último punto exitoso.")
        raise
    
    # Guardado final
    guardar_progreso(progreso)
    escribir_log("\n" + "="*65)
    escribir_log("🎉 ¡VERIFICACIÓN COMPLETADA!")
    escribir_log("="*65)
    escribir_log(generar_reporte(progreso))
    
    return progreso


# ═══════════════════════════════════════════════════════════════════════════
# PUNTO DE ENTRADA DEL PROGRAMA
# ═══════════════════════════════════════════════════════════════════════════

def main():
    """Función principal del programa."""
    
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║         🔬 VERIFICADOR MASIVO DE GOLDBACH 🔬                 ║
║                                                               ║
║  Este programa verificará la conjetura de Goldbach           ║
║  para millones (o billones) de números.                      ║
║                                                               ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  ⚙️  Configuración actual:                                    ║
║     • Rango: 6 hasta {:,}                       ║
║     • Cores: {:>2}                                            ║
║     • Guardado automático cada {} segundos             ║
║                                                               ║
║  💾 Archivos que se generarán:                                ║
║     • progreso_goldbach.json (estado actual)                  ║
║     • log_goldbach.txt (historial detallado)                  ║
║                                                               ║
║  ⚠️  ADVERTENCIA:                                             ║
║     Este proceso puede tardar DÍAS o SEMANAS                 ║
║     Asegúrate de tener espacio en disco y energía estable    ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """.format(
        CONFIG["n_final"],
        CONFIG["num_cores"],
        CONFIG["intervalo_guardado"]
    ))
    
    # Estimar tiempo aproximado (manejo seguro para valores muy grandes)
    try:
        estimacion_simple = CONFIG["n_final"] / (CONFIG["num_cores"] * 1000)
        if estimacion_simple > 86400 * 365 * 100:  # Si es más de 100 años
            print(f"\n⏱️  Estimación: MÁS DE 100 AÑOS")
            print("   (La verificación completa no es práctica con hardware actual)")
        else:
            print(f"\n⏱️  Estimación muy aproximada: {timedelta(seconds=int(estimacion_simple))}")
    except (ValueError, OverflowError):
        print(f"\n⏱️  Estimación: TIEMPO MUY EXTENSO")
        print("   (El rango es demasiado grande para estimar)")
    
    print("   (La estimación real se mostrará después de los primeros batches)\n")
    
    respuesta = input("¿Deseas continuar? (s/n): ")
    
    if respuesta.lower() not in ['s', 'si', 'sí', 'yes', 'y']:
        print("\n👋 ¡Hasta luego!")
        return 0
    
    try:
        resultado = verificacion_masiva_goldbach()
        
        # Reporte final
        print("\n" + "="*65)
        print("📈 ESTADÍSTICAS FINALES:")
        print(f"   • Total verificados: {resultado['total_verificados']:,}")
        print(f"   • Cumplen Goldbach: {resultado['total_cumple']:,}")
        print(f"   • Contraejemplos: {len(resultado['contraejemplos'])}")
        print(f"   • Tiempo total: {timedelta(seconds=int(resultado['tiempo_total']))}")
        print("="*65)
        
        if resultado['contraejemplos']:
            print("\n⚠️  CONTRAEJEMPLOS ENCONTRADOS:")
            print(resultado['contraejemplos'])
            print("\n🔍 Por favor, verifica estos números manualmente.")
            print("   Si se confirman, ¡has hecho un descubrimiento histórico!")
        else:
            print("\n✅ ¡La conjetura se cumple para todos los números verificados!")
            print("\n🎉 ¡Felicitaciones! Has contribuido a la verificación de Goldbach.")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⏸️  Verificación interrumpida por el usuario.")
        print("   El progreso ha sido guardado.")
        print("   Puedes reanudar ejecutando el programa nuevamente.")
        return 1
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("   El progreso ha sido guardado hasta el último punto.")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())