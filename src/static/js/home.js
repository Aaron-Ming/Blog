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

function checkend() {
    var filename = document.getElementById('avatar').value;
    if (!filename || !(filename.endsWith('.jpg') || filename.endsWith('.jpeg') || filename.endsWith('.png') || filename.endsWith('.gif'))) {
        document.getElementById('tishi').innerHTML('只有jpg、jpeg、png、gif的图片允许上传');
        return false;
    }
}

function avatar_filetype(obj){ 
    var extend = avatar_form.avatar.value.substring(avatar_form.avatar.value.lastindexof(".")+1);
    if(extend==""){
    } else {
      if(!(extend=="jpg"||extend=="jpeg"||extend=="png"||extend=="gif")){
          alert("请上传后缀名jpg、jpeg、png、gif的图片!");
          var nf = obj.clonenode(true);
          nf.value='';
          obj.parentnode.replacechild(nf, obj);
          document.getElementById('tishi').innerHTML('只有jpg、jpeg、png、gif的图片允许上传');
          return false;
      }
    }
    return true; 
}
function lastname(){
 //获取欲上传的文件路径
var filepath = document.getElementById("avatar").value; 
//为了避免转义反斜杠出问题，这里将对其进行转换
var re = /(\\+)/g; 
var filename=filepath.replace(re,"#");
//对路径字符串进行剪切截取
var one=filename.split("#");
//获取数组中最后一个，即文件名
var two=one[one.length-1];
//再对文件名进行截取，以取得后缀名
var three=two.split(".");
 //获取截取的最后一个字符串，即为后缀名
var last=three[three.length-1];
//添加需要判断的后缀名类型
var tp ="jpg,jpeg,gif,png,JPG,JPEG,GIF,PNG";
//返回符合条件的后缀名在字符串中的位置
var rs=tp.indexOf(last);
//如果返回的结果大于或等于0，说明包含允许上传的文件类型
if(rs>=0){
 return true;
 }else{
 alert("您选择的上传文件不是有效的图片文件！");
 return false;
  }
}