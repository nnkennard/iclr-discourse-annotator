goToTab("tab:align:0")

rebuttal_sentences = getJsonified("rebuttal_sentences");
review_sentences = getJsonified("review_sentences");

highlighted = new Array(rebuttal_sentences.length);
for (var i = 0; i < highlighted.length; i++) {
    highlighted[i] = new Array(review_sentences.length).fill(0);
}

function switchTab() {
    console.log("y no switching")
    current_tab_name = document.getElementById("currentTab").innerText
    console.log(current_tab_name)
    if (current_tab_name.startsWith("tab:align")){
        goToTab(current_tab_name.replace("align", "label"))
    } else {
        goToTab(current_tab_name.replace("label", "align"))
    }
}

function goToTab(goto_tab_name) {
    current_tab_name = document.getElementById("currentTab").innerText
    console.log("Going to tab", current_tab_name, goto_tab_name)
    document.getElementById(current_tab_name).style.display = "none"
    document.getElementById(goto_tab_name).style.display = "block"
    document.getElementById("currentTab").innerText = goto_tab_name
}

function last(l){
    return l[l.length - 1]
}

function someHighlighted(rebuttal_index){
    return highlighted[rebuttal_index].reduce(function(a, b) { return a + b; }, 0) > 0
}

function validateAlignment(button_element){
    rebuttal_index = last(button_element.id.split("-"))
    radio_id = "align:radios-"+rebuttal_index

    if (document.getElementById(radio_id+"-3").checked){
        if(someHighlighted(rebuttal_index)){
            switchTab();
        } else {
            window.alert("You have indicated that sentences are highlighted, but none are highlighted. Please fix.")
        }
    } else {
        if(someHighlighted(rebuttal_index)){
            window.alert("You have highlighted sentences, but selected a 'no context' option as well. Please fix.")
        
        } else {
            switchTab();
            }
    }
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
        ele.style = "background-color:#d4efdf"
    } else {
        ele.style = ""
    }
    highlighted_sentences = ""
    for (i in highlighted[rebuttal_idx]){
        if(highlighted[rebuttal_idx][i]){
sentence_text = document.getElementById("sentence-"+rebuttal_idx+"-"+i).innerText;
        highlighted_sentences += "\n" + sentence_text;
        }
        
    }
    if(highlighted_sentences){
        highlighted_sentences = highlighted_sentences.substring(1);
    }
    document.getElementById('review-box-'+rebuttal_idx).innerText = highlighted_sentences
    document.getElementById('label-review-box-'+rebuttal_idx).innerText = highlighted_sentences

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

