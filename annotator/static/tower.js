// Initialization
document.getElementById("submitBtn").disabled = "true"
document.getElementById("initials").value = getUrlVars().initials
// Utils

function last(l){
    return l[l.length - 1]
}

function sum(l){
    return l.reduce(function(a, b) { return parseInt(a) + parseInt(b); }, 0)

}

function getJsonified(label) {
    return JSON.parse(document.getElementById(label).textContent)
}


function getUrlVars() {
    var vars = {};
    var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi,    
    function(m,key,value) {
      vars[key] = value;
    });
    return vars;
  }

function switchRebuttalPage(new_index) {
    parts = window.location.href.split("/")
    new_url = parts.slice(0,5).join("/") + "/" + new_index + "/" + parts.slice(6)
    window.location.replace(new_url)
}



// Global vars

review_sentences = getJsonified("review_sentences");
metadata = getJsonified("metadata");
num_rebuttal_sentences = metadata["rebuttal_statuses"].length
document.getElementById("nav:" + metadata["rebuttal_index"].toString()).classList.add("is-active")

highlighted = new Array(review_sentences.length).fill(0);
new Array(review_sentences.length).fill(0);

is_done = metadata["rebuttal_statuses"][metadata["rebuttal_index"]]

// Tab switching


function navSwitch(button_element){
    switchRebuttalPage(last(button_element.id.split(":")))
}

function goToTab(goto_tab_name) {
    current_tab_name = document.getElementById("currentTab").innerText
    document.getElementById(current_tab_name).style.display = "none"
    document.getElementById(goto_tab_name).style.display = "block"
    document.getElementById("currentTab").innerText = goto_tab_name
    navButtonToggle(current_tab_name, goto_tab_name)
    
}


function toggleModal(){
    modal = document.getElementById("rebuttalmodal")
    if (modal.classList.contains("is-active")){
        modal.classList.remove("is-active")
    } else{
        modal.classList.add("is-active")
    }
}


// Validation

function validate(){
    // Is an alignment required? If so, given?
    // Is an explanation required? If so, given?


}


function someHighlighted(rebuttal_index){
    return sum(highlighted[rebuttal_index]) > 0
}

function validateAlignment(button_element){
    rebuttal_index = last(button_element.id.split(":"))
    radio_id = "align:radios:"+rebuttal_index

    if (document.getElementById(radio_id+":3").checked){
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
    rebuttal_index = last(button_element.id.split(":"))
    radio_id = "label:radios:"+rebuttal_index
    if (
        document.getElementById(radio_id+":14").checked 
        && document.getElementById("label:info:" + rebuttal_index).value.trim() == 0){
            window.alert("Please specify why none of the options apply")
    } else {
        // Validate for this rebuttal sentence
        window.alert("Good to go, please proceed to next rebuttal sentence.")
        markDone(rebuttal_index)

    }
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

function populatePreviewBoxes(){
    highlighted_sentences = ""
    for (i in highlighted){
        if(highlighted[i]){
sentence_text = document.getElementById("sentence:"+i).innerText;
        highlighted_sentences += "\n" + sentence_text;
        }
        
    }
    if(highlighted_sentences){
        highlighted_sentences = highlighted_sentences.substring(1);
    }
    console.log(highlighted_sentences)
    document.getElementById('reviewbox').innerText = highlighted_sentences
    flashElement('reviewbox')
}

function flashElement(id){
    document.getElementById(id).style="display:none"
    document.getElementById(id).style="display:block"
}

function clicked(ele) {
    // e.g. "sentence:1:2" for rebuttal index 1 and review index 2
    review_idx = parseInt(last(ele.id.split(":")));
    is_done = false
    highlighted[review_idx] = 1 - highlighted[review_idx];
    if (highlighted[review_idx]) {
        ele.style = "background-color:#d4efdf"
    } else {
        ele.style = ""
    }
    populatePreviewBoxes()
    
}

function copyPrevious(copy_btn){
    rebuttal_index = parseInt(last(copy_btn.id.split(":")))
    console.log("Rebuttal index", rebuttal_index, " ", copy_btn.id)

    if (rebuttal_index == 0){
        return
    }

    highlighted[rebuttal_index] = highlighted[rebuttal_index - 1]
    for (i in highlighted[rebuttal_index]){
        console.log(i,highlighted[rebuttal_index][i])
        sentence_element = document.getElementById("sentence:"+rebuttal_index+":"+i)
        if (highlighted[rebuttal_index][i] == 1){
            sentence_element.style = "background-color:#d5f5e3"
        } else {
            sentence_element.style = ""
        }
    }
    populatePreviewBoxes()
}


// Keyboard navigation

document.onkeydown = checkKey;


function selectRelation(keycode, index){
    element = "label:radios:" + index.toString() + ":9"
    document.getElementById(element).checked = true; 
 }

function checkKey(e) {

    index = metadata["rebuttal_index"]

    e = e || window.event;

    if (e.key == 'ArrowLeft') {
       new_tab_index = index -1;
    }
    else if (e.key == 'ArrowRight') {
      new_tab_index = index + 1
    } else {
        selectRelation(e.keyCode, index)
        return
    }

    console.log(new_tab_index)

    new_tab_name = ((new_tab_index + num_rebuttal_sentences) % num_rebuttal_sentences).toString()
    console.log("new name ", new_tab_name)
    switchRebuttalPage(new_tab_name)

}

function rowClicked(row_element) {
    relevant_radio_name = row_element.id.replace("tablerow", "label:radios")
    document.getElementById(relevant_radio_name).checked=true
}