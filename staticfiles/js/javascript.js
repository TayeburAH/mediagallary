$(document).ready(function(){
     $("#search-form").submit(function(e){
         if ( !$(this).find("#search").val() ){
         // Both can be used
         //!$(this).find("#search").val()
         //!$("input[type='search']").val()
            e.preventDefault()
            console.log('blank')
         }
     })

});











