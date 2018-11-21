function delete_appointment(e) {
    var element = e;
    var t = element.children[0].children;

    var doctor_id = t[0].innerHTML;
    var date = t[1].innerHTML;
    var time = t[3].innerHTML;


    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/update_appointment?doctor_id=" + doctor_id + "&date=" + date + "&time=" + time, false);
    xhr.onreadystatechange = function() {
        if( this.readyState == 4 && this.status == 200 ) {
            var res = this.responseText;
            if(res == "no") {
                swal({
                    title: 'Oops',
                    text: 'Cannot cancel past appointments',
                    type: 'error'
                    }, function(){
                      console.log("here");
                    window.location.href = "/cancel_appointment";
                  });   
            } else {
                swal({
                    title: 'Successful',
                    text: 'Canceled your appointment',
                    type: 'success'
                    }, function(){
                      console.log("here");
                    window.location.href = "/cancel_appointment";
                  });   
            }
        } 
    }
    xhr.send();

    
    
}