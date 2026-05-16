document.getElementById("analyze").addEventListener("click", async () => {

  let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

  chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: () => document.body.innerText
  }, async (results) => {

    let text = results[0].result.substring(0, 3000);

    let response = await fetch("http://127.0.0.1:5000/predict", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ news: text })
    });

    let data = await response.json();

    document.getElementById("result").innerHTML = `
      <h3>${data.prediction}</h3>
      <p>Fake Score: ${data.confidence}%</p>
    `;
  });

});