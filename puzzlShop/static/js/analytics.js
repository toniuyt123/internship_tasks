$(document).ready( function (){
    console.log('yee')
    $.ajax({
        type: "GET",
        dataType: "json",
        url: "localhost:5000/analytics",
        success: function(data){
            console.log('yee')
            console.log(data)
        },
        error: function(error) {
            console.log(error)
        }
      });
});
