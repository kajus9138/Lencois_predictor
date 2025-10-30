import pandas as pd
import matplotlib.dates as mdates
import matplotlib.patches as patches
import streamlit as st


# ==========================
# Função para estilizar um gráfico (ax)
# ==========================
def aplicar_estilo(ax, titulo: str):
    """Aplica fundo arredondado e cores padrão"""
    bg = patches.FancyBboxPatch(
        (0, 0), 1, 1,
        boxstyle="round,pad=0.03,rounding_size=20",
        transform=ax.transAxes,
        facecolor='#D6E8F7',
        edgecolor='none',
        zorder=-1
    )
    ax.add_patch(bg)
    ax.set_facecolor('#D6E8F7')
    ax.grid(True, linestyle='--', alpha=0.4)
    ax.set_title(titulo, color='#2C4A6B', fontsize=13, fontweight='bold', pad=10)
    ax.tick_params(colors='#2C4A6B', labelsize=9)
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
    ax.tick_params(axis='x', rotation=45)
    ax.set_xlabel("Data", color='#2C4A6B', fontsize=10)
    ax.set_ylabel("Nível (cm)", color='#2C4A6B', fontsize=10)
    for spine in ax.spines.values():
        spine.set_visible(False)       
      
        
def direitos_autorais():
    st.markdown("""
        <div class="direitos-autorais" style="text-align: center; font-size: 20px; color: #888888; margin-top: 20px;">
            © Desenvolvido pela UNIVESP em parceria com o Município de Lençóis Paulista.
        </div>
    """, unsafe_allow_html=True)       
