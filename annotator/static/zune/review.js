document.getElementById("submitBtn").disabled = "true"

function getJsonified(label) {
    return JSON.parse(document.getElementById(label).textContent)
}

const start_time = Date.now();

function getElapsedTime(){
    return Math.floor(Date.now() - start_time / 1000);
}

num_review_sentences = getJsonified("num_review_sentences");
metadata = getJsonified("metadata");

function last(l) {
    return l[l.length - 1];
}

function addArg(clickedButton) {
    sentence_index = last(clickedButton.id.split("-"))
    document.getElementById("arg-1-" + sentence_index).style = "display:block"
    document.getElementById("gro-1-" + sentence_index).style = "display:block"
    clickedButton.style = "display:none"

}

function revealItem(original_dropdown, key){
    document.getElementById(original_dropdown.id.replace("arg-d", key)).style="display:block"
}

function concealItem(original_dropdown, key){
    document.getElementById(original_dropdown.id.replace("arg-d", key)).style="display:none"
}


function strucChange(dropdown){
    if (dropdown.value == "Summary") {
        document.getElementById(dropdown.id.replace("struc", "gro")).value = "Whole manuscript"
    }
}


menu_map = getJsonified("menu_map")
all_menus = ["arg", "asp", "pol", "gro", "fine", "struc"]
full_menu_name_map = {
    "arg": "Argument",
    "asp": "Aspect",
    "pol": "Polarity",
    "gro": "Grounding",
    "fine": "Fine-grained request type",
    "struc": "Fine-grained structuring type",
}

function argChange(argDropdown) {
    val = argDropdown.value
    for (menu of all_menus) {
        if (menu == "arg" || menu == "gro"){
            continue;
        }
        if (menu_map[val]["required"].includes(menu) || menu_map[val]["allowed"].includes(menu)){
            revealItem(argDropdown, menu)
        } else {
            concealItem(argDropdown, menu)
        }
    }
}

function validateArgument(sentence_index, argument_index){
    labels = {}
    arg_value = document.getElementById("arg-d-" + argument_index + "-" + sentence_index).value
    for (menu of menu_map[arg_value]["required"]){
        if (menu == "arg"){
            continue
        }
        menu_value = document.getElementById(menu + "-d-" + argument_index + "-" + sentence_index).value
        if (menu_value.startsWith("--")) {
            alert("Please add " + full_menu_name_map[menu] + " for sentence " + sentence_index + "(argument " + argument_index +")")
            return null
        }
    }
    for (menu of [].concat(menu_map[arg_value]["required"], menu_map[arg_value]["allowed"])){
        menu_value = document.getElementById(menu + "-d-" + argument_index + "-" + sentence_index).value
        if (!menu_value.startsWith("--")) {
            labels[menu] = menu_value
        }
    }
    console.log(labels)
    return labels
}

function validateAll() {
    all_labels = {}
    arguments_to_validate = Array()
    for (i of Array(num_review_sentences).keys()) {
        for (bla of ["0", "1"]){
            arg_value = document.getElementById("arg-d-" + bla + "-" +i.toString()).value
            if (!arg_value.startsWith("--")){
                res = validateArgument(i.toString(), bla)
                if (res == null){
                    return
                } else {
                    all_labels[i.toString() + "-" + bla] = res
                }
            } else if (bla == "0"){
                alert("Please enter an argument value for sentence " + (i + 1).toString())
                return
            }
        }
    }
    seconds = getElapsedTime();
    result = {
        "metadata": metadata,
        "comments": document.getElementById("comments").value,
        "labels": all_labels,
        "time_to_annotate": seconds,
        "start_time": start_time,
    }
    document.getElementById("id_annotation").value = JSON.stringify(result)
    document.getElementById("submitBtn").removeAttribute("disabled");
}