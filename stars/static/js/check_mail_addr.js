function check_mail_addr(err_msg_div_id)
{
    var mail_addr_fmt = /[_a-z\d\-\./]+@[_a-z\d\-]+(\.[_a-z\d\-]+)*(\.(info|biz|com|edu|gov|net|am|bz|cn|cx|hk|jp|tw|vc|vn))$/i
    var addr = document.getElementById("mail_addr").value;
    var div_id = err_msg_div_id ? err_msg_div_id : "err_mail_msg_div_id"
    if(addr=="" || addr.replace(/\s/g,"")=="") {
        $("#"+div_id).html("请输入邮箱");
        return false;
    }else if(!mail_addr_fmt.test(addr))
    {
        $("#"+div_id).html("邮箱格式不正确");
        return false;
    }
    else {
        $("#"+div_id).html("");
    }
    return true;
}

    //离开输入框触发事件
    function OnBlurForMailAddrChk(element,elementvalue,err_msg_div_id)
    {
        var mail_addr_fmt = /[_a-z\d\-\./]+@[_a-z\d\-]+(\.[_a-z\d\-]+)*(\.(info|biz|com|edu|gov|net|am|bz|cn|cx|hk|jp|tw|vc|vn))$/i
        var div_id = err_msg_div_id ? err_msg_div_id : "err_mail_msg_div_id"

        if(element.value=="" || element.value.replace(/\s/g,"")=="")
        {
            element.value=elementvalue;
            element.type="text";
            element.style.color="#999";
            $("#"+div_id).html("");
        }
        else if(!mail_addr_fmt.test(element.value))
        {
            $("#"+div_id).html("邮箱格式错误");
        }
        else {
            $("#"+div_id).html("");
        }
    }