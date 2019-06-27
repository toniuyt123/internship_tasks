$(document).ready(function() {
    $(".delete-item").on('click', function() {
        console.log(this.cart)
        $.ajax({
            url: '/cartitem_delete',
            method: 'POST',
            data: {
                'cartid': cartid,
                'productid': productid
            },
            dataType: 'json',
            success:function(response){
                document.write(response); 
                var row = document.findElementById('item-' + productId);
                row.parentNode().removeChild(row)
            }
        });
    });
});