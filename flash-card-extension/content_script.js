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

const createButtons = () => {
  if (document.getElementById('flashcard-buttons-container')) return;

  // Check if we're on ChatGPT
  const isChatGPT = window.location.hostname.includes('chat.openai.com') ||
    window.location.hostname.includes('chatgpt.com');

  // Create container for buttons
  const container = document.createElement('div');
  container.id = 'flashcard-buttons-container';
  container.style.position = 'fixed';
  container.style.bottom = '20px';
  container.style.right = '20px';
  container.style.zIndex = '10000';
  container.style.display = 'flex';
  container.style.flexDirection = 'column';
  container.style.gap = '10px';

  // Button for conversation flashcards (only on ChatGPT)
  if (isChatGPT) {
    const conversationBtn = document.createElement('button');
    conversationBtn.id = 'makeFlashcardButton';
    conversationBtn.innerText = '💬 Chat → Cards';
    conversationBtn.style.padding = '10px 16px';
    conversationBtn.style.backgroundColor = '#007bff';
    conversationBtn.style.color = 'white';
    conversationBtn.style.border = 'none';
    conversationBtn.style.borderRadius = '8px';
    conversationBtn.style.cursor = 'pointer';
    conversationBtn.style.fontSize = '14px';
    conversationBtn.style.fontWeight = '500';
    conversationBtn.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.2)';

    conversationBtn.onclick = async () => {
      const conversation = extractMessages();
      if (conversation.length === 0) {
        // Temporarily show error state
        const originalText = conversationBtn.innerText;
        const originalBg = conversationBtn.style.backgroundColor;

        conversationBtn.innerText = '❌ No Chat Found';
        conversationBtn.style.backgroundColor = '#dc3545';

        setTimeout(() => {
          conversationBtn.innerText = originalText;
          conversationBtn.style.backgroundColor = originalBg;
        }, 2000);
        return;
      }

      // Show loading state
      const originalText = conversationBtn.innerText;
      const originalBg = conversationBtn.style.backgroundColor;
      conversationBtn.innerText = '⏳ Sending...';
      conversationBtn.style.backgroundColor = '#6c757d';
      conversationBtn.disabled = true;

      try {
        const response = await fetch('http://localhost:8000/flashcards', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ conversation, destination: 'anki' })
        });

        const data = await response.json();

        if (response.ok && data.status === 'success') {
          // Show success state
          conversationBtn.innerText = '✅ Sent!';
          conversationBtn.style.backgroundColor = '#28a745';

          // Reset after 3 seconds
          setTimeout(() => {
            conversationBtn.innerText = originalText;
            conversationBtn.style.backgroundColor = originalBg;
            conversationBtn.disabled = false;
          }, 3000);
        } else {
          // Show error state
          conversationBtn.innerText = '❌ Failed';
          conversationBtn.style.backgroundColor = '#dc3545';

          // Reset after 3 seconds
          setTimeout(() => {
            conversationBtn.innerText = originalText;
            conversationBtn.style.backgroundColor = originalBg;
            conversationBtn.disabled = false;
          }, 3000);
        }
      } catch (error) {
        console.error('Error sending flashcard:', error);

        // Show connection error state
        conversationBtn.innerText = '❌ No Connection';
        conversationBtn.style.backgroundColor = '#dc3545';

        // Reset after 3 seconds
        setTimeout(() => {
          conversationBtn.innerText = originalText;
          conversationBtn.style.backgroundColor = originalBg;
          conversationBtn.disabled = false;
        }, 3000);
      }
    };

    container.appendChild(conversationBtn);
  }

  // Button for text input flashcards (on all sites)
  const textBtn = document.createElement('button');
  textBtn.id = 'textFlashcardButton';
  textBtn.innerText = '📝 Text → Cards';
  textBtn.style.padding = '10px 16px';
  textBtn.style.backgroundColor = '#28a745';
  textBtn.style.color = 'white';
  textBtn.style.border = 'none';
  textBtn.style.borderRadius = '8px';
  textBtn.style.cursor = 'pointer';
  textBtn.style.fontSize = '14px';
  textBtn.style.fontWeight = '500';
  textBtn.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.2)';

  textBtn.onclick = () => {
    showTextInputModal();
  };

  container.appendChild(textBtn);
  document.body.appendChild(container);
};

const showTextInputModal = () => {
  // Remove existing panel if present
  const existingPanel = document.getElementById('text-flashcard-panel');
  if (existingPanel) {
    existingPanel.remove();
  }

  // Create side panel directly (no overlay)
  const panel = document.createElement('div');
  panel.id = 'text-flashcard-panel';
  panel.style.position = 'fixed';
  panel.style.top = '0';
  panel.style.right = '0';
  panel.style.width = '420px';
  panel.style.height = '100vh';
  panel.style.backgroundColor = 'white';
  panel.style.borderLeft = '1px solid #e1e5e9';
  panel.style.padding = '0';
  panel.style.overflow = 'hidden';
  panel.style.boxShadow = '-4px 0 20px rgba(0, 0, 0, 0.15)';
  panel.style.display = 'flex';
  panel.style.flexDirection = 'column';
  panel.style.transform = 'translateX(100%)';
  panel.style.transition = 'transform 0.3s ease-out';
  panel.style.zIndex = '20000';
  panel.style.fontFamily = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';

  panel.innerHTML = `
    <div style="padding: 20px; border-bottom: 1px solid #e1e5e9; background: #f8f9fa; flex-shrink: 0;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
        <h2 style="margin: 0; color: #333; font-size: 20px;">📝 Text to Flashcards</h2>
        <button id="close-btn" style="background: none; border: none; font-size: 24px; cursor: pointer; color: #666; padding: 4px; line-height: 1; border-radius: 4px;" onmouseover="this.style.background='#e9ecef'" onmouseout="this.style.background='none'">×</button>
      </div>
      <p style="margin: 0; color: #666; font-size: 14px; line-height: 1.4;">Copy text from this page and paste below to generate flashcards</p>
    </div>

    <div style="flex: 1; overflow-y: auto; padding: 20px;">
      <form id="text-flashcard-form" style="height: 100%; display: flex; flex-direction: column;">
        <div style="margin-bottom: 16px; flex: 1; display: flex; flex-direction: column;">
          <label style="display: block; margin-bottom: 8px; font-weight: 600; color: #333; font-size: 14px;">Text Content:</label>
          <textarea id="text-input" placeholder="Select and copy text from anywhere on this page (you can scroll and interact with the main page), then paste it here to generate flashcards!"
            style="width: 100%; flex: 1; min-height: 250px; padding: 12px; border: 2px solid #e1e5e9; border-radius: 8px; font-family: inherit; font-size: 14px; resize: none; box-sizing: border-box; line-height: 1.5; color: black; background-color: white;"
            required></textarea>
          <div style="margin-top: 8px; font-size: 13px; color: #666; display: flex; justify-content: space-between;">
            <span>Words: <span id="word-count">0</span></span>
            <span>Recommended: <span id="recommended-cards">5</span> cards</span>
          </div>
        </div>

        <div style="display: flex; gap: 12px; margin-bottom: 16px;">
          <div style="flex: 1;">
            <label style="display: block; margin-bottom: 6px; font-weight: 600; color: #333; font-size: 14px;">Cards (Optional):</label>
            <input type="number" id="card-count" value="5" min="1" max="50"
              style="width: 100%; padding: 8px; border: 2px solid #e1e5e9; border-radius: 6px; box-sizing: border-box; font-size: 14px; background-color: white; color: black;">
          </div>
          <div style="flex: 1;">
            <label style="display: block; margin-bottom: 6px; font-weight: 600; color: #333; font-size: 14px;">Export to:</label>
            <select id="destination" style="width: 100%; padding: 8px; border: 2px solid #e1e5e9; border-radius: 6px; box-sizing: border-box; font-size: 14px; background-color: white; color: black;" required>
              <option value="anki" selected>Anki</option>
              <option value="notion">Notion</option>
            </select>
          </div>
        </div>

        <div style="margin-bottom: 20px;">
          <label style="display: block; margin-bottom: 6px; font-weight: 600; color: #333; font-size: 14px;">Topic (Optional):</label>
          <input type="text" id="topic" placeholder="e.g., Biology, History, Programming..."
            style="width: 100%; padding: 8px; border: 2px solid #e1e5e9; border-radius: 6px; box-sizing: border-box; font-size: 14px; background-color: white; color: black;">
        </div>

        <div style="display: flex; gap: 10px;">
          <button type="button" id="cancel-btn" style="flex: 1; padding: 12px 16px; background: #6c757d; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 14px;">
            Cancel
          </button>
          <button type="submit" id="generate-btn" style="flex: 2; padding: 12px 16px; background: #28a745; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; font-size: 14px;">
            🚀 Generate Cards
          </button>
        </div>
      </form>
    </div>
  `;

  document.body.appendChild(panel);

  // Animate the panel sliding in
  requestAnimationFrame(() => {
    panel.style.transform = 'translateX(0)';
  });

  // Add event listeners
  const textInput = document.getElementById('text-input');
  const wordCountSpan = document.getElementById('word-count');
  const recommendedCardsSpan = document.getElementById('recommended-cards');
  const cardCountInput = document.getElementById('card-count');

  // Update word count and recommendations
  textInput.addEventListener('input', () => {
    const text = textInput.value.trim();
    const words = text ? text.split(/\s+/).length : 0;
    const recommended = Math.max(1, Math.ceil(words / 100));

    wordCountSpan.textContent = words;
    recommendedCardsSpan.textContent = recommended;

    // Auto-update card count
    if (cardCountInput.value == cardCountInput.defaultValue ||
      cardCountInput.value == Math.ceil((words - 100) / 100)) {
      cardCountInput.value = Math.min(50, recommended);
    }
  });

  // Force black text on paste by removing any formatting
  textInput.addEventListener('paste', (e) => {
    e.preventDefault();

    // Get plain text from clipboard
    const pastedText = (e.clipboardData || window.clipboardData).getData('text');

    // Insert at cursor position or replace selection
    const start = textInput.selectionStart;
    const end = textInput.selectionEnd;
    const currentValue = textInput.value;

    textInput.value = currentValue.substring(0, start) + pastedText + currentValue.substring(end);
    textInput.setSelectionRange(start + pastedText.length, start + pastedText.length);

    // Trigger input event to update word count
    textInput.dispatchEvent(new Event('input'));
  });

  // Form submission
  document.getElementById('text-flashcard-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const generateBtn = document.getElementById('generate-btn');
    const originalText = generateBtn.textContent;

    try {
      generateBtn.textContent = '⏳ Generating...';
      generateBtn.disabled = true;

      const formData = {
        text: textInput.value.trim(),
        destination: document.getElementById('destination').value,
        card_count: parseInt(cardCountInput.value),
        topic: document.getElementById('topic').value.trim() || null
      };

      const response = await fetch('http://localhost:8000/flashcards/from-text', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      if (response.ok && data.status === 'success') {
        // Show success state
        generateBtn.textContent = '✅ Cards Sent!';
        generateBtn.style.backgroundColor = '#28a745';

        // Auto-close panel after showing success
        setTimeout(() => {
          closePanel();
        }, 1500);
      } else {
        // Show error state
        generateBtn.textContent = '❌ Failed';
        generateBtn.style.backgroundColor = '#dc3545';

        // Reset button after 3 seconds
        setTimeout(() => {
          generateBtn.textContent = originalText;
          generateBtn.style.backgroundColor = '#28a745';
          generateBtn.disabled = false;
        }, 3000);
      }
    } catch (error) {
      console.error('Error:', error);

      // Show connection error state
      generateBtn.textContent = '❌ No Connection';
      generateBtn.style.backgroundColor = '#dc3545';

      // Reset button after 3 seconds
      setTimeout(() => {
        generateBtn.textContent = originalText;
        generateBtn.style.backgroundColor = '#28a745';
        generateBtn.disabled = false;
      }, 3000);
    }
  });

  // Close panel function with animation
  const closePanel = () => {
    panel.style.transform = 'translateX(100%)';
    setTimeout(() => panel.remove(), 300);
  };

  // Close button (X)
  document.getElementById('close-btn').addEventListener('click', closePanel);

  // Cancel button
  document.getElementById('cancel-btn').addEventListener('click', closePanel);

  // Close on Escape key
  const escapeHandler = (e) => {
    if (e.key === 'Escape') {
      closePanel();
      document.removeEventListener('keydown', escapeHandler);
    }
  };
  document.addEventListener('keydown', escapeHandler);

  // Focus on textarea
  setTimeout(() => textInput.focus(), 100);
};

// Observe DOM mutations and ensure the buttons stay
const observer = new MutationObserver(createButtons);
observer.observe(document.body, { childList: true, subtree: true });

// Initial call
createButtons();
