$(document).ready(function() {
    $('.active').each(function() {
        let collapseIdentifier = $(this).attr('href')
        $(collapseIdentifier).collapse('show')
    })
})

// Bind slider input events
$('.custom-range').each(function() {
    let identifier = $(this).attr('id')
    let output_identifier = $(`label[for="#${identifier}"] > span`).attr('id')
    $('#' + identifier).on('input', function() {
        $('#'+output_identifier).html(this.value)
    })
})

// Fill form
function submitActive(){
    $('ul > li.active').each(function() {
        console.log($(this).text(), $(this).attr('id'))
        let embedder_settings = $($(this).attr('href')).find('div.col-5 input')
        embedder_settings.each(function(){
            $(this).attr('form', 'pipelineForm')
        })
    })
    $('div.col-7 > li.active').each(function() {
        let reducer_settings = $($(this).attr('href')).find('input')
        reducer_settings.each(function(){
            $(this).attr('form', 'pipelineForm')
        })
    })
    $('#pipelineForm').submit();

    $(".wrapper").animate({
        opacity: .3
    });
    $('#loading').show()
}