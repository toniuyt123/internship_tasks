$(document).ready( function (){
    console.log('yee')
    $.ajax({
        type: "POST",
        url: "",
        success: function(data){
            console.log('yee')
            console.log(data)
        },
        error: function(req, status, err) {
            console.log('Something went wrong', status, err);
        }
      });
});
