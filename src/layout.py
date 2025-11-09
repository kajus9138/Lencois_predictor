import streamlit as st


def exibir_cabecalho():
    """
    Exibe o cabeçalho da aplicação com dois logos e título centralizado.
    """
    # CSS Global para estilização do cabeçalho
    st.markdown("""
        <style>
        
            .stApp {
                background-color: #fff;
                font-family: 'Gill Sans', sans-serif;
                font-weight: 400;
            }

            .block-container {
                max-width: 80% !important;
                padding-left: 1rem;
                padding-right: 1rem;
            }

            /* Centralização vertical das colunas */
            [data-testid="column"] {
                display: flex;
                align-items: center;
                justify-content: center;
            }

            .cabecalho {
                display: flex;
                align-items: center;
                justify-content: center;
                background-color: transparent;
                padding: 10px 20px;
                flex-direction: column;
                text-align: center;
            }

            .cabecalho h1 {
                margin: 0;
                padding: 0;
                font-size: 55px;
                color: #575757;
                font-weight: 600;
                line-height: 1.2;
            }

            .subtitulo {
                font-size: 45px !important;
                color: #23517a !important;
                text-align: center;
                margin-top: 10px;
                padding: 0; !important;
                margin-bottom: 10px;
                font-weight: 400;
                align-items: center;
            }
            
            /* Esconde o elemento de emoção do Streamlit */
            [data-testid="stMarkdownContainer"] span[data-testid*="emotion"] {
                display: none !important;
            }

            /* Controle do tamanho das imagens */
            .img-container img {
                max-width: 150px;
                height: auto;
                display: block;
                margin: 0 auto;
            }

            /* Remove espaços extras do Streamlit */
            .stImage {
                margin: 0 !important;
            }

        </style>

    """, unsafe_allow_html=True)

    # Criação de 3 colunas para alinhar os elementos
    col1, col2, col3 = st.columns([1.2, 3, 1])

    with col1:
        st.markdown("<div class='img-container'>", unsafe_allow_html=True)
        st.image("Univesp2.png", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div class="cabecalho">
                <h1>Monitoramento Hidrológico<br>Rio Lençóis</h1>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("<div class='img-container'>", unsafe_allow_html=True)
        st.image("Lencois_Paulista.png", use_container_width=False, width=150)
        st.markdown("</div>", unsafe_allow_html=True)
     
    # Subtítulo centralizado   
    st.markdown('<div class="subtitulo">Previsão e acompanhamento dos níveis fluviais</div>', unsafe_allow_html=True)

    # Linha divisória abaixo do cabeçalho
    st.markdown("<hr style='margin-top: 10px; margin-bottom: 30px; border: 1px solid #ddd;'>", unsafe_allow_html=True)