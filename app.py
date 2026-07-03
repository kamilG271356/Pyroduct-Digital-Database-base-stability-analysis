import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# --- 1. KONFIGURACJA ---
st.set_page_config(layout="wide", page_title="Gravity Analysis")
st.title("Comparative analysis of scenarios")

# --- 2. FUNKCJE WCZYTYWANIA DANYCH ---

@st.cache_data
def load_data(file_path):
    """Wczytuje główne pliki wynikowe."""
    if not os.path.exists(file_path):
        return None
    try:
        df = pd.read_csv(file_path, sep=',', header=None, engine='python', on_bad_lines='skip')
        # Dodajemy oryginalny indeks wiersza (użyteczny przy debugowaniu)
        df['orig_row_index'] = range(1, len(df) + 1)
        return df
    except Exception as e:
        st.error(f"Błąd pliku {file_path}: {e}")
        return None

def get_profile_data(file_path, row_idx):
    if not os.path.exists(file_path):
        st.error(f"Nie znaleziono pliku: {file_path}")
        return None, None
    try:
        import numpy as np
        import plotly.graph_objects as go
        
        # 1. Wczytujemy dane (NumPy genfromtxt radzi sobie z brakującymi danymi lepiej)
        dane = np.genfromtxt(file_path, delimiter=',')
        
        # 2. Konwersja row_idx na liczbę (zabezpieczenie przed tekstem)
        try:
            p_idx = int(float(str(row_idx).strip()))
        except ValueError:
            st.error(f"Błąd: '{row_idx}' nie jest poprawnym numerem profilu!")
            return None, None
        
        # 3. Logika kolumn (Poprawiona: MATLAB vs Python)
        # Jeśli MATLAB row 1 -> kolumny 2 i 3, to w Pythonie indeksy 1 i 2
        cx = (p_idx * 2) -2
        cy = (p_idx * 2) -1
        
        # Sprawdzenie zakresu kolumn
        if cy >= dane.shape[1]:
            st.warning(f"Indeks {cy} poza zakresem (plik ma {dane.shape[1]} kolumn)")
            return None, None

        # 4. Wyciągamy dane
        x = dane[:, cx]
        y = dane[:, cy]
        
        return x, y

    except Exception as e:
        st.error(f"Błąd przy czytaniu kordów: {e}")
        return None, None

# --- 3. DEFINICJA SCENARIUSZY I ŚCIEŻEK ---
scenariusze = {
    "Scenario A1 (Roof 1m, strong rock)": "dane/wynik_1m.txt",
    "Scenario A2 (Roof 5m, strong rock)": "dane/wynik_5m.txt",
    "Scenario A3 (Roof 10m, strong rock)": "dane/wynik_10m.txt",
    "Scenario B1 (Roof 1m, weak rock)": "dane/wynik_1m_sb.txt",
    "Scenario B2 (Roof 5m, weak rock)": "dane/wynik_5m_sb.txt",
    "Scenario B3 (Roof 10m, weak rock)": "dane/wynik_10m_sb.txt"
}

Krzywe_mid = {
    "Scenario A1 (Roof 1m, strong rock)": "dane/mid_curve_1m_mc.txt",
    "Scenario A2 (Roof 5m, strong rock)": "dane/mid_curve_5m_mc.txt",
    "Scenario A3 (Roof 10m, strong rock)": "dane/mid_curve_10m_mc.txt",
    "Scenario B1 (Roof 1m, weak rock)": "dane/mid_curve_1m_sb.txt",
    "Scenario B2 (Roof 5m, weak rock)": "dane/mid_curve_5m_sb.txt",
    "Scenario B3 (Roof 10m, weak rock)": "dane/mid_curve_10m_sb.txt"
}
Krzywe_up = {
    "Scenario A1 (Roof 1m, strong rock)": "dane/up_curve_1m_mc.txt",
    "Scenario A2 (Roof 5m, strong rock)": "dane/up_curve_5m_mc.txt",
    "Scenario A3 (Roof 10m, strong rock)": "dane/up_curve_10m_mc.txt",
    "Scenario B1 (Roof 1m, weak rock)": "dane/up_curve_1m_sb.txt",
    "Scenario B2 (Roof 5m, weak rock)": "dane/up_curve_5m_sb.txt",
    "Scenario B3 (Roof 10m, weak rock)": "dane/up_curve_10m_sb.txt"
}
Krzywe_down = {
    "Scenario A1 (Roof 1m, strong rock)": "dane/down_curve_1m_mc.txt",
    "Scenario A2 (Roof 5m, strong rock)": "dane/down_curve_5m_mc.txt",
    "Scenario A3 (Roof 10m, strong rock)": "dane/down_curve_10m_mc.txt",
    "Scenario B1 (Roof 1m, weak rock)": "dane/down_curve_1m_sb.txt",
    "Scenario B2 (Roof 5m, weak rock)": "dane/down_curve_5m_sb.txt",
    "Scenario B3 (Roof 10m, weak rock)": "dane/down_curve_10m_sb.txt"
}
# --- 4. PASEK BOCZNY (SIDEBAR) ---
st.sidebar.header("Choose a scenario")
wybrane_scenariusze = [n for n in scenariusze.keys() if st.sidebar.checkbox(n, value=(n == "Scenario 1 (1m)"))]

# --- 5. WYKRES GŁÓWNY ---
if not wybrane_scenariusze:
    st.warning("Select at least one scenario in the sidebar")
else:
    fig = go.Figure()

    for nazwa in wybrane_scenariusze:
        # A. RYSOWANIE PUNKTÓW (DANE POMIAROWE)
        df_p = load_data(scenariusze[nazwa])
        if df_p is not None:
            try:
                # Kolumna 1 (indeks 0): Multiplier (Y)
                # Kolumna 5 (indeks 4): B [m] (X)
                # Kolumna 6 (indeks 5): Nr Profilu (Info)
                y_val = pd.to_numeric(df_p[0], errors='coerce')
                x_val = pd.to_numeric(df_p[4], errors='coerce')
                info_val = df_p[5] if 5 in df_p.columns else "0"
                
                mask = y_val > 0 # Ważne dla skali logarytmicznej
                
                fig.add_trace(go.Scatter(
                    x=x_val[mask], 
                    y=y_val[mask],
                    mode='markers',
                    marker=dict(size=4),
                    name=f"{nazwa} (Pkt)",
                    customdata=list(zip(df_p['orig_row_index'][mask], info_val[mask])),
                    hovertemplate="B: %{x}<br>Y: %{y}<br>Row: %{customdata[0]}<extra></extra>"
                ))
            except Exception as e:
                st.error(f"Błąd formatu danych punktowych w {nazwa}: {e}")

        # B. RYSOWANIE KRZYWYCH (FUNKCJA POMOCNICZA)
        def add_curve(file_dict, suffix, color, dash=None):
            df_c = load_data(file_dict[nazwa])
            if df_c is not None and len(df_c.columns) >= 2:
                x_c = pd.to_numeric(df_c[0], errors='coerce')
                y_c = pd.to_numeric(df_c[1], errors='coerce')
                c_mask = y_c > 0
                fig.add_trace(go.Scatter(
                    x=x_c[c_mask], y=y_c[c_mask],
                    mode='lines', 
                    name=f"{nazwa} {suffix}",
                    line=dict(color=color, width=1, dash=dash),
                    hoverinfo='skip'
                ))

        add_curve(Krzywe_mid, "MID", "black")
        add_curve(Krzywe_up, "UP", "gray", "dash")
        add_curve(Krzywe_down, "DOWN", "gray", "dash")

    fig.update_layout(
        yaxis_type="log",
        xaxis_title="B [m]",
        yaxis_title="G [-]",
        height=600,
        template="plotly_white",
        clickmode='event+select',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    # Wyświetlenie wykresu i przechwycenie interakcji
    selected = st.plotly_chart(fig, use_container_width=True, on_select="rerun")

    # --- 6. DETALE (PO KLIKNIĘCIU W PUNKT) ---
    if selected and "selection" in selected and len(selected["selection"]["points"]) > 0:
        st.divider()
        st.subheader("Detailed analysis of selected point")
        
        for point in selected["selection"]["points"]:
            # Pobranie danych z customdata zapisanego w ścieżce Scatter
            # customdata[0] = row_index, customdata[1] = row_desc (nr profilu)
            row_nr, row_desc = point.get('customdata', [0, "0"])
            
            with st.expander(f"Row: {row_nr} (Profil {row_desc})", expanded=True):
                c1, c2 = st.columns(2)
                c1.metric("B [m] (X Axis)", f"{point['x']:.2f}")
                c2.metric("Gravity Multiplier (Y Axis)", f"{point['y']:.4e}")

 # Wykres profilu geometrycznego
                x_prof, y_prof = get_profile_data("dane_kord.txt", row_nr)
                
                if x_prof is not None and y_prof is not None:
                    # 1. Tworzymy wykres
                    sub = go.Figure()
                    sub.add_trace(go.Scatter(
                        x=x_prof, 
                        y=y_prof, 
                        mode='lines+markers', 
                        line=dict(color='firebrick'),
                        name="Profil"
                    ))
                    sub.update_layout(
                        height=500, 
                        template="plotly_white",
                        title=f"Profile geometry {row_desc}",
                        xaxis_title="X [m]",
                        yaxis_title="Y [m]",
                        yaxis=dict(scaleanchor="x", scaleratio=1)
                    )
                    st.plotly_chart(sub, use_container_width=True)

                    # 2. DODAJEMY TABELĘ PUNKTÓW
                    with st.expander("Coordinate data table"):
                        # Tworzymy DataFrame z serii NumPy
                        df_coords = pd.DataFrame({
                            "X [m]": x_prof,
                            "Y [m]": y_prof
                        })
                        # Wyświetlamy tabelę
                        st.dataframe(df_coords, use_container_width=True)
                else:
                    st.info(f"No profile data for index {row_desc}")
