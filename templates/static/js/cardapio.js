var num = 3;
var img = document.getElementById("imgprincipal");
function trocaImg(){
//apenas para cunho de testes
setTimeout(function () {
  if (num == 1)
    {
      img.src = "img/image10.jpg";
    }
  else if (num == 2)
    {
      img.src = "img/lH2kooyMxb8.png";
    }
    else if (num == 3)
    {
      img.src = "img/image12.jpg";
    }
    //garante que num fique alternando entre 1, 2 e 3
    num = (num % 3) + 1;
    }, 3000);
}

var setaEsquerda = document.getElementById('setaleft');
var setaDireita = document.getElementById('setaright');
var imagem1 = document.getElementById('imgprincipal');

function clicar() {
  imagem1.setAttribute('src', 'imagens/lH2kooyMxb8.png');
}

function clicar2() {
  imagem1.setAttribute('src', 'imagens/image12.jpg');
}


