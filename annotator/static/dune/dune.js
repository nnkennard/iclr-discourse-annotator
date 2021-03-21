STATUSES = ["NOT_STARTED", "STARTED", "VALIDATED"] // Change to not started if clicked sentence clicked any radio button, entered text

CURRENT_STATUS = "NOT_STARTED"

// Grabbing things from page
review_sentences = getJsonified("review_sentences");
other_annotations = getJsonified("other_annotations");
metadata = getJsonified("metadata");
num_rebuttal_sentences = getJsonified("num_rebuttal_sentences");


// Not started, started, confirmed
page_status = "not_started"

// Initialization
document.getElementById("submitBtn").disabled = "true"
document.getElementById("nav:" + metadata["rebuttal_index"].toString()).classList.add("is-active")
const start = Date.now();
var highlighted = new Array(review_sentences.length).fill(0);
maybeDisableCopyPrevious()

function getElapsedTime(){
    return Math.floor(Date.now() - start / 1000);
}

function last(l){
    return l[l.length - 1];
}

function sum(l){
    return l.reduce(function(a, b) { return parseInt(a) + parseInt(b); }, 0)

}

function getJsonified(label) {
    return JSON.parse(document.getElementById(label).textContent)
}


// Navigation

function switchRebuttalPage(new_index) {
    parts = window.location.href.split("/")
    new_url = parts.slice(0,7).join("/") + "/" + new_index + "/" + parts.slice(8)
    window.location.replace(new_url)
}


function navSwitch(button_element){
    switchRebuttalPage(last(button_element.id.split(":")))
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

function maybeDisableCopyPrevious() {
    if (metadata.rebuttal_index == 0 || other_annotations.statuses[metadata.rebuttal_index - 1] == "Incomplete") {
        document.getElementById("copyBtn").disabled = true;
    }
    for(i in other_annotations.statuses){
        if(other_annotations.statuses[i]){
            document.getElementById("nav:"+i.toString()).classList.add("is-success")
        }
    }
}

function isSentencesAreAlignedChecked(){
  return document.getElementById("align:radios:some-align").checked
}

function needsExplanationButDoesntHave(){
  return (document.getElementById("label:radios:nota").checked
        && document.getElementById("comments").value.trim() == 0)
}

function someHighlighted(){
    return sum(highlighted) > 0
}

function getRadios(){
    radio_buttons = document.getElementsByClassName("radio");
    labels = {}
        for (radio_button of radio_buttons){
        if (radio_button.checked){
            labels[radio_button.name] = radio_button.value;
        }
    }
    return labels
}

function validateAll(){


  labels = getRadios();
  console.log(labels)
  
  if (!('align:radios' in labels)){
    window.alert("Please select one of the alignment radio buttons.")
  } else if (!('label:radios' in labels)){
    window.alert("Please select one of the relation radio buttons.")
  } else if (isSentencesAreAlignedChecked() && !someHighlighted()) {
    window.alert("You have indicated that sentences are highlighted, but none are highlighted. Please fix.")
  } else if (!isSentencesAreAlignedChecked() && someHighlighted()){
    window.alert("You have highlighted sentences, but selected a 'no context' option as well. Please fix.")
  } else if (needsExplanationButDoesntHave()) {
    window.alert("Please specify why none of the label options apply")
  } else {
        document.getElementById("submitBtn").removeAttribute("disabled");
        seconds = getElapsedTime();
        labels = getRadios()
        result = {
            "alignment_labels": highlighted,
            "alignment_errors": labels["align:radios"],
            "relation_label": labels["label:radios"],
            "comment": document.getElementById("comments").value,
            "metadata": metadata,
            "num_rebuttal_sentences": num_rebuttal_sentences,
            "time_to_annotate":seconds,
        }
        console.log(result)
        document.getElementById("id_annotation").value = JSON.stringify(result)
        alert("Good to go! Please review then submit")
        CURRENT_STATUS = "VALIDATED"
  }
}


// Label propagation

function populatePreviewBox(){
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
    reviewbox = document.getElementById('reviewbox')
    reviewbox.innerText = highlighted_sentences
    reviewbox.style="display:none"
    reviewbox.style="display:inline"
}


function copyPrevious(){
    rebuttal_index = metadata["rebuttal_index"]
    if (other_annotations.previous_alignment.length > 0) {
        highlighted = new Array(review_sentences.length).fill(0);
        for (index_str of other_annotations.previous_alignment.split("|")){
          highlighted[parseInt(index_str)] = 1
        }
    } else {
      alert("No annotations available for the previous sentence.")
    }
    for (i in highlighted){
        sentence_element = document.getElementById("sentence:"+i)
        if (highlighted[i] == 1){
            sentence_element.style = "background-color:#d5f5e3"
        } else {
            sentence_element.style = ""
        }
    }
    populatePreviewBox()
}


// Interaction management

function clicked(ele) {
    review_idx = parseInt(last(ele.id.split(":")));
    highlighted[review_idx] = 1 - highlighted[review_idx];
    if (highlighted[review_idx]) {
        ele.style = "background-color:#d4efdf"
    } else {
        ele.style = ""
    }
    CURRENT_STATUS = "STARTED"
    populatePreviewBox()
}

document.onkeydown = checkKey;


function checkKey(e) {

    index = metadata["rebuttal_index"]

    e = e || window.event;

    if (e.key == 'ArrowLeft') {
       new_tab_index = index -1;
    }
    else if (e.key == 'ArrowRight') {
      new_tab_index = index + 1
    } else {
        return
    }

    new_tab_name = ((new_tab_index + num_rebuttal_sentences) % num_rebuttal_sentences).toString()
    switchRebuttalPage(new_tab_name)

}

function rowClicked(row_element) {
    relevant_radio_name = row_element.id.replace("tablerow", "label:radios")
    document.getElementById(relevant_radio_name).checked=true
}

window.addEventListener('beforeunload', function(e) {
  //var myPageIsDirty = ...; //you implement this logic...
  if(CURRENT_STATUS == "STARTED") {
    //following two lines will cause the browser to ask the user if they
    //want to leave. The text of this dialog is controlled by the browser.
    e.preventDefault(); //per the standard
    e.returnValue = ''; //required for Chrome
  }
});

