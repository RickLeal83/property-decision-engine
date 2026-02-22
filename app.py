"""
Property Decision Engine - MVP Streamlit
Motor VHE-1 completo con generación de documento
"""

import streamlit as st
import re
import json
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from enum import Enum

# ============================================
# CONFIGURACIÓN DE PÁGINA
# ============================================
st.set_page_config(
    page_title="Property Decision Engine",
    page_icon="🏢",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ============================================
# MODELOS Y CLASES
# ============================================

class AnclaVHE1(Enum):
    OBJETIVO = "objetivo_dominante"
    TENSION = "tension_emocional_activa"
    HORIZONTE = "horizonte_operativo_real"
    FRICCION = "capacidad_de_friccion"

@dataclass
class VHE1Detectado:
    objetivo_dominante: Optional[str] = None
    tension_emocional_activa: Optional[str] = None
    horizonte_operativo_real: Optional[int] = None
    capacidad_de_friccion: Optional[float] = None
    confianzas: Dict = field(default_factory=dict)
    
    def completo(self) -> bool:
        return all([
            self.objetivo_dominante,
            self.tension_emocional_activa,
            self.horizonte_operativo_real,
            self.capacidad_de_friccion
        ])
    
    def faltantes(self) -> List[str]:
        faltan = []
        if not self.objetivo_dominante: faltan.append("objetivo")
        if not self.tension_emocional_activa: faltan.append("tensión emocional")
        if not self.horizonte_operativo_real: faltan.append("horizonte temporal")
        if not self.capacidad_de_friccion: faltan.append("capacidad de fricción")
        return faltan

@dataclass
class UnidadPortafolio:
    id: str
    nombre: str
    inmobiliaria: str
    comuna: str
    cuadrante: str
    tipologia: str
    metraje: float
    precio_uf: float
    meses_entrega: int
    arriendo_estimado: float
    estrategia: str
    diferencial_estimado: float
    inflexion_anios: float
    
    def precio_clp(self, uf: float = 36500) -> float:
        return self.precio_uf * uf

# ============================================
# BASE DE DATOS EJEMPLO
# ============================================

PORTAFOLIO = [
    UnidadPortafolio(
        id="POR-001",
        nombre="Edificio Portugal",
        inmobiliaria="Inmobiliaria X",
        comuna="Santiago",
        cuadrante="Portugal",
        tipologia="1D",
        metraje=42.0,
        precio_uf=2600,
        meses_entrega=14,
        arriendo_estimado=420000,
        estrategia="PLUSVALIA_MIXTA_OBRA_OPERACION",
        diferencial_estimado=-180000,
        inflexion_anios=6.5
    ),
    UnidadPortafolio(
        id="FLD-001",
        nombre="Condominio La Florida",
        inmobiliaria="Desarrolladora Y",
        comuna="La Florida",
        cuadrante="Vicente Valdés",
        tipologia="Estudio",
        metraje=35.0,
        precio_uf=2200,
        meses_entrega=0,
        arriendo_estimado=380000,
        estrategia="CASHFLOW_KING_ENTREGA",
        diferencial_estimado=50000,
        inflexion_anios=0
    ),
    UnidadPortafolio(
        id="MAT-001",
        nombre="Proyecto Mata",
        inmobiliaria="Grupo Z",
        comuna="Santiago",
        cuadrante="Mata",
        tipologia="2D",
        metraje=58.0,
        precio_uf=3100,
        meses_entrega=24,
        arriendo_estimado=480000,
        estrategia="PLUSVALIA_OBRA_PREMIUM",
        diferencial_estimado=-250000,
        inflexion_anios=8.0
    )
]# ============================================
# MOTOR VHE-1
# ============================================

class DetectorVHE1:
    
    OBJETIVOS = {
        "prevision_jubilacion": ["jubilación", "pensión", "jubilar", "vejez", "no depender"],
        "flujo_mensual": ["renta mensual", "ingreso mensual", "flujo", "complementar sueldo", "pagar cuentas"],
        "plusvalia_patrimonial": ["crecer valor", "plusvalía", "vender más caro", "patrimonio", "herencia"],
        "liquidez_seguridad": ["liquidez", "disponible", "sacar plata", "emergencia", "por si acaso"]
    }
    
    TENSIONES = {
        "aversion_deuda_alta": ["bajo ninguna circunstancia", "nunca más deuda", "pánico deuda", "terror deber"],
        "aversion_deuda_media": ["no quiero deuda", "preferiría sin crédito", "liquidar pronto"],
        "ansiedad_incertidumbre": ["me angustia no saber", "estresa la incertidumbre", "quiero tener claro"],
        "experiencia_negativa": ["me quemé", "tuve mala experiencia", "la vez pasada", "problema con arriendo"]
    }
    
    def detectar(self, mensaje: str, vhe1_actual: VHE1Detectado) -> VHE1Detectado:
        v = vhe1_actual
        msg = mensaje.lower()
        
        # OBJETIVO
        if not v.objetivo_dominante:
            for obj, palabras in self.OBJETIVOS.items():
                if any(p in msg for p in palabras):
                    v.objetivo_dominante = obj
                    v.confianzas["objetivo"] = 0.85
                    break
        
        # TENSIÓN
        if not v.tension_emocional_activa:
            for ten, palabras in self.TENSIONES.items():
                if any(p in msg for p in palabras):
                    v.tension_emocional_activa = ten
                    v.confianzas["tension"] = 0.8
                    break
        
        # HORIZONTE (edad)
        if not v.horizonte_operativo_real:
            match = re.search(r"tengo (\d+)\s*añ?os", msg)
            if match:
                edad = int(match.group(1))
                v.horizonte_operativo_real = max(0, 65 - edad)
                v.confianzas["horizonte"] = 0.9
        
        # FRICCIÓN
        if not v.capacidad_de_friccion:
            match = re.search(r"(?:sostuve|mantuve|aguante|pagué)\s*.*?(\d+)\s*(?:mil|k)?", msg)
            if match:
                monto = int(match.group(1))
                if "millon" in msg:
                    monto *= 1000000
                elif monto < 1000:
                    monto *= 1000
                v.capacidad_de_friccion = monto
                v.confianzas["friccion"] = 0.9
        
        return v
    
    def pregunta_siguiente(self, vhe1: VHE1Detectado) -> str:
        faltan = vhe1.faltantes()
        
        if "objetivo" in faltan:
            return "¿Buscas principalmente generar ingreso mensual, que tu inversión crezca de valor, o seguridad para el futuro?"
        
        if "tensión emocional" in faltan:
            return "¿Qué te genera más inquietud: la idea de tener deuda, o que tu dinero pierda valor guardado?"
        
        if "horizonte temporal" in faltan:
            return "¿En cuántos años esperas dejar de trabajar activamente?"
        
        if "capacidad de fricción" in faltan:
            return "Si tuvieras que sostener un gasto mensual adicional por un tiempo, ¿hasta dónde podrías llegar sin que te afecte la tranquilidad? (¿Has pasado por algo similar?)"
        
        return None

class EvaluadorEstrategia:
    
    def evaluar(self, unidad: UnidadPortafolio, vhe1: VHE1Detectado, uf: float = 36500) -> dict:
        
        tensiones = []
        
        # Validar fricción
        if vhe1.capacidad_de_friccion:
            diff = abs(unidad.diferencial_estimado)
            limite = vhe1.capacidad_de_friccion
            
            if diff > limite * 1.3:
                tensiones.append({
                    "tipo": "friccion_excesiva",
                    "descripcion": f"Diferencial ${diff:,.0f} supera tu límite ${limite:,.0f} en más de 30%",
                    "severidad": "ALTA",
                    "compromiso": "Reconsiderar capacidad o buscar alternativa"
                })
            elif diff > limite:
                tensiones.append({
                    "tipo": "friccion_limite",
                    "descripcion": f"${diff:,.0f} es {diff/limite:.0%} de tu experiencia previa",
                    "severidad": "MEDIA",
                    "compromiso": "Validar que puedes sostener esto 24+ meses"
                })
        
        # Validar horizonte
        if vhe1.horizonte_operativo_real:
            if unidad.inflexion_anios > vhe1.horizonte_operativo_real * 0.9:
                tensiones.append({
                    "tipo": "horizonte_ajustado",
                    "descripcion": f"Inflexión año {unidad.inflexion_anios}, tu horizonte es {vhe1.horizonte_operativo_real} años",
                    "severidad": "MEDIA",
                    "compromiso": "Confirmar estabilidad laboral, no anticipar cambios"
                })
        
        # Determinar estado
        if any(t["severidad"] == "ALTA" for t in tensiones):
            estado = "NO_VIABLE"
        elif tensiones:
            estado = "VIABLE_CON_TENSIONES"
        else:
            estado = "VIABLE"
        
        return {
            "estado": estado,
            "unidad": unidad,
            "tensiones": tensiones,
            "estrategia": unidad.estrategia,
            "diferencial": unidad.diferencial_estimado,
            "inflexion": unidad.inflexion_anios,
            "precio_clp": unidad.precio_clp(uf)
        }# ============================================
# UI STREAMLIT
# ============================================

def init_session():
    if 'vhe1' not in st.session_state:
        st.session_state.vhe1 = VHE1Detectado()
    if 'historial' not in st.session_state:
        st.session_state.historial = []
    if 'unidad_seleccionada' not in st.session_state:
        st.session_state.unidad_seleccionada = None
    if 'evaluacion' not in st.session_state:
        st.session_state.evaluacion = None
    if 'mostrar_documento' not in st.session_state:
        st.session_state.mostrar_documento = False

def render_header():
    st.title("🏢 Property Decision Engine")
    st.markdown("""
    *Sistema de decisión patrimonial inmobiliaria*
    
    Este sistema no vende propiedades. Expone tensiones para que decidas con lucidez.
    """)

def render_puertas():
    st.subheader("¿Por dónde quieres partir?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔍 Ver proyectos disponibles", use_container_width=True):
            st.session_state.modo = "portafolio"
            st.rerun()
    
    with col2:
        if st.button("💡 Descubrir mi estrategia ideal", use_container_width=True):
            st.session_state.modo = "diagnostico"
            st.rerun()

def render_portafolio():
    st.subheader("Portafolio Q1 2024")
    
    col1, col2 = st.columns(2)
    with col1:
        comunas = list(set(u.comuna for u in PORTAFOLIO))
        comuna_sel = st.selectbox("Comuna", ["Todas"] + comunas)
    
    with col2:
        tipologias = list(set(u.tipologia for u in PORTAFOLIO))
        tipo_sel = st.selectbox("Tipología", ["Todas"] + tipologias)
    
    filtradas = PORTAFOLIO
    if comuna_sel != "Todas":
        filtradas = [u for u in filtradas if u.comuna == comuna_sel]
    if tipo_sel != "Todas":
        filtradas = [u for u in filtradas if u.tipologia == tipo_sel]
    
    for unidad in filtradas:
        with st.container():
            st.divider()
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**{unidad.nombre}**")
                st.caption(f"{unidad.comuna}, {unidad.cuadrante} | {unidad.tipologia}, {unidad.metraje}m²")
                st.caption(f"Entrega: {unidad.meses_entrega} meses")
                
                estrategia_label = {
                    "PLUSVALIA_MIXTA_OBRA_OPERACION": "⏳ Plusvalía Mixta",
                    "CASHFLOW_KING_ENTREGA": "💰 Cashflow King",
                    "PLUSVALIA_OBRA_PREMIUM": "🚀 Plusvalía Obra"
                }.get(unidad.estrategia, unidad.estrategia)
                
                st.info(estrategia_label)
            
            with col2:
                st.markdown(f"**{unidad.precio_uf:,.0f} UF**")
                st.caption(f"~${unidad.precio_clp():,.0f}")
                
                if st.button("¿Es para mí?", key=f"eval_{unidad.id}"):
                    st.session_state.unidad_seleccionada = unidad
                    st.session_state.modo = "evaluacion"
                    st.rerun()

def render_diagnostico():
    st.subheader("Descubrir tu estrategia ideal")
    
    detector = DetectorVHE1()
    vhe1 = st.session_state.vhe1
    
    if not vhe1.completo():
        progreso = len([a for a in [vhe1.objetivo_dominante, vhe1.tension_emocional_activa, 
                                    vhe1.horizonte_operativo_real, vhe1.capacidad_de_friccion] if a])
        st.progress(progreso / 4, text=f"Perfil completado: {progreso}/4")
        
        pregunta = detector.pregunta_siguiente(vhe1)
        if pregunta:
            st.markdown(f"**{pregunta}**")
            
            respuesta = st.text_input("Tu respuesta:", key="resp_diagnostico")
            if respuesta and st.button("Continuar"):
                st.session_state.vhe1 = detector.detectar(respuesta, vhe1)
                st.session_state.historial.append({"pregunta": pregunta, "respuesta": respuesta})
                st.rerun()
    else:
        st.success("✅ Perfil completo")
        st.json({
            "Objetivo": vhe1.objetivo_dominante,
            "Tensión": vhe1.tension_emocional_activa,
            "Horizonte": f"{vhe1.horizonte_operativo_real} años",
            "Fricción": f"${vhe1.capacidad_de_friccion:,.0f}/mes"
        })
        
        if st.button("Ver unidades que encajan"):
            st.session_state.modo = "portafolio"
            st.rerun()

def render_evaluacion():
    unidad = st.session_state.unidad_seleccionada
    vhe1 = st.session_state.vhe1
    evaluador = EvaluadorEstrategia()
    
    st.subheader(f"Evaluación: {unidad.nombre}")
    
    if not vhe1.completo():
        st.warning("Necesito entender tu situación antes de evaluar esta unidad.")
        detector = DetectorVHE1()
        pregunta = detector.pregunta_siguiente(vhe1)
        
        if pregunta:
            st.markdown(f"**{pregunta}**")
            respuesta = st.text_input("Tu respuesta:", key="resp_eval")
            if respuesta and st.button("Continuar"):
                st.session_state.vhe1 = detector.detectar(respuesta, vhe1)
                st.rerun()
        return
    
    evaluacion = evaluador.evaluar(unidad, vhe1)
    st.session_state.evaluacion = evaluacion
    
    col_estado = {
        "VIABLE": ("✅ VIABLE", "success"),
        "VIABLE_CON_TENSIONES": ("⚠️ VIABLE CON TENSIONES", "warning"),
        "NO_VIABLE": ("❌ NO VIABLE", "error")
    }
    
    label, tipo = col_estado[evaluacion["estado"]]
    st.markdown(f"## {label}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Diferencial mensual", f"${evaluacion['diferencial']:,.0f}")
    with col2:
        st.metric("Inflexión flujo positivo", f"Año {evaluacion['inflexion']}")
    
    if evaluacion["tensiones"]:
        st.subheader("Tensiones detectadas")
        for t in evaluacion["tensiones"]:
            with st.expander(f"[{t['severidad']}] {t['tipo'].replace('_', ' ').title()}"):
                st.write(t["descripcion"])
                st.caption(f"Compromiso: {t['compromiso']}")
    
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Generar documento de decisión", type="primary"):
            st.session_state.mostrar_documento = True
            st.rerun()
    
    with col2:
        if st.button("🔍 Ver otras opciones"):
            st.session_state.unidad_seleccionada = None
            st.session_state.modo = "portafolio"
            st.rerun()
    
    if st.session_state.mostrar_documento:
        render_documento(evaluacion, vhe1, unidad)

def render_documento(evaluacion: dict, vhe1: VHE1Detectado, unidad: UnidadPortafolio):
    st.divider()
    st.header("📄 DOCUMENTO DE DECISIÓN PATRIMONIAL")
    
    doc_id = f"DOC-{datetime.now().strftime('%Y%m%d-%H%M')}"
    st.caption(f"ID: {doc_id} | Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    estado_color = {"VIABLE": "green", "VIABLE_CON_TENSIONES": "orange", "NO_VIABLE": "red"}
    st.markdown(f"<h3 style='color: {estado_color[evaluacion['estado']]};'>"
                f"ESTADO: {evaluacion['estado'].replace('_', ' ')}</h3>", 
                unsafe_allow_html=True)
    
    st.subheader("TU SITUACIÓN DECLARADA")
    st.markdown(f"""
    - **Objetivo:** {vhe1.objetivo_dominante.replace('_', ' ').title()}
    - **Horizonte:** ~{vhe1.horizonte_operativo_real} años laborales
    - **Capacidad de fricción:** ${vhe1.capacidad_de_friccion:,.0f} mensuales
    - **Tensión principal:** {vhe1.tension_emocional_activa.replace('_', ' ').title()}
    """)
    
    st.subheader("ACTIVO ANALIZADO")
    st.markdown(f"""
    **{unidad.nombre}**  
    {unidad.comuna}, {unidad.cuadrante} | {unidad.tipologia}, {unidad.metraje}m²  
    **Valor:** {unidad.precio_uf:,.0f} UF (~${unidad.precio_clp():,.0f})  
    **Entrega:** {unidad.meses_entrega} meses  
    **Estrategia:** {unidad.estrategia.replace('_', ' ').title()}
    """)
    
    st.subheader("COMPROMISOS REQUERIDOS")
    for i, t in enumerate(evaluacion["tensiones"], 1):
        st.markdown(f"{i}. **{t['descripcion']}**")
        st.caption(f"Compromiso: {t['compromiso']}")
    
    if not evaluacion["tensiones"]:
        st.info("Estrategia alineada sin tensiones críticas.")
    
    st.subheader("ADVERTENCIAS")
    st.error("""
    ⚠️ Este documento no garantiza resultado positivo.  
    ⚠️ Los escenarios son ejercicios de coherencia, no predicciones.  
    ⚠️ La decisión final es tuya y solo tuya.  
    ⚠️ Recomendación: Releer en 48 horas antes de actuar.
    """)
    
    # Descargar
    doc_texto = f"""
DOCUMENTO DE DECISIÓN PATRIMONIAL
ID: {doc_id}
Fecha: {datetime.now().strftime('%d/%m/%Y')}

ESTADO: {evaluacion['estado']}

PERFIL:
- Objetivo: {vhe1.objetivo_dominante}
- Horizonte: {vhe1.horizonte_operativo_real} años
- Fricción máxima: ${vhe1.capacidad_de_friccion:,.0f}/mes

ACTIVO: {unidad.nombre}
- Precio: {unidad.precio_uf:,.0f} UF
- Estrategia: {unidad.estrategia}

TENSIONES:
{chr(10).join([f"- {t['descripcion']}" for t in evaluacion['tensiones']])}

Generado por Property Decision Engine MVP.
    """
    
    st.download_button(
        "⬇️ Descargar documento (TXT)",
        doc_texto,
        file_name=f"decision_{doc_id}.txt",
        mime="text/plain"
    )

def main():
    init_session()
    render_header()
    
    modo = st.session_state.get("modo", "inicio")
    
    if modo == "inicio":
        render_puertas()
    elif modo == "portafolio":
        if st.button("← Volver al inicio"):
            st.session_state.modo = "inicio"
            st.rerun()
        render_portafolio()
    elif modo == "diagnostico":
        if st.button("← Volver al inicio"):
            st.session_state.modo = "inicio"
            st.rerun()
        render_diagnostico()
    elif modo == "evaluacion":
        if st.button("← Volver al portafolio"):
            st.session_state.unidad_seleccionada = None
            st.session_state.modo = "portafolio"
            st.rerun()
        render_evaluacion()

if __name__ == "__main__":
    main()
