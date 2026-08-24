import { stopGame } from "./main.js";
import { postJSON } from "./main.js";

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
  console.log("Results");
  console.log(results);
  //apply style
  var i = 0;
  var errors = 0;
  var good = 0;
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

  //The game is won
  if(errors == 0) {
    stopGame();
  }
}

async function evaluate(session, query){
  const parameters = {
    session: session,
    query: query
  }

  const data = await postJSON("/api/evaluate", parameters);
  return data.result.split(",");
}

export async function solve() {
  const tree = document.querySelectorAll("div.tree");
  const session = tree[0].id;
  const sorted = await getSorted(session);
  sorted.forEach(element => { console.log(" - "+element) });
  //apply sorting
  reorder(sorted)
  await correct();
}

async function getSorted(session){
  const parameters = { session: session }
  const data = await postJSON("/api/solve", parameters);
  console.log("Solved: "+data.result);
  console.log("Type "+typeof(data.result));
  return data.result;
}

function reorder(sorted) {
  const list = document.querySelector('.sortable-list');
  if (!list) return;

  sorted.forEach(id => {
    const li = document.getElementById("YY"+id+"YY");
    if (li) 
      list.appendChild(li); // moves the <li> to the end, in this order
  });
}
