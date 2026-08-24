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

async function init() {
  show(MENU);
  await loadSection("header", "html/header.html");  
  await loadSection("splash", "html/splash.html");
  await loadSection("settings", "html/settings.html");
  await loadSection("score", "html/score.html");
  await loadSection("footer", "html/footer.html");

  speciesSelection();
  button("go", go);
  button("show", showAll);
  button("val", correct);
  button("solve", solve);
  button("restart", restart);

  resetScore();
}

async function button(name, fun) {
  document.getElementById(name).addEventListener("click", fun);
}

function speciesSelection(){
  document.querySelectorAll('input[name="speciesset"]').forEach(radio => {
    radio.addEventListener("change", updateCategoryList);
  }); 

  // Set the initial state
  updateCategoryList();
}

function updateCategoryList() {
  const selected = document.querySelector('input[name="speciesset"]:checked');
  document.querySelector(".category-list").classList.toggle("disabled", selected.value !== "custom");
}

async function loadSection(id, file) {
  console.log("Loading "+file+" into "+id);
  const response = await fetch(file, {cache: "no-store"});
  if (!response.ok) {
    throw new Error(`Failed to load ${file}: ${response.status}`);
  }

  const html = await response.text();
  document.getElementById(id).innerHTML = html;
}

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
  show(PLAY);
}

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
      document.getElementById("timer").textContent = seconds;
    }
  }, 1000);
}

export function stopGame() {
  running=false;
  document.getElementById("restart").style.display = BLOCK;
  document.getElementById("val").style.display = NONE;
  document.getElementById("solve").style.display = NONE;
}

function show(option) {
  if(option === "play"){
    document.getElementById("stop").style.display = NONE;
    document.getElementById("play").style.display = BLOCK;
  } else {
    document.getElementById("stop").style.display = BLOCK;
    document.getElementById("play").style.display = NONE;
  }
}

function restart() {
  show("menu");
  resetScore();
}

function resetScore(){
  document.getElementById("scoremode").textContent = "?";
  document.getElementById("correct").textContent = "?";
  document.getElementById("attempts").textContent = 0;
  document.getElementById("timer").textContent = 0;
}


async function prepareGame(){
  const sessionid = await createSession();
  await loadSection("game", "sessions/"+sessionid+"/game.html");
  drag();
}

export async function postJSON(url, parameters) {
  const response = await fetch(url, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(parameters)
  });

  const data = await response.json();
  return data;
}