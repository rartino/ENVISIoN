
// $ = require('jquery');
// require('popper.js');
// require('bootstrap')
function pathInputChanged() {
    var filePath = $(this)[0].files[0].path;
    $(this).next('.custom-file-label').addClass("selected").html(filePath);
    console.log(filePath)
}

function togglePathType() {
    var vaspDiv = $("#vaspSource")
    var hdf5Div = $("#hdf5Source")

    if ($("#vaspSourceCheckbox").is(":checked")) {
        console.log("Showing vasp")
        vaspDiv.css("display", "block")
        hdf5Div.css("display", "none")
    }
    else if ($("#hdf5SourceCheckbox").is(":checked")) {
        console.log("Hiding vasp")
        vaspDiv.css("display", "none")
        hdf5Div.css("display", "block")
    }
}

function bandSelected() {
    var selection = $("#bandSelection").val()
    console.log(selection)
}

function shadingModeSelected() {
    var selection = $("#shadingModeSelection").val()
    console.log(selection)
}



function addTfPoint() {
    // Validate input first
    if ($(this)[0].checkValidity() === false) {
        event.preventDefault();
        event.stopPropagation();
        //Adds indications of what input is invalid.
        $(this).addClass('was-validated');
        return false
    }

    // Removes validity symbols if input accepted
    $("this").removeClass("was-validated")

    const valueInput = parseFloat($(this)[0][0].value);
    const alphaInput = parseFloat($(this)[0][1].value);
    const colorInput = $(this)[0][2].value
    console.log(JSON.stringify([valueInput, alphaInput, colorInput]))
    //TODO test if all are decently valid

    // Add a new element for the added point.
    // This is not pretty.
    let elementString = (
        '<div class="row row-margin">' +
        '<form class="col-sm-8" name="tfPoint">' +
        '<div class="input-group">' +
        '<input type="text" class="form-control" value="' + valueInput + '" disabled>' +
        '<input type="text" class="form-control" value="' + alphaInput + '" disabled>' +
        '<input class="form-control" type="color" value="' + colorInput + '" disabled>' +
        '<div class="input-group-append">' +
        '<button class="btn btn-primary" type="submit">-</button>' +
        '</div>' +
        '</div>' +
        '</form>' +
        '</div>');
    // $("#tfPoints").prepend(elementString);

    // Insert new element at correct index
    let insertionIndex = 0;
    let tfPoints = [[valueInput, alphaInput, colorInput]]
    for (let i = 0; i < $("#tfPoints")[0].children.length; i++) {

        let formNode = $("#tfPoints")[0].children[i].children[0];
        if (formNode.getAttribute("id") == "tfAdder") {
            continue;
        }

        let formValue = parseFloat(formNode.children[0].children[0].value);
        let formAlpha = parseFloat(formNode.children[0].children[1].value);
        let formColor = formNode.children[0].children[2].value;
        tfPoints.push([formValue, formAlpha, formColor]);

        if (valueInput == formValue) {
            insertionIndex = -1;
            break;
        }
        if (valueInput > formValue) {
            console.log(formValue)
            insertionIndex = i + 1;
        }
    }
    // console.log(JSON.stringify(tfPoints))
    if (insertionIndex == -1) {
        // TODO: Set invalid input
        console.log("Point with that value already exist.")
    }
    else {
        let rowNode = $("#tfPoints")[0].children[insertionIndex];
        $(elementString).insertBefore($(rowNode))
    }
    $('[name="tfPoint"]').on("submit", removeTfPoint);
    return false; //Return false to stop page from reloading
}

function removeTfPoint() {
    console.log("Removing point");
    $(this).parent().remove();
    return false;
}

