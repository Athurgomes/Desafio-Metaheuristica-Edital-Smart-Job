# Desafio-Metaheuristica-Edital-Smart-Job
```markdown
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
```
Numero_de_maquinas Numero_de_jobs
Job_0: Maquina1 Duracao1 Maquina2 Duracao2 ...
Job_1: Maquina1 Duracao1 Maquina2 Duracao2 ...
...
```

Exemplo:
```
3 2
Job 0: 0 5 1 3
Job 1: 1 4 2 6
```

### Saida Gerada
Dois arquivos serao criados:
1. **resultado_final.txt**: Contem a sequencia otima e o cronograma detalhado.
2. **grafico_gantt.png**: Mostra a distribuicao das operacoes nas maquinas ao longo do tempo.

### Execucao
```bash
python GA_TS_MultiProcessamento.py
```

Siga as instrucoes no terminal para inserir os dados. Apos a execucao, verifique os arquivos gerados.

## Referencias

1. Goldberg, D. E. (1989). *Genetic Algorithms in Search, Optimization, and Machine Learning*.
2. Mitchell, M. (1998). *An Introduction to Genetic Algorithms*.
3. Gonçalves, J. F., & Resende, M. G. C. (2005). Hybrid GA-Tabu Search for Job Shop Scheduling.
4. Glover, F., & Laguna, M. (1997). *Tabu Search*.
```
