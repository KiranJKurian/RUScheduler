var name = prompt("Hello, what's your name?");
// name = JSON.stringify({'name':name});
$( document ).ready(function() {
  // var temp = prompt("Hello, what's your name?");
  // name = JSON.stringify({'name':name});
  var cap = 5;
 	function replacePeople(people){
    if(people=="Not found"){
      alert(name+" not found");
      return;
    }
    var str="";
    for(personIndex in people){
      if(personIndex<people.length-1){
        str+= people[personIndex]+", ";
      }
      else{
        str+= people[personIndex];
      }
    }
    if(str==""){
      str = "None";
    }
    $("#numPeople").text(str);
  }
  function update(){
        $.ajax({
          type: "GET",
          contentType: "application/json; charset=utf-8",
          url: "/chegg/people",
          async: false,
          success: function (data) {
            people=data["people"];
            replacePeople(people);
            // console.log("We have "+people+" people now!");
          },
          dataType: "json",
        });
 	}
 	setInterval(update, 5000);
    update();

    $("#up").click(function(){
    	$("#up").addClass("active").removeClass("success");
    	$.ajax({
          type: "GET",
          contentType: "application/json; charset=utf-8",
          url: "/chegg/add/"+name,
          // data:name,
          success: function (data) {
            people=data["people"];
            replacePeople(people);
            $("#up").removeClass("active").addClass("success");
            console.log("We have "+people+" people now!");
          },
          dataType: "json",
        });
        // if(people>=cap){
        //     alert("We are now at capacity. PLEASE SIGN OFF SOON!");
        // }
    });
    $("#down").click(function(){
     $("#down").addClass("active").removeClass("danger");
    	$.ajax({
          type: "GET",
          contentType: "application/json; charset=utf-8",
          url: "/chegg/subtract/"+name,
          success: function (data) {
            people=data["people"];
            replacePeople(people);
            $("#down").removeClass("active").addClass("danger");
            console.log("We have "+people+" people now!");
          },
          dataType: "json",
        });
    });
    $("#count").click(function(){
    	$("#count").addClass("active").removeClass("info");
    	update();
    	$("#count").removeClass("active").addClass("info");
        // if(people>=cap){
        //     alert("We are now at capacity. DO NOT LET MORE PEOPLE IN!");
        // }
    });
    $("#reserved").click(function(){
      $("#reserved").addClass("active").removeClass("info");
      
      if(prompt("Do you want to make a reservation?(yes/no)").toLowerCase()=="yes"){
        
      }

      $("#reserved").removeClass("active").addClass("info");
    });
 
});
