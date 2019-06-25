$(document).ready(function () {
    window.sort = function sort(param, desc) {
        $(function () {
            console.log('yo')
            $.ajax({
                url: '/products',
                method: 'POST',
                data: {
                    'sort': {
                        'param': param,
                        'desc': desc
                    }
                },
                dataType: 'json',
                success:function(response){
                    document.write(response); 
               }
            });
        });
    }
});