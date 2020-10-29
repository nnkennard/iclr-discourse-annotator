// INITIALIZATIONS
switchTab(-1, 1, 1); // Display the first tab
document.getElementById("submitBtn").disabled = "true";
window.error_map = {
    "review_errors": Array(),
    "rebuttal_errors": Array()
}
CONTEXT_SPANS = {}



function switchTab(current_tab, total_tabs, direction) {
    new_tab = (current_tab + direction + total_tabs) % total_tabs;
    var tabs = document.getElementsByClassName("tab");
    if (current_tab > -1) {
        tabs.item(current_tab).style.display = "none";
    }
    tabs.item(new_tab).style.display = "block";
}

function isNoContextChecked(index){
    return document.getElementById("errors_" + index + "-3").checked
}
function getErrors(index){
    error_list = []
    for(var i=0;i<3;i++){
        console.log(index, i)
        if (document.getElementById("errors_" + index + "-" + i).checked){
            console.log("peep")
            error_list.push(document.getElementById("errors_" + index + "-" + i).value)
        }
    }
    return error_list.join("|")
}


function generateJson() {

    rebuttal_indices = JSON.parse(document.getElementById('reb_id').textContent);
    console.log(rebuttal_indices)

    if (document.getElementById('initials').value === "") {
        alert("Please fill in your initials and run finalize again.")
    } else {
        submitButton = document.getElementById("submitBtn");
        submitButton.removeAttribute("disabled");

        alignments = []

        for (var reb_idx_str in rebuttal_indices) {
            reb_idx = parseInt(reb_idx_str)
            orig_idx = parseInt(rebuttal_indices[reb_idx])
            error = getErrors(reb_idx_str)
            if (CONTEXT_SPANS.hasOwnProperty(reb_idx_str)) {
                if(isNoContextChecked(reb_idx)){
                    alert("Conflicting annotations on rebuttal chunk "+ (reb_idx + 1))
                    return
                } else {
                    console.log(reb_idx, " was not checked")
                value = CONTEXT_SPANS[reb_idx_str]
                alignments.push(Array([orig_idx, value[1], value[2], error]))
                }
            } else {
                if(isNoContextChecked(reb_idx)){
                    alignments.push(Array([orig_idx, -1, -1, error]))
                } else {
                   alert("Please annotate rebuttal chunk "+(reb_idx + 1))
                   return
                }
            }
        }
        result = {"alignments": alignments}
        document.getElementById("annotation").value = JSON.stringify(result)
        alert("Good to go! Please review then submit")

    }
}

function confirmSpan(index) {
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
        if (review_tokens.slice(i, i + selection_tokens.length).join(" ") === selection_tokens.join(" ")) {
            span_found = true;
            confirmSpanButton.disabled = false;
            highlightSpan.innerHTML = selectionText.fontcolor("green");
            document.getElementById("highlightedSpanStartIndex_" + rebuttal_chunk_idx).innerHTML = i
            document.getElementById("highlightedSpanEndIndex_" + rebuttal_chunk_idx).innerHTML = i + selection_tokens.length
            break;
        }
    }
    if (!span_found) {
        confirmSpanButton.disabled = true;
        highlightSpan.innerHTML = selectionText.fontcolor("red");
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