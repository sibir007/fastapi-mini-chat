document.addEventListener(
    'DOMContentLoaded',
    domLoadEventListener
)

async function domLoadEventListener(event) {
    const users_container = document.querySelector('.users-container')
    const userItems = [];
    // const userItems = document.querySelectorAll('.user-item');
    const messageInput = document.querySelector('.message-input');
    const chatHistory = document.querySelector('.chat-history');
    const selectChatMessage = document.querySelector('.select-chat-message');
    const selectedUser = document.querySelector('.selected-user');
    const input = document.querySelector('.message-input input');
    const sendButton = document.querySelector('.message-input button');
    const logoutButton = document.querySelector('.logout-btn');
    let activUserId = null;
    // let websocket = null;
    
    // Chat histories for each user
    // let chatHistories = {};


    const me = await get_me();
    if (!me) {
        return
    }
    

    const interlocutors = await get_interlocutors();
    if (!interlocutors) {
        return
    }

    fill_user_container(users_container, interlocutors, userItems);

    const messages = await get_messages();
    if (!messages) {
        return
    }

    // Chat histories for each user
    const chatHistories = convert_messages_to_chatHistory(messages)

    userItems.forEach(user => {
        // users_container.childNodes.forEach( user => {
        user.addEventListener('click', function () {
            activUserId = this.getAttribute('user-id');
            // userElement.getAttribute('user_id')
            // console.info(userId)

            userItems.forEach(i => i.classList.remove('active'));
            // userItems.forEach(i => i.classList.remove('active'));
            this.classList.add('active');

            // Show selected user name
            // selectedUser.textContent = `Чат с ${userName}`;
            // selectedUser.style.display = 'block';

            // Show chat history and message input, hide select message
            chatHistory.style.display = 'block';
            messageInput.style.display = 'flex';
            selectChatMessage.style.display = 'none';

            // Display chat history for selected user
            displayChatHistory(activUserId, chatHistory, chatHistories);
        });
    });

    async function sendMessageEventListenr() {
        const message = input.value.trim();
        if (message) {
            const activeUser = document.querySelector('.user-item.active');
            if (activeUser) {
                const userId = activeUser.getAttribute('user-id');
                // const userName = activeUser.textContent;
                const response = await fetch(
                    '/api_v1/chat/send_message/',
                    {
                        method: 'POST',
                        headers: {"Content-Type": "application/json"},
                        body: JSON.stringify({
                            interlocutor_id: userId,
                            content: message
                            // email: email.value,
                            // password: password.value,
                            // password_check: confirmPassword.value,
                            // name: name.value
                          })
                    }
                )
    
                const result = await response.json()
        
                if (response.ok) {
                    input.value = '';
                } else {
                    alert(result.message || result.detail || 'Ошибка выполнения запроса')
                    // window.location.href = '/chat/login'
                }
    
                // // Add message to chat history array
                // if (!chatHistories[userId]) {
                //     chatHistories[userId] = [];
                // }
                // messages[userId].push({ type: 'sent', text: message });
    
                // // Create and display message element
                // const messageElement = document.createElement('div');
                // messageElement.classList.add('message', 'sent');
                // messageElement.textContent = message;
                // chatHistory.appendChild(messageElement);
    
                // input.value = '';
                // chatHistory.scrollTop = chatHistory.scrollHeight;
            }
        }
    }

    sendButton.addEventListener('click', sendMessageEventListenr);

    input.addEventListener('keypress', async function (e) {
        if (e.key === 'Enter') {
            await sendMessageEventListenr();
        }
    });

    logoutButton.addEventListener('click', async function () {
        
        if (websocket) {
            websocket.send('close')
            // websocket.close()
        }
        
        const response = await fetch(
            '/api_v1/auth/logout/',
            {
                method: 'POST'
                // ,
                // headers: {"Content-Type": "application/json"},
                // body: JSON.stringify({
                //     email: email.value,
                //     password: password.value,
                //     password_check: confirmPassword.value,
                //     name: name.value
                //   })
            }
        );
        window.location.href = '/chat'

        // const result = await response.json();

        // if (response.ok) {
        //     document.getElementById('registrationForm').reset();
        //     window.location.href = '/chat/login'
        // } else {
        //     alert(result.message || result.detail || 'Ошибка выполнения запроса')
        // }

        // window.location.href = "login.html";
    });

    
    // await connecAndConfigurtWebSocket(websocket, activUserId, chatHistories, chatHistory, me.id);
    // const websocket = await connecAndConfigurtWebSocket(activUserId, chatHistories, chatHistory, me.id);
    const websocket = new WebSocket(`ws://localhost:8000/ws/connect?user_id=${me.id}`);

    websocket.onopen = () => console.info(`websocket соединение установлено`);
    websocket.onmessage = (event) => {
        console.info(`websocket.onmessage = (event) => {`)
        const in_message = JSON.parse(event.data);
        const message_type = in_message.type
        if (message_type == 'new_message') {
            process_new_message_message(in_message, activUserId, chatHistories, chatHistory)
        }
        else if (message_type == 'new_user') {
            process_new_user_message(in_message)
        }
        else {
            alert(`Не поддерживаемый тип сообщения: ${message_type}`)
        }
    }
    websocket.onclose = (event) => {
        console.info(`[close] Соединение закрыто, код=${event.code} причина=${event.reason}`);
    }
    websocket.onerror = (e) => {
        console.error(e)
    }




}

async function connecAndConfigurtWebSocket(activUserId, chatHistories, chatHistory, me_id) {
    // async function connecAndConfigurtWebSocket(websocket, activUserId, chatHistories, chatHistory, me_id) {
    // if (websocket) {
    // }
    // if (websocket) {
    //     websocket.close();
    // }
    console.info(window.location.host)
    // const websocket = new WebSocket(`ws://${window.location.host}/ws/connect`)
    const websocket = new WebSocket(`ws://localhost:8000/items/item_id/ws`);

    websocket.onopen = () => console.info(`websocket соединение установлено`);
    websocket.onmessage = (event) => {
        const in_message = JSON.parse(event.data);
        const message_type = in_message.type
        if (message_type == 'new_message') {
            process_new_message_message(in_message, activUserId, chatHistories, chatHistory)
        }
        else if (message_type == 'new_user') {
            process_new_user_message(in_message)
        }
        else {
            alert(`Не поддерживаемый тип сообщения: ${message_type}`)
        }
    }
    websocket.onclose = (event) => {
        console.info(`[close] Соединение закрыто, код=${event.code} причина=${event.reason}`);
    }
    websocket.onerror = (e) => {
        console.error(e)
    }

    return websocket
   
}

function process_new_user_message(in_message) {

}

function process_new_message_message(in_message, activUserId, chatHistories, chatHistory){
    ms = in_message.message
    add_message_to_chat_Histories(ms, chatHistories)
    if (ms.interlocutor_id == activUserId){
        add_message_to_chat_chistory(ms, chatHistory, true)
    }

}


async function get_me() {
    const me_response = await fetch(
        '/api_v1/users/me',
        { method: 'GET' }
    );

    const me_result = await me_response.json();

    if (!me_response.ok) {
        alert(me_result.message || me_result.detail || 'Ошибка выполнения запроса авторизации')
        window.location.href = '/chat/login'
        return
        //     document.getElementById('registrationForm').reset();
        // } else {
        // }
    }

    // console.info(`user id: ${me_result.id}`)
    return me_result
}

async function get_interlocutors() {

    const interlocutors_response = await fetch(
        '/api_v1/users/all_interlocutors',
        { method: 'GET' }
    )

    const interlocutors_result = await interlocutors_response.json()

    if (!interlocutors_response.ok) {
        alert(
            interlocutors_result.message
            || interlocutors_result.detail
            || 'Ошибка выполнения запроса собеседников'
        )
        return
    }

    // console.info(`interlocutors_result ${JSON.stringify(interlocutors_result)}`)
    return interlocutors_result
}

function fill_user_container(users_container, interlocutors, userItems) {
    interlocutors.forEach(
        user => {
            const userElement = document.createElement('div');
            userElement.classList.add('user-item');
            userElement.setAttribute('user-id', user.id);
            userElement.textContent = user.email;
            users_container.appendChild(userElement)
            userItems.push(userElement)
            // userElement.attri
        }
    );
}

function displayChatHistory(activUserId, chatHistory, chatHistories) {
    chatHistory.innerHTML = ''; // Clear current chat history
    // console.info(`userId: ${userId}`)
    const messages = chatHistories[activUserId];
    // console.info(`displayChatHistory(userId, chatHistory, chatHistories) messages: ${messages}`)
    if (messages) {
        messages.forEach(message => add_message_to_chat_chistory(message, chatHistory));
    }
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

function add_message_to_chat_chistory(message, chatHistory, scrollTop=false) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', message.type);
    messageElement.textContent = message.text;
    chatHistory.appendChild(messageElement);
    if (scrollTop) {
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }
}


async function get_messages() {
    const messages_response = await fetch(
        '/api_v1/chat/messages',
        { method: 'GET' }
    );

    const messages_result = await messages_response.json();

    if (!messages_response.ok) {
        alert(
            messages_result.message
            || messages_result.detail
            || 'Ошибка выполнения запроса истории сообщений'
        );
        return;
    }

    // console.info(`messages_result ${JSON.stringify(messages_result)}`);
    return messages_result;

}

function convert_messages_to_chatHistory(messages) {
    
    /* in message format
        {
            type: str 'received' or 'sent'
            created: datetime
            interlocutor_id: int
            content: str
        }
    */

    const chatHistories = {};
    // let ms = [];

    messages.forEach(ms => add_message_to_chat_Histories(ms, chatHistories));


    // console.info(chatHistories)
    return chatHistories;
}

function add_message_to_chat_Histories(ms, chatHistories){
    
    if (!chatHistories[ms.interlocutor_id]) {
        chatHistories[ms.interlocutor_id] = []
    }

    chatHistories[ms.interlocutor_id].push({ type: ms.type, created: ms.created, text: ms.content })
}

// if (interlocutors_result) {
//     interlocutors_result.forEach(user => {
//         const userElement = document.createElement('div');
//         messageElement.classList.add('message', 'sent');
//         messageElement.textContent = message;
//         chatHistory.appendChild(messageElement);

//     })
//     const activeUser = document.querySelector('.user-item.active');
//     if (activeUser) {
//         const userName = activeUser.textContent;

//         // Add message to chat history array
//         if (!chatHistories[userName]) {
//             chatHistories[userName] = [];
//         }
//         chatHistories[userName].push({ type: 'sent', text: message });

//         // Create and display message element
//         const messageElement = document.createElement('div');
//         messageElement.classList.add('message', 'sent');
//         messageElement.textContent = message;
//         chatHistory.appendChild(messageElement);

//         input.value = '';
//         chatHistory.scrollTop = chatHistory.scrollHeight;
//     }
// }

// }


document.addEventListener('DOM', function () {
    const userItems = document.querySelectorAll('.user-item');
    const messageInput = document.querySelector('.message-input');
    const chatHistory = document.querySelector('.chat-history');
    const selectChatMessage = document.querySelector('.select-chat-message');
    const selectedUser = document.querySelector('.selected-user');
    const input = document.querySelector('.message-input input');
    const sendButton = document.querySelector('.message-input button');
    const logoutButton = document.querySelector('.logout-btn');

    // Chat histories for each user
    const chatHistories = {
        'John Doe': [
            { type: 'received', text: 'Hey, how are you?' },
            { type: 'sent', text: 'I\'m good, thanks! How about you?' },
            { type: 'received', text: 'Great! Would you like to grab lunch?' }
        ],
        'Jane Smith': [
            { type: 'received', text: 'Did you finish the project?' },
            { type: 'sent', text: 'Yes, I just sent it to you' },
            { type: 'received', text: 'Perfect, thanks!' }
        ],
        'Mike Johnson': [
            { type: 'sent', text: 'Are we still meeting today?' },
            { type: 'received', text: 'Yes, at 3 PM' },
            { type: 'sent', text: 'Great, see you then!' }
        ],
        'Sarah Williams': [
            { type: 'received', text: 'Happy Birthday!' },
            { type: 'sent', text: 'Thank you so much!' },
            { type: 'received', text: 'Hope you have a great day!' }
        ],
        'David Brown': [
            { type: 'sent', text: 'Can you send me those files?' },
            { type: 'received', text: 'Sure, sending them now' },
            { type: 'sent', text: 'Got them, thanks!' }
        ]
    };

    function displayChatHistory(userName) {
        chatHistory.innerHTML = ''; // Clear current chat history
        const messages = chatHistories[userName];
        if (messages) {
            messages.forEach(message => {
                const messageElement = document.createElement('div');
                messageElement.classList.add('message', message.type);
                messageElement.textContent = message.text;
                chatHistory.appendChild(messageElement);
            });
        }
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    userItems.forEach(item => {
        item.addEventListener('click', function () {
            const userName = this.textContent;

            userItems.forEach(i => i.classList.remove('active'));
            this.classList.add('active');

            // Show selected user name
            selectedUser.textContent = `Чат с ${userName}`;
            selectedUser.style.display = 'block';

            // Show chat history and message input, hide select message
            chatHistory.style.display = 'block';
            messageInput.style.display = 'flex';
            selectChatMessage.style.display = 'none';

            // Display chat history for selected user
            displayChatHistory(userName);
        });
    });

    function sendMessage() {
        const message = input.value.trim();
        if (message) {
            const activeUser = document.querySelector('.user-item.active');
            if (activeUser) {
                const userName = activeUser.textContent;

                // Add message to chat history array
                if (!chatHistories[userName]) {
                    chatHistories[userName] = [];
                }
                chatHistories[userName].push({ type: 'sent', text: message });

                // Create and display message element
                const messageElement = document.createElement('div');
                messageElement.classList.add('message', 'sent');
                messageElement.textContent = message;
                chatHistory.appendChild(messageElement);

                input.value = '';
                chatHistory.scrollTop = chatHistory.scrollHeight;
            }
        }
    }

    sendButton.addEventListener('click', sendMessage);
    input.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    logoutButton.addEventListener('click', async function () {
        const response = await fetch(
            '/api_v1/auth/logout/',
            {
                method: 'POST'
                // ,
                // headers: {"Content-Type": "application/json"},
                // body: JSON.stringify({
                //     email: email.value,
                //     password: password.value,
                //     password_check: confirmPassword.value,
                //     name: name.value
                //   })
            }
        );
        window.location.href = '/chat'

        // const result = await response.json();

        // if (response.ok) {
        //     document.getElementById('registrationForm').reset();
        //     window.location.href = '/chat/login'
        // } else {
        //     alert(result.message || result.detail || 'Ошибка выполнения запроса')
        // }

        // window.location.href = "login.html";
    });
});

