import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

# Configurações da Página
st.set_page_config(page_title="Checklist de Expedição", page_icon="✅", layout="centered")

# Título
st.title('📦 Checklist Diário de Expedição')

# 📅 Dados gerais
data = st.date_input('Data', datetime.now())

# 📋 Lista de funcionários
lista_funcionarios = [
    "Mateus",
    "João",
    "Maria",
    "Carlos",
    "Ana"
]

# Seletor de operador
operador = st.selectbox('Selecione seu nome', lista_funcionarios)

# ⚠️ Verificar se o operador já preencheu atividades hoje
if operador:
    try:
        df = pd.read_csv('checklist.csv')

        # Remove coluna "Tarefa" antiga se existir
        if 'Tarefa' in df.columns:
            df = df.drop(columns=['Tarefa'])

        # Filtrar registros do dia atual
        data_hoje = datetime.now().date().strftime("%Y-%m-%d")
        df_hoje = df[df['Data'] == data_hoje]

        # Filtrar registros do operador atual
        df_operador = df_hoje[df_hoje['Operador'] == operador]

        # Se o operador ainda não preencheu hoje
        if df_operador.empty:
            st.warning(f'⚠️ {operador}, você ainda não preencheu seu checklist hoje!')
        else:
            st.success(f'✅ {operador}, checklist já registrado hoje!')

    except FileNotFoundError:
        st.info('Nenhum checklist encontrado ainda. Preencha o primeiro!')

# 🛠️ Atividades fixas
st.markdown("## 🛠️ Atividades do Dia")

atividades = [
    "Separar mercadorias",
    "Emitir Nota Fiscal",
    "Guardar mercadorias no estoque",
    "Controle de estoque",
    "Recebimento"
]

# Checkboxes para as atividades
atividades_realizadas = []
for atividade in atividades:
    if st.checkbox(atividade):
        atividades_realizadas.append(atividade)

# Observações gerais
observacoes = st.text_area('Observações')

# Botão para salvar
if st.button('Salvar Checklist'):
    if operador and atividades_realizadas:
        # Captura a hora atual
        hora_atual = datetime.now().strftime("%H:%M:%S")

        # Criação do DataFrame
        df_atividades = pd.DataFrame({
            'Data': [data] * len(atividades_realizadas),
            'Hora': [hora_atual] * len(atividades_realizadas),
            'Operador': [operador] * len(atividades_realizadas),
            'Atividade': atividades_realizadas,
            'Status': ['Concluído'] * len(atividades_realizadas),
            'Observação': [observacoes] * len(atividades_realizadas)
        })

        try:
            df_existente = pd.read_csv('checklist.csv')
            df_total = pd.concat([df_existente, df_atividades], ignore_index=True)
        except FileNotFoundError:
            df_total = df_atividades

        df_total.to_csv('checklist.csv', index=False)
        st.success('Checklist salvo com sucesso! ✅')
    else:
        st.warning('Selecione seu nome e marque pelo menos uma atividade!')

# Mostrar o histórico do dia
st.markdown("---")
st.subheader('📋 Checklists Registrados de Hoje')

try:
    df = pd.read_csv('checklist.csv')

    if 'Tarefa' in df.columns:
        df = df.drop(columns=['Tarefa'])

    data_hoje = datetime.now().date().strftime("%Y-%m-%d")
    df_hoje = df[df['Data'] == data_hoje]

    st.dataframe(df_hoje)

except FileNotFoundError:
    st.info('Nenhum checklist preenchido ainda.')

# 📈 Gráfico de Atividades por Operador
st.markdown("---")
st.subheader('📈 Atividades Realizadas por Operador Hoje')

try:
    if not df_hoje.empty:
        resumo = df_hoje.groupby('Operador').count().reset_index()

        grafico = alt.Chart(resumo).mark_bar().encode(
            x=alt.X('Operador', sort='-y'),
            y='Atividade',
            color='Operador'
        ).properties(width=600, height=400)

        st.altair_chart(grafico)
    else:
        st.info('Nenhuma atividade registrada hoje para gerar gráfico.')

except:
    st.info('Nenhum checklist encontrado ainda.')

# 📈 Gráfico de Atividades Mais Realizadas Hoje
st.markdown("---")
st.subheader('📊 Atividades Mais Realizadas Hoje')

try:
    if not df_hoje.empty:
        resumo_atividades = df_hoje['Atividade'].value_counts().reset_index()
        resumo_atividades.columns = ['Atividade', 'Quantidade']

        grafico_atividades = alt.Chart(resumo_atividades).mark_bar().encode(
            x=alt.X('Atividade', sort='-y'),
            y='Quantidade',
            color='Atividade'
        ).properties(width=600, height=400)

        st.altair_chart(grafico_atividades)
    else:
        st.info('Nenhuma atividade registrada hoje para gerar gráfico.')

except:
    st.info('Nenhum checklist encontrado ainda.')

# 📈 Gráfico de Horário de Maior Movimentação
st.markdown("---")
st.subheader('⏰ Horário de Maior Movimentação')

try:
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
    else:
        st.info('Nenhuma atividade registrada hoje para gerar gráfico.')

except:
    st.info('Nenhum checklist encontrado ainda.')

# 🏆 Ranking de Eficiência dos Operadores
st.markdown("---")
st.subheader('🏆 Ranking de Eficiência dos Operadores')

try:
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

    else:
        st.info('Nenhuma atividade registrada hoje para gerar ranking.')

except:
    st.info('Nenhum checklist encontrado ainda.')

# 🔥 Painel de Pendências
st.markdown("---")
st.subheader('🛠️ Painel de Pendências - Quem ainda não preencheu hoje')

try:
    preenchidos = df_hoje['Operador'].unique().tolist()
    pendentes = [nome for nome in lista_funcionarios if nome not in preenchidos]

    if pendentes:
        st.warning('⚠️ Funcionários que ainda não preencheram hoje:')
        for nome in pendentes:
            st.write(f"🔹 {nome}")
    else:
        st.success('✅ Todos os funcionários preencheram hoje!')

except:
    st.info('Nenhum checklist encontrado ainda.')
