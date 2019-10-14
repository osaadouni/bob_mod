$(function($) {

    function debug_console(m) {
        console.log(m);
    }

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
                    scrollTop: $(elts[0]).offset().top-10
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

                        $first = $container.find('input[type=text],textarea,select').filter(':visible:first');
                        console.log('$first.length: ' + $first.length);
                        if ($first.length) {
                            $('html, body').animate({
                                scrollTop: $first.offset().top-100
                            }, 2000);
                        }

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
                    scrollTop: $(elts[0]).offset().top-50
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
        //==========================================
        // Generic PV Form Validation and processing
        //==========================================
        $('body').on('submit', 'form.pv-form-validate', function(e) {
            e.preventDefault();
            console.log('[form.pv-form-validate] submit clicked');
            var $form = $(this);

            var checked = true;

            $fields = $form.find('input[type=text],input[type=file],textarea,select').filter('[required]:visible');
            debug_console('$fields.length: ' + $fields.length);
            $fields.each(function () {
                val = $.trim($(this).val());
                console.log('=> id: ' +  $(this).attr('id') + '; val: '+ val + '; type: ' + $(this).attr('type'));
                if ('' == val) {
                    if ( 'file' === $(this).attr('type')) {
                        $file_hidden = $(this).closest('div.file-upload-wrapper').find('input[type=hidden].hidden-pdf-document');
                        if ($file_hidden.length) {
                            var h_value = $.trim($file_hidden.val());
                            console.log('h_value: ' + h_value);
                            if ( '' !== h_value) {
                                return true;
                            }
                        }
                    }
                    $(this).addClass('is-invalid');
                    $par = $(this).closest('div');
                    $par.find('div.invalid-feedback,div.valid-feedback').remove();
                    $par.append($('<div class="invalid-feedback">Dit veld is verplicht.</div>'));
                    $(this).closest('div.form-group').find('label').addClass('np-error');
                    checked = false;
                }
            })
            debug_console('checked = ', checked);
            if (!checked) {
                 debug_console('validation failed!, form.length: ' +  $form.length );
                 var $elts = $form.find('input.form-control.is-invalid,input[type=file].is-invalid,input.custom-file-input,select.custom-select.is-invalid,textarea.form-control.is-invalid');
                 debug_console('$elts.length: '+ $elts.length);
                 $elts.each(function() {
                     debug_console(' => '+ $(this).attr('id')) ;
                 });
                 var $focus = undefined;
                 if ( $elts.length ) {
                        $focus = $elts.first();
                 } else {
                        $focus = $form;
                 }
                 debug_console('$focus.length: ' + $focus.length) ;
                 if ($focus.length) {
                     $('html, body').animate({
                         scrollTop: $focus.offset().top - 50
                     }, 1000);
                 }
                 return false;
            }


            var form  = $form[0]
            console.log(form);
            var formData  = new FormData(form);
            console.log(formData);
            var $content_wrapper =  $form.closest('div.pv-tab-content-wrapper');
            console.log('$content_wrapper.length: '+ $content_wrapper.length);
            if (!$content_wrapper.length) {
                console.log('content wrapper missing');
                return false;
            }
            var $collapse_wrapper =  $content_wrapper.closest('div.collapse');
            console.log('$collapse_wrapper.length: '+ $collapse_wrapper.length);
            if (!$collapse_wrapper.length) {
                console.log('collapse wrapper missing');
                return false;
            }
            //$('body').find('div.loading').show();
            $.ajax({
                type: $form.attr('method'),
                url: $form.attr('action'),
                data: formData, // $form.serialize(),
                enctype: 'multipart/form-data',
                processData: false,
                contentType: false,
                cache: false,
                success: function(data) {
                    //console.log(data);
                    console.log('back on track ');
                    $('body').find('div.loading').hide();
                    if (typeof undefined !== typeof data.html &&  false !== data.html ) {
                        $content_wrapper.html(data.html);
                    }
                    if (typeof undefined !== typeof data.detail_url &&  false !== data.detail_url ) {
                        console.log('update data-url with detail_url: ' + data.detail_url);
                        $collapse_wrapper.attr('data-url',  data.detail_url);
                    }
                },
                error: function(data) {
                    console.log('error');
                }
            })
            return false;
        });

        $('input.form-control,select.form-control, textarea.form-control').on('click ', function (e) {
            //e.preventDefault();
            //e.stopPropagation();
            $(this).removeClass('is-invalid');
            $(this).closest('div.form-group').find('label').removeClass('np-error');
        });

        $('body').on('click', 'form input.form-control,input[type=file],select.form-control,select.custom-control,textarea.form-control', function (e) {
            //e.preventDefault();
            //e.stopPropagation();
            $(this).removeClass('is-invalid');
            $(this).closest('div.form-group').find('label').removeClass('np-error');
        });


        //  entity type check event
        $('body').on('click', 'input[type=radio].entity-type-check', function(e) {
            e.stopPropagation();
            var val = $(this).val();
            console.log('[entity-type]selected : ' + val);

            var $form = $(this).closest('form.pv-form-validate');
            if ( $form.length) {
                $form.find('input[type=radio].entity-type-check').removeAttr('checked');
                $(this).attr('checked', 'checked');
            }


            $('body').find('div.pv-entity-type').hide();
            var type = val;
            if (type == 'on') { type = 'np';}
            $entity_container = $('body').find('div.pv-entity-type[data-entity-type="'+type+'"]');
            console.log('$entity_container.length: '+ $entity_container.length);
            $entity_container.show();
            if ( val == 'on') {

                $entity_container.find('input,select,textarea').val('');
                var input_value = $.trim($entity_container.find('input[name*="achternaam"]').val());
                if ( '' === input_value) {
                    $entity_container.find('input[name*="achternaam"]').val('NN');
                }
            }
        });



    }); // end document.ready()
});