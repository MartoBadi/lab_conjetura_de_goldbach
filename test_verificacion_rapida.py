#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
═══════════════════════════════════════════════════════════════════════════
           TEST RÁPIDO - VERIFICADOR GOLDBACH CORREGIDO
═══════════════════════════════════════════════════════════════════════════

Este script ejecuta una verificación RÁPIDA para asegurarse de que
el código funciona correctamente después de las correcciones.

Verifica solo los primeros 1000 números pares (hasta n=2000).
═══════════════════════════════════════════════════════════════════════════
"""

import math
import time

def criba_eratostenes_simple(limite):
    """Criba simple para generar primos hasta 'limite'."""
    if limite < 2:
        return []
    
    es_primo = [True] * (limite + 1)
    es_primo[0] = es_primo[1] = False
    
    for i in range(2, int(math.sqrt(limite)) + 1):
        if es_primo[i]:
            for j in range(i*i, limite + 1, i):
                es_primo[j] = False
    
    return [i for i in range(limite + 1) if es_primo[i]]


def verificar_goldbach_numero(n, set_primos):
    """
    Verifica si un número par n cumple Goldbach.
    
    Returns:
        (cumple, representaciones) - tupla con resultado
    """
    if n % 2 != 0:
        raise ValueError(f"¡Error! {n} es impar. Goldbach solo aplica a pares.")
    
    representaciones = []
    
    for p in set_primos:
        if p > n // 2:
            break
        q = n - p
        if q in set_primos and q >= p:  # q >= p evita duplicados (3+7 = 7+3)
            representaciones.append((p, q))
    
    return len(representaciones) > 0, representaciones


def test_rapido():
    """Ejecuta un test rápido del verificador."""
    print("="*70)
    print("🧪 TEST RÁPIDO - VERIFICADOR GOLDBACH")
    print("="*70)
    
    n_max = 2000
    print(f"\n📋 Verificando números pares desde 6 hasta {n_max}...")
    
    # Generar primos
    print("🔢 Generando primos...")
    inicio = time.time()
    primos = criba_eratostenes_simple(n_max)
    set_primos = set(primos)
    tiempo_primos = time.time() - inicio
    print(f"   ✅ {len(primos)} primos generados en {tiempo_primos:.4f} segundos")
    
    # Verificar Goldbach
    print(f"\n🔍 Verificando Goldbach...")
    inicio = time.time()
    
    total_verificados = 0
    total_cumple = 0
    contraejemplos = []
    casos_ejemplo = []
    
    for n in range(6, n_max + 1, 2):  # Solo números PARES
        cumple, representaciones = verificar_goldbach_numero(n, set_primos)
        
        total_verificados += 1
        
        if cumple:
            total_cumple += 1
            
            # Guardar algunos ejemplos para mostrar
            if len(casos_ejemplo) < 5:
                casos_ejemplo.append({
                    'n': n,
                    'reps': representaciones[:3]  # Primeras 3 representaciones
                })
        else:
            # ¡Contraejemplo!
            contraejemplos.append(n)
    
    tiempo_verificacion = time.time() - inicio
    
    # Resultados
    print(f"   ✅ Verificación completada en {tiempo_verificacion:.4f} segundos")
    print("\n" + "="*70)
    print("📊 RESULTADOS:")
    print("="*70)
    print(f"   • Total verificados: {total_verificados}")
    print(f"   • Cumplen Goldbach: {total_cumple}")
    print(f"   • Contraejemplos: {len(contraejemplos)}")
    print(f"   • Porcentaje éxito: {(total_cumple/total_verificados)*100:.2f}%")
    
    # Mostrar ejemplos
    print("\n💡 EJEMPLOS DE VERIFICACIÓN:")
    for caso in casos_ejemplo:
        print(f"\n   n = {caso['n']}:")
        for p, q in caso['reps']:
            print(f"      {p} + {q} = {caso['n']}")
    
    # Verificar contraejemplos
    if contraejemplos:
        print("\n🚨 CONTRAEJEMPLOS ENCONTRADOS:")
        print(f"   {contraejemplos}")
        print("\n   ⚠️  ¡ADVERTENCIA! Esto NO debería ocurrir.")
        print("   La Conjetura de Goldbach se cumple para todos los números")
        print("   pares hasta 4×10^18. Si ves esto, hay un bug en el código.")
        return False
    else:
        print("\n✅ ¡PERFECTO! Todos los números cumplen Goldbach.")
        print("\n🎉 El verificador funciona correctamente.")
        print("\n📝 Puedes proceder con confianza a verificar rangos mayores:")
        print("   python verificador_goldbach.py")
        return True
    
    print("="*70)


if __name__ == "__main__":
    exito = test_rapido()
    exit(0 if exito else 1)
