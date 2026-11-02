# Validação da aplicação publicada

Data: 2 de novembro de 2026. Aplicação: [galileu-seguros-eda.streamlit.app](https://galileu-seguros-eda.streamlit.app/).

## Teste em janela anônima

O app foi aberto no Chrome em **Modo anônimo**, sem autenticação no Streamlit. O laboratório carregou o mapa de calor e os histogramas das quatro variáveis quantitativas. A aba **Indicadores da carteira** carregou quatro métricas e os três visuais: custos por tabagismo, custos altos por faixa etária e custo mediano por faixa de IMC e tabagismo.

| Interação | Resultado observado |
| --- | --- |
| Remover `Custo faturado (USD)` do seletor de variáveis | O histograma de custo desapareceu; os outros três histogramas e a matriz de correlação permaneceram. |
| Reduzir o limite superior do intervalo de custo para US$ 41.000 | A amostra exibida passou de 1.337 para 1.268 registros. |
| Excluir a região `Southwest` | A amostra passou de 1.268 para 955 registros. |
| Selecionar `Sim` em tabagismo | A amostra passou de 955 para 159 registros; os indicadores da segunda aba foram recalculados. |
| Trocar o método de `Spearman` para `Pearson` | O cabeçalho da matriz passou a `Correlação de Pearson`. |
| Alternar entre as duas abas | Ambos os painéis e seus gráficos carregaram. |

Uma segunda sessão, sem autenticação, abriu o URL público com os filtros padrão e confirmou os valores iniciais do painel 2: 1.337 registros, custo mediano de US$ 9.386, 25,1% de custos altos e 32,0% de concentração no topo 10%.

## Checagem de exposição

- O CSV versionado contém somente `idade`, `sexo`, `imc`, `filhos`, `fumante`, `regiao` e `custo`, provenientes da base pública citada no README. Não há nomes, contatos ou identificadores diretos.
- Os dados enviados aos gráficos são tabelas agregadas de frequência, correlação ou resumo por grupo. Grupos com menos de dez registros não aparecem nos gráficos comparativos do painel 2.
- O repositório não inclui arquivo de segredos. Foram revisados os arquivos versionados em busca de credenciais, chaves, tokens, emails privados e caminhos pessoais.
- A interface pública não exibiu dados privados ou erros internos durante os testes.

## Verificações locais

`python -m unittest discover -s tests -v`: quatro testes passaram, incluindo filtros, casos limite, atualização das métricas e uso de agregados nos gráficos.

O [README principal](../README.md) contém o link do app publicado. Os dois rascunhos permanecem neste diretório.
