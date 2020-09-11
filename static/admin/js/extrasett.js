(function($) {
    $(document).ready(function() {
        var module = $(".js-inline-admin-formset .module");
        var type = $(".field-type select#id_type");

        function toogleRowAddButton(type) {
            var addButton = module.find('.add-row');
            var emptyInput = module.find('#series-empty');

            if(type){
                addButton.show();
            }else{
                addButton.hide();
                emptyInput.show();
                var rows = $('tbody').find('tr');
                for(let i = 0; i < rows.length - 2; i++){
                    $(rows[i]).remove()
                }
            }
        }

        module.hide();
        if($(".field-type select#id_type option:selected").val()==='1')
            $(".field-episodes").hide();

        type.change(function(){
            if($(this).children("option:selected").val()==='1'){
                $(".field-episodes").hide();
                toogleRowAddButton(false)
            }else{
                $(".field-episodes").show();
                toogleRowAddButton(true)
            }
        });

        $(".js-inline-admin-show-or-hide-button").on('click',function () {
            module.toggle();
        });
    });
})(django.jQuery);