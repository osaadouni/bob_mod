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

    /*
     * Fix indexes of verbalisant rows
     */
    function fixVerbIndex() {
        $indexes = $('body').find('span.verb-index');
        console.log('$indexes.length: ' + $indexes.length);
        var i, n, id, newName, newId;
        $.each($indexes, function (key, el) {
            //console.log('key: ' + key +'; el: ' + el);
            i = parseInt(key) + 1;
            $(el).html(i);

            $inputs = $(el).closest('div.pv-verb-row').find('input');
            console.log('$inputs.length:' + $inputs.length);
            if ($inputs.length) {
                $.each($inputs, function (k, e) {
                    n = $(e).attr('name');
                    id = $(e).attr('id');
                    //console.log(k + '; n = ' + n );
                    newName = n.replace(/-[0-9]+$/g, "-" + i);
                    newId = n.replace(/-[0-9]+$/g, "-" + i);
                    $(e).attr('name', newName);
                    $(e).attr('id', newId);
                    console.log(i + ': name=' + newName + '; id:' + newId);
                });
            }

        });
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

        // Autocomplete id_pv_nummer
        $('#id_pv_nummer').autocomplete({
            lookup: function (query, done) {
                // Do Ajax call or lookup locally, when done,
                // call the callback and pass your results:
                var result = {
                    suggestions: [
                        { "value": "United Arab Emirates", "data": "AE" },
                        { "value": "United Kingdom",       "data": "UK" },
                        { "value": "United States",        "data": "US" },
                        { "value": "PV1111",        "data": "pv1111" },
                    ]
                };

                done(result);
            },
            onSelect: function (suggestion) {
                alert('You selected: ' + suggestion.value + ', ' + suggestion.data);
            }
        });


        /////////////////////////////////////////
        // Verbalisant functionlity
        /////////////////////////////////////////
        // add verbalisant
        $('body').on('click', 'i.btn-verb-add', function(e){
           e.stopPropagation();
           console.log('clicked btn-verb-add.');
           var url = $(this).attr('data-url');
           console.log('==> url: ' + url );
           $container = $('body').find('div.pv-verb-container');
           $row  = $('body').find('div.pv-verb-row');
           $verb_total = $('body').find('input#id_verbalisant_total');
           if (!$container.length) {
               console.log('div.pv-verb-container missing.')
               return false;
           }
           if (!$verb_total.length) {
                console.log('input#id_verbalisant_total missing.')
                return false;
           }

           var total = $row.length;
           console.log('[add] before verb total: '+ total );
           $verb_total.val(total);

           $.ajax(url, {
               dataType: 'json',
               data: {row_index: ++total },
               success: function(data, status, xhr) {
                   console.log(data);
                   if (typeof undefined !== typeof data.html && false !== data.html) {
                       $(data.html).appendTo($container);
                       total++;
                       $verb_total.val(total);
                       console.log('[add] after verb total: '+ total);

                       // fix index values
                       fixVerbIndex();
                   }
               },
               error: function(jqXhr, textStatus, errorMessage) {
                   console.log(errorMessage);
               }
           });
        });

        // del verbalisant
        $('body').on('click', 'i.btn-verb-del', function(e){
            e.stopPropagation();
            console.log('clicked btn-verb-del.');

            $verb_total = $('body').find('input#id_verbalisant_total');
            if (!$verb_total.length) {
                console.log('input#id_verbalisant_total missing.')
                return false;
            }

            $row = $('body').find('div.pv-verb-row');
            console.log('$row.length: ' + $row.length);
            var total = $row.length ? $row.length : 0;
            console.log('[del] before verb total: '+ total );

            // get parent container
            $container = $(this).closest('div.pv-verb-container');

            // remove parent row
            $(this).closest('div.pv-verb-row').remove();

            // decrease total
            total--;
            $verb_total.val(total);
            console.log('[del] after verb total: '+ total );

            // fix index values
            fixVerbIndex();

            // fix input names indexes

        });

        $('body').on('click', 'div#accordion  div.btn-pv-tab a.lnk-pv-tab', function(e) {
            e.preventDefault();
            e.stopPropagation();
            console.log('clicked');
            // get current container
            var $container = $(this).closest('div.card').find('div.card-body');
            console.log('$container.length: ' + $container.length);
            if (!$container.length) {
                console.log('container missing');
                return false;
            }
            $container.empty();

            // check if current already open
            var is_open = $(this).closest('div#accordion').find('div.collapse').hasClass('show');
            if (is_open) {
                console.log('already open.');
                $(this).closest('div#accordion').find('div.collapse').removeClass('show');
                $(this).removeClass('collapsed');
                return false;

            }

            // reset
            $(this).closest('div#accordion').find('div.collapse').removeClass('show');
            $(this).closest('div#accordion').find('a.lnk-pv-tab').removeClass('collapsed');

            // update current
            $(this).addClass('collapsed');
            $(this).closest('div.card').find('div.collapse').addClass('show');

            // get url
            var url = $(this).attr('data-url');
            console.log('url: '+ url);

            $.ajax(url, {
                dataType: 'json',
                data: {},
                success: function(data, status, xhr) {
                    console.log(data);
                    if (typeof undefined !== typeof data.html && false !== data.html) {
                        $(data.html).appendTo($container);
                    }
                },
                error: function(jqXhr, textStatus, errorMessage) {
                    console.log(errorMessage);
                }
            });
        });

        // PV van verdenking submit
        $('body').on('submit', 'form#pvVerdenkingFormId', function(e) {
            console.log('form submitted') ;
            $form = $(this);
            var form = $form[0];

            console.log(form);
            if (form.checkValidity() === false ) {
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
            //return false;

            $.ajax({
                type: 'POST',
                url: $form.attr('action'),
                data: $form.serialize(),
                success:function(response) {
                    console.log(response);
                }
            });
            return false;
        });

    }); // end document.ready()
});