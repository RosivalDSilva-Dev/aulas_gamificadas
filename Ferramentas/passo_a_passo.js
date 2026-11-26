/* PASSO-INI: passo a passo dos lacos (codigo + fluxograma + memoria + teste de mesa + tela), para o modo professor.
   Le o codigo da questao (q.rows: Portugol, Java ou JavaScript), executa de verdade e monta os passos.
   Se o codigo nao puder ser executado (lacunas, leia, faca-enquanto, erro de proposito), a questao fica sem o botao. */
var PASSO=(function(){
  var TIPOS={inteiro:1,real:1,cadeia:1,logico:1,caracter:1,"int":1,"double":1,"float":1,"long":1,"String":1,"boolean":1,"char":1,"let":1,"var":1,"const":1};
  var SAIDA={"escreva":"pt","System.out.println":"ln","System.out.print":"pr","console.log":"ln"};
  function semZona(s){return String(s).replace(/\[\[[^|\]]*\|([^\]]*)\]\]/g,"$1");}
  function linhas(rows){return (rows||[]).map(function(l){return semZona(Array.isArray(l)?l[1]:l);});}

  /* ---------------- lexico ---------------- */
  function lexar(ls){
    var tk=[],re=/\s+|("(?:[^"\\]|\\.)*")|(\d+(?:\.\d+)?)|([A-Za-z_À-ÿ][\wÀ-ÿ]*(?:\.[A-Za-z_]\w*)*)|(\+\+|--|\+=|-=|\*=|<=|>=|==|!=|&&|\|\||[-+*\/%<>=!(){};,])/g;
    ls.forEach(function(s,ln){
      var m;re.lastIndex=0;
      while(re.lastIndex<s.length){
        var at=re.lastIndex;m=re.exec(s);
        if(!m||m.index!==at)throw "lex";
        if(m[1])tk.push({k:"str",v:JSON.parse(m[1]),ln:ln,a:at,b:re.lastIndex});
        else if(m[2])tk.push({k:"num",v:Number(m[2]),ln:ln,a:at,b:re.lastIndex});
        else if(m[3])tk.push({k:"id",v:m[3],ln:ln,a:at,b:re.lastIndex});
        else if(m[4])tk.push({k:"op",v:m[4],ln:ln,a:at,b:re.lastIndex});
      }
    });
    return tk;
  }

  /* ---------------- sintatico ---------------- */
  function compilar(ls){
    var tk=lexar(ls),p=0,uid=0;
    function ve(v){return tk[p]&&tk[p].v===v&&tk[p].k!=="str";}
    function pega(v){if(!ve(v))throw "esperava "+v;return tk[p++];}
    function opc(v){if(ve(v)){p++;return true;}return false;}
    function txt(a,b){var t1=tk[a],t2=tk[b-1];if(t1.ln!==t2.ln)throw "multi";return ls[t1.ln].slice(t1.a,t2.b);}
    // expressoes
    var NIV=[["||","ou"],["&&","e"],["==","!="],["<","<=",">",">="],["+","-"],["*","/","%"]];
    function expr(n){
      n=n||0;
      if(n===NIV.length)return unario();
      var e=expr(n+1);
      while(tk[p]&&(tk[p].k==="op"||tk[p].k==="id")&&NIV[n].indexOf(tk[p].v)>=0){var o=tk[p++].v;e={k:"bin",o:o,a:e,b:expr(n+1)};}
      return e;
    }
    function unario(){
      if(ve("-")){p++;return {k:"neg",a:unario()};}
      if(ve("!")||ve("nao")){p++;return {k:"nao",a:unario()};}
      var t=tk[p++];if(!t)throw "fim";
      if(t.k==="num")return {k:"num",v:t.v};
      if(t.k==="str")return {k:"str",v:t.v};
      if(t.k==="id"){if(t.v==="verdadeiro"||t.v==="true")return {k:"num",v:true};if(t.v==="falso"||t.v==="false")return {k:"num",v:false};return {k:"var",n:t.v};}
      if(t.v==="("){var e=expr();pega(")");return {k:"par",a:e};}
      throw "expr";
    }
    function exprTxt(){var a=p,e=expr();e.t=txt(a,p);e.ln=tk[a].ln;e.ca=tk[a].a;e.cb=tk[p-1].b;return e;}
    // atribuicao simples (sem ;)
    function atrib(){
      var a=p,decl=false;
      if(tk[p]&&tk[p].k==="id"&&TIPOS[tk[p].v]){p++;decl=true;}
      var nm=tk[p++];if(!nm||nm.k!=="id")throw "nome";
      var s={k:"atr",n:nm.v,ln:nm.ln,id:"n"+(uid++),decl:decl};
      if(opc("++")){s.op="++";}
      else if(opc("--")){s.op="--";}
      else if(ve("=")||ve("+=")||ve("-=")||ve("*=")){s.op=tk[p++].v;s.e=exprTxt();}
      else if(decl){s.op="decl";}
      else throw "atrib";
      s.t=txt(a,p);s.ca=tk[a].a;s.cb=tk[p-1].b;
      return s;
    }
    function bloco(){pega("{");var b=[];while(!ve("}")){if(p>=tk.length)throw "}";var s=cmd();if(s)b.push(s);}pega("}");return b;}
    function corpo(){if(opc(";"))return [];return bloco();}
    function cmd(){
      var t=tk[p];
      if(t.v==="para"||t.v==="for"){
        p++;pega("(");var ini=atrib();pega(";");var c=exprTxt();pega(";");var pas=atrib();pega(")");
        return {k:"for",ini:ini,c:c,pas:pas,b:corpo(),ln:t.ln,id:"n"+(uid++),pt:t.v==="para"};
      }
      if(t.v==="enquanto"||t.v==="while"){
        p++;pega("(");var c2=exprTxt();pega(")");
        return {k:"while",c:c2,b:corpo(),ln:t.ln,id:"n"+(uid++),pt:t.v==="enquanto"};
      }
      if(t.v==="faca"||t.v==="do"){
        p++;var bd=bloco();var tw=tk[p];if(!(ve("enquanto")||ve("while")))throw "do";p++;pega("(");var c4=exprTxt();pega(")");opc(";");
        return {k:"do",c:c4,b:bd,ln:tw.ln,lnIni:t.ln,id:"n"+(uid++),pt:t.v==="faca"};
      }
      if(t.v==="se"||t.v==="if"){
        p++;pega("(");var c3=exprTxt();pega(")");var th=bloco(),el=null,eln=null;
        if(ve("senao")||ve("else")){eln=tk[p].ln;p++;if(ve("se")||ve("if"))el=[cmd()];else el=bloco();}
        return {k:"if",c:c3,th:th,el:el,ln:t.ln,eln:eln,id:"n"+(uid++),pt:t.v==="se"};
      }
      if(t.k==="id"&&SAIDA[t.v]){
        p++;pega("(");var args=[],a0=p;
        if(!ve(")")){args.push(exprTxt());while(opc(","))args.push(exprTxt());}
        var at=ve(")")&&p>a0?txt(a0,p):"";pega(")");opc(";");
        return {k:"out",f:SAIDA[t.v],args:args,t:at,ln:t.ln,id:"n"+(uid++)};
      }
      if(t.v==="{")return {k:"blk",b:bloco()};
      if(t.v===";"){p++;return null;}
      if(t.k==="id"){var s=atrib();opc(";");return s;}
      throw "cmd "+t.v;
    }
    var prog=[];while(p<tk.length){var s=cmd();if(s)prog.push(s);}
    return prog;
  }

  /* ---------------- execucao ---------------- */
  function temLaco(prog){var r=false;(function v(b){b.forEach(function(s){if(s.k==="for"||s.k==="while"||s.k==="do")r=true;if(s.b)v(s.b);if(s.th)v(s.th);if(s.el)v(s.el);});})(prog);return r;}
  function primeiroLaco(prog){var r=null;(function v(b){b.forEach(function(s){if(r)return;if(s.k==="for"||s.k==="while"||s.k==="do")r=s;else{if(s.b)v(s.b);if(s.th)v(s.th);if(s.el)v(s.el);}});})(prog);return r;}
  function ehInt(v){return typeof v==="number"&&Math.floor(v)===v;}
  function fmt(v){if(typeof v==="boolean")return v?"verdadeiro":"falso";return String(v);}
  function aval(e,M,js){
    switch(e.k){
      case "num":case "str":return e.v;
      case "par":return aval(e.a,M,js);
      case "var":if(!(e.n in M))throw "var "+e.n;return M[e.n];
      case "neg":return -aval(e.a,M,js);
      case "nao":return !aval(e.a,M,js);
      case "bin":
        var a=aval(e.a,M,js),b=aval(e.b,M,js);
        switch(e.o){
          case "+":return (typeof a==="string"||typeof b==="string")?fmt(a)+fmt(b):a+b;
          case "-":return a-b;case "*":return a*b;
          case "/":if(b===0)throw "div0";return (!js&&ehInt(a)&&ehInt(b))?Math.trunc(a/b):a/b;
          case "%":return a%b;
          case "<":return a<b;case "<=":return a<=b;case ">":return a>b;case ">=":return a>=b;
          case "==":return a===b;case "!=":return a!==b;
          case "&&":case "e":return a&&b;case "||":case "ou":return a||b;
        }
    }
    throw "aval";
  }
  // a expressao com os valores no lugar das variaveis (para a narracao)
  function subst(e,M){
    switch(e.k){
      case "num":return fmt(e.v);case "str":return '"'+e.v+'"';
      case "var":return e.n in M?(typeof M[e.n]==="string"?'"'+M[e.n]+'"':fmt(M[e.n])):e.n;
      case "par":return "("+subst(e.a,M)+")";
      case "neg":return "-"+subst(e.a,M);
      case "nao":return "não "+subst(e.a,M);
      case "bin":return subst(e.a,M)+" "+e.o+" "+subst(e.b,M);
    }
    return "?";
  }
  function soNum(e){return e.k==="num"||e.k==="str"||(e.k==="neg"&&e.a.k==="num");}
  function H(s){return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");}
  function C(s){return "<code>"+H(s)+"</code>";}

  /* ---------------- fluxograma (padrao Mapler) ---------------- */
  var CH=9.2,GAP=30;
  function tam(k,t){
    var w=Math.max(String(t).length*CH,20);
    if(k==="dec")return {w:Math.max(150,w+76),h:72};
    if(k==="sai")return {w:Math.max(110,w+56),h:44};
    if(k==="pil")return {w:110,h:38};
    return {w:Math.max(104,w+32),h:44};
  }
  function txAtr(s){
    if(s.op==="++")return s.n+" = "+s.n+" + 1";
    if(s.op==="--")return s.n+" = "+s.n+" - 1";
    if(s.op==="+=")return s.n+" = "+s.n+" + "+s.e.t;
    if(s.op==="-=")return s.n+" = "+s.n+" - "+s.e.t;
    if(s.op==="*=")return s.n+" = "+s.n+" * "+s.e.t;
    return s.n+" = "+s.e.t;
  }
  function montarFluxo(prog){
    var NOS=[],AR=[];
    function no(id,k,t,cx,y){var z=tam(k,t);var n={id:id,k:k,t:t,x:cx,y:y+z.h/2,w:z.w,h:z.h,top:y,bot:y+z.h};NOS.push(n);return n;}
    function liga(ex,alvo,e){ // ex: saida pendente {de,pts,lab}; e: ponto de entrada {x,y}
      var pts=ex.pts.slice(),u=pts[pts.length-1];
      if(u.x!==e.x){var my=e.y-14;if(u.y<my)pts.push({x:u.x,y:my});pts.push({x:e.x,y:Math.max(my,u.y)});}
      pts.push({x:e.x,y:e.y});
      AR.push({de:ex.de,pa:alvo,pts:pts,lab:ex.lab});
    }
    // devolve {l,r,bot,ent:{x,y},alvo,saidas:[]}; nada se o comando nao vira figura
    function seq(b,cx,y){
      var r=null;
      b.forEach(function(s){
        var x=item(s,cx,r?r.bot+GAP:y);if(!x)return;
        if(!r){r=x;return;}
        r.saidas.forEach(function(ex){liga(ex,x.alvo,x.ent);});
        r={l:Math.max(r.l,x.l),r:Math.max(r.r,x.r),bot:x.bot,ent:r.ent,alvo:r.alvo,saidas:x.saidas};
      });
      return r;
    }
    function simples(id,k,t,cx,y){var n=no(id,k,t,cx,y);return {l:n.w/2,r:n.w/2,bot:n.bot,ent:{x:cx,y:n.top},alvo:id,saidas:[{de:id,pts:[{x:cx,y:n.bot}]}]};}
    function laco(s,cond,corpoB,cx,y){
      var top=y+18,d=no(s.id,"dec",cond+"?",cx,top);
      var c=seq(corpoB,cx,d.bot+GAP);
      var L=Math.max(d.w/2,c?c.l:0)+24,R=Math.max(d.w/2,c?c.r:0)+34;
      var fim=c?c.bot:d.bot;
      if(c){
        AR.push({de:s.id,pa:c.alvo,pts:[{x:cx,y:d.bot},{x:c.ent.x,y:c.ent.y}],lab:"Sim"});
        c.saidas.forEach(function(ex){
          var pts=ex.pts.slice(),u=pts[pts.length-1];
          pts.push({x:u.x,y:fim+16},{x:cx-L,y:fim+16},{x:cx-L,y:y+6},{x:cx-4,y:y+6});
          AR.push({de:ex.de,pa:s.id,pts:pts,volta:true});
        });
      }else{
        AR.push({de:s.id,pa:s.id,pts:[{x:cx,y:d.bot},{x:cx,y:d.bot+14},{x:cx-L,y:d.bot+14},{x:cx-L,y:y+6},{x:cx-4,y:y+6}],lab:"Sim",volta:true});
        fim=d.bot+14;
      }
      return {l:L+6,r:R+6,bot:fim+20,ent:{x:cx,y:y},alvo:s.id,
        saidas:[{de:s.id,lab:"Não",pts:[{x:cx+d.w/2,y:d.y},{x:cx+R,y:d.y},{x:cx+R,y:fim+20}]}],dtop:top};
    }
    function item(s,cx,y){
      if(s.k==="atr"){if(s.op==="decl")return null;return simples(s.id,"proc",txAtr(s),cx,y);}
      if(s.k==="out")return simples(s.id,"sai",s.t||" ",cx,y);
      if(s.k==="blk")return seq(s.b,cx,y);
      if(s.k==="while"){var w=laco(s,s.c.t,s.b,cx,y);w.ent={x:cx,y:w.dtop};return w;}
      if(s.k==="do"){
        var c=seq(s.b,cx,y+18);if(!c)return null;
        var d=no(s.id,"dec",s.c.t+"?",cx,c.bot+GAP);
        c.saidas.forEach(function(ex){liga(ex,s.id,{x:cx,y:d.top});});
        var L=Math.max(d.w/2,c.l)+24;
        AR.push({de:s.id,pa:c.alvo,pts:[{x:cx-d.w/2,y:d.y},{x:cx-L,y:d.y},{x:cx-L,y:y+6},{x:cx-4,y:y+6}],lab:"Sim",volta:true});
        return {l:L+6,r:Math.max(d.w/2,c.r),bot:d.bot,ent:{x:cx,y:c.ent.y},alvo:c.alvo,saidas:[{de:s.id,lab:"Não",pts:[{x:cx,y:d.bot}]}]};
      }
      if(s.k==="for"){
        var i=simples(s.ini.id,"proc",txAtr(s.ini),cx,y);
        var w2=laco(s,s.c.t,s.b.concat([s.pas]),cx,i.bot+GAP-18);
        liga(i.saidas[0],s.id,{x:cx,y:w2.dtop});
        return {l:Math.max(i.l,w2.l),r:Math.max(i.r,w2.r),bot:w2.bot,ent:i.ent,alvo:i.alvo,saidas:w2.saidas};
      }
      if(s.k==="if"){
        var d=no(s.id,"dec",s.c.t+"?",cx,y);
        var probeT=s.th.length?seqMed(s.th):{l:0,r:0},probeE=s.el&&s.el.length?seqMed(s.el):{l:0,r:0};
        var tx=cx+Math.max(d.w/2+14,probeT.l+18),ex=cx-Math.max(d.w/2+14,probeE.r+18);
        var t=s.th.length?seq(s.th,tx,d.bot+22):null,e=s.el&&s.el.length?seq(s.el,ex,d.bot+22):null;
        var sd=[];
        if(t){AR.push({de:s.id,pa:t.alvo,pts:[{x:cx+d.w/2,y:d.y},{x:tx,y:d.y},{x:tx,y:t.ent.y}],lab:"Sim"});sd=sd.concat(t.saidas);}
        else sd.push({de:s.id,lab:"Sim",pts:[{x:cx+d.w/2,y:d.y},{x:tx,y:d.y}]});
        if(e){AR.push({de:s.id,pa:e.alvo,pts:[{x:cx-d.w/2,y:d.y},{x:ex,y:d.y},{x:ex,y:e.ent.y}],lab:"Não"});sd=sd.concat(e.saidas);}
        else sd.push({de:s.id,lab:"Não",pts:[{x:cx-d.w/2,y:d.y},{x:ex,y:d.y}]});
        var bot=Math.max(d.bot,t?t.bot:0,e?e.bot:0)+8;
        sd.forEach(function(q){var u=q.pts[q.pts.length-1];if(u.y<bot)q.pts.push({x:u.x,y:bot});});
        return {l:Math.max(d.w/2,cx-ex+(e?e.l:0)),r:Math.max(d.w/2,tx-cx+(t?t.r:0)),bot:bot,ent:{x:cx,y:d.top},alvo:s.id,saidas:sd};
      }
      return null;
    }
    // medida de uma sequencia sem desenhar (para posicionar as colunas do se)
    function seqMed(b){var n0=NOS.length,a0=AR.length,r=seq(b,0,0);NOS.length=n0;AR.length=a0;return r||{l:0,r:0};}
    var ini=simples("ini","pil","Início",0,0);
    var corpoR=seq(prog,0,ini.bot+GAP);
    ini.saidas.forEach(function(ex){liga(ex,corpoR.alvo,corpoR.ent);});
    var fy=corpoR.bot+GAP;
    var fim=no("fim","pil","Fim",0,fy);
    corpoR.saidas.forEach(function(ex){liga(ex,"fim",{x:0,y:fim.top});});
    // caixa de enquadramento
    var x0=1e9,x1=-1e9,y1=fim.bot;
    NOS.forEach(function(n){x0=Math.min(x0,n.x-n.w/2);x1=Math.max(x1,n.x+n.w/2);});
    AR.forEach(function(a){a.pts.forEach(function(q){x0=Math.min(x0,q.x);x1=Math.max(x1,q.x);});});
    return {nos:NOS,ar:AR,vb:(x0-26)+" -8 "+(x1-x0+70)+" "+(y1+20)};
  }

  /* ---------------- passos ---------------- */
  function simular(prog,js){
    var M={},out="",P=[],tab=[],cols=[],condCols=[],L1=primeiroLaco(prog),volta=0,linha=-1,fixas={},nv=0,laco1=0;
    var LIM_VOLTAS=12,LIM=260;
    function varsDe(e,a){a=a||[];if(e.k==="var"&&a.indexOf(e.n)<0)a.push(e.n);["a","b"].forEach(function(k){if(e[k])varsDe(e[k],a);});return a;}
    function col(n){if(cols.indexOf(n)<0)cols.push(n);}
    function cel(nome,v){if(linha<0||!tab[linha])return;if(fixas[nome])return;tab[linha].v[nome]=v;}
    function passo(o){
      if(P.length>LIM)throw "longo";
      o.M=JSON.parse(JSON.stringify(M));o.out=out;o.tab=JSON.parse(JSON.stringify(tab));o.linha=linha;o.mud=o.mud||[];
      P.push(o);
    }
    passo({no:"ini",ln:null,ic:"🚀",tx:"O programa começa no <b>Início</b>."});
    function atr(s,papel){
      var antes=s.n in M?M[s.n]:undefined,v,tx;
      if(s.op==="decl"){M[s.n]=undefined;return;}
      if(s.op==="++"||s.op==="--"){
        if(!(s.n in M))throw "var";
        v=s.op==="++"?antes+1:antes-1;
        tx=C(s.t)+(s.op==="++"?" soma 1":" tira 1")+" → "+H(fmt(antes))+(s.op==="++"?" + 1":" - 1")+" = <b>"+H(fmt(v))+"</b>.";
      }else{
        var val=aval(s.e,M,js);
        if(s.op==="+=")v=antes+val;else if(s.op==="-=")v=antes-val;else if(s.op==="*=")v=antes*val;else v=val;
        if(s.op==="="&&soNum(s.e))tx=(antes===undefined?"Cria a variável "+C(s.n)+" valendo ":C(s.n)+" passa a valer ")+"<b>"+H(fmt(v))+"</b>.";
        else{
          var conta=s.op==="="?subst(s.e,M):H(fmt(antes))+" "+s.op.charAt(0)+" "+subst(s.e,M);
          tx=C(s.t)+" → "+H(conta)+" = <b>"+H(fmt(v))+"</b>.";
        }
      }
      M[s.n]=v;col(s.n);cel(s.n,v);
      if(papel==="ini")tx="O "+(s.pt?"PARA":"for")+" começa com "+C(s.t)+". Essa parte roda <b>uma vez só</b>.";
      if(papel==="pas")tx="Fim da volta: "+tx;
      return tx;
    }
    function run(b){
      for(var i=0;i<b.length;i++){
        var s=b[i];
        if(s.k==="atr"){if(s.op==="decl"){M[s.n]=undefined;continue;}var t=atr(s);passo({no:s.id,ln:s.ln,seg:[s.ca,s.cb],mud:[s.n],ic:s.op==="="?"📦":"🔁",tx:t});}
        else if(s.k==="out"){
          var txo=s.args.map(function(a){return fmt(aval(a,M,js));}).join("");
          if(s.f==="ln")txo+="\n";
          var antes=out;out+=txo;
          if(linha>=0&&tab[linha])tab[linha].tela=(tab[linha].tela||"")+txo.replace(/\n/g," ");
          var mostra=txo.replace(/\n$/,"");
          passo({no:s.id,ln:s.ln,ic:"🖥️",novo:antes.length,tx:"Mostra na tela: <b>"+(mostra.trim()?H(mostra):"(espaço)")+"</b>"+(s.f==="ln"?" e pula para a linha de baixo.":".")});
        }
        else if(s.k==="blk")run(s.b);
        else if(s.k==="if"){
          var c=!!aval(s.c,M,js);
          if(linha>=0&&tab[linha]){if(condCols.indexOf(s.c.t)<0)condCols.push(s.c.t);tab[linha].c[s.c.t]=c?"Sim":"Não";}
          passo({no:s.id,ln:s.ln,seg:[s.c.ca,s.c.cb],cond:c,ic:"🤔",
            tx:"O "+C(s.pt?"se":"if")+" pergunta: "+H(subst(s.c,M))+"? "+(c?'<span class="sim">Sim</span>, vai pelo caminho do <b>Sim</b>.':'<span class="nao">Não</span>, '+(s.el?"vai pelo "+C(s.pt?"senao":"else")+".":"pula o bloco do "+C(s.pt?"se":"if")+"."))});
          if(c)run(s.th);else if(s.el)run(s.el);
        }
        else if(s.k==="do"){
          var eh1d=s===L1,nv2=0,vist2={},cvd=varsDe(s.c),nomeD=s.pt?"faça-enquanto":"do-while";
          while(true){
            nv2++;
            if(eh1d){volta++;tab.push({volta:volta,v:{},c:{},tela:""});linha=tab.length-1;fixas={};
              Object.keys(M).forEach(function(n){if(M[n]!==undefined){col(n);tab[linha].v[n]=M[n];}});
              cvd.forEach(function(n){fixas[n]=1;});}
            P[P.length-1].tx+=nv2===1?" Agora começa o "+C(s.pt?"faca":"do")+": o bloco roda <b>antes</b> de testar (volta 1).":"";
            var r2=run(s.b);if(r2==="inf")return r2;
            var c5=!!aval(s.c,M,js),ch2=JSON.stringify(M);
            if(eh1d)tab[linha].c[s.c.t]=c5?"Sim":"Não";
            passo({no:s.id,ln:s.ln,seg:[s.c.ca,s.c.cb],cond:c5,ic:c5?"✅":"🛑",lacoT:s.c.t,
              tx:"Fim da volta "+nv2+". Testa a condição do "+nomeD+": "+H(subst(s.c,M))+"? "+(c5?'<span class="sim">Sim</span>, a seta <b>volta</b> e o bloco roda de novo.':'<span class="nao">Não</span>, <b>sai do laço</b>.')});
            if(!c5)break;
            if(vist2[ch2]){P[P.length-1].tx+=" ⚠️ Tudo está igual à volta anterior: esse laço <b>nunca vai parar</b>. A demonstração para aqui.";P[P.length-1].infinito=true;return "inf";}
            vist2[ch2]=1;
            if(nv2>LIM_VOLTAS){P[P.length-1].tx+=" ⚠️ Esse laço <b>não termina</b>. A demonstração para aqui.";P[P.length-1].infinito=true;return "inf";}
          }
          if(eh1d)linha=-1;
        }
        else if(s.k==="for"||s.k==="while"){
          var eh1=s===L1,vistos={},nvolta=0;
          if(s.k==="for"){var t2=atr(s.ini,"ini");passo({no:s.ini.id,ln:s.ln,seg:[s.ini.ca,s.ini.cb],mud:[s.ini.n],ic:"📦",tx:t2});}
          var cv=varsDe(s.c);
          while(true){
            var c2=!!aval(s.c,M,js),chave=JSON.stringify(M);
            if(eh1){
              if(c2){volta++;tab.push({volta:volta,v:{},c:{},tela:""});}else tab.push({volta:"saiu",v:{},c:{},tela:""});
              linha=tab.length-1;fixas={};
              Object.keys(M).forEach(function(n){if(M[n]!==undefined){col(n);tab[linha].v[n]=M[n];}});
              cv.forEach(function(n){fixas[n]=1;});
              tab[linha].c[s.c.t]=c2?"Sim":"Não";
            }
            if(c2)nvolta++;
            var nome=s.pt?(s.k==="for"?"PARA":"ENQUANTO"):(s.k==="for"?"for":"while");
            passo({no:s.id,ln:s.ln,seg:[s.c.ca,s.c.cb],cond:c2,ic:c2?"✅":"🛑",lacoT:s.c.t,
              tx:"Testa a condição do "+nome+": "+H(subst(s.c,M))+"? "+(c2?'<span class="sim">Sim</span>, entra no laço (<b>volta '+nvolta+"</b>).":'<span class="nao">Não</span>, <b>sai do laço</b>.')});
            if(!c2)break;
            if(vistos[chave]){P[P.length-1].tx+=" ⚠️ Repare: tudo está igual à volta anterior. Esse laço <b>nunca vai parar</b> (laço infinito). A demonstração para aqui.";P[P.length-1].infinito=true;return "inf";}
            vistos[chave]=1;
            if(nvolta>LIM_VOLTAS){P[P.length-1].tx+=" ⚠️ Já foram "+LIM_VOLTAS+" voltas e a condição continua dando Sim: esse laço <b>não termina</b>. A demonstração para aqui.";P[P.length-1].infinito=true;return "inf";}
            var r=run(s.b);if(r==="inf")return r;
            if(s.k==="for"){var t3=atr(s.pas,"pas");passo({no:s.pas.id,ln:s.ln,seg:[s.pas.ca,s.pas.cb],mud:[s.pas.n],ic:"🔁",tx:t3});}
            P[P.length-1].tx+=" A seta <b>volta</b> para o teste.";
          }
          if(eh1){linha=-1;}
        }
        if(i===b.length-1)continue;
      }
    }
    var fimInf=run(prog)==="inf";
    if(!fimInf){
      var o=out.replace(/\n+$/,"").replace(/\n/g," ").trim();
      passo({no:"fim",ln:null,fim:true,ic:"🏁",tx:o?"Fim! Na tela ficou: <b>"+H(o)+"</b>":"Fim! <b>Nada</b> apareceu na tela."});
    }
    var cvs=L1?varsDe(L1.c):[];
    cols.sort(function(a,b){var ia=cvs.indexOf(a),ib=cvs.indexOf(b);if(ia>=0||ib>=0)return (ia<0?99:ia)-(ib<0?99:ib);return 0;});
    return {P:P,cols:cols,condL:L1?L1.c.t:null,condV:cvs,condCols:condCols,infinito:fimInf,saida:out};
  }

  function preparar(q){
    if(q._passo!==undefined)return q._passo;
    q._passo=null;
    try{
      if(!q.rows)return null;
      var ls=linhas(q.rows);if(!/\b(para|for|enquanto|while)\s*\(/.test(ls.join("\n")))return null;
      var js=/\b(let|const|var|console\.log)\b/.test(ls.join("\n"));
      var prog=compilar(ls);
      if(!temLaco(prog))return null;
      var sim=simular(prog,js);
      var fx=montarFluxo(prog);
      q._passo={ls:ls,sim:sim,fx:fx,js:js,java:/System\.out|\bint\b/.test(ls.join("\n"))};
    }catch(e){q._passo=null;}
    return q._passo;
  }

  /* ---------------- tela ---------------- */
  var KW=/\b(int|double|let|const|var|while|for|if|else|do|System\.out\.println|System\.out\.print|console\.log|para|enquanto|se|senao|escreva|inteiro|real)\b/g;
  function hl(s){
    return H(s).replace(/(&quot;|")([^"]*)(")/g,'<span class="pp-str">"$2"</span>').replace(/\b(\d+)\b/g,'<span class="pp-num">$1</span>').replace(KW,'<span class="pp-kw">$1</span>');
  }
  function linhaHTML(s,seg,on){
    if(!on||!seg)return hl(s);
    return hl(s.slice(0,seg[0]))+'<span class="pp-sg">'+hl(s.slice(seg[0],seg[1]))+'</span>'+hl(s.slice(seg[1]));
  }
  function forma(k,cx,cy,w,h){
    var x=cx-w/2,y=cy-h/2;
    if(k==="pil")return '<rect x="'+x+'" y="'+y+'" width="'+w+'" height="'+h+'" rx="'+(h/2)+'"/>';
    if(k==="proc")return '<rect x="'+x+'" y="'+y+'" width="'+w+'" height="'+h+'"/>';
    if(k==="dec")return '<polygon points="'+cx+','+y+' '+(x+w)+','+cy+' '+cx+','+(y+h)+' '+x+','+cy+'"/>';
    var r=h/2;return '<path d="M'+x+','+cy+' L'+(x+w*0.18)+','+y+' L'+(x+w-r)+','+y+' A'+r+','+r+' 0 0 1 '+(x+w-r)+','+(y+h)+' L'+(x+w*0.18)+','+(y+h)+' Z"/>';
  }
  function svgFluxo(fx){
    var h='<svg viewBox="'+fx.vb+'" preserveAspectRatio="xMidYMin meet"><defs>'+
      '<marker id="pp-m0" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#1B2733"/></marker>'+
      '<marker id="pp-m1" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#e8a317"/></marker></defs>';
    fx.ar.forEach(function(a,i){
      h+='<polyline class="pp-ar" data-a="'+i+'" points="'+a.pts.map(function(q){return q.x+","+q.y;}).join(" ")+'" marker-end="url(#pp-m0)"/>';
      if(a.lab){var p0=a.pts[0],p1=a.pts[1]||p0,hor=p1.y===p0.y;
        h+='<text class="pp-lab" x="'+(hor?(p1.x<p0.x?p0.x-34:p0.x+8):p0.x+8)+'" y="'+(hor?p0.y-7:p0.y+16)+'">'+a.lab+'</text>';}
    });
    fx.nos.forEach(function(n){h+='<g class="pp-no" data-n="'+n.id+'">'+forma(n.k,n.x,n.y,n.w,n.h)+'<text x="'+n.x+'" y="'+n.y+'" text-anchor="middle" dominant-baseline="middle">'+H(n.t)+'</text></g>';});
    h+='<g id="pp-res" opacity="0"><rect id="pp-resbg" rx="10" width="74" height="28"/><text id="pp-restx" font-size="15" font-weight="800" fill="#fff" text-anchor="middle" font-family="Arial"></text></g>';
    return h+'</svg>';
  }

  var ST=null;
  function abrir(q,titulo,resposta){
    var d=preparar(q);if(!d)return;
    fechar();
    var temTela=d.sim.P.some(function(x){return x.tab.some(function(r){return r.tela&&r.tela.trim();});});
    var cols=d.sim.cols,cond=[];if(d.sim.condL)cond.push(d.sim.condL);d.sim.condCols.forEach(function(c){if(cond.indexOf(c)<0)cond.push(c);});
    var ov=document.createElement("div");ov.className="pp-ov";
    ov.innerHTML=
      '<div class="pp-top"><span class="pp-selo">📽 ▶ Passo a passo</span>'+
        '<div class="pp-perg">'+(titulo?'<small>'+H(titulo)+'</small>':'')+H(q.p)+'</div>'+
        '<div class="pp-resp" id="pp-resp"><small>RESPOSTA</small><b id="pp-respv">?</b></div>'+
        '<button class="pp-x" id="pp-x" title="Voltar (Esc)">✕</button></div>'+
      '<div class="pp-main">'+
        '<div class="pp-narra"><div class="pp-ic" id="pp-ic"></div><div><div class="pp-pas" id="pp-pas"></div><div class="pp-tx" id="pp-tx"></div></div></div>'+
        '<div class="pp-grade">'+
          '<section class="pp-pn"><h3><i></i>Código</h3><div class="pp-cod" id="pp-cod">'+d.ls.map(function(l,i){return '<div class="pp-cl" data-l="'+i+'"><span class="pp-n">'+(i+1)+'</span><span class="pp-seta">▶</span><pre></pre></div>';}).join("")+'</div></section>'+
          '<section class="pp-pn pp-fx"><h3><i></i>Fluxograma</h3>'+svgFluxo(d.fx)+'</section>'+
          '<section class="pp-pn"><h3><i></i>Memória</h3><div class="pp-mem" id="pp-mem"></div><div class="pp-leg">Amarelo = valor que acabou de mudar.</div>'+
            '<h3><i></i>Teste de mesa</h3><div class="pp-mesaw"><table class="pp-mesa" id="pp-mesa"><thead><tr><th>Volta</th>'+cols.map(function(c){return '<th>'+H(c)+'</th>';}).join("")+cond.map(function(c){return '<th>'+H(c)+'?</th>';}).join("")+(temTela?'<th>Tela</th>':'')+'</tr></thead><tbody></tbody></table></div>'+
            '<div class="pp-tela"><small>TELA</small><span id="pp-telatx"></span><span class="pp-cur"></span></div></section>'+
        '</div></div>'+
      '<div class="pp-ctl"><button class="pp-bt" id="pp-ini" title="Começo (Home)">⏮</button><button class="pp-bt" id="pp-ant" title="Anterior (←)">◀ Anterior</button>'+
        '<button class="pp-bt pp-pri" id="pp-pro" title="Próximo (→ ou espaço)">Próximo ▶</button><button class="pp-bt" id="pp-auto" title="Automático (A)">⏵ Automático</button>'+
        '<div class="pp-trilha" id="pp-trilha">'+d.sim.P.map(function(_,i){return '<button data-k="'+i+'" title="Passo '+(i+1)+'"></button>';}).join("")+'</div><span class="pp-cont" id="pp-cont"></span></div>';
    document.body.appendChild(ov);document.body.classList.add("pp-aberto");
    ST={q:q,d:d,k:0,ov:ov,cols:cols,cond:cond,resp:resposta,timer:null,tela:temTela};
    ov.querySelector("#pp-x").onclick=fechar;
    ov.querySelector("#pp-ini").onclick=function(){parar();ir(0);};
    ov.querySelector("#pp-ant").onclick=function(){parar();ir(ST.k-1);};
    ov.querySelector("#pp-pro").onclick=function(){parar();ir(ST.k+1);};
    ov.querySelector("#pp-auto").onclick=auto;
    Array.prototype.forEach.call(ov.querySelectorAll("#pp-trilha button"),function(b){b.onclick=function(){parar();ir(+b.getAttribute("data-k"));};});
    document.addEventListener("keydown",tecla);
    ir(0);
  }
  function tecla(e){
    if(!ST)return;
    if(e.key==="ArrowRight"||e.key===" "||e.key==="PageDown"){e.preventDefault();parar();ir(ST.k+1);}
    else if(e.key==="ArrowLeft"||e.key==="PageUp"){e.preventDefault();parar();ir(ST.k-1);}
    else if(e.key==="Home"){parar();ir(0);}
    else if(e.key==="a"||e.key==="A")auto();
    else if(e.key==="Escape")fechar();
  }
  function fechar(){
    if(!ST)return;parar();document.removeEventListener("keydown",tecla);
    ST.ov.parentNode.removeChild(ST.ov);document.body.classList.remove("pp-aberto");ST=null;
  }
  function parar(){if(ST&&ST.timer){clearInterval(ST.timer);ST.timer=null;var b=ST.ov.querySelector("#pp-auto");b.classList.remove("on");b.textContent="⏵ Automático";}}
  function auto(){
    if(!ST)return;if(ST.timer){parar();return;}
    if(ST.k===ST.d.sim.P.length-1)ir(0);
    var b=ST.ov.querySelector("#pp-auto");b.classList.add("on");b.textContent="⏸ Pausar";
    ST.timer=setInterval(function(){ir(ST.k+1);},2300);
  }
  function ir(n){
    var P=ST.d.sim.P,ov=ST.ov;ST.k=Math.max(0,Math.min(P.length-1,n));
    var p=P[ST.k],ant=ST.k>0?P[ST.k-1]:null,$$=function(s){return ov.querySelector(s);};
    $$("#pp-ic").textContent=p.ic;$$("#pp-tx").innerHTML=p.tx;
    var lin=p.linha>=0?p.tab[p.linha]:null;
    $$("#pp-pas").textContent="Passo "+(ST.k+1)+" de "+P.length+(lin&&lin.volta!=="saiu"?" · Volta "+lin.volta:"");
    Array.prototype.forEach.call(ov.querySelectorAll(".pp-cl"),function(l){
      var i=+l.getAttribute("data-l"),on=i===p.ln;l.classList.toggle("on",on);
      l.querySelector("pre").innerHTML=linhaHTML(ST.d.ls[i],p.seg,on);
    });
    var vis={};P.slice(0,ST.k).forEach(function(x){vis[x.no]=1;});
    Array.prototype.forEach.call(ov.querySelectorAll(".pp-no"),function(g){var id=g.getAttribute("data-n");g.classList.toggle("on",id===p.no);g.classList.toggle("vis",!!vis[id]&&id!==p.no);});
    var ia=-1;if(ant)ST.d.fx.ar.forEach(function(a,i){if(a.de===ant.no&&a.pa===p.no)ia=i;});
    Array.prototype.forEach.call(ov.querySelectorAll(".pp-ar"),function(a){var on=+a.getAttribute("data-a")===ia;a.classList.toggle("on",on);a.setAttribute("marker-end",on?"url(#pp-m1)":"url(#pp-m0)");});
    var res=$$("#pp-res");
    if(p.cond!==undefined){
      var nd=null;ST.d.fx.nos.forEach(function(x){if(x.id===p.no)nd=x;});
      var rb=$$("#pp-resbg"),rt=$$("#pp-restx");
      rb.setAttribute("x",nd.x+16);rb.setAttribute("y",nd.y-nd.h/2-32);rb.setAttribute("fill",p.cond?"#1e9e4a":"#d9534f");
      rt.setAttribute("x",nd.x+53);rt.setAttribute("y",nd.y-nd.h/2-13);rt.textContent=p.cond?"Sim ✔":"Não ✘";res.setAttribute("opacity","1");
    }else res.setAttribute("opacity","0");
    var nomes=Object.keys(p.M).filter(function(n){return p.M[n]!==undefined;});
    $$("#pp-mem").innerHTML=nomes.length?nomes.map(function(n){return '<div class="pp-var'+(p.mud.indexOf(n)>=0?" mud":"")+'"><div class="nm">'+H(n)+'</div><div class="vl">'+H(fmt(p.M[n]))+'</div></div>';}).join(""):'<div class="pp-leg" style="margin:0">Ainda não há variáveis.</div>';
    var at=ant?ant.tab:[];
    $$("#pp-mesa tbody").innerHTML=p.tab.length?p.tab.map(function(r,i){
      var a=at[i]||{v:{},c:{}},cel=function(v,v0,cls){var s=v===undefined||v===""?"":String(v);return '<td class="'+(cls||"")+(s!==""&&s!==(v0===undefined?"":String(v0))?" novo":"")+'">'+H(s)+'</td>';};
      return '<tr class="'+(i===p.linha?"on":"")+(r.volta==="saiu"?" sai":"")+'">'+cel(r.volta,a.volta)+
        ST.cols.map(function(c){return cel(r.volta==="saiu"&&ST.d.sim.condV.indexOf(c)<0?"—":(r.v[c]===undefined?"":fmt(r.v[c])),a.v[c]===undefined?"":fmt(a.v[c]));}).join("")+
        ST.cond.map(function(c){var v=r.c[c];return cel(v===undefined?(r.volta==="saiu"?"—":""):v,a.c[c],v==="Sim"?"sim":v==="Não"?"nao":"");}).join("")+
        (ST.tela?cel(r.volta==="saiu"?"—":r.tela.trim(),a.tela===undefined?"":a.tela.trim()):"")+'</tr>';
    }).join(""):'<tr><td colspan="'+(1+(ST.tela?1:0)+ST.cols.length+ST.cond.length)+'" class="pp-vazio">As voltas aparecem aqui.</td></tr>';
    var velho=ant?ant.out:"";
    $$("#pp-telatx").innerHTML=p.out.indexOf(velho)===0&&p.out!==velho?H(velho)+'<span class="novo">'+H(p.out.slice(velho.length))+'</span>':H(p.out);
    var fim=ST.k===P.length-1;
    $$("#pp-resp").classList.toggle("ok",fim);$$("#pp-respv").textContent=fim?(ST.resp||"✔"):"?";
    $$("#pp-ant").disabled=$$("#pp-ini").disabled=ST.k===0;$$("#pp-pro").disabled=fim;
    $$("#pp-cont").textContent=(ST.k+1)+" / "+P.length;
    Array.prototype.forEach.call(ov.querySelectorAll("#pp-trilha button"),function(b,i){b.classList.toggle("feito",i<ST.k);b.classList.toggle("at",i===ST.k);});
    if(fim)parar();
  }
  return {preparar:preparar,abrir:abrir,fechar:fechar,_compilar:compilar,_simular:simular,_fluxo:montarFluxo,_linhas:linhas};
})();
/* PASSO-FIM */
