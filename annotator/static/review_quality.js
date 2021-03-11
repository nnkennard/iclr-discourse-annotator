function validate(){
	console.log(document.getElementById("metadata").textContent)
    radio_buttons = document.getElementsByClassName("radio");
    labels = Array()
    for (radio_button of radio_buttons){
        if (radio_button.checked){
            labels.push(radio_button.name+"|"+radio_button.value)
        }
    }
    if (labels.length < 8){
    	alert("Some labels are missing! Please complete and run Validate again.")
    	return
    }
    if (document.getElementById("initials").value.length == 0){
    	alert("Please add your initials and run Validate again.")
   		return
    }
    result = {
            "labels": labels,
            "annotator": document.getElementById("initials").value,
            "comment": document.getElementById("comments").value,
            "metadata": JSON.parse(document.getElementById("metadata").textContent),
        }
    document.getElementById("id_annotation").value = JSON.stringify(result)
}
