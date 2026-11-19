# Aulas Gamificadas — Curso Técnico em Informática

Rosival Silva · 2026. Página inicial: https://rosivaldsilva-dev.github.io/aulas_gamificadas/

Cada aula fica em `DISCIPLINA/DISC_Gam_Mod_NN/index.html` (NN = número do módulo, o mesmo da apostila `DISC_Ap_Mod_NN`; aulas extras: `DISC_Gam_Extra_NN`) e tem o próprio link. Os endereços antigos (`A05-condicionais` etc.) redirecionam para os novos.

| Disciplina | Aula | Link |
|---|---|---|
| LP | Mód. III · Laço PARA | https://rosivaldsilva-dev.github.io/aulas_gamificadas/LP/LP_Gam_Mod_03/ |
| LP | Extra 01 · Fluxogramas (as figuras, se/senão, enquanto e para; paralelo Portugol, Java e JavaScript com Scanner) | https://rosivaldsilva-dev.github.io/aulas_gamificadas/LP/LP_Gam_Extra_01/ |
| LP | Extra 01 · versão ae (Fluxogramas: passo a passo — 3 níveis de meta, 2 bônus e o Desafio final; errar não tira vida) | https://rosivaldsilva-dev.github.io/aulas_gamificadas/LP/LP_Gam_Extra_01_ae/ |
| LP | Extra 02 · Do fluxograma ao código (código↔desenho, esqueleto de arrastar, completar, executar e laboratório) | https://rosivaldsilva-dev.github.io/aulas_gamificadas/LP/LP_Gam_Extra_02/ |
| POO | Mód. IV · Operadores e Expressões | https://rosivaldsilva-dev.github.io/aulas_gamificadas/POO/POO_Gam_Mod_04/ |
| POO | Mód. V · Desvios Condicionais | https://rosivaldsilva-dev.github.io/aulas_gamificadas/POO/POO_Gam_Mod_05/ |
| POO | Mód. VI · Laços de Repetição | https://rosivaldsilva-dev.github.io/aulas_gamificadas/POO/POO_Gam_Mod_06/ |
| PWI | Mód. I · Introdução ao JavaScript | https://rosivaldsilva-dev.github.io/aulas_gamificadas/PWI/PWI_Gam_Mod_01/ |
| PWI | Mód. III · Decisão em JavaScript | https://rosivaldsilva-dev.github.io/aulas_gamificadas/PWI/PWI_Gam_Mod_03/ |
| SO | Mód. III · Treino antes da prova | https://rosivaldsilva-dev.github.io/aulas_gamificadas/SO/SO_Gam_Mod_03/ |
| SO | Mód. IV · Máquina Virtual | https://rosivaldsilva-dev.github.io/aulas_gamificadas/SO/SO_Gam_Mod_04/ |

## Padrão de todas as aulas
- **Estrutura (1 aula de 50 min):** 5 níveis de **meta** (~7 questões cada, valem a nota) + 3 níveis **bônus** (paralelo Portugol/Java/JavaScript, Entrada com `Scanner` e ache o erro) + **Chefão** (~11 questões, libera quando a meta termina). Cerca de 75 questões.
  Base: relatórios de 25/09/2026, com ~22 min de jogo efetivo por aula e a mediana dos alunos em 5 a 6 níveis.
- **Relatório:** mostra "Meta da aula: concluída ✔" ou "x de 5 níveis". É o número que vale para a nota.
- **Uma resposta por questão:** clique duplo ou toque repetido é ignorado (não pula questão, não tira vida duas vezes).
- **Área do professor (⚙️):** a senha do professor libera todas as fases naquele aparelho. A senha não fica escrita no código (só um hash dela).
- O progresso fica salvo no navegador do aluno. Todas as aulas estão no mesmo site (rosivaldsilva-dev.github.io), então o progresso continua ao trocar de link.

## Padrão visual (todas as aulas, atuais e futuras)
- **Cor da disciplina** (a mesma dos HTML e PDFs do projeto Curso Técnico em Informática): POO verde `#0b6b3a` · Programação Web (PWI) roxo `#5b3a8c` · Sistemas Operacionais (SO) vermelho `#9f1d1d` · Lógica (LP) azul `#274a9c`. Vale para o topo, botões, barra de progresso, tela de abertura e fundo, no modo claro e no escuro. Em SO o "errou" é laranja, para não confundir com o vermelho do tema, e o acerto continua verde. A disciplina é descoberta pelo nome da pasta (`POO/`, `PWI/`, `SO/`, `LP/`).
- **Rodapé:** "Rosival Silva · 2026" em todas as telas do jogo (abertura, trilha, teoria, questões e relatório). A página inicial também mostra o nome e o ano, no alto e no rodapé.
- **Topo durante o nível:** nome do aluno e turma, nível atual (com "Chefão" ou "Bônus" quando for o caso), barra de progresso e vidas (mais o cronômetro no Chefão).
- Para mudar uma cor ou o ano, edite `CORES`, `AUTOR` e `ANO` em `Ferramentas/padroniza_motor.py` e rode a ferramenta de novo nas aulas.

## Aula nova
1. Copie o `index.html` de uma aula da mesma disciplina para `DISCIPLINA/DISC_Gam_Mod_NN/`.
2. Troque os dados: `STORE`, `GAME`, `HAB` (habilidades) e `LEVELS` (9 níveis: 5 meta, 3 bônus e o Chefão com `"boss": true`).
3. Rode `python Ferramentas/padroniza_motor.py DISCIPLINA/DISC_Gam_Mod_NN/index.html` para garantir o padrão (trava de clique duplo, senha do professor, meta, **cor da disciplina, topo com nome/turma/nível e rodapé**). Pode rodar de novo sem estragar.
4. Acrescente um cartão no `index.html` da raiz, dentro da seção da disciplina (`<section class="poo|pwi|so|lp">`), para herdar a cor.
5. Aula com motor próprio não passa pela ferramenta: aplique à mão a cor, o rodapé e o topo com nome, turma e nível.

Tipos de questão com fluxograma (usados em `LP/LP_Gam_Extra_01` e `LP/LP_Gam_Extra_02`, o motor desenha as figuras no padrão "Formas de Fluxograma", uma cor só para todas):
- `fluxo` em qualquer questão (`pick`, `type`, `multi`): mostra um fluxograma no enunciado. Nós `{"i","k","t","x","r"}` (`k` = `inicio`, `fim`, `entrada`, `saida`, `proc`, `decisao`; `h:"t"` esconde o texto, `h:"f"` esconde a forma) e setas `[de, para, "rótulo", "rota"]`.
- `k` em um `pick`: mostra só a figura, sem texto, e pergunta o nome.
- `figura`: escolher entre quatro figuras (opções `entrada`, `saida`, `proc`, `decisao`).
- `slots` com `"fig": true`: liga figuras a nomes.
- `montar`: ordenar figuras para montar o fluxograma.
- `hotf`: tocar na figura certa dentro do fluxograma.
- `cola` (no nível) e `@@cola:saida,entrada,scanner@@` (na teoria): quadro de equivalências Portugol / Java / JavaScript, recolhível durante as questões.

Cuidados nos dados: em respostas digitadas (`type`), use palavras ou números (símbolos como `===` são ignorados na correção); em `slots` e `order`, não repita textos; dentro do texto, escreva `<\/script>` em vez de `</script>`.

Tipos novos da `LP/LP_Gam_Extra_02` (gerada a partir do motor da Extra 01):
- `qflux`: o aluno vê o código e escolhe, entre 3 desenhos, o fluxograma que o representa.
- `esq`: esqueleto do fluxograma com espaços vazios; o aluno **arrasta ou toca** a figura certa em cada espaço.
- `compl`: fluxograma pronto e código com lacunas `{0}`, `{1}`...; o aluno arrasta ou toca a peça em cada lacuna.
- `exec`: o marcador percorre o fluxograma; o aluno responde Sim/Não nas decisões e o novo valor nos processamentos (tabela de variáveis e "tela" do programa).
- `missao`: cartão de laboratório com fluxograma, modelo de código para copiar, link do Portugol Web Studio (portugol.dev) ou do OneCompiler (Java) e um valor de teste calculado do nome do aluno; ele digita o que o programa mostrou.
