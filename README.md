# Aulas Gamificadas — Curso Técnico em Informática

Rosival Silva · 2026. Página inicial: https://rosivaldsilva-dev.github.io/aulas_gamificadas/

Cada aula fica em `DISCIPLINA/Axx-tema/index.html` e tem o próprio link:

| Disciplina | Aula | Link |
|---|---|---|
| POO | 04 · Operadores e Expressões | https://rosivaldsilva-dev.github.io/aulas_gamificadas/POO/A04-operadores/ |
| POO | 05 · Desvios Condicionais | https://rosivaldsilva-dev.github.io/aulas_gamificadas/POO/A05-condicionais/ |
| PWI | 01 · Introdução ao JavaScript | https://rosivaldsilva-dev.github.io/aulas_gamificadas/PWI/A01-javascript/ |
| PWI | 03 · Decisão em JavaScript | https://rosivaldsilva-dev.github.io/aulas_gamificadas/PWI/A03-decisao/ |
| SO | 03 · Treino antes da prova | https://rosivaldsilva-dev.github.io/aulas_gamificadas/SO/A03-treino-prova/ |
| SO | 03 · Missão Desktop | https://rosivaldsilva-dev.github.io/aulas_gamificadas/SO/A03-missao-desktop/ |

## Padrão de todas as aulas
- **Estrutura (1 aula de 50 min):** 5 níveis de **meta** (~7 questões cada, valem a nota) + 2 níveis **bônus** (~7 questões) + **Chefão** (~8 questões, libera quando a meta termina). Cerca de 57 questões.
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
1. Copie o `index.html` de uma aula da mesma disciplina para `DISCIPLINA/Axx-tema/`.
2. Troque os dados: `STORE`, `GAME`, `HAB` (habilidades) e `LEVELS` (8 níveis: 5 meta, 2 bônus e o Chefão com `"boss": true`).
3. Rode `python Ferramentas/padroniza_motor.py DISCIPLINA/Axx-tema/index.html` para garantir o padrão (trava de clique duplo, senha do professor, meta, **cor da disciplina, topo com nome/turma/nível e rodapé**). Pode rodar de novo sem estragar.
4. Acrescente um cartão no `index.html` da raiz, dentro da seção da disciplina (`<section class="poo|pwi|so|lp">`), para herdar a cor.
5. Aula com motor próprio (como a Missão Desktop) não passa pela ferramenta: aplique à mão a cor, o rodapé e o topo com nome, turma e nível.

Cuidados nos dados: em respostas digitadas (`type`), use palavras ou números (símbolos como `===` são ignorados na correção); em `slots` e `order`, não repita textos; dentro do texto, escreva `<\/script>` em vez de `</script>`.
