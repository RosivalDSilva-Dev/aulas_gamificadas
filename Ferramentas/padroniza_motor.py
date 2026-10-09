"""Uso: python Ferramentas/padroniza_motor.py POO/A06-tema/index.html

Padroniza o motor das aulas gamificadas (trilha com niveis/estrelas).
- trava de uma resposta por questao (clique duplo nao pula questao nem tira vida 2x)
- barra de progresso so avanca no acerto
- area do professor com senha para liberar todas as fases
- cor tema da disciplina (POO azul, PWI laranja, SO verde, LP roxo), pela pasta da aula
- topo do jogo com nome, turma e nivel atual (mantendo vidas e cronometro)
- rodape "Rosival Silva · ano" em todas as telas
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
CORES = {  # chave = pasta da aula
    'POO': dict(nome='P.O.O / Java', pri='#2563c4', d='#1a4a96', l='#dbe7fa', bg='#e6eef9', s2='#f2f6fc', line='#c3d3ea',
                b1='#2a5ca8', b2='#14305e', b3='#0b1a35', bfg='#a9c8f5', tok='#5b93e8', tokbg='rgba(91,147,232,.25)',
                D=dict(bg='#0b1526', s='#122038', s2='#0e1a2e', ink='#e8eef8', ink2='#a3b5d0', line='#25395a', pri='#3f7fdc', d='#2d62b3', l='#14294d')),
    'PWI': dict(nome='Programação Web', pri='#b85f00', d='#8a4500', l='#fcebd2', bg='#f6eee3', s2='#fbf6ef', line='#e3d3bd',
                b1='#9a5208', b2='#4d2a06', b3='#241303', bfg='#ffcb8a', tok='#f0a24a', tokbg='rgba(240,162,74,.25)',
                D=dict(bg='#1b130a', s='#281c10', s2='#21170d', ink='#f6ede2', ink2='#c8b49b', line='#4a3720', pri='#c9731a', d='#a05a10', l='#3b2711')),
    'SO':  dict(nome='Sistemas Operacionais', pri='#1b7a45', d='#12582f', l='#d6efe0', bg='#e5f1e9', s2='#f1f8f3', line='#bfd9c8',
                b1='#1f6b44', b2='#0f3724', b3='#08190f', bfg='#9be3b9', tok='#4cc07f', tokbg='rgba(76,192,127,.25)',
                D=dict(bg='#0a1a12', s='#112619', s2='#0d1f15', ink='#e6f4ec', ink2='#9cbba9', line='#234634', pri='#2f9e60', d='#1f7745', l='#123022')),
    'LP':  dict(nome='Lógica de Programação', pri='#6d3fc0', d='#4e2a92', l='#e9e0f8', bg='#eee9f7', s2='#f6f3fb', line='#d3c8e8',
                b1='#5a3a9e', b2='#2c1a54', b3='#150c2b', bfg='#cdb8f5', tok='#a98af0', tokbg='rgba(169,138,240,.25)',
                D=dict(bg='#130d22', s='#1c1432', s2='#170f2a', ink='#eee8fa', ink2='#b4a6d0', line='#3a2c5e', pri='#8b5fe0', d='#6a42b8', l='#2a1d4d')),
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
    return (TEMA_INI + '\n'
        ':root{--bg:%(bg)s;--surface-2:%(s2)s;--line:%(line)s;--primary:%(pri)s;--primary-d:%(d)s;--primary-l:%(l)s;\n'
        '  --boot1:%(b1)s;--boot2:%(b2)s;--boot3:%(b3)s;--bootfg:%(bfg)s;--tok:%(tok)s;--tokbg:%(tokbg)s}\n' % c +
        '@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){\n'
        '  --bg:%(bg)s;--surface:%(s)s;--surface-2:%(s2)s;--ink:%(ink)s;--ink-2:%(ink2)s;--line:%(line)s;\n'
        '  --primary:%(pri)s;--primary-d:%(d)s;--primary-l:%(l)s}}\n' % D +
        TEMA_FIM)


def disciplina_da_pasta(caminho):
    """Descobre a disciplina pela pasta: POO/A05-xxx/index.html -> POO."""
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


if __name__ == '__main__':
    for a in sys.argv[1:]:
        s = open(a, encoding='utf-8').read().replace('\r\n', '\n')
        if 'function julgar(q,ok,msg)' not in s:
            print('pulado (motor diferente, ajuste a mao):', a)
            continue
        h = meta(patch(s))
        disc = disciplina_da_pasta(a)
        if disc:
            h = tema(h, disc)
        else:
            print('  AVISO', a, ': pasta fora de POO, PWI, SO ou LP; tema nao aplicado')
        open(a, 'w', encoding='utf-8', newline='\n').write(h)
        confere(h, a)
        print('ok', a)
