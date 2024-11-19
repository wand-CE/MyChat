// Função para verificar o tamanho da tela e aplicar as classes do offcanvas
function adjustChatLayout() {
    // Obtém a referência da div block-chats
    const blockChats = document.querySelector('.block-chats');

    // Verifica a largura da janela
    const windowWidth = window.innerWidth;

    if (windowWidth < 768) {
        // Se a tela for menor que 768px, transforma a div em offcanvas
        if (!blockChats.classList.contains('offcanvas')) {
            // Adiciona classes para tornar a div um offcanvas
            blockChats.classList.add('offcanvas', 'offcanvas-start', 'offcanvas-size'); // Define a largura do offcanvas
            blockChats.setAttribute('tabindex', '-1');
            blockChats.setAttribute('aria-labelledby', 'offcanvasLabel'); // Você pode criar um ID personalizado para o título

            const offcanvasHeader = document.createElement('div');
            offcanvasHeader.classList.add('offcanvas-header');
            offcanvasHeader.innerHTML = `
                <h5 class="offcanvas-title" id="offcanvasChats">Conversas</h5>
                <button type="button" class="btn-close text-reset" data-bs-dismiss="offcanvas" aria-label="Close"></button>
            `;

            // Adiciona o cabeçalho ao top do offcanvas
            blockChats.insertAdjacentElement('afterbegin', offcanvasHeader);
        }

        // Adiciona o botão para abrir o offcanvas (caso não tenha um já definido no HTML)
        if (!document.querySelector('#openOffcanvasButton')) {
            const openButton = document.createElement('button');
            openButton.id = 'openOffcanvasButton';
            openButton.classList.add('d-md-none', 'btn', 'rounded-circle', 'position-absolute', 'text-white', 'border');
            openButton.style.setProperty('background-color', '#002f5d', 'important');
            openButton.setAttribute('type', 'button');
            openButton.setAttribute('data-bs-toggle', 'offcanvas');
            openButton.setAttribute('data-bs-target', '.block-chats');

            // Adiciona o ícone de chat ao botão
            openButton.innerHTML = '<i class="bi bi-chat-dots" style="font-size: 1.5rem;"></i>';

            // Adiciona o botão ao corpo da página
            document.body.appendChild(openButton);
        }

    } else {
        // Se a tela for maior que 768px, remove as classes de offcanvas
        if (blockChats.classList.contains('offcanvas')) {
            blockChats.classList.remove('offcanvas', 'offcanvas-start', 'offcanvas-size');
        }

        // Remove o botão de abrir o offcanvas (se houver)
        const openButton = document.querySelector('#openOffcanvasButton');
        if (openButton) {
            openButton.remove();
        }

        // Remove o cabeçalho do offcanvas (se houver)
        const offcanvasHeader = document.querySelector('.offcanvas-header');
        if (offcanvasHeader) {
            offcanvasHeader.remove();
        }
    }
}

document.addEventListener('DOMContentLoaded', function () {
    adjustChatLayout();
});

window.addEventListener('resize', function () {
    adjustChatLayout();
});
