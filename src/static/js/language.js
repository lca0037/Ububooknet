
function idioma(nuevo,actual){
	alert(nuevo)
	alert(actual)
      if(nuevo != actual){
      	$.ajax({
            type: "POST",
            contentType: "application/json;charset=utf-8",
            url: "/Idioma/",
            traditional: "true",
            data: JSON.stringify(nuevo),
            dataType: "json",
            success: function(response){
            	alert(response)
                  validNavigation = true
            	location.reload()
            }
          });
      }
}