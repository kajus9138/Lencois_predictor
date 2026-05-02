import streamlit as st

def exibir_cabecalho():
    """
    Exibe o cabeçalho da aplicação com dois logos e título centralizado.
    """
    # Criação de 3 colunas para alinhar os elementos
    col1, col2, col3 = st.columns([2, 3, 1.5])

    with col1:
        st.image("Univesp2.png",
                use_container_width=True,  # ocupa a coluna inteira
                output_format="auto")
        
    

    with col2:
        st.markdown(
            """
            <div style='text-align: center;'>
                <h1 style='color: #003366;'>Monitoramento Hidrológico — Rio Lençóis</h1>
                <h4 style='color: gray;'>Previsão e acompanhamento dos níveis fluviais</h4>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.image("Lencois_Paulista.png",
                use_container_width=True,  # ocupa a coluna inteira
                output_format="auto")

    # Linha divisória abaixo do cabeçalho
    st.markdown("<hr style='margin-top: 10px; margin-bottom: 30px;'>", unsafe_allow_html=True)