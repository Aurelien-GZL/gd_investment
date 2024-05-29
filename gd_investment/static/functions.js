// Function to clear value of one or several elements, referring to them by their id
function clearValues() {
    for (var i = 0; i < arguments.length; i++) {
        var elementId = arguments[i];
        document.getElementById(elementId).value = "";
    }
}


// Function to keep modal open depending on a condition
function handleModal(modalId, condition) {
    if (condition) {
        $(modalId).modal('show');
    }
}


// Function to stop displaying a given element
function hideElementById(elementId) {
    var element = document.getElementById(elementId);
    if (element) {
        element.style.display = 'none';
    }
}


// Function to clear form field
function clearField(field_id) {
    document.getElementById(field_id).value = '';
}