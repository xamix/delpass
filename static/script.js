$(document).ready(function() {

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
    });

    $('.selectMode').on('click', e => {
        let el = $(e.target);
        let mode = el.data('mode');
        $('.selectMode').removeClass('btn-info').addClass('btn-secondary');
        el.removeClass('btn-secondary').addClass('btn-info');
        visualizationMode = mode;
        console.log(visualizationMode);
    });


});