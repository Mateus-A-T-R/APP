import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

# Configurações da Página
st.set_page_config(
    page_title="Checklist THMAX Ferramentas",
    page_icon="✅",
    layout="wide"
)

# Estado da sessão
if 'pagina' not in st.session_state:
    st.session_state.pagina = 'inicio'

# Estilos personalizados
st.markdown(
    """
    <style>
    .main {
        background-color: #ffffff;
    }
    h1, h2, h3, h4 {
        color: #4B0082;
        font-weight: bold;
        text-align: center;
    }
    .stButton>button {
        background-color: #FF0000;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        height: 3em;
        width: 100%;
        font-size: 20px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        color: #4B0082;
        background-color: #FF0000;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Página Inicial
if st.session_state.pagina == 'inicio':
    st.markdown("<br><br>", unsafe_allow_html=True)

    col_logo_esq, col_meio, col_logo_dir = st.columns([1, 2, 1])

    with col_logo_esq:
        st.image('image.png', width=380)  # Logo THMAX

    with col_meio:
        st.markdown("<h1>Bem-vindo ao sistema de checklist</h1>", unsafe_allow_html=True)
        st.markdown("<h2>THMAX Ferramentas</h2>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<h4 style='color:white;'>Controle diário de expedição com qualidade e agilidade.</h4>", unsafe_allow_html=True)
        st.markdown("<br><br>", unsafe_allow_html=True)

        if st.button('Entrar no Sistema'):
            st.session_state.pagina = 'sistema'

    with col_logo_dir:
        st.image('REDSCALE.png', width=380)  # Logo REDSCALE

# Página Interna (Checklist e Dashboards)
elif st.session_state.pagina == 'sistema':
    # Banco de dados
    try:
        df = pd.read_csv('checklist.csv')
        if 'Tarefa' in df.columns:
            df = df.drop(columns=['Tarefa'])
    except FileNotFoundError:
        df = pd.DataFrame(columns=['Data', 'Hora', 'Operador', 'Atividade', 'Status', 'Observação'])

    data_hoje = datetime.now().date().strftime("%Y-%m-%d")
    df_hoje = df[df['Data'] == data_hoje]

    # Botão Bonito de Voltar🔙
    voltar = st.button(' Voltar', key='voltar_topo')

    if voltar:
        st.session_state.pagina = 'inicio'

    # Barra lateral
    st.sidebar.image('image.png', width=300)
    pagina_selecionada = st.sidebar.radio('Menu', ['✅ Checklist', '📊 Dashboards'])

    lista_funcionarios = ["Mateus", "João", "Maria", "Carlos", "Ana"]
    operador = st.sidebar.selectbox('Selecione seu nome', lista_funcionarios)
    data_input = st.sidebar.date_input('Data', datetime.now())

    # Página de Preenchimento
    if pagina_selecionada == '✅ Checklist':
        if operador:
            df_operador = df_hoje[df_hoje['Operador'] == operador]

            if df_operador.empty:
                st.warning(f'⚠️ {operador}, você ainda não preencheu seu checklist hoje!')
            else:
                st.success(f'✅ {operador}, checklist já registrado hoje!')

        st.markdown("---")
        st.subheader('🛠️ Atividades do Dia')

        atividades = [
            "Separar mercadorias",
            "Emitir Nota Fiscal",
            "Guardar mercadorias no estoque",
            "Controle de estoque",
            "Recebimento"
        ]

        atividades_realizadas = []
        for atividade in atividades:
            if st.checkbox(atividade):
                atividades_realizadas.append(atividade)

        observacoes = st.text_area('Observações')

        if st.button('Salvar Checklist'):
            if operador and atividades_realizadas:
                hora_atual = datetime.now().strftime("%H:%M:%S")

                df_atividades = pd.DataFrame({
                    'Data': [data_input] * len(atividades_realizadas),
                    'Hora': [hora_atual] * len(atividades_realizadas),
                    'Operador': [operador] * len(atividades_realizadas),
                    'Atividade': atividades_realizadas,
                    'Status': ['Concluído'] * len(atividades_realizadas),
                    'Observação': [observacoes] * len(atividades_realizadas)
                })

                df = pd.concat([df, df_atividades], ignore_index=True)
                df.to_csv('checklist.csv', index=False)

                st.success('Checklist salvo com sucesso! ✅')
            else:
                st.warning('⚠️ Preencha seu nome e selecione ao menos uma atividade!')

        # Histórico
        st.markdown("---")
        st.subheader('📋 Checklists Registrados de Hoje')

        if not df_hoje.empty:
            st.dataframe(df_hoje)
        else:
            st.info('Nenhum checklist preenchido hoje.')

    # Página de Dashboards
    elif pagina_selecionada == '📊 Dashboards':
        st.markdown("---")
        st.subheader('📊 Dashboards de Desempenho')

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 📈 Atividades Realizadas por Operador")
            if not df_hoje.empty:
                resumo = df_hoje.groupby('Operador').count().reset_index()

                grafico = alt.Chart(resumo).mark_bar().encode(
                    x=alt.X('Operador', sort='-y'),
                    y='Atividade',
                    color='Operador'
                ).properties(width=400, height=300)

                st.altair_chart(grafico)

        with col2:
            st.markdown("#### 📊 Atividades Mais Realizadas")
            if not df_hoje.empty:
                resumo_atividades = df_hoje['Atividade'].value_counts().reset_index()
                resumo_atividades.columns = ['Atividade', 'Quantidade']

                grafico_atividades = alt.Chart(resumo_atividades).mark_bar().encode(
                    x=alt.X('Atividade', sort='-y'),
                    y='Quantidade',
                    color='Atividade'
                ).properties(width=400, height=300)

                st.altair_chart(grafico_atividades)

        st.markdown("---")
        st.subheader('⏰ Horário de Maior Movimento')

        if not df_hoje.empty:
            df_hoje['Hora'] = pd.to_datetime(df_hoje['Hora'], format='%H:%M:%S')
            df_hoje['Hora_Somente'] = df_hoje['Hora'].dt.hour

            resumo_hora = df_hoje['Hora_Somente'].value_counts().reset_index()
            resumo_hora.columns = ['Hora', 'Quantidade']
            resumo_hora = resumo_hora.sort_values('Hora')

            grafico_horas = alt.Chart(resumo_hora).mark_bar().encode(
                x=alt.X('Hora:O', title='Hora do Dia'),
                y='Quantidade',
                color='Hora:O'
            ).properties(width=600, height=400)

            st.altair_chart(grafico_horas)

        st.markdown("---")
        st.subheader('🏆 Ranking de Eficiência dos Operadores')

        if not df_hoje.empty:
            ranking = df_hoje.groupby('Operador').count()['Atividade'].sort_values(ascending=False).reset_index()

            for idx, row in ranking.iterrows():
                posicao = idx + 1
                operador_nome = row['Operador']
                atividades_realizadas = row['Atividade']

                if posicao == 1:
                    medalha = "🥇"
                elif posicao == 2:
                    medalha = "🥈"
                elif posicao == 3:
                    medalha = "🥉"
                else:
                    medalha = "🎖️"

                st.write(f"{medalha} {posicao}º - {operador_nome}: {atividades_realizadas} atividades concluídas")
