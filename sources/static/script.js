$(document).ready(function() {

    // Cache buster added because caching was a big problem on mobile
    let cacheBuster = new Date().getTime();

    var toastStatus = $('#toastStatus');
    var toastText = document.getElementById('toastText');

    // Enable input spinner on all number type
    var props = {
        buttonsClass: 'btn-primary'
    }
    $('input[type="number"]').inputSpinner(props);

    // Configure color picker
    Alwan.defaults.swatches = [
        'rgba(255, 0, 0, 1)',
        'rgba(255, 123, 0, 1)',
        'rgba(0, 255, 0, 1)',
        'rgba(0, 0, 255, 1)',
        'rgba(255, 255, 0, 1)',
        'rgba(255, 0, 255, 1)',
        'rgba(108, 16, 157, 1)',
        'rgba(0, 255, 255, 1)'
    ];
    const alwanColorPicker = new Alwan('#colorPicker',
    {
        color: 'rgba(255, 0, 255, 1)',
        theme: 'dark',
        format: 'rgb',
        inputs: {
            rgb: true,
            // hex: true,
            // hsl: true,
        },
        opacity: false,
        preview: true,
        copy: false,
    });

    // Function to popup error
    function popupHttpError(message) {
        toastStatus.addClass('bg-danger');
        toastStatus.removeClass('bg-success');
        toastText.textContent = 'HTTP request failed: ' + message;
        toastStatus.toast('show');
    }

    // Function to update mode
    function updateMode(mode) {

        console.log(mode);

        // Reset all buttons
        $('button[name=btnMode]').removeClass('btn-primary').addClass('btn-secondary');

        // Set current button to active
        $('button[name=btnMode][value=' + mode + ']').removeClass('btn-secondary').addClass('btn-primary');

        // Hide all
        $(
          '.textMode, .soundMode, .imageMode, .statusMode, .colorParams',
        ).addClass('is-hidden');

        // Depending on mode
        if(mode == 'text') {
            $('.textMode, .colorParams').removeClass('is-hidden');
        }
        else if(mode == 'sound') {
            $('.soundMode, .colorParams').removeClass('is-hidden');

            // Clear the existing list
            $('#soundList .list-group li').remove();

            $.get('/list-sound', function(data) {

                // Fill with retrived list
                $.each(data.data, function(index, props) {
                    let li = $('<li>')
                        .attr('class', 'list-group-item')
                        .data('props', JSON.stringify(props))
                        .text(props.name)

                    if(index === 0) {
                        li.addClass('active')
                    }

                    $('#soundList .list-group').append(li)
                });

                // Click handler
                $('.list-group li').click(function(e) {
                    e.preventDefault()

                    $(this).parent().find('li').removeClass('active');
                    $(this).addClass('active');
                });
            }).fail(function(xhr, textStatus, errorThrown) {
                popupHttpError("Fail to get sound list")
            });;
        }
        else if(mode == 'image') {
            $('.imageMode, .colorParams').removeClass('is-hidden');
        }
        else if(mode == 'status') {
            $('.statusMode').removeClass('is-hidden');

            // Display mode
            $('#statusModeLabel').text("Mode:")

            // Clear the existing list
            $('#historyList .list-group li').remove();

            $.get('/status', function(data) {

                // Display mode
                $('#statusModeLabel').text("Mode: " + data.data.mode)

                if(data.data.history.length > 0) {
                    // Fill with retrived list
                    $.each(data.data.history.reverse(), function(index, props) {

                        let text = props.mode
                        if(props.mode == "text") {
                            text = props.text
                        }
                        else if(props.mode == "sound") {
                            let sound = JSON.parse(props.sound)
                            text = sound.name
                        }
                        else if(props.mode == "image") {
                            text = props.image
                        }

                        let li = $('<li>')
                            .addClass('list-group-item')
                            .addClass('justify-content-start')
                            .append("<strong>" + props.mode.charAt(0).toUpperCase() + props.mode.slice(1) + "</strong><br>" + text)

                        if(props.mode == "text" || props.mode == "image") {
                            li.append("<small> (" + props.duration + "sec)</small>")
                        }

                        $('#historyList .list-group').append(li)
                    });
                }
                else {
                    let li = $('<li>')
                            .attr('class', 'list-group-item')
                            .data('props', JSON.stringify(props))
                            .text("NO HISTORY")

                        $('#historyList .list-group').append(li)
                }
            }).fail(function(xhr, textStatus, errorThrown) {
                popupHttpError("Fail to get status")
            });
        }
    }

    // Force current mode
    updateMode('text')

    $('input[name=radioBtnColor]').on('change', e => {
        let el = $(e.target);
        let mode = el.val();
        if(mode == 'spectrum') {
           $('#colorPicker').hide()
        } else {
            $('#colorPicker').show()
        }
    });

    $('button[name=btnMode]').on('click', e => {
        let el = $(e.target);
        let mode = el.val();
        updateMode($(e.target).val())
    });

    $('#text').keypress(function(event){
        var keycode = (event.keyCode ? event.keyCode : event.which);
        if(keycode == '13'){
            $('#send').click()
        }
    });

    $('#send').on('click', () => {
        let text = $('#text').val().trim();
        let params = {
            'mode': $('button[name=btnMode].btn-primary').val(),
            'text': text,
            'duration': parseInt($('#duration').val()) || null,
            'color': alwanColorPicker.getColor().rgb(),
            'color_mode': $('input[name=radioBtnColor]:checked').val(),
            'strobo_speed': $('#stroboSpeed').prop('max') - $('#stroboSpeed').val() + 1,
            'image': $('input[name=radioBtnImage]:checked').val(),
            'color_intensity': $('input[name=radioBtnIntensity]:checked').val(),
            'sound': $('#soundList .list-group').find('li.active').data('props') || null
        };
        console.dir(params);

        $.post('/set-mode', {'params': JSON.stringify(params)}, function(data) {
            let success = data['success']
            let message = data['message']
            if(success) {
                toastStatus.addClass('bg-success');
                toastStatus.removeClass('bg-danger');
                toastText.textContent='Successfully changed mode';
            }
            else {
                toastStatus.addClass('bg-danger');
                toastStatus.removeClass('bg-success');
                toastText.textContent='Fail to change mode: ' + message;
            }
            toastStatus.toast('show');
        }).fail(function(xhr, textStatus, errorThrown) {
            popupHttpError("Fail to set mode")
        });
    });
});