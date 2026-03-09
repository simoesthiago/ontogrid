| **ONS DADOS ABERTOS** |
|-----------------------|

Relatório de avaliação dos 80 conjuntos de dados públicos do ONS

Inventário analítico do catálogo, com foco em conteúdo, estrutura,
granularidade e observações de uso.

| **Escopo**          | 80 entradas do catálogo da organização ONS, incluindo 77 conjuntos históricos ativos, 2 descontinuados e 1 entrada colaborativa. |
|---------------------|----------------------------------------------------------------------------------------------------------------------------------|
| **Base consultada** | Portal ONS Dados Abertos (catálogo CKAN, páginas de conjunto e dicionários de dados selecionados).                               |
| **Produto**         | Relatório executivo-técnico com taxonomia temática, padrões de modelagem e inventário completo por conjunto.                     |

Março de 2026

# 1. Resumo executivo

- O catálogo da organização ONS informa 80 entradas. Para fechar esse
  universo de forma consistente, este relatório considerou 77 conjuntos
  históricos ativos listados na página inicial, 2 conjuntos
  explicitamente marcados como descontinuados e 1 entrada colaborativa
  do GitHub.

- A oferta de formatos é ampla: quase todo o catálogo tem PDF e formatos
  tabulares/machine-readable (JSON, CSV, PARQUET e XLSX), enquanto API
  aparece apenas em dois conjuntos e ZIP em um.

- Os conjuntos podem ser organizados em nove famílias analíticas:
  hidrologia, geração, carga/programação, intercâmbios, infraestrutura
  de rede, indicadores, custos, constrained-off e
  colaboração/documentação.

- A estrutura dos dados é heterogênea, mas bastante padronizada: séries
  temporais com chaves de data/hora e ativos, cadastros estáticos de
  referência, tabelas-ponte de relacionamento e painéis periódicos de
  indicadores.

- Do ponto de vista de integração analítica, o portal é forte em fatos
  históricos operativos e em indicadores consolidados; as principais
  lacunas relativas estão na ausência de um dicionário de campos
  igualmente explícito para todos os conjuntos e na coexistência de
  entradas não-tabulares no mesmo universo do catálogo.

# 2. Critério de avaliação e leitura do catálogo

O relatório foi construído a partir do catálogo público do ONS, usando a
página inicial do portal, a página da organização ONS, páginas
individuais de conjuntos selecionados e dicionários de dados disponíveis
em PDF. Onde havia dicionário, a descrição estrutural foi ancorada em
nomes de campos e convenções temporais; onde havia apenas descrição
catalográfica, a estrutura foi caracterizada no nível de granularidade,
chave principal e papel analítico do conjunto.

- Quando o título exibido variava entre páginas do portal, foi adotada a
  nomenclatura da página inicial e registrada a variação em observação
  (caso das bases de reservatórios).

- Os totais por grupo não somam 80; isso indica que a classificação por
  grupos no CKAN não é uma partição exclusiva dos conjuntos.

- Os totais por formato ultrapassam 80 porque um mesmo conjunto pode ter
  múltiplos recursos/publicações.

- “Ambiente Colaborativo - GITHUB” foi tratado como entrada
  documental/collaborativa e não como tabela operacional do SIN.

# 3. Panorama do portal ONS

Em termos de desenho de catálogo, o portal combina um núcleo grande de
séries históricas operativas com um conjunto menor de cadastros,
indicadores e artefatos de colaboração. A tabela seguinte resume os
números publicados na organização ONS e a forma como eles foram lidos
neste relatório.

| **Métrica do catálogo**                | **Leitura**                                                                                                                         |
|----------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------|
| **Total informado na organização ONS** | 80 conjuntos de dados encontrados.                                                                                                  |
| **Leitura adotada neste relatório**    | 77 conjuntos históricos ativos + 2 descontinuados + 1 entrada colaborativa.                                                         |
| **Leitura dos grupos**                 | Os grupos funcionam como categorização do CKAN e não como partição exclusiva; por isso a soma dos quantitativos de grupo supera 80. |
| **Leitura dos formatos**               | Os formatos são multi-recurso por conjunto; PDF, JSON, CSV, PARQUET e XLSX aparecem na maior parte do catálogo.                     |

| **Grupos publicados na organização ONS** | **Quantidade** |
|------------------------------------------|----------------|
| **Avaliação da Operação**                | 57             |
| **Programação da Operação**              | 16             |
| **Integração de Instalações**            | 8              |
| **Operação do Sistema**                  | 1              |
| **Planejamento da Operação**             | 1              |

| **Formatos publicados na organização ONS** | **Quantidade** |
|--------------------------------------------|----------------|
| **PDF**                                    | 79             |
| **JSON**                                   | 78             |
| **CSV**                                    | 76             |
| **PARQUET**                                | 75             |
| **XLSX**                                   | 74             |
| **API**                                    | 2              |
| **ZIP**                                    | 1              |

# 4. Padrões de estrutura observados no portal

Apesar da variedade temática, o catálogo do ONS é coerente do ponto de
vista de modelagem. Abaixo estão os padrões recorrentes que mais ajudam
a entender como os conjuntos foram organizados.

| **Padrão**                 | **Significado prático**                                                   | **Exemplo**                                                                         |
|----------------------------|---------------------------------------------------------------------------|-------------------------------------------------------------------------------------|
| **id\_\* / cod\_\***       | Chaves técnicas e identificadores de ativos, entidades e características. | Ex.: \`id_subsistema\`, \`id_reservatorio\`, \`cod_usina\`, \`cod_caracteristica\`. |
| **nom\_\***                | Campos descritivos legíveis para entidades e recortes.                    | Ex.: \`nom_subsistema\`, \`nom_bacia\`, \`nom_ree\`, \`nom_reservatorio\`.          |
| **dat\_\* / din_instante** | Marca temporal do registro, em data de referência ou instante.            | Ex.: \`dat_referencia\`, \`din_instante\`.                                          |
| **val\_\***                | Métricas numéricas do registro.                                           | Ex.: \`val_disp\`, \`val_indisppf\`, \`val_vazaoafluente\`, \`val_volumeutilcon\`.  |
| **tabela ponte**           | Relacionamentos entre entidades agregadas e entidades físicas.            | Ex.: conjuntos ↔ usinas; grupos de pequenas usinas ↔ usinas.                        |
| **cadastro estático**      | Master data de ativos e instalações.                                      | Ex.: reservatórios, linhas, subestações, equipamentos, modalidades.                 |

| **Tipo de modelagem**          | **Como reconhecer**                                                  | **Consequência analítica**                                               |
|--------------------------------|----------------------------------------------------------------------|--------------------------------------------------------------------------|
| **Série temporal operacional** | Há data/hora, ativo e uma ou mais medidas de valor.                  | É o desenho dominante para carga, geração, intercâmbios e hidrologia.    |
| **Cadastro de referência**     | Há uma linha por instalação/ativo e quase nenhuma dimensão temporal. | Serve como dimensão para enriquecer fatos históricos.                    |
| **Tabela-ponte**               | Relaciona entidades agregadas com entidades físicas.                 | É indispensável para reconciliar usina, conjunto e grupo.                |
| **Painel de KPI**              | Há período de referência e poucos campos de medição sintética.       | É típico dos indicadores de confiabilidade, disponibilidade e qualidade. |
| **Entrada documental**         | Os recursos são PDF e link externo, sem tabela de fatos.             | Deve ser separada do repositório analítico principal.                    |

# 5. Inventário completo dos 80 conjuntos de dados

A partir daqui, o relatório apresenta o inventário completo organizado
por família temática. Em cada conjunto, o objetivo é responder a três
perguntas: o que existe, qual a forma predominante de estruturação e que
observações ajudam a usar o dado corretamente.

| **Família**                                                    | **Quantidade de conjuntos** |
|----------------------------------------------------------------|-----------------------------|
| **Hidrologia e reservatórios**                                 | 16                          |
| **Geração e usinas**                                           | 17                          |
| **Carga, balanço e programação**                               | 13                          |
| **Intercâmbios, importação e comércio**                        | 6                           |
| **Infraestrutura e cadastro da rede**                          | 4                           |
| **Indicadores de confiabilidade, disponibilidade e qualidade** | 16                          |
| **Custos, preços operativos e parâmetros econômicos**          | 3                           |
| **Restrições operativas e constrained-off**                    | 4                           |
| **Colaborativo e documentação**                                | 1                           |
| **Total**                                                      | 80                          |

## 5.1 Hidrologia e reservatórios

Família que cobre a condição hídrica do sistema, o cadastro físico dos
reservatórios, agregações energéticas (EAR e ENA) e um componente
geoespacial de apoio. É onde o portal concentra os dados mais
diretamente conectados ao balanço água–energia.

| **Conjuntos**              | 16                                                                                                                                                                                                                                                                                                                                                  |
|----------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Modelagem predominante** | Predominam séries temporais diárias e horárias com chave de tempo combinada a reservatório, usina, bacia, REE ou subsistema. Nos dicionários consultados, a modelagem repete o padrão de identificadores (\`id\_\*\`, \`cod_usina\`), descrições (\`nom\_\*\`), marca temporal (\`dat\_\*\` ou \`din_instante\`) e medidas numéricas (\`val\_\*\`). |

| **Conjunto de dados**                                        | **O que existe**                                                                                                                                                | **Estrutura predominante e observações**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
|--------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Contornos das Bacias Hidrográficas**                       | Camada geoespacial com os contornos das bacias hidrográficas utilizadas pelo ONS para contextualizar séries de ENA, EAR, reservatórios e análises hidrológicas. | Cadastro geográfico: uma feição por bacia/polígono, com identificadores, nomes e geometria. É o conjunto mais próximo de um arquivo SIG do catálogo, pensado para junções espaciais, mapas e sobreposição com outros ativos. Observação: Funciona como dimensão espacial de referência, e não como série histórica.                                                                                                                                                                                                                                                                                                                                                |
| **Dados Hidrológicos de Reservatórios - Base Diária**        | Dados diários verificados e consolidados pelo ONS sobre a condição hidráulica dos reservatórios, incluindo nível, volume útil e diversos componentes de vazão.  | Série temporal diária por reservatório/usina/subsistema. O dicionário confirma identificadores como \`id_subsistema\`, \`nom_subsistema\`, \`tip_reservatorio\`, \`nom_bacia\`, \`nom_ree\`, \`id_reservatorio\`, \`nom_reservatorio\`, \`cod_usina\` e \`din_instante\`, além de medidas como \`val_nivelmontante\`, \`val_niveljusante\`, \`val_volumeutilcon\`, \`val_vazaoafluente\`, \`val_vazaoturbinada\`, \`val_vazaovertida\` e outros componentes hidráulicos. Observação: O portal informa atualizações às 9:15, 14:15 e 17:00. Em páginas individuais também aparece como “Dados Hidráulicos por Reservatório – Base diária”.                          |
| **Dados Hidrológicos de Reservatórios - Base Horária**       | Série horária com variáveis operativas dos reservatórios informadas pelos agentes de geração, oferecendo granularidade superior à base diária.                  | Série temporal horária por reservatório/usina. O dicionário confirma campos como \`id_subsistema\`, \`nom_subsistema\`, \`tip_reservatorio\`, \`nom_bacia\`, \`id_reservatorio\`, \`nom_reservatorio\`, \`cod_usina\`, \`din_instante\` e medidas como \`val_volumeutil\`, \`val_vazaoafluente\`, \`val_vazaodefluente\`, \`val_vazaoturbinada\`, \`val_vazaovertida\`, \`val_vazaooutrasestruturas\` e \`val_vazaotransferida\`. Observação: Os dados não são consistidos pelo ONS; o portal informa atualização recorrente a cada 15 minutos e convenção de hora-fim para a hora 00:00. Também aparece como “Dados Hidráulicos por Reservatório – Base horária”. |
| **Dados Hidrológicos - Volume de Espera Recomendado**        | Valores recomendados de volume de espera para reservatórios, usados em contexto de controle de cheias e operação sazonal.                                       | Tabela temporal por reservatório e data de referência, com o volume recomendado e atributos de identificação hidroelétrica/regional. É melhor tratá-la como uma tabela de parâmetros operativos no tempo, não como medição física realizada. Observação: É um conjunto de regra operativa recomendada, distinto das séries verificadas do reservatório.                                                                                                                                                                                                                                                                                                            |
| **EAR Diário por Bacia**                                     | Energia armazenada equivalente agregada por bacia hidrográfica, permitindo observar a condição de armazenamento sob um recorte regional hídrico.                | Série diária agregada por data + bacia. A estrutura típica tem uma linha por combinação de data e bacia, com medidas de EAR em valor absoluto e/ou percentual da capacidade máxima. Observação: É uma visão agregada derivada; útil para monitoramento regional e comparação histórica.                                                                                                                                                                                                                                                                                                                                                                            |
| **EAR Diário por REE - Reservatório Equivalente de Energia** | Energia armazenada equivalente agregada por REE, recorte clássico dos estudos de planejamento e operação.                                                       | Série diária por data + REE, normalmente com identificador e nome do REE, além das medidas de energia armazenada. É uma tabela sintética, menos granular que a base por reservatório e mais aderente aos modelos do setor. Observação: Serve de ponte entre ativos físicos e agregações de planejamento.                                                                                                                                                                                                                                                                                                                                                           |
| **EAR Diário por Reservatório**                              | Energia armazenada equivalente no nível do reservatório individual.                                                                                             | Série diária por data + reservatório, com chaves do reservatório/usina e medidas de EAR. É o corte mais granular da família EAR e pode ser integrado ao cadastro de reservatórios. Observação: Adequado para análises detalhadas de ativos hídricos específicos.                                                                                                                                                                                                                                                                                                                                                                                                   |
| **EAR Diário por Subsistema**                                | Energia armazenada equivalente agregada por subsistema do SIN.                                                                                                  | Série diária compacta por data + subsistema, com poucas dimensões e foco em indicadores agregados. É uma estrutura enxuta, orientada a dashboards executivos e séries históricas macro. Observação: É a visão mais gerencial da família EAR.                                                                                                                                                                                                                                                                                                                                                                                                                       |
| **ENA Diário por Bacia**                                     | Energia natural afluente agregada por bacia hidrográfica.                                                                                                       | Série diária por data + bacia, com valores de ENA e atributos de identificação da bacia. A lógica estrutural é análoga à EAR por bacia, mas com foco no aporte energético natural. Observação: Útil para correlação entre hidrologia e condição energética do sistema.                                                                                                                                                                                                                                                                                                                                                                                             |
| **ENA Diário por REE - Reservatório Equivalente de Energia** | Energia natural afluente agregada por REE.                                                                                                                      | Série diária por data + REE, com medidas de ENA e atributos do reservatório equivalente. Normalmente funciona como tabela de apoio a estudos de planejamento e sazonalidade hidrológica. Observação: Importante para modelagem e calibração de cenários energéticos.                                                                                                                                                                                                                                                                                                                                                                                               |
| **ENA Diário por Reservatório**                              | Energia natural afluente no nível do reservatório individual.                                                                                                   | Série diária por data + reservatório/usina, com chaves físicas do ativo e medida de ENA. É o corte mais granular da família ENA. Observação: Permite leitura fina das contribuições energéticas de cada reservatório.                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| **ENA Diário por Subsistema**                                | Energia natural afluente agregada por subsistema.                                                                                                               | Série diária por data + subsistema, com agregação macro semelhante à EAR por subsistema. A estrutura é simples e muito útil para integração com séries de carga, geração e CMO. Observação: Boa entrada para séries históricas e painéis executivos.                                                                                                                                                                                                                                                                                                                                                                                                               |
| **Energia Vertida Turbinável**                               | Energia associada ao vertimento turbinável, isto é, potencial energético não convertido apesar de turbinável.                                                   | Série temporal horária por reservatório/usina, com uma medida especializada de energia vertida e chaves de tempo e ativo hidráulico. O portal informa convenção de hora-fim para 00:00. Observação: É um conjunto especializado para estudos de eficiência hidráulica e perdas operacionais.                                                                                                                                                                                                                                                                                                                                                                       |
| **Grandezas Fluviométricas**                                 | Grandezas fluviométricas relacionadas ao sistema hídrico, complementando a visão dos reservatórios com variáveis fluviais.                                      | Série temporal associada a ponto/trecho/ativo hidrográfico, geralmente diária, com medições hidrológicas como cota, vazão ou grandeza correlata. Deve ser entendida como fato temporal e não como cadastro. Observação: É um conjunto complementar para leitura do comportamento do rio e da bacia.                                                                                                                                                                                                                                                                                                                                                                |
| **Reservatórios**                                            | Cadastro mestre dos reservatórios do universo operacional do ONS.                                                                                               | Tabela de referência estática, uma linha por reservatório, com atributos como identificadores, nome, vínculo com usina, bacia, REE, subsistema e classificação do reservatório. Observação: O portal indica ausência de histórico e atualização como cadastro de referência.                                                                                                                                                                                                                                                                                                                                                                                       |
| **Precipitação Diária Observada**                            | Série de precipitação observada em base diária para o contexto hidrológico do portal.                                                                           | Série diária por estação, região ou bacia, com data e valor de precipitação. Do ponto de vista analítico, opera como série temporal meteorológica de apoio à hidrologia. Observação: Conjunto explicitamente marcado como descontinuado ou sem atualização.                                                                                                                                                                                                                                                                                                                                                                                                        |

## 5.2 Geração e usinas

Agrupa cadastros de ativos de geração, séries de produção efetiva,
disponibilidade e indicadores de desempenho. Também inclui tabelas de
relacionamento necessárias para converter visões por usina, conjunto e
grupo de pequenas usinas.

| **Conjuntos**              | 17                                                                                                                                                                                                                                                                                                                  |
|----------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Modelagem predominante** | Há uma combinação clara de cadastros estáticos (capacidade instalada, modalidade, relacionamentos), fatos horários de geração e painéis periódicos de indicadores mensais/anuais. As chaves recorrentes são usina, unidade geradora, conjunto ou grupo, sempre combinadas a uma data/hora ou período de referência. |

| **Conjunto de dados**                                                                 | **O que existe**                                                                                                          | **Estrutura predominante e observações**                                                                                                                                                                                                                                                                                                                     |
|---------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Capacidade Instalada de Geração**                                                   | Cadastro da potência instalada dos ativos de geração do universo operacional.                                             | Tabela de referência, uma linha por usina ou entidade de geração equivalente, com identificadores, fonte/tecnologia, agente, subsistema e valor de capacidade instalada em MW. Observação: O portal sinaliza que não há histórico; funciona como dimensão cadastral.                                                                                         |
| **Disponibilidade de Usinas**                                                         | Histórico da disponibilidade das usinas, orientado a entender o quanto cada ativo esteve disponível para operação.        | Painel temporal por usina/unidade e período de referência, com métricas de disponibilidade e indisponibilidade em horas, percentual ou classificação de evento. É um conjunto de performance operacional, não de geração realizada. Observação: A estrutura exata varia por arquivo, mas a lógica é de série periódica por ativo.                            |
| **Fator de Capacidade de Geração Eólica e Solar**                                     | Fator de capacidade de usinas e conjuntos de usinas eólicas e solares despachadas pelo ONS em base horária.               | Série horária por usina/conjunto/grupo e instante, com geração observada, referência de capacidade e fator calculado. Costuma ser um fato temporal compacto, pronto para análises de intermitência e performance. Observação: Relevante para modelagem de renováveis variáveis.                                                                              |
| **Geração de Itaipu Binacional - Base horária**                                       | Série horária dedicada à geração da usina de Itaipu.                                                                      | Fato horário por instante de referência, com medidas de geração e atributos específicos do ativo binacional. O desenho tende a ser mais simples por tratar de um único empreendimento de grande porte. Observação: É uma visão especializada de um ativo singular do sistema brasileiro.                                                                     |
| **Geração por Usina em Base Horária**                                                 | Geração verificada de usinas, conjuntos de usinas e grupos de pequenas usinas em base horária.                            | Grande tabela fato horária por entidade geradora + instante. O portal informa partição anual para 2000–2021 e partição por mês/ano a partir de 2022, o que sugere volume elevado e orientação analítica para processamento incremental. Observação: É a principal tabela de geração realizada do portal.                                                     |
| **Geração Térmica por Motivo de Despacho**                                            | Dados programados e verificados de geração de usinas térmicas despachadas pelo ONS, discriminados por motivo de despacho. | Série horária por usina térmica + instante + motivo/classificação de despacho, com valores programados e verificados. Trata-se de uma tabela fato temática, com dimensão categórica relevante para estudos regulatórios e econômicos. Observação: O portal descreve cobertura histórica a partir de 2013, com mudanças de particionamento ao longo do tempo. |
| **Indicadores de Desempenho das Funções Geração por Unidade Geradora em Base Anual**  | Indicadores anuais de desempenho das funções geração no nível de unidade geradora.                                        | Painel anual por unidade geradora + ano, com métricas de desempenho, cumprimento e/ou disponibilidade. Estrutura típica de KPI consolidado, sem granularidade horária. Observação: Adequado para benchmarking de unidades ao longo do tempo.                                                                                                                 |
| **Indicadores de Desempenho das Funções Geração por Unidade Geradora em Base Mensal** | Indicadores mensais de desempenho das funções geração no nível de unidade geradora.                                       | Painel mensal por unidade + mês de referência, com a mesma lógica analítica da base anual, porém com maior resolução temporal. Observação: Permite leituras de sazonalidade e degradação operacional.                                                                                                                                                        |
| **Indicadores de Disponibilidade de Função Geração para o SIN – Base Mensal**         | Indicadores mensais de disponibilidade da função geração para o SIN.                                                      | Tabela periódica agregada por ativo, classe, região ou subsistema e mês de referência, com métricas de disponibilidade e indisponibilidade. É um conjunto mais sintético que a disponibilidade bruta por usina. Observação: Bom para visão sistêmica da confiabilidade da geração.                                                                           |
| **Modalidade de Operação de Usina**                                                   | Classificação das usinas segundo a modalidade de operação utilizada pelo ONS.                                             | Tabela de referência por usina, com modalidade, fonte, agente e demais atributos classificatórios. É uma dimensão essencial para segmentar outros fatos do portal. Observação: Especialmente importante para leitura de conjuntos de constrained-off e geração agregada.                                                                                     |
| **Relacionamento Entre Conjuntos e Usinas**                                           | Mapa entre os conjuntos sintéticos do portal e as usinas físicas que os compõem.                                          | Tabela ponte entre \`conjunto\` e \`usina\`, possivelmente com vigência ou atributos de composição. Sua função é habilitar reconciliação entre fatos publicados em nível agregado e o universo físico. Observação: É uma dimensão relacional, não uma série temporal principal.                                                                              |
| **Relacionamento Entre Grupos de Pequenas Usinas e Usinas**                           | Mapa entre grupos de pequenas usinas e as usinas individuais correspondentes.                                             | Tabela ponte entre grupo e usina, com chaves de ambos os lados e eventuais atributos cadastrais de apoio. Ajuda a desmontar agregações publicadas em algumas séries de geração. Observação: Essencial para análises em que o nível físico individual é necessário.                                                                                           |
| **Taxas TEIFa e TEIP**                                                                | Taxas clássicas de indisponibilidade forçada e programada aplicadas à análise de geração.                                 | Tabela periódica ou de referência por unidade/usina e período, com os valores TEIFa e TEIP. Pode ser tratada como conjunto paramétrico de confiabilidade. Observação: Serve como base para estudos de indisponibilidade e planejamento.                                                                                                                      |
| **Taxas TEIFa Oper e TEIP Oper**                                                      | Versão operacional das taxas TEIFa e TEIP, refletindo comportamento efetivamente observado.                               | Tabela por unidade/usina e período de referência, com os valores operacionais das taxas. A comparação com a base paramétrica é analiticamente útil. Observação: Mais aderente ao desempenho observado do que à parametrização teórica.                                                                                                                       |
| **Taxas TEIFa e TEIP - Parâmetros**                                                   | Conjunto paramétrico com os valores ou premissas de TEIFa e TEIP utilizados em processos do ONS.                          | Cadastro/parametrização por usina, unidade ou tecnologia, com datas de vigência e valores de parâmetro. É melhor interpretado como repositório de insumos de modelo. Observação: Diferencia-se das taxas operacionais por ter natureza de parâmetro.                                                                                                         |
| **Unidade Geradora em Operação como Compensador Síncrono**                            | Registros de unidades geradoras que operam como compensador síncrono, em vez de produzir energia ativa.                   | Tabela de status/evento por unidade e data/hora ou período de referência, com indicação da condição operacional e vínculo com a usina. Observação: É um conjunto especializado de estado operacional.                                                                                                                                                        |
| **Usinas prestando serviço ancilar de reativo conforme SANDBOX**                      | Usinas em operação prestando serviço ancilar de compensação de reativo segundo critérios SANDBOX.                         | Tabela de referência ou status por usina e data de referência, com sinalização de prestação do serviço e possíveis atributos elétricos. Não é uma série de alta frequência. Observação: O próprio portal informa atualização sob demanda, sem periodicidade fixa.                                                                                            |

## 5.3 Carga, balanço e programação

Família centrada na demanda do sistema e nos produtos da programação
diária. Reúne séries de carga verificada e programada, resultados do
DESSEM e conjuntos auxiliares para comparação entre previsão,
programação e execução.

| **Conjuntos**              | 13                                                                                                                                                                                                                                                                                                                |
|----------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Modelagem predominante** | A modelagem mistura fatos temporais diários, horários e mensais. Parte importante dos conjuntos nasce do ciclo de programação diária, de modo que a chave temporal e o recorte por subsistema/entidade operacional são dominantes. Dois conjuntos (Carga Programada e Carga Verificada) também aparecem como API. |

| **Conjunto de dados**                                                   | **O que existe**                                                                                                                                            | **Estrutura predominante e observações**                                                                                                                                                                                                                                                            |
|-------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Balanço de Energia do DESSEM - Geral**                                | Informação simplificada da programação eletroenergética diária resultante do modelo DESSEM, incluindo demanda e geração previstas para o dia de referência. | Tabela fato diária, normalmente por data de referência e recorte macro (subsistema/SIN e grandes componentes). É um desenho mais enxuto que a versão detalhada, adequado para leitura executiva. Observação: É a porta de entrada para o universo da programação diária.                            |
| **Balanço de Energia do DESSEM - Detalhado**                            | Versão detalhada do balanço eletroenergético do DESSEM, com decomposição mais rica da demanda, geração, intercâmbios e demais parcelas do balanço.          | Tabela diária de maior granularidade, com mais dimensões e categorias analíticas. Pode incluir recortes por fonte, componente, patamar ou subsistema, dependendo do arquivo. Observação: É a base programada mais rica para estudos de operação no curtíssimo prazo.                                |
| **Balanço de Energia nos Subsistemas**                                  | Balanço histórico de energia por subsistema, descrevendo a composição de oferta, demanda e intercâmbio.                                                     | Série temporal por data + subsistema, com múltiplas medidas de geração, carga, intercâmbio e saldo. É uma tabela sintética de balanço energético histórico. Observação: Boa ponte entre dados observados e produtos da programação.                                                                 |
| **Carga de Energia Diária**                                             | Carga/energia observada em base diária no SIN e/ou nos subsistemas.                                                                                         | Série diária por data + subsistema/SIN, com medida de carga/energia e, em geral, poucos atributos adicionais. É uma série macro de demanda. Observação: Muito útil para tendência, sazonalidade e comparação com séries programadas.                                                                |
| **Carga de Energia Mensal**                                             | Carga/energia consolidada em base mensal.                                                                                                                   | Série mensal por mês de referência + subsistema/SIN, com estrutura simples e orientada a histórico de longo prazo. Observação: Adequado para análises de tendência e comparações anuais.                                                                                                            |
| **Carga de Energia Programada**                                         | Carga/energia programada utilizada na operação e na programação do sistema.                                                                                 | Série temporal programada por data/período + subsistema, publicada em formatos tabulares e também por API. A estrutura tende a replicar a lógica de tempo + recorte geográfico + valor programado. Observação: É um dos dois conjuntos em que o portal explicita disponibilidade de API.            |
| **Carga de Energia Verificada**                                         | Carga/energia verificada efetivamente observada na operação.                                                                                                | Série temporal por data/período + subsistema/SIN, com valor realizado e, em geral, poucos atributos dimensionais adicionais. Também aparece como API no portal. Observação: É a principal série medida de demanda e o par natural da Carga Programada.                                              |
| **Carga Global de Roraima**                                             | Série específica da carga global de Roraima, relevante pelo tratamento operacional particular desse sistema.                                                | Série temporal por data/hora e recorte regional de Roraima, com medidas de carga/energia. Funciona como tabela temática dedicada a um recorte geográfico singular. Observação: É um conjunto importante para análises regionais específicas.                                                        |
| **Curva de Carga Horária**                                              | Curva horária de carga do SIN e/ou de seus subsistemas.                                                                                                     | Série horária por instante + subsistema/SIN, normalmente uma linha por hora e recorte geográfico, com medida de carga. É o principal fato intradiário de demanda. Observação: Base central para shape de carga e estudos intradiários.                                                              |
| **Dados dos Programados dos Elementos de Fluxo Controlado**             | Valores programados para elementos de fluxo controlado acompanhados pelo ONS.                                                                               | Tabela programada por elemento + data/hora ou patamar, com valor de fluxo e identificadores do elemento. Deve ser lida como fato de programação, não de medição histórica. Observação: Útil para estudos de rede e aderência da programação.                                                        |
| **Dados dos Valores da Previsão Versus Programado - Eólicas e Solares** | Comparação entre valores previstos e programados para geração eólica e solar.                                                                               | Série temporal por ativo, conjunto ou recorte regional e período, com pelo menos duas medidas centrais: previsão e programado; em alguns casos, a diferença/desvio é facilmente derivável. Observação: É uma base muito útil para avaliar acurácia de previsão e decisões de programação.           |
| **Dados dos Valores da Programação Diária**                             | Valores da programação diária do sistema, cobrindo variáveis e entidades relevantes do ciclo operacional.                                                   | Tabela de programação por data de referência + entidade + variável/valor programado. É um fato de day-ahead/intraday, menos sintético que o balanço geral e mais genérico que as bases específicas. Observação: Complementa os produtos derivados do DESSEM.                                        |
| **Histórico de Despacho de Energia de Janeiro/2021 A Setembro/2024**    | Arquivo histórico do despacho de energia para o período explicitado no título.                                                                              | Série histórica por data/hora e entidade de despacho, normalmente com valores de despacho e atributos operacionais. Estruturalmente é um grande fato temporal orientado a eventos/intervalos de despacho. Observação: O portal o marca como descontinuado ou sem atualização após setembro de 2024. |

## 5.4 Intercâmbios, importação e comércio

Reúne o fluxo físico e comercial entre subsistemas e nas fronteiras
internacionais. É a família que conecta a topologia do SIN às trocas
externas e às modalidades comerciais de importação/exportação.

| **Conjuntos**              | 6                                                                                                                                                                                                                          |
|----------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Modelagem predominante** | Predominam séries temporais horárias, com chaves de tempo combinadas a origem/destino, país, interface, conversora ou bloco comercial. Algumas bases representam fluxo realizado; outras, oferta ou programação comercial. |

| **Conjunto de dados**                                       | **O que existe**                                                       | **Estrutura predominante e observações**                                                                                                                                                                                                                                                       |
|-------------------------------------------------------------|------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Geração Comercial Para Exportação Internacional**         | Geração destinada à exportação internacional na modalidade comercial.  | Série temporal por data/hora + ativo, subsistema ou interface de exportação, com medidas de energia/geração associadas à exportação comercial. Observação: É um recorte comercial da geração, distinto da geração total realizada.                                                             |
| **Importação de Energia na Modalidade Comercial por Bloco** | Importação de energia em modalidade comercial discriminada por bloco.  | Série temporal por período + bloco + país/interface, com quantidade importada e atributos contratuais/comerciais. A presença do bloco indica granularidade categórica adicional. Observação: É apropriado para análises contratuais e de composição da importação.                             |
| **Intercâmbios Entre Subsistemas**                          | Fluxos de intercâmbio entre os subsistemas do SIN.                     | Série horária por instante + subsistema de origem + subsistema de destino, com medida de fluxo/energia. É uma tabela fato clássica de rede. Observação: É uma das bases mais úteis para fechar o balanço físico entre regiões.                                                                 |
| **Intercâmbio do SIN com Outros Países**                    | Intercâmbio entre o SIN e países vizinhos.                             | Série horária por instante + país/interface/conversora, com valores de importação e exportação ou direção do fluxo. Trata-se de uma visão de fronteira internacional. Observação: Complementa, mas não substitui, a base por modalidade.                                                       |
| **Intercâmbio de Energia por Modalidade**                   | Intercâmbio de energia segregado por modalidade operacional/comercial. | Série horária por instante + conversora/interface + modalidade, com valores energéticos em MWh. A dimensão “modalidade” é o principal diferencial desse conjunto. Observação: É mais classificatória do que a base apenas por país ou subsistema.                                              |
| **Ofertas de Preço para Importação**                        | Ofertas de preço associadas ao processo de importação de energia.      | Tabela de ofertas por data/hora + agente/bloco/pais/interface, contendo preço, quantidade ofertada e demais atributos do lance. Estruturalmente é um fato de mercado/oferta, não de fluxo realizado. Observação: Complementa os dados de importação efetiva com a camada econômica da decisão. |

## 5.5 Infraestrutura e cadastro da rede

Família de cadastros da rede de operação. São conjuntos estruturais:
mapeiam linhas, subestações, capacidade de transformação e equipamentos
de controle de reativos, servindo como dimensões para outras séries e
indicadores.

| **Conjuntos**              | 4                                                                                                                                                                                       |
|----------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Modelagem predominante** | Predomina a lógica de cadastro estático ou lentamente mutável. Em geral, cada linha representa um ativo ou função de rede e não há histórico longo embutido; a atualização é cadastral. |

| **Conjunto de dados**                                        | **O que existe**                                                         | **Estrutura predominante e observações**                                                                                                                                                                                                                                                     |
|--------------------------------------------------------------|--------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Capacidade de Transformação da Rede Básica**               | Capacidade de transformação instalada/disponível na rede básica.         | Tabela cadastral por banco, transformador, subestação ou nível de tensão, com identificadores do ativo e valor de capacidade. Em termos analíticos, é uma dimensão técnica da rede. Observação: Útil como base de referência para estudos de transmissão e expansão.                         |
| **Equipamentos de Controle de Reativos da Rede de Operação** | Inventário dos equipamentos de controle de reativos da rede de operação. | Cadastro estático por equipamento, subestação e subsistema, com atributos elétricos e de identificação. Não é uma base de eventos ou medições. Observação: Serve de dimensão para análises de disponibilidade e prestação de serviço reativo.                                                |
| **Linhas de Transmissão da Rede de Operação**                | Inventário das linhas de transmissão da rede de operação.                | Cadastro estático, uma linha por LT/trecho, com atributos explicitamente citados pelo portal como subsistema, UF, agente proprietário, nível de tensão e comprimento. O desenho é de master data da rede. Observação: O portal informa ausência de histórico e atualização diária cadastral. |
| **Subestação da Rede de Operação**                           | Inventário das subestações da rede de operação.                          | Cadastro estático por subestação, com identificadores, localização, agente, subsistema e atributos classificatórios. Estruturalmente é a dimensão base das instalações de rede. Observação: Também é descrito sem histórico e com atualização cadastral.                                     |

## 5.6 Indicadores de confiabilidade, disponibilidade e qualidade

Família de KPIs da rede básica e de funções de transmissão/geração. Em
vez de descrever o estado bruto dos ativos, estes conjuntos sintetizam
conformidade, severidade, robustez, indisponibilidades e impactos de
eventos.

| **Conjuntos**              | 16                                                                                                                                                                                                                                             |
|----------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Modelagem predominante** | A maioria dos conjuntos tem estrutura de painel periódico (mensal ou anual) ou de evento agregado. Os registros costumam ser compactos: período de referência + característica/recorte + valores KPI. É a camada mais “indicadores” do portal. |

| **Conjunto de dados**                                                                                                 | **O que existe**                                                                                               | **Estrutura predominante e observações**                                                                                                                                                                                                                                                                                                          |
|-----------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Indicadores de Confiabilidade da Rede Básica: ATLS – Atendimento aos Limites Sistêmicos**                           | Indicador de confiabilidade associado ao atendimento aos limites sistêmicos da rede básica.                    | Painel periódico por período de referência e característica/localização, com métricas de conformidade, taxa ou contagem. É uma tabela sintética de KPI e não um log de operação. Observação: A leitura detalhada do indicador depende do glossário específico do ONS.                                                                             |
| **Indicadores de Confiabilidade da Rede Básica: CCAL - Controle de Carregamento de Linhas de Transmissão**            | Indicador voltado ao controle de carregamento das linhas de transmissão.                                       | Painel periódico por período e recorte da rede, com métricas de desempenho/confiabilidade relacionadas a carregamento de LT. Observação: Expressa a ótica de confiabilidade do carregamento de linhas.                                                                                                                                            |
| **Indicadores de Confiabilidade da Rede Básica: CCAT – Controle de Carregamento de Transformadores**                  | Indicador de confiabilidade para o controle de carregamento de transformadores.                                | Painel periódico semelhante ao CCAL, mas associado a transformadores, com período de referência e medidas de desempenho. Observação: É a contrapartida de transformadores no tema de carregamento.                                                                                                                                                |
| **Indicadores de Confiabilidade da Rede Básica: CIPER – Carga Interrompida por Perturbações**                         | Indicador da carga interrompida em perturbações.                                                               | Tabela de indicador por período e evento/categoria, com medida de carga interrompida e recortes de análise. Pode ser entendida como impacto consolidado das perturbações. Observação: Relaciona confiabilidade à consequência percebida pelo sistema.                                                                                             |
| **Indicadores de Confiabilidade da Rede Básica: DREQ, FREQ**                                                          | Conjunto de indicadores de confiabilidade identificado pelas siglas DREQ e FREQ.                               | Painel periódico por referência temporal e categoria de indicador, com contagens, frequências ou taxas. Trata-se de base de KPI, não de evento operacional bruto. Observação: As siglas exigem consulta à documentação de negócio do ONS para interpretação fina.                                                                                 |
| **Indicadores de Confiabilidade da Rede Básica: ENS – Energia Não Suprida**                                           | Indicador de energia não suprida da rede básica.                                                               | Tabela periódica ou agregada por evento, local ou classe, com valores de ENS. Estruturalmente é um indicador de adequação/continuidade do suprimento. Observação: É um dos KPIs mais relevantes para impacto sistêmico.                                                                                                                           |
| **Indicadores de Confiabilidade da Rede Básica: Robustez – RMAL, RMCS, RRB E RRBCS**                                  | Família de indicadores de robustez da rede básica identificados pelas siglas RMAL, RMCS, RRB e RRBCS.          | Painel periódico por período de referência e tipo de robustez, com uma medida por sigla ou colunas correspondentes. A estrutura é de KPI sintético multicritério. Observação: É apropriado para análise institucional da robustez da rede.                                                                                                        |
| **Indicadores de Confiabilidade da Rede Básica: SM - Severidade das Perturbações**                                    | Indicador de severidade das perturbações.                                                                      | Tabela de eventos agregados ou painel por período, com escore/índice de severidade e eventuais classificações. Observação: Permite ranking e acompanhamento de criticidade das ocorrências.                                                                                                                                                       |
| **Indicadores de Cumprimento de Providências: ECPA E PCPA**                                                           | Indicadores de cumprimento de providências e ações demandadas.                                                 | Painel gerencial por período, agente, tipo de providência ou categoria, com métricas de cumprimento. É claramente uma base de acompanhamento de gestão. Observação: Tem natureza mais gerencial do que eletroenergética direta.                                                                                                                   |
| **Indicadores de Disponibilidade de Função Transmissão – Equipamentos de Controle de Reativo**                        | Indicadores mensais de disponibilidade da função transmissão associados a equipamentos de controle de reativo. | Painel mensal por função/característica e período de referência, com métricas de disponibilidade e indisponibilidade. É uma estrutura compacta de KPI agregado, análoga às demais bases de disponibilidade de transmissão. Observação: Bom para leitura macro da disponibilidade sem entrar no log de cada equipamento.                           |
| **Indicadores de Disponibilidade de Função Transmissão – Conversores**                                                | Indicadores mensais de disponibilidade das funções de transmissão ligadas a conversores.                       | Painel mensal por instalação/função de conversão e mês de referência, com métricas de disponibilidade, indisponibilidade programada e/ou forçada. Observação: Focado nos ativos de conversão e interligações associadas.                                                                                                                          |
| **Indicadores de Disponibilidade de Função Transmissão – Linhas de Transmissão e Transformadores**                    | Indicadores mensais de disponibilidade da função transmissão para linhas de transmissão e transformadores.     | O dicionário confirma uma modelagem compacta com campos como \`cod_caracteristica\`, \`dat_referencia\`, \`val_disp\`, \`val_indisppf\` e \`val_indispff\`, indicando uma linha por característica e mês de referência com métricas de disponibilidade/indisponibilidade. Observação: É um dos exemplos mais claros de base KPI mensal no portal. |
| **Indicadores de Qualidade de Energia da Rede Básica: DFD – Desempenho da Frequência em Distúrbios por Evento**       | Indicadores de desempenho da frequência durante distúrbios, em nível de evento.                                | Tabela de evento por ocorrência/distúrbio e data/hora, com métricas ligadas ao comportamento da frequência. Tem granularidade maior que a versão mensal/anual. Observação: É a visão mais detalhada do tema DFD.                                                                                                                                  |
| **Indicadores de Qualidade de Energia da Rede Básica: DFD – Desempenho da Frequência em Distúrbios - Mensal e Anual** | Agregação mensal e anual dos indicadores DFD.                                                                  | Painel consolidado por mês/ano e categoria, com métricas resumidas de qualidade da frequência em distúrbios. É a camada executiva do DFD. Observação: Naturalmente deve ser conciliado com a base por evento, e não analisado isoladamente.                                                                                                       |
| **Indicadores de Qualidade de Energia da Rede Básica: DFP – Desempenho da Frequência em Regime Permanente**           | Indicadores de desempenho da frequência em regime permanente.                                                  | Painel periódico por período e recorte de análise, com métricas de qualidade da frequência fora do contexto de distúrbios. É um KPI de estabilidade/qualidade contínua. Observação: Complementa o DFD ao deslocar o foco para o regime permanente.                                                                                                |
| **Interrupção de Carga**                                                                                              | Registros ou agregações de interrupções de carga no sistema.                                                   | Tabela de evento ou painel periódico por data/hora, local/subsistema e medida de carga interrompida, eventualmente com duração e causa. É uma base de impacto operacional sobre o atendimento. Observação: Pode ser combinada com ENS, CIPER e severidade das perturbações.                                                                       |

## 5.7 Custos, preços operativos e parâmetros econômicos

Família pequena, porém central para análises econômicas da operação.
Reúne custo marginal de operação em diferentes granularidades e custo
variável unitário das térmicas.

| **Conjuntos**              | 3                                                                                                                                                                                                                                      |
|----------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Modelagem predominante** | São séries ou parâmetros econômicos compactos, normalmente indexados por período de referência e subsistema/usina. Podem ser integrados às famílias de geração, carga e despacho para análises de custo e formação de sinal operativo. |

| **Conjunto de dados**       | **O que existe**                                      | **Estrutura predominante e observações**                                                                                                                                                                                                                         |
|-----------------------------|-------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **CMO Semanal**             | Custo Marginal de Operação em base semanal.           | Série por semana de referência + subsistema + patamar, com valor de CMO. A estrutura é enxuta e clássica para o setor: período, região e preço operativo. Observação: É a visão histórica mais agregada do sinal de custo marginal.                              |
| **CMO Semi-Horário**        | Custo Marginal de Operação em resolução semi-horária. | Série semi-horária por instante + subsistema, com valor de CMO. É estruturalmente um fato temporal de alta resolução e pode gerar volumes relevantes. Observação: Indicado para análises intradiárias e aderência da operação ao custo marginal.                 |
| **CVU das Usinas Térmicas** | Custo Variável Unitário das usinas térmicas.          | Tabela de referência ou periodicidade por usina/unidade e vigência/período, com o valor de CVU e atributos térmicos de apoio. É uma dimensão econômica da geração térmica. Observação: Deve ser cruzada com geração térmica e despacho para análises econômicas. |

## 5.8 Restrições operativas e constrained-off

Família dedicada às restrições de operação por constrained-off em usinas
eólicas e fotovoltaicas. O portal oferece tanto visões agregadas quanto
versões detalhadas por usina.

| **Conjuntos**              | 4                                                                                                                                                                                                                                                                  |
|----------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Modelagem predominante** | A estrutura predominante é de série periódica por período e ativo, com dimensões de classificação da restrição e métricas de energia/valor associado ao constrained-off. As versões “detalhamento por usina” aprofundam a granularidade causal e o nível do ativo. |

| **Conjunto de dados**                                                                          | **O que existe**                                                                                                           | **Estrutura predominante e observações**                                                                                                                                                                                                                                                     |
|------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Restrição de Operação por Constrained-off de Usinas Eólicas**                                | Apuração das restrições de operação por constrained-off de usinas eólicas enquadradas nas modalidades Tipo I, II-B e II-C. | Série periódica por usina, conjunto, subsistema ou classificação operacional e período de referência, com métricas de constrained-off. O portal sugere particionamento recorrente por período e acompanhamento histórico contínuo. Observação: É a visão agregada do constrained-off eólico. |
| **Restrição de Operação por Constrained-off de Usinas Eólicas - Detalhamento por Usina**       | Versão detalhada do constrained-off eólico, explicitamente aberta por usina.                                               | Tabela mais granular por usina e período/evento/causa, com quantidades restringidas e classificações adicionais. Em geral, é a melhor base para análises regulatórias, causais e de reconciliação fina. Observação: É mais detalhada do que a visão agregada e tende a ser mais volumosa.    |
| **Restrição de Operação por Constrained-off de Usinas Fotovoltaicas**                          | Apuração das restrições de operação por constrained-off para usinas fotovoltaicas.                                         | Série periódica por usina, conjunto ou recorte operacional, com medidas de constrained-off e classificação da restrição. A modelagem é análoga à da base eólica agregada. Observação: É a contraparte solar da visão agregada.                                                               |
| **Restrição de Operação por Constrained-off de Usinas Fotovoltaicas - Detalhamento por Usina** | Versão detalhada do constrained-off fotovoltaico por usina.                                                                | Tabela detalhada por usina e período/evento, com granularidade analítica suficiente para estudos de causa e impacto. Estruturalmente é o par solar da base detalhada eólica. Observação: É a base mais granular da família solar de constrained-off.                                         |

## 5.9 Colaborativo e documentação

Conjunto singular do catálogo que não é um dataset operacional
propriamente dito, mas sim uma entrada de apoio ao ecossistema de reuso
dos dados do portal.

| **Conjuntos**              | 1                                                                                                                                                       |
|----------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Modelagem predominante** | A estrutura não é de tabela de fatos. Trata-se de uma página-catálogica com recursos documentais em PDF e um link externo para o repositório do GitHub. |

| **Conjunto de dados**              | **O que existe**                                                                                                               | **Estrutura predominante e observações**                                                                                                                                                                                                                                                                                 |
|------------------------------------|--------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Ambiente Colaborativo - GITHUB** | Entrada do catálogo que aponta para o repositório colaborativo do ONS no GitHub e para PDFs de orientação de uso e publicação. | Não é uma base de dados operacional. Estruturalmente, funciona como item documental: recursos PDF + link externo para repositório de notebooks, com foco em comunidade e reuso. Observação: Foi considerado no fechamento das 80 entradas do catálogo, mas deve ser tratado separadamente das séries e cadastros do ONS. |

# 6. Leitura crítica do catálogo e recomendações de uso

- Monte um modelo analítico em camadas: primeiro os cadastros
  (reservatórios, usinas, linhas, subestações, modalidades), depois as
  tabelas-ponte, e por fim os fatos temporais e os indicadores
  agregados.

- Trate separadamente os níveis de agregação. As bases por reservatório,
  por REE, por bacia e por subsistema não são substitutas entre si; elas
  representam diferentes pontos da mesma hierarquia analítica.

- Respeite a natureza dos conjuntos de constrained-off, disponibilidade
  e indicadores: eles não são medições operativas brutas, mas apurações
  ou KPIs derivados.

- Use cuidado com cobertura histórica e particionamento dos arquivos.
  Algumas bases mudam a estratégia de particionamento ao longo do tempo,
  o que afeta ETL e incrementalidade.

- Não misture, no mesmo repositório analítico, a entrada “Ambiente
  Colaborativo - GITHUB” com tabelas operacionais. Ela deve ser tratada
  como documentação/ecossistema.

- Para casos com objetivo de reconciliação física, priorize as bases
  mais granulares (usina, reservatório, evento) e use as visões
  agregadas apenas como camada de validação e reporting.

# 7. Fontes consultadas

- Portal ONS Dados Abertos – página inicial do catálogo:
  https://dados.ons.org.br/

- Organização ONS no catálogo CKAN:
  https://dados.ons.org.br/organization/ons

- Catálogo geral de datasets: https://dados.ons.org.br/dataset/

- Página do Ambiente Colaborativo – GITHUB:
  https://dados.ons.org.br/dataset/ambiente-colaborativo

- Dicionário de dados – Dados Hidrológicos de Reservatórios / Base
  diária (PDF do portal).

- Dicionário de dados – Dados Hidrológicos de Reservatórios / Base
  horária (PDF do portal).

- Dicionário de dados – Indicadores de Disponibilidade de Função
  Transmissão – Linhas de Transmissão e Transformadores (PDF do portal).

Nota final: este relatório descreve a estrutura funcional dos conjuntos
do portal com base em metadados públicos. Quando um dicionário de dados
explícito estava disponível, a descrição foi feita no nível de campos.
Nos demais casos, a caracterização estrutural foi feita no nível de
granularidade, chaves e papel analítico do conjunto.
