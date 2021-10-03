function mostrarOcultarSenha (){
  var senha=document.getElementById("senha");
  if(senha.type=="password"){
    senha.type="text";
    document.getElementById('mostrar').style.display = 'inline-block';
    document.getElementById('ocultar').style.display = 'none';
   
  }else{
      senha.type="password";
      document.getElementById('mostrar').style.display = 'none';
      document.getElementById('ocultar').style.display = 'inline-block';
  }
}

/*function openHome() {

  window.location.href="../teste.html";
 
}
*/
