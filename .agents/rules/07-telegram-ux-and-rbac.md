# Telegram User Experience & RBAC Authorization

- **Single Status Bubble Architecture**:
  - NEVER flood the Telegram chat with successive messages for status updates or menu transitions.
  - Always edit existing message text and reply markup (`edit_message_text`) when responding to callback queries or refreshing status.
- **Strict Role-Based Access Control (RBAC)**:
  - Enforce `ALLOWED_USER_IDS` authorization in `telegrambot/core/config.py`.
  - Default-deny all unauthorized incoming updates and commands.
- **Dynamic Emoji and Sticker Fallback**:
  - Dynamically format status badges via `telegrambot/core/dynamic_emojis.py`.
  - When Telegram Premium custom emoji/stickers are unavailable, gracefully fallback to clean unicode symbols or standard text badges.
