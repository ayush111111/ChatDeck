console.log("Flashcard extension loaded");

const extractMessages = () => {
  const conversationTurns = document.querySelectorAll('article[data-testid^="conversation-turn"]');
  const allMessages = [];

  conversationTurns.forEach(turn => {
    const userMsg = turn.querySelector('[data-message-author-role="user"] .whitespace-pre-wrap');
    if (userMsg) {
      const text = userMsg.innerText.trim();
      if (text) allMessages.push({ role: 'user', content: text });
    }

    const assistantMsg = turn.querySelector('[data-message-author-role="assistant"] .markdown');
    if (assistantMsg) {
      const text = assistantMsg.innerText.trim();
      if (text) allMessages.push({ role: 'assistant', content: text });
    }
  });

  return allMessages;
};

const createButton = () => {
  if (document.getElementById('makeFlashcardButton')) return;

  const btn = document.createElement('button');
  btn.id = 'makeFlashcardButton';
  btn.innerText = 'Make Flashcards';
  btn.style.position = 'fixed';
  btn.style.bottom = '20px';
  btn.style.right = '20px';
  btn.style.zIndex = '10000';
  btn.style.padding = '10px 16px';
  btn.style.backgroundColor = '#007bff';
  btn.style.color = 'white';
  btn.style.border = 'none';
  btn.style.borderRadius = '8px';
  btn.style.cursor = 'pointer';

  btn.onclick = () => {
    const conversation = extractMessages();
    fetch('http://localhost:8000/flashcards', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ conversation, destination: 'notion' })
    })
      .then(() => alert('Full conversation sent!'))
      .catch(err => console.error('Error sending flashcard:', err));
  };

  document.body.appendChild(btn);
};

// Observe DOM mutations and ensure the button stays
const observer = new MutationObserver(createButton);
observer.observe(document.body, { childList: true, subtree: true });

// Initial call
createButton();
