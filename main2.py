import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# 🎨 Настройка стилей
st.set_page_config(page_title="Профиль рельефа", layout="wide")
st.markdown("""
<style>
    .main-header {font-size: 1.8rem; font-weight: 700; color: #1E293B; margin-bottom: 20px;}
    /* Стили для имитации кружков (расстояния) */
    div[data-testid="stNumberInput"] label { font-size: 0.8rem; color: #64748B; }
    .dist-label { 
        background: #EFF6FF; border-radius: 50%; width: 40px; height: 40px; 
        display: flex; align-items: center; justify-content: center; 
        border: 2px solid #3B82F6; margin: 0 auto; font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🏔️ Цепочка высотных отметок</div>', unsafe_allow_html=True)

# --- 1. ВВОД ГЕОМЕТРИИ (Сетка как на рисунке) ---
st.subheader("📍 Конфигурация профиля")

# Создаем 4 точки (A, B, C, D) и расстояния между ними
col1, space1, col2, space2, col3, space3, col4 = st.columns([2, 1, 2, 1, 2, 1, 2])

with col1:
    h_a = st.number_input("Высота A", value=144.0, format="%.3f", key="h_a")
with space1:
    st.markdown("<div style='text-align: center;'>↔️</div>", unsafe_allow_html=True)
    d_ab = st.number_input("A—B", value=50.0, min_value=0.1, key="d_ab", label_visibility="collapsed")
with col2:
    h_b = st.number_input("Высота B", value=145.5, format="%.3f", key="h_b")
with space2:
    st.markdown("<div style='text-align: center;'>↔️</div>", unsafe_allow_html=True)
    d_bc = st.number_input("B—C", value=30.0, min_value=0.1, key="d_bc", label_visibility="collapsed")
with col3:
    h_c = st.number_input("Высота C", value=143.2, format="%.3f", key="h_c")
with space3:
    st.markdown("<div style='text-align: center;'>↔️</div>", unsafe_allow_html=True)
    d_cd = st.number_input("C—D", value=40.0, min_value=0.1, key="d_cd", label_visibility="collapsed")
with col4:
    h_d = st.number_input("Высота D", value=146.0, format="%.3f", key="h_d")

st.markdown("---")

# --- 2. ЗАПРОСЫ ВЫСОТ (Раздельные ячейки) ---
st.subheader("🔍 Запросить высоты на дистанциях")
q_col1, q_col2, q_col3 = st.columns(3)

with q_col1:
    q_ab = st.text_input(f"На отрезке A-B (max {d_ab}м)", value="10, 15, 20")
with q_col2:
    q_bc = st.text_input(f"На отрезке B-C (max {d_bc}м)", value="18, 19.7")
with q_col3:
    q_cd = st.text_input(f"На отрезке C-D (max {d_cd}м)", value="")

# --- 3. ЛОГИКА РАСЧЕТА ---
if st.button("📊 Рассчитать профиль", type="primary", use_container_width=True):
    # Координаты узловых точек (накопительным итогом)
    x_coords = [0, d_ab, d_ab + d_bc, d_ab + d_bc + d_cd]
    y_coords = [h_a, h_b, h_c, h_d]
    labels = ["A", "B", "C", "D"]

    # Парсинг запросов
    def parse_queries(raw_str, offset, limit):
        try:
            vals = [float(x.strip()) for x in raw_str.split(",") if x.strip()]
            # Фильтруем, чтобы не выходили за пределы сегмента
            return [x + offset for x in vals if 0 <= x <= limit]
        except: return []

    q_points = []
    q_points += parse_queries(q_ab, 0, d_ab)
    q_points += parse_queries(q_bc, d_ab, d_bc)
    q_points += parse_queries(q_cd, d_ab + d_bc, d_cd)

    if q_points:
        # Интерполяция
        interp_y = np.interp(q_points, x_coords, y_coords)
        res_df = pd.DataFrame({"Дистанция от A (м)": q_points, "Высота (м)": interp_y})
        
        # График
        fig = go.Figure()
        # Линия рельефа
        fig.add_trace(go.Scatter(x=x_coords, y=y_coords, mode='lines+markers+text', 
                                 text=labels, textposition="top center",
                                 name='Узлы', line=dict(color='#1E293B', width=3)))
        # Запрошенные точки
        fig.add_trace(go.Scatter(x=q_points, y=interp_y, mode='markers', 
                                 name='Запросы', marker=dict(color='#EF4444', size=12, symbol='x')))
        
        fig.update_layout(template="plotly_white", height=400, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)
        
        # Таблица
        st.dataframe(res_df.style.format("{:.3f}"), use_container_width=True)
    else:
        st.info("Введите значения в поля запросов выше, чтобы увидеть расчетные точки.")
