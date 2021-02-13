function drag(ev) {
    ev.dataTransfer.setData("img", ev.target.id);
}

function allowDrop(ev) {
    ev.preventDefault();
}

function drop(ev) {
    ev.preventDefault();
    var value = ev.dataTransfer.getData("img");
    if (ev.target.tagName == 'IMG') {
        // console.log('Oops. Accidentally dropping in <img>')
        var target = ev.target.parentElement.parentElement
    } else {
        target = ev.target
    }
    var select = target.children[0].classList[target.children[0].classList.length-1]
    console.log(`${value} dropping in ${select}`)
    $(`#add-${select}`).append(new Option(value, value, false, true));
    $('#actions').submit()
}

// Prevent default behaviour: opening draggable link
$('.grid.pos').on("dragenter dragstart dragend dragleave dragover drag drop", function (e) {
    e.preventDefault();
});

$('.grid.neg').on("dragenter dragstart dragend dragleave dragover drag drop", function (e) {
    e.preventDefault();
});