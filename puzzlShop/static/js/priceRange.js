$(document).ready( function () {
    $('#slider-container').slider({
        range: true,
        min: 299,
        max: 1099,
        values: [299, 1099],
        create: function() {
            $("#amount").val("$299 - $1099");
        },
        slide: function (event, ui) {
            $("#amount").val("$" + ui.values[0] + " - $" + ui.values[1]);
            var mi = ui.values[0];
            var mx = ui.values[1];
            filterSystem(mi, mx);
        }
    })
});

function filterSystem(minPrice, maxPrice) {
    $(".product-container").hide().filter(function () {
        var price = parseInt($(this).data("price"), 10);
        return price >= minPrice && price <= maxPrice;
    }).show();
}