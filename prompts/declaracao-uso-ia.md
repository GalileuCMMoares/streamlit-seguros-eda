# Registro de uso de IA — rascunho para revisão

**Este registro ainda não está assinado e não deve ser tratado como declaração final.** A ferramenta usada foi Codex (OpenAI). A Skill oficial do Streamlit **não foi usada**.

## Registro resumido dos usos

1. A IA ajudou a consultar a EDA e os materiais da atividade, planejar a estrutura dos painéis e discutir público, métricas e gráficos.
2. Na etapa inicial, a IA propôs medidas, escreveu uma justificativa das métricas e elaborou interpretações dos dados. Essas escolhas e interpretações tiveram apoio da IA, apesar das diretrizes da atividade reservarem essa autoria ao estudante. Esse uso precisa ser declarado e discutido com a professora; não será apresentado como trabalho independente do estudante.
3. Após a discussão, o estudante confirmou o público de pessoas fumantes, as três medidas, o corte de US$ 20.000, o cálculo dos 10% dentro de cada grupo e os três tipos de visualização agora registrados no app.
4. A IA gerou e alterou código Python/Streamlit, cálculos agregados, testes, rascunhos de interface e documentação. Também apoiou depuração e conferência do app.
5. A EDA original está preservada em `notebooks/eda-original.ipynb`. O notebook `notebooks/preparacao-dados.ipynb` e os módulos de preparação, leitura, análise e interface receberam apoio de IA.

## Arquivos de código com apoio de IA

Os arquivos Python assistidos têm uma anotação `[IA]` no início do módulo. No notebook de preparação, cada célula de código assistida é identificada. A anotação indica assistência de IA e não substitui a revisão do estudante.

- `app.py`: estrutura Streamlit, filtros, cálculos apresentados, visualizações e textos de interface.
- `src/analytics.py`: cálculos e agregações para os painéis.
- `src/data_loader.py` e `src/prepare_data.py`: leitura e preparação da base usada no app.
- `tests/test_dashboard.py`: testes da interface e dos cálculos.
- `notebooks/preparacao-dados.ipynb`: células de código da preparação da base.

README, brief, rascunhos e este registro também foram redigidos ou revisados com ajuda da IA. O notebook de EDA original foi mantido sem alterações.

## Revisão individual ainda necessária

- Preencher os dados pessoais solicitados no modelo oficial.
- Escrever a reflexão pessoal pedida pela atividade, sem reutilizar uma justificativa redigida pela IA.
- Consultar a professora sobre como registrar o uso que ultrapassou as diretrizes e como isso afeta a entrega.
- Conferir cada trecho de código e não assinar até conseguir explicá-lo.
- Assinar e datar a versão final por conta própria.
