$( document ).ready(function() {
 	var people=0;
    var cap=5;

 	function update(){
        $.ajax({
          type: "GET",
          contentType: "application/json; charset=utf-8",
          url: "/basement/number",
          async: false,
          success: function (data) {
            people=data["people"];
            $("#numPeople").text(people);
            console.log("We have "+people+" people now!");
          },
          dataType: "json",
        });
 	}

    update();

    $("#up").click(function(){
    	$.ajax({
          type: "GET",
          contentType: "application/json; charset=utf-8",
          url: "/basement/add",
          success: function (data) {
            people=data["people"];
            $("#numPeople").text(people);
            console.log("We have "+people+" people now!");
          },
          dataType: "json",
        });
        if(people>=cap){
            alert("We are now at capacity. DO NOT LET MORE PEOPLE IN!");
        }
    })
    $("#down").click(function(){
    	$.ajax({
          type: "GET",
          contentType: "application/json; charset=utf-8",
          url: "/basement/subtract",
          success: function (data) {
            people=data["people"];
            $("#numPeople").text(people);
            console.log("We have "+people+" people now!");
          },
          dataType: "json",
        });
    })
    $("#count").click(function(){
    	update();
        if(people>=cap){
            alert("We are now at capacity. DO NOT LET MORE PEOPLE IN!");
        }
    })
 
});