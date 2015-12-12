$( document ).ready(function() {
 	var people=0;

 	function update(){
 		$("#numPeople").text(people);
 		console.log("We have "+people+" people now!");
 	}

    $("#up").click(function(){
    	people++;
    	update();
    })
    $("#down").click(function(){
    	people--;
    	update();
    })
    $("#count").click(function(){
    	update();
    })
 
});