
$(function(){
        $('button').click(function(){
                var user = $('#txtUsername').val();
                var pass = $('#txtPassword').val();
                $.ajax({
                        url: '/json',
                        data: $('form').serialize(),
                        type: 'GET',
                        success: function(response){
                                alert(response);
                        },
                        error: function(error){
                                alert(error);
                        }
                });
        });
});

