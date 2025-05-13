import random
import matplotlib.pyplot as plt # type: ignore
from collections import defaultdict, deque
from multiprocessing import Pool, cpu_count
import time

#FUNCAO PARA LER DADOS DO USUARIO
def ler_entrada_interativa():
    print("Digite a quantidade de maquinas e trabalhos:")
    maquinas, num_jobs=map(int, input().strip().split())
    job_machines=[]
    job_durations=[]
    #Para cada job, pegar maquinas e tempos de operacao
    for i in range(num_jobs):
        print(f"Job {i}:")
        dados=list(map(int, input().strip().split()))
        job_machines.append(dados[::2])  #Maquinas usadas nas operacoes
        job_durations.append(dados[1::2])  #Tempos de cada operacao
    return maquinas, num_jobs, job_machines, job_durations

#PARAMETROS DO ALGORITMO
'''TAMANHO_POPULACAO=90 #Quantidade de solucoes na populacao
GERACOES=200 #Quantidade de iteracoes do algoritmo
TAXA_MUTACAO=0.2 #Chance de uma solucao sofrer mutacao
FREQUENCIA_TABU=3 #A cada quantas geracoes aplica busca tabu
TOP_REFINAMENTO=0.1 #Porcentagem das melhores solucoes para refinamento'''

TAMANHO_POPULACAO=90 #Quantidade de solucoes na populacao
GERACOES=100 #Quantidade de iteracoes do algoritmo
TAXA_MUTACAO=0.2 #Chance de uma solucao sofrer mutacao
FREQUENCIA_TABU=3 #A cada quantas geracoes aplica busca tabu
TOP_REFINAMENTO=0.1 #Porcentagem das melhores solucoes para refinamento

#FUNCOES PARA MANIPULAR POPULACAO
def avaliar_wrapper(args):
    return avaliar_individuo(*args)

def busca_tabu_wrapper(args):
    return busca_tabu(*args)

def gerar_individuo_valido(job_machines):
    #Cria uma sequencia valida de operacoes respeitando a ordem dos jobs
    operacoes_pendentes=[(j,0) for j in range(len(job_machines))]
    individuo=[]
    while operacoes_pendentes:
        #Escolhe aleatoriamente uma operacao pendente
        job_id, op_idx=random.choice(operacoes_pendentes)
        individuo.append((job_id, op_idx))
        operacoes_pendentes.remove((job_id, op_idx))
        #Adiciona proxima operacao do mesmo job se existir
        if op_idx+1<len(job_machines[job_id]):
            operacoes_pendentes.append((job_id, op_idx+1))
    return individuo

def criar_populacao(n, job_machines):
    #Gera uma populacao inicial de n individuos validos
    return [gerar_individuo_valido(job_machines) for _ in range(n)]

#FUNCOES PARA AVALIAR SOLUCOES
def avaliar_individuo(individuo, job_machines, job_durations, num_maquinas):
    #Calcula o makespan (tempo total) de uma solucao
    tempos_maquinas=[0]*num_maquinas
    tempos_jobs=[0]*len(job_machines)
    for job_id, op_idx in individuo:
        maquina=job_machines[job_id][op_idx]
        duracao=job_durations[job_id][op_idx]
        #Calcula inicio considerando disponibilidade da maquina e do job
        inicio=max(tempos_maquinas[maquina], tempos_jobs[job_id])
        fim=inicio+duracao
        #Atualiza os tempos
        tempos_maquinas[maquina]=fim
        tempos_jobs[job_id]=fim
    #O makespan e o maior tempo de conclusao entre todos os jobs
    return max(tempos_jobs)

#OPERADORES GENETICOS
def crossover(pai1, pai2):
    #Combina duas solucoes para criar um filho
    ponto1, ponto2 = sorted(random.sample(range(len(pai1)), 2))
    parte_pai1=pai1[ponto1:ponto2]
    parte_pai2=[op for op in pai2 if op not in parte_pai1]
    return parte_pai2[:ponto1]+parte_pai1+parte_pai2[ponto1:]

def mutacao(individuo):
    #Troca duas operacoes de lugar se nao quebrar a ordem do job
    for _ in range(10): #Tenta no maximo 10 vezes
        i,j=sorted(random.sample(range(len(individuo)), 2))
        a,b=individuo[i], individuo[j]
        #Nao permite trocar operacoes do mesmo job fora de ordem
        if a[0]==b[0] and abs(a[1]-b[1])!=1:
            continue
        novo=individuo.copy()
        novo[i], novo[j]=novo[j], novo[i]
        return novo
    return individuo #Se nao conseguir, retorna original

#BUSCA TABU PARA REFINAMENTO LOCAL
def busca_tabu(solucao, job_machines, job_durations, num_maquinas, max_iter=30, tabu_size=7):
    #Melhora uma solucao explorando vizinhanca
    melhor_solucao=solucao.copy()
    melhor_tempo=avaliar_individuo(melhor_solucao, job_machines, job_durations, num_maquinas)
    lista_tabu=deque(maxlen=tabu_size) #Memoriza movimentos recentes
    for _ in range(max_iter):
        #Gera vizinhos trocando operacoes adjacentes
        vizinhos=[]
        for i in range(len(solucao)-1):
            #Nao permite trocas invalidas no mesmo job
            if solucao[i][0]==solucao[i+1][0] and solucao[i][1]>solucao[i+1][1]:
                continue 
            vizinho=solucao.copy()
            vizinho[i], vizinho[i+1]=vizinho[i+1], vizinho[i]
            vizinhos.append((vizinho, (i,i+1)))
        #Avalia vizinhos nao tabu
        candidatos=[]
        for viz, movimento in vizinhos:
            if movimento in lista_tabu:
                continue
            tempo=avaliar_individuo(viz, job_machines, job_durations, num_maquinas)
            candidatos.append((tempo, viz, movimento))
        if not candidatos:
            break
        #Seleciona melhor vizinho
        melhor_candidato=sorted(candidatos)[0]
        solucao=melhor_candidato[1]
        lista_tabu.append(melhor_candidato[2])
        #Atualiza melhor solucao encontrada
        if melhor_candidato[0]<melhor_tempo:
            melhor_solucao=solucao.copy()
            melhor_tempo=melhor_candidato[0]
    return melhor_solucao

#EXECUCAO PRINCIPAL
if __name__=='__main__':
    inicio=time.time()
    #Ler dados do problema
    maquinas, num_jobs, job_machines, job_durations=ler_entrada_interativa()
    #Criar populacao inicial
    populacao=criar_populacao(TAMANHO_POPULACAO, job_machines)
    
    #Configurar processamento paralelo
    with Pool(processes=cpu_count()) as pool:
        #Loop principal das geracoes
        for geracao in range(1, GERACOES+1):
            #Avaliar todas as solucoes em paralelo
            args=[(ind, job_machines, job_durations, maquinas) for ind in populacao]
            tempos=pool.map(avaliar_wrapper, args)
            #Ordenar populacao pelo makespan
            populacao=[ind for _,ind in sorted(zip(tempos, populacao))]
            #Manter as 2 melhores solucoes (elitismo)
            nova_geracao=populacao[:2]
            # Preencher nova geracao com cruzamentos
            while len(nova_geracao)<TAMANHO_POPULACAO:
                #Selecionar pais entre os 15 melhores
                pai1, pai2=random.sample(populacao[:15], 2)
                filho=crossover(pai1, pai2)
                #Aplicar mutacao com certa probabilidade
                if random.random()<TAXA_MUTACAO:
                    filho=mutacao(filho)
                nova_geracao.append(filho)
            #A cada X geracoes, aplicar busca tabu nas melhores solucoes
            if geracao%FREQUENCIA_TABU==0:
                quantidade=max(1, int(TAMANHO_POPULACAO*TOP_REFINAMENTO))
                melhores=nova_geracao[:quantidade]
                args=[(ind, job_machines, job_durations, maquinas) for ind in melhores]
                refinados=pool.map(busca_tabu_wrapper, args)
                nova_geracao[:quantidade]=refinados
            populacao=nova_geracao
            print(f"Geracao {geracao}: Melhor makespan = {min(tempos)}")

    #SALVAR RESULTADOS EM ARQUIVO E GERAR GRAFICO
    with open("resultado_final.txt", "w") as arquivo:
        #Encontrar melhor solucao final
        melhor=min(populacao, key=lambda x: avaliar_individuo(x, job_machines, job_durations, maquinas))
        makespan=avaliar_individuo(melhor, job_machines, job_durations, maquinas)
        #Escrever detalhes da solucao
        arquivo.write(f"Melhor sequencia:\n{melhor}\n\n")
        arquivo.write(f"Makespan final: {makespan}\n")
        arquivo.write(f"Tempo total: {time.time()-inicio:.2f}s\n\n")
        #Calcular cronograma por maquina
        tempos_maquinas=[0]*maquinas
        tempos_jobs=[0]*num_jobs
        alocacao=defaultdict(list)
        for job_id, op_idx in melhor:
            maquina=job_machines[job_id][op_idx]
            duracao=job_durations[job_id][op_idx]
            inicio_op=max(tempos_maquinas[maquina], tempos_jobs[job_id])
            fim_op=inicio_op+duracao
            alocacao[maquina].append( (inicio_op, fim_op, f"J{job_id}-O{op_idx}") )
            tempos_maquinas[maquina]=fim_op
            tempos_jobs[job_id]=fim_op
        #Gerar grafico de Gantt
        fig, ax=plt.subplots(figsize=(12,6))
        cores=plt.cm.tab20.colors
        for maq in range(maquinas):
            for inicio, fim, nome in sorted(alocacao[maq], key=lambda x: x[0]):
                ax.barh(maq, fim-inicio, left=inicio, color=cores[maq%len(cores)], edgecolor='black')
                ax.text( (inicio+fim)/2, maq, nome, ha='center', va='center', fontsize=8)
        ax.set_yticks(range(maquinas))
        ax.set_yticklabels([f"Maquina {i}" for i in range(maquinas)])
        ax.set_xlabel("Tempo")
        ax.set_title("Cronograma de Execucao")
        plt.tight_layout()
        plt.savefig("grafico_gantt.png")
        plt.close()
        #Escrever detalhes no arquivo
        arquivo.write("Detalhes por maquina:\n")
        for maq in range(maquinas):
            arquivo.write(f"Maquina {maq}:\n")
            for inicio, fim, nome in sorted(alocacao[maq], key=lambda x: x[0]):
                arquivo.write(f"  {nome}: {inicio} - {fim}\n")
            arquivo.write("\n")
    print("Processo concluido! Dados salvos em resultado_final.txt e grafico_gantt.png")