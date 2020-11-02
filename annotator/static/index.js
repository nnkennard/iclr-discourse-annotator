// INITIALIZATIONS
switchTab(-1, 1, 1); // Display the first tab
document.getElementById("submitBtn").disabled = "true"
CONTEXT_SPANS = {}


function switchTab(current_tab, total_tabs, direction) {
    new_tab = (current_tab + direction + total_tabs) % total_tabs;
    var tabs = document.getElementsByClassName("tab");
    if (current_tab > -1) {
        tabs.item(current_tab).style.display = "none";
    }
    tabs.item(new_tab).style.display = "block";
}

function isNoContextChecked(index, errors){
    return errors[index].includes("no_context")
}

function getErrors(rebuttal_indices){
    checkboxes = document.getElementsByName('checkboxes');
    errors = {}
    console.log("Reb id ", rebuttal_indices)
    for (var i=0; i<rebuttal_indices.length; i++){
        console.log("***", i)
        errors[i] = Array();
    }
    console.log("Errors ", errors)
    for (checkbox of checkboxes) {
        if (checkbox.checked){
            parts = checkbox.id.split("-")
            errors[parseInt(parts[1])].push(parts[2])
        }
    }
    return errors
}

function getJsonified(label){
    return JSON.parse(document.getElementById(label).textContent)
}


function generateJson() {

    rebuttal_indices = getJsonified("reb_id");
    rebuttal_sid = getJsonified("rebuttal");
    review_sid = getJsonified("review");

    if (document.getElementById('initials').value === "") {
        alert("Please fill in your initials and run Validate again.")
    } else {
        submitButton = document.getElementById("submitBtn");
        submitButton.removeAttribute("disabled");

        errors = getErrors(rebuttal_indices)

        alignments = []

        for (var reb_idx_str in rebuttal_indices) {
            reb_idx = parseInt(reb_idx_str)
            console.log("Checking rebuttal index ", reb_idx)
            orig_idx = parseInt(rebuttal_indices[reb_idx])
            if (CONTEXT_SPANS.hasOwnProperty(reb_idx_str)) {
                if(isNoContextChecked(reb_idx, errors)){
                    alert("Conflicting annotations on rebuttal chunk "+ (reb_idx + 1))
                    return
                } else {
                value = CONTEXT_SPANS[reb_idx_str]
                alignments.push([orig_idx, value[1], value[2]])
                }
            } else {
                if(isNoContextChecked(reb_idx, errors)){
                    alignments.push([orig_idx, -1, -1])
                } else {
                   alert("Please annotate rebuttal chunk "+(reb_idx + 1))
                   return
                }
            }
        }
        alert(alignments)
        result = {"alignments": alignments,
                  "errors": errors,
                  "review_sid": review_sid,
                  "rebuttal_sid": rebuttal_sid,
                  "annotator": document.getElementById("initials").textContent,
              }
        document.getElementById("annotation").value = JSON.stringify(result)
        alert("Good to go! Please review then submit")

    }
}

function confirmSpan(index) {
    var inputs = document.getElementsByName('checkboxes');
    confirmedSpan = document.getElementById("contextSpan_" + index);
    spanText = document.getElementById("highlightedSpan_" + index)
    confirmedSpan.innerHTML = spanText.innerHTML;
    CONTEXT_SPANS[index] = [spanText.textContent,
        parseInt(document.getElementById("highlightedSpanStartIndex_" + index).innerHTML),
        parseInt(document.getElementById("highlightedSpanEndIndex_" + index).innerHTML)
    ]
}


function consumeSelection(rebuttal_chunk_idx) {
    selectionText = window.getSelection().toString()
    selection_tokens = selectionText.trim().split(/[\s]+/)
    confirmSpanButton = document.getElementById("confirmSpanButton_" + rebuttal_chunk_idx)
    highlightSpan = document.getElementById("highlightedSpan_" + rebuttal_chunk_idx)
    review_tokens = document.getElementById("reviewtablecell_0").innerHTML.replace(/\<br\>/g, " ").trim().split(/[\s]+/) // This is actually the same text for any rebuttal chunk...
    span_found = false;
    for (var i = 0; i <= review_tokens.length - selection_tokens.length; i++) {
        console.log(i, review_tokens[i])
        if (review_tokens.slice(i, i + selection_tokens.length).join(" ") === selection_tokens.join(" ")) {
            span_found = true;
            confirmSpanButton.disabled = false;
            highlightSpan.innerHTML = selectionText.fontcolor("#82e0aa");
            document.getElementById("highlightedSpanStartIndex_" + rebuttal_chunk_idx).innerHTML = i
            document.getElementById("highlightedSpanEndIndex_" + rebuttal_chunk_idx).innerHTML = i + selection_tokens.length
            break;
        }
    }
    if (!span_found) {
        confirmSpanButton.disabled = true;
        highlightSpan.innerHTML = selectionText.fontcolor("#f1948a");
    }

}


function updateNoContext(index){
    if (isNoContextChecked(index)) {
        document.getElementById("contextSpan_" + index).innerHTML = "No context available".fontcolor("red");
        delete CONTEXT_SPANS[index]
    } else {
        document.getElementById("contextSpan_" + index).innerHTML = "No span confirmed -- please select a span on the left."
    }

}
