document.addEventListener('DOMContentLoaded', () => {
    const themeToggleBtn = document.querySelector('.theme-toggle');
    const body = document.body;
    const themeIcon = themeToggleBtn.querySelector('.material-symbols-rounded');

    // Check for saved theme
    const savedTheme = localStorage.getItem('hive-theme');
    if (savedTheme) {
        body.className = savedTheme;
        updateThemeIcon(savedTheme);
    }

    themeToggleBtn.addEventListener('click', () => {
        if (body.classList.contains('light-theme')) {
            body.classList.replace('light-theme', 'dark-theme');
            localStorage.setItem('hive-theme', 'dark-theme');
            updateThemeIcon('dark-theme');
        } else {
            body.classList.replace('dark-theme', 'light-theme');
            localStorage.setItem('hive-theme', 'light-theme');
            updateThemeIcon('light-theme');
        }
    });

    function updateThemeIcon(theme) {
        if (theme === 'dark-theme') {
            themeIcon.textContent = 'light_mode';
        } else {
            themeIcon.textContent = 'dark_mode';
        }
    }

    // Profile Modal Logic
    const userProfileBtn = document.getElementById('userProfileBtn');
    const profileModal = document.getElementById('profileModal');
    const closeProfileBtn = document.getElementById('closeProfileBtn');

    if (userProfileBtn && profileModal && closeProfileBtn) {
        userProfileBtn.addEventListener('click', (e) => {
            e.preventDefault();
            profileModal.classList.add('active');
        });

        closeProfileBtn.addEventListener('click', () => {
            profileModal.classList.remove('active');
        });

        profileModal.addEventListener('click', (e) => {
            if (e.target === profileModal) {
                profileModal.classList.remove('active');
            }
        });
    }

    // Notification Dropdown Logic
    const notificationBtn = document.getElementById('notificationBtn');
    const notificationsDropdown = document.getElementById('notificationsDropdown');

    if (notificationBtn && notificationsDropdown) {
        notificationBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            notificationsDropdown.classList.toggle('active');

            // Close profile modal if open
            if (profileModal) profileModal.classList.remove('active');
        });

        document.addEventListener('click', (e) => {
            if (!notificationBtn.contains(e.target) && !notificationsDropdown.contains(e.target)) {
                notificationsDropdown.classList.remove('active');
            }
        });
    }

    // Messages Page Interactivity
    const threadItems = document.querySelectorAll('.thread-item');
    const chatName = document.getElementById('chatName');
    const chatSubtitle = document.getElementById('chatSubtitle');
    const messageHistory = document.getElementById('messageHistory');
    const messageInput = document.getElementById('messageInput');
    const sendMessageBtn = document.getElementById('sendMessageBtn');

    if (threadItems.length > 0 && chatName && messageHistory && messageInput && sendMessageBtn) {
        const chats = {
            'prof-smith': {
                name: 'Prof. Smith',
                subtitle: 'Computer Science Dept',
                messages: [
                    { type: 'received', text: 'Today, 9:00 AM', isDate: true },
                    { type: 'sent', text: 'Hi Professor, I had a quick question regarding the data set for Assignment 1. Are we allowed to use the Pandas library for the initial data cleaning, or should we build custom parsers?', time: '09:15 AM - Delivered' },
                    { type: 'received', text: 'Yes, you can use Pandas for data wrangling. In fact, I encourage it! The focus of this assignment is on the core logic after perfectly cleaning up the schema.', time: '10:30 AM' }
                ]
            },
            'cs101': {
                name: 'Study Group: CS101',
                subtitle: '3 members active',
                messages: [
                    { type: 'received', text: 'Yesterday', isDate: true },
                    { type: 'received', text: 'Are we meeting at the library at 5?', time: '04:20 PM' },
                    { type: 'sent', text: 'I might be a bit late, finishing my lab.', time: '04:25 PM - Delivered' }
                ]
            }
        };

        function renderMessages(threadId) {
            const chat = chats[threadId];
            chatName.textContent = chat.name;
            chatSubtitle.textContent = chat.subtitle;
            messageHistory.innerHTML = '';

            chat.messages.forEach(msg => {
                if (msg.isDate) {
                    const dateDiv = document.createElement('div');
                    dateDiv.style.display = 'flex';
                    dateDiv.style.justifyContent = 'center';
                    dateDiv.innerHTML = `<div style="background: var(--bg-main); color: var(--text-muted); padding: 0.25rem 1rem; border-radius: 20px; font-size: 0.75rem; border: 1px solid var(--border-color);">${msg.text}</div>`;
                    messageHistory.appendChild(dateDiv);
                } else {
                    const msgDiv = document.createElement('div');
                    msgDiv.className = 'message-wrapper';
                    msgDiv.style.alignSelf = msg.type === 'sent' ? 'flex-end' : 'flex-start';
                    msgDiv.style.maxWidth = '70%';
                    msgDiv.style.position = 'relative';
                    msgDiv.style.group = 'true';

                    const bubbleStyle = msg.type === 'sent'
                        ? 'background: var(--primary-color); color: white; padding: 1rem; border-radius: 16px 16px 0 16px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);'
                        : 'background: var(--bg-main); border: 1px solid var(--border-color); padding: 1rem; border-radius: 16px 16px 16px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.05);';

                    const timeAlign = msg.type === 'sent' ? 'text-align: right;' : '';
                    const deleteBtnPos = msg.type === 'sent' ? 'left: -35px;' : 'right: -35px;';

                    msgDiv.innerHTML = `
                        <div style="${bubbleStyle}">${msg.text}</div>
                        <div style="font-size: 0.7rem; color: var(--text-muted); margin-top: 0.25rem; ${timeAlign}">${msg.time}</div>
                        <button class="delete-msg-btn" data-index="${chat.messages.indexOf(msg)}" 
                                style="position: absolute; top: 10px; ${deleteBtnPos} background: none; border: none; color: var(--danger-color); cursor: pointer; padding: 5px; opacity: 0; transition: opacity 0.2s;">
                            <span class="material-symbols-rounded" style="font-size: 1.2rem;">delete</span>
                        </button>
                    `;

                    // Hover effect for delete button
                    msgDiv.addEventListener('mouseenter', () => {
                        msgDiv.querySelector('.delete-msg-btn').style.opacity = '1';
                    });
                    msgDiv.addEventListener('mouseleave', () => {
                        msgDiv.querySelector('.delete-msg-btn').style.opacity = '0';
                    });

                    messageHistory.appendChild(msgDiv);
                }
            });

            // Handle deletion
            document.querySelectorAll('.delete-msg-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const index = parseInt(e.currentTarget.dataset.index);
                    const activeThread = document.querySelector('.thread-item.active').dataset.threadId;
                    chats[activeThread].messages.splice(index, 1);
                    renderMessages(activeThread);
                });
            });

            messageHistory.scrollTop = messageHistory.scrollHeight;
        }

        threadItems.forEach(item => {
            item.addEventListener('click', () => {
                threadItems.forEach(i => {
                    i.classList.remove('active');
                    i.style.background = 'transparent';
                    i.style.borderLeft = 'none';
                });
                item.classList.add('active');
                item.style.background = 'rgba(37, 99, 235, 0.05)';
                item.style.borderLeft = '3px solid var(--primary-color)';

                renderMessages(item.dataset.threadId);
            });
        });

        function sendMessage() {
            const text = messageInput.value.trim();
            if (!text) return;

            const activeThread = document.querySelector('.thread-item.active').dataset.threadId;
            const now = new Date();
            const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) + ' - Sent';

            chats[activeThread].messages.push({
                type: 'sent',
                text: text,
                time: timeStr
            });

            messageInput.value = '';
            renderMessages(activeThread);
        }

        sendMessageBtn.addEventListener('click', sendMessage);
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });

        // Meeting Assistant Logic
        const startMeetingBtn = document.getElementById('startMeetingBtn');
        if (startMeetingBtn) {
            startMeetingBtn.addEventListener('click', () => {
                const generateRoomId = () => {
                    const chars = 'abcdefghijklmnopqrstuvwxyz';
                    const part = () => Array.from({ length: 4 }, () => chars[Math.floor(Math.random() * chars.length)]).join('');
                    return `${part()}-${part()}-${part()}`;
                };

                const roomId = generateRoomId();
                const url = `https://meet.google.com/${roomId}`;
                const activeThread = document.querySelector('.thread-item.active').dataset.threadId;

                // Create a "Meeting Invite" message type
                const now = new Date();
                const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) + ' - Sent';

                chats[activeThread].messages.push({
                    type: 'sent',
                    text: `Hey, let's hop on a call! 🚀<br><br><a href="${url}" target="_blank" style="display: inline-block; background: white; color: var(--primary-color); padding: 0.5rem 1rem; border-radius: 8px; font-weight: 600; margin-top: 0.5rem; text-decoration: none;">Join Meeting: ${roomId}</a>`,
                    time: timeStr
                });

                renderMessages(activeThread);
                window.open(url, '_blank');
            });
        }
    }
});
