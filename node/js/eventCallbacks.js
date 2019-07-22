const fs = require('fs')

var activeVisualisation = "";


// TODO: Validations for most text field inputs.
//       If they are empty you cant just send null

// --------------------------------
// ----- File selection panel -----
// --------------------------------

function startVisPressed() {
    if (activeVisualisation == "") {
        console.log("No visualisation type selected")
        return
    }
    let path = "";
    if ($("#vaspSourceCheckbox").is(":checked")) {
        let vaspPath = $("#vaspDirInput")[0].files[0].path;
        try {
            fs.unlinkSync("temp.hdf5");
        } catch (err) {
            // console.error(err)
        }
        send_data("parser request", ["All", "temp.hdf5", vaspPath])
        send_data("envision request", ["start", activeVisualisation, [activeVisualisation, "temp.hdf5"]]);
    }
    else
        path = $("#hdf5LoadInput")[0].files[0].path;
    send_data("envision request", ["start", activeVisualisation, [activeVisualisation, path]]);
}

function stopVisPressed() {
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
// ----- Volume rendering panel -----
// ----------------------------------

function bandChanged() {
    let selection = $("#bandSelection").val();
    send_data("envision request", ["set_active_band", activeVisualisation, [selection]]);
}

function shadingModeChanged() {
    let selectionIndex = $(this)[0].selectedIndex;
    send_data("envision request", ["set_shading_mode", activeVisualisation, [selectionIndex]]);
}

function volumeBackgroundChanged() {
    let color1 = hexToRGB($("#backgroundColor1").val());
    let color2 = hexToRGB($("#backgroundColor2").val());
    color1.push(1);
    color2.push(1);
    let styleIndex = $("#backgroundStyleSelection")[0].selectedIndex;
    console.log(JSON.stringify([color1, color2, styleIndex]));
    send_data("envision request", ["set_volume_background", activeVisualisation, [color1, color2, styleIndex]])
}

function updateMask() {
    if (!$("#transperancyCheckbox").is(':checked'))
        send_data("envision request", ["set_mask", activeVisualisation, [0, 1]]);
    else if (getTfPoints().length > 0)
        send_data("envision request", ["set_mask", activeVisualisation, [getTfPoints()[0][0], 1]]);
}

function addTfPointSubmitted() {
    const valueInput = parseFloat($(this)[0][0].value);
    const alphaInput = parseFloat($(this)[0][1].value);
    const colorInput = $(this)[0][2].value;

    // Add a new element for the added point.
    addTfPointElement(valueInput, alphaInput, colorInput);

    send_data("envision request", ["set_tf_points", activeVisualisation, [getTfPoints()]]);
    updateMask();
    return false;
}

function removeTfPoint() {
    $(this).remove();
    send_data("envision request", ["set_tf_points", activeVisualisation, [getTfPoints()]]);
    updateMask();
    return false;
}

function sliceCanvasToggle() {
    send_data("envision request", ["toggle_slice_canvas", activeVisualisation, [$("#sliceCanvasCheck").is(":checked")]]);
}

function slicePlaneToggle() {
    send_data("envision request", ["toggle_slice_plane", activeVisualisation, [$("#slicePlaneCheck").is(":checked")]]);
}

function sliceHeightChanged() {
    let value = $(this).val();
    $("#sliceHeightRange").val(value);
    $("#sliceHeightText").val(value);
    if (value == "")
        value = 0.5;
    else
        value = parseFloat(value);
    send_data("envision request", ["set_plane_height", activeVisualisation, [value]]);
}

function sliceZoomChanged() {
    let value = $(this).val();
    $("#sliceZoomtRange").val(value);
    $("#sliceZoomText").val(value);
    let a = Math.pow(10.99, value) - 0.99;
    send_data("envision request", ["set_slice_zoom", activeVisualisation, [a]]);
}


function wrapModeSelected() {
    let selectedIndex = $("#sliceWrapSelection")[0].selectedIndex;
    let modeIndexes = [0, 2]
    send_data("envision request", ["set_texture_wrap_mode", activeVisualisation, [modeIndexes[selectedIndex]]]);
}

function sliceNormalChanged() {
    let x = parseFloat($(this)[0].children[1].value);
    let y = parseFloat($(this)[0].children[2].value);
    let z = parseFloat($(this)[0].children[3].value);
    send_data("envision request", ["set_plane_normal", activeVisualisation, [x, y, z]]);
    return false;
}

// ---------------------------
// ----- 2-D graph panel -----
// ---------------------------

function xRangeSubmitted() {
    let min = parseFloat($("#xRangeMin").val());
    let max = parseFloat($("#xRangeMax").val());
    send_data("envision request", ["set_x_range", activeVisualisation, [min, max]]);
    return false;
}

function yRangeSubmitted() {
    // let min = $("#yRangeMin").val()!="" ? parseFloat($("#yRangeMin").val()) : -10000;
    let min = parseFloat($("#yRangeMin").val())
    let max = parseFloat($("#yRangeMax").val());
    send_data("envision request", ["set_y_range", activeVisualisation, [min, max]]);
    return false;
}

function verticalLineChecked() {
    let enable = $("#verticalLineCheck").is(":checked");
    send_data("envision request", ["toggle_vertical_line", activeVisualisation, [enable]]);
}

function verticalLineXChanged() {
    let value = parseFloat($("#verticalLineXInput").val());
    send_data("envision request", ["set_vertical_line_x", activeVisualisation, [value]]);
}

function gridChecked() {
    let enable = $("#gridCheck").is(":checked");
    send_data("envision request", ["toggle_grid", activeVisualisation, [enable]]);
}

function gridSizeChanged() {
    let value = parseFloat($("#gridSizeInput").val());
    send_data("envision request", ["set_grid_size", activeVisualisation, [value]]);
}

function xLabelChecked() {
    send_data("envision request", ["toggle_x_label", activeVisualisation, [$("#xLabelCheck").is(":checked")]]);
}

function yLabelChecked() {
    send_data("envision request", ["toggle_y_label", activeVisualisation, [$("#yLabelCheck").is(":checked")]]);
}

function nLabelsChanged() {
    let value = parseInt($("#labelCountInput").val());
    send_data("envision request", ["set_n_labels", activeVisualisation, [value]]);
}

function ySelectionRadiosChanged() {
    if ($("#allYCheck").is(":checked")) {
        send_data("envision request", ["set_y_selection_type", activeVisualisation, [2]]);
        $("#specificY").hide();
        $("#multipleY").hide();
    }
    else if ($("#specificYCheck").is(":checked")) {
        send_data("envision request", ["set_y_selection_type", activeVisualisation, [0]]);
        $("#specificY").show();
        $("#multipleY").hide();
    }
    else if ($("#multipleYCheck").is(":checked")) {
        send_data("envision request", ["set_y_selection_type", activeVisualisation, [1]]);
        $("#specificY").hide();
        $("#multipleY").show();
    }
    // xRangeSubmitted();
    // yRangeSubmitted();
}

function ySingleSelectionChanged() {
    let selectionIndex = $("#ySingleSelection")[0].selectedIndex;
    send_data("envision request", ["set_y_single_selection_index", activeVisualisation, [selectionIndex]]);
}

function yMultiSelectionChanged() {
    let input = $("#yMultiSelectInput").val();
    send_data("envision request", ["set_y_multi_selection", activeVisualisation, [input]]);
    // xRangeSubmitted();
    // yRangeSubmitted();
    return false;
}

function hideAtomsChanged() {
    let enable = $("#hideAllAtomsCheck").is(":checked");
    if (!enable)
        send_data("envision request", ["hide_atoms", activeVisualisation, []]);
    else
        $('[name="atomRadiusSlider"]').trigger("input");
}

function atomRadiusChanged() {
    if (!$("#hideAllAtomsCheck").is(":checked"))
        return
    let value = parseInt($(this).val());
    let radius = (Math.pow(1.0243, value) - 1) / 12;
    let index = parseInt($(this).parent().parent().parent().index());
    send_data("envision request", ["set_atom_radius", activeVisualisation, [radius, index]]);
}

// ------------------------
// ----- Parser panel -----
// ------------------------

function parseClicked() {
    let vaspDir = $("#vaspDirInput")[0].files[0].path;
    let hdf5Dir = $("#hdf5DirInput")[0].files[0].path;
    let hdf5FileName = $("#hdf5FileNameInput").val();
    let parseType = $("#parseTypeSelect").val();

    if (!/^.*\.(hdf5|HDF5)$/.test(hdf5FileName)) {
        alert("File must end with .hdf5");
        return;
    }

    send_data("parser request", [[parseType], hdf5Dir + "/" + hdf5FileName, vaspDir])
    console.log(vaspDir, hdf5Dir, hdf5FileName, parseType);
}


// ----------------------------------
// ----- Python response events -----
// ----------------------------------

function visualisationStarted(visInfo) {
    if (visInfo[0] == "charge")
        initializeChargePanel();
    else if (visInfo[0] == "elf")
        initializeELFPanel();
    else if (visInfo[0] == "bandstructure")
        initializeBandstructurePanel();
    else if (visInfo[0] == "pcf")
        initializePCFPanel();
}

function loadBands(bands) {
    $("#bandSelection").empty();
    for (let i = 0; i < bands.length; i++) {
        if (i == bands.length - 1)
            $("#bandSelection").append("<option selected>" + bands[i] + "</option>")
        else
            $("#bandSelection").append("<option>" + bands[i] + "</option>")
    }
}

function loadAtoms(atoms) {
    $("#atomControls").empty();
    for (let i = 0; i < atoms.length; i++) {
        let atomControlElement = $(
            '<div class="form-row row-margin" name="atomControlRow">' +
            '<div class="col-sm-3">' +
            // '<div class="form-check">' +
            // '<input type="checkbox" class="form-check-input" checked>' +
            '<label class="form-check-label">' + atoms[i] + ' radius</label>' +
            // '</div>' +
            '</div>' +
            '<div class="col-sm-4">' +
            '<div class="form-group">' +
            '<input type="range" class="form-control-range" name="atomRadiusSlider">' +
            '</div>' +
            '</div>' +
            '</div>')
        $("#atomControls").append(atomControlElement)
        atomControlElement.find(".form-control-range").on("input", atomRadiusChanged)
        // atomControlElement.find(".form-control-range").on("input", atomRadiusChanged)
    }
}

function loadTFPoints(points) {
    $("#tfPoints").empty();
    for (let i = 0; i < points.length; i++) {
        let hexColor = rgbToHex(points[i][1][0], points[i][1][1], points[i][1][2])
        addTfPointElement(points[i][0], points[i][1][3], hexColor)
    }
}

function loadAvailableDatasets(options) {
    console.log(JSON.stringify(options))
    $("#possibleYDatasets").empty();
    $("#ySingleSelection").empty();
    for (let i = 0; i < options.length; i++) {
        $("#possibleYDatasets").append("<option>[" + i + "]: " + options[i] + "</option>");
        $("#ySingleSelection").append("<option>" + options[i] + "</option>");
    }
}

// ----------------------------
// ----- Helper functions -----
// ----------------------------

function getXRange() {

}

function getTfPoints() {
    // Return a list containing current tfPonts
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

function addTfPointElement(value, alpha, color) {
    // Adds an elemend representing the point to the list in the interface.
    let points = getTfPoints();
    if (points.find(function (point) { return point[0] == value }) != undefined) {
        console.log("Point with value already already exist.");
        return false
    }

    let pointElement = $(
        '<div class="row row-margin">' +
        '<form class="col-sm-10" name="tfPoint">' +
        '<div class="input-group">' +
        '<input type="text" class="form-control" value="' + value + '" disabled>' +
        '<input type="text" class="form-control" value="' + alpha + '" disabled>' +
        '<input class="form-control" type="color" value="' + color + '" disabled>' +
        '<div class="input-group-append">' +
        '<button class="btn btn-primary" type="submit">-</button>' +
        '</div>' +
        '</div>' +
        '</form>' +
        '</div>');

    let insertionIndex = points.findIndex(function (point) { return point[0] > value });
    if (insertionIndex == -1)
        $("#tfPoints").append(pointElement);
    else {
        pointElement.insertBefore($("#tfPoints")[0].children[insertionIndex])
    }
    pointElement.on("submit", removeTfPoint);
}

// ---------------------------------
// ----- Panel initializations -----
// ---------------------------------

function initializeChargePanel() {
    console.log("CHG")
    // $("#visSettings :input").attr("disabled", false);
    send_data("envision request", ["get_bands", "charge", []])
    send_data("envision request", ["get_atom_names", "charge", []])
    send_data("envision request", ["get_tf_points", "charge", []])
}

function initializeELFPanel() {
    console.log("ELF")
    // $("#visSettings :input").attr("disabled", false);
    send_data("envision request", ["get_bands", "elf", []])
    send_data("envision request", ["get_atom_names", "elf", []])
    send_data("envision request", ["get_tf_points", "elf", []])
}

function initializeBandstructurePanel() {
    console.log("Bandstructure")
    send_data("envision request", ["get_available_datasets", "bandstructure", []])
}

function initializePCFPanel(){
    console.log("PCF")
    send_data("envision request", ["get_available_datasets", "pcf", []])
}

function initializeDOSPanel(){
    console.log("PCF")
    send_data("envision request", ["get_available_datasets", "dos", []])
}