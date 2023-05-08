$(document).ready(function() {

    var toastStatus = $("#toastStatus");
    var toastText = document.getElementById("toastText");

    // Cache buster added because caching was a big problem on mobile
    let cacheBuster = new Date().getTime();

    let visualizationMode = 'chase';
    let chosenColor = '';

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
        color: 'rgba(0, 255, 0, 1)',
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
        $('.selectMode').removeClass('btn-info').addClass('btn-secondary');
        el.removeClass('btn-secondary').addClass('btn-info');
        visualizationMode = mode;
        console.log(visualizationMode);

        $.get('/list-sound', function(data) { 
            // Clear the existing list
            $('#soundList .list-group li').remove();

            $.each(data.data, function(index, props) {
                $('#soundList .list-group').append(
                        $("<li>")
                        .attr('class', 'list-group-item')
                        .attr('data-props', JSON.stringify(props))
                        .text(props.name)
                )
                // $('#soundList .list-group').append('<li class="list-group-item" data-props="' + JSON.stringify(props) + '"><strong>' + props.name + '</strong> ' + props.lyrics + '</li>')
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
                'duration': 10,
                'color': alwanColorPicker.getColor().rgb(),
                'color_mode': "fixed",
                'color_intensity': "variable",
            };
            console.dir(params);
            $.post('/send-text', {"params": JSON.stringify(params)}, function(data) { 
                let success = data["success"]
                let message = data["message"]
                if(success) {
                    toastStatus.addClass('bg-success');
                    toastStatus.removeClass('bg-danger');
                    toastText.textContent="Successfully updated mode";
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