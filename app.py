"""Aplicación web didáctica para analizar números primos con Streamlit."""

from __future__ import annotations

import math
import random
import time

import streamlit as st


LIMITE = 1_000_000_000_000
MAX_DIVISORES_MUESTRA = 40


def factorizar_numero(n: int) -> dict[int, int]:
    """Devuelve los factores primos de n con sus exponentes (n > 1)."""
    factores: dict[int, int] = {}
    restante = n
    divisor = 2
    while divisor * divisor <= restante:
        if restante % divisor == 0:
            exponente = 0
            while restante % divisor == 0:
                restante //= divisor
                exponente += 1
            factores[divisor] = exponente
        divisor = 3 if divisor == 2 else divisor + 2
    if restante > 1:
        factores[restante] = 1
    return factores


def formato_factorizacion(factores: dict[int, int]) -> str:
    """Formatea una factorización como 2² × 3 × 5."""
    superindices = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
    partes = []
    for factor, exponente in factores.items():
        partes.append(str(factor) if exponente == 1 else f"{factor}{str(exponente).translate(superindices)}")
    return " × ".join(partes)


def obtener_divisores(factores: dict[int, int], max_limite: int = MAX_DIVISORES_MUESTRA) -> tuple[list[int], int]:
    """Genera los divisores desde la factorización, sin volver a probar hasta √n."""
    divisores = [1]
    for factor, exponente in factores.items():
        anteriores = divisores[:]
        potencia = 1
        for _ in range(exponente):
            potencia *= factor
            divisores.extend(valor * potencia for valor in anteriores)
    divisores.sort()
    return divisores[:max_limite], len(divisores)


def analizar_primalidad(n: int) -> dict:
    """Determina primalidad y arma una explicación paso a paso."""
    inicio = time.perf_counter()

    if n < 0:
        estado = {
            "es_primo": False,
            "titulo": f"El número {n} no es primo",
            "resumen": "Los números primos son enteros estrictamente mayores que 1. Ningún número negativo cumple esa condición.",
            "pasos": [
                f"{n} es menor que 0.",
                "Por definición, un número primo debe ser un entero mayor que 1.",
                "Por lo tanto, este número no es primo.",
            ],
            "divisores_muestra": [],
            "total_divisores": 0,
            "factorizacion": "No aplica para números negativos.",
        }
    elif n == 0:
        estado = {
            "es_primo": False,
            "titulo": "El número 0 no es primo",
            "resumen": "El 0 no es mayor que 1 y tiene infinitos divisores; no tiene una factorización prima definida.",
            "pasos": ["Un número primo debe ser mayor que 1.", "Todo entero distinto de cero divide al 0.", "Por lo tanto, el 0 no es primo."],
            "divisores_muestra": [],
            "total_divisores": -1,
            "factorizacion": "Indefinida.",
        }
    elif n == 1:
        estado = {
            "es_primo": False,
            "titulo": "El número 1 no es primo",
            "resumen": "El 1 solo tiene un divisor positivo. Un número primo debe tener exactamente dos divisores positivos distintos.",
            "pasos": ["El único divisor positivo de 1 es 1.", "Un primo debe tener dos divisores positivos distintos.", "Por lo tanto, 1 no es primo ni compuesto."],
            "divisores_muestra": [1],
            "total_divisores": 1,
            "factorizacion": "1 (unidad; no es primo ni compuesto).",
        }
    elif n == 2:
        estado = {
            "es_primo": True,
            "titulo": "¡El número 2 es primo!",
            "resumen": "El 2 es el único número primo par: sus únicos divisores positivos son 1 y 2.",
            "pasos": ["2 es mayor que 1.", "Sus divisores positivos son 1 y 2.", "Tiene exactamente dos divisores positivos, así que es primo."],
            "divisores_muestra": [1, 2],
            "total_divisores": 2,
            "factorizacion": "2 (primo).",
        }
    else:
        raiz = math.isqrt(n)
        raiz_aprox = math.sqrt(n)
        factores = factorizar_numero(n)
        divisor = min(factores) if sum(factores.values()) > 1 else None
        muestra, total = obtener_divisores(factores)
        factorizacion = formato_factorizacion(factores)
        if divisor is not None:
            cociente = n // divisor
            estado = {
                "es_primo": False,
                "titulo": f"El número {n} no es primo (es compuesto)",
                "resumen": f"Es divisible exactamente entre {divisor}: {n} = {divisor} × {cociente}.",
                "pasos": [
                    f"Se revisan los divisores posibles hasta √{n} ≈ {raiz_aprox:.3f}.",
                    f"Se encontró {divisor}, que divide a {n} sin residuo.",
                    f"{n} = {divisor} × {cociente}, así que tiene divisores adicionales a 1 y a sí mismo.",
                ],
                "divisores_muestra": muestra,
                "total_divisores": total,
                "factorizacion": factorizacion,
            }
        else:
            estado = {
                "es_primo": True,
                "titulo": f"¡El número {n} es primo!",
                "resumen": f"No se encontraron divisores entre 2 y √{n} ≈ {raiz_aprox:.3f}; sus únicos divisores positivos son 1 y {n}.",
                "pasos": [
                    f"Se revisaron los divisores posibles hasta √{n} ≈ {raiz_aprox:.3f} (límite entero: {raiz}).",
                    "Ningún entero de ese rango divide al número exactamente.",
                    "Si tuviera un divisor mayor que su raíz cuadrada, tendría uno complementario menor.",
                    f"Por lo tanto, sus únicos divisores son 1 y {n}: es primo.",
                ],
                "divisores_muestra": [1, n],
                "total_divisores": 2,
                "factorizacion": f"{n} (primo).",
            }

    estado["tiempo_ms"] = (time.perf_counter() - inicio) * 1000
    return estado


def mostrar_resultado(resultado: dict, numero: int) -> None:
    """Presenta el análisis en la interfaz de Streamlit."""
    if resultado["es_primo"]:
        st.success(f"✅ {resultado['titulo']}")
    else:
        st.error(f"❌ {resultado['titulo']}")
    st.write(resultado["resumen"])

    col_factor, col_divisores, col_tiempo = st.columns(3)
    col_factor.metric("Factorización prima", resultado["factorizacion"])
    total = resultado["total_divisores"]
    col_divisores.metric("Divisores positivos", "Infinitos" if total == -1 else str(total))
    col_tiempo.metric("Tiempo de cálculo", f"{resultado['tiempo_ms']:.4f} ms")

    if total > 0:
        divisores = ", ".join(map(str, resultado["divisores_muestra"]))
        if total > len(resultado["divisores_muestra"]):
            divisores += f" … (primeros {len(resultado['divisores_muestra'])} de {total})"
        st.caption(f"Divisores positivos: {divisores}")

    with st.expander("Ver explicación paso a paso", expanded=True):
        for paso in resultado["pasos"]:
            st.markdown(f"- {paso}")


st.set_page_config(page_title="Verificador de números primos", page_icon="🔢", layout="centered")
st.title("🔢 Verificador de números primos")
st.markdown("Escribe un número entero para saber si es primo y consultar una explicación matemática paso a paso.")

if "numero" not in st.session_state:
    st.session_state.numero = 17
if "analizar_aleatorio" not in st.session_state:
    st.session_state.analizar_aleatorio = False


def preparar_numero_aleatorio() -> None:
    st.session_state.numero = random.randint(2, 5000)
    st.session_state.analizar_aleatorio = True

with st.form("formulario_primos"):
    numero = st.number_input(
        "Número entero",
        min_value=-LIMITE,
        max_value=LIMITE,
        step=1,
        value=st.session_state.numero,
        key="numero",
        help="Se aceptan enteros entre −1 000 000 000 000 y 1 000 000 000 000.",
    )
    comprobar = st.form_submit_button("🔍 Comprobar número", type="primary", use_container_width=True)

col_azar, col_info = st.columns([1, 3])
with col_azar:
    st.button("🎲 Probar uno al azar", on_click=preparar_numero_aleatorio, use_container_width=True)
with col_info:
    st.caption("El análisis por divisibilidad llega hasta la raíz cuadrada del número.")

if comprobar or st.session_state.analizar_aleatorio:
    st.session_state.analizar_aleatorio = False
    numero = st.session_state.numero
    with st.spinner("Analizando divisores…"):
        analisis = analizar_primalidad(int(numero))
    mostrar_resultado(analisis, int(numero))

st.divider()
st.caption("Un número primo es un entero mayor que 1 con exactamente dos divisores positivos: 1 y él mismo.")
