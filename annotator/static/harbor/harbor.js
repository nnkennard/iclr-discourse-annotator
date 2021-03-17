
function getJsonified(label) {
    return JSON.parse(document.getElementById(label).textContent)
}

function validate(){
    radio_buttons = document.getElementsByClassName("radio");
    ratings = {}
    for (radio_button of radio_buttons){
        if (radio_button.checked){
            ratings[radio_button.name] = radio_button.value
        }
    }
    if (ratings.length < getJsonified("num_questions")){
    	alert("Some labels are missing! Please complete and run Validate again.")
    	return
    }
    result = {
            "review_id": getJsonified("review_id"),
            "ratings": JSON.stringify(ratings),
            "annotator": getJsonified("annotator_initials"),
            "comment": document.getElementById("comments").value,
        }
    document.getElementById("id_annotation").value = JSON.stringify(result)
}
