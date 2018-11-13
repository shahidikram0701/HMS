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
    xhr2 = new XMLHttpRequest();
    // n = 1;
    function fetch_appointments(){
        console.log("fetch appointments")
        xhr.onreadystatechange = show_appointments;
        xhr.open("GET", "/update_appointments", true);
        xhr.send();
    }

    function show_appointments(){
        if(xhr.readyState == 4 && xhr.status == 200){
            //alert("results obtained!");
            // n = 1;
            var res = JSON.parse(xhr.responseText);
            add_to_appointments(res);
            console.log(res);
            setTimeout(fetch, 2000);
        }
    }

    function fetch_emergency(){
        console.log("fetch emergency")
        xhr2.onreadystatechange = show_emergency;
        xhr2.open("GET", "/update_emergency", true);
        xhr2.send();
    }

    function show_emergency(){
        if(xhr2.readyState == 4 && xhr2.status == 200){
            //alert("results obtained!");
            // n = 1;
            var res = JSON.parse(xhr2.responseText);
            add_to_inpatients(res);
            swal("EMERGENCY ARRIVED");
            console.log(res);
            setTimeout(fetch, 2000);
        }
    }

    fetch_appointments();
    fetch_emergency();
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

function add_to_inpatients(arr) {
    var tbody = document.getElementById("myPatient");
    for(var i = 0; i < arr.length; ++i) {
        var s = `<tr onclick="handle_inpatients(this)">
            <td>${arr[i]["patient_id"]}</td>
            <td>${arr[i]["patient_name"]}</td>
            <td>${arr[i]["date"]}</td>
            <td>${arr[i]["time"]}</td>
            <td>${arr[i]["nurse_id"]}</td>
            <td>${arr[i]["nurse_name"]}</td>
            <td>${arr[i]["ward_number"]}</td>
        </tr>`
        tbody.innerHTML += s;
    }
}

function handle_inpatients(e) {
    patient_id = e.children[0].innerHTML;
    patient_name = e.children[1].innerHTML;
    date = e.children[2].innerHTML;
    time = e.children[3].innerHTML;
    nurse_id = e.children[4].innerHTML;
    nurse_name = e.children[5].innerHTML;
    ward_icu_number = e.children[6].innerHTML;

    // console.log(patient_id);
    // console.log(patient_name);
    // console.log(date);
    // console.log(time);
    // console.log(nurse_id);
    // console.log(nurse_name);
    // console.log(ward_icu_number);
    swal({
        title: "What next?",
        text: "1. Discharge\n 2. Shift to ward\n 3.Shift to ICU\n",
        type: "input",
        showCancelButton: true,
        closeOnConfirm: false,
        inputPlaceholder: "Select an option"
    }, function (inputValue) {
        if (inputValue === false) return false;
        if (inputValue === "") {
        swal.showInputError("Pls select an option!!");
        return false
        }
        if(inputValue === "1") {
            $.ajax({
                type: "GET",
                url: "/discharge?patient_id=" + patient_id + "&nurse_id=" + nurse_id + "&ward_icu_number=" + ward_icu_number 
            }).done(function(o) {
                swal({
                    title: 'Successful',
                    text: 'Discharged',
                    type: 'success'
                    }, function(){
                      console.log("success");
                      window.location.href = "/home";    
                }); 
            });  
        }
        else if(inputValue === "2") {
            $.ajax({
                type: "GET",
                url: "/to_ward?patient_id=" + patient_id + "&nurse_id=" + nurse_id + "&ward_icu_number=" + ward_icu_number 
            }).done(function(o) {
                if(o == "no_wards_free") {
                    var type_ = "error";
                    var title_ = "Oops";
                }
                else {
                    var type_ = "success";
                    var title_ = "Successful";
                }
                swal({
                    title: title_,
                    text: o,
                    type: type_
                    }, function(){
                      console.log("success");
                      window.location.href = "/home";    
                }); 
            });   
        }
        else if(inputValue === "3") {
            $.ajax({
                type: "GET",
                url: "/to_icu?patient_id=" + patient_id + "&nurse_id=" + nurse_id + "&ward_icu_number=" + ward_icu_number 
            }).done(function(o) {
                if(o == "no_icu_free") {
                    var type_ = "error";
                    var title_ = "Oops";
                }
                else {
                    var type_ = "success";
                    var title_ = "Successful";
                }
                swal({
                    title: title_,
                    text: o,
                    type: type_
                    }, function(){
                      console.log("success");
                      window.location.href = "/home";    
                }); 
            });   
        }
        else {
            swal({
                title: 'Error',
                text: 'Invalid option',
                type: 'error'
                }, function(){
                  console.log("error");
                  //window.location.href = "/cancel_appointment";
              });   
        }
        
    });
  
  
}