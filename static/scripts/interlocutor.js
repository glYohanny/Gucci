// Variables globales
let data = [];
const rowsPerPage = 10;
let currentPage = 1;
let editMode = false;
let selectedInterlocutorId = null;

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM Content Loaded - Initializing...');
    
    // Inicializar tabla
    initializeTable();
    
    // Configurar búsqueda
    let searchTimeout;
    document.getElementById('searchInput')?.addEventListener('input', function(e) {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            handleSearch(e.target.value);
        }, 300);
    });

    // Configurar botones principales
    document.getElementById('newInterlocutor')?.addEventListener('click', () => openModal('new'));
    document.getElementById('editInterlocutor')?.addEventListener('click', () => openModal('edit'));
    document.getElementById('deleteInterlocutor')?.addEventListener('click', deleteInterlocutor);
    
    // Configurar modal
    document.querySelector('.close-button')?.addEventListener('click', closeModal);
    document.querySelector('.cancel')?.addEventListener('click', closeModal);
    
    // Configurar formulario
    document.getElementById('interlocutorForm')?.addEventListener('submit', async function(e) {
        e.preventDefault();
        await saveInterlocutor(e.target);
    });

    // Event listener para cambio de tipo de interlocutor
    document.getElementById('tipo_interlocutor')?.addEventListener('change', function(e) {
        adjustFormFields(e.target.value);
    });
});

// Funciones de inicialización y carga de datos
async function initializeTable() {
    try {
        console.log('Iniciando carga de datos...');
        const response = await fetch('/api/interlocutor/lista');
        if (!response.ok) {
            console.error('Error en la respuesta:', response.status);
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('Datos recibidos:', result);
        
        data = [...(result.clientes || []), ...(result.proveedores || [])].map(item => ({
            id: item.id,
            nombre: item.nombre_cliente || item.nombre_proveedor,
            empresa: item.empresa_cliente || item.empresa_proveedor,
            tipo: item.nombre_cliente ? 'cliente' : 'proveedor'
        }));
        
        renderTable(1);
        renderPagination();
        
    } catch (error) {
        console.error('Error en initializeTable:', error);
        showError('Error al cargar los datos: ' + error.message);
    }
}

// Funciones de renderizado
function renderTable(page) {
    const tableBody = document.querySelector("#data-table tbody");
    if (!tableBody) return;
    
    tableBody.innerHTML = '';
    
    if (!data || data.length === 0) {
        const tr = document.createElement("tr");
        tr.innerHTML = '<td colspan="3" class="text-center">No hay datos disponibles</td>';
        tableBody.appendChild(tr);
        return;
    }

    const startIndex = (page - 1) * rowsPerPage;
    const endIndex = Math.min(startIndex + rowsPerPage, data.length);
    const paginatedData = data.slice(startIndex, endIndex);

    paginatedData.forEach(item => {
        const tr = document.createElement("tr");
        tr.setAttribute('data-id', item.id);
        tr.setAttribute('data-tipo', item.tipo);
        
        tr.innerHTML = `
            <td>${item.nombre}</td>
            <td>${item.empresa}</td>
            <td class="actions">
                <button onclick="viewDetails(${item.id}, '${item.tipo}')" class="btn-small">
                    Ver detalles
                </button>
            </td>
        `;
        
        tr.addEventListener('click', () => selectRow(tr));
        tableBody.appendChild(tr);
    });
}

function renderPagination() {
    const pagination = document.querySelector("#pagination");
    if (!pagination) return;
    
    const totalPages = Math.ceil(data.length / rowsPerPage);
    pagination.innerHTML = "";

    // Botón anterior
    const prevButton = document.createElement("button");
    prevButton.textContent = "Anterior";
    prevButton.classList.add("btn");
    prevButton.disabled = currentPage === 1;
    prevButton.onclick = () => {
        if (currentPage > 1) {
            currentPage--;
            renderTable(currentPage);
            renderPagination();
        }
    };
    pagination.appendChild(prevButton);

    // Botones de página
    for (let i = 1; i <= totalPages; i++) {
        const button = document.createElement("button");
        button.textContent = i;
        button.classList.add("btn");
        button.classList.toggle("active", i === currentPage);
        button.onclick = () => {
            currentPage = i;
            renderTable(currentPage);
            renderPagination();
        };
        pagination.appendChild(button);
    }

    // Botón siguiente
    const nextButton = document.createElement("button");
    nextButton.textContent = "Siguiente";
    nextButton.classList.add("btn");
    nextButton.disabled = currentPage === totalPages;
    nextButton.onclick = () => {
        if (currentPage < totalPages) {
            currentPage++;
            renderTable(currentPage);
            renderPagination();
        }
    };
    pagination.appendChild(nextButton);
}

// Funciones de manejo de datos
function selectRow(tr) {
    document.querySelectorAll('#data-table tbody tr').forEach(row => {
        row.classList.remove('selected');
    });
    tr.classList.add('selected');
    selectedInterlocutorId = tr.getAttribute('data-id');
    
    document.getElementById('editInterlocutor').disabled = false;
    document.getElementById('deleteInterlocutor').disabled = false;
}

function viewDetails(id, tipo) {
    window.location.href = `/interlocutor/detalle?id=${id}&tipo=${tipo}`;
}

// Funciones del modal
function openModal(mode = 'new') {
    editMode = mode === 'edit';
    const modal = document.getElementById('interlocutorModal');
    modal.style.display = 'block';
    document.querySelector('.modal-title').textContent = 
        editMode ? 'Editar Interlocutor' : 'Nuevo Interlocutor';
    
    if (editMode && selectedInterlocutorId) {
        loadInterlocutorData();
    } else {
        document.getElementById('interlocutorForm').reset();
        document.getElementById('tipo_interlocutor').disabled = false;
    }
}

function closeModal() {
    document.getElementById('interlocutorModal').style.display = 'none';
    document.getElementById('interlocutorForm').reset();
    document.getElementById('tipo_interlocutor').disabled = false;
}

async function loadInterlocutorData() {
    try {
        const selectedRow = document.querySelector(`tr[data-id="${selectedInterlocutorId}"]`);
        const tipo = selectedRow.getAttribute('data-tipo');
        console.log('Cargando datos para:', tipo, selectedInterlocutorId);
        
        const response = await fetch(`/api/interlocutor/${tipo}/${selectedInterlocutorId}`);
        
        if (!response.ok) throw new Error('Error al cargar los datos');
        
        const result = await response.json();
        console.log('Datos recibidos:', result); // Para depuración
        
        // Obtener la información correcta del objeto
        const info = result.info_interlocutor;
        console.log('Info del interlocutor:', info); // Para depuración
        
        // Deshabilitar cambio de tipo en edición
        const tipoSelect = document.getElementById('tipo_interlocutor');
        tipoSelect.value = tipo;
        tipoSelect.disabled = true;
        
        // Rellenar campos según el tipo
        if (tipo === 'cliente') {
            document.getElementById('nombre').value = info.nombre || info.nombre_cliente || '';
            document.getElementById('empresa').value = info.empresa || info.empresa_cliente || '';
        } else {
            document.getElementById('nombre').value = info.nombre || info.nombre_proveedor || '';
            document.getElementById('empresa').value = info.empresa || info.empresa_proveedor || '';
        }
        
        // Rellenar campos comunes
        document.getElementById('email').value = info.email || '';
        document.getElementById('telefono').value = info.telefono || '';
        document.getElementById('direccion').value = info.direccion || '';
        
    } catch (error) {
        console.error('Error completo:', error);
        showError('Error al cargar los datos del interlocutor');
        closeModal();
    }
}

async function saveInterlocutor(form) {
    try {
        const formData = new FormData(form);
        let tipo;
        
        if (editMode) {
            const selectedRow = document.querySelector(`tr[data-id="${selectedInterlocutorId}"]`);
            tipo = selectedRow.getAttribute('data-tipo');
        } else {
            tipo = formData.get('tipo_interlocutor');
        }
        
        if (!tipo) {
            throw new Error('Tipo de interlocutor no especificado');
        }

        // Crear el payload base con todos los campos
        const payload = {
            email: formData.get('email') || '',
            telefono: formData.get('telefono') || '',
            direccion: formData.get('direccion') || '',
        };

        // Agregar campos específicos según el tipo
        if (tipo === 'cliente') {
            payload.nombre_cliente = formData.get('nombre');
            payload.empresa_cliente = formData.get('empresa');
        } else {
            payload.nombre_proveedor = formData.get('nombre');
            payload.empresa_proveedor = formData.get('empresa');
        }

        const endpoint = editMode ? 
            `/api/interlocutor/${tipo}/${selectedInterlocutorId}` : 
            `/api/interlocutor/${tipo}`;

        console.log('Enviando payload:', payload); // Para depuración
        
        const response = await fetch(endpoint, {
            method: editMode ? 'PUT' : 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        const responseData = await response.json();
        console.log('Respuesta del servidor:', responseData); // Para depuración

        if (!response.ok) {
            throw new Error(responseData.error || 'Error al guardar');
        }
        
        showError(editMode ? 'Interlocutor actualizado correctamente' : 'Interlocutor creado correctamente');
        closeModal();
        await initializeTable();
        
    } catch (error) {
        console.error('Error:', error);
        showError('Error al guardar el interlocutor: ' + error.message);
    }
}

async function deleteInterlocutor() {
    if (!selectedInterlocutorId) {
        showError('Seleccione un interlocutor');
        return;
    }

    if (!confirm('¿Está seguro de eliminar este interlocutor?')) {
        return;
    }

    try {
        const selectedRow = document.querySelector(`tr[data-id="${selectedInterlocutorId}"]`);
        const tipo = selectedRow.getAttribute('data-tipo');
        
        const response = await fetch(`/api/interlocutor/${tipo}/${selectedInterlocutorId}`, {
            method: 'DELETE'
        });

        const responseData = await response.json();
        console.log('Respuesta del servidor:', responseData); // Para depuración

        if (!response.ok) {
            if (response.status === 400) {
                throw new Error('No se puede eliminar el interlocutor porque tiene órdenes asociadas. Por favor, elimine primero las órdenes.');
            } else {
                throw new Error(responseData.error || 'Error al eliminar el interlocutor');
            }
        }
        
        showError(responseData.message || 'Interlocutor eliminado correctamente');
        await initializeTable();
        
        document.getElementById('editInterlocutor').disabled = true;
        document.getElementById('deleteInterlocutor').disabled = true;
        
    } catch (error) {
        console.error('Error en deleteInterlocutor:', error);
        showError(error.message || 'Error al eliminar el interlocutor');
    }
}

// Actualizar la función showError para que sea más descriptiva
function showError(message) {
    const isError = message.toLowerCase().includes('error') || 
                   message.toLowerCase().includes('no se puede');
    
    if (isError) {
        alert('❌ ' + message);
    } else {
        alert('✅ ' + message);
    }
}

// Funciones de utilidad
function handleSearch(searchTerm) {
    if (!searchTerm) {
        initializeTable();
        return;
    }

    const searchLower = searchTerm.toLowerCase();
    const filteredData = data.filter(item => 
        item.nombre.toLowerCase().includes(searchLower) ||
        item.empresa.toLowerCase().includes(searchLower)
    );
    
    data = filteredData;
    currentPage = 1;
    renderTable(currentPage);
    renderPagination();
}

function adjustFormFields(tipo) {
    const nombreLabel = document.querySelector('label[for="nombre"]');
    const empresaLabel = document.querySelector('label[for="empresa"]');
    
    if (tipo === 'cliente') {
        nombreLabel.textContent = 'Nombre del Cliente: *';
        empresaLabel.textContent = 'Empresa del Cliente: *';
    } else if (tipo === 'proveedor') {
        nombreLabel.textContent = 'Nombre del Proveedor: *';
        empresaLabel.textContent = 'Empresa del Proveedor: *';
    }
}

function showError(message) {
    alert(message);
}