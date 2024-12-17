// Variables globales
let data = [];
const rowsPerPage = 10;
let currentPage = 1;
let editMode = false;
let selectedProductId = null;

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
    document.getElementById('newProducto')?.addEventListener('click', () => openModal('new'));
    document.getElementById('editProducto')?.addEventListener('click', () => openModal('edit'));
    document.getElementById('deleteProducto')?.addEventListener('click', deleteProducto);
    
    // Configurar modal
    document.querySelector('.close-button')?.addEventListener('click', closeModal);
    document.querySelector('.cancel')?.addEventListener('click', closeModal);
    
    // Configurar formulario
    document.getElementById('productoForm')?.addEventListener('submit', async function(e) {
        e.preventDefault();
        await saveProducto(e.target);
    });
});

// Funciones de inicialización y carga de datos
async function initializeTable() {
    try {
        const response = await fetch('/api/inventario/lista');
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        const result = await response.json();
        data = result.productos;
        
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
        tr.innerHTML = '<td colspan="6" class="text-center">No hay datos disponibles</td>';
        tableBody.appendChild(tr);
        return;
    }

    const startIndex = (page - 1) * rowsPerPage;
    const endIndex = Math.min(startIndex + rowsPerPage, data.length);
    const paginatedData = data.slice(startIndex, endIndex);

    paginatedData.forEach(item => {
        const tr = document.createElement("tr");
        tr.setAttribute('data-id', item.id);
        
        tr.innerHTML = `
            <td>${item.codigo}</td>
            <td>${item.nombre}</td>
            <td>${item.tipo_prenda}</td>
            <td>${item.stock_actual}</td>
            <td>${item.estado}</td>
            <td class="actions">
                <button onclick="viewDetails(${item.id})" class="btn-small">
                    Ver detalles
                </button>
            </td>
        `;
        
        tr.addEventListener('click', () => selectRow(tr));
        tableBody.appendChild(tr);
    });
}

// Funciones del modal
function openModal(mode = 'new') {
    editMode = mode === 'edit';
    const modal = document.getElementById('productoModal');
    modal.style.display = 'block';
    document.querySelector('.modal-title').textContent = 
        editMode ? 'Editar Producto' : 'Nuevo Producto';
    
    if (editMode && selectedProductId) {
        loadProductData();
    } else {
        document.getElementById('productoForm').reset();
        document.getElementById('codigo').disabled = false;
    }
}

function closeModal() {
    document.getElementById('productoModal').style.display = 'none';
    document.getElementById('productoForm').reset();
    document.getElementById('codigo').disabled = false;
}

async function loadProductData() {
    try {
        const response = await fetch(`/api/inventario/producto/${selectedProductId}`);
        if (!response.ok) throw new Error('Error al cargar los datos');
        
        const data = await response.json();
        const info = data.info_producto;
        
        // Deshabilitar código en edición
        document.getElementById('codigo').value = info.codigo;
        document.getElementById('codigo').disabled = true;
        
        // Rellenar campos
        document.getElementById('nombre').value = info.nombre;
        document.getElementById('tipo_prenda').value = info.tipo_prenda;
        document.getElementById('descripcion').value = info.descripcion || '';
        document.getElementById('marca').value = info.marca || '';
        document.getElementById('talla').value = info.talla || '';
        document.getElementById('color').value = info.color || '';
        document.getElementById('valor_compra').value = info.valor_compra;
        document.getElementById('valor_venta').value = info.valor_venta;
        document.getElementById('stock_minimo').value = info.stock_minimo;
        document.getElementById('estado').value = info.estado;
        
    } catch (error) {
        console.error('Error:', error);
        showError('Error al cargar los datos del producto');
        closeModal();
    }
}

async function saveProducto(form) {
    try {
        const formData = new FormData(form);
        const payload = {
            codigo: formData.get('codigo'),
            nombre: formData.get('nombre'),
            tipo_prenda: formData.get('tipo_prenda'),
            descripcion: formData.get('descripcion'),
            marca: formData.get('marca'),
            talla: formData.get('talla'),
            color: formData.get('color'),
            valor_compra: parseFloat(formData.get('valor_compra')),
            valor_venta: parseFloat(formData.get('valor_venta')),
            stock_minimo: parseInt(formData.get('stock_minimo')),
            estado: formData.get('estado')
        };

        const url = editMode ? 
            `/api/inventario/producto/${selectedProductId}` : 
            `/api/inventario/producto`;
        
        const response = await fetch(url, {
            method: editMode ? 'PUT' : 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Error al guardar');
        }
        
        showError(editMode ? 'Producto actualizado correctamente' : 'Producto creado correctamente');
        closeModal();
        await initializeTable();
        
    } catch (error) {
        console.error('Error:', error);
        showError('Error al guardar el producto: ' + error.message);
    }
}

async function deleteProducto() {
    if (!selectedProductId) {
        showError('Seleccione un producto');
        return;
    }

    if (!confirm('¿Está seguro de eliminar este producto?')) {
        return;
    }

    try {
        const response = await fetch(`/api/inventario/producto/${selectedProductId}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Error al eliminar');
        }
        
        showError(data.message || 'Producto eliminado correctamente');
        await initializeTable();
        
        document.getElementById('editProducto').disabled = true;
        document.getElementById('deleteProducto').disabled = true;
        
    } catch (error) {
        console.error('Error:', error);
        showError(error.message || 'Error al eliminar el producto');
    }
}

function handleSearch(searchTerm) {
    if (!searchTerm) {
        initializeTable();
        return;
    }

    fetch(`/api/inventario/buscar?q=${encodeURIComponent(searchTerm)}`)
        .then(response => response.json())
        .then(result => {
            data = result;
            currentPage = 1;
            renderTable(currentPage);
            renderPagination();
        })
        .catch(error => {
            console.error('Error en búsqueda:', error);
            showError('Error al realizar la búsqueda');
        });
}

function showError(message) {
    const isError = message.toLowerCase().includes('error') || 
                   message.toLowerCase().includes('no se puede');
    
    if (isError) {
        alert('❌ ' + message);
    } else {
        alert('✅ ' + message);
    }
}

// Funciones de paginación
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

function selectRow(tr) {
    document.querySelectorAll('#data-table tbody tr').forEach(row => {
        row.classList.remove('selected');
    });
    tr.classList.add('selected');
    selectedProductId = tr.getAttribute('data-id');
    
    document.getElementById('editProducto').disabled = false;
    document.getElementById('deleteProducto').disabled = false;
}

function viewDetails(id) {
    window.location.href = `/inventario/detalle?id=${id}`;
}