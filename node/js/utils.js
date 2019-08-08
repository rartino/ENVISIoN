function hexToRGB(hex) {
    hex = hex.replace("#", "");
    let r = parseInt(hex.substring(0, 2), 16);
    let g = parseInt(hex.substring(2, 4), 16);
    let b = parseInt(hex.substring(4, 6), 16);
    return [r / 255.0, g / 255.0, b / 255.0];
}

function componentToHex(c) {
    c = parseInt(c*255);
    var hex = c.toString(16);
    return hex.length == 1 ? "0" + hex : hex;
}

function rgbArrToHex(rgb){
    return rgbToHex(rgb[0], rgb[1], rgb[2]);
}

function rgbToHex(r, g, b) {
    return "#" + componentToHex(r) + componentToHex(g) + componentToHex(b);
}