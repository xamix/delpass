$(document).ready(function() {

    var toastStatus = $("#toastStatus");
    var toastText = document.getElementById("toastText");

    // Cache buster added because caching was a big problem on mobile
    let cacheBuster = new Date().getTime();

    let visualizationMode = 'chase';
    let chosenColor = '';

    // Enable input spinner on all number type
    var props = {
        buttonsClass: "btn-primary"
    }
    $("input[type='number']").inputSpinner(props);

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

    $('.selectMode').on('click', e => {
        let el = $(e.target);
        let mode = el.data('mode');
        $('.selectMode').removeClass('btn-primary').addClass('btn-secondary');
        el.removeClass('btn-secondary').addClass('btn-primary');
        visualizationMode = mode;
        console.log(visualizationMode);

        $.get('/list-sound', function(data) { 
            // Clear the existing list
            $('#soundList .list-group li').remove();

            // Fill with retrived list
            $.each(data.data, function(index, props) {
                let li = $("<li>")
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
        });
    });

    $('#text').keypress(function(event){
        var keycode = (event.keyCode ? event.keyCode : event.which);
        if(keycode == '13'){
            $('#send').click()
        }
    });

    $('#send').on("click touchstart", () => {
        let text = $("#text").val().trim();
        if(text) {
            let params = {
                'text': text,
                'duration': parseInt($('#duration').val())  || null,
                'color': alwanColorPicker.getColor().rgb(),
                'color_mode': $("input[name=radioBtnColor]:checked").val(),
                'color_intensity': $("input[name=radioBtnIntensity]:checked").val(),
                'sound': $('#soundList .list-group').find('li.active').data('props') || null
            };
            console.dir(params);
            $.post('/set-mode', {"params": JSON.stringify(params)}, function(data) { 
                let success = data["success"]
                let message = data["message"]
                if(success) {
                    toastStatus.addClass('bg-success');
                    toastStatus.removeClass('bg-danger');
                    toastText.textContent="Successfully changed mode";
                }
                else {
                    toastStatus.addClass('bg-danger');
                    toastStatus.removeClass('bg-success');
                    toastText.textContent="Fail to change mode: " + message;
                }
                toastStatus.toast('show');
            });
        }
        else {
            console.log("Empty text, skip sending it");
        }
        return false
    });
});