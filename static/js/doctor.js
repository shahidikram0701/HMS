function select(e) {
    //alert("selected");
    console.log(e);
    time = e.children[0].innerHTML;
    patient_id = e.children[1].innerHTML;
    patient_name = e.children[2].innerHTML;
    details = e.children[3].innerHTML;
    console.log(time);
    console.log(patient_id);
    console.log(patient_name);
    console.log(details);
    window.location.href = "/doctor_patient?time=" + time + "&patient_id=" + patient_id + "&patient_name=" + patient_name + "&details=" + details; 
}

function init() {
    xhr = new XMLHttpRequest();
    // n = 1;
    function fetch(){
        console.log("fetch")
        xhr.onreadystatechange = show;
        // xhr.timeout = 8000;
        // xhr.ontimeout = backoff;
        xhr.open("GET", "/update_appointments", true);
        xhr.send();
    }

    function show(){
        if(xhr.readyState == 4 && xhr.status == 200){
            //alert("results obtained!");
            // n = 1;
            var res = JSON.parse(xhr.responseText);
            add_to_appointments(res);
            console.log(res);
            setTimeout(fetch, 2000);
        }
    }
    // function backoff(){
    //     console.log('backoff')
    //     console.log(n*500)
    //     setTimeout(fetch, (n * 500));
    //     n = n * 2;
    //     //console.log(n);	
    // }
    fetch();
}

function add_to_appointments(arr) {
    var tbody = document.getElementById("myAppt");
    for(var i = 0; i < arr.length; ++i) {
        for(var time in arr[i]) {
            var s = `<tr onclick="select(this)">
                <td>${time}</td>
                <td>${arr[i][time]["patient_id"]}</td>
                <td>${arr[i][time]["patient_name"]}</td>
                <td>${arr[i][time]["details"]}</td>
            </tr>`
            tbody.innerHTML += s;
        }
    }
}
