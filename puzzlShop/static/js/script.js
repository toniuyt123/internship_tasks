$(document).ready(function () {
    $('.productDescription').each(function () {
        if (this.textContent.length > 300) {
            this.textContent = this.textContent.slice(0, 300).concat('...')
        }
    });

    setInputFilter(document.getElementById("min-ammount"), function (value) {
        return /^\d*$/.test(value);
    });
    setInputFilter(document.getElementById("max-ammount"), function (value) {
        return /^\d*$/.test(value);
    });
});

function filterSystem(minPrice, maxPrice) {
    $(".product-container").hide().filter(function () {
        var price = parseInt($(this).data("price"), 10);
        return price >= minPrice && price <= maxPrice;
    }).show();
}

function setInputFilter(textbox, inputFilter) {
    ["input", "keydown", "keyup", "mousedown", "mouseup", "select", "contextmenu", "drop"].forEach(function (event) {
        textbox.addEventListener(event, function () {
            if (inputFilter(this.value)) {
                this.oldValue = this.value;
                this.oldSelectionStart = this.selectionStart;
                this.oldSelectionEnd = this.selectionEnd;
            } else if (this.hasOwnProperty("oldValue")) {
                this.value = this.oldValue;
                this.setSelectionRange(this.oldSelectionStart, this.oldSelectionEnd);
            }
        });
    });
}