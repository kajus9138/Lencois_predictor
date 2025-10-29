import streamlit as st


def exibir_cabecalho():
    """
    Exibe o cabeçalho da aplicação com dois logos e título centralizado.
    """
    # CSS Global para estilização do cabeçalho
    st.markdown("""
        <style>
            @font-face{
                font-family: 'Poppins';
                src: url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&display=swap') format('truetype');
                font-weight: normal;
                font-style: normal;
            } 
            
            .stApp {
                background-color: #f0f2f6;
                font-family;
            }

            .block-container {
                max-width: 75% !important;
                padding-left: 2rem;
                padding-right: 2rem;
            }
            
            .cabecalho {
                display: flex;
                align-items: center;
                justify-content: space-between;
                background-color: #f5f8fa;
                padding: 10px 20px;
                border-radius: 10px;
            }
            
            .cabecalho h1 {
                margin-bottom: 0;
                font-size: 60px;
                color: #575757;
            }
            
            .stApp h4 {
                font-size: 38px;
                color: #23517a; 
            }
            
        </style>             
    """, unsafe_allow_html=True)

    # Criação de 3 colunas para alinhar os elementos
    col1, col2, col3 = st.columns([0.8, 3, 0.5])

    with col1:
        st.image("Univesp2.png",
                 use_container_width=True)  # ocupa a coluna inteira

    with col2:
        st.markdown(
            """
            <div class="cabecalho" style="flex-direction: column; text-align: center;">
                <h1>Monitoramento Hidrológico<br>Rio Lençóis</h1> 
            """,
            unsafe_allow_html=True)

    with col3:
        st.image("Lencois_Paulista.png",
                 use_container_width=True)  # ocupa a coluna inteira

    st.markdown(
        """
            <div style='text-align: center;'>
                <h4>Previsão e acompanhamento dos níveis fluviais</h4>
            """,
        unsafe_allow_html=True)

    # Linha divisória abaixo do cabeçalho
    st.markdown("<hr style='margin-top: 10px; margin-bottom: 30px;'>",
                unsafe_allow_html=True)
