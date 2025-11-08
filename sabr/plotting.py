import plotly.graph_objs as go
import numpy as np

def smile_figure(strikes, market_vals, model_vals, title: str, y_label: str):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=strikes, y=market_vals, mode='markers', name='Marché'))
    fig.add_trace(go.Scatter(x=strikes, y=model_vals, mode='lines', name='Modèle'))
    fig.update_layout(title=title, xaxis_title='Strike', yaxis_title=y_label, template='plotly_dark')
    return fig

def surface_figure(K_grid, expiries, Z, title: str = 'Nappe de volatilité 3D'):
    surf = go.Figure(data=[go.Surface(x=K_grid, y=expiries, z=Z)])
    surf.update_layout(scene=dict(xaxis_title='Strike', yaxis_title='Maturité (ans)', zaxis_title='Vol (annuelle)'),
                       title=title, template='plotly_dark', height=600)
    return surf
