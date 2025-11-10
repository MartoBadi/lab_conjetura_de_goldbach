#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
═══════════════════════════════════════════════════════════════════════════
               SCRIPT DE REINICIO - VERIFICADOR GOLDBACH
═══════════════════════════════════════════════════════════════════════════

Este script elimina los archivos de progreso previo para empezar
una verificación limpia desde cero.

Úsalo cuando:
- Quieras empezar de nuevo
- Hayas actualizado el código
- Los datos anteriores tengan errores

ADVERTENCIA: Esto eliminará TODO el progreso guardado.
═══════════════════════════════════════════════════════════════════════════
"""

import os

archivos_a_eliminar = [
    "progreso_goldbach.json",
    "log_goldbach.txt",
    "resultados_test_1.txt",
    "resultados.txt",
    "verificador_goldbach.txt"
]

def reiniciar():
    print("="*70)
    print("🔄 REINICIAR VERIFICACIÓN DE GOLDBACH")
    print("="*70)
    print("\n⚠️  ADVERTENCIA:")
    print("   Este script eliminará TODOS los archivos de progreso guardado.")
    print("   Perderás el historial de verificaciones previas.\n")
    
    respuesta = input("¿Estás seguro de que quieres continuar? (escribe 'SI' para confirmar): ")
    
    if respuesta.strip().upper() != "SI":
        print("\n❌ Operación cancelada. No se eliminó nada.")
        return
    
    print("\n🗑️  Eliminando archivos...")
    eliminados = 0
    
    for archivo in archivos_a_eliminar:
        if os.path.exists(archivo):
            try:
                os.remove(archivo)
                print(f"   ✅ Eliminado: {archivo}")
                eliminados += 1
            except Exception as e:
                print(f"   ❌ Error al eliminar {archivo}: {e}")
        else:
            print(f"   ⊝ No existe: {archivo}")
    
    print(f"\n✨ Operación completada. Se eliminaron {eliminados} archivo(s).")
    print("\n📋 Ahora puedes ejecutar:")
    print("   python verificador_goldbach.py")
    print("\n   La verificación comenzará desde cero (n=6).")
    print("="*70)

if __name__ == "__main__":
    reiniciar()
