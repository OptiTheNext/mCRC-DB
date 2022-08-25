let input, hashtagArray, container, t;

input = document.querySelector('#hashtags');
container = document.querySelector('.tag-container');
hashtagArray = [];

let currentHashTag = [];

input.addEventListener('keyup', () => {
    if (event.which == 13 && input.value.length > 0) {
      var text = document.createTextNode(input.value);
      var p = document.createElement('p');
      container.appendChild(p);
      p.appendChild(text);
      currentHashTag.push(text);
      p.classList.add('tag');
      input.value = '';
      
      let deleteTags = document.querySelectorAll('.tag');
      
    /*  for(let i = 0; i < deleteTags.length; i++) {
    
        deleteTags[i].addEventListener('click', () => {
          currentHashTag.splice(currentHashTag.indexOf(deleteTags[i].innerText))
          container.removeChild(deleteTags[i]);
        });
      }*/

    for (let i of deleteTags){
      i.addEventListener('mousedown', () => {
        currentHashTag.splice(currentHashTag.indexOf(i.innerText))
        container.removeChild(i);
        
      });
    }
    console.log(currentHashTag)
    }
    
});

function submitTags(){
  console.log(currentHashTag);
  let tags = [];
  for (let i of currentHashTag){
    tags.push(i.data)
  }
  console.log(tags)
  var xhr = new XMLHttpRequest();
  xhr.open("POST", "/datenanalyse_admin", true);
  xhr.setRequestHeader('Content-Type', 'application/json');
  xhr.send(JSON.stringify({
    value: tags
  }));
  
  currentHashTag = [];
  container.innerHTML = "";
}

var data =
  '[{ "value": 1, "text": "Task 1", "continent": "Task" }, { "value": 2, "text": "Task 2", "continent": "Task" }, { "value": 3, "text": "Task 3", "continent": "Task" }, { "value": 4, "text": "Task 4", "continent": "Task" }, { "value": 5, "text": "Task 5", "continent": "Task" }, { "value": 6, "text": "Task 6", "continent": "Task" } ]';

//get data pass to json
var task = new Bloodhound({
  datumTokenizer: Bloodhound.tokenizers.obj.whitespace("text"),
  queryTokenizer: Bloodhound.tokenizers.whitespace,
  local: jQuery.parseJSON(data) //your can use json type
});

task.initialize();

var elt = $("#hashtags");
elt.tagsinput({
  itemValue: "value",
  itemText: "text",
  typeaheadjs: {
    name: "task",
    displayKey: "text",
    source: task.ttAdapter()
  }
});


