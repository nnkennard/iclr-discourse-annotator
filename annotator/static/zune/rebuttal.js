STATUSES = ["NOT_STARTED", "STARTED", "VALIDATED"] // Change to not started if clicked sentence clicked any radio button, entered text

CURRENT_STATUS = "NOT_STARTED"


// Timing stuff
const start_time = Date.now();

function getElapsedTime() {
    return Math.floor(Date.now() - start_time / 1000);
}


// Initialization

review_sentences = getJsonified("review_sentences");
other_annotations = getJsonified("other_annotations");
metadata = getJsonified("metadata");
num_rebuttal_sentences = getJsonified("num_rebuttal_sentences");

document.getElementById("submitBtn").disabled = "true"
document.getElementById("nav:" + metadata["rebuttal_index"].toString()).classList.add("is-focused")
var highlighted = new Array(review_sentences.length).fill(0);
maybeDisableCopyPrevious()

function maybeDisableCopyPrevious() {
    if (metadata.rebuttal_index == 0 || other_annotations.statuses[metadata.rebuttal_index - 1] == "Incomplete") {
        document.getElementById("copyBtn").disabled = true;
    }
    for (i in other_annotations.statuses) {
        if (other_annotations.statuses[i]) {
            document.getElementById("nav:" + i.toString()).classList.add("is-success")
        }
    }
}

// Utils
function last(l) {
    return l[l.length - 1];
}

function sum(l) {
    return l.reduce(function(a, b) {
        return parseInt(a) + parseInt(b);
    }, 0)

}

function someHighlighted() {
    return sum(highlighted) > 0
}

function getJsonified(label) {
    return JSON.parse(document.getElementById(label).textContent)
}

function toggleModal() {
    modal = document.getElementById("rebuttalmodal")
    if (modal.classList.contains("is-active")) {
        modal.classList.remove("is-active")
    } else {
        modal.classList.add("is-active")
    }
}

function navSwitch(button_element) {
    new_index = last(button_element.id.split(":"))
    parts = window.location.href.split("/")
    new_url = parts.slice(0, 7).join("/") + "/" + new_index + "/" + parts.slice(8)
    window.location.replace(new_url)
}


// Validation



function isSentencesAreAlignedChecked() {
    return document.getElementById("errors").value == "Aligned sentences have been highlighted"
}

function checkNeedsExplanationButDoesntHave() {
    if (document.getElementById("comments").value.trim() == 0){
        if (document.getElementById("label:radios:other").checked) {
            window.alert("Please specify why none of the label options apply")
            return 0
        } else if (document.getElementById("label:radios:multiple").checked){
            window.alert("Please specify which multiple label options apply")
            return 0
        }
    }
    return 1
}

function getLabel(){
    radio_buttons = document.getElementsByClassName("radio");
    labels = {}
        for (radio_button of radio_buttons){
        if (radio_button.checked){
            labels[radio_button.name] = radio_button.value;
        }
    }
    if ("label:radios" in labels){
        return labels["label:radios"]
    } else {
        return null;
    }
}

function validateAll() {

    relation_label = getLabel();
    if (relation_label === null){
        window.alert("Please select a relation label. If none applies, please select 'Other'.")
        return
    }
    if (isSentencesAreAlignedChecked() && !someHighlighted()) {
        window.alert("You have indicated that sentences are highlighted, but none are highlighted. Please fix.")
    } else if (!isSentencesAreAlignedChecked() && someHighlighted()) {
        window.alert("You have highlighted sentences, but selected a 'no context' option as well. Please fix.")
    } else if (!checkNeedsExplanationButDoesntHave()) {
        return
    } else {
        document.getElementById("submitBtn").removeAttribute("disabled");
        result = {
            "alignment_labels": highlighted,
            "alignment_errors": document.getElementById("errors").value,
            "relation_label": relation_label,
            "comments": document.getElementById("comments").value,
            "metadata": metadata,
            "num_rebuttal_sentences": num_rebuttal_sentences,
            "time_to_annotate": getElapsedTime(),
            "start_time": start_time,
        }
        document.getElementById("id_annotation").value = JSON.stringify(result)
        CURRENT_STATUS = "VALIDATED"
    }
}

TAG_TYPE_MAP = {
    "arg": "danger",
    "asp": "link",
    "pol": "success",
    "gro": "warning",
    "fine": "primary"
}

// Label propagation

function getReviewLabelTags(review_index) {
    tags = ""
    for (argx of other_annotations.review_annotations[review_index]) {
        for (category in argx) {
            label = argx[category]
            tag_type = TAG_TYPE_MAP[category]
            tags += '<span class="tag is-' + tag_type + '">' + label + '</span>'
        }
    }

    return '<div class="tags are-small"> ' + tags + ' </div>'
}

function populatePreviewBox() {
    reviewtable = document.getElementById('reviewtable')
    reviewtable.innerHTML = ""

    for (i in highlighted) {
        if (highlighted[i]) {
            reviewtable.innerHTML += '<tr class="border_bottom"><td>' + document.getElementById(
                "sentence:" + i).innerText + ' </td> <td> ' + getReviewLabelTags(i) + ' </td> </tr>';
        }

    }
}


function copyPrevious() {
    rebuttal_index = metadata["rebuttal_index"]
    if (other_annotations.previous_alignment.length > 0) {
        highlighted = new Array(review_sentences.length).fill(0);
        for (index_str of other_annotations.previous_alignment.split("|")) {
            highlighted[parseInt(index_str)] = 1
        }
    } else {
        alert("No annotations available for the previous sentence.")
    }
    for (i in highlighted) {
        updateHighlight(i)
    }
    elementToChange = document.getElementById("label:radios:" + other_annotations.previous_label)
    elementToChange.checked = true;
    relRadioChange(elementToChange)
    populatePreviewBox()
}


// Interaction management

function clicked(ele) {
    review_idx = parseInt(last(ele.id.split(":")));
    highlighted[review_idx] = 1 - highlighted[review_idx];
    updateHighlight(review_idx)
    CURRENT_STATUS = "STARTED"
    populatePreviewBox()
}

function updateHighlight(review_index) {
    sentence_element = document.getElementById("sentence:" + review_index)
    if (highlighted[review_index]) {
        sentence_element.style = "background-color:#d5f5e3"
    } else {
        sentence_element.style = ""
    }
}

function relRadioChange(changed_radio){
    document.getElementById("label:select").value = changed_radio.value;
}

function relSelectChange(sel_element){
    document.getElementById("label:radios:" + sel_element.value).checked = "true"
}

function flipAllControls(clickedElement){
    sentence_index = last(clickedButton.id.split("_"))
    if (clickedButton.checked){
        new_style="display:none"
    } else {
        new_style="display:block"
    }
    for (bla of ["0", "1"]){
        for (menu of all_menus){
            element = document.getElementById(menu+"-d-"+bla+"-"+sentence_index)
            if (clickedButton.checked){
                element.disabled = "true"
            } else {
                element.removeAttribute("disabled")
            }
        }
    }
    argBtn = document.getElementById("addArgBtn-"+sentence_index)
    if (clickedButton.checked){
                argBtn.disabled = "true"
            } else {
                argBtn.removeAttribute("disabled")
            }
}

window.addEventListener('beforeunload', function(e) {
    if (CURRENT_STATUS == "STARTED") {
        e.preventDefault(); //per the standard
        e.returnValue = ''; //required for Chrome
    }
});