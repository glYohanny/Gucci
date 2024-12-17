// Variables globales
let currentInterlocutorData = null;
let ordenesData = [];
const rowsPerPage = 10;
let currentPage = 1;
const API_BASE = '/api';

document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const interlocutorId = urlParams.get('id');
    const interlocutorTipo = urlParams.get('tipo');

    if (!interlocutorId || !interlocutorTipo) {
        showError('No se proporcionaron los parámetros necesarios');
        setTimeout(() => {
            window.location.href = '/interlocutor';
        }, 2000);
        return;
    }

    fetchInterlocutorData(interlocutorId, interlocutorTipo);
    
    // Configurar búsqueda
    let searchTimeout;
    document.getElementById('searchInput')?.addEventListener('input', function(e) {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            handleSearch(e.target.value);
        }, 300);
    });
});

// Función para obtener los datos del interlocutor
async function fetchInterlocutorData(id, tipo) {
    try {
        console.log(`Fetching data for ${tipo} ${id}`);
        const url = `${API_BASE}/${tipo}/${id}`;
        
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Received data:', data);
        
        currentInterlocutorData = data;
        ordenesData = data.ordenes || [];
        
        updateInterlocutorInfo();
        updateEstadisticas();
        renderOrdenesTable(1);
        renderPagination();
        
    } catch (error) {
        console.error('Error:', error);
        showError('Error al cargar los datos: ' + error.message);
    }
}

// Función para actualizar la información del interlocutor
function updateInterlocutorInfo() {
    if (!currentInterlocutorData?.info_interlocutor) return;
    
    const info = currentInterlocutorData.info_interlocutor;
    document.getElementById('nombreInterlocutor').textContent = info.nombre || '-';
    document.getElementById('tipoInterlocutor').textContent = info.tipo || '-';
    document.getElementById('emailInterlocutor').textContent = info.email || '-';
    document.getElementById('telefonoInterlocutor').textContent = info.telefono || '-';
}

// Función para actualizar las estadísticas
function updateEstadisticas() {
    if (!currentInterlocutorData?.estadisticas) return;
    
    const stats = currentInterlocutorData.estadisticas;
    document.getElementById('totalOrdenes').textContent = stats.total_ordenes || 0;
    
    const valorTotal = (stats.valor_total || 0).toLocaleString('es-CL', {
        style: 'currency',
        currency: 'CLP'
    });
    document.getElementById('valorTotal').textContent = valorTotal;
    
    const ultimaOrden = stats.ultima_orden ? 
        new Date(stats.ultima_orden).toLocaleDateString('es-CL') : 
        'Sin órdenes';
    document.getElementById('ultimaOrden').textContent = ultimaOrden;
}

// Función para renderizar la tabla de órdenes
function renderOrdenesTable(page) {
    const tableBody = document.querySelector("#data-table tbody");
    if (!tableBody) return;
    
    tableBody.innerHTML = '';
    
    if (!ordenesData || ordenesData.length === 0) {
        const tr = document.createElement("tr");
        tr.innerHTML = '<td colspan="5" class="text-center">No hay órdenes disponibles</td>';
        tableBody.appendChild(tr);
        return;
    }

    const startIndex = (page - 1) * rowsPerPage;
    const endIndex = Math.min(startIndex + rowsPerPage, ordenesData.length);
    const paginatedOrdenes = ordenesData.slice(startIndex, endIndex);

    paginatedOrdenes.forEach(orden => {
        const tr = document.createElement("tr");
        tr.setAttribute('data-id', orden.id);
        
        const valor = orden.valor.toLocaleString('es-CL', {
            style: 'currency',
            currency: 'CLP'
        });
        
        const fecha = new Date(orden.fecha).toLocaleDateString('es-CL');
        
        tr.innerHTML = `
            <td>${orden.id}</td>
            <td><div class="tipo-orden ${orden.tipo.toLowerCase()}">${orden.tipo}</div></td>
            <td>${valor}</td>
            <td>${fecha}</td>
            <td><div class="estado ${orden.estado.toLowerCase()}">${orden.estado}</div></td>
        `;
        
        tr.addEventListener('click', () => selectRow(tr));
        tableBody.appendChild(tr);
    });
}

// Función para seleccionar una fila
function selectRow(tr) {
    document.querySelectorAll('#data-table tbody tr').forEach(row => {
        row.classList.remove('selected');
    });
    tr.classList.add('selected');
    
    const orderId = tr.getAttribute('data-id');
    if (orderId) {
        document.getElementById('editarOrden').disabled = false;
        document.getElementById('eliminarOrden').disabled = false;
    }
}

// Función para manejar búsqueda
function handleSearch(searchTerm) {
    if (!currentInterlocutorData?.ordenes) return;
    
    if (!searchTerm) {
        ordenesData = currentInterlocutorData.ordenes;
    } else {
        const searchLower = searchTerm.toLowerCase();
        ordenesData = currentInterlocutorData.ordenes.filter(orden => 
            orden.id.toString().includes(searchLower) ||
            orden.tipo.toLowerCase().includes(searchLower) ||
            orden.estado.toLowerCase().includes(searchLower)
        );
    }
    
    currentPage = 1;
    renderOrdenesTable(currentPage);
    renderPagination();
}

// Función para renderizar paginación
function renderPagination() {
    const pagination = document.querySelector("#pagination");
    if (!pagination) return;
    
    const totalPages = Math.ceil(ordenesData.length / rowsPerPage);
    pagination.innerHTML = '';

    // Si no hay páginas, no mostrar paginación
    if (totalPages <= 1) return;

    // Botón anterior
    const prevButton = document.createElement('button');
    prevButton.textContent = 'Anterior';
    prevButton.classList.add('btn');
    prevButton.disabled = currentPage === 1;
    prevButton.onclick = () => {
        if (currentPage > 1) {
            currentPage--;
            renderOrdenesTable(currentPage);
            renderPagination();
        }
    };
    pagination.appendChild(prevButton);

    // Botones de página
    for (let i = 1; i <= totalPages; i++) {
        const button = document.createElement('button');
        button.textContent = i;
        button.classList.add('btn');
        button.classList.toggle('active', i === currentPage);
        button.onclick = () => {
            currentPage = i;
            renderOrdenesTable(currentPage);
            renderPagination();
        };
        pagination.appendChild(button);
    }

    // Botón siguiente
    const nextButton = document.createElement('button');
    nextButton.textContent = 'Siguiente';
    nextButton.classList.add('btn');
    nextButton.disabled = currentPage === totalPages;
    nextButton.onclick = () => {
        if (currentPage < totalPages) {
            currentPage++;
            renderOrdenesTable(currentPage);
            renderPagination();
        }
    };
    pagination.appendChild(nextButton);
}

// Función para mostrar errores
function showError(message) {
    alert(message);
}