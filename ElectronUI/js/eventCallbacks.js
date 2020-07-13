//  ENVISIoN
//
//  Copyright (c) 2019 Jesper Ericsson
//  All rights reserved.
//
//  Redistribution and use in source and binary forms, with or without
//  modification, are permitted provided that the following conditions are met:
//
//  1. Redistributions of source code must retain the above copyright notice, this
//  list of conditions and the following disclaimer.
//  2. Redistributions in binary form must reproduce the above copyright notice,
//  this list of conditions and the following disclaimer in the documentation
//  and/or other materials provided with the distribution.
//
//  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
//  ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
//  WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
//  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
//  ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
//  (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
//  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
//  ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
//  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
//  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
//
// ##############################################################################################

// TODO: Validations for most text field inputs.
//       If they are empty you cant just send null send 0 or something instead.

// TODO: This file is pretty long and difficult to read. Events callbacks could be moved out to each HTML files <script> tag.
//       That way functions are at the same place as their html elements.

function resetCanvasPositions(visId) {
    let xPos = window.screenX + window.outerWidth;
    let yPos = window.screenY;
    send_data("envision request", ["position_canvases", visId, [xPos, yPos]]);
    // send_data("envision request", ["toggle_tf_editor", activeVisId, [true]]);
}

function showVolumeDist() {
    send_data("envision request", ["show_volume_dist", activeVisId, []]);
}


// --------------------------------
// ----- Partial charge panel -----
// --------------------------------

function partialBandAdded() {
    let band = $("#partialBandSelection").val();
    let mode = $("#partialModeSelection")[0].selectedIndex - 1;
    if (band == "band" || mode == -1)
        return false;
    band = parseInt(band);
    addPartialBandElement(band, mode);
    $("#partialBandSelection").val("band");
    $("#partialModeSelection").val("mode");
    send_data("envision request", ["select_bands", activeVisId, getPartialBandSelections()]);
    visPanelChanged();
    return false;
}

function partialBandChanged() {
    send_data("envision request", ["select_bands", activeVisId, getPartialBandSelections()]);
    visPanelChanged();
}

function partialBandRemoved() {
    $(this).remove();
    send_data("envision request", ["select_bands", activeVisId, getPartialBandSelections()]);
    return false;
}


// ---------------------------
// ----- 2-D graph panel -----
// ---------------------------

function xRangeSubmitted() {
    let min = parseFloat($("#xRangeMin").val());
    let max = parseFloat($("#xRangeMax").val());
    send_data("envision request", ["set_x_range", activeVisId, [min, max]]);
    visPanelChanged();
    return false;
}

function yRangeSubmitted() {
    // let min = $("#yRangeMin").val()!="" ? parseFloat($("#yRangeMin").val()) : -10000;
    let min = parseFloat($("#yRangeMin").val())
    let max = parseFloat($("#yRangeMax").val());
    send_data("envision request", ["set_y_range", activeVisId, [min, max]]);
    visPanelChanged();
    return false;
}

function verticalLineChecked() {
    let enable = $("#verticalLineCheck").is(":checked");
    send_data("envision request", ["toggle_vertical_line", activeVisId, [enable]]);
}

function verticalLineXSubmitted() {
    let value = parseFloat($("#verticalLineXInput").val());
    send_data("envision request", ["set_vertical_line_x", activeVisId, [value]]);
    return false;
}

function gridChecked() {
    let enable = $("#gridCheck").is(":checked");
    send_data("envision request", ["toggle_grid", activeVisId, [enable]]);
}

function gridSizeSubmitted() {
    let value = parseFloat($("#gridSizeInput").val());
    send_data("envision request", ["set_grid_size", activeVisId, [value]]);
    return false;
}

function xLabelChecked() {
    send_data("envision request", ["toggle_x_label", activeVisId, [$("#xLabelCheck").is(":checked")]]);
}

function yLabelChecked() {
    send_data("envision request", ["toggle_y_label", activeVisId, [$("#yLabelCheck").is(":checked")]]);
}

function nLabelsSubmitted() {
    let value = parseInt($("#labelCountInput").val());
    send_data("envision request", ["set_n_labels", activeVisId, [value]]);
    return false;
}

function ySelectionRadiosChanged() {
    if ($("#allYCheck").is(":checked")) {
        send_data("envision request", ["set_y_selection_type", activeVisId, [2]]);
        $("#specificY").hide();
        $("#multipleY").hide();
    }
    else if ($("#specificYCheck").is(":checked")) {
        send_data("envision request", ["set_y_selection_type", activeVisId, [0]]);
        $("#specificY").show();
        $("#multipleY").hide();
    }
    else if ($("#multipleYCheck").is(":checked")) {
        send_data("envision request", ["set_y_selection_type", activeVisId, [1]]);
        $("#specificY").hide();
        $("#multipleY").show();
    }
    // xRangeSubmitted();
    // yRangeSubmitted();
}

function ySingleSelectionChanged() {
    let selectionIndex = $("#ySingleSelection")[0].selectedIndex;
    send_data("envision request", ["set_y_single_selection_index", activeVisId, [selectionIndex]]);
}

function yMultiSelectionSubmitted() {
    let input = $("#yMultiSelectInput").val();
    send_data("envision request", ["set_y_multi_selection", activeVisId, [input]]);
    // xRangeSubmitted();
    // yRangeSubmitted();
    return false;
}

function loadGraph2DUiData(data) {
    let [type, xRange, yRange,
        lineActive, lineX, gridActive, gridWidth,
        xLabelsActive, yLabelsActive, nLabels,
        ySelectionInfo, yDatasets] = data;

    console.log(data);


    $("#xRangeMin").val(xRange[1]);
    $("#xRangeMax").val(xRange[0]);
    $("#yRangeMin").val(yRange[1]);
    $("#yRangeMax").val(yRange[0]);
    $("#verticalLineCheck").prop("checked", lineActive);
    $("#verticalLineXInput").val(lineX);


    $("#gridCheck").prop("checked", gridActive);
    $("#gridSizeInput").val(gridWidth);

    $("#xLabelCheck").prop("checked", xLabelsActive);
    $("#yLabelCheck").prop("checked", yLabelsActive);
    $("#labelCountInput").val(nLabels);

    // Fill selection lists with options
    $("#possibleYDatasets").empty();
    $("#ySingleSelection").empty();
    for (let i = 0; i < yDatasets.length; i++) {
        $("#possibleYDatasets").append("<option>[" + i + "]: " + yDatasets[i] + "</option>");
        $("#ySingleSelection").append("<option>" + yDatasets[i] + "</option>");
    }

    $("#specificYCheck").prop("checked", ySelectionInfo[0]==0);
    $("#multipleYCheck").prop("checked", ySelectionInfo[0]==1);
    $("#allYCheck").prop("checked", ySelectionInfo[0]==2);
    $("#specificY").css("display", ySelectionInfo[0]==0 ? "block" : "none");
    $("#multipleY").css("display", ySelectionInfo[0]==1 ? "block" : "none");

    if (ySelectionInfo[0]==0) $("#ySingleSelection")[0][ySelectionInfo[1]].selected = true;
    if (ySelectionInfo[0]==1) $("#yMultiSelectInput").val(ySelectionInfo[1]);
}

function loadBands(data) {
    let [bands, activeBand]  = data;

    $("#bandSelection").empty();
    for (let i = 0; i < bands.length; i++) {
        if (i == bands.length - 1)
            $("#bandSelection").append("<option selected>" + bands[i] + "</option>")
        else
            $("#bandSelection").append("<option>" + bands[i] + "</option>")
    }
    $("#bandSelection")[0][activeBand].selected = true;
}

function loadAvailablePartials(options) {
    $("#partialBandSelection > option").slice(1).remove();
    $("#partialModeSelection > option").slice(1).remove();
    for (let i = 0; i < options[0].length; i++)
        $("#partialBandSelection").append("<option>" + options[0][i] + "</option>");
    for (let i = 0; i < options[1].length; i++)
        $("#partialModeSelection").append("<option>" + options[1][i] + "</option>");
}

function loadActivePartials(partials) {
    $("#partialBands").empty();
    for (let i = 0; i < partials[0].length; i++) {
        addPartialBandElement(partials[0][i], partials[1][i]);
    }
}


function addPartialBandElement(band, mode) {
    let elem = $(`
    <form class="row row-margin">
      <div class="input-group col-sm-10">
        <div class="input-group-prepend medium">
          <label class="input-group-text">Active band</label>
        </div>
        <select class="custom-select" name="bandSelect">
        </select>
        <select class="custom-select" name="modeSelect">
        </select>
        <div class="input-group-append">
          <button class="btn btn-primary" type="submit">&nbsp;-</button>
        </div>
      </div>
    </form>`);

    // Copy options from the original element, excluding first option.
    elem.find('[name="bandSelect"]').append($("#partialBandSelection > option").clone().slice(1));
    elem.find('[name="modeSelect"]').append($("#partialModeSelection > option").clone().slice(1));

    // Set correct selected option.
    elem.find('[name="bandSelect"]').val(band);
    elem.find('[name="modeSelect"]')[0][mode].selected = true;

    elem.on("submit", partialBandRemoved)
    elem.find('[name="bandSelect"],[name="modeSelect"]').on("change", partialBandChanged);
    $("#partialBands").append(elem);
}

function getPartialBandSelections() {
    // Return two lists containing active bands and corresponding modes
    let bands = [];
    let modes = [];
    for (let i = 0; i < $("#partialBands")[0].children.length; i++) {
        let inputGroup = $("#partialBands")[0].children[i].children[0];
        let band = parseInt(inputGroup.children[1].value);
        let mode = inputGroup.children[2].selectedIndex
        bands.push(band)
        modes.push(mode)
    }
    return [bands, modes];
}
