# Justificativa das métricas do Dashboard 2

**Público-alvo:** analista de custos de uma carteira de seguros de saúde. A pergunta operacional é quais recortes da amostra merecem investigação adicional de concentração de custos. Os indicadores não são utilizados para avaliar pessoas ou estabelecer preços.

| Métrica | Variável e cálculo | Por que foi escolhida / o que comunica | Decisão que pode apoiar |
| --- | --- | --- | --- |
| Registros avaliados | Contagem das observações após os filtros | Dá contexto ao tamanho da amostra e evita comparar percentuais sem denominador. | Verificar se o recorte tem volume suficiente antes de investigar. |
| Custo mediano | Mediana de `custo` no recorte, em USD | Representa o valor central sem ser tão afetado pela cauda à direita observada na EDA. | Priorizar segmentos com custo típico elevado para análise adicional. |
| Custos altos | Percentual de registros com `custo` ≥ P75 da base tratada completa | Usa um limiar fixo, permitindo comparar recortes ao mesmo referencial mesmo quando o slider muda. | Identificar grupos com maior concentração de valores altos. |
| Concentração no topo 10% | Soma dos custos dos `ceil(0,10 × n)` maiores valores / soma total dos custos do recorte | Mostra quanto da soma observada está concentrada na cauda superior. | Avaliar onde a variabilidade de custos exige análise mais detalhada. |

Todos os indicadores são recalculados ao mudar intervalo de custo, região ou tabagismo. Se o recorte tiver menos de 10 registros, eles não são exibidos. Os três gráficos complementam os cartões: distribuição por tabagismo, participação de custos altos por faixa etária e mediana por faixa de IMC e tabagismo. Grupos com menos de 10 registros são omitidos. Diferenças observadas são associações descritivas; a base não informa cobertura, estado clínico ou outros fatores que permitam explicar causas.
