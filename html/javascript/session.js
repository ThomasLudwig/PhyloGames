import { postJSON } from "./main.js";

export async function createSession() {
  const parameters = {
    speciesset: document.querySelector('input[name="speciesset"]:checked').value,
    mam: document.getElementById("sMam").checked,
    mars: document.getElementById("sMars").checked,
    bird: document.getElementById("sBird").checked,
    rep: document.getElementById("sRep").checked,
    fish: document.getElementById("sFish").checked,
    dino: document.getElementById("sDino").checked,
    inv: document.getElementById("sInv").checked,
    plan: document.getElementById("sPlan").checked,
    fung: document.getElementById("sFung").checked,
    bact: document.getElementById("sBact").checked,
    nbspecies: parseInt(document.getElementById("nbspecies").value),
    gamemode: document.querySelector('input[name="gamemode"]:checked').value
  };

  /*
  const response = await fetch("/api/session", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(parameters)
  });

  const data = await response.json();
  console.log("Session ID:", data.sessionId);
  return data.sessionId;*/
  const data = await postJSON("/api/session", parameters);
  return data.sessionId;
}

export async function deleteSession(sessionId) {
  await fetch(`/api/session/${sessionId}`, {method: "DELETE"});
}