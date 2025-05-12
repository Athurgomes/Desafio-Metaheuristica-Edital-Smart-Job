# Algoritmo Genetico Hibrido para Job Shop Scheduling

Este projeto implementa um algoritmo genetico combinado com Busca Tabu para resolver problemas de escalonamento em ambientes de producao (Job Shop Scheduling). O objetivo e encontrar a sequencia de operacoes que minimize o **makespan** (tempo total de conclusao).

## Como Funciona

### Estrutura do Codigo

- **Algoritmo Genetico (AG)**: Gera solucoes candidatas (individuos) e as evolui ao longo de geracoes.
- **Busca Tabu**: Refina periodicamente as melhores solucoes para escapar de otimos locais.
- **Multiprocessamento**: Acelera a avaliacao das solucoes usando todos os nucleos do processador.
- **Visualizacao**: Gera um grafico de Gantt para mostrar o cronograma das operacoes.

### Fluxo Principal

1. **Leitura dos Dados**: O usuario informa o numero de maquinas, jobs e as operacoes de cada job.
2. **Inicializacao**: Cria uma populacao inicial de solucoes validas.
3. **Avaliacao**: Calcula o makespan de cada solucao.
4. **Selecao e Cruzamento**: Combina as melhores solucoes para criar uma nova geracao.
5. **Mutacao**: Introduz variabilidade nas solucoes.
6. **Refinamento com Busca Tabu**: A cada X geracoes, aplica busca local nas melhores solucoes.
7. **Resultados**: Salva a melhor solucao encontrada e gera um grafico de Gantt.

## Parametros do Algoritmo

| Parametro           | Valor Padrao | Descricao                                      |
|---------------------|--------------|------------------------------------------------|
| TAMANHO_POPULACAO   | 90           | Quantidade de solucoes em cada geracao         |
| GERACOES            | 200          | Numero total de iteracoes do algoritmo         |
| TAXA_MUTACAO        | 0.2 (20%)    | Probabilidade de uma solucao sofrer mutacao    |
| FREQUENCIA_TABU     | 3            | A cada 3 geracoes aplica busca tabu            |
| TOP_REFINAMENTO     | 0.1 (10%)    | Porcentagem das melhores solucoes refinadas    |

## Como Executar

### Entrada de Dados
Digite os dados interativamente no formato:

Numero_de_maquinas Numero_de_jobs  
Job_0: Maquina1 Duracao1 Maquina2 Duracao2 ...  
Job_1: Maquina1 Duracao1 Maquina2 Duracao2 ...  
...  


Exemplo:
instance abz6  
Adams, and Zawack 10x10 instance (Table 1, instance 6)  
10 10  
7 62 8 24 5 25 3 84 4 47 6 38 2 82 0 93 9 24 1 66  
5 47 2 97 8 92 9 22 1 93 4 29 7 56 3 80 0 78 6 67  
1 45 7 46 6 22 2 26 9 38 0 69 4 40 3 33 8 75 5 96  
4 85 8 76 5 68 9 88 3 36 6 75 2 56 1 35 0 77 7 85  
8 60 9 20 7 25 3 63 4 81 0 52 1 30 5 98 6 54 2 86  
3 87 9 73 5 51 2 95 4 65 1 86 6 22 8 58 0 80 7 65  
5 81 2 53 7 57 6 71 9 81 0 43 4 26 8 54 3 58 1 69  
4 20 6 86 5 21 8 79 9 62 2 34 0 27 1 81 7 30 3 46  
9 68 6 66 5 98 8 86 7 66 0 56 3 82 1 95 4 47 2 78  
0 30 3 50 7 34 2 58 1 77 5 34 8 84 4 40 9 46 6 44  


### Saida Gerada
Dois arquivos serao criados:
1. **resultado_final.txt**: Contem a sequencia otima e o cronograma detalhado.
2. **grafico_gantt.png**: Mostra a distribuicao das operacoes nas maquinas ao longo do tempo.

### Execucao
python GA_TS_MultiProcessamento.py

Siga as instrucoes no terminal para inserir os dados. Apos a execucao, verifique os arquivos gerados.

## Referencias

1. Goldberg, D. E. (1989). *Genetic Algorithms in Search, Optimization, and Machine Learning*.
2. Mitchell, M. (1998). *An Introduction to Genetic Algorithms*.
3. Gonçalves, J. F., & Resende, M. G. C. (2005). *Hybrid GA-Tabu Search for Job Shop Scheduling*.
4. Glover, F., & Laguna, M. (1997). *Tabu Search*.
5. Eiben, Á. E., Hinterding, R., & Michalewicz, Z. (1999). *Parameter Control in Evolutionary Algorithms*.
