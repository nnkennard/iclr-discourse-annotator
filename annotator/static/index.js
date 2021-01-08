// INITIALIZATIONS
switchTab(-1, 1, 1); // Display the first tab
document.getElementById("submitBtn").disabled = "true"


function switchTab(current_tab, total_tabs, direction) {
    new_tab = (current_tab + direction + total_tabs) % total_tabs;
    var tabs = document.getElementsByClassName("tab");
    if (current_tab > -1) {
        tabs.item(current_tab).style.display = "none";
    }
    tabs.item(new_tab).style.display = "block";
}

function isNoContextChecked(index, errors) {
    return errors[index].includes(
        "no_context") || errors[index].includes(
        "global_context") || errors[index].includes(
        "signpost") || errors[index].includes(
        "reference") || errors[index].includes(
        "quote")

}

function getErrors(rebuttal_chunks) {
    checkboxes = document.getElementsByName('checkboxes');
    errors = {}
    for (var i = 0; i < rebuttal_chunks.length; i++) {
        errors[i] = Array();
    }
    for (checkbox of checkboxes) {
        if (checkbox.checked) {
            parts = checkbox.id.split("-")
            errors[parseInt(parts[1])].push(parts[2])
        }
    }
    return errors
}

function getJsonified(label) {
    return JSON.parse(document.getElementById(label).textContent)
}


function generateJson() {

    rebuttal_chunks = getJsonified("rebuttal_chunks");
    rebuttal_sid = getJsonified("rebuttal");
    review_sid = getJsonified("review");

    if (document.getElementById('initials').value === "") {
        alert("Please fill in your initials and run Validate again.")
    } else {
        submitButton = document.getElementById("submitBtn");
        submitButton.removeAttribute("disabled");

        errors = getErrors(rebuttal_chunks)

        alignments = []

        for (i in rebuttal_chunks) {
            rebuttal_chunk_highlights = highlighted[i];
            matches = Array();
            for (j in rebuttal_chunk_highlights) {
                if (rebuttal_chunk_highlights[j]) {
                    matches.push(j)
                }
            }
            if (matches.length == 0 && !isNoContextChecked(i, errors)) {

                alert("Please annotate rebuttal chunk " + (parseInt(i) + 1))
                return
            } else if (matches.length > 0 && isNoContextChecked(i, errors)) {

                alert("Conflicting annotations on rebuttal chunk " + (parseInt(i) + 1))
                return
            }
            alignments.push(matches)
        }

        result = {
            "alignments": alignments,
            "errors": errors,
            "review_sid": review_sid,
            "rebuttal_sid": rebuttal_sid,
            "annotator": document.getElementById("initials").value,
            "comment": document.getElementById("comments").value,
            "metadata": getJsonified("metadata"),
        }
        document.getElementById("annotation").value = JSON.stringify(result)
        alert("Good to go! Please review then submit")

    }
}

rebuttal_chunks = getJsonified("rebuttal_chunks");
review_sentences = getJsonified("review_sentences");
highlighted = new Array(rebuttal_chunks.length);

for (var i = 0; i < highlighted.length; i++) {
    highlighted[i] = new Array(review_sentences.length).fill(0);
}


function clicked(ele) {
    review_idx = parseInt(ele.attributes.review_idx.value);
    rebuttal_idx = parseInt(ele.attributes.rebuttal_idx.value);
    highlighted[rebuttal_idx][review_idx] = 1 - highlighted[rebuttal_idx][review_idx];
    if (highlighted[rebuttal_idx][review_idx]) {
        ele.style = "background-color:#d5f5e3"
    } else {
        ele.style = ""
    }
}
