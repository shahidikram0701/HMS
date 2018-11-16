function init() {
    xhr2 = new XMLHttpRequest(); // for checking if a new emergency is arrived
   
    function fetch_emergency(){
        console.log("fetch emergency")
        xhr2.onreadystatechange = show_emergency;
        xhr2.open("GET", "/update_emergency", true);
        xhr2.send();
    }

    function show_emergency(){
        if(this.readyState == 4 && this.status == 200){
            //alert("results obtained!");
            // n = 1;
            var res = JSON.parse(this.responseText);
            // add_to_inpatients(res);
            swal({
                title: "EMERGENCY Arrived",
                text: "An Emergency case: " + res[0]["patient_id"] + " requires your presence!",
                type: "warning"
                }, function(){
                  console.log("accept emergency");
                  window.location.href = "\home";    
            });
            console.log(res);
            setTimeout(fetch_emergency, 2000);
        }
    }
   fetch_emergency();
}