$(document).ready(function(){

  development=false

function randomString(length) {
    return Math.round((Math.pow(36, length + 1) - Math.random() * Math.pow(36, length))).toString(36).slice(1);
}
var name=randomString(Math.floor(Math.random()*15)+10);
localStorage.setItem(getName(),false);

var func='getCalendars';

function storage_handler(evt)
{
  console.log("fired!");
  if(localStorage.getItem(name)=="true"){
    // if(development){
      console.log(getName());
    // }
    localStorage.setItem(getName(),false);
    localStorage.removeItem(evt.key);
    newName();
    authorize(func);
  }
}



window.addEventListener('storage', storage_handler, false);

function newName(){
  name=randomString(Math.floor(Math.random()*15)+10);
}
function getName(){
  return name;
}

function getCalendars(){
  $.ajax({
      type: "GET",
      contentType: "application/json; charset=utf-8",
      url: "/getCalendars",
      // data: JSON.stringify(datas),
      success: function (data) {
        console.log("Worked");
        $('#title').html('');
        $("#calendarList").html('');

        // $("#form").hide();
        $("#add").show();
        $("#calendarList").show();
        $("#newForm").hide();

        $('#title').append('<h3>Select Calendars To Add</h3>');
        // $('#form')[0].reset();
        localStorage.removeItem(getName());
        newName();

        console.log("appending ...");

        if(data["error"]){
            console.log("Data gave an error...");
            $('#title').append('<h3>Got an error: '+data["error"]+'! Please try again.</h3>');
            // $('#form')[0].reset();
            localStorage.removeItem(getName());
            newName();
        }
        else{
          for(var cal of data['items']){
            console.log("appending "+cal['summary']);
            $("#calendarList").append('<div class="3u 12u(2)"><center><input type="checkbox" id="'+cal['id']+'" name="'+cal['id']+'"><label for="'+cal['id']+'">'+cal['summary']+'</label></center></div>');
          }
        }
      },
      dataType: "json",
      error: function (xhr, ajaxOptions) {
           $('#title').html('<h3>Ooopps, got an error...</h3>');
           if(development){
             console.log(xhr.status);
             console.log(xhr.responseText);
           }
           // console.log(thrownError);
      }
  });
}

function authorize(method){
  var datas=JSON.stringify({'id':name});
  console.log(datas);
  $.ajax({
    type: "POST",
    contentType: "application/json; charset=utf-8",
    url: "/authorize",
    success: function (data) {
      console.log("Authorizing");
      $('#title').html('<h3>Authorizing...</h3><h4>P.S. You will need to allow this popup to authorize you.</h4>');
      if(data['url']){
        console.log("Going to url: "+data["url"]);
        localStorage.setItem(getName(),false);
        window.open(data["url"]);
      }
      else{
        // console.log("Success: "+data['success']+" url: "+data["url"]);
        if(method=="getCalendars"){
          getCalendars();
        }
        else if(method=="send"){
          send();
        }
        else{
          console.log('Did not get a method for authorize');
        }
      }
    },
    data: datas,
    dataType: "json",
    error: function (xhr, ajaxOptions) {
         $('#title').html('<h3>Ooopps, got an error...</h3>');
         if(development){
           console.log(xhr.status);
           console.log(xhr.responseText);
         }
         // console.log(thrownError);
    }
  });
}

function send() {

        $('#title').html('<h3>Processing, this may take a minute...</h3>');
        var datas={
          ids:[],
        };
        $("input:checked").each(function(){
          datas['ids'].push($(this).attr('id'));
        });
        console.log(JSON.stringify(datas));
        $.ajax({
              type: "POST",
              contentType: "application/json; charset=utf-8",
              url: "/magicPledge",
              data: JSON.stringify(datas),
              success: function (data) {
                console.log("Worked");
                $('#title').html('');
                $("#form").hide();
                $("#add").hide();
                $("#calendarList").hide();
                $("#newForm").show();

                $('#title').append('<h3>Added you to our database '+data['name']+'!</h3>');
                // $('#form')[0].reset();
                localStorage.removeItem(getName());
                newName();

                if(data["error"]!="None"){
                    if(data["error"]=="Access Token Error"){
                      send();
                      return;
                    }
                    console.log("Data gave an error...");
                    $('#title').append('<h3>Got an error: '+data["error"]+'! Please try again.</h3>');
                    // $('#form')[0].reset();
                    localStorage.removeItem(getName());
                    newName();
                }
              },
              dataType: "json",
              error: function (xhr, ajaxOptions) {
                   $('#title').html('<h3>Ooopps, got an error...</h3>');
                   if(development){
                     console.log(xhr.status);
                     console.log(xhr.responseText);
                   }
                   // console.log(thrownError);
       }
        });
    };

  console.log("Pledge...");
    $("#add").hide();
    $("#calendarList").hide();
    $("#newForm").hide();
    $("#add").click(function(){
        func='send';
        $("#calendarList").hide();
        authorize('send');
    });
    $("#newForm").click(function(){
      // $("#form").show();
      $("#add").hide();
      $("#calendarList").hide();
      $("#getCalendars").show();
      $("#newForm").hide();
    });
    $("#getCalendars").click(function(){
      // $("#form").show();
      $("#add").show();
      $("#calendarList").show();
      $("#getCalendars").hide();
      $("#newForm").hide();
      func='getCalendars';
      authorize("getCalendars");
    });
});





























