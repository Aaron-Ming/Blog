function validate() {
    var pw1 = document.getElementById("pw1").value;
    var pw2 = document.getElementById("pw2").value;
    if(pw1 == pw2) {
      document.getElementById("tishi").innerHTML="<font color='green'>两次密码相同</font>";
      document.getElementById("submit").disabled = false;
    } else {
      document.getElementById("tishi").innerHTML="<font color='red'>两次密码不相同</font>";
      document.getElementById("submit").disabled = true;
    }
}
function checklong() {
    var pw1 = document.getElementById("pw1").value;
    var pw2 = document.getElementById("pw2").value;
    if(pw1.length<6 || pw2.length<6) {
      document.getElementById("tishi").innerHTML="<font color='red'>至少6位密码</font>";
      document.getElementById("submit").disabled = true;
    }
}

