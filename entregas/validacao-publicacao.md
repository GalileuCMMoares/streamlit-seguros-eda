# Validação da aplicação publicada

Data da verificação: 2 de novembro de 2026. Aplicação: [Observatório de custos](https://galileu-seguros-eda.streamlit.app/). Código publicado: `92617d4` (`Atualiza dashboard de comparação por tabagismo`).

## Acesso e estado do deploy

O app foi aberto sem autenticação em uma janela anônima do Chrome. Na primeira tentativa, o Streamlit Cloud exibiu um `ImportError`: os logs apontavam que o processo estava usando uma cópia em cache de `src.analytics` sem a constante `HIGH_COST_LIMIT`, embora o arquivo estivesse no commit publicado. Reiniciei o app pelo painel do Streamlit Cloud; depois disso, a página carregou com o título “Observatório de custos | EDA · Streamlit” e os dois painéis ficaram disponíveis. Não foi necessário alterar o código para resolver essa falha de cache.

## Verificação dos painéis e controles

Na janela anônima do Chrome, confirmei que o painel 1 abriu com 1.337 registros, mapa de calor e histogramas. Remover “Custo faturado (USD)” no seletor reduziu o mapa para três variáveis e deixou três histogramas. Trocar a correlação de Spearman para Pearson atualizou o título e a matriz. O controle deslizante aceitou a alteração do limite superior de US$ 63.800 para US$ 63.700. A aba 2 carregou as três métricas e os três gráficos.

Com os filtros padrão, o painel 2 mostrou os grupos na ordem não fumantes / fumantes: 1.063 / 274 registros; 5,7% / 77,4% com custo de pelo menos US$ 20.000; e 26,0% / 16,1% de concentração nos 10% de custos mais altos de cada grupo. Os gráficos de mediana e custo médio por faixa etária apareceram, assim como os histogramas com 15 intervalos, contagens e limites compartilhados. Ao selecionar “Sim” em Tabagismo, a seleção passou a conter 274 de 1.337 registros e os indicadores e gráficos foram atualizados para esse grupo.

Também testei o seletor de regiões no app público sem autenticação: com “Southwest” removida, a contagem passou de 1.337 para 1.012. Esse teste foi feito na aba pública do navegador integrado; os demais controles acima foram verificados no Chrome anônimo. O README contém o link do app público. Os dois rascunhos de dashboard estão em `entregas/`.

## Dados e privacidade

O app usa o conjunto público Medical Cost Personal Dataset. O CSV contém idade, sexo, IMC, número de filhos, tabagismo, região e custo; não contém nomes, contatos ou identificadores diretos. A interface não oferece linhas individuais para consulta: os gráficos recebem contagens e resumos agregados. O painel 2 omite grupos ou combinações com menos de 10 registros. Não encontrei credenciais ou segredos no material versionado.

## Verificações locais

`/private/tmp/streamlit-seguros-venv/bin/python -m unittest discover -s tests -v`: quatro testes passaram, cobrindo cálculos, filtros, casos limite, agregações e limites compartilhados dos histogramas. `git diff --check` não apontou problemas de formatação no commit anterior.
