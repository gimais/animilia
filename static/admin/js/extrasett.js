(function ($) {
    $(document).ready(function () {
        const module = $(".js-inline-admin-formset .module");
        const type = $(".field-type select#id_type");

        function toggleRowAddButton(type) {
            let addButton = module.find('.add-row');
            let emptyInput = module.find('#series-empty');

            if (type) {
                addButton.show();
            } else {
                addButton.hide();
                emptyInput.show();
                let rows = $('tbody').find('tr');
                for (let i = 0; i < rows.length - 2; i++) {
                    $(rows[i]).remove()
                }
            }
        }

        module.hide();

        if ($(this).children("option:selected").val() === '1') {
            $(".field-episodes").hide();
        }

        type.change(function () {
            if ($(this).children("option:selected").val() === '1') {
                $(".field-episodes").hide();
                toggleRowAddButton(false)
            } else {
                $(".field-episodes").show();
                toggleRowAddButton(true)
            }
        });

        $(".js-inline-admin-show-or-hide-button").on('click', function () {
            module.toggle();
        });
    });
})(django.jQuery);