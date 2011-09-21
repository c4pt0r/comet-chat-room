var roomname = "global"

$(document).ready(function() {
    str = location.pathname
    str = str.substr(str.lastIndexOf("/")+1)
    roomname = str
    $("#roomname").html(roomname)
    function setname()
    {
        name = $('#name').val()
        var args = {"_xsrf": getCookie("_xsrf"), "name": name };
        
        $.ajax({url: "/login", type: "POST", dataType: "text",
                   data: $.param(args)
        });
        
        $('#nick').html(name)
    }
    var dialog = art.dialog({lock:true, title:'Please Enter Your Nickname',okVal:'OK', content:'<input width="100%" type="text" id="name"/>', 
    ok:function(){
        setname() 
        $('#entry').focus()
    }});
    $('#name').focus()
    $('#name').keydown(function(e){
        if (e.keyCode == 13)
        {
            setname()
            dialog.close()
            $('#entry').focus()
        }
    });
    
    updater.poll();
    $('#entry').keydown(function(e){
        if (e.keyCode == 13)
        {
            var args = {"_xsrf": getCookie("_xsrf"), "text": $(this).val(), "roomname": roomname};
            $.ajax({url:"/new", type: "POST", dataType: "text",
                       data: $.param(args)});
            $(this).val('')
        }
    })
});
function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}
var updater = {
    errorSleepTime : 500,
    cursor : null,
    poll: function() {
           var args = {"_xsrf": getCookie("_xsrf"), "roomname": roomname};
           $.ajax({url:"/update", type: "POST", dataType: "text",
                   data: $.param(args), success: updater.onSuccess,
                   error: updater.onError});
    },
    onError: function()
    {
        $("#log").append("<div id='msg' ><font color=red> Server Error! </font><br/></div>");
        $('html, body').animate({ scrollTop: 60000 }, 'slow');
    },
    onSuccess: function(response) {
            try {
                updater.newMessages(response);
            } catch (e) {
                updater.onError();
                return;
            }
            updater.errorSleepTime = 500;
            window.setTimeout(updater.poll, 0);
    },
    
    newMessages: function(response) {
            $("#log").append("<div id='msg' > " + response + "<br/></div>");
            $('html, body').animate({ scrollTop: 60000 }, 'slow'); 
    },
}