var running=false;
import { drag } from "./drag.js";
import { createSession } from "./session.js";
import { correct } from "./correction.js";
import { solve } from "./correction.js";
const NONE = "none";
const BLOCK = "block";
const PLAY = "play"
const MENU = "menu"

init();

//Page initialization
async function init() {
  await loadSection("header", "html/headerbig.html");
  await loadSection("splash", "html/splash.html");
  await loadSection("settings", "html/settings.html");
  await loadSection("score", "html/score.html");
  await loadSection("footer", "html/footer.html");

  await show(MENU);
  speciesSelection();
  button("go", go);
  button("show", showAll);
  button("val", correct);
  button("solve", solve);
  button("restart", restart);

  resetScore();
}

//Links each button to its function
async function button(name, fun) {
  document.getElementById(name).addEventListener("click", fun);
}

//Hides/Show the custom species group selection
function speciesSelection(){
  document.querySelectorAll('input[name="speciesset"]').forEach(radio => {
    radio.addEventListener("change", updateCategoryList);
  }); 

  // Set the initial state
  updateCategoryList();
}

//Companion function to speciesSelection()
function updateCategoryList() {
  const selected = document.querySelector('input[name="speciesset"]:checked');
  document.querySelector(".category-list").classList.toggle("disabled", selected.value !== "custom");
}

//Loads the content of an HTML file into a div
async function loadSection(id, file) {
  const response = await fetch(file, {cache: "no-store"});
  if (!response.ok)
    throw new Error(`Failed to load ${file}: ${response.status}`);

  const html = await response.text();
  document.getElementById(id).innerHTML = html;
}

//Starts the game
async function go() {
  const gamemode = document.querySelector('input[name="gamemode"]:checked').value;
  const nbspecies = parseInt(document.getElementById("nbspecies").value);
  document.getElementById("restart").style.display = NONE;
  document.getElementById("val").style.display = BLOCK;
  document.getElementById("solve").style.display = BLOCK;
  document.getElementById("scoremode").textContent = (gamemode === "1" ? "Facile" : "Normal");
  document.getElementById("total").textContent = nbspecies;
  await prepareGame(nbspecies, gamemode);
  startTimer();
  show(PLAY);
}

//Timer function
function startTimer() {
  let seconds = 0;
  document.getElementById("timer").textContent = 0;
  document.getElementById("attempts").textContent = 0;
  running=true;
  const intervalId = setInterval(() => {
    if (!running) 
      clearInterval(intervalId);
    else {
      seconds++;
      document.getElementById("timer").textContent = getElapsed(seconds);
    }
  }, 1000);
}

function getElapsed(seconds){
  let m = Math.floor(seconds/60);
  let s = seconds%60;
  let min = m < 10 ? "0"+m : ""+m;
  let sec = s < 10 ? "0"+s : ""+s;
  return min+":"+sec;
}

//Stops the game (on win or solve)
export function stopGame() {
  running=false;
  document.getElementById("restart").style.display = BLOCK;
  document.getElementById("val").style.display = NONE;
  document.getElementById("solve").style.display = NONE;
}

//Shows either the menu or the game
async function show(option) {
  if(option === "play"){
    document.getElementById("stop").style.display = NONE;
    document.getElementById("play").style.display = BLOCK;
    await bigHeader(false);
  } else {
    document.getElementById("stop").style.display = BLOCK;
    document.getElementById("play").style.display = NONE;
    await bigHeader(true);
  }
}

//Shows either the big or small header
async function bigHeader(big) {
  const main = document.getElementsByTagName('main')[0];
  if(big){
    await loadSection("header", "html/headerbig.html");
    main.classList.remove('mainsmall');
    main.classList.add('mainbig');
  } else {
    await loadSection("header", "html/headersmall.html");
    main.classList.remove('mainbig');
    main.classList.add('mainsmall');
  }
}

//Gets back to the menu
async function restart() {
  await show("menu");
  resetScore();
  document.getElementById("score").style.backgroundColor = "white";
}

//Reinitialize the score panel
function resetScore(){
  document.getElementById("scoremode").textContent = "?";
  document.getElementById("correct").textContent = "?";
  document.getElementById("attempts").textContent = 0;
  document.getElementById("timer").textContent = "00:00";
}

//Starts game
async function prepareGame(){
  const sessionid = await createSession();
  await loadSection("game", "sessions/"+sessionid+"/game.html");
  drag();
}

//Hidden functionnality to show all available species
async function showAll() {
  const gamemode = document.querySelector('input[name="gamemode"]:checked').value;
  const nbspecies = parseInt(document.getElementById("nbspecies").value);
  document.getElementById("restart").style.display = NONE;
  document.getElementById("val").style.display = BLOCK;
  document.getElementById("solve").style.display = BLOCK;
  document.getElementById("scoremode").textContent = (gamemode === "1" ? "Facile" : "Normal");
  document.getElementById("total").textContent = nbspecies;
  await postJSON("/api/showAll", null)
  await loadSection("game", "data/allSpecies.html");
  await show(PLAY);
}

//Worker function the calls a python webservices (handle query and response)
export async function postJSON(url, parameters) {
  const response = await fetch(url, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(parameters)
  });

  const data = await response.json();
  return data;
}