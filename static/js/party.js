$( document ).ready(function() {
 	var people=0;
    var cap=999;

 	function update(){
        $.ajax({
          type: "GET",
          contentType: "application/json; charset=utf-8",
          url: "/party/number",
          async: false,
          success: function (data) {
            people=data["people"];
            $("#numPeople").text(people);
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
          url: "/party/add",
          success: function (data) {
            people=data["people"];
            $("#numPeople").text(people);
            $("#up").removeClass("active").addClass("success");
            console.log("We have "+people+" people now!");
          },
          dataType: "json",
        });
        if(people>=cap){
            alert("We are now at capacity. DO NOT LET MORE PEOPLE IN!");
        }
    })
    $("#down").click(function(){
     $("#down").addClass("active").removeClass("danger");
    	$.ajax({
          type: "GET",
          contentType: "application/json; charset=utf-8",
          url: "/party/subtract",
          success: function (data) {
            people=data["people"];
            $("#numPeople").text(people);
            $("#down").removeClass("active").addClass("danger");
            console.log("We have "+people+" people now!");
          },
          dataType: "json",
        });
    })
    $("#count").click(function(){
    	$("#count").addClass("active").removeClass("info");
    	update();
    	$("#count").removeClass("active").addClass("info");
        if(people>=cap){
            alert("We are now at capacity. DO NOT LET MORE PEOPLE IN!");
        }
    })
 
});
