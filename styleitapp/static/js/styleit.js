$(document).ready(function(){
  $('#state').change(function(){
      var stateid = $(this).val()
      var csrf = "{{ csrf_token() }}"
      data2send = {"stateid":stateid, "csrf_token":csrf}

      ///make ajax call
      $.ajax({
          url:"/load/lga/",
          data:data2send,
          type:'post',
          success:function(msg){
          $('#lga').html(msg)
          }
      });
  });
    
  //activating signup
  $('#agree').click(function(){
    var dis = $(this).prop('checked')
    if(dis == false){
      $('#btn').attr('disabled', 'disabled')
    }else{
      $('#btn').removeAttr('disabled')
    }
  });

    
    //switching profile picture 
    $('#profiletoggler').click(function(){
      $('#divbody').toggleClass('col-md-9')
     });

   
    // share buttons
    $('#facebook').click(function(){
      $('#shareon').css("display", "none");
      $('#share').css("display", "block");
      var name="facebook";
      var sharepost=$("#sharepost").val();
      var user=$("#user").val();
      var csrf = "{{ csrf_token() }}";
      data2send = {"name":name, "csrf_token":csrf, "sharepost":sharepost, "user":user}
      //Ajax call
      $.ajax({
          url:"/share/",
          data:data2send,
          type:'POST',
          success:function(msg){
          console.log(msg);
          $('#share').load(location.href + " #share")
          }
        });
    });

    $('#linkedin').click(function(){
      $('#shareon').css("display", "none")
      $('#share').css("display", "block")
      var name="linkedin"
      var sharepost=$("#sharepost").val();
      var user=$("#user").val();
      var csrf = "{{ csrf_token() }}";
      data2send = {"name":name, "csrf_token":csrf, "sharepost":sharepost, "user":user}
      //Ajax call
      $.ajax({
          url:"/share/",
          data:data2send,
          type:'POST',
          success:function(msg){
          console.log(msg);
          $('#share').load(location.href + " #share")
          }
        });
    });

    $('#telegram').click(function(){
      $('#shareon').css("display", "none")
      $('#share').css("display", "block")
      var name="telegram"
      var sharepost=$("#sharepost").val();
      var user=$("#user").val();
      var csrf = "{{ csrf_token() }}";
      data2send = {"name":name, "csrf_token":csrf, "sharepost":sharepost, "user":user}
      //Ajax call
      $.ajax({
          url:"/share/",
          data:data2send,
          type:'POST',
          success:function(msg){
          console.log(msg);
          $('#share').load(location.href + " #share")
          }
        });
    });

    $('#twitter').click(function(){
      $('#shareon').css("display", "none")
      $('#share').css("display", "block")
      var name="twitter"
      var sharepost=$("#sharepost").val();
      var user=$("#user").val();
      var csrf = "{{ csrf_token() }}";
      data2send = {"name":name, "csrf_token":csrf, "sharepost":sharepost, "user":user}
      //Ajax call
      $.ajax({
          url:"/share/",
          data:data2send,
          type:'POST',
          success:function(msg){
          console.log(msg);
          $('#share').load(location.href + " #share")
          }
        });
    });
     
    //post trash by creator section
    $('#trashit').click(function(){
      var potid = $('#potid').val();
      var csrf = "{{ csrf_token() }}";
      data3send = {"postid":potid, "csrf_token":csrf}
      $.ajax({
        url:'/trashit/',
        data:data3send,
        type:'POST',
        success:function(msg){
          console.log(msg);
          location.reload(true);
        }
      });
    }); 
     
    //newsletter section
    $('#newsbtn').click(function(){
      var newsname=$('#newsname').val();
      var newsmail=$('#newsmail').val();
      var csrf="{{ csrf_token() }}";
      data={"name":newsname, "email":newsmail, "csrf_token":csrf}
      $.ajax({
        url:'/newsletter/',
        data:data,
        type:"POST",
        success:function(msg){
          console.log(msg)
          $('#output').html(msg)
        }
      });
    });

    $('#country').change(function(){
      const countryid=$("#country").val();
      var csrf="{{ csrf_token() }}";
      data={"countryid":countryid, "csrf_token":csrf}
      $.ajax({
        url:'/countrycheck/',
        data:data,
        type:"POST",
        success:function(msg){
          console.log(msg)
          if(msg=='Nigeria') {
            $('#nigblock').css("display", "block");
            $('#nonNigblock').css("display", "none");
          }else{
            if(msg !='Nigeria'){
              $('#nonNigblock').css("display", "block");
              $('#nigblock').css("display", "none");
            };
          };
        }
      });
    });

 });


//window scroll to load more post 
var loading = false;

$(window).scroll(function() {
if($(window).scrollTop() == $(document).height() - $(window).height()){
if (!loading) {
loading = true;
var page = $(this).data('page');
$.get('/trending?page=' + page, function(data) {
if(data.trim().length==0){
 alert('No more data to load')
}else{
 var posts = $(data).find('.post');
 $('.post').append(posts);
};
});
}
};

});



//Javascript to change multiple divs
function divchange(){
      document.getElementById("Sameprofile").style.display='block';
      document.getElementById("Samelike").style.display='none';
      document.getElementById("Sameunlike").style.display='none';
      document.getElementById("editprofile").style.display='none';
      document.getElementById('task').style.display='none';
  };
function divchange2(){
    document.getElementById("Sameprofile").style.display='none';
    document.getElementById("Samelike").style.display='block';
    document.getElementById("Sameunlike").style.display='none';
    document.getElementById("editprofile").style.display='none';
    document.getElementById('task').style.display='none';
};
function divchange3(){
    document.getElementById("Sameprofile").style.display='none';
    document.getElementById("Samelike").style.display='none';
    document.getElementById("Sameunlike").style.display='block';
    document.getElementById("editprofile").style.display='none';
    document.getElementById('task').style.display='none';
};
function divchange4(){
  document.getElementById("editprofile").style.display='block';
    document.getElementById("Sameprofile").style.display='none';
    document.getElementById("Samelike").style.display='none';
    document.getElementById("Sameunlike").style.display='none';
    document.getElementById('task').style.display='none';
};            
function divchange5(){
    document.getElementById("Sameprofile").style.display='none';
    document.getElementById("Samelike").style.display='none';
    document.getElementById("Sameunlike").style.display='none';
    document.getElementById("editprofile").style.display='none';
    document.getElementById('task').style.display='block';
};

//reply function            
function reply(id){
  var rep=document.getElementById(id)
  if(rep.style.display==='block'){
    rep.style.display='none';
  }else{
    rep.style.display='block';
  };
};

// designer delete display
var dots = document.getElementById('3dot');
var trashi = document.getElementById('trashi');
var trashit = document.getElementById('trashit');
if (trashit !==null){
  trashi.addEventListener("click", function() {
  dots.style.display = dots.style.display === 'none' ? 'block' : 'none';
});
}
   

// share function
function share(){
  document.getElementById('shareon').style.display='block';
  document.getElementById('share').style.display='none';
};


// notification toggle
const noti=document.getElementById('notif');
if (noti !==null){
  noti.addEventListener('click', (event)=>{
  var displayelement = document.getElementById('note');
  if (displayelement.style.display==='none'){
    displayelement.style.display='block';
    var hideelement = document.getElementById('note');
    if (hideelement){
      hideelement.addEventListener('mouseleave', function(event){
        noti.style.display='block';
        displayelement.style.display='none';
        });                  
      };
    }else{
      displayelement.style.display='none';
      document.getElementById('notif').style.display='block';
    };
  });
};
   

//text complaint area
const textarea1 = document.getElementById('textarea');
if (textarea1 !== null){
  textarea1.addEventListener('input', function(){
  if (this.value.length > this.maxLength){
    this.value = this.value.slice(0, this.maxLength);
  }
});
};
   

//currency digit validation
const acno = document.getElementById('acno');
if (acno !==null){
  acno.addEventListener('input', function() {
  if (this.value.length > this.maxLength) {
    this.value = this.value.slice(0, this.maxLength);
  }
});
};