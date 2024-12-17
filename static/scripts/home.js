// Variables globales
let data = [];
const rowsPerPage = 10;
let currentPage = 1;
let editMode = false;
let currentOrderId = null;
const API_BASE = '/home';

// Función para mostrar errores
function showError(message) {
    alert(message);
}

// CRUD Operations
async function deleteOrder() {
    if (!currentOrderId) {
        showError('Por favor, seleccione una orden para eliminar');
        return;
    }

    if (!confirm('¿Está seguro que desea eliminar esta orden?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/orden/${currentOrderId}`, {
            method: 'DELETE'
        });

        const result = await response.json();
        
        if (result.success) {
            showError('Orden eliminada correctamente');
            await fetchData();
            document.getElementById('editarOrden').disabled = true;
            document.getElementById('eliminarOrden').disabled = true;
        } else {
            throw new Error(result.error || 'Error al eliminar la orden');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Error al eliminar la orden: ' + error.message);
    }
}

async function fetchData() {
  try {
      console.log('Iniciando fetchData...');
      const response = await fetch(`${API_BASE}/ordenes`);
      console.log('Response status:', response.status);

      if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      console.log('Datos recibidos:', result);

      // Asegurarse de que result sea un array
      if (!Array.isArray(result)) {
          console.error('Los datos recibidos no son un array:', result);
          data = [];
      } else {
          // Mapear los datos para asegurar la estructura correcta
          data = result.map(orden => ({
              ID: orden.ID,
              Interlocutor: orden.Interlocutor || 'Sin asignar',
              Empresa: orden.Empresa || 'Sin asignar',
              Valor_de_Orden: orden.Valor_de_Orden || 0,
              Fecha_de_Orden: orden.Fecha_de_Orden || '',
              Estado: orden.Estado || 'Pendiente',
              tipo: orden.tipo || ''
          }));
      }

      console.log('Datos procesados:', data);
      
      // Actualizar la UI
      if (data.length > 0) {
          console.log('Actualizando UI con datos...');
          updateGanancias();
          renderTable(1); // Empezar en la primera página
          renderPagination();
      } else {
          console.log('No hay datos para mostrar');
          const tableBody = document.querySelector("#data-table tbody");
          tableBody.innerHTML = `
              <tr>
                  <td colspan="6" class="text-center">No hay datos disponibles</td>
              </tr>
          `;
      }
  } catch (error) {
      console.error('Error en fetchData:', error);
      const tableBody = document.querySelector("#data-table tbody");
      tableBody.innerHTML = `
          <tr>
              <td colspan="6" class="text-center">Error al cargar los datos: ${error.message}</td>
          </tr>
      `;
  }
}

async function loadClientes() {
  try {
      const response = await fetch(`${API_BASE}/clientes`);
      if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || 'Error al cargar clientes');
      }
      
      const clientes = await response.json();
      // Cambiamos de 'interlocutor' a 'cliente' como está en el HTML
      const select = document.getElementById('interlocutor');
      select.innerHTML = '<option value="">Seleccione un cliente</option>';
      
      clientes.forEach(cliente => {
          const option = document.createElement('option');
          option.value = cliente.id;
          option.textContent = `${cliente.nombre_cliente} - ${cliente.empresa_cliente}`;
          select.appendChild(option);
      });
  } catch (error) {
      console.error('Error cargando clientes:', error);
      showError(`Error al cargar clientes: ${error.message}`);
  }
}

async function loadProveedores() {
  try {
      const response = await fetch(`${API_BASE}/proveedores`);
      if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || 'Error al cargar proveedores');
      }
      
      const proveedores = await response.json();
      // Cambiamos de 'proveedor' a 'interlocutor' como está en el HTML
      const select = document.getElementById('interlocutor');
      select.innerHTML = '<option value="">Seleccione un proveedor</option>';
      
      proveedores.forEach(proveedor => {
          const option = document.createElement('option');
          option.value = proveedor.id;
          option.textContent = `${proveedor.nombre_proveedor} - ${proveedor.empresa_proveedor}`;
          select.appendChild(option);
      });
  } catch (error) {
      console.error('Error cargando proveedores:', error);
      showError(`Error al cargar proveedores: ${error.message}`);
  }
}

// UI Functions
function selectRow(tr) {
    document.querySelectorAll('#data-table tbody tr').forEach(row => {
        row.classList.remove('selected');
    });
    tr.classList.add('selected');
    currentOrderId = tr.getAttribute('data-id');
    
    document.getElementById('editarOrden').disabled = false;
    document.getElementById('eliminarOrden').disabled = false;
}

function openModal(mode = 'new') {
  editMode = mode === 'edit';
  const modal = document.getElementById('ordenModal');
  if (modal) {
      modal.style.display = 'block';
      document.querySelector('.modal-title').textContent = editMode ? 'Editar Orden' : 'Nueva Orden';
      
      if (editMode && currentOrderId) {
          loadOrderData(currentOrderId);
      } else {
          document.getElementById('ordenForm').reset();
          document.getElementById('fecha').value = new Date().toISOString().split('T')[0];
      }
  }
}

function closeModal() {
    const modal = document.getElementById('ordenModal');
    if (modal) {
        modal.style.display = 'none';
        document.getElementById('ordenForm').reset();
    }
    editMode = false;
    currentOrderId = null;
}
console.log(data)
// Render Functions
function renderTable(page) {
    const tableBody = document.querySelector("#data-table tbody");
    tableBody.innerHTML = "";
    
    if (!data || data.length === 0) {
        const tr = document.createElement("tr");
        tr.innerHTML = '<td colspan="6" class="text-center">No hay datos disponibles</td>';
        tableBody.appendChild(tr);
        return;
    }

    const startIndex = (page - 1) * rowsPerPage;
    const endIndex = startIndex + rowsPerPage;
    const rows = data.slice(startIndex, endIndex);

    rows.forEach(row => {
        const tr = document.createElement("tr");
        tr.setAttribute('data-id', row.ID);
        
        const valorOrden = parseFloat(row.Valor_de_Orden || 0).toLocaleString('es-CL', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
        
        const fecha = row.Fecha_de_Orden ? new Date(row.Fecha_de_Orden).toLocaleDateString('es-CL') : '';
        
        tr.innerHTML = `
            <td>${row.Interlocutor || ''}</td>
            <td>${row.Empresa || ''}</td>
            <td>$${valorOrden}</td>
            <td>${fecha}</td>
            <td><div class="estado ${(row.Estado || '').toLowerCase()}">${row.Estado || ''}</div></td>
            <td><div class="tipo-orden ${(row.tipo || '').toLowerCase()}">${row.tipo || ''}</div></td>
        `;
        tr.addEventListener('click', () => selectRow(tr));
        tableBody.appendChild(tr);
    });
}

function renderPagination() {
    const totalPages = Math.ceil(data.length / rowsPerPage) || 1;
    const pagination = document.querySelector("#pagination");
    pagination.innerHTML = "";

    // Botón anterior
    const prevButton = document.createElement("button");
    prevButton.textContent = "Anterior";
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

function updateGanancias() {
  const total = data.reduce((sum, orden) => {
      const valor = parseFloat(orden.Valor_de_Orden) || 0;
      // Si es una orden de entrada (proveedor) resta, si es de salida (cliente) suma
      return orden.tipo === 'Entrada' ? sum - valor : sum + valor;
  }, 0);
  
  const totalFormateado = total.toLocaleString('es-CL', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
  });
  
  document.getElementById('gananciaTotal').textContent = `$${totalFormateado}`;
}

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM Content Loaded - Initializing...');
    
    fetchData();
    
    // Evento para cambio de tipo de orden
    document.getElementById('tipo_orden')?.addEventListener('change', function(e) {
        const tipoOrden = e.target.value;
        if (tipoOrden === 'Entrada') {
            loadProveedores();
        } else if (tipoOrden === 'Salida') {
            loadClientes();
        }
    });
    
    // Botones principales
    document.getElementById('nuevaOrden')?.addEventListener('click', () => openModal('new'));
    document.getElementById('editarOrden')?.addEventListener('click', () => openModal('edit'));
    document.getElementById('eliminarOrden')?.addEventListener('click', deleteOrder);
    
    // Modal
    document.querySelector('.close-button')?.addEventListener('click', closeModal);
    document.querySelector('.cancel')?.addEventListener('click', closeModal);
    
    // Formulario
    document.getElementById('ordenForm')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        await saveOrder(formData);
    });
    
    // Búsqueda
    let searchTimeout;
    document.getElementById('searchInput')?.addEventListener('input', function(e) {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            handleSearch(e.target.value);
        }, 300);
    });
});

function handleSearch(searchTerm) {
  if (!searchTerm) {
      fetchData(); // Si no hay término de búsqueda, mostrar todos los datos
      return;
  }

  const filteredData = data.filter(orden => 
      orden.Interlocutor.toLowerCase().includes(searchTerm.toLowerCase()) ||
      orden.Empresa.toLowerCase().includes(searchTerm.toLowerCase()) ||
      orden.Estado.toLowerCase().includes(searchTerm.toLowerCase())
  );

  data = filteredData;
  currentPage = 1;
  renderTable(currentPage);
  renderPagination();
  updateGanancias();
}

// Modificar la función saveOrder para manejar tanto creación como edición
async function saveOrder(formData) {
  try {
      // Verificar y formatear los datos antes de enviar
      const valor = formData.get('valor');
      const fecha = formData.get('fecha');
      const interlocutor = formData.get('interlocutor');
      const tipo = formData.get('tipo_orden');
      const estado = formData.get('estado');

      console.log('Valores del formulario:', {
          valor, fecha, interlocutor, tipo, estado
      });

      // Validar que todos los campos requeridos tengan valor
      if (!valor || !fecha || !interlocutor || !tipo || !estado) {
          throw new Error('Todos los campos son requeridos');
      }

      const orderData = {
          tipo_orden: tipo,
          interlocutor_id: parseInt(interlocutor),
          valor_orden: parseFloat(valor),
          fecha_orden: fecha,
          estado_orden: estado
      };

      console.log('Datos a enviar:', orderData);

      // Determinar si es una edición o una nueva orden
      const method = editMode ? 'PUT' : 'POST';
      const url = editMode ? `${API_BASE}/orden/${currentOrderId}` : `${API_BASE}/orden`;

      const response = await fetch(url, {
          method: method,
          headers: {
              'Content-Type': 'application/json'
          },
          body: JSON.stringify(orderData)
      });

      const result = await response.json();
      console.log('Respuesta del servidor:', result);

      if (!response.ok) {
          throw new Error(result.error || 'Error al procesar la orden');
      }

      if (result.success) {
          showError(editMode ? 'Orden actualizada correctamente' : 'Orden creada correctamente');
          closeModal();
          await fetchData();
      } else {
          throw new Error(result.error || 'Error al procesar la orden');
      }
  } catch (error) {
      console.error('Error al guardar orden:', error);
      showError('Error al guardar la orden: ' + error.message);
      throw error;
  }
}

// Actualizar la función loadOrderData para manejar correctamente el interlocutor
async function loadOrderData(orderId) {
  try {
      // Obtener los datos de la orden del servidor
      const response = await fetch(`${API_BASE}/orden/${orderId}`);
      if (!response.ok) {
          throw new Error('Error al obtener los datos de la orden');
      }
      
      const orden = await response.json();
      if (!orden) {
          throw new Error('Orden no encontrada');
      }

      // Establecer el tipo de orden
      const tipoOrdenSelect = document.getElementById('tipo_orden');
      tipoOrdenSelect.value = orden.tipo_orden;
      
      // Cargar los interlocutores correspondientes
      if (orden.tipo_orden === 'Entrada') {
          await loadProveedores();
      } else {
          await loadClientes();
      }
      
      // Esperar a que se carguen los interlocutores y establecer el valor
      setTimeout(() => {
          const interlocutorSelect = document.getElementById('interlocutor');
          interlocutorSelect.value = orden.interlocutor_id;
      }, 500);

      // Establecer los demás valores
      document.getElementById('valor').value = orden.valor_orden;
      document.getElementById('fecha').value = orden.fecha_orden;
      document.getElementById('estado').value = orden.estado_orden;

  } catch (error) {
      console.error('Error al cargar los datos de la orden:', error);
      showError('Error al cargar los datos de la orden: ' + error.message);
  }
}

// Añade esta función antes de openModal
async function loadOrderData(orderId) {
  try {
      // Buscar la orden en los datos existentes
      const selectedOrder = data.find(order => order.ID === parseInt(orderId));
      if (!selectedOrder) {
          throw new Error('Orden no encontrada');
      }

      // Establecer el tipo de orden
      const tipoOrdenSelect = document.getElementById('tipo_orden');
      tipoOrdenSelect.value = selectedOrder.tipo;
      
      // Disparar el evento change manualmente para cargar los interlocutores
      const event = new Event('change');
      tipoOrdenSelect.dispatchEvent(event);
      
      // Esperar a que se carguen los interlocutores antes de establecer el valor
      setTimeout(() => {
          const interlocutorSelect = document.getElementById('interlocutor');
          // El ID del interlocutor dependerá del tipo de orden
          const interlocutorId = selectedOrder.tipo === 'Entrada' ? selectedOrder.proveedor_id : selectedOrder.cliente_id;
          interlocutorSelect.value = interlocutorId;
      }, 500);

      // Establecer los demás valores
      document.getElementById('valor').value = selectedOrder.Valor_de_Orden;
      document.getElementById('fecha').value = selectedOrder.Fecha_de_Orden;
      document.getElementById('estado').value = selectedOrder.Estado;

  } catch (error) {
      console.error('Error al cargar los datos de la orden:', error);
      showError('Error al cargar los datos de la orden: ' + error.message);
  }
}