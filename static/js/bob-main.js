$(function($) {

    function toggleMondelingCheck($ba_mondeling_check) {

        $ba_mondeling_datum = $('body').find('div.bobaanvraag-mondeling-datum');

        if ($ba_mondeling_check.length) {
            var value = $ba_mondeling_check.val();
            console.log('value: ' + value);
            if ('False' == value) {
                if ($ba_mondeling_datum.length) {
                    $ba_mondeling_datum.hide();
                }
            } else {
                if ($ba_mondeling_datum.length) {
                    $ba_mondeling_datum.show();
                }
            }
        }
    }

    $(document).ready(function(){
        console.log('ready');
        $fields = $('input,textarea,select').filter('[required]:visible');
        console.log('$fields.length: ', $fields.length);

        $form = $('body').find('form');

        $('body').on('click', 'input[type=submit].btn-submit',function(e) {
        //$('#aanvraagFormId').on('submit', function(e) {
            e.preventDefault();
            //e.stopPropagation();
            $fields.each(function() {
                val = $(this).val();
                console.log('id: ', $(this).attr('id'), '; val: ', val);
            });

            if ($form[0].checkValidity() === false ) {
                e.preventDefault();
                e.stopPropagation();
                console.log('form not valid');
                var elts = document.querySelectorAll('input.form-control:invalid, select.custom-select:invalid');
                $('html, body').animate({
                    scrollTop: $(elts[0]).offset().top
                }, 2000);
                $form.addClass('was-validated');
                return false;

            }

            console.log('Done. submit the form');
            //return false;
            $form.submit();
            //return true;
        });

        // check bobaanvraag mondeling bevestiging
        $ba_mondeling_check = $('body').find('div.bobaanvraag-mondeling-check input[type=radio]:checked');
        toggleMondelingCheck($ba_mondeling_check);
        $('body').on('click' , 'div.bobaanvraag-mondeling-check input[type=radio]', function(e) {
            e.stopPropagation();
            toggleMondelingCheck($(this));

        });

    }); // end document.ready()
});