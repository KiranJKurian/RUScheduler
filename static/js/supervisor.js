$( document ).ready(function() {
	$("#clear").click(function(){
		if(confirm("Are you sure you want to clear the number of people?")){
			$.ajax({
	          type: "GET",
	          contentType: "application/json; charset=utf-8",
	          url: "/party/clear",
	          async: false,
	          success: function () {
	            alert("People cleared");
	          },
	          dataType: "json",
	        });
		}
	});
)}