// Particles background

particlesJS("particles-js",{

particles:{
number:{value:70},
size:{value:3},
move:{speed:2},
line_linked:{enable:true}
}

});


// Prediction functions

function predictNews(){

let text=document.getElementById("newsText").value

let loader=document.getElementById("loader")

loader.classList.remove("hidden")

fetch("/predict",{

method:"POST",

headers:{
"Content-Type":"application/x-www-form-urlencoded"
},

body:"news="+encodeURIComponent(text)

})
.then(res=>res.json())
.then(data=>{

loader.classList.add("hidden")

displayResult(data)

})

}



function predictURL(){

let url=document.getElementById("newsURL").value

let loader=document.getElementById("loader")

loader.classList.remove("hidden")

fetch("/predict_url",{

method:"POST",

headers:{
"Content-Type":"application/x-www-form-urlencoded"
},

body:"url="+encodeURIComponent(url)

})
.then(res=>res.json())
.then(data=>{

loader.classList.add("hidden")

displayResult(data)

})

}



function displayResult(data){

let box=document.getElementById("resultBox")

box.innerHTML=`

<div class="result">

<h2>${data.prediction}</h2>

<p>Fake Score: ${data.confidence}%</p>

<div class="meter">
<div class="meter-bar" style="width:${data.confidence}%"></div>
</div>

</div>

`
}

function clearHistory(){

if(confirm("Are you sure you want to delete history?")){

fetch("/clear_history",{
method:"POST"
})
.then(res=>res.json())
.then(data=>{
location.reload()
})

}

}