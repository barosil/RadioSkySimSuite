import panel as pn
import holoviews as hv
import numpy as np

hv.extension("bokeh")

# ---------------------------------------
# Simulação: ganho x frequência x polarização
# (depois trocamos por dados reais do Radiotelescope)
# ---------------------------------------
frequencies = np.linspace(1, 10, 200)  # GHz
polarizations = ["H", "V"]

def compute_gain(f, pol, metric="Máximo"):
    if metric == "Máximo":
        return 20 * np.log10(np.sinc(f - (5 if pol == "H" else 6)))
    elif metric == "Médio":
        return 10 * np.log10(np.abs(np.sinc(f - (5 if pol == "H" else 6))))
    elif metric == "Boresight":
        return -3 * np.abs(f - (5 if pol == "H" else 6))
    else:
        return np.zeros_like(f)

# ---------------------------------------
# Função de plot
# ---------------------------------------
def plot_ganho(metric):
    curves = []
    for pol in polarizations:
        y = compute_gain(frequencies, pol, metric)
        curves.append(
            hv.Curve((frequencies, y), kdims=["Frequência (GHz)"], vdims=["Ganho (dB)"])
              .opts(title="Ganho x Frequência", line_width=2, width=700, height=400)
              .relabel(f"Polarização {pol}")
        )
    return hv.Overlay(curves).opts(legend_position="top_left")

# ---------------------------------------
# Widgets + Binding
# ---------------------------------------
metric_select = pn.widgets.Select(name="Métrica de Ganho", options=["Máximo", "Médio", "Boresight"], value="Máximo")
interactive_plot = pn.bind(plot_ganho, metric=metric_select)

# ---------------------------------------
# Layout do painel
# ---------------------------------------
gain_panel = pn.Column(
    "## 📡 Ganho x Frequência",
    metric_select,
    interactive_plot
)

# Para servir isolado:
if __name__ == "__main__":
    pn.extension()
    gain_panel.show()
