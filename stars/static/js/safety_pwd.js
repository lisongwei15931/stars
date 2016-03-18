
function check_upd_pwd(only_digit) {
    var flag = check_old_pwd();
    return check_set_pwd(only_digit) && flag;
}

function check_old_pwd() {
    var pwd = document.getElementById("pwd").value;

    if(pwd == "") {
        $("#pwd_err_msg_div_id").html("请输入原密码");
        return false;
    }
    return true;
}

function check_set_pwd(only_digit){
    $("#pwd0_err_msg_div_id").html("");
    $("#pwd1_err_msg_div_id").html("");

    var pwd0 = document.getElementById("pwd0").value;
    var pwd1 = document.getElementById("pwd1").value;
    var flag = true;

    var is_only_digit = arguments[0] ? arguments[0]: false;
    if(pwd0 == ""){
        flag = false;
        $("#pwd0_err_msg_div_id").html("请输入新密码");
    } else if(pwd0.length <6 || pwd0.length > 20) {
        flag = false;
        $("#pwd0_err_msg_div_id").html("密码长度应为6-20位");
    } else if(is_only_digit && !/^\d+$/.test(pwd0)) {
        flag = false;
        $("#pwd0_err_msg_div_id").html("密码只能是数字");
    }

    if(flag && pwd0 != "") {
        if(pwd1 == "") {
            flag = false;
            $("#pwd1_err_msg_div_id").html("请再次输入新密码");
        } else if(pwd0 != pwd1) {
            $("#pwd1_err_msg_div_id").html("两次输入的密码不一致");
            flag = false;
        }
    }
    return flag;
}
