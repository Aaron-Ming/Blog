﻿function a(x,y){
	l = $('#main').offset().left;
	w = $('#main').width();
	$('#tbox').css('left',(l + w + x) + 'px');
	$('#tbox').css('bottom',y + 'px');
}
function b(){
	h = $(window).height();
	t = $(document).scrollTop();
	if(t > h){
		$('#gotop').fadeIn('slow');
	}else{
		$('#gotop').fadeOut('slow');
	}
}
$(document).ready(function(e) {		
	a(10,10);
	b();
	$('#gotop').click(function(){
		$(document).scrollTop(0);	
	})
});
$(window).resize(function(){
	a(10,10);
});

$(window).scroll(function(e){
	b();		
})
