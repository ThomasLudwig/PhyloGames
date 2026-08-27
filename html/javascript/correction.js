import { stopGame } from "./main.js";
import { postJSON } from "./main.js";

// Launches correction process
export async function correct() {
  document.getElementById("attempts").textContent = 1+parseInt(document.getElementById("attempts").textContent);
  const selection = document.querySelectorAll("div.select");
  const tree = document.querySelectorAll("div.tree");
  const session = tree[0].id
  var i = 0;

  //build query
  var query = "";
  selection.forEach(select => {
    query = query +"," + select.id.slice(2, -2); //remove leading and trailing "XX"
  })
  query = query.substring(1);
  
  //send query get results
  var results = await evaluate(session, query);

  //apply style
  var i = 0;
  var errors = 0;
  var good = 0;
  var total = document.getElementById("total").textContent;
  selection.forEach(select => {
    select.classList.remove("neutral");
    select.classList.remove("correct");
    select.classList.remove("incorrect");

    if(results[i++] === "true"){
      select.classList.add("correct");
      good++;
    } else {
      select.classList.add("incorrect");
      errors++;
    }
  })

  document.getElementById("correct").textContent = good;
  applyColor(good, total);

  //The game is won
  if(errors == 0) {
    stopGame();
  }
}

//Applies a background color to the score panel, in function of the score
function applyColor(good, total) {
  const base = 200;
  const rest = 255 - base;
  const green = Math.round(rest * parseInt(good) / parseInt(total));
  const red = rest - green;
  const color = "rgb("+(base+red)+", "+(base+green)+", "+base+")"; 
  document.getElementById("score").style.backgroundColor = color;
}

//Calls the evaluation python service
async function evaluate(session, query){
  const parameters = {
    session: session,
    query: query
  }

  const data = await postJSON("/api/evaluate", parameters);
  return data.result.split(",");
}

// Solves the current game
export async function solve() {
  const tree = document.querySelectorAll("div.tree");
  const session = tree[0].id;
  const sorted = await getSorted(session);
  //apply sorting
  reorder(sorted)
  await correct();
}

//Calls the solving python webservice 
async function getSorted(session){
  const parameters = { session: session }
  const data = await postJSON("/api/solve", parameters);
  return data.result;
}

//Reorders the species divs according to the solution
function reorder(sorted) {
  const list = document.querySelector('.sortable-list');
  if (!list) return;

  sorted.forEach(id => {
    const li = document.getElementById("YY"+id+"YY");
    if (li) 
      list.appendChild(li); // moves the <li> to the end, in this order
  });
}
