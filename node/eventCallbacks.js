
// $ = require('jquery');
// require('popper.js');
// require('bootstrap')

var activeVisualisation = "";


// --------------------------------
// ----- File selection panel -----
// --------------------------------

function startVisPressed(){
    // TODO load atom types
    activeVisualisation = "charge";
    send_data("envision request", ["start", "charge", ["charge", "/home/labb/HDF5/nacl_new.hdf5"]]);
}

function stopVisPressed(){
    send_data("envision request", ["stop", "-", [true]]);
}

function pathInputChanged() {
    let filePath = $(this)[0].files[0].path;
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

// ----------------------------------
// ----- Electron density panel -----
// ----------------------------------

function bandChanged(){
    let selection = $("#bandSelection").val();
    send_data("envision request", ["set_active_band", activeVisualisation, [selection]]);
}

function shadingModeChanged(){
    let selectionIndex = $(this)[0].selectedIndex;
    send_data("envision request", ["set_shading_mode", activeVisualisation, [selectionIndex]]);
}

function volumeBackgroundChanged(){
    let color1 = hexToRGB($("#backgroundColor1").val());
    let color2 = hexToRGB($("#backgroundColor2").val());
    color1.push(1);
    color2.push(1);
    let styleIndex = $("#backgroundStyleSelection")[0].selectedIndex;
    console.log(JSON.stringify([color1, color2, styleIndex]));
    send_data("envision request", ["set_volume_background", activeVisualisation, [color1, color2, styleIndex]])
}

function updateMask(){
    if (!$("#transperancyCheckbox").is(':checked'))
        send_data("envision request", ["set_mask", activeVisualisation, [0, 1]]);
    else if (getTfPoints().length > 0)
        send_data("envision request", ["set_mask", activeVisualisation, [getTfPoints()[0][0], 1]]);
}

function addTfPoint() {
    // Validate input first
    // console.log("adding something HERE")
    // if ($(this)[0].checkValidity() === false) {
    //     event.preventDefault();
    //     event.stopPropagation();
    //     //Adds indications of what input is invalid.
    //     $(this).addClass('was-validated');
    //     return false
    // }
    // // Removes validity symbols if input accepted
    // $("this").removeClass("was-validated")

    const valueInput = parseFloat($(this)[0][0].value);
    const alphaInput = parseFloat($(this)[0][1].value);
    const colorInput = $(this)[0][2].value;

    // Add a new element for the added point.
    let elementString = (
        '<div class="row row-margin">' +
        '<form class="col-sm-10" name="tfPoint">' +
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

    let points = getTfPoints();
    if (points.length == 0){
        let rowNode = $("#tfPoints")[0].children[0];
        $(elementString).insertBefore($(rowNode))
    }
    else if (points.find(function(point){return point[0] == valueInput}) != undefined){
        console.log("point already exist");
    }
    else{
        let insertionIndex = points.findIndex(function(point){return point[0] > valueInput});
        if (insertionIndex == -1)
            insertionIndex = points.length;
        let rowNode = $("#tfPoints")[0].children[insertionIndex];
        $(elementString).insertBefore($(rowNode))
    }
    $('[name="tfPoint"]').on("submit", removeTfPoint);
    send_data("envision request", ["set_tf_points", activeVisualisation, [getTfPoints()]]);
    updateMask()
    return false;
}

function removeTfPoint() {
    $(this).parent().remove();
    send_data("envision request", ["set_tf_points", activeVisualisation, [getTfPoints()]]);
    return false;
}

function sliceCanvasToggle(){
    send_data("envision request", ["toggle_slice_canvas", activeVisualisation, [$("#sliceCanvasCheck").is(":checked")]]);
}

function slicePlaneToggle(){
    send_data("envision request", ["toggle_slice_plane", activeVisualisation, [$("#slicePlaneCheck").is(":checked")]]);
}

function sliceHeightChanged(){
    let value = $(this).val();
    $("#sliceHeightRange").val(value);
    $("#sliceHeightText").val(value);
    if (value == "")
        value = 0.5;
    else
        value = parseFloat(value);
    send_data("envision request", ["set_plane_height", activeVisualisation, [value]]);
}

function sliceNormalChanged(){
    let x = parseFloat($(this)[0].children[0].value);
    let y = parseFloat($(this)[0].children[1].value);
    let z = parseFloat($(this)[0].children[2].value);
    send_data("envision request", ["set_plane_normal", activeVisualisation, [x, y, z]]);
    return false;
}



// ----------------------------
// ----- Helper functions -----
// ----------------------------

function getTfPoints(){
    let tfPoints = [];
    for (let i = 0; i < $("#tfPoints")[0].children.length; i++) {
        let formNode = $("#tfPoints")[0].children[i].children[0];
        if (formNode.getAttribute("id") == "tfAdder")
            continue;
        let value = parseFloat(formNode.children[0].children[0].value);
        let alpha = parseFloat(formNode.children[0].children[1].value);
        let color = hexToRGB(formNode.children[0].children[2].value);
        color.push(alpha);
        tfPoints.push([value, color]);
    }
    return tfPoints;
}

