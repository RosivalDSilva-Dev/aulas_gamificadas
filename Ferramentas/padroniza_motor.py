"""Uso: python Ferramentas/padroniza_motor.py POO/POO_Gam_Mod_07/index.html

Padroniza o motor das aulas gamificadas (trilha com niveis/estrelas).
- trava de uma resposta por questao (clique duplo nao pula questao nem tira vida 2x)
- barra de progresso so avanca no acerto
- area do professor com senha para liberar todas as fases
- cor tema da disciplina (POO verde, PWI roxo, SO vermelho, LP azul: as cores dos HTML do projeto), pela pasta da aula
- topo do jogo com nome, turma e nivel atual (mantendo vidas e cronometro)
- rodape "Rosival Silva · ano" em todas as telas
- modo professor (projetor), ligado com a senha: ordem fixa, botao "Ver resposta", sem cronometro e gabarito
"""
import sys, re, json

SENHA_HASH = '8570079599154905'  # h53("javhash404!")

CSS_ADD = """
.travado #app{pointer-events:none}
.pwrow{display:flex;gap:10px;margin-top:10px}
.pwrow input{flex:1}
.pwerr{color:var(--bad-d,#b3261e);font-size:14px;min-height:20px;margin-top:6px}
"""

CFG = r'''/* --- area do professor (senha) --- */
function h53(str){var h1=0xdeadbeef,h2=0x41c6ce57;for(var i=0,ch;i<str.length;i++){ch=str.charCodeAt(i);h1=Math.imul(h1^ch,2654435761);h2=Math.imul(h2^ch,1597334677);}h1=Math.imul(h1^(h1>>>16),2246822507);h1^=Math.imul(h2^(h2>>>13),3266489909);h2=Math.imul(h2^(h2>>>16),2246822507);h2^=Math.imul(h1^(h1>>>13),3266489909);return 4294967296*(2097151&h2)+(h1>>>0);}
var SENHA_PROF="__HASH__";
function telaConfig(){
  jogo=null;
  var h=topo('<button class="iconbtn" id="volta">←</button><div class="grow"><b style="font-size:15px">Área do professor</b></div>');
  if(S.liberarTudo){
    h+='<div class="card"><h3>🔓 Todas as fases liberadas</h3>'+
       '<p class="sub">Neste aparelho, todos os níveis da trilha (inclusive o desafio final) estão abertos.</p>'+
       '<button class="btn ghost small" id="trancar">Bloquear de novo</button></div>';
  }else{
    h+='<div class="card"><h3>🔒 Liberar todas as fases</h3>'+
       '<p class="sub">Uso do professor: libera todos os níveis desta trilha neste aparelho, sem precisar concluir os anteriores.</p>'+
       '<div class="pwrow"><input type="password" id="pw" autocomplete="off" placeholder="Senha do professor">'+
       '<button class="btn" id="lib" style="width:auto;margin:0">Liberar</button></div>'+
       '<div class="pwerr" id="pwerr"></div></div>';
  }
  h+='<button class="btn ghost" id="volta2">Voltar para a trilha</button>';
  app.innerHTML=h;
  $("#volta").onclick=$("#volta2").onclick=telaMapa;
  if(S.liberarTudo){
    $("#trancar").onclick=function(){S.liberarTudo=false;save();telaMapa();};
  }else{
    var pw=$("#pw");
    var tenta=function(){
      if(String(h53(pw.value))===SENHA_PROF){S.liberarTudo=true;save();telaMapa();}
      else{$("#pwerr").textContent="Senha incorreta.";pw.value="";pw.focus();}
    };
    $("#lib").onclick=tenta;
    pw.addEventListener("keydown",function(e){if(e.key==="Enter")tenta();});
    setTimeout(function(){pw.focus();},100);
  }
  window.scrollTo(0,0);
}
'''.replace('__HASH__', SENHA_HASH)


def sub1(h, old, new, nome):
    assert old in h, 'nao achei: ' + nome
    return h.replace(old, new, 1)


def patch(h):
    if 'SENHA_PROF' in h:  # ja padronizado
        return h
    # CSS
    if '.travado #app' not in h:
        h = sub1(h, '</style>', CSS_ADD + '</style>', 'css')
    else:
        h = sub1(h, '</style>', CSS_ADD.replace('.travado #app{pointer-events:none}\n', '') + '</style>', 'css')
    # julgar com trava
    if 'jogo.travado' not in h or 'if(!jogo||jogo.travado)return;' not in h:
        h = sub1(h, 'function julgar(q,ok,msg){\n',
                 'function julgar(q,ok,msg){\n'
                 '  if(!jogo||jogo.travado)return;          /* uma resposta por questão: ignora toques extras */\n'
                 '  jogo.travado=true;document.body.classList.add("travado");\n', 'julgar')
    if '  jogo.respondidas++;\n  if(ok){ S.xp+=q._rep?4:10; }' in h:
        h = h.replace('  jogo.respondidas++;\n  if(ok){ S.xp+=q._rep?4:10; }',
                      '  if(ok){ jogo.respondidas++; S.xp+=q._rep?4:10; }', 1)
    assert 'if(ok){ jogo.respondidas++;' in h, 'respondidas'
    if 'bc._ok' not in h:
        h = sub1(h, '  $("#cont").onclick=function(){\n    f.remove();\n',
                 '  var bc=f.querySelector("#cont");\n  bc.onclick=function(){\n    if(bc._ok)return;bc._ok=true;\n'
                 '    f.remove();document.body.classList.remove("travado");\n', 'cont')
        h = sub1(h, '  $("#cont").focus();', '  bc.focus();', 'focus')
    if 'var velho=document.querySelector(".feed")' not in h:
        h = sub1(h, 'function render(q){\n  if(cron){clearInterval(cron);cron=null;}\n  var lv=jogo.lv;\n',
                 'function render(q){\n  if(cron){clearInterval(cron);cron=null;}\n  var lv=jogo.lv;\n'
                 '  jogo.travado=false;document.body.classList.remove("travado");\n'
                 '  var velho=document.querySelector(".feed");if(velho)velho.remove();\n', 'render')
    # codigo (rows) aparece em todas as questoes, nao so nas de "tocar no trecho"
    if 'q.rows&&q.t!=="hot"' not in h:
        h = sub1(h, "  h+='<h2 style=\"margin-bottom:12px\">'+esc(q.p)+'</h2>';\n",
                 "  h+='<h2 style=\"margin-bottom:12px\">'+esc(q.p)+'</h2>';\n  if(q.rows&&q.t!==\"hot\")h+=sCode(q.rows);\n", 'rows no enunciado')
    # respostas digitadas: aceita "imprime 5", "o resultado e 5" etc.
    if 'function limpaResp' not in h and 'function norm(s)' in h:
        i = h.index('\n', h.index('function norm(s)')) + 1
        h = h[:i] + '''function limpaResp(v){
  v=norm(v);var r=/^(aparece|apareceria|imprime|imprimiria|imprimiu|mostra|escreve|sera|seria|resulta em|resultado|o resultado e|o resultado seria|a resposta e|resposta|e|eh|fica|vai imprimir|vai aparecer|o|a|um|uma)\\s+/;
  var ant;do{ant=v;v=v.replace(r,"");}while(v!==ant&&v.length>1);
  return v;
}
''' + h[i:]
        h = h.replace('var ok=q.ac.some(function(a){return norm(a)===v;});',
                      'var ok=q.ac.some(function(a){return norm(a)===v||norm(a)===limpaResp(v)||limpaResp(a)===limpaResp(v);});', 1)
    # liberar tudo
    if 'liberarTudo:false' not in h:
        h = h.replace('sessoes:0}', 'sessoes:0,liberarTudo:false}')
    h = h.replace('  if(i===0)return true;', '  if(i===0||S.liberarTudo)return true;')
    assert 'S.liberarTudo)return true' in h, 'desbloqueado'
    if 'id="cfg"' not in h:
        h = sub1(h, """'<button class="iconbtn" id="rep" title="Relatório">📋</button>')""",
                 """'<button class="iconbtn" id="rep" title="Relatório">📋</button>'+\n    '<button class="iconbtn" id="cfg" title="Área do professor">⚙️</button>')""", 'botao cfg')
        h = sub1(h, '  $("#rep").onclick=$("#rep2").onclick=function(){telaRelatorio();};\n',
                 '  $("#rep").onclick=$("#rep2").onclick=function(){telaRelatorio();};\n  $("#cfg").onclick=telaConfig;\n', 'cfg onclick')
    else:
        h = h.replace('id="cfg" title="Configurações"', 'id="cfg" title="Área do professor"')
    # tela de configuracao (troca a antiga, sem senha)
    h = re.sub(r'/\* --- configurações --- \*/\nfunction telaConfig\(\)\{.*?\n\}\n', '', h, flags=re.S)
    assert 'function telaConfig' not in h, 'telaConfig antiga'
    m = re.search(r'\n(/\* [-=]+ ?teoria[^\n]*\n)?function telaTeoria\(lv\)\{', h)
    assert m, 'telaTeoria'
    h = h[:m.start()] + '\n' + CFG + h[m.start():]
    # relatorio
    h = sub1(h, '     kv("Data",', '     (S.liberarTudo?kv("Fases liberadas pelo professor","sim"):"")+\n     kv("Data",', 'relatorio')
    return h


# ---------------------------------------------------------------- META DA AULA
# Padrao (2026-09): 5 niveis de META (valem a nota) + 2 BONUS + 1 CHEFAO (libera com a meta).
META_JS = r"""
/* --- meta da aula: os META primeiros niveis valem a nota; depois vem bonus; chefao libera com a meta --- */
var META=(typeof GAME!=="undefined"&&GAME.meta)||5;
function metaFeitos(){var n=0;for(var i=0;i<META&&i<LEVELS.length;i++){var st=S.niveis[LEVELS[i].id];if(st&&st.estrelas>0)n++;}return n;}
function metaOk(){return metaFeitos()>=META;}
function metaTxt(){return metaOk()?"concluída ✔":metaFeitos()+" de "+META+" níveis";}
function secaoNivel(i,lv){
  if(i===0)return '<div class="secao">🎯 Meta da aula · vale a nota</div>';
  if(lv.boss)return '<div class="secao">🏆 Chefão · libera quando a meta termina</div>';
  if(i===META)return '<div class="secao">⭐ Bônus · para ir além</div>';
  return '';
}
"""
META_CSS = """
.secao{font-size:12.5px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;color:var(--ink-2);margin:16px 4px 6px}
.metabox{background:var(--gold-l);border:1.5px solid var(--gold);border-radius:12px;padding:10px 14px;margin:0 0 12px;font-size:15px}
"""


def meta(h):
    if 'function metaOk' in h:
        return h
    h = sub1(h, '</style>', META_CSS + '</style>', 'css meta')
    h = sub1(h, 'function totalEstrelas(){', META_JS + 'function totalEstrelas(){', 'meta js')
    h, n = re.subn(r'if\(lv\.boss\)return concluidos\(\)>=[^;]+;', 'if(lv.boss)return metaOk();', h)
    assert n == 1, 'boss unlock'
    h = sub1(h, """h+='<button class="node'""", """h+=secaoNivel(i,lv);h+='<button class="node'""", 'secoes')
    h = h.replace('(lv.boss?("conclua os "+GAME.bossUnlock+" níveis"):', '(lv.boss?("conclua a meta ("+META+" níveis)"):')
    h = h.replace('(lv.boss?"conclua os 8 níveis":', '(lv.boss?("conclua a meta ("+META+" níveis)"):')
    assert 'conclua a meta' in h, 'rotulo chefao'
    h = sub1(h, """   '<div class="trail">';""",
             """   '<div class="metabox">🎯 Meta da aula: <b>'+metaTxt()+'</b>'+(metaOk()?' · agora é bônus ou Chefão!':'')+'</div>'+\n   '<div class="trail">';""", 'metabox mapa')
    h = sub1(h, '     kv("Níveis concluídos"', '     kv("Meta da aula",metaTxt())+\n     kv("Níveis concluídos"', 'kv meta')
    h = sub1(h, '  linha("Níveis concluídos"', '  linha("Meta da aula",metaTxt());\n  linha("Níveis concluídos"', 'png meta')
    h = re.sub(r'var W=900,H=(\d+)', lambda m: 'var W=900,H=%d' % (int(m.group(1)) + 42), h, count=1)
    h = sub1(h, 'function fimNivel(venceu){\n  var lv=jogo.lv;\n', 'function fimNivel(venceu){\n  var lv=jogo.lv;\n  var metaAntes=metaOk();\n', 'fim meta')
    h = sub1(h, """'<h2 style="margin-top:8px">'+(venceu?"Nível concluído":"Vidas acabaram")+'</h2>'+""",
             """'<h2 style="margin-top:8px">'+(venceu?"Nível concluído":"Vidas acabaram")+'</h2>'+\n      (!metaAntes&&metaOk()?'<div class="metabox">🎯 Meta da aula concluída! Agora escolha: bônus ou Chefão.</div>':'')+""", 'aviso meta')
    # contagens fixas antigas (SO)
    h = h.replace("feitos/9*100", "feitos/LEVELS.length*100").replace("' de 9 níveis concluídos · '", "' de '+LEVELS.length+' níveis concluídos · '")
    h = h.replace("' de 27 estrelas</p>'", "' de '+(LEVELS.length*3)+' estrelas</p>'").replace('concluidos()+" de 9"', 'concluidos()+" de "+LEVELS.length')
    h = h.replace("concluidos()+' de 9 níveis · '", "concluidos()+' de '+LEVELS.length+' níveis · '")
    return h



# ---------------------------------------------------------------- TEMA, TOPO E RODAPE
# Padrao (2026-10): cada disciplina tem a sua cor; todas as telas tem rodape com nome e ano;
# durante o nivel, o topo mostra nome, turma e nivel atual, alem da barra de progresso e das vidas.
AUTOR = 'Rosival Silva'
ANO = '2026'
CORES = {  # chave = pasta da aula. Cores = as dos HTML das aulas do projeto "Curso Tecnico em Informatica"
    'POO': dict(nome='P.O.O / Java', pri='#0b6b3a', d='#07502a', l='#e6f4ec', bg='#e9f1ec', s2='#f3f8f5', line='#c4d8cb',
                b1='#157a47', b2='#0b3d24', b3='#06200f', bfg='#a8e6c1', tok='#4cc07f', tokbg='rgba(76,192,127,.25)',
                D=dict(bg='#0a1a12', s='#112619', s2='#0d1f15', ink='#e6f4ec', ink2='#9cbba9', line='#234634', pri='#1f8f55', d='#146b3f', l='#123022')),
    'PWI': dict(nome='Programação Web', pri='#5b3a8c', d='#432a6a', l='#ece6f5', bg='#eeeaf4', s2='#f6f3fa', line='#d4cbe3',
                b1='#6a45a3', b2='#2f1d4e', b3='#170e29', bfg='#d3c0f5', tok='#a98af0', tokbg='rgba(169,138,240,.25)',
                D=dict(bg='#150f20', s='#1e1630', s2='#19122a', ink='#eee8fa', ink2='#b4a6d0', line='#3a2c5e', pri='#8761c9', d='#6a45a3', l='#2a1d4d')),
    'SO':  dict(nome='Sistemas Operacionais', pri='#9f1d1d', d='#761414', l='#fbe9e7', bg='#f4e9e7', s2='#faf3f2', line='#e3c8c4',
                b1='#a42525', b2='#4d0f0f', b3='#250707', bfg='#ffb3a8', tok='#f07a6e', tokbg='rgba(240,122,110,.25)',
                # no tema vermelho o "errou" vira laranja (regra do projeto), para nao confundir com a cor da disciplina
                bad=dict(bad='#c77700', d='#945700', l='#fff1dc', D_bad='#f0a030', D_d='#c77f10', D_l='#3a2610'),
                D=dict(bg='#1c0e0e', s='#2a1515', s2='#221111', ink='#f8eceb', ink2='#cfaeaa', line='#4d2a2a', pri='#c23b3b', d='#9a2a2a', l='#3d1818')),
    'LP':  dict(nome='Lógica de Programação', pri='#274a9c', d='#1c3777', l='#e3e9f7', bg='#e8ecf6', s2='#f2f5fb', line='#c5cfe8',
                b1='#2f56b3', b2='#14285a', b3='#0a1330', bfg='#b5c8f5', tok='#6f93e8', tokbg='rgba(111,147,232,.25)',
                D=dict(bg='#0b1226', s='#121c38', s2='#0e1730', ink='#e8eef9', ink2='#a3b2d3', line='#25355e', pri='#4a72d6', d='#3558ad', l='#14264f')),
}
ALIAS_DISC = {'LOGICA': 'LP', 'LÓGICA': 'LP', 'PROGWEB': 'PWI'}

TEMA_INI = '/* TEMA-INI */'
TEMA_FIM = '/* TEMA-FIM */'

TOPO_CSS = """
.topbar.col{flex-direction:column;align-items:stretch;gap:8px}
.topbar .trow{display:flex;align-items:center;gap:10px}
.topbar .info{display:flex;flex-direction:column;line-height:1.25;min-width:0}
.topbar .info b{font-size:14.5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.topbar .info span{font-size:12.5px;color:var(--ink-2);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.rodape{max-width:560px;margin:8px auto 0;padding:14px 14px calc(22px + env(safe-area-inset-bottom,0px));
  text-align:center;font-size:13px;color:var(--ink-2);border-top:1px solid var(--line)}
"""

INFO_JS = """function topoJogo(extra){return '<div class="topbar col">'+extra+'</div>';}
function infoJogador(lv){
  var i=LEVELS.indexOf(lv);
  var quem=(S.nome||"Aluno")+(S.turma?" · "+S.turma:"");
  var tipo="Nível "+(i+1)+(lv.boss?" · Chefão":(typeof META!=="undefined"&&i>=META?" · Bônus":""));
  return '<b>'+esc(quem)+'</b><span>'+esc(tipo)+' — '+esc(lv.nome)+'</span>';
}
"""

TOPO_ANTIGO = """  var h=topo('<button class="iconbtn" id="sair">✕</button>'+
     '<div class="grow"><div class="bar"><i style="width:'+Math.min(100,prog)+'%"></i></div></div>'+
     (lv.timer?'<span class="pill timer" id="cron">'+lv.timer+'s</span>':'')+
     '<span class="pill hp">'+vidas+'</span>');
"""
TOPO_NOVO = """  var h=topoJogo('<div class="trow"><button class="iconbtn" id="sair">✕</button>'+
     '<div class="grow info">'+infoJogador(lv)+'</div>'+
     (lv.timer?'<span class="pill timer" id="cron">'+lv.timer+'s</span>':'')+
     '<span class="pill hp">'+vidas+'</span></div>'+
     '<div class="bar"><i style="width:'+Math.min(100,prog)+'%"></i></div>');
"""


def bloco_tema(disc):
    c = CORES[disc]
    D = c['D']
    bad_l = bad_d = ''
    if 'bad' in c:
        b = c['bad']
        bad_l = ';--bad:%s;--bad-d:%s;--bad-l:%s' % (b['bad'], b['d'], b['l'])
        bad_d = ';--bad:%s;--bad-d:%s;--bad-l:%s' % (b['D_bad'], b['D_d'], b['D_l'])
    return (TEMA_INI + '\n'
        ':root{--bg:%(bg)s;--surface-2:%(s2)s;--line:%(line)s;--primary:%(pri)s;--primary-d:%(d)s;--primary-l:%(l)s;\n'
        '  --boot1:%(b1)s;--boot2:%(b2)s;--boot3:%(b3)s;--bootfg:%(bfg)s;--tok:%(tok)s;--tokbg:%(tokbg)s;--hp:#c23b4d' % c + bad_l + '}\n' +
        '@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){\n'
        '  --bg:%(bg)s;--surface:%(s)s;--surface-2:%(s2)s;--ink:%(ink)s;--ink-2:%(ink2)s;--line:%(line)s;\n'
        '  --primary:%(pri)s;--primary-d:%(d)s;--primary-l:%(l)s;--hp:#f0697c' % D + bad_d + '}}\n' +
        TEMA_FIM)


def disciplina_da_pasta(caminho):
    """Descobre a disciplina pela pasta: POO/POO_Gam_Mod_05/index.html -> POO."""
    import os
    partes = os.path.normpath(caminho).split(os.sep)
    for parte in reversed(partes[:-1]):
        k = parte.upper()
        k = ALIAS_DISC.get(k, k)
        if k in CORES:
            return k
    return None


def tema(h, disc):
    """Aplica cor da disciplina, topo do jogador e rodape. Pode rodar de novo: so atualiza."""
    c = CORES[disc]
    # 1) cores fixas do tema azul-petroleo antigo viram variaveis
    h = h.replace('#1d4e63 0%,#0d2231 55%,#081520 100%', 'var(--boot1) 0%,var(--boot2) 55%,var(--boot3) 100%')
    h = h.replace('color:#8fd4e8', 'color:var(--bootfg)').replace('background:#8fd4e8', 'background:var(--bootfg)')
    h = h.replace('background:#061019', 'background:var(--boot3)').replace('background:#2a5f75', 'background:var(--tok)')
    h = h.replace('dotted #3aa8c4', 'dotted var(--tok)').replace('rgba(58,168,196,.22)', 'var(--tokbg)')
    h = h.replace('.pill.hp{color:var(--bad);border-color:var(--bad)}', '.pill.hp{color:var(--hp);border-color:var(--hp)}')
    h = h.replace('.bar > i{display:block;height:100%;background:var(--ok);', '.bar > i{display:block;height:100%;background:var(--primary);')
    h = h.replace('padding:10px 14px;background:var(--surface);border-bottom:2px solid var(--line);',
                  'padding:10px 14px;background:var(--surface);border-bottom:3px solid var(--primary);')
    # 2) bloco de tema (sempre o ultimo do CSS) + css do topo e do rodape
    if TEMA_INI in h:
        h = re.sub(re.escape(TEMA_INI) + r'.*?' + re.escape(TEMA_FIM), lambda m: bloco_tema(disc), h, count=1, flags=re.S)
    else:
        h = sub1(h, '</style>', TOPO_CSS + bloco_tema(disc) + '\n</style>', 'css tema')
    # 3) cor da barra do navegador no celular
    h = re.sub(r'<meta name="theme-color"[^>]*>\n?', '', h)
    h = sub1(h, '<title>', '<meta name="theme-color" content="%s">\n<title>' % c['pri'], 'theme-color')
    # 4) topo do jogo: nome, turma e nivel atual (+ progresso e vidas)
    if 'function infoJogador' not in h:
        h = sub1(h, 'function topo(extra){', INFO_JS + 'function topo(extra){', 'infoJogador')
        h = sub1(h, TOPO_ANTIGO, TOPO_NOVO, 'topo do nivel')
    # 5) rodape em todas as telas (fica fora do #app)
    h = re.sub(r'<footer class="rodape">.*?</footer>\n?', '', h, flags=re.S)
    h = sub1(h, '<div class="shell" id="app"></div>\n',
             '<div class="shell" id="app"></div>\n<footer class="rodape">%s · %s</footer>\n' % (AUTOR, ANO), 'rodape')
    # 6) imagem do relatorio (PNG que o aluno envia): cor da disciplina e "nome · ano" no rodape
    if 'function gerarPNG(' in h:
        h = re.sub(r'var COR_TEMA="[^"]*";\n', '', h)
        h = h.replace('x.fillStyle="#15697f"', 'x.fillStyle=COR_TEMA')
        h = sub1(h, 'function gerarPNG(', 'var COR_TEMA="%s";\nfunction gerarPNG(' % c['pri'], 'cor do relatorio')
        h = re.sub(r'x\.fillText\("[^"]*",W-70,y\+62\)', 'x.fillText("%s · %s",W-70,y+62)' % (AUTOR, ANO), h)
    return h


def confere(h, nome):
    """Avisa problemas comuns nos dados (nao altera nada)."""
    m = re.search(r'var LEVELS\s*=\s*(\[.*?\]);\n', h, re.S)
    if not m:
        return
    if '</script' in m.group(1):
        print('  AVISO', nome, ': escreva <\\/script> dentro de LEVELS')
    try:
        L = json.loads(m.group(1).replace('<\\/', '</'))
    except Exception:
        return
    for lv in L:
        for i, q in enumerate(lv['qs'], 1):
            onde = '%s nivel %s questao %d' % (nome, lv['id'], i)
            if q['t'] == 'slots' and len({b for a, b in q['pairs']}) != len(q['pairs']):
                print('  AVISO', onde, ': slots com respostas repetidas (o aluno pode travar)')
            if q['t'] == 'order' and len(set(q['items'])) != len(q['items']):
                print('  AVISO', onde, ': order com linhas repetidas')
            if q['t'] == 'type' and any(not re.sub(r'[^a-z0-9]', '', a.lower()) for a in q['ac']):
                print('  AVISO', onde, ': resposta digitada so com simbolos (nao da para corrigir)')
    regs = [l for l in L if not l.get('boss')]
    print('  %s: %d niveis (%d meta + %d bonus + %d chefao), %d questoes' % (
        nome, len(L), min(5, len(regs)), max(0, len(regs) - 5), len(L) - len(regs), sum(len(l['qs']) for l in L)))


# ---------------------------------------------------------------- MODO PROFESSOR (PROJETOR)
# Padrao (2026-11): na Area do professor, a senha libera as fases (uso com aluno) OU liga o modo professor
# (uso no projetor). O modo professor vale para todas as aulas do aparelho (fica no localStorage do site) e traz:
# ordem fixa (questoes na ordem do gabarito e alternativas sempre no mesmo lugar), botao "Ver resposta",
# opcao de tirar o cronometro e o gabarito completo da aula (com impressao).
PROF_CSS = """/* PROF-CSS */
.profbar{display:flex;align-items:center;justify-content:space-between;gap:10px;background:var(--gold-l);border:1.5px dashed var(--gold);border-radius:10px;padding:6px 10px;margin:0 0 10px;font-weight:700;font-size:14px}
.profbar .btn{width:auto;margin:0;padding:8px 12px}
.profbox{background:var(--gold-l);border:1.5px dashed var(--gold);border-radius:12px;padding:8px 12px;margin:0 0 12px;font-size:14.5px;font-weight:700}
.gabbox{background:var(--ok-l);border:2px solid var(--ok);border-radius:12px;padding:10px 12px;margin:10px 0;font-size:16px}
.gab-ok{outline:3px solid var(--ok);outline-offset:2px;border-radius:6px;background:var(--ok-l)}
g.gab-ok path,g.gab-ok rect,g.gab-ok polygon,g.gab-ok ellipse{stroke:var(--ok)!important;stroke-width:4px!important}
.gabq{break-inside:avoid;page-break-inside:avoid}
.gabn{display:inline-block;font-weight:800;color:var(--primary);margin-right:6px}
.gabresp{margin-top:8px;font-weight:700;color:var(--ok-d);background:var(--ok-l);border-radius:8px;padding:6px 10px}
.gabops{margin:8px 0 0 22px;padding:0}.gabops li{margin:2px 0}.gabops li.ok{font-weight:800;color:var(--ok-d)}
.gabnav{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}.gabnav .chip{min-width:44px}
.gablv h2{margin:18px 4px 8px}
.gabmont{display:flex;flex-direction:column;align-items:center;gap:2px;margin:6px 0}
.chkrow{display:flex;gap:10px;align-items:flex-start;margin:10px 0;font-size:15px;cursor:pointer}
.chkrow input{width:20px;height:20px;margin-top:2px;flex:none}
@media print{.topbar,.rodape,.noprint,.profbar{display:none!important}body{background:#fff}.card{border:1px solid #bbb}}
"""

PROF_JS = r'''/* PROF-INI: modo professor (projetor): ordem fixa, ver resposta, sem cronometro e gabarito */
var PROF_KEY="aulas_gamificadas_prof";
var PROF=(function(){try{return JSON.parse(localStorage.getItem(PROF_KEY))||{};}catch(e){return {};}})();
function salvaProf(){try{if(PROF.ok)localStorage.setItem(PROF_KEY,JSON.stringify(PROF));else localStorage.removeItem(PROF_KEY);}catch(e){}}
function profOk(){return !!PROF.ok;}
function modoFixo(){return profOk()&&!!PROF.fixo;}
function timerOn(lv){return !!lv.timer&&!(profOk()&&PROF.semTimer);}
var SEMENTE=null;
function sementeDe(lvid,q){return (h53(String(lvid)+"|"+q.p)%4294967296)>>>0;}
function semear(q){SEMENTE=modoFixo()?sementeDe(jogo.lv.id,q):null;}
function sorteio(){
  if(SEMENTE===null)return Math.random();
  SEMENTE=(SEMENTE+0x6D2B79F5)>>>0;var t=SEMENTE;
  t=Math.imul(t^(t>>>15),t|1);t^=t+Math.imul(t^(t>>>7),t|61);
  return ((t^(t>>>14))>>>0)/4294967296;
}
function filaNivel(lv){lv.qs.forEach(function(q,i){q._n=i+1;});return modoFixo()?lv.qs.slice():shuffle(lv.qs);}
function ordemOps(lvid,q){var s=SEMENTE;SEMENTE=sementeDe(lvid,q);var o=shuffleIdx(q);SEMENTE=s;return o;}
var LETRAS="abcdefghij";
var NOMEFIG={inicio:"Início",fim:"Fim",entrada:"Entrada",saida:"Saída",proc:"Processamento",decisao:"Decisão"};
var ZONAS={icons:"Ícones de atalho",taskbar:"Barra de tarefas",start:"Botão Iniciar",apps:"Programas abertos (meio da barra)",
  tray:"Bandeja do sistema (relógio e WiFi)",wallpaper:"Área livre do papel de parede",bottom:"Borda de baixo da tela",
  escola:"Pasta Escola",c:"Disco local (C:)",titulo:"Barra de título",fechar:"Botão fechar (X)",endereco:"Barra de endereço",
  conteudo:"Área de conteúdo",status:"Barra de status"};
function zonasCodigo(rows){var m={};(rows||[]).forEach(function(l){var s=Array.isArray(l)?l[1]:l,re=/\[\[([^|]+)\|([^\]]+)\]\]/g,x;while((x=re.exec(s)))m[x[1]]=x[2];});return m;}
function noFluxo(fx,id){var n=null;((fx&&fx.n)||[]).forEach(function(d){if(d.i===id)n=d;});return n;}
function txtFig(d){var t=String(d.t||"").replace(/\n/g," ");return (NOMEFIG[d.k]||d.k)+(t&&d.k!=="inicio"&&d.k!=="fim"?" “"+t+"”":"");}
function gabResp(q,lvid){
  var t=q.t;
  if(t==="pick"){var o=ordemOps(lvid,q);return LETRAS[o.indexOf(q.ok)]+") "+q.opts[q.ok];}
  if(t==="multi"){var o2=ordemOps(lvid,q);return q.ok.map(function(i){return LETRAS[o2.indexOf(i)]+") "+q.opts[i];}).join(" · ");}
  if(t==="type")return q.ac[0];
  if(t==="order")return q.items.map(function(s,i){return (i+1)+") "+s;}).join("   ");
  if(t==="slots")return q.pairs.map(function(p){return p[0]+" → "+p[1];}).join(" · ");
  if(t==="keys")return (q.combo||[]).join(" + ");
  if(t==="figura")return NOMEFIG[q.opts[q.ok]]||q.opts[q.ok];
  if(t==="montar")return q.items.map(function(it){return txtFig({k:it[0],t:it[1]});}).join(" → ");
  if(t==="hot"){
    if(q.rows){var z=zonasCodigo(q.rows);return q.ok.map(function(k){return z[k]||k;}).join(" · ");}
    if(q.ok.indexOf("taskbar")>=0)return "Barra de tarefas (qualquer parte dela)";
    return q.ok.map(function(k){return ZONAS[k]||k;}).join(" · ");
  }
  if(t==="hotf")return q.ok.map(function(k){var d=noFluxo(q.fluxo,k);return d?txtFig(d):k;}).join(" · ");
  if(t==="esq")return (q.holes||[]).map(function(k){var d=noFluxo(q.fx,k);return d?txtFig(d):k;}).join(" · ");
  if(t==="compl")return (q.resp||[]).map(function(r,i){return "lacuna "+(i+1)+": "+r;}).join(" · ");
  if(t==="qflux")return "o desenho abaixo";
  if(t==="exec")return "siga o fluxograma com "+Object.keys(q.entradas||{}).map(function(k){return k+" = "+q.entradas[k];}).join(", ");
  if(t==="missao")return "o valor de teste muda com o nome do aluno; veja o modelo";
  if(q.ac)return q.ac[0];
  return "veja a explicação";
}
function gabVisual(q,live,lvid){
  var h="",F=typeof sFluxo==="function",M=typeof miniForma==="function";
  if(!live){
    if(q.rows&&q.t!=="qflux")h+=sCode(q.rows);
    if(q.scene&&typeof SCENES!=="undefined"&&SCENES[q.scene])h+=SCENES[q.scene]();
    if(F&&q.fluxo)h+=sFluxo(q.fluxo,{zonas:true,max:340});
    if(M&&q.k)h+='<div style="text-align:center">'+miniForma(q.k,q.txt||"",160)+'</div>';
    if(q.t==="pick"||q.t==="multi"){
      var ok=q.t==="pick"?[q.ok]:q.ok;
      h+='<ol type="a" class="gabops">'+ordemOps(lvid,q).map(function(i){return '<li'+(ok.indexOf(i)>=0?' class="ok"':'')+'>'+esc(q.opts[i])+(ok.indexOf(i)>=0?' ✔':'')+'</li>';}).join("")+'</ol>';
    }
  }
  if(q.t==="qflux"){if(!live&&q.rows)h+=sCode(q.rows);if(F)h+=sFluxo(q.flows[q.ok],{max:340});}
  if(F&&q.fx&&(q.t==="esq"||!live))h+=sFluxo(q.fx,{max:340});
  if(q.t==="compl"&&q.code)h+=sCode(q.code.map(function(l){return l.replace(/\{(\d+)\}/g,function(m,i){return q.resp[+i];});}));
  if(q.t==="missao"&&q.modelo&&!live)h+=sCode(q.modelo);
  if(M&&q.t==="figura")h+='<div style="text-align:center">'+miniForma(q.opts[q.ok],q.txt||"",160)+'</div>';
  if(M&&q.t==="montar")h+='<div class="gabmont">'+q.items.map(function(it){return miniForma(it[0],it[1],150);}).join('<span class="dn">↓</span>')+'</div>';
  return h;
}
function marcaZonas(box,q){
  if((q.t!=="hot"&&q.t!=="hotf")||!q.ok)return;
  Array.prototype.forEach.call(box.querySelectorAll("[data-zone]"),function(z){if(q.ok.indexOf(z.getAttribute("data-zone"))>=0)z.classList.add("gab-ok");});
}
function barraProf(q){
  if(!profOk())return "";
  return '<div class="profbar"><span>📽 Q'+(q._n||"?")+' de '+jogo.lv.qs.length+(modoFixo()?'':' · ordem embaralhada')+'</span>'+
    (PROF.ver?'<button class="btn ghost small" id="verResp" type="button">👁 Ver resposta</button>':'')+'</div>';
}
function ligaProf(q,area){
  if(!profOk())return;
  if(modoFixo()&&q.t==="pick")Array.prototype.forEach.call(area.querySelectorAll(".opt .mark"),function(m,i){m.textContent=LETRAS[i];});
  var b=$("#verResp");if(!b)return;
  b.onclick=function(){
    if(b._ab)return;b._ab=true;b.disabled=true;
    marcaZonas(app,q);
    var box=el('<div class="gabbox"><b>✔ Resposta:</b> '+esc(gabResp(q,jogo.lv.id))+gabVisual(q,true,jogo.lv.id)+
      (q.e?'<p class="sub" style="margin:6px 0 0">'+esc(q.e)+'</p>':'')+'</div>');
    var ac=$("#acao");ac.parentNode.insertBefore(box,ac);
  };
}
function telaGabarito(){
  jogo=null;if(cron){clearInterval(cron);cron=null;}
  var h=topo('<button class="iconbtn" id="volta">←</button><div class="grow"><b style="font-size:15px">Gabarito do professor</b></div>'+
     '<button class="iconbtn" id="imp" title="Imprimir ou salvar em PDF">🖨</button>');
  var G=(typeof GAME!=="undefined"&&GAME)||{};
  h+='<div class="card"><h2 style="margin:0">📄 '+esc(G.titulo?(G.eyebrow?G.eyebrow+" · ":"")+G.titulo:document.title)+'</h2>'+
     '<p class="sub">Gabarito do professor. A ordem é a do jogo com a <b>ordem fixa</b> ligada: Q1, Q2... e as alternativas a), b), c)... na mesma posição da tela.</p>'+
     '<div class="gabnav noprint">'+LEVELS.map(function(lv,i){return '<button class="chip" data-ir="'+i+'">Nível '+(i+1)+(lv.boss?' 🏆':'')+'</button>';}).join("")+'</div></div>';
  LEVELS.forEach(function(lv,i){
    h+='<div class="gablv" id="gab'+i+'"><h2>'+(lv.glyph||"")+' Nível '+(i+1)+(lv.boss?' · Chefão':(i>=META?' · Bônus':''))+' — '+esc(lv.nome)+'</h2>'+
       (lv.timer?'<p class="sub" style="margin:0 4px 8px">⏱ No jogo dos alunos: '+lv.timer+' s por questão.</p>':'');
    lv.qs.forEach(function(q,j){
      h+='<div class="card gabq" data-l="'+i+'" data-q="'+j+'"><span class="gabn">Q'+(j+1)+'</span><b>'+esc(q.p)+'</b>'+gabVisual(q,false,lv.id)+
         '<div class="gabresp">✔ '+esc(gabResp(q,lv.id))+'</div>'+(q.e?'<p class="sub" style="margin:6px 0 0">'+esc(q.e)+'</p>':'')+'</div>';
    });
    h+='</div>';
  });
  h+='<button class="btn noprint" id="volta2">Voltar para a Área do professor</button>';
  app.innerHTML=h;
  Array.prototype.forEach.call(app.querySelectorAll(".gabq"),function(c){marcaZonas(c,LEVELS[+c.getAttribute("data-l")].qs[+c.getAttribute("data-q")]);});
  Array.prototype.forEach.call(app.querySelectorAll("[data-ir]"),function(b){b.onclick=function(){var a=document.getElementById("gab"+b.getAttribute("data-ir"));if(a)a.scrollIntoView({behavior:"smooth"});};});
  $("#volta").onclick=$("#volta2").onclick=telaConfig;
  $("#imp").onclick=function(){window.print();};
  window.scrollTo(0,0);
}
/* PROF-FIM */
'''

CFG_PROF = r'''/* --- area do professor (senha) --- */
function h53(str){var h1=0xdeadbeef,h2=0x41c6ce57;for(var i=0,ch;i<str.length;i++){ch=str.charCodeAt(i);h1=Math.imul(h1^ch,2654435761);h2=Math.imul(h2^ch,1597334677);}h1=Math.imul(h1^(h1>>>16),2246822507);h1^=Math.imul(h2^(h2>>>13),3266489909);h2=Math.imul(h2^(h2>>>16),2246822507);h2^=Math.imul(h1^(h1>>>13),3266489909);return 4294967296*(2097151&h2)+(h1>>>0);}
var SENHA_PROF="__HASH__";
/* PROF-CFG */
function chkProf(k,t){return '<label class="chkrow"><input type="checkbox" data-prof="'+k+'"'+(PROF[k]?' checked':'')+'><span>'+t+'</span></label>';}
function telaConfig(){
  jogo=null;if(cron){clearInterval(cron);cron=null;}
  var h=topo('<button class="iconbtn" id="volta">←</button><div class="grow"><b style="font-size:15px">Área do professor</b></div>');
  if(!profOk()){
    h+='<div class="card"><h3>🔒 Senha do professor</h3>'+
       '<div class="pwrow"><input type="password" id="pw" autocomplete="off" placeholder="Senha do professor"></div>'+
       '<div class="pwerr" id="pwerr"></div>'+
       (!S.liberarTudo?'<button class="btn" id="lib">🔓 Liberar todas as fases</button>'+
         '<p class="sub" style="margin:-4px 0 12px">Para um aluno que precisa pular fases. As respostas continuam escondidas.</p>':'')+
       '<button class="btn ghost" id="ativa">📽 Ligar o modo professor (projetor)</button>'+
       '<p class="sub" style="margin:-4px 0 0">Ordem fixa, botão de ver a resposta, sem cronômetro e gabarito. Use só no seu computador ou no do projetor, nunca no de aluno.</p></div>';
  }
  if(S.liberarTudo){
    h+='<div class="card"><h3>🔓 Todas as fases liberadas</h3>'+
       '<p class="sub">Neste aparelho, todos os níveis desta trilha (inclusive o desafio final) estão abertos.</p>'+
       '<button class="btn ghost small" id="trancar">Bloquear de novo</button></div>';
  }
  if(profOk()){
    h+='<div class="card"><h3>📽 Modo professor ligado</h3>'+
       '<p class="sub">Vale para todas as aulas gamificadas neste aparelho, até você desligar. Todos os níveis ficam abertos.</p>'+
       chkProf("fixo","<b>Ordem fixa:</b> as questões vêm na ordem do gabarito (Q1, Q2...) e as alternativas não mudam de lugar.")+
       chkProf("ver","<b>Botão 👁 Ver resposta</b> em cada questão.")+
       chkProf("semTimer","<b>Sem cronômetro</b> nos níveis com tempo (como o Chefão).")+
       '<button class="btn" id="gab">📄 Abrir o gabarito desta aula</button>'+
       '<button class="btn ghost small" id="desliga">Desligar o modo professor</button></div>';
  }
  h+='<button class="btn ghost" id="volta2">Voltar para a trilha</button>';
  app.innerHTML=h;
  $("#volta").onclick=$("#volta2").onclick=telaMapa;
  if($("#trancar"))$("#trancar").onclick=function(){S.liberarTudo=false;save();telaConfig();};
  if(profOk()){
    Array.prototype.forEach.call(app.querySelectorAll("[data-prof]"),function(c){
      c.onchange=function(){PROF[c.getAttribute("data-prof")]=c.checked;salvaProf();};
    });
    $("#gab").onclick=telaGabarito;
    $("#desliga").onclick=function(){PROF={};salvaProf();telaConfig();};
  }
  var pw=$("#pw");
  if(pw){
    var confere=function(){
      if(String(h53(pw.value))===SENHA_PROF)return true;
      $("#pwerr").textContent="Senha incorreta.";pw.value="";pw.focus();return false;
    };
    if($("#lib"))$("#lib").onclick=function(){if(confere()){S.liberarTudo=true;save();telaMapa();}};
    $("#ativa").onclick=function(){if(confere()){PROF={ok:true,fixo:true,ver:true,semTimer:true};salvaProf();telaConfig();}};
    pw.addEventListener("keydown",function(e){if(e.key==="Enter"){var b=$("#lib")||$("#ativa");b.click();}});
    setTimeout(function(){pw.focus();},100);
  }
  window.scrollTo(0,0);
}
'''.replace('__HASH__', SENHA_HASH)


def professor(h):
    """Modo professor. Pode rodar de novo: so acrescenta o que falta."""
    if '/* PROF-CSS */' not in h:
        if TEMA_INI in h:
            h = sub1(h, TEMA_INI, PROF_CSS + TEMA_INI, 'css prof')
        else:
            h = sub1(h, '</style>', PROF_CSS + '</style>', 'css prof')
    if 'PROF-CFG' not in h:
        h, n = re.subn(r'/\* --- area do professor \(senha\) --- \*/\n.*?\nfunction telaConfig\(\)\{.*?\n\}\n',
                       lambda m: CFG_PROF, h, count=1, flags=re.S)
        assert n == 1, 'telaConfig'
    if 'PROF-INI' not in h:
        h = sub1(h, '/* --- area do professor (senha) --- */', PROF_JS + '/* --- area do professor (senha) --- */', 'prof js')
    if 'Math.floor(sorteio()*(i+1))' not in h:
        h = sub1(h, 'var j=Math.floor(Math.random()*(i+1));', 'var j=Math.floor(sorteio()*(i+1));', 'shuffle')
    if 'fila:filaNivel(lv)' not in h:
        h = sub1(h, 'fila:shuffle(lv.qs)', 'fila:filaNivel(lv)', 'fila')
    if '  semear(q);\n' not in h:
        h = sub1(h, '  var velho=document.querySelector(".feed");if(velho)velho.remove();\n',
                 '  var velho=document.querySelector(".feed");if(velho)velho.remove();\n  semear(q);\n', 'semear')
    h = h.replace("(lv.timer?'<span class=\"pill timer\"", "(timerOn(lv)?'<span class=\"pill timer\"")
    h = h.replace('  if(lv.timer){\n', '  if(timerOn(lv)){\n')
    assert "(timerOn(lv)?'<span" in h and '  if(timerOn(lv)){\n' in h, 'timer'
    if 'h+=barraProf(q);' not in h:
        h = sub1(h, "  h+='<h2 style=\"margin-bottom:12px\">'+esc(q.p)+'</h2>';\n",
                 "  h+=barraProf(q);\n  h+='<h2 style=\"margin-bottom:12px\">'+esc(q.p)+'</h2>';\n", 'barra prof')
    if 'ligaProf(q,area);' not in h:
        h = sub1(h, '  RENDER[q.t](q,area,acao);\n', '  RENDER[q.t](q,area,acao);\n  ligaProf(q,area);\n', 'liga prof')
    h = h.replace('if(i===0||S.liberarTudo)return true;', 'if(i===0||S.liberarTudo||profOk())return true;')
    assert 'S.liberarTudo||profOk())return true' in h, 'desbloqueado prof'
    if 'class="profbox"' not in h:
        h = sub1(h, """   '<div class="metabox">🎯 Meta da aula: <b>'""",
                 """   (profOk()?'<div class="profbox">📽 Modo professor ligado neste aparelho · ⚙️ para mudar ou abrir o gabarito</div>':'')+\n   '<div class="metabox">🎯 Meta da aula: <b>'""", 'aviso mapa')
    if 'kv("Modo professor"' not in h:
        h = sub1(h, '(S.liberarTudo?kv("Fases liberadas pelo professor","sim"):"")+',
                 '(S.liberarTudo?kv("Fases liberadas pelo professor","sim"):"")+(profOk()?kv("Modo professor","ligado neste aparelho"):"")+', 'kv prof')
    return h


if __name__ == '__main__':
    for a in sys.argv[1:]:
        s = open(a, encoding='utf-8').read().replace('\r\n', '\n')
        if 'function julgar(q,ok,msg)' not in s:
            print('pulado (motor diferente, ajuste a mao):', a)
            continue
        h = professor(meta(patch(s)))
        disc = disciplina_da_pasta(a)
        if disc:
            h = tema(h, disc)
        else:
            print('  AVISO', a, ': pasta fora de POO, PWI, SO ou LP; tema nao aplicado')
        open(a, 'w', encoding='utf-8', newline='\n').write(h)
        confere(h, a)
        print('ok', a)
