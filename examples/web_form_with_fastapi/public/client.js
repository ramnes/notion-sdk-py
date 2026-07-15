const dbForm = document.getElementById("databaseForm");
const pageForm = document.getElementById("pageForm");
const blocksForm = document.getElementById("blocksForm");
const commentForm = document.getElementById("commentForm");

const dbResponseEl = document.getElementById("dbResponse");
const pageResponseEl = document.getElementById("pageResponse");
const blocksResponseEl = document.getElementById("blocksResponse");
const commentResponseEl = document.getElementById("commentResponse");

function appendApiResponse(apiResponse, el) {
  console.log(apiResponse);
  const msg = document.createElement("p");
  msg.textContent = "Result: " + apiResponse.message;
  el.appendChild(msg);
  if (apiResponse.message === "error") return;

  const id = document.createElement("p");
  id.textContent = "ID: " + apiResponse.data.id;
  el.appendChild(id);

  if (apiResponse.data.dataSourceId) {
    const ds = document.createElement("p");
    ds.textContent = "Data Source ID: " + apiResponse.data.dataSourceId;
    el.appendChild(ds);
  }

  if (apiResponse.data.url) {
    const link = document.createElement("a");
    link.setAttribute("href", apiResponse.data.url);
    link.innerText = apiResponse.data.url;
    el.appendChild(link);
  }
}

function appendBlocksResponse(apiResponse, el) {
  console.log(apiResponse);
  const msg = document.createElement("p");
  msg.textContent = "Result: " + apiResponse.message;
  el.appendChild(msg);
  const id = document.createElement("p");
  id.textContent = "ID: " + apiResponse.data.results[0].id;
  el.appendChild(id);
}

dbForm.onsubmit = async function (event) {
  event.preventDefault();
  const body = JSON.stringify({ dbName: event.target.dbName.value });
  const resp = await fetch("/databases", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body,
  });
  appendApiResponse(await resp.json(), dbResponseEl);
};

pageForm.onsubmit = async function (event) {
  event.preventDefault();
  const body = JSON.stringify({
    dbID: event.target.newPageDB.value,
    pageName: event.target.newPageName.value,
    header: event.target.header.value,
  });
  const resp = await fetch("/pages", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body,
  });
  appendApiResponse(await resp.json(), pageResponseEl);
};

blocksForm.onsubmit = async function (event) {
  event.preventDefault();
  const body = JSON.stringify({
    pageID: event.target.pageID.value,
    content: event.target.content.value,
  });
  const resp = await fetch("/blocks", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body,
  });
  appendBlocksResponse(await resp.json(), blocksResponseEl);
};

commentForm.onsubmit = async function (event) {
  event.preventDefault();
  const body = JSON.stringify({
    pageID: event.target.pageIDComment.value,
    comment: event.target.comment.value,
  });
  const resp = await fetch("/comments", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body,
  });
  appendApiResponse(await resp.json(), commentResponseEl);
};
