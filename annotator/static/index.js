// INITIALIZATIONS
switchTab(-1, 1, 1); // Display the first tab
document.getElementById("submitBtn").disabled = "true"

// In ids, both rebuttal chunk and review chunk are 0-indexed

rebuttal_chunks = getJsonified("rebuttal_chunks");
review_sentences = getJsonified("review_sentences");
TOTAL_TABS = rebuttal_chunks.length
num_nonempty_review_sentences = 0
for (sentence of review_sentences){
    if (sentence.idx > -1){
        num_nonempty_review_sentences += 1
    }
}
highlighted = new Array(rebuttal_chunks.length);
for (var i = 0; i < highlighted.length; i++) {
    highlighted[i] = new Array(num_nonempty_review_sentences).fill(0);
}

function switchTab(current_tab, total_tabs, direction) {
    new_tab = (current_tab + direction + total_tabs) % total_tabs;
    var tabs = document.getElementsByClassName("tab");
    if (current_tab > -1) {
        tabs.item(current_tab).style.display = "none";
    }
    tabs.item(new_tab).style.display = "block";
    document.getElementById("currentTab").innerHtml = new_tab
}

function contextNotRequired(index, errors) {
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
            // e.g. "errors-0-signpost"
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
            if (matches.length == 0 && !contextNotRequired(i, errors)) {
                alert("Please annotate rebuttal chunk " + (parseInt(i) + 1))
                return
            } else if (matches.length > 0 && contextNotRequired(i, errors)) {
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


function clicked(ele) {
    // e.g. "sentence-1-2" for rebuttal index 1 and review index 2
    parts = ele.id.split("-")
    review_idx = parseInt(parts[2]);
    rebuttal_idx = parseInt(parts[1]);
    highlighted[rebuttal_idx][review_idx] = 1 - highlighted[rebuttal_idx][review_idx];
    if (highlighted[rebuttal_idx][review_idx]) {
        ele.style = "background-color:#d5f5e3"
    } else {
        ele.style = ""
    }
}

function copyPrevious(chunk_idx_str){
    chunk_idx = parseInt(chunk_idx_str)
    checkbox_container = document.getElementById("checkbox-container-"+chunk_idx_str)
    // Clear errors
    for (row of checkbox_container.children){
        if (row.className != "row") {
            continue
        }
        row.children[0].children[0].children[0].children[0].checked = false
    }

    // Copy errors
    rebuttal_chunks = getJsonified("rebuttal_chunks");
    errors = getErrors(rebuttal_chunks)
    previous_errors = errors[chunk_idx - 1]
    for (error_code of previous_errors) {
        checkbox_id = "errors-" + chunk_idx_str + "-" + error_code
        document.getElementById(checkbox_id).checked = true
    }

    review_sentences = getJsonified("review_sentences");
    highlighted[chunk_idx] = highlighted[chunk_idx - 1]
    for (i in highlighted[chunk_idx]){
        sentence = highlighted[chunk_idx][i]
        sentence_element = document.getElementById("sentence-"+chunk_idx+"-"+i)
        if (sentence){
            sentence_element.style = "background-color:#d5f5e3"
        } else {
            sentence_element.style = ""
        }
    }
}

document.onkeydown = checkKey;

function checkKey(e) {

    current_tab = parseInt(document.getElementById("currentTab").innerHtml)

    e = e || window.event;

    if (e.keyCode == '37') {
       switchTab(current_tab, TOTAL_TABS, -1); 
    }
    else if (e.keyCode == '39') {
       switchTab(current_tab, TOTAL_TABS, 1); 
    }

}

