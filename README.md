# <p align = "center">API 6º Semestre - BD 2026


<p align="center">
  <a href=#requisitos-funcionais-e-nao-funcionais>Requisitos Funcionais e Não Funcionais</a> •
  <a href=></a> •
  <a href=></a> •
  <a href=></a> •
  <a href=></a> •
  <a href=></a> •
  <a href=></a> •
  <a href=></a> •
  <a href=></a> •
  <a href=></a>

</p>

## :bulb: Contexto e Desafio <a id="problema"></a>

## :dart: Objetivo do Projeto

## Requisitos Funcionais e Não Funcionais<a id="requisitos-funcionais-e-nao-funcionais"></a>

<details>
<summary>Exibir Requisitos Funcionais e Não Funcionais</summary>

### Requisitos Funcionais

<details>
<summary>Exibir Requisitos Funcionais</summary><br>

| ID | Requisito | Descrição |
|:---|:---|:---|
| <a id="RF01">RF01</a> | _Pipeline ETL_ | O sistema deve realizar a extração, o tratamento e o carregamento (ETL) dos dados provenientes da base disponibilizada pela ANEEL, com registro de logs e controle de versionamento dos dados. |
| <a id="RF02">RF02</a> | _Dashboard de Redes de Distribuição_ | O sistema deve exibir dados referentes às estruturas das redes de distribuição (informações geográficas, elétricas e estruturais) via dashboards e relatórios interativos. |
| <a id="RF03">RF03</a> | _Relatórios de Redes de Distribuição_ | O sistema deve exibir indicadores e métricas de qualidade das redes elétricas (DEC, FEC e perdas de energia), permitindo filtragem por região e período. |
| <a id="RF04">RF04</a> | _Cálculo de TAM Físico_ | O sistema deve calcular e exibir os valores de TAM (Total Addressable Market) físico de instalação de sensores na rede elétrica, identificando o número máximo de pontos tecnicamente monitoráveis no Brasil. |
| <a id="RF05">RF05</a> | _Classificação por Criticidade com ML_ | O sistema deve agrupar regiões ou áreas da rede por nível de criticidade (alta, média, baixa), aplicando modelos de Machine Learning para apoiar a priorização de ações. |
| <a id="RF06">RF06</a> | _Ranking de Perdas de Energia_ | O sistema deve gerar um ranking de regiões com base nos indicadores de perdas de energia, utilizando modelos de regressão para projeção e ordenação das áreas mais críticas. |
| <a id="RF07">RF07</a> | _Gestão de Usuários e Perfis_ | O sistema deve permitir o cadastro de usuários com perfis distintos (Administrador e Analista), controlando o acesso a funcionalidades e dados conforme o perfil. |
| <a id="RF08">RF08</a> | _Cálculo de SAM_ | O sistema deve calcular e exibir os valores de SAM, cruzando o TAM com critérios técnicos, regulatórios e de viabilidade operacional. |
| <a id="RF09">RF09</a> | _Mapa de Calor Geográfico_ | O sistema deve exibir um mapa de calor (heatmap) geográfico indicando o nível de criticidade da rede elétrica por região, com suporte a filtros dinâmicos por indicador. |
| <a id="RF10">RF10</a> | _Conformidade com LGPD_ | O sistema deve garantir conformidade com a LGPD: coleta de consentimento explícito, anonimização de dados pessoais, política de retenção e exclusão, e geração de relatório de tratamento de dados (ROPA simplificado para fins acadêmicos). |

</details>

### Requisitos Não Funcionais

<details>
<summary>Exibir Requisitos não Funcionais</summary><br>

| ID | Requisito | Descrição |
|:---|:---|:---|
| <a id="RNF01">RNF01</a> | _Performance de Consultas ao Banco_ | As consultas críticas ao banco de dados — relacional (dados sensíveis) e MongoDB (dados da ANEEL) — devem apresentar desempenho adequado para uso fluido da aplicação, com uso de paginação e índices básicos.|
| <a id="RNF02">RNF02</a> | _Inicialização e Estabilidade da Aplicação_ | A aplicação web deve inicializar corretamente e operar de forma estável durante sessões contínuas de uso, sem travamentos ou erros inesperados. |
| <a id="RNF03">RNF03</a> | _Responsividade e Compatibilidade_ | A interface deve ser responsiva, garantindo compatibilidade e boa experiência em navegadores modernos. |
| <a id="RNF04">RNF04</a> | _Métricas de Desempenho de ML_ | O desempenho do modelo de machine learning treinado deve ser documentado com as métricas adequadas ao tipo de tarefa: Silhouette Score para clustering, RMSE para regressão e F1-Score para classificação. |
| <a id="RNF05">RNF05</a> | _Consistência Pós-Carga Manual_ | Sempre que houver nova carga de dados os indicadores (DEC, FEC e perdas) devem ser recalculados, com exibição da data/hora da última carga e identificação da versão do lote utilizado. |

</details>
</details>

<a id=""></a>

## :date: Backlog do Produto <a id="date-backlog-do-produto"></a>
<details>

<summary>Mostrar Backlog do Produto</summary>

<br>

| ID | Rank | Prioridade | User Story | Sprint | Requisitos Relacionados |
|:---|:---|:---|:---|:---|:---|


</details>

## :date: Sprint Backlog <a id="date-sprint-backlog"></a>
<details>

<summary>Mostrar Spring Backlog</summary>

### Sprint 1

| ID | Rank | Prioridade na Sprint | User Story | Requisitos Relacionados |
|:---|:---|:---|:---|:---|

### Sprint 2</summary>

| ID | Rank | Prioridade na Sprint | User Story | Requisitos Relacionados |
|:---|:---|:---|:---|:---|

### Sprint 3

| ID | Rank | Prioridade na Sprint | User Story | Requisitos Relacionados |
|:---|:---|:---|:---|:---|

</details>

<br>

## :calendar: <a id="cronograma"> Cronograma 📅 </a>

| Sprint  | Nome | Data inicio  | Data Fim | Status |
| --- | -------------------------- | --------| ----- | --- |
| --- | KickOff                    | 02/03   | 06/03 |     |
| --- | Planejamento               | 09/03   | 13/13 |     |
|  1  | Sprint 1                   | 16/03   | 05/04 |     |
|  2  | Sprint review / Planning   | 06/04   | 10/04 |     |
|  3  | Sprint 2                   | 13/04   | 03/05 |     |
|  4  | Sprint review / Planning   | 04/05   | 08/05 |     |
|  5  | Sprint 3                   | 11/05   | 31/05 |     |
|  6  | Sprint review              | 01/06   | 05/06 |     |
|  7  | Feira de Soluções          | 11/06   |       |     |
|  8  | Apresentações TGs          | 15/06   | 19/06 |     |

<br>

## :mortar_board: Integrantes da Equipe:

| *Nome*                   | *Função*            | *LinkedIn*                                                  |
|:------------------:|:-----------------:|:---------------------------------------:|
| Vinicius Monteiro | Product Owner     | [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?style=flat-square&logo=linkedin&labelColor=blue)](https://www.linkedin.com/in/viniciusvasm/ ) |
| Cesar Pelogia | Scrum Master  | [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?style=flat-square&logo=linkedin&labelColor=blue)](http://www.linkedin.com/in/cesar-augusto-anselmo-pelogia-truyts-94a08a268/ ) |
| Alexandre Jonas | Developer     | [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?style=flat-square&logo=linkedin&labelColor=blue)](http://www.linkedin.com/in/alexandre-jonas-de-souza-fonseca-989920181/) |
| Eliézer Lopes     | Developer     | [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?style=flat-square&logo=linkedin&labelColor=blue)](https://www.linkedin.com/in/eli%C3%A9zer-lopes/) |
| Lucas Henrique | Developer     | [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?style=flat-square&logo=linkedin&labelColor=blue)](https://www.linkedin.com/in/lucashenriqueco/) |
| Gabriel Souza | Developer     | [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?style=flat-square&logo=linkedin&labelColor=blue)](http://www.linkedin.com/in/gabriel-alves-de-souza-5b7747267/) |
| Gustavo Robert     | Developer     | [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?style=flat-square&logo=linkedin&labelColor=blue)](http://www.linkedin.com/in/gustavo-robert/) |
| Vitor Morais       | Developer     | [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?style=flat-square&logo=linkedin&labelColor=blue)](http://www.linkedin.com/in/vitor-faria-morais-330b19204/) |

</br>

## Padrões de Processo <a id="padroes-processos"></a>
[Wiki]()

</br>

## Gráfico Burndown

<img src="burndown/src/main/resources/static/burndown.png">

</br>

## Tecnologias Utilizadas

## Burndown Automatico

Guia completo de uso, execução local e CI:

- `burndown/README.md`
