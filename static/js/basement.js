$( document ).ready(function() {
 	var people=0;
    var cap=5;

 	function update(){
 		$("#numPeople").text(people);
 		console.log("We have "+people+" people now!");
 	}

    $("#up").click(function(){
    	people++;
    	update();
        if(people>=cap){
            alert("We are now at capacity. DO NOT LET MORE PEOPLE IN!");
        }
    })
    $("#down").click(function(){
    	people--;
    	update();
    })
    $("#count").click(function(){
    	update();
        if(people>=cap){
            alert("We are now at capacity. DO NOT LET MORE PEOPLE IN!");
        }
    })

 
});