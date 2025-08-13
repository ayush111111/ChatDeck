console.log("Flashcard extension loaded");

document.addEventListener('mouseup', function (event) {
  let selectedText = window.getSelection().toString();
  if (selectedText.length > 10) {
    let btn = document.createElement('button');
    btn.innerText = 'Make Flashcard';
    btn.style.position = 'fixed';
    btn.style.top = event.pageY + 'px';
    btn.style.left = event.pageX + 'px';
    btn.style.zIndex = 10000;
    btn.style.backgroundColor = '#007bff';
    btn.style.color = 'white';
    btn.style.border = 'none';
    btn.style.padding = '8px';
    btn.style.borderRadius = '4px';
    btn.onclick = function () {
      fetch('http://localhost:8000/flashcards', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          conversation: [{ role: 'user', content: selectedText }],
          destination: 'notion'
        })
      }).then(() => {
        alert('Flashcard sent!');
        btn.remove();
      });
    };
    document.body.appendChild(btn);
  }
});
