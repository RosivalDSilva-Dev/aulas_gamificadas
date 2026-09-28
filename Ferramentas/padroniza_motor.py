"""Uso: python Ferramentas/padroniza_motor.py POO/A06-tema/index.html

Padroniza o motor das aulas gamificadas (trilha com niveis/estrelas).
- trava de uma resposta por questao (clique duplo nao pula questao nem tira vida 2x)
- barra de progresso so avanca no acerto
- area do professor com senha para liberar todas as fases
"""
import sys, re

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


if __name__ == '__main__':
    for a in sys.argv[1:]:
        s = open(a, encoding='utf-8').read().replace('\r\n', '\n')
        open(a, 'w', encoding='utf-8', newline='\n').write(patch(s))
        print('ok', a)
