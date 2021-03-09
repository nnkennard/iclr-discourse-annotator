goToTab("tab:align:0")
document.getElementById("submitBtn").disabled = "true"

rebuttal_sentences = getJsonified("rebuttal_sentences");
review_sentences = getJsonified("review_sentences");
metadata = getJsonified("metadata");

highlighted = new Array(rebuttal_sentences.length);
for (var i = 0; i < highlighted.length; i++) {
    highlighted[i] = new Array(review_sentences.length).fill(0);
}

for (var i = 0; i < highlighted.length; i++) {
    console.log(i, highlighted[i])
}



done = new Array(rebuttal_sentences.length).fill(0);

function switchTab() {
    current_tab_name = document.getElementById("currentTab").innerText
    console.log(current_tab_name)
    if (current_tab_name.startsWith("tab:align")){
        goToTab(current_tab_name.replace("align", "label"))
    } else {
        goToTab(current_tab_name.replace("label", "align"))
    }
}

function navSwitch(button_element){
    goToTab(button_element.id.replace("nav", "tab:align"))
}

function goToTab(goto_tab_name) {
    current_tab_name = document.getElementById("currentTab").innerText
    document.getElementById(current_tab_name).style.display = "none"
    document.getElementById(goto_tab_name).style.display = "block"
    document.getElementById("currentTab").innerText = goto_tab_name
    navButtonToggle(current_tab_name, goto_tab_name)
    
}

function navButtonToggle(old_tab_name, new_tab_name){
    old_button = document.getElementById("nav:" + old_tab_name.substring(10))
    new_button = document.getElementById("nav:" + new_tab_name.substring(10))
    if (old_button.classList.contains("is-active")){
        old_button.classList.remove("is-active")
    }
    new_button.classList.add("is-active")
}

function last(l){
    return l[l.length - 1]
}

function sum(l){
    return l.reduce(function(a, b) { return parseInt(a) + parseInt(b); }, 0)

}

function someHighlighted(rebuttal_index){
    return sum(highlighted[rebuttal_index]) > 0
}

function isAllDone(){
    console.log(sum(done), done.length)
    return sum(done) == done.length
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


function validateLabel(button_element){
    rebuttal_index = last(button_element.id.split("-"))
    radio_id = "label:radios-"+rebuttal_index

    console.log(document.getElementById("label:info-" + rebuttal_index).innerText)

    if (
        document.getElementById(radio_id+"-13").checked 
        && document.getElementById("label:info-" + rebuttal_index).value.trim() == 0){
            window.alert("Please specify why none of the options apply")
    } else {
        // Validate for this rebuttal sentence
        window.alert("Good to go, please proceed to next rebuttal sentence.")
        markDone(rebuttal_index)

    }
}



function getJsonified(label) {
    return JSON.parse(document.getElementById(label).textContent)
}

function getErrors(){
    radio_buttons = document.getElementsByClassName("radio");
    labels = Array()
    for (radio_button of radio_buttons){
        if (radio_button.checked){
            labels.push(radio_button.name+"|"+radio_button.value)
        }
    }
    return labels
}



function validateAll() {

    if (document.getElementById('initials').value === "") {
        alert("Please fill in your initials and run Validate again.")
    } else if (!isAllDone()) {
        alert("Some annotations are not done. Please check for nav buttons that are not green to find them and complete them.")
    } else {
        document.getElementById("submitBtn").removeAttribute("disabled");
        errors = getErrors()
        result = {
            "highlighted": highlighted,
            "errors": errors,
            "annotator": document.getElementById("initials").value,
            "comment": document.getElementById("comments").value,
            "metadata": metadata,
        }
        document.getElementById("id_annotation").value = JSON.stringify(result)
        alert("Good to go! Please review then submit")


    }
}

function populatePreviewBoxes(rebuttal_index_int){
    highlighted_sentences = ""
    for (i in highlighted[rebuttal_index_int]){
        if(highlighted[rebuttal_index_int][i]){
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

function markDone(rebuttal_index){
    button = document.getElementById("nav:" + rebuttal_index)
    button.classList.add("is-success")
    done[parseInt(rebuttal_index)] = 1
}

function markNotDone(rebuttal_index){
    button = document.getElementById("nav:" + rebuttal_index)
    if (button.classList.contains("is-success")){
        button.classList.remove("is-success")
    }
    done[parseInt(rebuttal_idx)] = 0
}


function clicked(ele) {
    // e.g. "sentence-1-2" for rebuttal index 1 and review index 2
    parts = ele.id.split("-")
    review_idx = parseInt(parts[2]);
    rebuttal_idx = parseInt(parts[1]);
    markNotDone(parts[1])
    highlighted[rebuttal_idx][review_idx] = 1 - highlighted[rebuttal_idx][review_idx];
    if (highlighted[rebuttal_idx][review_idx]) {
        ele.style = "background-color:#d4efdf"
    } else {
        ele.style = ""
    }
    populatePreviewBoxes(rebuttal_idx)
    
}

function copyPrevious(copy_btn){
    rebuttal_index = last(copy_btn.id.split("-"))
    console.log("rebuttal index", rebuttal_index)
    rebuttal_index_int = parseInt(rebuttal_index)

    highlighted[rebuttal_index_int] = highlighted[rebuttal_index_int - 1]
    for (i in highlighted[rebuttal_index_int]){
        sentence_element = document.getElementById("sentence-"+rebuttal_index+"-"+i)
        if (highlighted[rebuttal_index_int][i] == 1){
            sentence_element.style = "background-color:#d5f5e3"
        } else {
            sentence_element.style = ""
        }
    }
    populatePreviewBoxes(rebuttal_index_int)
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

