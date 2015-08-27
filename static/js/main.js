function send() {
        
        $('#title').html('<h3>Authorizing...</h3>');

        $.ajax({
              type: "GET",
              contentType: "application/json; charset=utf-8",
              url: "/authorize",
              data: JSON.stringify(datas),
              success: function (data) {
                console.log("Authorizing");
                $('#title').html('');
                if(!data['success']){
                  window.open(data["url"]);
                }
              },
              dataType: "json",
              error: function (xhr, ajaxOptions, thrownError) {
                   $('#title').html('<h3>Ooopps, got an error...</h3>');
                   console.log(xhr.status);
                   console.log(xhr.responseText);
                   console.log(thrownError);
              }
        });

        var datas = {
            classInfo: [],
            school:"",
            reminders:[],
        };

        for(var i=1;i<=input;i++){
            if($("#subjectNumber"+i).val()!==""&&$("#courseNumber"+i).val()!==""&&$("#sectionNumber"+i).val()!==""){
                datas['classInfo'].push({subNum:$("#subjectNumber"+i).val(),courseNum:$("#courseNumber"+i).val(),sectionNum:$("#sectionNumber"+i).val(),});
            }  
        }
        for(var i=1;i<=4;i++){
            datas['reminders'].push($("#reminder"+i).is(":checked"));
            console.log("Reminder"+i+" checked: "+$("#reminder"+i).is(":checked"));
        }
        datas['school']=$("#campus").val();


        $('#title').html('<h3>Processing...</h3>');

        $.ajax({
              type: "POST",
              contentType: "application/json; charset=utf-8",
              url: "/magic",
              data: JSON.stringify(datas),
              success: function (data) {
                console.log("Worked");
                $('#title').html('');
                for(var summary of data["success"]){
                    $('#title').append('<h3>Added '+summary+'!</h3>');
                }
                if(data["error"]!="None"){
                    if(data["error"]=="Access Token Error"){
                      send();
                      return;
                    }
                    $('#title').append('<h3>Got an error: '+data["error"]+'! Please try again.</h3>');
                    $('#form')[0].reset();
                }
              },
              dataType: "json",
              error: function (xhr, ajaxOptions, thrownError) {
                   $('#title').html('<h3>Authorizing...</h3>');
                   console.log("Authorizing...");
                   console.log(xhr.status);
                   console.log(xhr.responseText);
                   console.log(thrownError);
       }
        });
    };

$(document).ready(function(){

    init();
    $("#add").click(function(){
        send();
    });
});

input=1;

function init()
{
    $("#inputs div input").slice(-3).focus(function(){
        $("#inputs div input").slice(-3).unbind("focus");
        input++;
        $("#inputs").append("<div class='4u 12u(2)'><input type='text' name='subjectNumber"+input+"' id='subjectNumber"+input+"' value='' placeholder='Example: 198 in 01:198:111' /></div><div class='4u 12u(2)'><input type='text' name='courseNumber"+input+"' id='courseNumber"+input+"' value='' placeholder='Example: 111 in 01:198:111' /></div><div class='4u 12u(2)'><input type='text' name='sectionNumber"+input+"' id='sectionNumber"+input+"' value='' placeholder='Section' /></div>");
        init();
    });
}





























