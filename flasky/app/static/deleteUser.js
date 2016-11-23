function deleteUser(id){
 if(window.confirm('你确定要删除该账户吗？')){ 

    $.post('usermanager', { username: id}, function (response) {
        // var obj = window.open("about:blank");  
            document.write(response); });

}else{ 
//alert("取消"); 
    
} 
}